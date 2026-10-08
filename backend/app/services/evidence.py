"""Backend-owned provenance checks; quotations do not validate legal interpretations."""
import re

from app.models.contracts import (
    AnalysisDraft, Contract, ModelInterpretation, Playbook, RejectedRecord, SourceFacts,
    VerifiedFinding, VerifiedObligation,
)
from app.services.analysis_observability import emit, timed
from app.services.reasoning_boundaries import deadline_type, explicit_reference


class EvidenceError(RuntimeError):
    def __init__(self, message, rejections=None):
        super().__init__(message)
        self.rejections = rejections or []


def original_quote_slice(quote: str | None, clause_text: str) -> str | None:
    """Only whitespace may differ; return literal source text, never a paraphrase.

    No case folding, punctuation/Unicode substitutions, dehyphenation, token
    deletion, cross-clause search or fuzzy matching is permitted.
    """
    if not quote or not quote.strip():
        return None
    if quote in clause_text:
        return quote
    tokens = re.findall(r"\S+", quote)
    pattern = r"\s+".join(re.escape(token) for token in tokens)
    match = re.search(pattern, clause_text)
    return match.group(0) if match else None


@timed("evidence_verification")
def verify_analysis(draft: AnalysisDraft, contract: Contract, playbook: Playbook):
    emit("proposed", draft=draft, contract=contract)
    clauses = {clause.clause_id: clause for clause in contract.clauses}
    pages = {page.page_number: page.text for page in contract.pages}
    policies = {rule.policy_id: rule for rule in playbook.rules}
    findings, obligations, rejections = [], [], []
    resolved_quotes = {}

    def source_error(item):
        clause = clauses.get(item.clause_id)
        if clause is None:
            return "unknown_clause_id"
        if item.page_number != clause.page_number:
            return "wrong_page_number"
        original = pages.get(item.page_number, "")
        if original[clause.start_offset:clause.end_offset] != clause.text:
            return "source_offset_mismatch"
        quote = original_quote_slice(item.evidence_quote, clause.text)
        if quote is None or quote not in original:
            return "quote_not_in_original_clause"
        resolved_quotes[id(item)] = quote
        return None

    for index, item in enumerate(draft.findings):
        missing = item.finding_status == "missing"
        if missing:
            reason = "missing_finding_has_contract_evidence" if any(value is not None for value in (item.clause_id, item.page_number, item.evidence_quote)) else None
            if reason is None and (item.referenced_parties or item.referenced_dates):
                reason = "missing_finding_has_source_references"
        else:
            reason = source_error(item)
        if reason is None and not missing:
            item = item.model_copy(update={"evidence_quote": resolved_quotes[id(item)]})
        policy = policies.get(item.policy_id)
        if reason is None and policy is None:
            reason = "unknown_policy_id"
        if reason is None and policy.category != item.clause_category:
            reason = "policy_category_mismatch"
        if reason is None and item.policy_requirement is not None and item.policy_requirement != policy.rule:
            reason = "policy_requirement_mismatch"
        if reason is None and not missing:
            for references, field in [(item.referenced_parties, "party"), (item.referenced_dates, "date")]:
                if any(not explicit_reference(value, item.evidence_quote) for value in references):
                    reason = f"referenced_{field}_not_in_evidence"
                    break
        if reason:
            rejections.append(RejectedRecord(record_type="finding", index=index, reason=reason))
            continue
        review = missing or item.finding_status == "ambiguous" or not item.policy_match_reliable or bool(item.unsupported_assumptions)
        data = item.model_dump()
        # Resolve actual requirement from trusted playbook; never promote model text.
        data["policy_requirement"] = policy.rule
        interpretation = ModelInterpretation(
            finding_status=item.finding_status, explanation=item.explanation,
            recommended_action=item.recommended_action, uncertainty=item.uncertainty,
            unsupported_assumptions=item.unsupported_assumptions,
        )
        if missing:
            interpretation.uncertainty = "Potential omission only. Complete-document review is required; absence is not confirmed."
        elif review and not interpretation.uncertainty:
            interpretation.uncertainty = "Ambiguity, assumptions, or unreliable policy matching require human review."
        data["uncertainty"] = interpretation.uncertainty
        facts = None if missing else SourceFacts(
            clause_id=item.clause_id, page_number=item.page_number, evidence_quote=item.evidence_quote,
            referenced_parties=item.referenced_parties, referenced_dates=item.referenced_dates,
        )
        findings.append(VerifiedFinding(
            **data, applicable_policy_rule=policy, evidence_verified=not missing,
            evidence_status="needs_review" if review else "verified",
            source_facts=facts, model_interpretation=interpretation,
            potential_omission=missing, complete_document_review_required=missing,
        ))
    for index, item in enumerate(draft.obligations):
        reason = source_error(item)
        if reason is None:
            item = item.model_copy(update={"evidence_quote": resolved_quotes[id(item)]})
        for value, field in [(item.responsible_party, "party"), (item.deadline, "deadline")]:
            if reason is None and value is not None and not explicit_reference(value, item.evidence_quote):
                reason = f"{field}_not_explicit_in_evidence"
        if reason:
            rejections.append(RejectedRecord(record_type="obligation", index=index, reason=reason))
        else:
            kind = deadline_type(item.deadline)
            obligations.append(VerifiedObligation(
                **item.model_dump(), deadline_type=kind,
                evidence_status="needs_review" if kind == "ambiguous" else "verified",
            ))
    emit("verified", findings=findings, obligations=obligations, rejections=rejections)
    if rejections and not findings and not obligations:
        raise EvidenceError("The AI could not verify its generated evidence. No supported analysis was saved. Your uploaded contract is preserved; retry manually or use the separately labeled demo.", rejections)
    return findings, obligations, rejections
