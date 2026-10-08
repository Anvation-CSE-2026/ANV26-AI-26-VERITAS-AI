"""Backend-owned provenance checks; quotations do not validate legal interpretations."""
from app.models.contracts import (
    AnalysisDraft, Contract, ModelInterpretation, Playbook, RejectedRecord, SourceFacts,
    VerifiedFinding, VerifiedObligation,
)
from app.services.reasoning_boundaries import deadline_type, explicit_reference


class EvidenceError(RuntimeError):
    def __init__(self, message, rejections=None):
        super().__init__(message)
        self.rejections = rejections or []


def verify_analysis(draft: AnalysisDraft, contract: Contract, playbook: Playbook):
    clauses = {clause.clause_id: clause for clause in contract.clauses}
    pages = {page.page_number: page.text for page in contract.pages}
    policies = {rule.policy_id: rule for rule in playbook.rules}
    findings, obligations, rejections = [], [], []

    def source_error(item):
        clause = clauses.get(item.clause_id)
        if clause is None:
            return "unknown_clause_id"
        if item.page_number != clause.page_number:
            return "wrong_page_number"
        original = pages.get(item.page_number, "")
        if original[clause.start_offset:clause.end_offset] != clause.text:
            return "source_offset_mismatch"
        if not item.evidence_quote or not item.evidence_quote.strip() or item.evidence_quote not in clause.text or item.evidence_quote not in original:
            return "quote_not_in_original_clause"
        return None

    for index, item in enumerate(draft.findings):
        missing = item.finding_status == "missing"
        if missing:
            reason = "missing_finding_has_contract_evidence" if any(value is not None for value in (item.clause_id, item.page_number, item.evidence_quote)) else None
            if reason is None and (item.referenced_parties or item.referenced_dates):
                reason = "missing_finding_has_source_references"
        else:
            reason = source_error(item)
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
    if rejections and not findings and not obligations:
        raise EvidenceError("All generated records failed evidence verification; no analysis was saved.", rejections)
    return findings, obligations, rejections
