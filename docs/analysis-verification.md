# Contract analysis MVP verification

Verified October 8, 2026. No frontend files were changed. Existing embedding and health/CORS implementation files were preserved. No dependency changes were required; pinned PyMuPDF, google-genai, HTTPX, and python-multipart were already installed.

## Implemented endpoints

- POST /api/contracts/upload: multipart PDF upload; HTTP 201 with preserved extracted page text, clause IDs, exact offsets, and extraction warnings. Original PDF bytes and source JSON are stored in SQLite.
- POST /api/analyze: JSON contract_id; local semantic matching, structured Gemini analysis, deterministic evidence gate, verified result persistence.
- GET /api/analysis/{analysis_id}: persistent result retrieval or 404.
- Existing POST /api/embeddings/test and GET /health remain registered and pass tests.

The sample policy playbook contains rules for liability, indemnification, termination, confidentiality, payment, data protection, and intellectual property. The synthetic PDF has two pages and ten extracted clauses.

## Evidence checks

Every returned quote must be an exact substring of its cited clause and original page text. The cited page must match the clause, and the saved original offsets must reproduce the clause text exactly. Policy IDs must exist in the playbook and match the finding category. Applicable policy rule text is resolved from that playbook, not invented by Gemini. Responsible parties and deadlines must be exact substrings of obligation evidence or null.

No fuzzy quote repair, invented evidence for missing provisions, synthetic success fallback, or assumed dates is used. Rejected records are excluded and reported by reason. Mixed verified/rejected output is partial; completely rejected proposed output fails with 502 and is not saved. Empty valid output stays empty and does not imply compliance. Semantic matches contain actual cosine scores, not fabricated scores. Unassessed policy IDs are coverage indicators, not proof of absence.

Verification confirms provenance, not the legal correctness or completeness of model interpretations.

## Actual test results

Final full live suite: **31 tests run; 30 passed; 1 failed; 0 skipped**. The failed test is the real Gemini/Ollama HTTP E2E, because Gemini returned HTTP 503 for temporary high demand. The final attempt ran in 52.233 seconds. No successful real contract analysis was produced, and no actual risk-finding counts are claimed. No successful E2E JSON report was created.

Passing checks include:

- Original PDF extraction, stable clause IDs, exact original page offsets, original PDF storage, and SQLite result persistence.
- Invalid, encrypted, textless, over-limit, and mixed blank-page PDFs.
- Fabricated quotes, altered whitespace, wrong page/clauses, invented policy IDs, category mismatch, and inferred party/deadline rejection.
- Partial output, all-records-rejected output, and empty output semantics.
- Semantic policy ranking and model/rule-aware policy embedding cache.
- Official Gemini SDK request configuration, strict local schema validation, missing key, malformed output, access/request/model failures, quota/rate limits, connection errors, timeouts, and sanitized error messages using mocks.
- Upload/analyze/fetch API flow using mocked providers, invalid requests, unknown IDs, and sanitized storage failures.
- Existing health/CORS and embedding tests, including both real Ollama tests.

Real Ollama results: metadata-only embedding endpoint HTTP 200; dimensions 1024. Measured related-clause cosine similarity 0.771340; unrelated-clause score 0.427288.

Real HTTP contract E2E progress: upload HTTP 201, two pages, ten clauses; local Ollama matching completed; analysis HTTP 503 with sanitized detail: Gemini service is temporarily unavailable. Result fetch cannot be validated against a successful real analysis because generation failed. It is validated in automated tests with mocked providers.

Python dependency check: No broken requirements found.

## Gemini configuration and connectivity

Backend configuration loaded a nonempty Gemini key; its value was never printed, logged, or exposed. The official SDK and PyMuPDF imports succeeded. Network-restricted attempts initially failed with ConnectError. With network access enabled, HTTPS and SDK authentication/model lookup succeeded.

The previously configured gemini-2.5-flash returned 404 for generation because it is no longer available to new users on this account. The provider recommended gemini-3.8-flash. The user explicitly requested updating GEMINI_MODEL in backend/.env and the defaults; that update was made while preserving the API key.

Minimal real structured generation succeeded with gemini-3.8-flash. Full contract requests encountered provider request/schema rejections during development and then repeated temporary high-demand HTTP 503 responses. Provider schema encoding was changed from the legacy SDK schema to compact JSON schema, while local Pydantic validation retains bounds and rejects extra fields. The final full structured contract generation remains unverified because of provider unavailability; do not interpret simple generation success as a successful full analysis.

## Remaining issues and limits

- Real full Gemini-backed contract analysis did not complete; rerun the live suite when provider capacity is available.
- Starlette emits a nonblocking deprecation warning for HTTPX-backed TestClient.
- OCR is not supported. PDF layout/reading-order errors can affect extracted text and lightweight clause segmentation.
- Input caps: 10 MiB, 30 pages, 60,000 text characters, 100 clauses; configurable.
- Local hackathon MVP only: one synthetic playbook, synchronous generation, local SQLite, no authentication, user isolation, background jobs, or deletion/retention API.
- No actual production contracts, load tests, or legal correctness evaluation were performed.

## Reproduce

From the workspace root:

~~~powershell
.\backend\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\backend\.venv\Scripts\python.exe -m pip check
.\backend\.venv\Scripts\python.exe tests/diagnose_gemini.py
.\backend\.venv\Scripts\python.exe tests/run_live_tests.py
~~~

Offline tests explicitly skip the three opt-in live tests. The live runner enables them and reports unavailable services as failures. It uses temporary storage and an isolated Uvicorn server, then cleans up.

## Files added or changed

- backend/.env (GEMINI_MODEL only; key preserved)
- backend/.env.example
- backend/app/config.py
- backend/app/main.py
- backend/app/models/contracts.py
- backend/app/routes/contracts.py
- backend/app/resources/sample_playbook.json
- backend/app/services/pdf_extraction.py
- backend/app/services/storage.py
- backend/app/services/playbook.py
- backend/app/services/policy_matching.py
- backend/app/services/gemini_analysis.py
- backend/app/services/evidence.py
- backend/app/services/contract_analysis.py
- tests/test_contract_analysis.py
- tests/sample_pdf.py
- tests/fixtures/sample_contract.json
- tests/fixtures/synthetic_supplier_contract.pdf
- tests/diagnose_gemini.py
- tests/verify_ai_http.py
- tests/run_live_tests.py
- README.md
- docs/analysis-verification.md

requirements.txt and requirements-lock.txt were unchanged because all dependencies were already pinned. Frontend files and existing embedding service/router/tests were unchanged.
