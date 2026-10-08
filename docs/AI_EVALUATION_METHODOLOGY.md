# VERITAS AI evaluation methodology

## Scope and inspection

Inspection and offline validation completed on 2026-10-08. This is the initial benchmark phase. Existing prompts, risk detection, model settings, frontend, authentication, Razorpay/subscriptions and production database are preserved.

The actual configuration was loaded through `app.config.settings`, which loads `backend/.env`. Only a key-present boolean and model names were inspected. The effective models are `gemini-3.5-flash` and `qwen3-embedding:0.6b`; Gemini credentials are present. This confirms configuration, **not current provider connectivity**. No live provider calls were made.

| Existing component | Current behavior |
|---|---|
| `app/services/pdf_extraction.py` | PyMuPDF `get_text("text", sort=True)`; preserves original page strings, zero-based start/exclusive-end offsets and clause slices. Numbered headings/blank paragraphs segment text; long blocks split around 2,000 characters. Pages are 1-based; clause IDs encode page and local index. Page-spanning clauses become separate fragments. OCR is unsupported; blank pages produce warnings; upload/page/character/clause limits apply. |
| `app/services/ollama_embeddings.py` | Synchronous HTTPX requests to local `/api/embed`, configurable embedding model, finite/nonzero vectors, connect/read timeouts and cosine utility. No chat requests. |
| `app/services/policy_matching.py` | Cached policy vectors; embeds each clause and ranks all rules with cosine similarity, keeps top three per clause. Similarity is retrieval, not a risk score. All rules still go to Gemini. |
| `app/services/gemini_analysis.py` | Official google-genai SDK, strict local AnalysisDraft validation, compact JSON response schema, temperature 0, output limit 12,000. Source-only system instruction, protected credential guards, bounded application retries (default three attempts) for 429/500/502/503/504 and transport failures; SDK retries disabled. Auth failures are not retried. |
| `app/services/evidence.py` | Exact nonblank quote must exist in the cited original clause and page; source offsets must reproduce the clause. Policy ID/category/optional rule text and referenced parties/dates verified. Rejected records excluded. Missing-clause findings are policy-only potential omissions, never confirmed absence. Evidence validity does not establish legal interpretation. |
| `app/services/contract_analysis.py` | Reuses playbook, instruction checks, retrieval, reasoning and verifier; constructs completed/partial Analysis; persists successful output or explicit AnalysisFailure on errors. Attempts, stage, upstream status and processing time recorded. No synthetic fallback. |
| `app/services/storage.py` | SQLite storage, account scoping and additive migrations for contracts, analyses, failures, users, subscriptions, payment events and usage. No database reset is needed for benchmarking. |
| `app/models/contracts.py` | Seven production categories; strict RiskDraft/ObligationDraft; separate source facts and interpretation; evidence statuses verified/unsupported/needs_review. Analysis statuses completed/partial; failure is a separate failed record. Human review always required. |
| `app/routes/contracts.py` | Authenticated PDF upload, synchronous `POST /api/analyze`, account-scoped `GET /api/analysis/{analysis_id}`; analysis quota and retention enforced. Public static `GET /api/demo/analysis`. |
| `app/services/demo.py` | Existing explicit synthetic snapshot is reverified deterministically; no AI calls and no live-failure substitution. It is not benchmark gold. |

No dedicated evaluation package existed before this work. Existing tests cover extraction, embeddings, structured reasoning, evidence, retry boundaries, demo stability, API storage, authentication, billing and quota enforcement. The earlier demo and historical live artifacts were inspected for architecture only; neither was copied as benchmark gold or presented as a new live baseline.

## Dataset and assumptions

`synthetic_v1`, version 1.0.0: **12 original synthetic contracts**, **42 annotations**:
21 present risks, 3 missing requirements, 14 present non-risk targets and 4 ambiguous/context-dependent targets. Types: supplier agreements (3), SaaS (2), NDA (2), services (3), consulting (2).

The protected party is Company, procuring work/data services. These are short English-language text PDFs, not real customer or copyrighted agreements. One target explicitly spans a page boundary and has two evidence spans. The set includes opposing indemnity allocations, different licensing rights, protective clauses with adverse overrides, nominal caps, termination/interest/deletion departures, missing clauses and ambiguous terms.

The first seven policy categories use a frozen copy of the application's synthetic sample-company-policy v1.0. Severity is an author judgment: low for the annotated compliant target, medium for illustrative exit/payment/confidentiality/venue issues, high for illustrative nominal liability, supplier-misconduct indemnity, data and revocable bespoke IP exposure. These are **not universal legal rankings**; value, jurisdiction, bargaining position and other contractual provisions may change them. Targets marked non-risk mean only the annotated issue satisfies the stated assumption, not that the whole agreement is compliant.

A supplementary `BENCH-LAW-001` assumes Company prefers England and Wales law and London courts; fictional foreign exclusive law/forum is a negotiation departure. This rule is clearly separate in `benchmark_playbook.json`. Production lacks `governing_law` in both its schema and playbook. The live adapter does not inject the supplementary rule or change prompts: all-eight-category results will expose that coverage gap rather than silently exclude it. Use per-category results to distinguish this gap from model error.

Missing annotations are author-reviewed absence **within these authored short documents**, not invented quotes. A missing liability requirement in the services example assumes Company expects explicit allocation. The research NDA's missing notification target assumes personal data is involved. Cross-page data protection interpretation uses both fragments; either identified fragment can locate the target, but a returned quotation must still pass the production single-page/single-clause verifier.

Every annotation contains the requested contract/finding ID, category, expected severity, original quote/page, explanation, risk_present, confidence and reviewer status, plus explicit annotation_state, policy ID and evidence spans. Primary expected text/page equals the first span; further spans preserve cross-page context. Missing annotations have null text/page and no spans. Ambiguous annotations use risk_present=null and no forced severity. Confidence high/medium/low is descriptive author confidence, not a calibrated probability or metric weight.

All labels are **pending_manual_review**, hand-authored judgments, not externally or legally validated. Text and annotation intent are explicit in `build_fixtures.py`; labels were not copied from existing or newly generated model output. Exact stored gold quotations are obtained from their authored source fragments to preserve PDF line wrapping, not to assign labels automatically. This does not constitute independent human annotation.

The loader validates file hashes, unique IDs, source offsets, consecutive pages, gold references and exact PDF-to-source round-trip through existing extraction. It fails rather than silently skipping malformed data. Fixtures preserve original text for audits; report bodies and console output use IDs and reason codes instead of printing contracts.

## Fixture versus live execution

The default runner and `--dry-run` path use explicit canned predictions from a separate plan. These intentionally include duplicates, false positives, missed risks, wrong category/severity, whitespace changes, fabricated/empty quotes, wrong pages and nonexistent clauses. They also include one partial outcome with a rejected record and one entirely failed simulated provider outcome.

**Fixture metrics test the evaluator only. They are not measured Gemini accuracy, model latency, API reliability or usage.** Simulated attempt counts and HTTP statuses remain under a fixture-labelled report; their values are not evidence of real network requests.

Only `--live` lazy-loads the live adapter. The user has not authorized execution yet. After approval, it reuses existing extraction, `analyze_contract`, save/get contract/analysis/failure functions with actual services. All SQLite migrations/inserts go to a temporary benchmark database, which is removed when the standalone run ends; source and report IDs remain auditable via fixtures/reports, not the application DB. Authentication/quota/billing HTTP routes are intentionally outside this service-level benchmark. The process restores the original storage setting even on failure; do not embed this adapter concurrently in the running server.

Live metrics measure **returned post-verification findings**. The engine exposes rejection metadata/counts but not discarded raw predictions. Consequently rejected findings contribute to unsupported-evidence counts, but cannot be classified by quote existence or risk target; raw-model precision and raw exact-quote rates cannot be recovered. Rejected obligations are counted separately, not mixed into risk-finding denominators. These restrictions are explicitly recorded.

## Matching and risk metrics

1. Restrict definite positive gold to state risk or missing. Non-risk targets supply negative examples; ambiguous targets are held separate.
2. Only predicted risky, conflicting or missing findings are detection-positive. Compliant or ambiguous predictions against a definite positive produce a missed risk; inactive predictions are counted separately.
3. For a present target, a candidate match requires a matching source clause ID in one gold evidence span, **or** a nonempty whitespace-normalized quote/subquote overlap with a span on the same page. No LLM or semantic similarity is used in scoring.
4. For a missing target, candidate matching requires predicted status missing and the exact policy ID. No quotation is required or inferred.
5. Category and severity are deliberately not matching gates, so a located risk assigned the wrong category is a detection TP and a classification error.
6. Match maximum cardinality through deterministic augmenting paths. Candidate preference: exact quote first, then gold ID. Input prediction order is retained. Each prediction and gold may participate at most once. This avoids greedy match losses and duplicate inflation.
7. Remaining active predictions may match ambiguous targets one-to-one and be excluded from binary scoring; duplicates beyond one prediction per ambiguous target remain FPs. Predictions unmatched to any positive/ambiguous target are FPs; unmatched positive gold are FNs. Flags identify FPs on known non-risk targets.
8. Failed analyses have no substituted findings; **all their positive gold remain FNs**. Partial output is evaluated as actually returned; missing targets remain FNs. Missing or duplicate outcomes are validation failures, not dropped cases.

Detection TP means the prediction identifies an annotated risk **target**, not that the rationale is legally correct. Clause identity can locate a target even if a quote/page is invalid. Evidence is independently measured; an additional supported_evidence_detection score removes unsupported returned predictions and rescales the same gold. Multiple legal issues in one source clause can be ambiguous under this heuristic; one-to-one constraints prevent one finding claiming every issue, but matching is not a semantic entailment judge.

For each category, correctly classified matched risk is TP. Misclassified matched risk contributes FN to the gold category and FP to the predicted category. Unmatched predictions/gold contribute FP/FN in their categories. Category micro counts sum across categories; they differ from category-independent detection counts when classifications are wrong.

- Precision = TP / (TP + FP).
- Recall = TP / (TP + FN).
- F1 = 2 TP / (2 TP + FP + FN).
- Classification micro F1 uses summed category counts.
- Macro F1 averages category F1 values with defined denominators; count of included categories reported.
- Category/severity accuracy and confusion matrices are **conditional on matched positive targets**. Unmatched risks are separately reported and not hidden.
- Binary true negatives and overall accuracy are not claimed: an open-ended finding inventory lacks a complete defensible negative universe.
- A zero denominator produces JSON null and CSV/Markdown N/A, not invented zero or perfect scores. When positives are missed, recall/F1 are legitimately zero even if precision is undefined.

An exact quote does not prove the risk explanation or legal conclusion. Interpretation errors are judged only against these synthetic author labels, and are not called hallucinations.

## Deterministic evidence metrics

Normalization replaces runs of Unicode whitespace with one ASCII space and strips leading/trailing whitespace. It does not lowercase, remove punctuation, fuzzy-match words or join pages.

Each non-missing finding is quote-eligible, including findings with absent/empty evidence:
- Exact quote match: nonblank quote occurs verbatim on **some original extracted page**.
- Normalized quote match: normalized quote occurs on some normalized original page.
- Correct page citation: exact quote occurs on the cited 1-based page.
- Normalized correct page: separate diagnostic with the same page and whitespace-only normalization.
- Supported: exact quotation, correct page, valid matching clause and known policy ID; no missing required evidence.
- Failure reasons: empty/missing quote, fabricated quote, whitespace-only mismatch, missing/nonexistent/wrong page, missing/nonexistent clause, clause-page mismatch, quote outside cited clause, unknown/missing policy. Multiple reasons do not multiply a finding's unsupported count.

Production verification remains strict exact; a normalized-only success is still unsupported under that standard. Gold/category checking is separate from policy-ID existence. Missing findings are quotation-ineligible policy-only omission candidates. Non-null quote/page/clause on a missing prediction is fabricated omission evidence. Even supported missing records are **not verified absence**.

Quote and citation rates use **returned quote-eligible findings** as denominator. Rejected raw findings are unavailable and excluded from those literal rates. Unsupported evidence count = returned unsupported findings + engine rejected findings. Unsupported/evidence-failure rate denominator = returned findings (including policy-only omissions) + rejected findings. Rejected obligations are separate. Full failures with no predictions/rejections have N/A literal rates rather than successful verification. Error-reason breakdown counts reasons, so its sum may exceed unsupported findings.

## Metadata, latency, usage and reports

Each run records UTC timestamp, dataset version/manifest SHA-256, evaluator version/source hashes, effective configured model names, actual model identifier (null when fixture-only), response model when exposed, prompt SHA-256, engine source hashes and whitelisted effective configuration/hash. The system instruction is read via AST; no SDK client is created on the offline path. Generation/schema parameter changes are captured by module/schema source hashes. Secrets and their hashes are never included.

Fixture analysis latency, model token usage and costs are N/A. Runner wall time is separately labelled overhead. Live processing latency measures extraction, analysis, verification, SQLite persistence and retrieval in the adapter; it includes bounded retry time. Mean latency uses only observed values and reports availability count, including timed failures. It does not claim authenticated upload HTTP latency.

The production result currently exposes attempts and response model but not input/output token usage or prices. Optional Outcome token/cost fields can be aggregated only if available for every case; this adapter leaves them null. **No guessed prices, token counts or zero-cost estimate** is reported. No billable request was made in the offline task.

JSON contains full per-case matches, omissions, evidence flags, unmatched/missed IDs, conditional confusion matrices, status/error breakdown and provenance. CSV contains risk counts/metrics, evidence, reliability, classification, usage/latency, unmatched predictions and missed gold. Markdown describes the same baseline and limitations without full quoted contract text.

## Validation and limitations

Tests cover exact/normalized quotes, wrong/nonexistent pages, fabricated/empty evidence, missing fields, nonexistent clauses, omission evidence, duplicates, maximum matching, missing risks, false positives, category/severity separation, ambiguity, multiple findings/cross-page spans, empty datasets/zero denominators, missing outcomes/pages, failed/partial output, invalid labels, manifest tampering and offline CLI/reporting.

The full regression launcher disables RUN_AI_INTEGRATION and RUN_OLLAMA_INTEGRATION and blocks outbound connects, address resolution and async connection creation. Windows requires a loopback socketpair for asyncio internals; the guard permits only the exact stdlib socketpair caller, not Ollama or external HTTP. Existing auth/billing tests still run in their own temporary storage with mocked providers. No production database reset occurs.

Main limitations: small authored dataset, pending independent review, simplified page layouts, no OCR/languages/tables, coarse target matching, conditional classification metrics, governing-law production gap, no live results, no token/cost telemetry and no statistical confidence intervals. Recommended subsequent work: independent domain review/adjudication, larger balanced and adversarial holdout with multiple issue spans, approved live baseline and repeated variance runs, raw rejection/usage telemetry if authorized later, and retrieval/obligation-specific gold. No model/prompt tuning should precede a reviewed baseline.
