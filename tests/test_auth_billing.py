import hashlib
import hmac
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.config import settings
from app.main import app
from app.models.contracts import AnalysisDraft, ObligationDraft, RiskDraft
from app.services.billing import get_current_billing_period
from app.services.pdf_extraction import extract_contract
from app.services.storage import count_analyses_in_period, record_analysis_usage
from sample_pdf import sample_pdf


def sample_draft(contract):
    clause = next(c for c in contract.clauses if "1. Liability" in c.text)
    obligation_clause = next(c for c in contract.clauses if "8. Reporting" in c.text)
    return AnalysisDraft(
        findings=[
            RiskDraft(
                risk_level="high",
                clause_category="liability",
                explanation="Low liability cap conflict.",
                evidence_quote=clause.text,
                page_number=clause.page_number,
                clause_id=clause.clause_id,
                policy_id="POL-LIAB-001",
                recommended_action="Negotiate higher cap.",
            )
        ],
        obligations=[
            ObligationDraft(
                description="Deliver monthly report.",
                evidence_quote=obligation_clause.text,
                page_number=obligation_clause.page_number,
                clause_id=obligation_clause.clause_id,
                responsible_party="Supplier",
                deadline="by the fifth day",
            )
        ],
    )


class AuthBillingBaseTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        database_patch = patch.object(settings, "database_url", "")
        database_patch.start()
        self.addCleanup(database_patch.stop)
        self.storage_patch = patch.object(settings, "storage_path", Path(self.temp.name) / "test.sqlite3")
        self.storage_patch.start()
        self.addCleanup(self.storage_patch.stop)

        self.key_patch = patch.object(settings, "gemini_api_key", "test-gemini-key")
        self.key_patch.start()
        self.addCleanup(self.key_patch.stop)

        self.rzp_patch = patch.object(settings, "razorpay_webhook_secret", "test_webhook_secret_123")
        self.rzp_patch.start()
        self.addCleanup(self.rzp_patch.stop)

        self.rzp_sec_patch = patch.object(settings, "razorpay_key_secret", "test_key_secret_123")
        self.rzp_sec_patch.start()
        self.addCleanup(self.rzp_sec_patch.stop)

        self.rzp_key_patch = patch.object(settings, "razorpay_key_id", "rzp_test_mock_key_123")
        self.rzp_key_patch.start()
        self.addCleanup(self.rzp_key_patch.stop)

        self.rzp_std_patch = patch.object(settings, "razorpay_standard_plan_id", "plan_mock_std_123")
        self.rzp_std_patch.start()
        self.addCleanup(self.rzp_std_patch.stop)

        self.rzp_pro_patch = patch.object(settings, "razorpay_pro_plan_id", "plan_mock_pro_123")
        self.rzp_pro_patch.start()
        self.addCleanup(self.rzp_pro_patch.stop)

        self.client = TestClient(app)
        self.addCleanup(self.client.close)

    def register_user(self, email="user@veritas.internal", password="StrongPassword123!"):
        res = self.client.post("/api/auth/register", json={"email": email, "password": password})
        return res

    def login_user(self, email="user@veritas.internal", password="StrongPassword123!"):
        res = self.client.post("/api/auth/login", json={"email": email, "password": password})
        return res


class AuthTests(AuthBillingBaseTest):
    def test_user_registration_success(self):
        res = self.register_user("newuser@example.com", "Password123")
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["token_type"], "bearer")
        self.assertEqual(data["user"]["email"], "newuser@example.com")
        self.assertFalse(data["user"]["trial_used"])

    def test_user_registration_duplicate_email(self):
        self.register_user("dup@example.com", "Password123")
        dup_res = self.register_user("dup@example.com", "Password123")
        self.assertEqual(dup_res.status_code, 409)
        self.assertIn("already exists", dup_res.json()["detail"])

    def test_user_registration_short_password(self):
        res = self.register_user("short@example.com", "123")
        self.assertEqual(res.status_code, 422)  # Pydantic validation error

    def test_user_login_success(self):
        self.register_user("login@example.com", "MyPassword123")
        res = self.login_user("login@example.com", "MyPassword123")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["user"]["email"], "login@example.com")

    def test_user_login_wrong_password(self):
        self.register_user("wrongpw@example.com", "MyPassword123")
        res = self.login_user("wrongpw@example.com", "WrongPassword!")
        self.assertEqual(res.status_code, 401)
        self.assertIn("Invalid email or password", res.json()["detail"])

    def test_user_login_nonexistent_email(self):
        res = self.login_user("ghost@example.com", "Password123")
        self.assertEqual(res.status_code, 401)

    def test_get_current_user_me(self):
        reg = self.register_user("me@example.com", "Password123").json()
        token = reg["access_token"]
        res = self.client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["email"], "me@example.com")

    def test_protected_route_without_token(self):
        res = self.client.get("/api/auth/me")
        self.assertEqual(res.status_code, 401)

    def test_protected_route_invalid_token(self):
        res = self.client.get("/api/auth/me", headers={"Authorization": "Bearer invalid.token.payload"})
        self.assertEqual(res.status_code, 401)

    def test_logout(self):
        reg = self.register_user("logout@example.com", "Password123").json()
        token = reg["access_token"]
        res = self.client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res.status_code, 200)
        self.assertIn("logged out", res.json()["message"])


class TrialAndBillingTests(AuthBillingBaseTest):
    def test_list_plans(self):
        res = self.client.get("/api/billing/plans")
        self.assertEqual(res.status_code, 200)
        plans = res.json()["plans"]
        self.assertEqual(len(plans), 2)
        std = next(p for p in plans if p["tier"] == "standard")
        pro = next(p for p in plans if p["tier"] == "pro")
        self.assertEqual(std["price_inr"], 199)
        self.assertEqual(std["monthly_analyses_limit"], 10)
        self.assertFalse(std["features"]["category_knowledge_graph"])
        self.assertFalse(std["features"]["priority_processing"])
        self.assertEqual(pro["price_inr"], 299)
        self.assertEqual(pro["monthly_analyses_limit"], 30)
        self.assertTrue(pro["features"]["category_knowledge_graph"])
        self.assertFalse(pro["features"]["priority_processing"])

    def test_start_trial_standard(self):
        reg = self.register_user("stdtrial@example.com", "Password123").json()
        token = reg["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        res = self.client.post("/api/billing/trial/start", json={"plan": "standard"}, headers=headers)
        self.assertEqual(res.status_code, 201)
        sub = res.json()
        self.assertEqual(sub["plan"], "standard")
        self.assertEqual(sub["status"], "trialing")
        self.assertTrue(sub["is_active"])
        self.assertIsNotNone(sub["trial_end"])
        self.assertEqual(sub["analyses_limit"], 10)
        self.assertEqual(sub["analyses_remaining"], 10)

    def test_start_trial_pro(self):
        reg = self.register_user("protrial@example.com", "Password123").json()
        token = reg["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        res = self.client.post("/api/billing/trial/start", json={"plan": "pro"}, headers=headers)
        self.assertEqual(res.status_code, 201)
        sub = res.json()
        self.assertEqual(sub["plan"], "pro")
        self.assertEqual(sub["status"], "trialing")

    def test_duplicate_trial_rejected(self):
        reg = self.register_user("duptrial@example.com", "Password123").json()
        token = reg["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        # First trial start succeeds
        self.client.post("/api/billing/trial/start", json={"plan": "standard"}, headers=headers)
        # Second trial start must fail
        res2 = self.client.post("/api/billing/trial/start", json={"plan": "pro"}, headers=headers)
        self.assertEqual(res2.status_code, 400)
        self.assertIn("already utilized", res2.json()["detail"])

    def test_cancel_subscription(self):
        reg = self.register_user("canceltrial@example.com", "Password123").json()
        token = reg["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        self.client.post("/api/billing/trial/start", json={"plan": "standard"}, headers=headers)
        res = self.client.post("/api/billing/cancel", headers=headers)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()["success"])
        status_res = self.client.get("/api/billing/subscription", headers=headers)
        self.assertEqual(status_res.json()["status"], "cancelled")


class UsageAndQuotaEnforcementTests(AuthBillingBaseTest):
    def test_quota_exhaustion_on_standard_plan(self):
        reg = self.register_user("quotastd@example.com", "Password123").json()
        token = reg["access_token"]
        user_id = reg["user"]["id"]
        headers = {"Authorization": f"Bearer {token}"}
        self.client.post("/api/billing/trial/start", json={"plan": "standard"}, headers=headers)

        # Upload contract
        upload_res = self.client.post(
            "/api/contracts/upload",
            files={"file": ("synthetic.pdf", sample_pdf(), "application/pdf")},
            headers=headers,
        )
        contract_id = upload_res.json()["contract_id"]

        period = get_current_billing_period()
        # Simulate standard limit of 10 analyses used
        for i in range(10):
            record_analysis_usage(user_id, f"test-analysis-{i}", period)
        self.assertEqual(count_analyses_in_period(user_id, period), 10)

        # Attempt 11th analysis -> Should return 429 Quota Exceeded
        res = self.client.post("/api/analyze", json={"contract_id": contract_id}, headers=headers)
        self.assertEqual(res.status_code, 429)
        self.assertIn("Monthly contract analysis limit reached", str(res.json()["detail"]))

    def test_quota_not_deducted_on_failed_analysis(self):
        reg = self.register_user("failuser@example.com", "Password123").json()
        token = reg["access_token"]
        user_id = reg["user"]["id"]
        headers = {"Authorization": f"Bearer {token}"}
        self.client.post("/api/billing/trial/start", json={"plan": "standard"}, headers=headers)

        upload_res = self.client.post(
            "/api/contracts/upload",
            files={"file": ("synthetic.pdf", sample_pdf(), "application/pdf")},
            headers=headers,
        )
        contract_id = upload_res.json()["contract_id"]

        period = get_current_billing_period()
        # Initial usage is 0
        self.assertEqual(count_analyses_in_period(user_id, period), 0)

        # Mock generate_analysis raising an exception
        from app.services.gemini_analysis import GeminiError
        with patch("app.services.contract_analysis.match_policies", return_value=[]), \
             patch("app.services.contract_analysis.generate_analysis", side_effect=GeminiError("API quota hit", 502)):
            res = self.client.post("/api/analyze", json={"contract_id": contract_id}, headers=headers)
            self.assertEqual(res.status_code, 502)

        # Usage should still be 0!
        self.assertEqual(count_analyses_in_period(user_id, period), 0)

    def test_demo_endpoint_public_and_unrestricted(self):
        # GET /api/demo/analysis requires NO authorization and does NOT consume quota
        res = self.client.get("/api/demo/analysis")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["label"], "SAMPLE ANALYSIS — DEMO DATA")
        self.assertFalse(data["live_ai_used"])
        self.assertGreater(len(data["analysis"]["findings"]), 0)


class RazorpayIntegrationTests(AuthBillingBaseTest):
    def test_create_checkout(self):
        reg = self.register_user("checkout@example.com", "Password123").json()
        token = reg["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        mock_rzp = MagicMock()
        mock_rzp.subscription.create.return_value = {"id": "sub_test_mock_pro"}

        with patch("app.services.razorpay_service.get_razorpay_client", return_value=mock_rzp):
            res = self.client.post("/api/billing/checkout", json={"plan": "pro"}, headers=headers)
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data["plan"], "pro")
            self.assertEqual(data["subscription_id"], "sub_test_mock_pro")
            self.assertEqual(data["amount_paise"], 29900)

    def test_verify_payment_valid_signature(self):
        reg = self.register_user("verify@example.com", "Password123").json()
        token = reg["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        sub_id = "sub_test_12345"
        pay_id = "pay_test_67890"

        mock_rzp = MagicMock()
        mock_rzp.subscription.create.return_value = {"id": sub_id}

        with patch("app.services.razorpay_service.get_razorpay_client", return_value=mock_rzp):
            self.client.post("/api/billing/checkout", json={"plan": "pro"}, headers=headers)

        # Generate valid HMAC signature: payment_id|subscription_id
        message = f"{pay_id}|{sub_id}"
        valid_sig = hmac.new(
            settings.razorpay_key_secret.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        res = self.client.post(
            "/api/billing/verify",
            json={
                "razorpay_payment_id": pay_id,
                "razorpay_subscription_id": sub_id,
                "razorpay_signature": valid_sig,
                "plan": "pro",
            },
            headers=headers,
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["subscription"]["status"], "active")
        self.assertEqual(data["subscription"]["plan"], "pro")

    def test_verify_payment_invalid_signature(self):
        reg = self.register_user("badverify@example.com", "Password123").json()
        token = reg["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        res = self.client.post(
            "/api/billing/verify",
            json={
                "razorpay_payment_id": "pay_test_111",
                "razorpay_subscription_id": "sub_test_222",
                "razorpay_signature": "invalid_signature_hash",
                "plan": "standard",
            },
            headers=headers,
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("Payment verification failed", res.json()["detail"])

    def test_webhook_valid_and_idempotent(self):
        reg = self.register_user("webhook@example.com", "Password123").json()
        token = reg["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        # Start a trial/sub
        self.client.post("/api/billing/trial/start", json={"plan": "standard"}, headers=headers)
        sub_info = self.client.get("/api/billing/subscription", headers=headers).json()
        sub_db_id = sub_info["id"]

        webhook_payload = {
            "id": "evt_test_unique_999",
            "entity": "event",
            "account_id": "acc_test",
            "event": "subscription.activated",
            "contains": ["subscription"],
            "payload": {
                "subscription": {
                    "entity": {
                        "id": "sub_rzp_live_abc",
                        "plan_id": "plan_test_std",
                        "customer_id": "cust_test",
                        "status": "active",
                        "current_start": int(time.time()),
                        "current_end": int(time.time()) + 2592000,
                        "notes": {"subscription_id": sub_db_id},
                    }
                }
            },
            "created_at": int(time.time()),
        }
        body_bytes = json.dumps(webhook_payload).encode("utf-8")
        signature = hmac.new(
            settings.razorpay_webhook_secret.encode("utf-8"),
            body_bytes,
            hashlib.sha256,
        ).hexdigest()

        # First webhook delivery -> processed
        res1 = self.client.post(
            "/api/webhooks/razorpay",
            content=body_bytes,
            headers={"X-Razorpay-Signature": signature, "Content-Type": "application/json"},
        )
        self.assertEqual(res1.status_code, 200)
        self.assertEqual(res1.json()["status"], "processed")

        # Second delivery with same event ID -> duplicate detected (idempotent!)
        res2 = self.client.post(
            "/api/webhooks/razorpay",
            content=body_bytes,
            headers={"X-Razorpay-Signature": signature, "Content-Type": "application/json"},
        )
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.json()["status"], "ignored")

    def test_webhook_invalid_signature_rejected(self):
        body = b'{"event": "subscription.charged"}'
        res = self.client.post(
            "/api/webhooks/razorpay",
            content=body,
            headers={"X-Razorpay-Signature": "tampered_signature", "Content-Type": "application/json"},
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("Invalid webhook signature", res.json()["detail"])


class DataIsolationTests(AuthBillingBaseTest):
    def test_cross_user_isolation(self):
        # User A registers, starts trial, uploads contract
        user_a = self.register_user("usera@example.com", "Password123").json()
        token_a = user_a["access_token"]
        headers_a = {"Authorization": f"Bearer {token_a}"}
        self.client.post("/api/billing/trial/start", json={"plan": "standard"}, headers=headers_a)

        contract_a = self.client.post(
            "/api/contracts/upload",
            files={"file": ("contract_a.pdf", sample_pdf(), "application/pdf")},
            headers=headers_a,
        ).json()
        contract_id_a = contract_a["contract_id"]

        # Run analysis for User A
        extracted = extract_contract(sample_pdf(), "contract_a.pdf")
        with patch("app.services.contract_analysis.match_policies", return_value=[]), \
             patch("app.services.contract_analysis.generate_analysis", return_value=sample_draft(extracted)):
            analysis_a = self.client.post("/api/analyze", json={"contract_id": contract_id_a}, headers=headers_a).json()
        analysis_id_a = analysis_a["analysis_id"]

        # User B registers and starts trial
        user_b = self.register_user("userb@example.com", "Password123").json()
        token_b = user_b["access_token"]
        headers_b = {"Authorization": f"Bearer {token_b}"}
        self.client.post("/api/billing/trial/start", json={"plan": "standard"}, headers=headers_b)

        # User B attempts to analyze User A's contract -> 404 (Contract not found for User B)
        res_analyze_unauth = self.client.post("/api/analyze", json={"contract_id": contract_id_a}, headers=headers_b)
        self.assertEqual(res_analyze_unauth.status_code, 404)

        # User B attempts to access User A's analysis -> 404 Not Found
        res_analysis = self.client.get(f"/api/analysis/{analysis_id_a}", headers=headers_b)
        self.assertEqual(res_analysis.status_code, 404)

        # User A CAN access their own analysis
        self.assertEqual(self.client.get(f"/api/analysis/{analysis_id_a}", headers=headers_a).status_code, 200)
