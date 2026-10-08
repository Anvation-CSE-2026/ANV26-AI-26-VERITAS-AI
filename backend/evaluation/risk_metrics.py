"""Deterministic maximum-cardinality one-to-one source-target matching."""
from collections import Counter
from .schema import Annotation, Prediction, CATEGORIES
from .evidence_metrics import normalize, ratio

ACTIVE = {"risky", "conflicting", "missing"}

def metrics(tp: int, fp: int, fn: int) -> dict:
    return dict(tp=tp, fp=fp, fn=fn, precision=ratio(tp, tp + fp),
                recall=ratio(tp, tp + fn), f1=ratio(2 * tp, 2 * tp + fp + fn))

def candidate(p: Prediction, g: Annotation) -> bool:
    if g.annotation_state == "missing":
        return p.finding_status == "missing" and p.policy_id == g.policy_id
    if p.finding_status == "missing":
        return False
    # Identity establishes the interpretation target, not quotation validity.
    # Category and severity are deliberately NOT required to match.
    if any(p.clause_id == s.clause_id for s in g.evidence_spans):
        return True
    q = normalize(p.evidence_quote or "")
    return bool(q) and any(p.page_number == s.page_number and
                          (q in normalize(s.quote) or normalize(s.quote) in q)
                          for s in g.evidence_spans)

def one_to_one(predictions: list[Prediction], gold: list[Annotation]) -> list[tuple[int, int]]:
    # Stable augmenting paths ensure maximal cardinality; prevents greedy FN artifacts.
    # Exact quote candidates first, then gold ID; ties never use predicted categories.
    edges = []
    for p in predictions:
        hits = [j for j, g in enumerate(gold) if candidate(p, g)]
        hits.sort(key=lambda j: (
            not any(p.evidence_quote == s.quote for s in gold[j].evidence_spans),
            gold[j].finding_id))
        edges.append(hits)
    owner = {}
    def assign(i, seen):
        for j in edges[i]:
            if j in seen:
                continue
            seen.add(j)
            if j not in owner or assign(owner[j], seen):
                owner[j] = i
                return True
        return False
    for i in range(len(predictions)):
        assign(i, set())
    return sorted((i, j) for j, i in owner.items())

def score_case(predictions: list[Prediction], gold: list[Annotation]) -> dict:
    positive = [g for g in gold if g.annotation_state in ("risk", "missing")]
    active = [p for p in predictions if p.finding_status in ACTIVE]
    pairs = one_to_one(active, positive)
    used_p, used_g = {i for i, _ in pairs}, {j for _, j in pairs}
    ambiguous = [g for g in gold if g.annotation_state == "ambiguous"]
    remaining = [i for i in range(len(active)) if i not in used_p]
    # Only one prediction may be excluded per ambiguous target. Duplicate ambiguity
    # predictions remain FPs, preventing unlimited ignored predictions.
    apairs = one_to_one([active[i] for i in remaining], ambiguous)
    excluded = {remaining[i] for i, _ in apairs}
    unmatched = [i for i in remaining if i not in excluded]
    per_category = {c: [0, 0, 0] for c in CATEGORIES}
    confusion, severity = Counter(), Counter()
    matches = []
    for i, j in pairs:
        p, g = active[i], positive[j]
        confusion[(g.risk_category, p.risk_category)] += 1
        severity[(g.expected_severity, p.severity)] += 1
        if g.risk_category == p.risk_category:
            per_category[g.risk_category][0] += 1
        else:
            per_category[g.risk_category][2] += 1
            per_category[p.risk_category][1] += 1
        matches.append(dict(prediction_id=p.prediction_id, finding_id=g.finding_id,
                            category_correct=p.risk_category == g.risk_category,
                            severity_correct=p.severity == g.expected_severity,
                            omission=g.annotation_state == "missing"))
    for i in unmatched:
        per_category[active[i].risk_category][1] += 1
    missed = [g for j, g in enumerate(positive) if j not in used_g]
    for g in missed:
        per_category[g.risk_category][2] += 1
    return dict(detection=metrics(len(pairs), len(unmatched), len(missed)),
                per_category={c: metrics(*counts) for c, counts in per_category.items()},
                matches=matches, unmatched_predictions=[active[i].prediction_id for i in unmatched],
                missed_gold=[g.finding_id for g in missed],
                ambiguous_predictions_excluded=[active[i].prediction_id for i in sorted(excluded)],
                ambiguous_gold_count=len(ambiguous),
                non_risk_gold_count=sum(g.annotation_state == "non_risk" for g in gold),
                non_risk_false_positives=[active[i].prediction_id for i in unmatched
                    if any(candidate(active[i], g) for g in gold if g.annotation_state == "non_risk")],
                inactive_prediction_count=len(predictions) - len(active),
                category_confusion=[dict(gold=a, predicted=b, count=n) for (a,b),n in sorted(confusion.items())],
                severity_confusion=[dict(gold=a, predicted=b, count=n) for (a,b),n in
                                   sorted(severity.items(), key=lambda x: str(x[0]))])
