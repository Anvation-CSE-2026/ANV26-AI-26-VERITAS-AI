"""Offline provider, SDK wire-format, cache isolation and cloud storage checks."""
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import httpx
from fastapi.testclient import TestClient
from google import genai
from google.genai import errors
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.config import Settings, settings
from app.main import app
from app.services import embeddings, gemini_embeddings, policy_matching
from app.services.contract_analysis import analyze_contract
from app.services.storage import connection, get_failure, get_contract, save_contract
from evaluation.dataset_loader import load_dataset
from evaluation.offline_guard import no_network
from app.services.playbook import load_playbook
from test_contract_analysis import source, valid_draft
from sample_pdf import sample_pdf


class EmbeddingProviderTests(unittest.TestCase):
    def setUp(self):
        for field, value in {"embedding_provider": "gemini", "gemini_api_key": "synthetic-secret",
                             "gemini_embedding_model": "gemini-embedding-001",
                             "gemini_embedding_dimensions": 768}.items():
            mock = patch.object(settings, field, value)
            mock.start()
            self.addCleanup(mock.stop)
        policy_matching.policy_vectors.cache_clear()
        self.addCleanup(policy_matching.policy_vectors.cache_clear)
        self.contract = load_dataset().cases[0].contract
        self.book = load_playbook()

    def client(self, response=None, error=None):
        factory = MagicMock()
        client = factory.return_value.__enter__.return_value
        client.models.embed_content.return_value = response or SimpleNamespace(
            embeddings=[SimpleNamespace(values=[1.0] + [0.0] * 767)])
        client.models.embed_content.side_effect = error
        return factory, client

    def test_defaults_selection_and_invalid_provider(self):
        with patch.dict(os.environ, {"EMBEDDING_PROVIDER": "ollama"}):
            self.assertEqual(Settings(_env_file=None).embedding_provider, "ollama")
        with patch.dict(os.environ, {"EMBEDDING_PROVIDER": "gemini"}):
            self.assertEqual(Settings(_env_file=None).embedding_provider, "gemini")
        with self.assertRaises(ValidationError):
            Settings(_env_file=None, embedding_provider="unknown")
        with patch.object(settings, "embedding_provider", "ollama"), \
             patch("app.services.ollama_embeddings.embed_text", return_value=[1.0, 0.0]) as ollama:
            self.assertEqual(embeddings.embed_text(" exact text "), [1.0, 0.0])
            ollama.assert_called_once_with(" exact text ")

    def test_sdk_request_and_no_reasoning_or_retry(self):
        calls = []
        def handler(request):
            calls.append(request)
            self.assertEqual(request.url.path, "/v1beta/models/gemini-embedding-001:batchEmbedContents")
            body = json.loads(request.content)["requests"][0]
            self.assertEqual(body["content"]["parts"][0]["text"], " exact\nsynthetic clause ")
            self.assertEqual(body["taskType"], "SEMANTIC_SIMILARITY")
            self.assertEqual(body["outputDimensionality"], 768)
            return httpx.Response(200, json={"embeddings": [{"values": [1.0] + [0.0] * 767}]})
        real_client = genai.Client
        def factory(**kwargs):
            self.assertFalse(kwargs["vertexai"])
            self.assertEqual(kwargs["http_options"].base_url, "https://generativelanguage.googleapis.com")
            self.assertEqual(kwargs["http_options"].timeout, 60000)
            self.assertEqual(kwargs["http_options"].retry_options.attempts, 1)
            kwargs["http_options"].httpx_client = httpx.Client(transport=httpx.MockTransport(handler))
            return real_client(**kwargs)
        with no_network(), patch("app.services.gemini_embeddings.genai.Client", side_effect=factory):
            self.assertEqual(embeddings.embed_text(" exact\nsynthetic clause "), [1.0] + [0.0] * 767)
        self.assertEqual(len(calls), 1)

    def test_errors_are_sanitized_bounded_and_structured(self):
        for code, status, category in [(400, 502, "embedding_provider_error"),
                                      (401, 502, "embedding_authentication"),
                                      (403, 502, "embedding_authentication"),
                                      (404, 502, "embedding_model_unavailable"),
                                      (429, 429, "embedding_rate_limit"),
                                      (503, 503, "embedding_provider_error"),
                                      (504, 504, "embedding_timeout")]:
            factory, client = self.client(error=errors.APIError(code, {"error": {
                "code": code, "message": "synthetic-secret private-clause"}}))
            with self.subTest(code=code), no_network(), \
                 patch("app.services.gemini_embeddings.genai.Client", factory):
                with self.assertRaises(gemini_embeddings.HostedEmbeddingError) as caught:
                    embeddings.embed_text("private-clause")
            self.assertEqual(caught.exception.status_code, status)
            self.assertEqual(caught.exception.category, category)
            self.assertEqual(caught.exception.upstream_status, code)
            self.assertNotIn("synthetic-secret", str(caught.exception.detail()))
            self.assertNotIn("private-clause", str(caught.exception.detail()))
            self.assertEqual(client.models.embed_content.call_count, 1)
            self.assertIsNone(gemini_embeddings._client_scope.get())

    def test_sdk_http_429_has_one_attempt(self):
        calls = []
        def handler(request):
            calls.append(request)
            return httpx.Response(429, json={"error": {"code": 429, "message": "synthetic"}})
        real_client = genai.Client
        def factory(**kwargs):
            kwargs["http_options"].httpx_client = httpx.Client(transport=httpx.MockTransport(handler))
            return real_client(**kwargs)
        with no_network(), patch("app.services.gemini_embeddings.genai.Client", side_effect=factory):
            with self.assertRaises(gemini_embeddings.HostedEmbeddingError):
                embeddings.embed_text("synthetic")
        self.assertEqual(len(calls), 1)

    def test_timeout_connection_and_invalid_response(self):
        for error, status in [(httpx.ReadTimeout("private-clause"), 504),
                              (httpx.ConnectError("synthetic-secret"), 503),
                              (ValueError("private-clause"), 502)]:
            factory, _ = self.client(error=error)
            with patch("app.services.gemini_embeddings.genai.Client", factory):
                with self.assertRaises(gemini_embeddings.HostedEmbeddingError) as caught:
                    embeddings.embed_text("synthetic")
                self.assertEqual(caught.exception.status_code, status)
        for vector in ([], [1.0], [0.0] * 768, [True] * 768, [float("nan")] * 768,
                       [float("inf")] * 768):
            factory, _ = self.client(SimpleNamespace(embeddings=[SimpleNamespace(values=vector)]))
            with self.subTest(vector_length=len(vector)), patch("app.services.gemini_embeddings.genai.Client", factory):
                with self.assertRaises(gemini_embeddings.HostedEmbeddingError):
                    embeddings.embed_text("synthetic")
        with patch.object(settings, "gemini_api_key", ""), \
             patch("app.services.gemini_embeddings.genai.Client") as factory:
            with self.assertRaises(gemini_embeddings.HostedEmbeddingError):
                embeddings.embed_text("synthetic")
            factory.assert_not_called()

    def test_cache_isolated_by_provider_model_dimensions_timeout_credentials(self):
        rules = ("synthetic policy",)
        factory, _ = self.client()
        with no_network(), patch("app.services.gemini_embeddings.genai.Client", factory), \
             patch.object(policy_matching, "embed_text", return_value=[1.0, 0.0]) as embed:
            def vectors():
                return policy_matching.policy_vectors(settings.ollama_base_url,
                                                     settings.ollama_embedding_model, rules)
            vectors(); vectors()
            self.assertEqual(embed.call_count, 1)
            for field, value in [("embedding_provider", "ollama"),
                                 ("gemini_embedding_model", "synthetic-other-model"),
                                 ("gemini_embedding_dimensions", 1536),
                                 ("gemini_embedding_timeout_seconds", 61),
                                 ("gemini_api_key", "other-synthetic-key"),
                                 ("ollama_read_timeout", 121)]:
                # Last setting affects only Ollama: verify that space independently.
                provider = "ollama" if field.startswith("ollama_") else settings.embedding_provider
                with patch.object(settings, "embedding_provider", provider), patch.object(settings, field, value):
                    before = embed.call_count
                    vectors(); vectors()
                    self.assertEqual(embed.call_count, before + 1)
            self.assertNotIn("synthetic-secret", str(embeddings.embedding_cache_key()))

    def test_hosted_retrieval_reuses_client_and_preserves_duplicates_order_scores(self):
        factory, client = self.client()
        original = self.contract.model_dump()
        with no_network(), patch("app.services.gemini_embeddings.genai.Client", factory):
            first = policy_matching.match_policies(self.contract, self.book)
            self.assertEqual(client.models.embed_content.call_count, 11)
            second = policy_matching.match_policies(self.contract, self.book)
        self.assertEqual(client.models.embed_content.call_count, 15)
        self.assertEqual(factory.call_count, 2)
        self.assertEqual(factory.return_value.__exit__.call_count, 2)
        self.assertEqual(first, second)
        self.assertEqual(self.contract.model_dump(), original)
        self.assertEqual([m.clause_id for m in first], [c.clause_id for c in self.contract.clauses for _ in range(3)])
        self.assertEqual([m.policy_id for m in first[:3]], [r.policy_id for r in self.book.rules[:3]])
        self.assertTrue(all(abs(m.similarity - 1.0) < 1e-12 for m in first))

    def test_no_sensitive_output(self):
        factory, _ = self.client()
        out, err = io.StringIO(), io.StringIO()
        with no_network(), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), \
             patch("app.services.gemini_embeddings.genai.Client", factory):
            embeddings.embed_text("private-clause")
        self.assertEqual(out.getvalue() + err.getvalue(), "")

    def test_hosted_and_production_diagnostics_require_authentication(self):
        with TestClient(app) as client, patch("app.routes.embeddings.embed_text") as embed:
            for provider, environment in [("gemini", "development"), ("ollama", "production")]:
                with patch.object(settings, "embedding_provider", provider), \
                     patch.object(settings, "environment", environment), \
                     patch.object(settings, "allow_legacy_unauthenticated_access", True):
                    self.assertEqual(client.post("/api/embeddings/test", json={"text": "synthetic"}).status_code, 401)
                    self.assertEqual(client.post("/api/embeddings/test", json={"text": "synthetic"},
                                                headers={"Authorization": "Bearer invalid"}).status_code, 401)
            embed.assert_not_called()
        with TestClient(app) as client, \
             patch("app.routes.embeddings.get_current_user", return_value=SimpleNamespace(id="synthetic")), \
             patch("app.routes.embeddings.embed_text", return_value=[1.0] * 768):
            response = client.post("/api/embeddings/test", json={"text": "synthetic"},
                                   headers={"Authorization": "Bearer synthetic-token"})
            self.assertEqual(response.json(), {"success": True, "model": "gemini-embedding-001", "dimensions": 768})

    def test_failure_is_persisted_without_losing_upload_and_reasoning_is_not_called(self):
        contract = source()
        error = gemini_embeddings.HostedEmbeddingError("Gemini embedding service rejected the request.",
                                                      "embedding_rate_limit", 429, 429)
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(settings, "database_url", ""), patch.object(settings, "storage_path", Path(directory) / "nested" / "veritas.sqlite3"), \
             patch("app.services.contract_analysis.match_policies", side_effect=error), \
             patch("app.services.contract_analysis.generate_analysis") as reasoning:
            save_contract(contract, b"synthetic PDF fixture")
            with self.assertRaises(gemini_embeddings.HostedEmbeddingError):
                analyze_contract(contract)
            failure = get_failure(error.analysis_id)
            self.assertEqual(failure.error_category, "embedding_rate_limit")
            self.assertEqual(failure.http_status, 429)
            self.assertEqual(failure.upstream_http_status, 429)
            self.assertEqual(failure.failed_stage, "policy_retrieval")
            self.assertEqual(get_contract(contract.contract_id), contract)
            reasoning.assert_not_called()

    def test_analysis_metadata_uses_selected_model(self):
        contract = source()
        with no_network(), patch("app.services.contract_analysis.match_policies", return_value=[]), \
             patch("app.services.contract_analysis.generate_analysis", return_value=valid_draft(contract)), \
             patch("app.services.contract_analysis.save_analysis"):
            result = analyze_contract(contract)
        self.assertEqual(result.embedding_model, "gemini-embedding-001")
        self.assertTrue(result.findings[0].evidence_verified)

    def test_authenticated_analysis_api_reports_hosted_failure_and_saved_upload(self):
        factory, sdk = self.client(error=errors.APIError(429, {"error": {
            "code": 429, "message": "synthetic-secret private-clause"}}))
        with tempfile.TemporaryDirectory() as directory, no_network(), \
             patch.object(settings, "database_url", ""), patch.object(settings, "storage_path", Path(directory) / "veritas.sqlite3"), \
             patch("app.services.gemini_embeddings.genai.Client", factory), TestClient(app) as client:
            registered = client.post("/api/auth/register", json={"email": "cloud@test.invalid", "password": "synthetic-password"})
            client.headers["Authorization"] = "Bearer " + registered.json()["access_token"]
            self.assertEqual(client.post("/api/billing/trial/start", json={"plan": "pro"}).status_code, 201)
            uploaded = client.post("/api/contracts/upload", files={"file": ("synthetic.pdf", sample_pdf(), "application/pdf")})
            self.assertEqual(uploaded.status_code, 201)
            failed = client.post("/api/analyze", json={"contract_id": uploaded.json()["contract_id"]})
            self.assertEqual(failed.status_code, 429)
            detail = failed.json()["detail"]
            self.assertEqual(detail["error_category"], "embedding_rate_limit")
            self.assertEqual(detail["embedding_provider"], "gemini")
            self.assertEqual(detail["embedding_model"], "gemini-embedding-001")
            self.assertTrue(detail["failure_recorded"])
            self.assertNotIn("synthetic-secret", failed.text)
            self.assertNotIn("private-clause", failed.text)
            self.assertEqual(client.get("/api/analysis/" + detail["analysis_id"]).json()["status"], "failed")
            self.assertIsNotNone(get_contract(uploaded.json()["contract_id"]))
            with connection() as conn:
                self.assertEqual(conn.execute("SELECT count(*) FROM analyses").fetchone()[0], 0)
            self.assertEqual(sdk.models.embed_content.call_count, 1)
            sdk.models.generate_content.assert_not_called()

    def test_storage_path_environment_initializes_nested_directory_and_tables(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "render-disk" / "nested" / "veritas.sqlite3"
            with patch.dict(os.environ, {"STORAGE_PATH": str(path)}):
                config = Settings(_env_file=None)
                self.assertEqual(config.storage_path, path)
            with patch.object(settings, "database_url", ""), patch.object(settings, "storage_path", config.storage_path):
                with connection() as conn:
                    tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                self.assertTrue({"contracts", "analyses", "analysis_failures", "users"}.issubset(tables))
            self.assertTrue(path.is_file())


if __name__ == "__main__":
    unittest.main()
