# First live Gemini finding audit

## 1. Executive summary

**The analysis was partial because records were rejected by deterministic provenance checks and four retained findings were potential omissions requiring review. The exact four rejection reasons cannot be recovered from the saved artifacts.** Both rejection presence and omission review independently trigger partial status in the inspected production code.

The reported 40% precision, 66.67% recall and 50% F1 are arithmetically correct for the current post-verification matching rules. They do **not** establish that three model claims were wrong or that Gemini failed to notice indemnification. Sparse gold labels, unconfirmed omissions and missing rejected-output traces prevent those conclusions.

Confirmed scope:

- Contract: `SYN-supplier_red`; analysis: `a1aaa7af-7bfc-432c-abc1-abbd4d474f9d`.
- Model: `gemini-3.5-flash`; run timestamp: 2026-10-08T15:57:58.106741+00:00.
- Seven proposed findings, derived from five retained plus two rejected findings. Two obligations were rejected; the total proposed/retained obligation counts are unavailable.
- One retained source-quoted finding and four retained policy-only omissions.
- One Gemini generation attempt; no Gemini request retries recorded.
- No new Gemini calls, Ollama calls, benchmark evaluations or tests involving providers were made during this audit.
- No production code, prompt, model, settings, gold annotation, authentication, billing, frontend or database modifications. Only this report was created. No commits or pushes.

**Main investigation blocker:** `live_adapter.py` retrieved the full verified Analysis from temporary SQLite but reduced it to selected Prediction fields and rejection counts. `evaluator.py` then reduced those predictions to match/evidence flags. Full proposed drafts were never archived, full verified analyses/rejection reasons were not exported, and temporary SQLite was deleted when the process exited.

### Artifacts and provenance checked

Sources: [live JSON](../backend/evaluation/reports/synthetic_v1-live.json), [CSV](../backend/evaluation/reports/synthetic_v1-live.csv), [Markdown](../backend/evaluation/reports/synthetic_v1-live.md), [recovery report](AI_EMBEDDING_RECOVERY_SMOKE.md), [gold annotations](../backend/evaluation/fixtures/annotations/supplier_red.json), [canonical source](../backend/evaluation/fixtures/contracts/supplier_red.json), [synthetic playbook](../backend/app/resources/sample_playbook.json), and the adapter/evaluator/verifier/analysis/schema/retrieval/runner source files.

The live artifact's recorded hashes match every inspected engine module, evaluator module and dataset manifest. All 38 manifest-listed fixture files also match their digests, including the actual source PDFs and gold annotation files; the manifest itself matches the run's recorded hash. This supports applying the current source logic to the historical run. A narrowly scoped **read-only SQLite query** found no target analysis in the configured production database. The documented adapter used a TemporaryDirectory and did not store this analysis in production. Searches of existing report/document artifacts found no archived draft or full target Analysis. Historical sample/demo findings and example API rejection codes are not records from this run and were not substituted.

These checks establish what is available in the workspace; they do not claim recovery from deleted temporary storage or unidentified external backups.

## 2. Finding-by-finding analysis

### Identifier and availability rules

`RiskDraft` has no model-generated finding identifier. The adapter assigns `SYN-supplier_red-LIVE-001` through `005` **after rejection/filtering**, based on retained-list order. These are evaluator IDs, not original Gemini array indices. Rejected records originally had array indices in RejectedRecord, but those indices were discarded.

Use the full prefix `SYN-supplier_red-` for abbreviated LIVE IDs below. “Rejected A/B” are audit row labels for the two counted rejected findings, **not recovered IDs or original ordering**. Gold IDs use that same contract prefix.

All seven generated explanations are unavailable. Every exact generated quote string is unavailable. Gold/source text must not be represented as a recovered model quotation.

| Finding identifier | Risk category | Severity | Evidence verification assessment | Retained/rejected | Matched gold |
|---|---|---|---|---|---|
| `SYN-supplier_red-LIVE-001` | liability, inferred uniquely from matched gold and category_correct=true | critical, inferred uniquely from severity confusion | Exact and normalized quote and page checks passed; original evidence_status enum unavailable | Retained | `SYN-supplier_red-G01` |
| `SYN-supplier_red-LIVE-002` | termination, inferred from matched gold and category_correct=true | medium, inferred from gold plus severity_correct=true | Policy-only missing finding; no quotation verified; production needs_review inferred from verifier | Retained | `SYN-supplier_red-G04` |
| `SYN-supplier_red-LIVE-003` | One of confidentiality/data_protection/intellectual_property; ID mapping unavailable | Unavailable | Policy-only missing finding; requires review; absence not confirmed | Retained | None |
| `SYN-supplier_red-LIVE-004` | One of confidentiality/data_protection/intellectual_property; ID mapping unavailable | Unavailable | Policy-only missing finding; requires review; absence not confirmed | Retained | None |
| `SYN-supplier_red-LIVE-005` | One of confidentiality/data_protection/intellectual_property; ID mapping unavailable | Unavailable | Policy-only missing finding; requires review; absence not confirmed | Retained | None |
| Rejected A — original ID/index unavailable | Unavailable | Unavailable | Production RejectedRecord evidence_status=unsupported, inferred from rejection type | Rejected | Not evaluated; cannot determine |
| Rejected B — original ID/index unavailable | Unavailable | Unavailable | Production RejectedRecord evidence_status=unsupported, inferred from rejection type | Rejected | Not evaluated; cannot determine |

The three unmatched categories form an **unordered multiset with one occurrence each**, established by per-category FP counts. Neither CSV nor JSON preserves the category-to-ID mapping. Assigning confidentiality to LIVE-003, data protection to LIVE-004 and IP to LIVE-005 would invent their ordering.

| Finding identifier | Generated explanation | Supporting quote | Cited page | Exact rejection reason |
|---|---|---|---|---|
| LIVE-001 | Unavailable | Actual quote unavailable; at least one nonblank exact source substring was returned | 1 inferred from source-target matching plus successful clause/page checks; original field not archived | Not applicable: retained |
| LIVE-002 | Unavailable | null inferred from supported missing-finding check; not a missing data error | null inferred for omission | Not applicable: retained |
| LIVE-003 | Unavailable | null inferred for omission | null inferred for omission | Not applicable: retained |
| LIVE-004 | Unavailable | null inferred for omission | null inferred for omission | Not applicable: retained |
| LIVE-005 | Unavailable | null inferred for omission | null inferred for omission | Not applicable: retained |
| Rejected A | Unavailable | Unavailable; may have been present, null or mismatched | Unavailable | Unavailable; count alone preserved |
| Rejected B | Unavailable | Unavailable; may have been present, null or mismatched | Unavailable | Unavailable; count alone preserved |

LIVE-001's page inference follows both matching paths: valid clause identity with the sole liability gold span fixes page 1; the quote fallback also requires that span's page. Successful evidence checks enforce clause/page consistency. This does **not** recover the quote string or prove it equals the entire gold quote.

Known reference source, not model output: G01 describes the USD 50 liability cap including fraud/data breaches on page 1. Gold severity is high; the prediction's critical severity is a confirmed disagreement with the author label, not proof of a universal severity error.

## 3. Why the result was partial and why records were rejected

### Confirmed partial-status causes

[contract_analysis.py](../backend/app/services/contract_analysis.py) computes partial if any verification rejection, source warning or review-needed record/alert exists. In this run:

1. Two finding plus two obligation rejection counts imply four verifier rejection records. This alone forces partial.
2. Four supported missing findings must be emitted by [evidence.py](../backend/app/services/evidence.py) with evidence_verified=false, evidence_status=needs_review, potential_omission=true, complete_document_review_required=true and absence_confirmed=false. This independently forces partial.
3. Canonical source warnings are empty. Alert and other uncertainty/assumption details were not archived; no additional reason is asserted.

Partial does not indicate HTTP/provider failure. The successful run contains no error_category or failed_stage and one generation attempt.

### What can be ruled out

The entire JSON response must pass strict `AnalysisDraft.model_validate_json` before the verifier runs. Pydantic failures cause a failed analysis with invalid_structured_output, not selective per-record rejections in a successful partial result. Therefore **invalid typed schema or genuinely missing schema-required fields do not explain these four verifier rejections under the recorded code path**.

A schema-valid finding can still omit/null its optional source fields and fail provenance. That is different from a missing Pydantic-required field. An obligation's required quote/page/clause/party/deadline fields must be structurally present; nullable party/deadline can legitimately be null.

### Actual verifier taxonomy — possible causes, not observed assignments

The verifier records the **first applicable reason**, so even a preserved rejection reason would not enumerate every defect.

| Requested classification | Actual reason codes in production | Evidence in this run |
|---|---|---|
| Missing quotation / quotation mismatch | quote_not_in_original_clause covers null/blank finding quote, paraphrase, whitespace changes, quote outside clause/page | Possible; no record-specific reason retained |
| Incorrect page | wrong_page_number | Possible; not confirmed |
| Unsupported clause/source | unknown_clause_id, source_offset_mismatch | Possible; not confirmed |
| Invalid schema | Whole-response invalid_structured_output before verifier | Excluded as the selective rejection mechanism here |
| Missing required evidence field | Nullable missing clause leads unknown_clause_id; null/wrong page leads wrong_page_number; null quote may reach quote_not_in_original_clause | Possible for findings if structurally valid; not confirmed |
| Unsupported parties/dates | referenced_party_not_in_evidence, referenced_date_not_in_evidence | Possible finding rejection; not confirmed |
| Unsupported obligation party/deadline | party_not_explicit_in_evidence, deadline_not_explicit_in_evidence | Possible obligation rejection; not confirmed |
| Other policy provenance | unknown_policy_id, policy_category_mismatch, policy_requirement_mismatch | Possible finding rejection; not confirmed |
| Invalid omission provenance | missing_finding_has_contract_evidence, missing_finding_has_source_references | Possible finding rejection; not confirmed |

Obligations are checked for known source clause, correct page, source offsets, exact quote, then exact word-boundary responsible-party/deadline references. There are no policy-category checks for obligations. A predicted inferred deadline or party may fail the reference rule, but no such inference is established from this run's artifact.

The source indemnification and payment clauses contain extraction line breaks. If a model removed those breaks, exact matching would reject the quotation. **This is a hypothesis, not a recovered cause.** Policy text paraphrasing, wrong references and other listed failures are also possible. The counts do not prove that the rejected findings were indemnification/payment or that exactly seven policy categories were generated once.

There are two rejected obligations, but their original IDs/indices, descriptions, parties, deadlines, quotes, pages and exact reasons are unavailable. No rejected obligation can be tied to a particular source sentence from counts alone.

## 4. False-positive investigation

The only positive gold targets are liability, indemnification and missing termination. Payment is annotated non-risk. Confidentiality, data protection and intellectual property have **no annotation at all for this contract**. The production prompt nevertheless asks for all seven playbook rules to be analyzed. This is a direct scope mismatch between generation and reference coverage.

The matcher counts any remaining active prediction as FP unless it matches an ambiguous gold target. It does not distinguish an unreviewed/unknown category from a reviewed negative. The report's non_risk_false_positives is empty: none of these three FPs is established as a contradiction of the reviewed payment negative.

### Classification for each unmatched ID

| Unmatched finding | Audit disposition A–E | Why |
|---|---|---|
| SYN-supplier_red-LIVE-003 | **E: impossible to determine without human review** | Exact category mapping, explanation, severity and applicability rationale were lost; it is a policy-only omission for one of the three unannotated categories |
| SYN-supplier_red-LIVE-004 | **E: impossible to determine without human review** | Same data loss; an unmatched score is not proof of an incorrect observation |
| SYN-supplier_red-LIVE-005 | **E: impossible to determine without human review** | Same data loss; no quote was fabricated in the retained omission structure |

### What can be assessed at category level

These are assessments of source coverage, **not reconstructions of the missing generated explanations**.

| Omission category, mapping to ID unknown | Source/playbook inspection | Possible classification, qualified |
|---|---|---|
| Confidentiality | All three pages contain liability, indemnification and payment; there is no confidentiality duty/purpose/survival provision. The supplied playbook requires one. | **B is plausible for the limited observation that a policy provision is absent**. Exact finding correctness/qualification remains E until its explanation is available and reviewed. |
| Data protection | No notification/security/deletion provision exists. “Data breaches” appears in liability, but does not establish personal-data processing or supplier role. | Literal absence is consistent with source; material policy applicability is **D, context-dependent**, and the particular lost finding remains E. |
| Intellectual property | Supplier owes no IP defense addresses indemnification, not bespoke ownership or durable license. No bespoke-deliverable allocation appears; equipment context does not establish paid bespoke work. | Literal absence is consistent with source; whether the bespoke-IP rule applies is **D, context-dependent**, and the lost finding remains E. |

No retained unmatched finding is confirmed A (genuine unsupported/incorrect risk) or C (valid observation assigned a demonstrably wrong category). None is established as a hallucination. Conversely, all three cannot be declared fully valid merely because a clause is absent: applicability and the missing generated explanations still matter.

## 5. False-negative investigation

Missed gold: **SYN-supplier_red-G02**, indemnification, expected high severity, policy POL-INDEM-001, page 2, clause P002-C002. Exact gold/source text:

```text
2. Company shall indemnify Supplier for every claim, including claims caused by Supplier
negligence. Supplier owes no IP defense.
```

This is reference text, not recovered Gemini evidence. It supports the author interpretation that Company bears supplier-negligence exposure and supplier IP defense is absent. The uncapped “every claim” scope and severity remain pending independent review; the label is not legally validated.

| Possible FN explanation | Audit conclusion |
|---|---|
| Gemini did not identify the clause | Possible; raw draft unavailable |
| Gemini identified it but assigned another category | Possible in rejected/lost output; no retained indemnification finding exists. Category mismatch **alone** would not cause a detection FN, because candidate matching does not require category equality. |
| Gemini identified it but verifier rejected it | Possible; either rejected finding could concern it, but no original category/index/reason survives |
| Matching algorithm failed | No demonstrated matching failure. No returned finding has a confirmed indemnification source target: the sole quoted record matched liability, all others are missing findings. Missing-status findings cannot match a present-risk annotation. Wrong source targeting/status could matter, but exact fields were lost. |
| Gold requires review | Yes: every annotation is pending manual review; the clause combines two legal issues in one target and severity/context may need adjudication. Source text and page are valid. |

**Confirmed conclusion:** the final post-verification output did not match G02. It is an end-to-end recall loss. It cannot be attributed specifically to Gemini detection, categorization, quotation, provenance rules or matching from the available artifact.

## 6. Evidence verification assessment

- The single retained quote-eligible finding passes exact/normalized quote existence and exact/normalized cited-page tests: **1/1**. This confirms literal support for that returned record, not legal interpretation.
- Four retained omissions are quote-ineligible and require human/full-document review. They do not add four verified contract quotations or four verified absences.
- Returned evidence_error_breakdown is empty because every **retained** record passes the evaluator's applicable structural tests. It excludes production rejection reasons and does not mean no rejection happened.
- Unsupported evidence count=2 comes entirely from rejected findings. Reported rejection/failure rate is **2/(5 retained+2 rejected)=28.57%**. These failures could include policy/reference provenance, so this must not be described as a fabricated-quotation rate.
- Two rejected obligations are recorded separately and excluded from finding denominators. Total proposed obligation count and obligation success rate are unavailable.
- Exact quotation rate=100% refers to **one retained quote**, not all seven proposed findings. Including four policy-only omissions in the supported denominator dilutes some interpretation of evidence failure rates; rejected raw quotes are unavailable.
- The evaluator's supported=true for a missing finding means valid policy-only omission shape, not evidence_verified=true. Its supported_evidence_detection consequently still contains all four omissions. The equal supported/original risk metrics are not proof that every predicted risk is grounded in verified contract evidence.
- LIVE-001 production evidence_verified=true follows from being non-missing and accepted. Its exact evidence_status enum could be verified or needs_review due to assumptions/unreliable matching; those flags were lost. Missing records' needs_review enum is determined by the verified source logic.

## 7. Metric validity and limitations

The recorded calculations are:
precision=2/(2+3)=0.40; recall=2/(2+1)=0.666666…; F1=4/(4+3+1)=0.50. No scores were recomputed under changed labels/rules.

| Issue | Current behavior | Validity/limitation |
|---|---|---|
| Missing clauses | Missing gold is detection-positive; prediction matches by missing status plus exact policy ID, without quote | Reasonable omission-target scoring under reviewed applicability. It does not demonstrate verified absence or literal grounding. Should be distinguished from present-clause detection. |
| Sparse gold | Unmatched active predictions become FPs even in unannotated categories | Main precision limitation in this run. The reference inventory is not exhaustive; closed-world FP interpretation is unsafe. |
| Multiple findings per clause | Maximum-cardinality one-to-one matching prevents one prediction matching several labels; extra predictions become FP | Stops duplicate inflation, but one gold annotation may bundle several issues. Multiple independently valid findings may be penalized if reference granularity differs. Original rejected/returned explanations are needed for adjudication. |
| Rejected predictions | Risk scoring uses accepted findings only; rejections add evidence counts but no risk-matching data | Measures final product output, not raw Gemini detection/precision. Rejected true risks can become FN; rejected false risks disappear from risk FP counts. |
| Unsupported categories | Governing law is separately tagged/per-category reported, but global eight-category aggregates still include it | Full-dataset scores conflate a schema/playbook coverage gap with model performance. This smoke contract has zero governing-law annotations, so it does not affect these scores. |
| Ambiguous gold | One-to-one match to ambiguous gold excludes remaining active predictions; duplicates beyond one remain FP | Separate handling exists, but ambiguous prediction status is inactive against definite positives, causing FN. This contract has no ambiguous gold. Unknown/unannotated targets are not handled like ambiguous gold. |
| Without verified evidence | Clause-target matching can score a TP independently of evidence; missing predictions can be supported without quote | Separation is intentional, but names like supported_evidence_detection can imply stronger grounding than present. Need explicit distinction between quotation verification and potential omission. |
| Source-based matching | Same clause ID or same-page normalized quote containment locates targets; category is not a gate | Not semantic entailment. Short generic subquotes or multi-issue clauses can cause misleading target matches. Exact supporting quote does not prove explanation correctness. |
| Conditional category/severity metrics | Confusion and accuracy use only matched positives | 100% category accuracy applies to two matched targets. Severity accuracy 50% reflects critical-vs-high liability disagreement and matched medium termination, not all seven proposals. |
| Legal validity | All gold labels pending manual review | Even a gold disagreement is not automatically a model legal error or hallucination. One document cannot establish general accuracy. |

No true-negative universe is enumerated, so the current open-ended finding inventory cannot support a reliable overall accuracy claim. The evidence verifier checks source and reference provenance, not semantic truth of risk reasoning or omission applicability.

## 8. Latency findings

Observed adapter processing time: **48.605386700015515 seconds**, displayed as 48.61. Observed runner_seconds: **49.01018669997575 seconds**. Their difference is **0.4048 seconds**, derived arithmetic, not a measured stage. Runner timing stops before report writing and printing; it includes dataset loading/validation, metadata hashing and scoring outside the timed adapter case.

| Stage | Supported timing |
|---|---|
| Selected PDF read/extraction | N/A; included in case timer, no span |
| Ollama embedding requests | N/A; no per-call durations/load timing/cache events stored |
| Policy ranking/retrieval overhead | N/A; no span distinct from embeddings |
| Gemini generation | N/A; one attempt observed, no SDK/round-trip/token timing stored |
| Evidence/schema verification | N/A; no span; raw draft and original Analysis timings not archived |
| SQLite contract write, analysis write and retrieval | N/A; included in case timer, no individual transaction spans |
| Selected case total | 48.6054 seconds, measured |
| Runner overhead outside selected case | 0.4048 seconds, derived, not allocated to individual work |

Normal fresh-process source path embeds seven rules plus six extracted clauses, **13 expected local embedding calls**. Three of the six clauses are repeated page headings. This is a code-derived expectation under a cold policy cache, not a logged request count or duration; it cannot establish whether embeddings or Gemini dominated runtime. Similarity ranks would be 18 matches under normal execution, but the actual semantic-match records were not exported.

The application Analysis also has a processing_seconds measured before analysis persistence and excluding upload/extraction, but that full record is gone. The benchmark retained only its broader adapter timer. Request timeout limits are not timing measurements. Prior connectivity probes and other historical runs cannot be used as this run's stage durations.

Missing instrumentation: monotonic stage spans, individual embedding request IDs/durations and cache-hit/load indicators, Gemini start/end/attempt metadata and usage, verification/schema duration, SQLite write/read durations, and the retained original application processing_seconds. No artificial allocation of the 48.61 seconds is defensible.

## 9. Recommended improvements, ranked by priority

These are recommendations only. **No implementation or scoring/gold changes were made.**

1. **P0 — Preserve forensic output for controlled synthetic runs.** Before temporary storage deletion, archive full verified Analysis and RejectedRecord index/reason/type, original stable proposal-to-retained IDs and compact prediction fields. Add an explicitly authorized benchmark observer for the pre-verification structured draft, including obligation proposals. Do not print raw output/credentials; restrict access and keep provenance hashes. Production prompts/models need not change to preserve observability.
2. **P0 — Resolve reference coverage through independent review.** Define applicability and exhaustive present/missing/non-applicable/unknown policy targets for each synthetic contract. Adjudicate the three omission categories and G02; do not retrofit this frozen gold version to the model's output. Any approved gold revision must be separately versioned with review history and an untouched holdout.
3. **P0 — Report scopes separately before claiming accuracy.** Clearly label current scores post-verification reference-target metrics; distinguish quoted present risks, potential omissions, reviewed negative FPs, unannotated/unknown predictions and unsupported production categories. Propose and test any scoring revision explicitly instead of silently changing baseline rules.
4. **P1 — Add stage telemetry and retain rejection taxonomy.** Time extraction, embedding calls/cache, ranking, Gemini each attempt, schema/evidence checks and SQLite operations. Preserve usage if exposed by SDK, without guessed costs or raw credentials. This permits targeted latency work later.
5. **P1 — Reproduce known verifier failure modes offline after causes are captured.** Exact line breaks, policy-text copying, source IDs/pages and party/deadline substrings are candidates. Use deterministic tests against the actual recovered record; do not weaken exact provenance or change prompts based on an unproven whitespace hypothesis.
6. **P1 — Review matching granularity.** Use reviewed issue spans/identities for multi-risk clauses and define handling of generic quote overlap, duplicates, inactive/ambiguous outputs and rejected proposed targets. Keep detection, category, severity and literal evidence separate.
7. **P2 — Add repeatable, approved broader measurements.** Only after observability and review, authorize a small live run and then a larger balanced holdout/variance study. Do not infer dataset-wide Gemini accuracy from this single partial analysis.

### Final determination

Confirmed: Gemini produced a schema-valid draft, four records failed deterministic provenance checks, four retained omissions required review, and final matching missed the indemnification target. Confirmed benchmark limitations: loss of forensic detail, incomplete gold coverage, policy-only support treated differently from quoted evidence, and aggregate-only timing.

Unresolved: the exact rejection causes, the original seven explanations/quotes and array positions, each unmatched ID's category/severity, semantic correctness of the omission claims, and the causal origin of the indemnification FN. Those gaps cannot be repaired by inventing records or making an unauthorized new model call.
