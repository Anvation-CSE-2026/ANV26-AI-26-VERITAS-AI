# Evidence verification failure: diagnosis and constrained repair

2026-10-09; feature/ai-reliability. No live Gemini call made.

## Observed failure and limits

Read-only inspection found failure 3a8c53d0-8392-4ac4-8048-1b19ab790801, contract 7df50041-a3a5-4882-9e2a-c3e3fa605440: seven finding and two obligation exclusions, all quote_not_in_original_clause. Uploaded source/PDF remains available. It has one page and twelve clauses, nine with internal line breaks. Re-extracting its saved PDF reproduced its stored clauses exactly. It did not match the twelve benchmark PDFs or known tests/fixtures PDFs, so its synthetic identity is not asserted. Contract contents were not printed or exported.

The rejected raw Gemini quotations were not persisted in this failure record. **The exact cause of each of these nine mismatches cannot be established from counts alone.** Paraphrase, policy text, cross-clause quotation and whitespace differences remain possible. No raw output was reconstructed. A confirmed reproducible verifier defect was its byte-exact rejection of otherwise identical words/punctuation when PDF newline formatting became spaces. The repair addresses that defect without declaring the unavailable generated response supported.

## Pipeline investigation

| Suspected cause | Source inspection / evidence |
|---|---|
| Clause-ID mismatch | Prompt serializes the same contract.clauses IDs used by verifier. This failure reason is downstream of ID/page checks; IDs existed, but whether a quote belonged to another clause is unknown without proposals. |
| Paraphrasing | Existing instruction already requested exact evidence; generation can still disobey. Stronger instructions added. Paraphrases remain rejected. |
| Whitespace/Unicode/PDF breaks | Strict original substring comparison reproducibly failed when newline became space. Only whitespace character/run differences are now recoverable. No punctuation, case, hyphen, smart-quote or Unicode letter normalization. |
| Another source clause | Search remains confined to the cited clause. Even a unique quote in another clause is excluded, not silently reassigned. |
| Incorrect verifier source | Page offset slice must exactly reproduce the cited clause. Actual failure upload re-extraction matches its stored clauses; original page/offset checks retained. |
| Aggressive normalization | None existed; new matching escapes all non-whitespace tokens literally, preserving content. No fuzzy/edit-distance/semantic matching. |
| Truncation | Extraction splits long text into <=2000-character clauses while preserving remaining text. Prompt includes every clause's full model_dump; no prompt-side text truncation found. Source limits reject oversize inputs instead of silently trimming. |
| JSON parsing | json.dumps escapes newlines; model_validate_json decodes them without a quote transform. Regression checks JSON round-trip preservation. Literal backslash-n is not treated as an actual newline. |
| Persistence / frontend | Failed generation saves an explicit failure record, not supported findings; uploaded contract remains. Frontend surfaces exclusions and manual retry. No evidence-stage automatic retry exists. |

## Exact repair

original_quote_slice first checks the existing exact substring path. Otherwise it builds a pattern from literal escaped non-whitespace tokens, allowing only whitespace runs between them, **within the original correctly cited clause**. It returns a literal matched slice of original source text. An accepted result and source_facts use that exact original slice; the raw draft is not mutated, so active synthetic trace observers can retain the original proposal separately. Page/ID/source-offset/policy/category/party/deadline checks remain active. No match elsewhere, punctuation repair or paraphrase substitution occurs. Cases where exact party/deadline text is unavailable remain rejected.

This is an explicit narrow change to the former byte-whitespace acceptance rule, authorized by the task; it is not a claim that every prior verification rule is byte-for-byte unchanged. Original literal-source provenance is preserved in returned/stored accepted quotes. The prior whitespace test was updated to require restoration of exact original source rather than rejection. Gold/scoring rules were not changed.

Prompt now explicitly requires verbatim quotations from contract_clauses[].text, correct clause/page ID, no paraphrase/summarization/invention, no policy-as-contract quotations or cross-clause spans, and separate policy-only potential omissions. Omission handling remains unchanged: no source quote/page/clause and no verified absence.

Total rejection stays HTTP 502/evidence_verification/unsupported_evidence. Message now says the AI could not verify its evidence, no supported analysis was saved, and upload remains available for manual retry or explicit demo. Frontend explains that a retry is another AI request. No automatic new Gemini invocation was introduced. Mixed results retain only valid records with partial status and exclusion warnings.

## Tests and outcome

Full offline suite: **154 passed, 3 live-service tests skipped, 0 failures/errors**, 157 total, 10.080 seconds. Ten new regressions cover exact quotes/JSON, PDF/newline/Unicode-whitespace source restoration, obligations, wrong IDs/pages/offsets, other-clause quotes, paraphrase/token/case/punctuation rejection, mixed partial persistence, total failure/upload preservation/one mocked invocation, unverified omissions, and prompt instructions.

An additional mechanical read-only test on the actual failing uploaded PDF restored one whitespace-flattened quote to its original clause text. This was not a model-generated finding or a legal assessment, and no result was saved. No whole-response live recovery is claimed. Existing fixture evaluation stayed TP=17, FP=3, FN=7; this is not Gemini accuracy.

Frontend build and lint passed. Bundle-size and existing test dependency deprecation warnings remain unrelated. Browser interaction is not verified in this task.

## Files modified

- backend/app/services/evidence.py
- backend/app/services/gemini_analysis.py
- tests/test_contract_analysis.py
- tests/test_quote_grounding.py (new)
- frontend/src/components/ErrorBanner.jsx
- docs/AI_EVIDENCE_VERIFICATION_FIX.md (this report)
- backend/evaluation/reports/offline-tests.json (test-run result artifact)

No production database write/reset, gold/scoring modification, model change, secret change/exposure or Git push. Tests used temporary storage. One newly approved live synthetic Gemini invocation would be required to verify end-to-end provider behavior; existing failure proposals cannot be replayed because they were not saved. Until approved, use the existing genuine synthetic snapshot or separately labeled demo. A new response may still paraphrase; it will fail closed rather than be fabricated as supported evidence.

The same local backend was restarted to apply the tested source change. Direct /health and the frontend-proxied /health both returned HTTP 200 after restart. No AI request was sent during restart/health checks.
