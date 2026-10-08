# Gemini reasoning boundary audit

October 8, 2026. Frontend unchanged. API keys were not printed, logged, or exposed.

## Existing safeguards reused

- Official google-genai client, SDK system_instruction, and structured response schema.
- Verbatim quote checks against a real clause and its original page text, with original offset checks.
- Clause/page matching, policy ID/category validation, stored playbook resolution, explicit party/deadline substring validation.
- Malformed/extra-field output rejection, no fabricated live-success fallback, SQLite persistence only after verification.
- Embedding ranking without arbitrary compliance thresholds; all policy rules available for analysis.
- Sanitized Gemini/Ollama API errors and existing health/CORS tests.

No second embedding service, retrieval implementation, or quote-verification path was introduced.

## New safeguards

1. Strengthened system instruction: VERITAS role, source-only contractual facts, no definitive legal advice or guarantees, no independent authority, no autonomous approval/rejection, no document modification or instruction execution. Contract AND playbook instructions are untrusted data; role/schema/secret/verdict overrides are forbidden.
2. Explicit five-state finding classification: compliant/risky/ambiguous/conflicting/missing. Strict draft schemas reject coercion, extra evidence statuses, confidence fields, approval decisions, and unknown graph output.
3. Backend-owned evidence_status: verified for supported source provenance, unsupported on rejected records, needs_review for ambiguity, unreliable matching, assumptions, potential omissions, and ambiguous deadlines. The model cannot assign verification. Valid quotation provenance never proves legal interpretation.
4. Potential omissions are policy-only: null contract quote/page/clause, no referenced parties/dates, real policy/category, potential_omission=true, absence_confirmed=false, complete-document review required. No fabricated absence evidence.
5. Source facts, model interpretations, assumptions, uncertainty, and resolved policy requirements are distinguished. Model-supplied requirement text must exactly match the stored rule. Referenced party/date fields must occur verbatim with word boundaries in evidence.
6. Deadline strings are never calculated or reformatted. The backend labels fixed_date/relative/ambiguous/unspecified. Ambiguous numeric formats and invalid supported calendar dates require review.
7. Conservative detection of embedded role/schema/secret/verdict instruction patterns in contract clauses and policy text. Alerts force a partial analysis even for empty model output. Every analysis requires human review. Detection may overflag legitimate quotations and miss obfuscated attacks.
8. At most three Gemini attempts by default for HTTP 429/500/502/503/504 and transport errors, with exponential one/two-second waits. SDK retries remain disabled. Attempts are configurable 1–5; waits are capped at ten seconds. Malformed output and permanent request/auth/model errors are not retried. Exhaustion returns a sanitized failed state without fabricated findings or successful storage writes.
9. Explicit standalone synthetic demonstration, labeled synthetic_demo and live_ai_used=false. It is never substituted for live output or invoked automatically after provider failure.
10. Credential guard blocks source content containing the configured backend key before sending it to Gemini and rejects response text containing that key before it can be returned or stored. Errors contain no key or raw SDK exception.

## Graph boundary

No graph feature or graph entities exist in this MVP. Graph output is therefore rejected as an unexpected field rather than accepting edges to unverifiable entities. A future graph feature must validate both endpoints against real stored source entities before accepting edges.

## System instruction delivery

Yes. generate_analysis passes SYSTEM_INSTRUCTION as GenerateContentConfig.system_instruction to client.models.generate_content through the retry wrapper on every attempt. The automated test inspects the exact SDK arguments, verifies source attacks stay in user JSON data, and confirms automatic function calling is disabled. These tests verify configuration delivery; they do not claim a live adversarial red-team result or immunity to every attack.

## Model verification completed before this audit

The actual API returned 62 listed models; 45 advertise generateContent. Metadata capability is not a guarantee of generation availability for this account. Preferred gemini-3.8-flash and gemini-flash-latest returned 503. Listed gemini-2.5-flash returned 404. gemini-3.5-flash successfully generated real structured JSON with an exact evidence quote and deadline; reported response model version was gemini-3.5-flash. Only after success did the interrupted verification script update backend/.env and .env.example. The backend default is now aligned with that verified model. Full inventory and result: docs/gemini-model-verification.json.

## Modified or added files

- backend/app/config.py: bounded retry settings and verified model default.
- backend/.env.example: model and retry settings.
- backend/app/models/contracts.py: statuses, facts/interpretation separation, deadline types, rejection statuses, review flags.
- backend/app/services/gemini_analysis.py: strengthened prompt, retry/backoff, credential guard, tool-call disablement.
- backend/app/services/evidence.py: extended existing deterministic verifier; no duplicate implementation.
- backend/app/services/reasoning_boundaries.py: conservative instruction alerts, explicit-reference checks, deadline classification.
- backend/app/services/contract_analysis.py: backend review/partial states and alerts.
- backend/app/routes/contracts.py: explicit Gemini/evidence failure state.
- tests/test_contract_analysis.py: preserve existing tests and validate failure states without real sleeps.
- tests/test_reasoning_boundaries.py: mocked adversarial, schema, omission, status, reference, retry, and credential tests.
- tests/show_synthetic_demo.py: explicit offline synthetic-only demonstration.
- README.md: current model, retry behavior, evidence statuses, omissions, limits, and test/demo commands.
- docs/reasoning-boundaries-audit.md: this audit.

The preceding model-verification task also added tests/verify_gemini_model.py and docs/gemini-model-verification.json and updated backend/.env only after real structured JSON generation succeeded.

## Remaining limits

- Quotation existence, source references, and policy matching do not validate all factual implications in free-form prose, referenced party roles, legal interpretations, absence, or completeness. Human review remains mandatory.
- Prompt-injection tests use mocked Gemini output and recognizable attack patterns. They do not prove immunity to all attacks or that a live model will never follow embedded instructions.
- Potential omissions stay unconfirmed even if every extracted page was supplied. OCR/layout/segmentation limitations remain.
- Historical stored verified results remain readable; new response fields have compatibility defaults. They are not retroactively reanalyzed under the new prompt.
- No graph, authentication, user isolation, or background-job system was introduced.
- A nonblocking Starlette HTTPX TestClient deprecation warning remains. Full real contract analysis was not rerun as part of this mocked boundary audit; prior successful simple JSON generation must not be presented as successful full contract analysis.

## Actual automated test results

Final suite: 44 tests discovered; 41 passed; 3 opt-in real-service tests skipped; 0 failures. Runtime: 0.992 seconds. Existing health/CORS, embedding unit tests, PDF extraction, persistence, contract API, and Gemini error tests pass. New mocked tests cover all requested rejection categories, omission handling, five-status classification, backend-owned evidence status, policy/reference checks, deadline classification, supplied injection examples, schema/graph rejection, credential guards, bounded exponential retries, exhaustion, system-instruction delivery, and explicit demonstration labeling. Live contract analysis and live adversarial testing were not run in this audit.

## Reproduce

~~~powershell
.\backend\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\backend\.venv\Scripts\python.exe -m pip check
.\backend\.venv\Scripts\python.exe tests/show_synthetic_demo.py
~~~
