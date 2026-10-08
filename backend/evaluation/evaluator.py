"""Aggregate independent risk, evidence, reliability and latency measurements."""
from collections import Counter
from statistics import mean
from .schema import Dataset, Outcome, CATEGORIES
from .risk_metrics import score_case, metrics
from .evidence_metrics import check_evidence, summarize, ratio

def evaluate(dataset: Dataset, outcomes: list[Outcome]) -> dict:
    by_id = {o.contract_id: o for o in outcomes}
    ids = {c.contract.contract_id for c in dataset.cases}
    if len(by_id) != len(outcomes) or set(by_id) != ids:
        raise ValueError("Outcomes must cover each dataset case exactly once")
    details, evidence, rejections = [], [], 0
    for case in dataset.cases:
        o = by_id[case.contract.contract_id]
        ev = [check_evidence(p, case.contract, set(dataset.policy_ids)) for p in o.predictions]
        scored = score_case(o.predictions, case.annotations)
        supported = [p for p, e in zip(o.predictions, ev) if e["supported"]]
        verified = score_case(supported, case.annotations)
        details.append(dict(contract_id=o.contract_id,status=o.status,risk=scored,
            supported_evidence_detection=verified["detection"],evidence=ev,
            processing_seconds=o.processing_seconds,analysis_id=o.analysis_id,
            error_category=o.error_category,failed_stage=o.failed_stage,http_status=o.http_status,
            upstream_http_status=o.upstream_http_status,attempts=o.attempts,
            failure_recorded=o.failure_recorded,response_model=o.response_model,
            rejected_finding_count=o.rejected_finding_count,
            rejected_obligation_count=o.rejected_obligation_count,
            proposed_finding_count=o.proposed_finding_count,retained_finding_count=o.retained_finding_count,
            proposed_obligation_count=o.proposed_obligation_count,retained_obligation_count=o.retained_obligation_count,
            trace_id=o.trace_id,trace_file=o.trace_file,trace_observation_failed=o.trace_observation_failed,
            rejection_reason_counts=o.rejection_reason_counts))
        evidence.extend(ev)
        rejections += o.rejected_finding_count
    def sum_metric(items):
        return metrics(*(sum(m[k] for m in items) for k in ("tp","fp","fn")))
    detection = sum_metric([d["risk"]["detection"] for d in details])
    verified_detection = sum_metric([d["supported_evidence_detection"] for d in details])
    categories = {c: sum_metric([d["risk"]["per_category"][c] for d in details]) for c in CATEGORIES}
    micro = sum_metric(list(categories.values()))
    macro_values = [m["f1"] for m in categories.values() if m["f1"] is not None]
    matches = [m for d in details for m in d["risk"]["matches"]]
    cat_conf, sev_conf = Counter(), Counter()
    for d in details:
        for row in d["risk"]["category_confusion"]:
            cat_conf[(row["gold"],row["predicted"])] += row["count"]
        for row in d["risk"]["severity_confusion"]:
            sev_conf[(row["gold"],row["predicted"])] += row["count"]
    latency = [o.processing_seconds for o in outcomes if o.processing_seconds is not None]
    failures = [o for o in outcomes if o.status == "failed"]
    annotations = [a for c in dataset.cases for a in c.annotations]
    tokens_known = bool(outcomes) and all(o.input_tokens is not None and o.output_tokens is not None for o in outcomes)
    costs_known = bool(outcomes) and all(o.estimated_cost_usd is not None for o in outcomes)
    return dict(dataset_size=len(dataset.cases),annotation_count=len(annotations),
        annotated_risks=sum(g.annotation_state in ("risk","missing") for g in annotations),
        missing_clause_annotations=sum(g.annotation_state == "missing" for g in annotations),
        non_risk_annotations=sum(g.annotation_state == "non_risk" for g in annotations),
        ambiguous_annotations=sum(g.annotation_state == "ambiguous" for g in annotations),
        reviewer_status_counts=dict(Counter(a.reviewer_status for a in annotations)),
        detection=detection,supported_evidence_detection=verified_detection,
        per_category=categories,classification_micro=micro,
        micro_f1=micro["f1"],macro_f1=mean(macro_values) if macro_values else None,
        macro_categories_with_defined_f1=len(macro_values),
        category_accuracy_on_matched_risks=ratio(sum(m["category_correct"] for m in matches),len(matches)),
        severity_accuracy_on_matched_risks=ratio(sum(m["severity_correct"] for m in matches),len(matches)),
        category_confusion=[dict(gold=a,predicted=b,count=n) for (a,b),n in sorted(cat_conf.items())],
        severity_confusion=[dict(gold=a,predicted=b,count=n) for (a,b),n in sorted(sev_conf.items(),key=lambda x:str(x[0]))],
        evidence=summarize(evidence,rejections),
        evidence_error_breakdown=dict(Counter(r for e in evidence for r in e["reasons"])),
        reliability=dict(completed=sum(o.status == "completed" for o in outcomes),
            partial=sum(o.status == "partial" for o in outcomes),failed=len(failures),
            failure_rate=ratio(len(failures),len(outcomes)),
            error_breakdown=dict(Counter(o.error_category or "unknown" for o in failures)),
            rejected_obligations=sum(o.rejected_obligation_count for o in outcomes)),
        average_processing_seconds=mean(latency) if latency else None,
        latency_available_analyses=len(latency),
        total_tokens=sum(o.total_tokens for o in outcomes) if outcomes and all(o.total_tokens is not None for o in outcomes) else None,
        proposed_finding_count=sum(o.proposed_finding_count for o in outcomes) if outcomes and all(o.proposed_finding_count is not None for o in outcomes) else None,
        retained_finding_count=sum(len(o.predictions) for o in outcomes),
        proposed_obligation_count=sum(o.proposed_obligation_count for o in outcomes) if outcomes and all(o.proposed_obligation_count is not None for o in outcomes) else None,
        retained_obligation_count=sum(o.retained_obligation_count for o in outcomes) if outcomes and all(o.retained_obligation_count is not None for o in outcomes) else None,
        rejection_reason_counts=dict(sum((Counter(o.rejection_reason_counts) for o in outcomes),Counter())),
        input_tokens=sum(o.input_tokens for o in outcomes) if tokens_known else None,
        output_tokens=sum(o.output_tokens for o in outcomes) if tokens_known else None,
        estimated_cost_usd=sum(o.estimated_cost_usd for o in outcomes) if costs_known else None,
        unmatched_predictions=[dict(contract_id=d["contract_id"],prediction_id=p)
            for d in details for p in d["risk"]["unmatched_predictions"]],
        missed_gold_annotations=[dict(contract_id=d["contract_id"],finding_id=g)
            for d in details for g in d["risk"]["missed_gold"]],
        ambiguous_predictions_excluded=sum(len(d["risk"]["ambiguous_predictions_excluded"]) for d in details),
        cases=details)
