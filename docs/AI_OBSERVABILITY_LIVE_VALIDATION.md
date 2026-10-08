# Controlled live observability validation

This is one real Gemini/Ollama diagnostic evaluation of a synthetic contract. It is not a general accuracy estimate or an accuracy optimization. No second live invocation was made.

## Preflight

- Branch: feature/ai-reliability. Working tree was already dirty with the uncommitted observability instrumentation, evaluation package, tests and earlier reports. No existing changes were discarded.
- Ollama reachable at http://localhost:11434; reported version 0.40.1. The configured qwen3-embedding:0.6b produced an actual 1024-dimensional embedding in the preflight request. This was a separate embedding-only check, not another benchmark or Gemini request.
- Gemini configuration was present; the key was checked for presence only and was not printed. Configured model: gemini-3.5-flash.
- Dataset synthetic_v1 v1.0.0 passed the loader source/PDF/hash checks. Its first entry is SYN-supplier_red; --limit 1 selects only that case. All 12 cases are repository synthetic fixtures; no customer contracts were involved.
- Private-directory ACL setup passed preflight. The actual trace is gitignored and was created by the same fail-closed owner-only Windows ACL writer. Tracing was explicitly enabled for this run.
- The adapter redirects storage to a temporary benchmark SQLite database, restores the original process setting in finally, and deletes the temporary database on exit. Production SQLite, WAL and SHM existence/hash checks matched the preflight baseline afterward. No authentication or billing endpoints were invoked.
- Previous live JSON/CSV/Markdown reports were archived before the documented default-output command replaced those filenames.

## Execution

Executed exactly once from backend, using the README syntax:

~~~powershell
.\.venv\Scripts\python.exe -m evaluation.runner --dataset synthetic_v1 --live --limit 1 --trace
~~~

- Started (UTC): 2026-10-08T16:39:08.806774+00:00
- Evaluation run ID: 1a9c514b-3b7b-4f60-839a-8d14558f60de
- Contract ID: SYN-supplier_red
- Analysis ID: d3b73ac4-0524-4f28-ab94-b8e967e2d0d7
- Trace ID: d2144a9f-147a-4468-9ec0-7763481b2c2b
- Configured and actual provider-reported model: gemini-3.5-flash
- Exit code: 0. Gemini was reached and returned schema-valid structured output. One Gemini attempt; no request retries and no automatic benchmark retry.
- Analysis status: partial. Extraction, retrieval, generation, verification, SQLite persistence and equality-checked retrieval all completed.
- No provider/pipeline errors or trace collection failures were recorded. All spans completed; trace diagnostics are empty.

The partial status is explained by four retained potential omissions with evidence_status=needs_review. The production status rule marks review-needed findings partial even when there are no verification rejections. This status is not a failed request.

## Counts and rejection breakdown

| Item type | Proposed | Retained | Rejected | Unverified |
|---|---:|---:|---:|---:|
| findings | 7 | 7 | 0 | 0 |
| obligations | 2 | 2 | 0 | 0 |

There are **zero rejected findings and zero rejected obligations**. Therefore no per-item rejection reason exists in this run; all rejection_stage, rejection_reason_code, original_verifier_reason and diagnostic item fields are null. No rejection reason was invented. The reason-code histogram is empty. Live rejection capture remains unexercised by this response; the earlier offline tests exercised those paths.

## Finding-level diagnostics

Stable item IDs use the trace UUID above plus :finding:001 through :finding:007. LIVE-NNN below abbreviates SYN-supplier_red-LIVE-NNN. Original generated text is kept in the ignored private trace; the descriptions here are curated summaries of synthetic data.

| Prediction | Category / severity | Generated status | Quote/page verification | Gold match / metric outcome |
|---|---|---|---|---|
| LIVE-001 | liability / critical | risky; retained | Exact quote, clause and page 1 verified | SYN-supplier_red-G01 |
| LIVE-002 | indemnification / high | risky; retained | Exact quote, clause and page 2 verified | SYN-supplier_red-G02 |
| LIVE-003 | payment / low | compliant; retained | Exact quote, clause and page 3 verified | Compliant; excluded from active risk scoring |
| LIVE-004 | termination / medium | missing; retained | N/A; no quote/page; absence not confirmed | SYN-supplier_red-G04 |
| LIVE-005 | confidentiality / medium | missing; retained | N/A; no quote/page; absence not confirmed | Unmatched; benchmark FP |
| LIVE-006 | data_protection / medium | missing; retained | N/A; no quote/page; absence not confirmed | Unmatched; benchmark FP |
| LIVE-007 | intellectual_property / medium | missing; retained | N/A; no quote/page; absence not confirmed | Unmatched; benchmark FP |

The liability severity is critical while gold G01 expects high. All three risk matches have the correct category; severity accuracy on matched risks is 2/3. The compliant payment finding is retained but excluded from active risk detection, explaining why seven returned findings yield six scored risk predictions.

### Generated explanations and source references

- **SYN-supplier_red-LIVE-001** (POL-LIAB-001): The supplier's liability is capped at a flat USD 50, which is extremely low and does not scale with fees paid or payable. Furthermore, the cap explicitly includes fraud and data breaches, which violates the policy requiring these to be excluded from any liability cap.
  Source: P001-C002; page 1.
- **SYN-supplier_red-LIVE-002** (POL-INDEM-001): The clause requires the Company to indemnify the Supplier for all claims, including those caused by the Supplier's own negligence, which constitutes an unlimited indemnity for supplier misconduct. Additionally, it explicitly states that the Supplier owes no IP defense, violating the requirement for supplier IP indemnification.
  Source: P002-C002; page 2.
- **SYN-supplier_red-LIVE-003** (POL-PAY-001): The clause is compliant as undisputed invoices are payable in 30 days (not earlier than 30 days), the Company is permitted to withhold disputed sums in good faith, and the late interest rate is capped at exactly 1 percent per month.
  Source: P003-C002; page 3.
- **SYN-supplier_red-LIVE-004** (POL-TERM-001): POTENTIAL OMISSION: The contract does not contain provisions regarding the company's right to terminate for material breach or convenience. Full-document coverage and human review are required before confirming absence.
  Source: None; page None.
- **SYN-supplier_red-LIVE-005** (POL-CONF-001): POTENTIAL OMISSION: The contract lacks confidentiality obligations. Full-document coverage and human review are required before confirming absence.
  Source: None; page None.
- **SYN-supplier_red-LIVE-006** (POL-DATA-001): POTENTIAL OMISSION: The contract does not contain data protection or breach notification obligations. Full-document coverage and human review are required before confirming absence.
  Source: None; page None.
- **SYN-supplier_red-LIVE-007** (POL-IP-001): POTENTIAL OMISSION: The contract does not address intellectual property ownership or licensing of deliverables. Full-document coverage and human review are required before confirming absence.
  Source: None; page None.

### Every unmatched prediction

| Prediction | Assessment | Reason and review requirement |
|---|---|---|
| LIVE-005: confidentiality | Potentially valid unannotated finding | The three-page fixture contains no confidentiality provision, while POL-CONF-001 requires mutual protection and survival. Gold has no confidentiality annotation. The omission is plausible under this synthetic policy; complete-document and applicability review are still required. |
| LIVE-006: data_protection | Ambiguous finding; requires human review | The fixture contains no breach notification/security/data-return duties, but does not explicitly establish personal-data processing. POL-DATA-001 supplies those requirements; whether they apply to this equipment agreement needs human review. Gold has no data-protection annotation. |
| LIVE-007: intellectual_property | Ambiguous finding; requires human review | The fixture contains no ownership/licensing provision, but does not establish bespoke deliverables or a license need. POL-IP-001 is conditional on those interests. Gold has no intellectual-property annotation; applicability needs human review. |

None of these three is confirmed incorrect from the available evidence. Their categories match the policy rules they cite, so there is no demonstrated category mismatch. They are not automatically classified as hallucinations. Gold remains unchanged. A literal omitted topic is not proof that the omission is a material contractual risk.

## Evidence verification and obligations

- Three retained findings have exact source quotations and correct page/clause references: liability page 1, indemnification page 2 and payment page 3. Exact and normalized quote match rates and correct-page rates are all 100% across these three eligible findings.
- Four retained omissions (termination, confidentiality, data protection and IP) have no quote, page or clause ID. Trace evidence_state=not_applicable, evidence_verification_succeeded=false, absence_confirmed=false; final evidence_status=needs_review. No fabricated quotations were substituted.
- Unsupported evidence count: 0. Finding verification failure rate: 0%. These results validate literal provenance, not interpretation completeness or legal correctness.
- The evaluator reports supported=true for valid omission representations, and consequently its supported_evidence_detection repeats TP=3/FP=3/FN=0. That field does **not** mean four absences have verified source evidence; the trace explicitly shows N/A and review needed.

| Obligation | Responsible party | Explicit deadline | Source | Evidence |
|---|---|---|---|
| Company must pay undisputed invoices within 30 days after receipt. | Company | 30 days after receipt (relative) | P003-C002, page 3 | verified; exact quote/page/party verified |
| Company must indemnify Supplier for every claim, including claims caused by Supplier negligence. | Company | None (unspecified) | P002-C002, page 2 | verified; exact quote/page/party verified |

Both obligation evidence checks passed. The invoice description says within 30 days whereas the exact source says payable in 30 days; this is a paraphrase requiring interpretation review, not an exact quotation error. The indemnity has no explicit deadline; null is preserved.

## Risk detection metrics

| Metric | Actual result |
|---|---:|
| True positives | 3 |
| False positives (unmatched active predictions) | 3 |
| False negatives | 0 |
| Precision | 50.00% |
| Recall | 100.00% |
| F1 | 66.67% |

The three matches are liability G01, indemnification G02 and termination omission G04. No gold risk was missed. Gold includes four labels: three risks (one omission) and one compliant payment observation. These labels remain pending human review. Precision penalizes unannotated omission candidates, so 50% is agreement with this sparse gold set, not a proven 50% hallucination rate. The single synthetic case cannot establish general Gemini accuracy.

## Measured stage timings

| Stage | Seconds | Parent / scope |
|---|---:|---|
| total_analysis (span-0001) | 53.278278 | None |
| pdf_extraction (span-0002) | 0.003316 | span-0001 |
| persistence_contract (span-0003) | 0.036837 | span-0001 |
| contract_analysis (span-0004) | 53.234570 | span-0001 |
| policy_retrieval (span-0005) | 28.099807 | span-0004 |
| embedding_request (span-0006) | 2.219771 | span-0005 |
| embedding_request (span-0007) | 2.152777 | span-0005 |
| embedding_request (span-0008) | 2.135307 | span-0005 |
| embedding_request (span-0009) | 2.152182 | span-0005 |
| embedding_request (span-0010) | 2.133348 | span-0005 |
| embedding_request (span-0011) | 2.134128 | span-0005 |
| embedding_request (span-0012) | 2.213702 | span-0005 |
| embedding_request (span-0013) | 2.107463 | span-0005 |
| embedding_request (span-0014) | 2.206934 | span-0005 |
| embedding_request (span-0015) | 2.114590 | span-0005 |
| embedding_request (span-0016) | 2.210045 | span-0005 |
| embedding_request (span-0017) | 2.104066 | span-0005 |
| embedding_request (span-0018) | 2.200697 | span-0005 |
| gemini_generation (span-0019) | 25.125053 | span-0004 |
| structured_response_parsing (span-0020) | 0.000654 | span-0019 |
| evidence_verification (span-0021) | 0.001718 | span-0004 |
| persistence_analysis (span-0022) | 0.005907 | span-0004 |
| persistence_retrieval (span-0023) | 0.002842 | span-0001 |

- Embedding requests: 13; sum of sequential request spans: 28.085011 seconds. This is a fresh process with cold in-memory policy-vector cache: seven policy embeddings and six clause embeddings.
- Policy retrieval includes these embedding spans. Gemini generation includes parsing. Contract analysis contains retrieval, Gemini, verification and analysis persistence. Total analysis contains PDF extraction, storage and retrieval. Do not sum nested stages.
- Embedding timings include client/network/request/vector validation; the trace does not isolate model compute, HTTP connection setup or transport delay. Retrieval is the largest measured span, but its internal bottleneck is not proven.
- Adapter processing time: 53.278175 seconds.
- Total traced analysis span: 53.278278 seconds.
- Benchmark runner time: 53.872435 seconds (includes dataset/tracing/report preparation beyond the analysis). The separate preflight embedding request is excluded.

## Provider-reported usage

| Usage field | Tokens |
|---|---:|
| input_tokens | 2629 |
| output_tokens | 1567 |
| total_tokens | 8836 |

Values were copied from SDK usage metadata for the last returned response, with one attempt. Total 8836 is provider-reported and is intentionally not replaced by input+output (4196). A finer usage breakdown was not captured, so the difference is not attributed to a specific token type. Cost was not calculated; no unverified pricing or inferred token counts are presented.

## Comparison with previous live run

| Measure | Previous | This run |
|---|---:|---:|
| Actual model | gemini-3.5-flash | gemini-3.5-flash |
| Analysis status | partial | partial |
| Findings proposed / retained / rejected | 7 / 5 / 2 | 7 / 7 / 0 |
| Obligations proposed / retained / rejected | 2 / 0 / 2 | 2 / 2 / 0 |
| Quote/page-verified retained findings | 1 | 3 |
| Retained potential omissions | 4 | 4 |
| TP / FP / FN | 2 / 3 / 1 | 3 / 3 / 0 |
| Precision | 40.00% | 50.00% |
| Recall | 66.67% | 100.00% |
| F1 | 50.00% | 66.67% |
| Adapter latency | 48.6054 s | 53.2782 s |

Latency increased by 4.6728 seconds. Previous per-stage timings and usage were unavailable. Prompt, configuration and dataset-manifest hashes are identical across runs; risk_metrics.py and evidence_metrics.py hashes also match. Production engine hashes changed for observability hooks. The prior discarded proposals are unavailable, so the exact output changes cannot be reconstructed item-by-item.

The new run retained an indemnification risk matched to G02 (the previously missed annotation), a compliant payment observation and both obligations. Output can vary between Gemini calls. The improved score and fewer rejections are not evidence that observability improved model accuracy; no controlled causal comparison was performed.

## Recommended next engineering improvement

Prioritize a reviewed omission-applicability/annotation coverage protocol and clearly separate source-verified findings from omission candidates in benchmark reporting. This run demonstrates that the three FPs are unannotated omission observations, and supported_evidence_detection can be misread as verified absence. Have a reviewer assess all policy categories consistently before adopting a revised benchmark version; do not silently relabel this gold dataset. Also correct the runner generic measurement_notes that still claim usage/rejected proposals are unavailable: this traced run provides usage, and the private trace preserves proposals.

For performance, next profile per-request transport/client setup and consider a separately tested batched embedding interface, preserving retrieval inputs/ranking. Thirteen sequential embedding requests consumed most of the 28.10-second retrieval span. This is a recommendation only; no batching, prompt, model, acceptance or scoring changes were made.

## Artifacts and files changed in this task

- docs/AI_OBSERVABILITY_LIVE_VALIDATION.md: this report.
- backend/evaluation/reports/synthetic_v1-live.json, .csv and .md: outputs of the single invocation.
- backend/evaluation/reports/previous-live-before-observability-validation/: preserved previous report copies.
- backend/evaluation/reports/observability-live-preflight.json: safe preflight metadata/database integrity baseline.
- Private ignored trace: evaluation/private_traces/1a9c514b-3b7b-4f60-839a-8d14558f60de/d2144a9f-147a-4468-9ec0-7763481b2c2b/trace.json (relative to backend).

Temporary diagnostic helper scripts were removed after use. No production source, prompt/model settings, evidence acceptance rules, gold labels, authentication, billing or frontend was modified in this task. No production database reset and no Git push occurred. The regression suite was not rerun because this task made no implementation changes; the preceding 126-pass/3-skip result remains the offline validation record.
