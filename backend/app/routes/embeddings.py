from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, field_validator

from app.config import settings
from app.services.ollama_embeddings import (
    EmbeddingError, EmbeddingTimeout, EmbeddingUnavailable,
)
from app.services.embeddings import embed_text, embedding_model
from app.services.gemini_embeddings import HostedEmbeddingError
from app.services.security import bearer_scheme, get_current_user

router = APIRouter(prefix="/api/embeddings", tags=["Embeddings"])


class EmbeddingTestRequest(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def nonblank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Text must not be blank.")
        return value


class EmbeddingTestResponse(BaseModel):
    success: bool
    model: str
    dimensions: int


def require_embedding_access(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)):
    if settings.embedding_provider == "gemini" or settings.environment.lower() != "development":
        # Hosted diagnostics must never enable anonymous paid provider calls, even with the legacy toggle.
        if credentials is None or not credentials.credentials:
            raise HTTPException(status_code=401, detail="Authentication required.",
                                headers={"WWW-Authenticate": "Bearer"})
        get_current_user(credentials)


@router.post("/test", response_model=EmbeddingTestResponse, dependencies=[Depends(require_embedding_access)])
def test_embedding(request: EmbeddingTestRequest) -> EmbeddingTestResponse:
    try:
        vector = embed_text(request.text)
    except HostedEmbeddingError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail()) from None
    except EmbeddingTimeout as exc:
        raise HTTPException(status_code=504, detail=str(exc)) from exc
    except EmbeddingUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except EmbeddingError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return EmbeddingTestResponse(
        success=True, model=embedding_model(), dimensions=len(vector),
    )
