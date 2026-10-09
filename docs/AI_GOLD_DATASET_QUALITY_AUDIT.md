# Gold dataset quality audit and human review preparation

Audit date: 2026-10-09. Branch: feature/ai-reliability. Dataset: synthetic_v1 v1.0.0. This is an offline dataset audit, not model tuning or a new accuracy evaluation.

## Dataset overview and readiness

All 12 synthetic PDFs were re-extracted using the existing extraction function and compared with their canonical source records. The dataset loader verified all 38 manifest file hashes, contract identities, clause offsets, policy references, schema coherence and evidence citations. There are 42 annotations and 40 evidence spans: 21 present risks, 3 missing-clause labels, 14 non-risk labels and 4 ambiguous labels. All 42 are pending_manual_review; none is human-approved. Confidence is author-assigned (35 high, 7 medium), not an empirical confidence score.

The dataset is technically valid and usable for diagnostic runs. It is **not ready for a credible adjudicated full-benchmark accuracy claim**. Human review of applicability, coverage and severity is needed before interpreting false positives as model errors. No labels were changed, and the existing single-contract scores were not recalculated.

## Annotation validation

The worksheet contains one row for every annotation, including category, severity, primary quote/page, all evidence spans, original state/confidence/reviewer status, policy ID and explanation. Contract IDs, annotation IDs, categories, explanations, confidence values and reviewer statuses are present and schema-valid. All annotation IDs are globally unique; no exact duplicate contract/category/state/evidence identities were found. Every present annotation has source evidence; all 40 quotes occur in the cited clause on the cited PDF page. Source clause offsets reproduce original page text. No incorrect quotations or page references were found.

Intentional nulls must not be mistaken for missing required fields: the three missing-clause labels have no quote, page or span; the four ambiguous labels have no severity. No unsupported category exists within the benchmark schema. Governing law is unsupported by the production taxonomy, as discussed below.

Mechanical evidence correctness does not establish policy applicability, severity, interpretation or completeness. For SYN-services_split-G01 the evidence spans pages 1 and 2: the first span introduces notification, and the second supplies the eight-day deadline and sixty-day deletion term. Review both. The second span includes an extracted repeated synthetic header; this is exact source text, not a fabricated quote, but can distract interpretation.

## Category coverage

Annotation counts: liability 6; indemnification 4; termination 6; payment 6; confidentiality 6; data protection 5; intellectual property 5; governing law 4. There are 41 annotated contract/category slots out of 96; two confidentiality annotations belong to SYN-nda_durable. The remaining 55 slots are review prompts, **not 55 proven missing risks**.

A = clearly missing annotation candidate requiring approval; B = ambiguous/context-dependent review; C = existing annotation coverage; D = outside production taxonomy. C means a target is represented, not that the category or contract is fully adjudicated. Existing ambiguous annotations are B; governing-law slots are D whether or not they contain gold.

| Contract | Liability | Indemnity | Termination | Payment | Confidentiality | Data | IP | Law |
|---|---|---|---|---|---|---|---|---|
| SYN-supplier_red | C | C | C | C | A | B | B | D |
| SYN-supplier_green | C | C | C | B | B | B | B | D |
| SYN-saas_red | B | B | B | C | B | C | C | D |
| SYN-saas_green | B | B | B | C | B | C | C | D |
| SYN-nda_short | C | B | B | B | C | B | B | D |
| SYN-nda_durable | B | B | B | B | C | C | B | D |
| SYN-services_exit | B | C | C | C | B | B | B | D |
| SYN-services_balanced | C | C | C | B | B | B | B | D |
| SYN-consulting_owned | B | B | B | C | C | B | C | D |
| SYN-consulting_retained | B | B | B | B | C | B | C | D |
| SYN-services_split | C | B | B | C | B | C | B | D |
| SYN-supplier_failure | C | B | C | B | B | C | B | D |

All substantive numbered provisions in these short source contracts are represented by existing gold spans; no clearly unannotated present numbered clause was identified. Uncovered category slots mostly concern absence and policy applicability. Page headers are not substantive risk clauses. The worksheet deliberately includes every uncovered category to make review scope explicit rather than infer risk from silence.

## Potential missing annotations and applicability

The supplier_red confidentiality omission is an A candidate under the unconditional mutual-confidentiality playbook. Review the full document and policy scope before approving it. Its existing termination omission also requires full-document review. Data-protection and IP omissions are B: the supplier source does not establish personal-data processing or bespoke deliverables/licence needs.

Across other contracts, unrepresented liability, indemnity, termination, payment, confidentiality, data and IP topics are B review prompts. NDA payment or procurement remedies, for example, may be inapplicable; an absent topic is not automatically a risky omission. Explicitly document applicable/not-applicable/insufficient-context decisions before expanding gold. Do not derive labels solely from Gemini output.

Three existing omission labels need separate scrutiny:

- SYN-supplier_red-G04 (termination): no termination provision in the synthetic PDF; confirm policy applicability and full-document absence.
- SYN-nda_durable-G03 (data protection): the explanation assumes research involves personal data, but the PDF does not state this. Absence of breach terms is observable; the personal-data premise is unsupported by this source. Adjudicate scope rather than silently changing the label.
- SYN-services_balanced-G04 (liability): absence of a fee-cap allocation needs review of protected party and allocation assumptions. Absence of a supplier cap does not by itself show a disadvantage to the company.

## Ambiguous classifications and contextual issues

Four ambiguous annotations exist: SaaS red confidentiality G04, NDA short IP G03, services balanced governing law G03, and consulting retained termination G03. Their uncertainty should be judged consistently against policy requirements. SaaS red's unspecified duration/mutuality is especially worth comparing with definite confidentiality deviations elsewhere.

NDA durable's confidentiality G01 describes a locally compliant provision, but G02 expressly overrides it with publication after ten days. These are not duplicate annotations; reviewers must distinguish local-clause compliance from whole-contract compliance. SaaS green's IP clause references Schedule A and consulting owned's IP clause references Schedule B; neither schedule is supplied. The ownership language is visible, but completeness of pre-existing IP identification is unverified. Supplier failure's breach clause does not explicitly identify personal data; check applicability of the personal-data policy.

## Unmatched live predictions and four omissions

Only the existing synthetic trace was read. Run ID: 1a9c514b-3b7b-4f60-839a-8d14558f60de; trace ID: d2144a9f-147a-4468-9ec0-7763481b2c2b. No new provider request occurred. The three unmatched predictions have no relevant present clause, quote, page or clause ID; their target is an alleged omission across the document.

| Prediction | Category / policy | Assessment | Evidence |
|---|---|---|---|
| SYN-supplier_red-LIVE-005 | Confidentiality / POL-CONF-001 | Potentially valid unannotated omission; full-document human review required | No quotation/page; retained needs_review; absence_confirmed=false |
| SYN-supplier_red-LIVE-006 | Data protection / POL-DATA-001 | Ambiguous/context-dependent; personal-data applicability unestablished | No quotation/page; retained needs_review; absence_confirmed=false |
| SYN-supplier_red-LIVE-007 | Intellectual property / POL-IP-001 | Ambiguous/context-dependent; deliverables/licensing applicability unestablished | No quotation/page; retained needs_review; absence_confirmed=false |

Categories agree with their referenced policies. None is confirmed incorrectly classified or an invented quotation. No current evidence justifies declaring all three hallucinations. Their support for a *confirmed risk* is unproven, and legal/business applicability requires human review. LIVE-004 termination matches existing gold G04 but is also an unconfirmed omission; hence four retained omissions require review. Retention is not proof of absence.

## Severity consistency

Gold uses 10 high, 14 medium and 14 low labels, plus 4 null ambiguous labels; there are no critical labels. The 14 low labels correspond to non-risk provisions, which conflates compliance with low risk if consumed without annotation_state. A written severity rubric and applicable-party perspective are missing from the annotation schema; author explanations do not substitute for adjudication.

Nominal liability caps (USD 10/25/50) and severe ownership/data deviations are generally high; termination/payment/confidentiality deviations and omissions are generally medium. This is an author convention, not a validated impact scale. Review confidentiality publication overrides versus ordinary duration failures, omission severity versus explicit harmful terms, and context-dependent fee/payment impact. Do not normalize severity automatically.

## Unsupported categories and metric limitations

Four governing-law annotations use BENCH-LAW-001, a synthetic benchmark-only rule; production has no governing-law category. The ambiguous governing-law label also requires review. Report supported-category performance separately when planning future reporting; do not change production taxonomy or silently remove these labels.

The unchanged matcher counts unmatched active predictions as FP even when gold is sparse. It can credit a missing-clause prediction by matching policy ID without proving absence. Present targets match by clause ID or quote overlap; any one span can match a multi-span annotation. Detection matching does not require category or severity agreement, which are scored separately. Ambiguous gold can exclude one matching prediction; duplicate predictions can still become FP. These rules mean the existing TP=3, FP=3, FN=0, precision=50%, recall=100%, F1=66.67% measure agreement with this sparse, unreviewed target inventory, not comprehensive Gemini accuracy or verified-risk precision. Source validity and semantic correctness must be reported separately.

## Human review worksheet and process

File: backend/evaluation/reviews/gold_review_v1.csv (UTF-8 BOM CSV). It has 100 unique rows: 42 existing labels, 55 coverage prompts and 3 unmatched live findings. The four ambiguous labels are included among existing rows. New REVIEW-* identifiers are worksheet identifiers only, not gold annotations. The extra columns preserve source state, confidence, original reviewer status, quote/spans, policy and audit context. Human decision, notes, reviewer ID and reviewed-at cells are all blank. Multiple spans are stored as JSON in evidence_spans; evidence_page remains the original primary page.

Review existing annotations independently from model findings first to reduce anchoring. Then assess omission scope/applicability and unmatched predictions. Use source PDFs, canonical source records and the synthetic playbook, not model output as evidence. Suggested human decisions: confirm, reject, revise, not_applicable, insufficient_context. Record identity, date, rationale and exact span changes. Obtain independent adjudication for disagreements and then create an explicitly versioned gold revision with updated hashes and changelog. This worksheet does not constitute approval or alter v1 scoring.

Priority improvements: (1) adjudicate the four supplier omissions and NDA personal-data assumption; (2) define policy applicability and clause-versus-contract annotation scope; (3) review all 42 labels and multi-span/schedule context; (4) establish severity and uncertainty rubrics; (5) version reviewed additions and report supported-taxonomy/evidence-qualified metrics separately. No scoring changes were implemented.

## Verification and audit artifacts

The standalone offline preparation script validates the dataset, creates the worksheet without overwriting an existing review, verifies unique worksheet IDs and blank human fields, and compares SHA-256 hashes of gold/source fixtures, production Python files and scoring/schema files. Its machine-readable audit records the category matrix and hashes. Worksheet authoring used standard-library CSV because the installed artifact-tool could not load in the restricted Node runtime (node:process import blocked); the saved CSV was round-trip checked.

Private raw traces remain owner-protected and gitignored. git ls-files backend/evaluation/private_traces returned no tracked files. Only synthetic fixtures and the existing synthetic trace were inspected; no customer contracts or production database were opened by this audit. No network services, authentication provider or billing provider were called. Full offline backend suite: 147 tests discovered, **144 passed, 3 live-service tests skipped, 0 failures/errors**, in 9.504 seconds. Command from backend: `.\.venv\Scripts\python.exe -m evaluation.run_offline_tests`. Outbound network was blocked by the offline runner. Authentication/billing, analysis, evidence, observability and benchmark regression tests passed using test fixtures/mocks. The existing fixture benchmark remained TP=17, FP=3, FN=7; these are fixture results, not model accuracy. A final protected-file hash comparison passed after the tests.

Files added: this report; backend/evaluation/reviews/gold_review_v1.csv; backend/evaluation/reviews/gold_quality_audit_v1.json; backend/evaluation/reviews/prepare_gold_review.py. No production, gold, scoring, authentication, billing or frontend files changed. No database reset or Git push occurred.
