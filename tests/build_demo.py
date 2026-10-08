"""Explicit developer command to precompute hand-authored synthetic demo data."""
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "backend"), str(Path(__file__).parent)]
from app.models.contracts import Analysis, AnalysisDraft, DemoArtifact, ObligationDraft, RiskDraft
from app.services.demo import DEMO_PATH
from app.services.evidence import verify_analysis
from app.services.pdf_extraction import extract_contract
from app.services.playbook import load_playbook
from sample_pdf import sample_pdf


def build():
    contract = extract_contract(sample_pdf(), "SYNTHETIC-DEMO.pdf")
    contract.contract_id = "synthetic-demo-contract-v1"
    playbook = load_playbook()
    explanations = [
        "The USD 100 cap expressly includes data and confidentiality breaches, while the sample policy requires exclusions and a fee-based minimum.",
        "The Company indemnifies Supplier even for Supplier negligence, while Supplier expressly has no duty to defend IP claims.",
        "The 90-day notice and remaining-fees penalty conflict with the sample convenience-termination requirements.",
        "The one-year confidentiality survival period is shorter than the sample three-year requirement.",
        "The ten-day payment period, three-percent monthly interest and ban on withholding disputes conflict with sample payment rules.",
        "Seven-day breach notification and sixty-day deletion exceed the sample deadlines.",
        "Supplier owns bespoke deliverables and grants only a revocable term license, contrary to sample ownership or perpetual-license rules.",
    ]
    findings = []
    for number, (rule, explanation) in enumerate(zip(playbook.rules, explanations), 1):
        clause = next(item for item in contract.clauses if item.text.startswith(f"{number}. "))
        findings.append(RiskDraft(
            finding_status="risky", risk_level="high" if number in (1, 2, 6, 7) else "medium",
            clause_category=rule.category, explanation="Hand-authored demo interpretation: " + explanation,
            evidence_quote=clause.text, page_number=clause.page_number, clause_id=clause.clause_id,
            policy_id=rule.policy_id, policy_requirement=rule.rule, recommended_action=rule.recommended_action,
        ))
    obligations = []
    for heading, party, deadline, description in [
        ("5. Payment", "The Company", "within 10 days after receipt", "Pay invoices."),
        ("6. Data Protection", "Supplier", "within 7 days", "Notify the Company of a personal data breach."),
        ("8. Reporting", "Supplier", "by the fifth day of each month", "Deliver the monthly service report."),
    ]:
        clause = next(item for item in contract.clauses if item.text.startswith(heading))
        # Use exact extracted spelling/line breaks, not retyped document text.
        quote = clause.text
        if deadline not in quote:
            raise ValueError("Synthetic deadline does not appear verbatim.")
        obligations.append(ObligationDraft(description=description, evidence_quote=quote, page_number=clause.page_number,
            clause_id=clause.clause_id, responsible_party=party, deadline=deadline))
    accepted, duties, rejected = verify_analysis(AnalysisDraft(findings=findings, obligations=obligations), contract, playbook)
    if rejected:
        raise ValueError("Hand-authored demo records did not pass verification.")
    analysis = Analysis(
        analysis_id="synthetic-demo-analysis-v1", contract_id=contract.contract_id, created_at=datetime.now(timezone.utc),
        status="completed", output_origin="synthetic_demo", gemini_model="not_used", embedding_model="not_used",
        playbook_id=playbook.playbook_id, playbook_version=playbook.version, findings=accepted, obligations=duties,
        semantic_matches=[], unassessed_policy_ids=[], verification_rejections=[],
        warnings=["SAMPLE ANALYSIS — DEMO DATA. Hand-authored, precomputed synthetic findings; not live Gemini output.",
                  "No AI generation or embedding retrieval is used by demo mode. Evidence verification proves provenance, not legal correctness."],
    )
    artifact = DemoArtifact(label="SAMPLE ANALYSIS — DEMO DATA", output_origin="synthetic_demo", live_ai_used=False,
        description="Hand-authored precomputed analysis of a synthetic contract against a synthetic company playbook; no live Gemini claims.",
        contract=contract, playbook=playbook, analysis=analysis)
    DEMO_PATH.write_text(artifact.model_dump_json(indent=2) + "\n", encoding="utf-8")
    print(f"Precomputed demo: {len(accepted)} verified findings, {len(duties)} obligations.")


if __name__ == "__main__":
    build()
