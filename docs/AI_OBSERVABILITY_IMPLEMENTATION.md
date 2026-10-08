# AI analysis observability implementation

Implemented on feature/ai-reliability. This change adds opt-in synthetic benchmark diagnostics; it does not tune accuracy. No live Gemini or Ollama requests were made during implementation. The earlier live run's discarded proposals cannot be reconstructed by this change.

## Execution sequence

The live benchmark adapter creates an isolated temporary SQLite database, extracts the selected fixture PDF, persists the contract, and invokes the existing production analysis service. That service loads the playbook, checks source instructions, retrieves policies using Ollama embeddings, requests Gemini structured output, parses the existing AnalysisDraft schema, verifies evidence, persists the completed/partial result, and retrieves it for consistency checking. Failures retain the existing explicit failure persistence path. Temporary database settings are restored on exit.

Verification runs source clause lookup, cited-page checking, source-offset integrity checking and exact quotation matching before policy ID/category/wording checks and explicit party/date checks. Potential omissions follow the existing separate validation path. Obligations require their existing explicit source evidence, party and deadline validation. The verifier reports its first rejection reason; diagnostics do not infer later failures or legal correctness.

## Files modified

| File | Change |
|---|---|
| backend/app/services/analysis_observability.py (new) | Context-local optional observer, monotonic spans and fail-safe events. |
| backend/app/services/pdf_extraction.py | Extraction span. |
| backend/app/services/ollama_embeddings.py | Per-embedding-request span. |
| backend/app/services/policy_matching.py | Retrieval span. |
| backend/app/services/gemini_analysis.py | Generation/parsing spans, reported usage and schema-failure events. |
| backend/app/services/evidence.py | Proposed and final disposition events; verification span. |
| backend/app/services/contract_analysis.py | Analysis span and final outcome/failure events. |
| backend/app/services/storage.py | Contract/analysis/failure persistence and analysis/failure retrieval spans only. |
| backend/evaluation/tracing.py (new) | Trusted synthetic source gate, private trace writer, diagnostic codes and evidence flags. |
| backend/evaluation/live_adapter.py | Opt-in observer around the existing production pipeline; legacy prediction ID mapping. |
| backend/evaluation/schema.py | Optional outcome count, usage and trace fields. |
| backend/evaluation/runner.py | Explicit --trace flag, run ID and sanitized reporting. |
| backend/evaluation/evaluator.py | Additional diagnostic totals without changing risk/evidence scoring. |
| backend/evaluation/README.md | Trace usage and privacy instructions. |
| tests/test_observability.py (new) | 23 offline observability tests, including a mocked full pipeline. |
| .gitignore | Excludes private benchmark traces. |
| backend/evaluation/reports/offline-tests.json | Actual regression result. |
| docs/AI_OBSERVABILITY_IMPLEMENTATION.md (new) | This report. |

No Gemini prompts, model configuration, scoring algorithms, gold labels, evidence acceptance conditions, authentication, payment logic, frontend files or public API response schemas were changed. Storage instrumentation wraps existing contract-analysis helpers; SQL and authentication/payment helpers are unchanged.

## Enablement and artifact security

Tracing defaults to disabled. The benchmark CLI rejects --trace without --live. A future separately approved run may use the README command:

~~~powershell
.\.venv\Scripts\python.exe -m evaluation.runner --dataset synthetic_v1 --live --limit 1 --trace
~~~

That live command was **not executed** for this task. The offline example below invokes only deterministic verification on a hand-authored synthetic draft.

Traces are stored at backend/evaluation/private_traces/<evaluation_run_id>/<trace_id>/trace.json. Each trace uses a new private directory. Windows removes inherited permissions and grants the current numeric user SID access; POSIX uses directory mode 0700 and file mode 0600. ACL setup fails closed before model calls or raw artifact writes. Run IDs reject path traversal, files are created exclusively, and traces are gitignored. Retention is manual; no automatic deletion or production database reset occurs.

A synthetic flag or ID prefix is insufficient: the collector validates against the hash-checked repository synthetic_v1 dataset, requires the approved PDF path and matching extracted source, then rechecks the actual observed contract before copying proposals. Customer data is not eligible. Default production execution has no collector, copies no proposals into traces, and introduces no raw-content logging.

Known configured credentials, common email/phone/ID formats, bearer/JWT tokens and labelled credential strings are redacted before serialization. Provider exception bodies and malformed raw SDK output are excluded. Redaction is defense in depth, not a universal PII detector; trusted synthetic-only gating is essential. Arbitrary personal names and novel credential formats cannot be universally classified. Do not enable this collector for customer data.

Observation callbacks do not change application acceptance decisions. A collection/write problem marks trace_observation_failed and makes the benchmark return a nonzero exit code rather than silently declaring a complete trace. Interrupted runs unwind stage scopes and attempt to write an interrupted artifact; a hard process kill cannot guarantee a final write.

## Trace schema (version 1.0)

| Field | Meaning |
|---|---|
| evaluation_run_id, trace_id, contract_id | Run, per-contract trace UUID and approved fixture ID. |
| model_identifier, response_model | Configured model and provider-returned model version, if supplied. A configured identifier alone does not prove a model call occurred. |
| analysis_id, status | Actual result/failure ID and outcome; interrupted or unverified may occur before completion. |
| synthetic_source_only, created_at_utc | Source gate marker and artifact timestamp. |
| pipeline_stage | Most recently registered span; inspect stages and diagnostics for actual failure attribution. |
| counts.findings / counts.obligations | proposed, retained, rejected and unverified; null when no validated draft was observed. |
| items[] | Stable original proposal identity, exact disposition, diagnostics and evidence assessment. |
| stages[] | span_id, parent_span_id, stage, seconds and running/completed/failed_or_interrupted status. |
| token_usage | input_tokens, output_tokens, total_tokens; unavailable values are null, scope is last_reported_response. |
| diagnostics[] | Non-item schema or pipeline failures with stage/category. |
| observation_failed | Whether diagnostics may be incomplete. |
| trace_collection_seconds, timing_notes | Collection interval and overlap/coverage caveats. |

Each item contains item_type (finding/obligation), item_id (<trace UUID>:<type>:<one-based index>), proposed_index (zero-based), pipeline_stage, final_status (retained/rejected/unverified), retained (boolean/null), rejection_stage, rejection_reason_code, original_verifier_reason, diagnostic, evidence_validation, proposed and final. Retained findings also map to the benchmark's existing prediction identifier. Proposed raw fields are confined to the private synthetic trace; final contains the original verified output or null. Index-based identity preserves rejected entries without assuming identical explanations uniquely identify an item.

Counts reconcile as proposed = retained + rejected + unverified. Successful verification has zero unverified items. Schema-invalid responses have no attributable typed proposals, so item counts remain unknown rather than falsely zero.

### Evidence assessment

Each item records evidence_supplied, quotation_supplied, quotation_matches_extracted_text, cited_page_matches, quotation_matches_cited_clause, evidence_state, evidence_verification_succeeded, evidence_verification_not_applicable and absence_confirmed. Missing quote comparisons are null. These substring/page flags supplement, and never override, the existing verifier's disposition.

Evidence states distinguish missing, invalid, unverified, verified and not_applicable. A valid omission has not_applicable evidence, verification success false and absence_confirmed false; it remains a review observation, not proof that a clause is absent. Retention does not imply an omission has verified quotation evidence. A policy/reference rejection can coexist with an exact source quotation, so inspect both the evidence flags and the rejection code.

## Rejection codes

| Code | Confirmed basis |
|---|---|
| MISSING_EVIDENCE | The actual first source-reference/quotation failure corresponds to a missing clause ID, page or blank quotation. Does not allege fabrication. |
| QUOTE_NOT_FOUND | Supplied nonblank quotation fails exact original clause/page validation. |
| PAGE_MISMATCH | Supplied page differs from the referenced source clause page. |
| INVALID_REFERENCE | Unknown clause/policy or party/date not explicit in the required evidence. |
| SOURCE_INTEGRITY_FAILURE | Offsets fail to reproduce original source text. |
| POLICY_MISMATCH | Policy category or policy wording differs from the playbook. |
| INVALID_OMISSION_REFERENCE | Potential omission contains prohibited source evidence or party/date references. |
| INVALID_SCHEMA | Whole structured response fails the existing schema; recorded as a stage diagnostic, not invented item rejections. |
| UNKNOWN_REJECTION | Existing verifier reason is unrecognized; no inferred cause. |

The original lower-case verifier reason is retained alongside the code. UNSUPPORTED_CLAIM and DUPLICATE_FINDING are not emitted: the existing verifier does not establish these diagnoses. Rejection codes do not constitute a hallucination classifier.

## Actual offline synthetic example

**OFFLINE SYNTHETIC DRAFT — NOT LIVE MODEL OUTPUT.** The example was generated using the frozen SYN-supplier_red source and the actual deterministic verifier under a network-blocking guard. Findings: 5 proposed, 2 retained, 3 rejected. Obligations: 2 proposed, 1 retained, 1 rejected. The four rejection codes are QUOTE_NOT_FOUND, PAGE_MISMATCH, MISSING_EVIDENCE and INVALID_REFERENCE. Token usage is unknown because no provider was called.

The following curated excerpt comes from the actual ignored, owner-only artifact; it is not a reconstruction of the historical live run:

~~~json
{
  "schema_version": "1.0",
  "evaluation_run_id": "offline-observability-example",
  "trace_id": "78d55b56-33fa-46ee-a79b-88e7af0abc8e",
  "contract_id": "SYN-supplier_red",
  "analysis_id": "offline-example-not-live",
  "status": "partial",
  "model_identifier": "gemini-3.5-flash",
  "response_model": null,
  "counts": {
    "findings": {
      "proposed": 5,
      "retained": 2,
      "rejected": 3,
      "unverified": 0
    },
    "obligations": {
      "proposed": 2,
      "retained": 1,
      "rejected": 1,
      "unverified": 0
    }
  },
  "token_usage": {
    "input_tokens": null,
    "output_tokens": null,
    "total_tokens": null,
    "scope": "last_reported_response"
  },
  "stages": [
    {
      "span_id": "span-0001",
      "stage": "offline_verifier_example",
      "parent_span_id": null,
      "seconds": 0.0008948000031523407,
      "status": "completed"
    },
    {
      "span_id": "span-0002",
      "stage": "evidence_verification",
      "parent_span_id": "span-0001",
      "seconds": 0.0004639000107999891,
      "status": "completed"
    }
  ],
  "example_item": {
    "item_type": "finding",
    "item_id": "78d55b56-33fa-46ee-a79b-88e7af0abc8e:finding:002",
    "proposed_index": 1,
    "pipeline_stage": "evidence_verification",
    "final_status": "rejected",
    "retained": false,
    "rejection_stage": "evidence_verification",
    "rejection_reason_code": "QUOTE_NOT_FOUND",
    "original_verifier_reason": "quote_not_in_original_clause",
    "diagnostic": "Supplied quotation is not an exact substring of the original cited clause/page.",
    "evidence_validation": {
      "evidence_supplied": true,
      "quotation_supplied": true,
      "quotation_matches_extracted_text": false,
      "cited_page_matches": false,
      "quotation_matches_cited_clause": false,
      "evidence_state": "invalid",
      "evidence_verification_succeeded": false,
      "evidence_verification_not_applicable": false,
      "absence_confirmed": false
    },
    "proposed": {
      "finding_status": "risky",
      "policy_requirement": null,
      "referenced_parties": [],
      "referenced_dates": [],
      "policy_match_reliable": true,
      "uncertainty": null,
      "unsupported_assumptions": [],
      "risk_level": "high",
      "clause_category": "liability",
      "explanation": "Synthetic cap risk.",
      "evidence_quote": "This quote does not exist.",
      "page_number": 1,
      "clause_id": "P001-C002",
      "policy_id": "POL-LIAB-001",
      "recommended_action": "Review synthetic cap."
    },
    "final": null
  }
}
~~~

## Timing and provider usage

Spans use time.perf_counter, with parent relationships and nonnegative elapsed durations. A span records completed or failed_or_interrupted; failure and interruption are intentionally not distinguished at the span level. Instrumented stages: pdf_extraction, policy_retrieval, embedding_request, gemini_generation, structured_response_parsing, evidence_verification, contract_analysis, persistence_contract, persistence_analysis, persistence_failure, persistence_retrieval, persistence_failure_retrieval and total_analysis. Only stages actually reached appear.

Retrieval includes embedding requests; Gemini includes parsing and existing retry delays; contract_analysis contains retrieval/Gemini/verification/persistence; total_analysis includes selected PDF extraction, persistence and retrieval. Nested durations overlap and must not be summed. Embedding spans include request and vector validation, not isolated network time. Trace directory setup, whole-dataset validation and final artifact writing are outside total_analysis. The small offline example measures only its verifier scope; it cannot measure Gemini/Ollama latency. The mocked full-pipeline test exercises every successful-path stage but supplies no live service latency evidence.

Usage is copied directly from SDK prompt_token_count, candidates_token_count and total_token_count. Missing/non-integer values remain null; total is not calculated from input/output. The scope is the last returned provider response. Failed requests/retries may have unreported billable usage, and this is not an account-wide cost estimate. Generation options, SDK retries and production retry bounds remain unchanged.

## Tests and preservation checks

Executed from backend:

~~~powershell
.\.venv\Scripts\python.exe -m evaluation.run_offline_tests
~~~

Actual result: **129 discovered; 126 passed; 3 live-service tests skipped; 0 failures; 0 errors.** The offline harness blocks network and disables live opt-ins. All 23 new observability tests passed. SHA-256 checks confirmed all 38 manifest-listed fixture files and the manifest itself are unchanged; risk_metrics.py and evidence_metrics.py match the pre-change baseline. The prompt constant and public contract-model file match the historical live-run hashes. Git confirms the example private trace is ignored.

Coverage includes every requested diagnostic category: reason coverage/count reconciliation, absence versus invalid quotation, page/quote mismatch, unchanged verification decisions, quiet default/active observation, opt-in gate, monotonic spans, unknown usage, stable item/prediction identities and partial diagnostics. Additional checks cover all-rejected drafts, schema failures, source mismatch, credential/common-PII redaction, callback failures, fail-closed ACL setup, traversal rejection and a mocked extraction-to-SQLite pipeline. The full-path test exercised 13 cold-cache embedding requests and structured SDK output without external service calls.

## Known limitations

- Historical discarded live proposals and per-stage timings remain unavailable; this feature cannot retroactively recover them.
- Only schema-valid typed proposals are preserved. Malformed raw provider text is deliberately excluded; item attribution is unavailable for INVALID_SCHEMA.
- Diagnostics preserve the verifier's first failure and existing acceptance rules; they do not adjudicate semantic truth, legal risk or omissions.
- Synthetic source gating trusts repository code/manifest integrity against ordinary accidental use, not a hostile operator changing both.
- Provider usage and retries may be incomplete; timings overlap and include application work. Live instrumentation behavior has not been tested with real services in this task.
- Observation or artifact-write failures can leave incomplete diagnostics, explicitly flagged. Abrupt process termination can prevent final output.
- Private traces need deliberate local retention/cleanup. Redaction is not a general-purpose guarantee for arbitrary customer PII.
- Sparse gold annotations, supported-category coverage and existing metric matching remain unchanged; these diagnostics improve auditability, not benchmark accuracy.
