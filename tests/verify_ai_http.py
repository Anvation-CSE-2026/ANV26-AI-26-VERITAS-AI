"""Real HTTP E2E: live Gemini/Ollama, concise metrics, persisted results/failures."""
import argparse
import json
import os
import re
import socket
import subprocess
import sys
import tempfile
import time
from contextlib import nullcontext
from datetime import datetime, timezone
from pathlib import Path

import httpx
from google import genai
from google.genai import errors, types

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.config import settings
from app.models.contracts import Analysis, AnalysisDraft, AnalysisFailure, Contract, ObligationDraft, RiskDraft
from app.services.evidence import verify_analysis
from app.services.playbook import load_playbook
from sample_pdf import sample_pdf


class CheckFailed(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise CheckFailed(message)


def start_server(port, storage_path, model):
    env = os.environ.copy()
    env.update(STORAGE_PATH=str(storage_path), GEMINI_MODEL=model)
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(port)],
        cwd=ROOT / "backend", env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def stop_server(server):
    server.terminate()
    try:
        server.wait(timeout=10)
    except subprocess.TimeoutExpired:
        server.kill()
        server.wait(timeout=10)


def update_model(model):
    for path in [ROOT / "backend" / ".env", ROOT / "backend" / ".env.example"]:
        old = path.read_bytes()
        line = b"GEMINI_MODEL=" + model.encode("ascii")
        pattern = rb"(?m)^[ \t]*GEMINI_MODEL[ \t]*=[^\r\n]*"
        require(bool(re.search(pattern, old)), "Model setting was not found; automatic update blocked.")
        path.write_bytes(re.sub(pattern, lambda match: line, old))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=settings.gemini_model)
    parser.add_argument("--keep-storage", action="store_true")
    parser.add_argument("--report", default=os.environ.get("AI_E2E_REPORT_PATH"))
    parser.add_argument("--apply-model-on-success", action="store_true")
    args = parser.parse_args()
    report = {
        "verified_at": datetime.now(timezone.utc).isoformat(), "gemini_model": args.model,
        "contract_id": None, "analysis_id": None, "status": "failed", "findings": None,
        "verified_findings": None, "unsupported_findings": None, "obligations": None,
        "total_processing_seconds": None, "failed_stage": "prerequisites", "error_category": None,
        "http_status": None, "gemini_attempts": 0, "retries_occurred": False,
        "failure_recorded_correctly": False, "success": False, "configuration_updated": False,
    }
    started = None
    try:
        require(bool(settings.gemini_api_key.strip()), "Gemini key is not configured.")
        with genai.Client(api_key=settings.gemini_api_key, http_options=types.HttpOptions(timeout=15000, retry_options=types.HttpRetryOptions(attempts=1))) as client:
            model = client.models.get(model=args.model)
            require("generateContent" in (model.supported_actions or []), "Selected model does not advertise generateContent.")
        report["model_accessible"] = report["supports_generateContent"] = True
        with httpx.Client(timeout=10, trust_env=False) as ollama:
            tags = ollama.get(settings.ollama_base_url.rstrip("/") + "/api/tags")
            require(tags.status_code == 200, "Ollama model inventory request failed.")
            require(any(item["name"] == settings.ollama_embedding_model for item in tags.json().get("models", [])), "Requested Ollama embedding model is unavailable.")
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        storage_context = nullcontext(None) if args.keep_storage else tempfile.TemporaryDirectory()
        with storage_context as temp:
            storage = settings.storage_path if args.keep_storage else Path(temp) / "e2e.sqlite3"
            server = start_server(port, storage, args.model)
            try:
                with httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=540, trust_env=False) as client:
                    for attempt in range(100):
                        require(server.poll() is None, "Backend exited before readiness.")
                        try:
                            require(client.get("/health").status_code == 200, "Health check failed.")
                            break
                        except httpx.ConnectError:
                            time.sleep(0.1)
                    else:
                        raise CheckFailed("Backend did not become ready.")
                    started = time.monotonic()
                    report["failed_stage"] = "pdf_upload_extraction"
                    upload = client.post("/api/contracts/upload", files={"file": ("synthetic_supplier_contract.pdf", sample_pdf(), "application/pdf")})
                    report["http_status"] = upload.status_code
                    require(upload.status_code == 201, "Synthetic PDF upload failed.")
                    contract = Contract.model_validate_json(upload.text)
                    report.update(contract_id=contract.contract_id, pages=len(contract.pages), clauses=len(contract.clauses))
                    print(json.dumps({"contract_id": contract.contract_id, "upload_http": 201, "pages": len(contract.pages), "clauses": len(contract.clauses)}), flush=True)
                    report["failed_stage"] = "analysis"
                    response = client.post("/api/analyze", json={"contract_id": contract.contract_id})
                    report["http_status"] = response.status_code
                    require(settings.gemini_api_key not in response.text, "Secret redaction check failed.")
                    if response.status_code != 200:
                        detail = response.json().get("detail", {})
                        if isinstance(detail, dict):
                            report.update(analysis_id=detail.get("analysis_id"), failed_stage=detail.get("failed_stage", "analysis"),
                                          error_category=detail.get("error_category", "analysis_failure"),
                                          gemini_attempts=detail.get("gemini_attempts", 0), upstream_http_status=detail.get("upstream_http_status"))
                        if report["analysis_id"]:
                            fetched = client.get("/api/analysis/" + report["analysis_id"])
                            if fetched.status_code == 200:
                                failure = AnalysisFailure.model_validate_json(fetched.text)
                                report.update(failure_recorded_correctly=failure.status == "failed", failed_stage=failure.failed_stage,
                                              error_category=failure.error_category, gemini_attempts=failure.gemini_attempts,
                                              upstream_http_status=failure.upstream_http_status, fetch_http=200)
                        report["retries_occurred"] = report["gemini_attempts"] > 1
                        raise CheckFailed("Real analysis failed; see recorded stage and status.")
                    result = Analysis.model_validate_json(response.text)
                    report.update(analysis_id=result.analysis_id, status=result.status, findings=len(result.findings),
                                  verified_findings=sum(item.evidence_status == "verified" for item in result.findings),
                                  quote_verified_findings=sum(item.evidence_verified for item in result.findings),
                                  needs_review_findings=sum(item.evidence_status == "needs_review" for item in result.findings),
                                  unsupported_findings=sum(item.record_type == "finding" for item in result.verification_rejections),
                                  obligations=len(result.obligations), rejected_obligations=sum(item.record_type == "obligation" for item in result.verification_rejections),
                                  gemini_attempts=result.gemini_attempts, retries_occurred=result.gemini_attempts > 1,
                                  response_model=result.gemini_response_model)
                    require(result.findings and result.obligations, "Synthetic contract produced no usable verified findings or obligations.")
                    report["failed_stage"] = "independent_evidence_verification"
                    draft = AnalysisDraft(
                        findings=[RiskDraft.model_validate({key: value for key, value in item.model_dump().items() if key in RiskDraft.model_fields}) for item in result.findings],
                        obligations=[ObligationDraft.model_validate({key: value for key, value in item.model_dump().items() if key in ObligationDraft.model_fields}) for item in result.obligations],
                    )
                    require(not verify_analysis(draft, contract, load_playbook())[2], "Returned evidence failed independent verification.")
                    report["failed_stage"] = "sqlite_retrieval"
                    fetched = client.get("/api/analysis/" + result.analysis_id)
                    require(fetched.status_code == 200 and fetched.json() == response.json(), "Stored result retrieval failed.")
                    require(len(result.semantic_matches) == 3 * len(contract.clauses), "Semantic retrieval coverage failed.")
                    # Restart to prove persistence rather than an in-memory result.
                    stop_server(server)
                    server = start_server(port, storage, args.model)
                    for attempt in range(100):
                        try:
                            restarted = client.get("/api/analysis/" + result.analysis_id)
                            if restarted.status_code == 200:
                                break
                        except httpx.ConnectError:
                            pass
                        time.sleep(0.1)
                    else:
                        raise CheckFailed("Restarted result retrieval failed.")
                    require(restarted.json() == response.json(), "Result changed across backend restart.")
                    report.update(success=True, failed_stage=None, error_category=None, fetch_http=200, restart_persistence_verified=True,
                                  semantic_matches=len(result.semantic_matches), evidence_reverified=True,
                                  durable_storage=args.keep_storage)
                    if args.apply_model_on_success:
                        update_model(args.model)
                        report["configuration_updated"] = True
            finally:
                stop_server(server)
    except errors.APIError as exc:
        report.update(http_status=exc.code, error_category="model_access_error")
        raise CheckFailed("Model access verification failed.") from None
    except Exception as exc:
        if report["error_category"] is None:
            report["error_category"] = type(exc).__name__
        raise
    finally:
        if started is not None:
            report["total_processing_seconds"] = round(time.monotonic() - started, 3)
        serialized = json.dumps(report, indent=2)
        require(not settings.gemini_api_key or settings.gemini_api_key not in serialized, "Secret redaction check failed.")
        if args.report:
            Path(args.report).write_text(serialized + "\n", encoding="utf-8")
        print(json.dumps(report, sort_keys=True), flush=True)


if __name__ == "__main__":
    try:
        main()
    except CheckFailed as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
    except Exception as exc:
        print(f"Real E2E failed ({type(exc).__name__}); details suppressed.", file=sys.stderr)
        raise SystemExit(1)
