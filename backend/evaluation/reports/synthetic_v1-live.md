# LIVE MODEL EVALUATION

Dataset: synthetic_v1 v1.0.0; contracts: 1; annotated risks: 3.

Synthetic labels are pending manual review. Fixture results measure evaluator behavior, not Gemini reliability.

Model actually evaluated: gemini-3.5-flash.

| Scope | TP | FP | FN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|
| overall_detection | 3 | 3 | 0 | 0.500000 | 1.000000 | 0.666667 |
| liability | 1 | 0 | 0 | 1.000000 | 1.000000 | 1.000000 |
| indemnification | 1 | 0 | 0 | 1.000000 | 1.000000 | 1.000000 |
| termination | 1 | 0 | 0 | 1.000000 | 1.000000 | 1.000000 |
| payment | 0 | 0 | 0 | N/A | N/A | N/A |
| confidentiality | 0 | 1 | 0 | 0.000000 | N/A | 0.000000 |
| data_protection | 0 | 1 | 0 | 0.000000 | N/A | 0.000000 |
| intellectual_property | 0 | 1 | 0 | 0.000000 | N/A | 0.000000 |
| governing_law | 0 | 0 | 0 | N/A | N/A | N/A |

Classification micro F1: 0.666667; macro F1: 0.500000.
Category accuracy on matched risks: 1.000000; severity accuracy: 0.666667.

## Deterministic evidence

- returned_findings: 7
- quote_eligible_findings: 3
- omission_candidates: 4
- exact_quote_match_rate: 1.000000
- normalized_quote_match_rate: 1.000000
- correct_page_citation_rate: 1.000000
- normalized_correct_page_rate: 1.000000
- unsupported_evidence_count: 0
- rejected_finding_count: 0
- evidence_verification_failure_rate: 0.000000
- unsupported_evidence_rate: 0.000000
- rejected_quotes_not_available: 0

Evidence error breakdown: {}

## Processing reliability

- completed: 0
- partial: 1
- failed: 0
- failure_rate: 0.000000
- error_breakdown: {}
- rejected_obligations: 0
- Average analysis latency (seconds): 53.278175
- Input / output tokens: 2629 / 1567
- Estimated API cost (USD): N/A
- Provider total tokens: 8836

## Observability

- proposed_finding_count: 7
- retained_finding_count: 7
- proposed_obligation_count: 2
- retained_obligation_count: 2
- rejection_reason_counts: {}

## Failures

- SYN-supplier_red: partial; stage=N/A; category=N/A; HTTP=N/A; upstream=N/A; attempts=1.

## Unmatched predictions

- SYN-supplier_red: SYN-supplier_red-LIVE-005
- SYN-supplier_red: SYN-supplier_red-LIVE-006
- SYN-supplier_red: SYN-supplier_red-LIVE-007

## Missed gold annotations


## Limitations

- Gold labels are synthetic author judgments pending manual review, not legally validated.
- Detection uses source-target matching; literal evidence and legal interpretation are separate.
- Failed analyses retain all annotated risks as false negatives.
- Governing law is a benchmark-only category; the production schema/playbook lacks it.
- Live quote metrics cover returned findings; rejected raw quotes are not exposed by the engine.
- Token usage and costs are N/A because the current analysis result does not expose usage.
- Fixture processing latency is N/A; runner overhead is not model latency.

Source quotes are preserved in fixtures, not repeated in reports. Full per-case evidence reasons, confusion matrices, hashes and matching IDs are in JSON.
