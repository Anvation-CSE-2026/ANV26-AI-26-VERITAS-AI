from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.config import settings
from app.models.auth import UserRecord
from app.models.contracts import Analysis, AnalysisFailure, AnalyzeRequest, DemoArtifact, Contract
from app.services.billing import (
    enforce_analysis_quota,
    get_user_subscription,
    record_successful_analysis_usage,
)
from app.services.contract_analysis import analyze_contract
from app.services.demo import load_demo
from app.services.evidence import EvidenceError
from app.services.gemini_analysis import GeminiError
from app.services.ollama_embeddings import EmbeddingError, EmbeddingTimeout, EmbeddingUnavailable
from app.services.gemini_embeddings import HostedEmbeddingError
from app.services.pdf_extraction import ContractLimitError, PDFError, extract_contract
from app.services.security import get_current_user
from app.services.storage import (
    STORAGE_ERRORS,
    get_analysis,
    get_contract,
    get_failure,
    get_user_analyses_history,
    save_contract,
)

router = APIRouter(tags=["Contracts"])


def storage_failure() -> HTTPException:
    return HTTPException(status_code=503, detail="Local contract storage is unavailable.")


@router.post("/api/contracts/upload", response_model=Contract, status_code=201)
def upload_contract(
    file: UploadFile = File(...),
    current_user: UserRecord = Depends(get_current_user),
) -> Contract:
    """Uploads a contract PDF, extracts clauses and offsets, and associates it with the authenticated account."""
    filename = Path((file.filename or "contract.pdf").replace("\\", "/")).name
    filename = "".join(char for char in filename if char.isprintable())[:200]
    try:
        if not filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=415, detail="Only PDF uploads are supported.")
        pdf_bytes = file.file.read(settings.max_upload_bytes + 1)
        contract = extract_contract(pdf_bytes, filename)
        save_contract(contract, pdf_bytes, user_id=current_user.id)
        return contract
    except ContractLimitError as exc:
        raise HTTPException(status_code=413, detail=str(exc)) from None
    except PDFError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from None
    except STORAGE_ERRORS:
        raise storage_failure() from None
    finally:
        file.file.close()


@router.post("/api/analyze", response_model=Analysis)
def analyze(
    request: AnalyzeRequest,
    current_user: UserRecord = Depends(get_current_user),
) -> Analysis:
    """Performs evidence-verified contract analysis, enforcing server-side subscription quotas and data isolation."""
    # 1. Fetch contract with account-level isolation
    contract = get_contract(request.contract_id, user_id=current_user.id)
    if contract is None:
        raise HTTPException(status_code=404, detail="Contract not found.")

    # 2. Server-side quota check before triggering AI pipeline
    sub, billing_period = enforce_analysis_quota(current_user.id)

    # 3. AI pipeline execution
    try:
        if not settings.gemini_api_key.strip():
            raise GeminiError("Gemini API key is not configured on the backend.", 503)
        result = analyze_contract(contract, user_id=current_user.id)
        # 4. Record consumed quota ONLY on successful analysis
        record_successful_analysis_usage(current_user.id, result.analysis_id, billing_period)
        return result
    except GeminiError as exc:
        headers = {"Retry-After": exc.retry_after} if exc.retry_after else None
        raise HTTPException(
            status_code=exc.status_code,
            detail={
                "state": "failed",
                "message": str(exc),
                "synthetic_demo_command": "python tests/show_synthetic_demo.py",
                "analysis_id": getattr(exc, "analysis_id", None),
                "failure_recorded": getattr(exc, "failure_recorded", False),
                "failed_stage": exc.stage,
                "error_category": exc.category,
                "gemini_attempts": exc.attempts,
                "upstream_http_status": exc.upstream_status,
            },
            headers=headers,
        ) from None
    except HostedEmbeddingError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail()) from None
    except EmbeddingTimeout:
        raise HTTPException(status_code=504, detail="Ollama embedding request timed out.") from None
    except EmbeddingUnavailable:
        raise HTTPException(status_code=503, detail="Ollama embedding service is unavailable.") from None
    except (EmbeddingError, ValueError):
        raise HTTPException(status_code=502, detail="Policy retrieval failed; no analysis was saved.") from None
    except EvidenceError as exc:
        raise HTTPException(
            status_code=502,
            detail={
                "state": "failed",
                "message": str(exc),
                "verification_rejections": [record.model_dump() for record in exc.rejections],
                "analysis_id": getattr(exc, "analysis_id", None),
                "failure_recorded": getattr(exc, "failure_recorded", False),
                "failed_stage": "evidence_verification",
                "error_category": "unsupported_evidence",
            },
        ) from None
    except STORAGE_ERRORS:
        raise storage_failure() from None


@router.get("/api/analysis/{analysis_id}", response_model=Analysis | AnalysisFailure)
def read_analysis(
    analysis_id: str,
    current_user: UserRecord = Depends(get_current_user),
) -> Analysis | AnalysisFailure:
    """Retrieves verified analysis or failure report with strict account scoping and plan history retention limits."""
    try:
        result = get_analysis(analysis_id, user_id=current_user.id) or get_failure(analysis_id, user_id=current_user.id)
    except STORAGE_ERRORS:
        raise storage_failure() from None
    if result is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")

    # Check plan history limit if user has an active subscription/trial
    sub = get_user_subscription(current_user.id)
    if sub and isinstance(result, Analysis):
        history_allowed = get_user_analyses_history(current_user.id, limit=sub.history_limit)
        allowed_ids = {a.analysis_id for a in history_allowed}
        if result.analysis_id not in allowed_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Analysis history retention limit ({sub.history_limit}) exceeded for your {sub.plan} plan.",
            )

    return result


@router.get("/api/demo/analysis", response_model=DemoArtifact, tags=["Demo"])
def read_demo() -> DemoArtifact:
    """Public read-only demonstration analysis fixture. Does not require authentication."""
    try:
        return load_demo()
    except (ValueError, OSError, EvidenceError):
        raise HTTPException(status_code=503, detail="Precomputed synthetic demo is unavailable or failed verification.") from None
