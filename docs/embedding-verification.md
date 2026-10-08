# Ollama embedding verification

Verified October 8, 2026 against local Ollama 0.40.1 at http://localhost:11434.

## Implemented

- Synchronous embed_text(text: str) -> list[float] in backend/app/services/ollama_embeddings.py.
- POST /api/embed only; no chat endpoint or chat-model use.
- POST /api/embeddings/test returns success, configured model, and actual dimensions only.
- Configurable base URL, model, connection timeout (5 seconds), and read timeout (120 seconds). Legacy OLLAMA_EMBEDDING_MODEL remains compatible.
- Validates nonblank input and finite, nonempty, nonzero vectors. Rejects silent context truncation.
- HTTP errors: 422 invalid input, 503 connection failures, 504 timeout, 502 upstream errors/invalid responses. Upstream response bodies and input text are not exposed in errors.
- Cosine similarity with dimension, finite-value, and zero-norm validation.
- Frontend untouched. HTTPX already installed and pinned; requirements files unchanged.

## Actual results

Initial real calls failed: Ollama was reachable but /api/tags returned an empty model list. POST /api/embed returned HTTP 404 with model-not-found; our test endpoint correctly returned 502. The requested qwen3-embedding:0.6b model was then pulled through Ollama.

Final full suite: 10 tests passed, zero failures or skips, including existing health/CORS tests and both real Ollama tests. The real embedding dimension was 1024.

Actual semantic comparison:

- Contract: The supplier must notify the company within 48 hours of discovering a data breach.
- Related policy: Vendors are required to report data security incidents to our company within two days.
- Unrelated rule: Invoices are payable in US dollars thirty days after receipt.
- Related cosine similarity: 0.771340.
- Unrelated cosine similarity: 0.427288.

These are measured scores for these specific texts, not general compliance thresholds.

A separate real HTTP smoke check launched an isolated Uvicorn server and stopped it afterward. POST /api/embeddings/test returned HTTP 200 with {"success":true,"model":"qwen3-embedding:0.6b","dimensions":1024}. GET /health returned HTTP 200 with its unchanged response contract.

Python dependency check: No broken requirements found.

## Remaining limitations

No functional failures remain in the performed checks. Starlette emits a deprecation warning for HTTPX-backed TestClient; tests still pass, and no dependency upgrade was introduced. Connection/timeout/malformed-response cases were tested with mocks, not by disrupting the running Ollama service. Production load, large-document retrieval, and policy compliance decisions were not tested.

## Reproduce

From the workspace root in PowerShell:

~~~powershell
$env:RUN_OLLAMA_INTEGRATION="1"
.\backend\.venv\Scripts\python.exe -m unittest discover -s tests -v
Remove-Item Env:RUN_OLLAMA_INTEGRATION
.\backend\.venv\Scripts\python.exe tests/verify_embedding_http.py
.\backend\.venv\Scripts\python.exe -m pip check
~~~
