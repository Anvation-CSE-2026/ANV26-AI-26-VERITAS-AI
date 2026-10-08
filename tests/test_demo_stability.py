import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

sys.path[:0] = [str(Path(__file__).resolve().parents[1] / "backend"), str(Path(__file__).parent)]
from app.main import app
from app.models.contracts import AnalysisDraft
from app.services.demo import load_demo
from app.services.gemini_analysis import GeminiError
from app.services.storage import get_failure
import test_contract_analysis as contract_tests
from test_contract_analysis import valid_draft


class DemoStabilityTests(unittest.TestCase):
    def test_demo_is_precomputed_repeatable_and_independent_of_services(self):
        with patch("app.services.gemini_analysis.genai.Client", side_effect=AssertionError("No live Gemini allowed")), patch("app.services.policy_matching.embed_text", side_effect=AssertionError("No Ollama allowed")), TestClient(app) as client:
            first = client.get("/api/demo/analysis")
            second = client.get("/api/demo/analysis")
        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.json(), second.json())
        payload = first.json()
        self.assertEqual(payload["label"], "SAMPLE ANALYSIS — DEMO DATA")
        self.assertFalse(payload["live_ai_used"])
        self.assertEqual(payload["analysis"]["output_origin"], "synthetic_demo")
        self.assertEqual(payload["analysis"]["gemini_attempts"], 0)
        self.assertEqual(len(payload["analysis"]["findings"]), 7)
        self.assertTrue(all(item["evidence_verified"] for item in payload["analysis"]["findings"]))

    def test_tampered_precomputed_quote_is_rejected(self):
        artifact = load_demo().model_dump(mode="json")
        artifact["analysis"]["findings"][0]["evidence_quote"] = "Fabricated quote."
        with patch("app.services.demo.Path.read_text", return_value=json.dumps(artifact)), self.assertRaises(ValueError):
            load_demo()

    def test_tampered_demo_cannot_claim_live_generation(self):
        artifact = load_demo().model_dump(mode="json")
        artifact["analysis"]["gemini_attempts"] = 1
        with patch("app.services.demo.Path.read_text", return_value=json.dumps(artifact)), self.assertRaises(ValueError):
            load_demo()


class FailurePersistenceTests(unittest.TestCase):
    setUp = contract_tests.ContractAPITests.setUp
    upload = contract_tests.ContractAPITests.upload

    def test_failed_gemini_attempt_is_saved_and_retrievable_without_findings(self):
        uploaded = self.upload()
        error = GeminiError("Gemini service is temporarily unavailable.", 503, attempts=3,
                            upstream_status=503, category="provider_transient")
        with patch("app.services.contract_analysis.match_policies", return_value=[]), patch("app.services.contract_analysis.generate_analysis", side_effect=error):
            response = self.client.post("/api/analyze", json={"contract_id": uploaded["contract_id"]})
        self.assertEqual(response.status_code, 503)
        detail = response.json()["detail"]
        self.assertEqual(detail["state"], "failed")
        self.assertTrue(detail["failure_recorded"])
        self.assertEqual(detail["gemini_attempts"], 3)
        result = self.client.get("/api/analysis/" + detail["analysis_id"])
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json()["status"], "failed")
        self.assertTrue(result.json()["retries_occurred"])
        self.assertEqual(result.json()["upstream_http_status"], 503)
        self.assertNotIn("findings", result.json())
        self.assertEqual(get_failure(detail["analysis_id"]).contract_id, uploaded["contract_id"])

    def test_evidence_failure_is_recorded_as_failure_not_success(self):
        uploaded = self.upload()
        from app.services.storage import get_contract
        draft = valid_draft(get_contract(uploaded["contract_id"]))
        draft.findings[0].evidence_quote = "Fabricated quote."
        draft.obligations = []
        with patch("app.services.contract_analysis.match_policies", return_value=[]), patch("app.services.contract_analysis.generate_analysis", return_value=draft):
            response = self.client.post("/api/analyze", json={"contract_id": uploaded["contract_id"]})
        self.assertEqual(response.status_code, 502)
        failure = self.client.get("/api/analysis/" + response.json()["detail"]["analysis_id"]).json()
        self.assertEqual(failure["failed_stage"], "evidence_verification")
        self.assertEqual(failure["verification_rejections"][0]["evidence_status"], "unsupported")
        self.assertNotIn("findings", failure)

    def test_demo_is_not_an_accepted_live_analyze_mode(self):
        response = self.client.post("/api/analyze", json={"contract_id": "missing", "mode": "demo"})
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
