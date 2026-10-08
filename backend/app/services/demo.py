"""Serve only the explicit precomputed synthetic snapshot; no AI service calls."""
from pathlib import Path

from app.models.contracts import AnalysisDraft, DemoArtifact, ObligationDraft, RiskDraft
from app.services.evidence import verify_analysis

DEMO_PATH = Path(__file__).resolve().parents[1] / "resources" / "demo_analysis.json"


def load_demo() -> DemoArtifact:
    artifact = DemoArtifact.model_validate_json(DEMO_PATH.read_text(encoding="utf-8"))
    result = artifact.analysis
    if result.output_origin != "synthetic_demo" or result.gemini_attempts != 0 or result.gemini_model != "not_used":
        raise ValueError("Demo snapshot must not claim live Gemini generation.")
    if result.contract_id != artifact.contract.contract_id or result.playbook_id != artifact.playbook.playbook_id or result.playbook_version != artifact.playbook.version:
        raise ValueError("Demo source IDs do not match.")
    draft = AnalysisDraft(
        findings=[RiskDraft.model_validate({key: value for key, value in item.model_dump().items() if key in RiskDraft.model_fields}) for item in result.findings],
        obligations=[ObligationDraft.model_validate({key: value for key, value in item.model_dump().items() if key in ObligationDraft.model_fields}) for item in result.obligations],
    )
    findings, obligations, rejected = verify_analysis(draft, artifact.contract, artifact.playbook)
    if rejected or [item.model_dump() for item in findings] != [item.model_dump() for item in result.findings] or [item.model_dump() for item in obligations] != [item.model_dump() for item in result.obligations]:
        raise ValueError("Demo snapshot failed independent evidence verification.")
    return artifact
