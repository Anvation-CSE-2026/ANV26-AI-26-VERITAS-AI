# Hackathon backend verification

Verified October 8, 2026. No frontend files changed. No API key was printed or logged. No external provider was mocked in the real end-to-end run.

## Real end-to-end result

- Working configured model: gemini-3.5-flash. Actual API model lookup advertised generateContent; the full structured contract analysis succeeded. Response model version: gemini-3.5-flash.
- Contract ID: dbb99d52-0df2-4072-829a-26799679e627.
- Analysis ID: d1a44317-f041-436f-a15d-319ba8722a86.
- Analysis HTTP status: 200. Analysis status: completed. Output origin: live_gemini.
- Two PDF pages, ten source clauses, thirty measured Ollama semantic policy matches.
- Accepted findings: 7. Evidence-status verified findings: 7. Quote-verified findings: 7. Needs-review findings: 0. Unsupported/rejected findings: 0.
- Obligations: 5. Rejected obligations: 0.
- Gemini attempts: 1. Retries occurred: no.
- Total end-to-end verification time: 63.714 seconds (upload through retrieval, additional restart verification, and cleanup).
- Original PDF/text persistence, independent evidence re-verification, result retrieval, and identical result retrieval after a backend restart succeeded.
- Records remain in default SQLite storage, retrievable with GET /api/analysis/d1a44317-f041-436f-a15d-319ba8722a86 when using the same STORAGE_PATH.
- backend/.env and .env.example model settings were written only after successful full request verification. GEMINI_MODEL remains configurable; the key bytes were preserved.

Exact machine-readable summary: docs/live-e2e-result.json. It logs identifiers and metrics, not full contract text. Completed does not mean legal approval or legal compliance; human review remains mandatory.

## Failure handling checked

The existing retry policy was reused: at most three attempts by default for 429/500/502/503/504 and transport errors, exponential one/two-second waits, SDK internal retries disabled. Authentication 401/403 and permanent request/model failures are not retried. Tests now assert actual attempt counts, no retry on authentication, and exhaustion without demo substitution.

Sanitized failed attempts are now stored in a separate analysis_failures SQLite table, never as successful results. Gemini/evidence error responses include failure_recorded and analysis_id when storage succeeds. GET that ID returns status=failed and no findings/obligations. Mocked exhaustion and evidence-failure persistence/retrieval passed. No real failure occurred in this live run, so there is no real failure-stage/HTTP-error/retry case to report for it.

## Offline demonstration readiness

GET /api/demo/analysis and tests/show_synthetic_demo.py use a fixed precomputed synthetic snapshot, independently reverified on access. Label: **SAMPLE ANALYSIS — DEMO DATA**. Live AI used: false. Seven hand-authored, evidence-verified sample findings and three obligations. Gemini and Ollama are not called; embedding/generation metadata is not_used. The normal analyze endpoint never silently substitutes this snapshot and rejects demo-mode request flags.

The snapshot includes a synthetic contract and company policy playbook. Tampered quotes or false live-generation metadata are rejected. Repeated requests return identical precomputed data. Demo readiness was verified with both provider functions blocked in automated tests and by executing the summary-only offline CLI.

Repeatable five-minute workflow: docs/demo-workflow.md.

## API documentation

- docs/frontend-api-contract.md: exact requests, response field tables, analysis/finding/evidence statuses, errors, obligations, failure retrieval, and separate demo endpoint.
- docs/frontend-openapi.json: exact OpenAPI export from the installed backend.
- There is no graph API/data layer. Documentation explicitly records that nodes/edges/graph fields are absent and unverified graph output is rejected. It does not invent a graph contract.

## Tests

Final automated suite: 51 tests discovered, **48 passed**, 3 opt-in live-service tests skipped, zero failures; runtime 1.037 seconds. The full real HTTP Gemini/Ollama test was run separately and passed, using no external mocks. Existing health/CORS, PDF, SQLite, embeddings, schema, evidence, and boundary tests remain passing.

New coverage: retry telemetry, authentication non-retry, separate failure persistence and retrieval, repeatable service-independent precomputed demo, tamper rejection, and rejection of implicit demo mode on the live endpoint.

Dependency check: No broken requirements found. Offline demo CLI: success, seven findings and three obligations, correct label/origin.

## Main files added or updated

- backend/app/models/contracts.py: generation metrics, failed-attempt model, demo artifact model.
- backend/app/services/gemini_analysis.py: thread/context-local attempt telemetry; retry logic preserved.
- backend/app/services/contract_analysis.py: actual metrics and sanitized failed-attempt recording.
- backend/app/services/storage.py: separate failure storage/retrieval without changing successful records.
- backend/app/services/demo.py and backend/app/resources/demo_analysis.json: precomputed, evidence-checked explicit demo.
- backend/app/routes/contracts.py: failure retrieval metadata and separate GET /api/demo/analysis.
- tests/verify_ai_http.py: complete live metrics, model confirmation, independent evidence/restart verification, configurable report/storage, verify-before-settings update.
- tests/build_demo.py, tests/show_synthetic_demo.py, tests/test_demo_stability.py, tests/test_reasoning_boundaries.py, tests/export_frontend_contract.py.
- README.md and the frontend API/demo/verification documentation listed above.
- backend/.env and .env.example: preferred model confirmed and written only after the successful real request; secrets preserved.

## Remaining limitations

No blocker remains for the verified local hackathon demonstration. External provider capacity/network/quota can still interrupt future live generations; the explicit offline demo remains separate and usable. The existing nonblocking Starlette TestClient deprecation warning remains. OCR, authentication/user isolation, background jobs, and graph features are not implemented. Evidence provenance checks do not prove legal correctness or resistance to every prompt-injection attack. No production readiness claim is made.
