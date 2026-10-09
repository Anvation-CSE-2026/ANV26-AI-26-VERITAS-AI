from contextlib import closing
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import httpx
import pymupdf
from fastapi.testclient import TestClient
from google.genai import errors

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.config import Settings, settings
from app.main import app
from app.models.contracts import AnalysisDraft, ObligationDraft, RiskDraft
from app.services.evidence import EvidenceError, verify_analysis
from app.services.gemini_analysis import GeminiError, analysis_response_schema, generate_analysis
from app.services.ollama_embeddings import EmbeddingError, EmbeddingTimeout, EmbeddingUnavailable
from app.services.pdf_extraction import ContractLimitError, PDFError, extract_contract
from app.services.playbook import load_playbook
from app.services.policy_matching import match_policies, policy_vectors
from app.services.storage import get_contract
from sample_pdf import sample_pdf


def source():
    return extract_contract(sample_pdf(), "synthetic.pdf")


def valid_draft(contract):
    clause = next(c for c in contract.clauses if "1. Liability" in c.text)
    obligation_clause = next(c for c in contract.clauses if "8. Reporting" in c.text)
    return AnalysisDraft(findings=[RiskDraft(
        risk_level="high", clause_category="liability", explanation="The low liability cap conflicts with the sample policy.",
        evidence_quote=clause.text, page_number=clause.page_number, clause_id=clause.clause_id,
        policy_id="POL-LIAB-001", recommended_action="Negotiate a higher cap and exclusions.",
    )], obligations=[ObligationDraft(
        description="Deliver the monthly service report.", evidence_quote=obligation_clause.text,
        page_number=obligation_clause.page_number, clause_id=obligation_clause.clause_id,
        responsible_party="Supplier", deadline="by the fifth day of each month",
    )])


class ExtractionTests(unittest.TestCase):
    def test_default_storage_is_inside_project(self):
        default = Settings(_env_file=None).storage_path
        self.assertTrue(default.is_relative_to(Path(__file__).resolve().parents[1]))

    def test_original_page_text_and_exact_clause_offsets(self):
        pdf_bytes = sample_pdf()
        contract = extract_contract(pdf_bytes, "synthetic.pdf")
        self.assertEqual(len(contract.pages), 2)
        self.assertEqual(len({c.clause_id for c in contract.clauses}), len(contract.clauses))
        with pymupdf.open(stream=pdf_bytes, filetype="pdf") as pdf:
            for index, page in enumerate(contract.pages):
                self.assertEqual(page.text, pdf[index].get_text("text", sort=True))
        for clause in contract.clauses:
            text = contract.pages[clause.page_number - 1].text
            self.assertEqual(clause.text, text[clause.start_offset:clause.end_offset])
        self.assertEqual([c.model_dump() for c in contract.clauses], [c.model_dump() for c in source().clauses])

    def test_invalid_scanned_and_encrypted_pdfs(self):
        for value in [b"", b"not a PDF", b"%PDF-1.7 invalid"]:
            with self.assertRaises(PDFError):
                extract_contract(value, "bad.pdf")
        with pymupdf.open() as doc:
            doc.new_page()
            empty = doc.tobytes()
            encrypted = doc.tobytes(encryption=pymupdf.PDF_ENCRYPT_AES_256, owner_pw="owner", user_pw="user")
        for value in [empty, encrypted]:
            with self.assertRaises(PDFError):
                extract_contract(value, "unsupported.pdf")

    def test_limits(self):
        for field, value in [("max_upload_bytes", 10), ("max_contract_pages", 1),
                             ("max_contract_chars", 10), ("max_contract_clauses", 1)]:
            with self.subTest(field=field), patch.object(settings, field, value):
                with self.assertRaises(ContractLimitError):
                    source()

    def test_blank_page_warning_and_long_clause_preservation(self):
        with pymupdf.open() as doc:
            page = doc.new_page()
            page.insert_text((45, 45), "Supplier shall perform the services.")
            doc.new_page()
            contract = extract_contract(doc.tobytes(), "mixed.pdf")
        self.assertIn("Page 2", contract.warnings[0])
        from app.models.contracts import PageText
        from app.services.pdf_extraction import split_clauses
        original = PageText(page_number=1, text="word " * 1000)
        clauses = split_clauses(original)
        self.assertGreater(len(clauses), 1)
        self.assertEqual(" ".join(c.text for c in clauses).split(), original.text.split())


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.contract, self.playbook = source(), load_playbook()
        self.draft = valid_draft(self.contract)

    def test_valid_evidence_and_policy_are_resolved(self):
        findings, obligations, rejected = verify_analysis(self.draft, self.contract, self.playbook)
        self.assertEqual(rejected, [])
        self.assertEqual(findings[0].applicable_policy_rule.policy_id, "POL-LIAB-001")
        self.assertTrue(findings[0].evidence_verified)
        self.assertEqual(obligations[0].deadline, "by the fifth day of each month")

    def test_fabricated_quote_page_clause_policy_and_category_are_rejected(self):
        for field, value, reason in [
            ("evidence_quote", "Supplier has unlimited liability.", "quote_not_in_original_clause"),
            ("page_number", 2, "wrong_page_number"),
            ("clause_id", "invented", "unknown_clause_id"),
            ("policy_id", "POL-INVENTED", "unknown_policy_id"),
            ("clause_category", "payment", "policy_category_mismatch"),
        ]:
            draft = self.draft.model_copy(deep=True)
            setattr(draft.findings[0], field, value)
            with self.subTest(field=field):
                findings, obligations, rejected = verify_analysis(draft, self.contract, self.playbook)
                self.assertEqual(findings, [])
                self.assertEqual(len(obligations), 1)
                self.assertEqual(rejected[0].reason, reason)

    def test_whitespace_restores_original_slice_but_source_offsets_stay_strict(self):
        draft = self.draft.model_copy(deep=True)
        draft.findings[0].evidence_quote = draft.findings[0].evidence_quote.replace("\n", " ")
        verified = verify_analysis(draft, self.contract, self.playbook)
        self.assertEqual(verified[2], [])
        self.assertEqual(verified[0][0].evidence_quote, self.draft.findings[0].evidence_quote)
        contract = self.contract.model_copy(deep=True)
        clause = next(c for c in contract.clauses if c.clause_id == draft.findings[0].clause_id)
        clause.start_offset += 1
        self.assertEqual(verify_analysis(self.draft, contract, self.playbook)[2][0].reason, "source_offset_mismatch")

    def test_inferred_party_deadline_and_missing_clause_evidence_are_rejected(self):
        for field, value in [("responsible_party", "Legal Department"), ("deadline", "2026-11-05")]:
            draft = self.draft.model_copy(deep=True)
            setattr(draft.obligations[0], field, value)
            with self.subTest(field=field):
                self.assertEqual(verify_analysis(draft, self.contract, self.playbook)[1], [])
        draft = self.draft.model_copy(deep=True)
        draft.obligations[0].deadline = None
        draft.obligations[0].responsible_party = None
        self.assertEqual(len(verify_analysis(draft, self.contract, self.playbook)[1]), 1)
        draft = self.draft.model_copy(deep=True)
        draft.findings[0].evidence_quote = "No liability clause exists."
        draft.obligations = []
        with self.assertRaises(EvidenceError):
            verify_analysis(draft, self.contract, self.playbook)

    def test_empty_model_output_is_not_populated_with_fake_findings(self):
        self.assertEqual(verify_analysis(AnalysisDraft(findings=[], obligations=[]), self.contract, self.playbook), ([], [], []))


class RetrievalTests(unittest.TestCase):
    def test_actual_vector_ranking_and_cache(self):
        policy_vectors.cache_clear()
        book = load_playbook()
        contract = source().model_copy(deep=True)
        contract.clauses = contract.clauses[:1]
        with patch("app.services.policy_matching.embed_text", side_effect=[[1, 0]] + [[0, 1]] * 6 + [[1, 0], [1, 0]]) as embed:
            matches = match_policies(contract, book)
            self.assertEqual(matches[0].policy_id, "POL-LIAB-001")
            self.assertEqual(matches[0].similarity, 1.0)
            self.assertEqual(len(matches), 3)
            match_policies(contract, book)
            self.assertEqual(embed.call_count, 9)
        policy_vectors.cache_clear()


class GeminiTests(unittest.TestCase):
    def setUp(self):
        sleep_patch = patch("app.services.gemini_analysis.time.sleep")
        sleep_patch.start()
        self.addCleanup(sleep_patch.stop)
        self.contract, self.playbook = source(), load_playbook()
        self.key_patch = patch.object(settings, "gemini_api_key", "test-secret-must-never-escape")
        self.key_patch.start()
        self.addCleanup(self.key_patch.stop)

    def fake_client(self, output=None, error=None):
        mock = MagicMock()
        service = mock.return_value.__enter__.return_value
        if error:
            service.models.generate_content.side_effect = error
        else:
            service.models.generate_content.return_value = SimpleNamespace(text=output)
        return mock

    def test_structured_output_and_no_secret_in_prompt(self):
        draft = valid_draft(self.contract)
        mock = self.fake_client(draft.model_dump_json())
        with patch("app.services.gemini_analysis.genai.Client", mock):
            self.assertEqual(generate_analysis(self.contract, self.playbook, []), draft)
        kwargs = mock.return_value.__enter__.return_value.models.generate_content.call_args.kwargs
        self.assertNotIn(settings.gemini_api_key, kwargs["contents"])
        self.assertEqual(kwargs["config"].response_json_schema, analysis_response_schema())
        self.assertNotIn(settings.gemini_api_key, repr(settings))

    def test_api_errors_rate_limits_timeouts_and_sanitization(self):
        for error, status in [
            (errors.APIError(429, {"error": {"message": settings.gemini_api_key}}), 429),
            (errors.APIError(403, {"error": {"message": settings.gemini_api_key}}), 502),
            (errors.APIError(404, {"error": {"message": settings.gemini_api_key}}), 502),
            (errors.APIError(503, {"error": {"message": settings.gemini_api_key}}), 503),
            (errors.APIError(400, {"error": {"message": settings.gemini_api_key}}), 502),
            (httpx.ReadTimeout(settings.gemini_api_key), 504),
            (httpx.ConnectError(settings.gemini_api_key), 503),
            (RuntimeError(settings.gemini_api_key), 502),
        ]:
            with self.subTest(status=status), patch("app.services.gemini_analysis.genai.Client", self.fake_client(error=error)):
                with self.assertRaises(GeminiError) as caught:
                    generate_analysis(self.contract, self.playbook, [])
                self.assertEqual(caught.exception.status_code, status)
                self.assertNotIn(settings.gemini_api_key, str(caught.exception))
                if status == 429:
                    self.assertEqual(caught.exception.retry_after, "60")

    def test_empty_malformed_and_wrong_schema_outputs_fail(self):
        for text in [None, "not json", '{"findings": [], "obligations": [], "extra": true}', '{}']:
            with patch("app.services.gemini_analysis.genai.Client", self.fake_client(text)):
                with self.assertRaises(GeminiError):
                    generate_analysis(self.contract, self.playbook, [])

    def test_missing_configuration(self):
        with patch.object(settings, "gemini_api_key", ""):
            with self.assertRaises(GeminiError) as caught:
                generate_analysis(self.contract, self.playbook, [])
            self.assertEqual(caught.exception.status_code, 503)


class ContractAPITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        database_patch = patch.object(settings, "database_url", "")
        database_patch.start()
        self.addCleanup(database_patch.stop)
        self.storage_patch = patch.object(settings, "storage_path", Path(self.temp.name) / "test.sqlite3")
        self.storage_patch.start()
        self.addCleanup(self.storage_patch.stop)
        self.key_patch = patch.object(settings, "gemini_api_key", "test-only-secret")
        self.key_patch.start()
        self.addCleanup(self.key_patch.stop)
        self.client = TestClient(app)
        self.addCleanup(self.client.close)
        reg = self.client.post("/api/auth/register", json={"email": "tester@veritas.internal", "password": "password123"})
        self.token = reg.json()["access_token"]
        self.client.headers["Authorization"] = f"Bearer {self.token}"
        self.client.post("/api/billing/trial/start", json={"plan": "pro"})

    def upload(self):
        response = self.client.post("/api/contracts/upload", files={"file": ("synthetic.pdf", sample_pdf(), "application/pdf")})
        self.assertEqual(response.status_code, 201)
        return response.json()

    def test_upload_analyze_fetch_and_persistence(self):
        uploaded = self.upload()
        contract = get_contract(uploaded["contract_id"])
        self.assertEqual(contract.model_dump(), uploaded)
        with closing(sqlite3.connect(settings.storage_path)) as conn:
            pdf_bytes = conn.execute("SELECT pdf FROM contracts WHERE id=?", (contract.contract_id,)).fetchone()[0]
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))
        with patch("app.services.contract_analysis.match_policies", return_value=[]), patch("app.services.contract_analysis.generate_analysis", return_value=valid_draft(contract)):
            response = self.client.post("/api/analyze", json={"contract_id": contract.contract_id})
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["findings"][0]["applicable_policy_rule"]["policy_id"], "POL-LIAB-001")
        self.assertNotIn(settings.gemini_api_key, response.text)
        self.assertEqual(self.client.get("/api/analysis/" + result["analysis_id"]).json(), result)
        with TestClient(app) as another_client:
            another_client.headers["Authorization"] = f"Bearer {self.token}"
            self.assertEqual(another_client.get("/api/analysis/" + result["analysis_id"]).status_code, 200)

    def test_partial_and_all_rejected_output(self):
        uploaded = self.upload()
        contract = get_contract(uploaded["contract_id"])
        draft = valid_draft(contract)
        draft.findings[0].evidence_quote = "Fabricated quotation."
        with patch("app.services.contract_analysis.match_policies", return_value=[]), patch("app.services.contract_analysis.generate_analysis", return_value=draft):
            response = self.client.post("/api/analyze", json={"contract_id": contract.contract_id})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["status"], "partial")
            self.assertEqual(response.json()["findings"], [])
            self.assertNotIn("Fabricated quotation", response.text)
            draft.obligations = []
            failed = self.client.post("/api/analyze", json={"contract_id": contract.contract_id})
            self.assertEqual(failed.status_code, 502)
        with closing(sqlite3.connect(settings.storage_path)) as conn:
            self.assertEqual(conn.execute("SELECT count(*) FROM analyses").fetchone()[0], 1)

    def test_invalid_uploads_missing_ids_and_request_validation(self):
        for filename, content, status in [("file.txt", b"text", 415), ("bad.pdf", b"invalid", 422)]:
            self.assertEqual(self.client.post("/api/contracts/upload", files={"file": (filename, content)}).status_code, status)
        self.assertEqual(self.client.post("/api/contracts/upload").status_code, 422)
        with patch.object(settings, "max_upload_bytes", 10):
            self.assertEqual(self.client.post("/api/contracts/upload", files={"file": ("big.pdf", sample_pdf())}).status_code, 413)
        self.assertEqual(self.client.post("/api/analyze", json={"contract_id": "missing"}).status_code, 404)
        self.assertEqual(self.client.post("/api/analyze", json={}).status_code, 422)
        self.assertEqual(self.client.get("/api/analysis/missing").status_code, 404)

    def test_model_errors_return_no_findings_or_saved_success(self):
        uploaded = self.upload()
        for error, status in [(GeminiError("Rate limited.", 429, "60"), 429), (GeminiError("Access rejected.", 502), 502),
                              (EmbeddingUnavailable("offline"), 503), (EmbeddingTimeout("slow"), 504), (EmbeddingError("bad"), 502)]:
            with patch("app.routes.contracts.analyze_contract", side_effect=error):
                response = self.client.post("/api/analyze", json={"contract_id": uploaded["contract_id"]})
            self.assertEqual(response.status_code, status)
            self.assertNotIn("findings", response.json())
            if isinstance(error, GeminiError):
                self.assertEqual(response.json()["detail"]["state"], "failed")
            if status == 429:
                self.assertEqual(response.headers["retry-after"], "60")
        with closing(sqlite3.connect(settings.storage_path)) as conn:
            self.assertEqual(conn.execute("SELECT count(*) FROM analyses").fetchone()[0], 0)
        with patch.object(settings, "gemini_api_key", ""):
            self.assertEqual(self.client.post("/api/analyze", json={"contract_id": uploaded["contract_id"]}).status_code, 503)

    def test_storage_failure_is_sanitized(self):
        with patch("app.routes.contracts.get_analysis", side_effect=sqlite3.OperationalError("private storage path")):
            response = self.client.get("/api/analysis/anything")
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("private", response.text)


@unittest.skipUnless(os.environ.get("RUN_AI_INTEGRATION") == "1", "Set RUN_AI_INTEGRATION=1 for real Gemini/Ollama HTTP E2E")
class RealAIIntegrationTests(unittest.TestCase):
    def test_real_upload_analyze_and_fetch(self):
        script = Path(__file__).parent / "verify_ai_http.py"
        result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, timeout=600)
        print(result.stdout)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
