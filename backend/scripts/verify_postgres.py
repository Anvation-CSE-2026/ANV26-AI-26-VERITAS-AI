"""Explicit Neon verification using uniquely named synthetic records; never calls AI/billing providers."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import psycopg
from fastapi.testclient import TestClient
from psycopg.conninfo import conninfo_to_dict
from app.config import settings
from app.models.contracts import Analysis, AnalysisFailure
from app.services import storage
from app.services.evidence import verify_analysis
from app.services.playbook import load_playbook
from app.services.security import verify_password


def main():
    report = {"database_configured": bool(settings.database_url.strip()), "checks": {},
              "ai_calls": 0, "payment_provider_calls": 0}
    if not report["database_configured"]:
        print(json.dumps({**report, "status": "failed", "category": "database_not_configured"}))
        return 1
    # Existing fixture helpers are used only by this local diagnostic, never by the deployed application.
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tests"))
    from sample_pdf import sample_pdf
    from test_contract_analysis import valid_draft
    from app.services.pdf_extraction import extract_contract
    tag = str(uuid4())
    uid, cid, aid, fid, sid, eid = [str(uuid4()) for _ in range(6)]
    stage = "connection_and_migrations"
    checks = report["checks"]
    value = settings.database_url.strip()
    report["url_format_checks"] = {
        "postgres_uri": value.startswith(("postgresql://", "postgres://")),
        "sqlalchemy_uri": value.startswith("postgresql+"),
        "psql_command": value.startswith("psql"),
        "outer_quote": value.startswith(("'", '"')),
        "contains_newline": "\n" in value,
    }
    try:
        try:
            conninfo_to_dict(settings.database_url)
            checks["connection_string_parse"] = True
        except psycopg.ProgrammingError as exc:
            message = str(exc).lower()
            for phrase in ("invalid percent-encoded token", "extra key/value separator", "missing key/value separator",
                           "unterminated quoted string", "invalid integer value", "unexpected spaces",
                           "invalid uri", "invalid query", "invalid dsn"):
                if phrase in message:
                    report["parse_error_category"] = phrase.replace(" ", "_")
            report["configuration_issue"] = ("psql_command_instead_of_url" if settings.database_url.strip().startswith("psql ")
                else "invalid_connection_option" if "invalid connection option" in message
                else "invalid_uri_parameter" if "invalid uri query parameter" in message
                else "invalid_connection_string")
            raise
        with storage.connection() as conn:
            tables = {r[0] for r in conn.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema=current_schema()"
            ).fetchall()}
            expected = {"users", "contracts", "analyses", "analysis_failures", "subscriptions", "payment_events", "usage_records"}
            assert expected.issubset(tables)
            checks["tables"] = sorted(expected)
            # Execute migrations twice on the real database to verify idempotency.
            conn.execute("SELECT pg_advisory_xact_lock(742918650)")
            storage._run_migrations(conn)
            storage._run_migrations(conn)
            pdf_type = conn.execute("SELECT data_type FROM information_schema.columns WHERE table_schema=current_schema() AND table_name='contracts' AND column_name='pdf'").fetchone()[0]
            assert pdf_type == "bytea"
            checks["migrations_idempotent"] = True
            checks["pdf_column_bytea"] = True
        stage = "user_roundtrip"
        now = datetime.now(timezone.utc).isoformat()
        from app.main import app
        with TestClient(app) as api:
            registered = api.post("/api/auth/register", json={"email": f"neon-verification-{tag}@test.invalid", "password": "synthetic-only-password"})
            assert registered.status_code == 201
            uid = registered.json()["user"]["id"]
            logged_in = api.post("/api/auth/login", json={"email": registered.json()["user"]["email"], "password": "synthetic-only-password"})
            assert logged_in.status_code == 200
            api.headers["Authorization"] = "Bearer " + logged_in.json()["access_token"]
            assert api.get("/api/auth/me").json()["id"] == uid
        user = storage.get_user_by_id(uid)
        assert user is not None
        assert storage.get_user_by_id(uid) == user
        assert storage.get_user_by_email(user.email) == user
        assert verify_password("synthetic-only-password", storage.get_user_by_id(uid).password_hash)
        storage.set_user_trial_used(uid)
        assert storage.get_user_by_id(uid).trial_used
        checks["user_creation_retrieval_password_and_trial"] = True
        checks["registration_login_authenticated_profile"] = True
        stage = "contract_and_analysis_roundtrip"
        pdf = sample_pdf()
        contract = extract_contract(pdf, "synthetic-neon-verification.pdf")
        contract.contract_id = cid
        storage.save_contract(contract, pdf, user_id=uid)
        assert storage.get_contract(cid, user_id=uid) == contract
        assert storage.get_contract(cid, user_id="different-synthetic-user") is None
        with storage.connection() as conn:
            assert bytes(conn.execute("SELECT pdf FROM contracts WHERE id=?", (cid,)).fetchone()[0]) == pdf
        findings, obligations, rejections = verify_analysis(valid_draft(contract), contract, load_playbook())
        assert not rejections and all(f.evidence_verified for f in findings)
        book = load_playbook()
        analysis = Analysis(analysis_id=aid, contract_id=cid, created_at=datetime.now(timezone.utc),
                            status="completed", gemini_model="not_used", embedding_model="not_used",
                            output_origin="synthetic_demo", playbook_id=book.playbook_id,
                            playbook_version=book.version, processing_seconds=0,
                            findings=findings, obligations=obligations, semantic_matches=[],
                            unassessed_policy_ids=[], verification_rejections=[],
                            warnings=["SAMPLE ANALYSIS — DEMO DATA; storage verification only, no AI call."])
        storage.save_analysis(analysis, user_id=uid)
        assert storage.get_analysis(aid, user_id=uid) == analysis
        assert storage.get_analysis(aid, user_id="different-synthetic-user") is None
        assert storage.get_user_analyses_history(uid, limit=1) == [analysis]
        second = analysis.model_copy(update={"analysis_id": str(uuid4())})
        storage.save_analysis(second, user_id=uid)
        assert storage.get_user_analyses_history(uid, limit=1) == [second]
        checks["pdf_contract_analysis_history_and_isolation"] = True
        stage = "failure_roundtrip"
        failure = AnalysisFailure(analysis_id=fid, contract_id=cid, created_at=datetime.now(timezone.utc),
                                  failed_stage="gemini_reasoning", error_category="synthetic_test",
                                  message="Synthetic verification failure record.", http_status=503,
                                  gemini_model="not_used", gemini_attempts=0, retries_occurred=False,
                                  processing_seconds=0)
        storage.save_failure(failure, user_id=uid)
        assert storage.get_failure(fid, user_id=uid) == failure
        assert storage.get_failure(fid, user_id="different-synthetic-user") is None
        checks["failure_persistence_and_isolation"] = True
        stage = "subscription_events_usage"
        subscription = dict(id=sid, user_id=uid, plan="pro", status="trialing", created_at=now,
                            updated_at=now, razorpay_subscription_id=f"synthetic-{tag}")
        storage.save_subscription(subscription)
        assert storage.get_latest_subscription_by_user_id(uid)["id"] == sid
        storage.update_subscription(sid, {"status": "active", "updated_at": now, "not_allowed": "ignored"})
        assert storage.get_subscription_by_razorpay_id(subscription["razorpay_subscription_id"])["status"] == "active"
        storage.record_payment_event(eid, "synthetic.verification")
        assert storage.get_payment_event(eid)["event_type"] == "synthetic.verification"
        storage.record_analysis_usage(uid, aid, "synthetic-period")
        assert storage.count_analyses_in_period(uid, "synthetic-period") == 1
        assert storage.count_analyses_in_period("other", "synthetic-period") == 0
        checks["subscriptions_payment_events_usage"] = True
        stage = "rollback"
        try:
            with storage.connection() as conn:
                conn.execute("UPDATE users SET trial_used=0 WHERE id=?", (uid,))
                raise RuntimeError("synthetic rollback")
        except RuntimeError:
            pass
        assert storage.get_user_by_id(uid).trial_used
        checks["transaction_rollback"] = True
        report["status"] = "passed"
    except Exception as exc:
        # Never stringify exceptions: drivers may include hosts, usernames, SQL values or DSNs.
        report.update(status="failed", failed_stage=stage, error_type=type(exc).__name__,
                      sqlstate=getattr(exc, "sqlstate", None))
    finally:
        try:
            with storage.connection() as conn:
                # Delete only records created by this invocation, in FK-safe order.
                for table in ("usage_records", "subscriptions", "analyses", "analysis_failures", "contracts"):
                    conn.execute(f"DELETE FROM {table} WHERE user_id=?", (uid,))
                conn.execute("DELETE FROM payment_events WHERE provider_event_id=?", (eid,))
                conn.execute("DELETE FROM users WHERE id=?", (uid,))
            checks["synthetic_records_cleaned_up"] = True
        except Exception as exc:
            checks["synthetic_records_cleaned_up"] = False
            report.update(status="failed", cleanup_error_type=type(exc).__name__)
        report["existing_records_modified"] = False
        output = Path(__file__).resolve().parents[2] / "docs" / "POSTGRES_VERIFICATION.json"
        output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
