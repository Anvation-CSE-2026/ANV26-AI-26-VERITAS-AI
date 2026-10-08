"""Literal quotation metrics, independent of legal interpretation."""
import re
from .schema import Prediction
from app.models.contracts import Contract

def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

def ratio(n: int, d: int) -> float | None:
    return n / d if d else None

def check_evidence(pred: Prediction, contract: Contract, policy_ids: set[str]) -> dict:
    pages = {p.page_number: p.text for p in contract.pages}
    clauses = {c.clause_id: c for c in contract.clauses}
    reasons = []
    if pred.policy_id not in policy_ids:
        reasons.append("unknown_or_missing_policy")
    if pred.finding_status == "missing":
        if pred.evidence_quote is not None or pred.page_number is not None or pred.clause_id is not None:
            reasons.append("fabricated_evidence_for_omission")
        return dict(prediction_id=pred.prediction_id, quote_eligible=False, exact_match=None,
                    normalized_match=None, correct_page=None, normalized_correct_page=None,
                    supported=not reasons, reasons=reasons, omission_not_confirmed=True)
    quote = pred.evidence_quote or ""
    exact = bool(quote.strip()) and any(quote in text for text in pages.values())
    norm = normalize(quote)
    normalized = bool(norm) and any(norm in normalize(text) for text in pages.values())
    page = pages.get(pred.page_number)
    correct = bool(quote.strip()) and page is not None and quote in page
    normalized_page = bool(norm) and page is not None and norm in normalize(page)
    if not quote.strip():
        reasons.append("empty_or_missing_quote")
    elif not exact:
        reasons.append("whitespace_only_mismatch" if normalized else "fabricated_quote")
    if pred.page_number is None:
        reasons.append("missing_page")
    elif page is None:
        reasons.append("nonexistent_page")
    elif not correct:
        reasons.append("wrong_page" if exact else "quote_not_exact_on_cited_page")
    clause = clauses.get(pred.clause_id)
    if pred.clause_id is None:
        reasons.append("missing_clause")
    elif clause is None:
        reasons.append("nonexistent_clause")
    elif clause.page_number != pred.page_number:
        reasons.append("clause_page_mismatch")
    elif quote.strip() and quote not in clause.text:
        reasons.append("quote_not_in_cited_clause")
    return dict(prediction_id=pred.prediction_id, quote_eligible=True, exact_match=exact,
                normalized_match=normalized, correct_page=correct,
                normalized_correct_page=normalized_page, supported=not reasons,
                reasons=reasons, omission_not_confirmed=False)

def summarize(records: list[dict], rejected_finding_count: int = 0) -> dict:
    quoted = [r for r in records if r["quote_eligible"]]
    unsupported = sum(not r["supported"] for r in records) + rejected_finding_count
    total = len(records) + rejected_finding_count
    return dict(returned_findings=len(records), quote_eligible_findings=len(quoted),
                omission_candidates=sum(not r["quote_eligible"] for r in records),
                exact_quote_match_rate=ratio(sum(r["exact_match"] for r in quoted), len(quoted)),
                normalized_quote_match_rate=ratio(sum(r["normalized_match"] for r in quoted), len(quoted)),
                correct_page_citation_rate=ratio(sum(r["correct_page"] for r in quoted), len(quoted)),
                normalized_correct_page_rate=ratio(sum(r["normalized_correct_page"] for r in quoted), len(quoted)),
                unsupported_evidence_count=unsupported,
                rejected_finding_count=rejected_finding_count,
                evidence_verification_failure_rate=ratio(unsupported, total),
                unsupported_evidence_rate=ratio(unsupported, total),
                rejected_quotes_not_available=rejected_finding_count)
