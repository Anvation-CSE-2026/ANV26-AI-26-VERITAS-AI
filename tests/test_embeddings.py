import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import httpx
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.config import Settings
from app.main import app
from app.services.ollama_embeddings import (
    EmbeddingError, EmbeddingTimeout, EmbeddingUnavailable, cosine_similarity, embed_text,
)


class EmbeddingTests(unittest.TestCase):
    def test_request_and_vector_validation(self):
        def handle(request):
            import json
            self.assertEqual(request.url.path, "/api/embed")
            body = json.loads(request.content)
            self.assertEqual(body["input"], "clause")
            self.assertFalse(body["truncate"])
            return httpx.Response(200, json={"embeddings": [[1, 0.5]]})
        client = httpx.Client(transport=httpx.MockTransport(handle))
        with patch("app.services.ollama_embeddings.httpx.Client", return_value=client):
            self.assertEqual(embed_text("clause"), [1.0, 0.5])

    def test_errors(self):
        for exception, expected in [
            (httpx.ConnectError("offline"), EmbeddingUnavailable),
            (httpx.ReadTimeout("slow"), EmbeddingTimeout),
        ]:
            with self.subTest(exception=exception), patch("httpx.Client.post", side_effect=exception):
                with self.assertRaises(expected):
                    embed_text("clause")
        for response in [httpx.Response(404, json={"error": "missing model"}),
                         httpx.Response(200, json={"embeddings": []}),
                         httpx.Response(200, json={"embeddings": [[True]]}),
                         httpx.Response(200, json={"embeddings": [[0, 0]]}),
                         httpx.Response(200, text="invalid JSON")]:
            response.request = httpx.Request("POST", "http://localhost:11434/api/embed")
            with self.subTest(response=response), patch("httpx.Client.post", return_value=response):
                with self.assertRaises(EmbeddingError):
                    embed_text("clause")
        with self.assertRaises(ValueError):
            embed_text(" ")

    def test_cosine(self):
        self.assertAlmostEqual(cosine_similarity([1, 0], [1, 0]), 1)
        self.assertAlmostEqual(cosine_similarity([1, 0], [0, 1]), 0)
        self.assertAlmostEqual(cosine_similarity([1, 0], [-1, 0]), -1)
        for left, right in [([], []), ([0], [1]), ([1], [1, 2]), ([float("nan")], [1])]:
            with self.assertRaises(ValueError):
                cosine_similarity(left, right)

    def test_model_setting_alias(self):
        self.assertEqual(Settings(_env_file=None, OLLAMA_EMBED_MODEL="new", OLLAMA_EMBEDDING_MODEL="old").ollama_embedding_model, "new")
        self.assertEqual(Settings(_env_file=None, OLLAMA_EMBEDDING_MODEL="old").ollama_embedding_model, "old")

    def test_endpoint_contract_and_errors(self):
        with TestClient(app) as client:
            with patch("app.routes.embeddings.embed_text", return_value=[1.0, 0.0]):
                response = client.post("/api/embeddings/test", json={"text": "clause"})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(set(response.json()), {"success", "model", "dimensions"})
                self.assertEqual(response.json()["dimensions"], 2)
            for error, status in [(EmbeddingTimeout("timeout"), 504),
                                  (EmbeddingUnavailable("offline"), 503),
                                  (EmbeddingError("bad response"), 502)]:
                with patch("app.routes.embeddings.embed_text", side_effect=error):
                    self.assertEqual(client.post("/api/embeddings/test", json={"text": "clause"}).status_code, status)
            for body in [{}, {"text": " "}, {"text": 42}]:
                self.assertEqual(client.post("/api/embeddings/test", json=body).status_code, 422)


@unittest.skipUnless(os.environ.get("RUN_OLLAMA_INTEGRATION") == "1", "Set RUN_OLLAMA_INTEGRATION=1 for real Ollama tests")
class RealOllamaTests(unittest.TestCase):
    def test_semantic_clause_policy_comparison(self):
        clause = embed_text("The supplier must notify the company within 48 hours of discovering a data breach.")
        related = embed_text("Vendors are required to report data security incidents to our company within two days.")
        unrelated = embed_text("Invoices are payable in US dollars thirty days after receipt.")
        related_score = cosine_similarity(clause, related)
        unrelated_score = cosine_similarity(clause, unrelated)
        print(f"Actual dimensions={len(clause)}; related={related_score:.6f}; unrelated={unrelated_score:.6f}")
        self.assertGreater(related_score, unrelated_score)

    def test_real_endpoint(self):
        with TestClient(app) as client:
            response = client.post("/api/embeddings/test", json={"text": "The supplier must notify the company within 48 hours."})
            print(f"Actual embedding endpoint: HTTP {response.status_code} {response.json()}")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(set(response.json()), {"success", "model", "dimensions"})
            self.assertTrue(response.json()["success"])
            self.assertGreater(response.json()["dimensions"], 0)


if __name__ == "__main__":
    unittest.main()
