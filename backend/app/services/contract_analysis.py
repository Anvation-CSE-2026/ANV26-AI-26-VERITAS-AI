import time

from datetime import datetime, timezone
from uuid import uuid4

from app.config import settings
from app.services.analysis_observability import emit, timed
from app.models.contracts import Analysis, AnalysisFailure, Contract
from app.services.evidence import verify_analysis
from app.services.gemini_analysis import generate_analysis
from app.services.playbook import load_playbook
from app.services.policy_matching import match_policies
from app.services.storage import STORAGE_ERRORS, save_analysis, save_failure
from app.services.evidence import EvidenceError
from app.services.gemini_analysis import GeminiError
from app.services.ollama_embeddings import EmbeddingError, EmbeddingTimeout, EmbeddingUnavailable
from app.services.embeddings import embedding_model
from app.services.gemini_embeddings import HostedEmbeddingError
from app.services.reasoning_boundaries import detect_document_instructions


def _run_analysis(contract: Contract, analysis_id: str, started: float, progress: dict, user_id: str | None = None) -> Analysis:
    progress["stage"] = "policy_retrieval"
    playbook = load_playbook()
    alerts = detect_document_instructions(contract, playbook)
    matches = match_policies(contract, playbook)
    progress["stage"] = "gemini_reasoning"
    draft = generate_analysis(contract, playbook, matches)
    progress["attempts"] = draft._gemini_attempts
    progress["stage"] = "evidence_verification"
    findings, obligations, rejections = verify_analysis(draft, contract, playbook)
    addressed = {finding.policy_id for finding in findings}
    warnings = list(contract.warnings)
    warnings.append("Evidence verification confirms quoted text and IDs, not the legal correctness or completeness of model interpretations.")
    warnings.append("Unassessed policies are coverage gaps, not proof that clauses are missing or compliant.")
    review_needed = bool(alerts) or any(item.evidence_status == "needs_review" for item in [*findings, *obligations])
    if alerts:
        warnings.append("Possible document instructions were detected and treated as untrusted data. Human review is required; no clean-contract verdict is given.")
    if rejections:
        warnings.append("Some generated records failed verification and were excluded. This analysis is incomplete.")
    result = Analysis(
        analysis_id=analysis_id, contract_id=contract.contract_id,
        created_at=datetime.now(timezone.utc), status="partial" if rejections or contract.warnings or review_needed else "completed",
        gemini_model=settings.gemini_model, embedding_model=embedding_model(),
        playbook_id=playbook.playbook_id, playbook_version=playbook.version,
        gemini_attempts=draft._gemini_attempts, gemini_response_model=draft._gemini_model_version,
        processing_seconds=round(time.monotonic() - started, 4),
        findings=findings, obligations=obligations, semantic_matches=matches,
        document_instruction_alerts=alerts,
        unassessed_policy_ids=[rule.policy_id for rule in playbook.rules if rule.policy_id not in addressed],
        verification_rejections=rejections, warnings=warnings,
    )
    progress["stage"] = "postgresql_persistence" if settings.database_url.strip() else "sqlite_persistence"
    save_analysis(result, user_id=user_id)
    emit("analysis_result", result=result)
    return result


@timed("contract_analysis")
def analyze_contract(contract: Contract, user_id: str | None = None) -> Analysis:
    analysis_id, started = str(uuid4()), time.monotonic()
    progress = {"stage": "policy_retrieval", "attempts": 0}
    try:
        return _run_analysis(contract, analysis_id, started, progress, user_id=user_id)
    except (GeminiError, EmbeddingError, EvidenceError, ValueError, *STORAGE_ERRORS) as exc:
        if isinstance(exc, GeminiError):
            status, category, message = exc.status_code, exc.category, str(exc)
            progress["stage"], progress["attempts"] = exc.stage, exc.attempts
        elif isinstance(exc, EvidenceError):
            status, category, message = 502, "unsupported_evidence", str(exc)
        elif isinstance(exc, HostedEmbeddingError):
            status, category, message = exc.status_code, exc.category, str(exc)
        elif isinstance(exc, EmbeddingTimeout):
            status, category, message = 504, "embedding_timeout", "Ollama embedding request timed out."
        elif isinstance(exc, EmbeddingUnavailable):
            status, category, message = 503, "embedding_connection", "Ollama embedding service is unavailable."
        else:
            status = 503 if isinstance(exc, STORAGE_ERRORS) else 502
            category, message = "storage" if status == 503 else "policy_retrieval", "Analysis failed; no successful result was saved."
        failure = AnalysisFailure(
            analysis_id=analysis_id, contract_id=contract.contract_id, created_at=datetime.now(timezone.utc),
            failed_stage=progress["stage"], error_category=category, message=message, http_status=status,
            upstream_http_status=getattr(exc, "upstream_status", None), gemini_model=settings.gemini_model,
            gemini_attempts=progress["attempts"], retries_occurred=progress["attempts"] > 1,
            processing_seconds=round(time.monotonic() - started, 4), verification_rejections=getattr(exc, "rejections", []),
        )
        try:
            save_failure(failure, user_id=user_id)
            exc.analysis_id, exc.failure_recorded = analysis_id, True
        except STORAGE_ERRORS:
            exc.analysis_id, exc.failure_recorded = None, False
        emit("analysis_failure", stage=progress["stage"], category=category, analysis_id=getattr(exc, "analysis_id", None))
        raise
