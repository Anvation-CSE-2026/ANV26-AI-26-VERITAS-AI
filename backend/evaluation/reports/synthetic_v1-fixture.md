# FIXTURE EVALUATION — NOT MODEL ACCURACY

Dataset: synthetic_v1 v1.0.0; contracts: 12; annotated risks: 24.

Synthetic labels are pending manual review. Fixture results measure evaluator behavior, not Gemini reliability.

Model actually evaluated: N/A.

| Scope | TP | FP | FN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|
| overall_detection | 17 | 3 | 7 | 0.850000 | 0.708333 | 0.772727 |
| liability | 3 | 2 | 1 | 0.600000 | 0.750000 | 0.666667 |
| indemnification | 1 | 0 | 1 | 1.000000 | 0.500000 | 0.666667 |
| termination | 2 | 0 | 2 | 1.000000 | 0.500000 | 0.666667 |
| payment | 2 | 1 | 1 | 0.666667 | 0.666667 | 0.666667 |
| confidentiality | 3 | 0 | 0 | 1.000000 | 1.000000 | 1.000000 |
| data_protection | 3 | 1 | 1 | 0.750000 | 0.750000 | 0.750000 |
| intellectual_property | 1 | 0 | 1 | 1.000000 | 0.500000 | 0.666667 |
| governing_law | 1 | 0 | 1 | 1.000000 | 0.500000 | 0.666667 |

Classification micro F1: 0.727273; macro F1: 0.718750.
Category accuracy on matched risks: 0.941176; severity accuracy: 0.882353.

## Deterministic evidence

- returned_findings: 21
- quote_eligible_findings: 19
- omission_candidates: 2
- exact_quote_match_rate: 0.842105
- normalized_quote_match_rate: 0.894737
- correct_page_citation_rate: 0.789474
- normalized_correct_page_rate: 0.842105
- unsupported_evidence_count: 6
- rejected_finding_count: 1
- evidence_verification_failure_rate: 0.272727
- unsupported_evidence_rate: 0.272727
- rejected_quotes_not_available: 1

Evidence error breakdown: {"clause_page_mismatch": 1, "empty_or_missing_quote": 1, "fabricated_quote": 1, "nonexistent_clause": 1, "quote_not_exact_on_cited_page": 3, "quote_not_in_cited_clause": 2, "whitespace_only_mismatch": 1, "wrong_page": 1}

## Processing reliability

- completed: 10
- partial: 1
- failed: 1
- failure_rate: 0.083333
- error_breakdown: {'fixture_provider_transient': 1}
- rejected_obligations: 0
- Average analysis latency (seconds): N/A
- Input / output tokens: N/A / N/A
- Estimated API cost (USD): N/A

## Failures

- SYN-services_split: partial; stage=N/A; category=fixture_evidence_rejection; HTTP=N/A; upstream=N/A; attempts=0.
- SYN-supplier_failure: failed; stage=gemini_reasoning; category=fixture_provider_transient; HTTP=503; upstream=503; attempts=3.

## Unmatched predictions

- SYN-supplier_red: SYN-supplier_red-P02
- SYN-supplier_red: SYN-supplier_red-P04
- SYN-saas_green: SYN-saas_green-P01

## Missed gold annotations

- SYN-supplier_red: SYN-supplier_red-G04
- SYN-services_exit: SYN-services_exit-G02
- SYN-services_split: SYN-services_split-G03
- SYN-supplier_failure: SYN-supplier_failure-G01
- SYN-supplier_failure: SYN-supplier_failure-G02
- SYN-supplier_failure: SYN-supplier_failure-G03
- SYN-supplier_failure: SYN-supplier_failure-G04

## Limitations

- Gold labels are synthetic author judgments pending manual review, not legally validated.
- Detection uses source-target matching; literal evidence and legal interpretation are separate.
- Failed analyses retain all annotated risks as false negatives.
- Governing law is a benchmark-only category; the production schema/playbook lacks it.
- Live quote metrics cover returned findings; rejected raw quotes are not exposed by the engine.
- Token usage and costs are N/A because the current analysis result does not expose usage.
- Fixture processing latency is N/A; runner overhead is not model latency.

Source quotes are preserved in fixtures, not repeated in reports. Full per-case evidence reasons, confusion matrices, hashes and matching IDs are in JSON.
