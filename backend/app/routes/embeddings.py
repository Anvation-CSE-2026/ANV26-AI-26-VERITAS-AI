from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator

from app.config import settings
from app.services.ollama_embeddings import (
    EmbeddingError, EmbeddingTimeout, EmbeddingUnavailable, embed_text,
)

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


@router.post("/test", response_model=EmbeddingTestResponse)
def test_embedding(request: EmbeddingTestRequest) -> EmbeddingTestResponse:
    try:
        vector = embed_text(request.text)
    except EmbeddingTimeout as exc:
        raise HTTPException(status_code=504, detail=str(exc)) from exc
    except EmbeddingUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except EmbeddingError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return EmbeddingTestResponse(
        success=True, model=settings.ollama_embedding_model, dimensions=len(vector),
    )
