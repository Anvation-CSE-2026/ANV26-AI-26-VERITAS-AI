"""Hosted text embeddings via the official SDK; no reasoning calls or fallbacks."""
import math
from contextlib import contextmanager
from contextvars import ContextVar

import httpx
from google import genai
from google.genai import errors, types

from app.config import settings
from app.services.analysis_observability import timed
from app.services.ollama_embeddings import EmbeddingError

_client_scope = ContextVar("gemini_embedding_client", default=None)


class HostedEmbeddingError(EmbeddingError):
    def __init__(self, message: str, category: str, status_code: int = 502,
                 upstream_status: int | None = None):
        super().__init__(message)
        self.category = category
        self.status_code = status_code
        self.upstream_status = upstream_status

    def detail(self) -> dict:
        return {"state": "failed", "failed_stage": "policy_retrieval",
                "error_category": self.category, "message": str(self),
                "embedding_provider": "gemini",
                "embedding_model": settings.gemini_embedding_model,
                "upstream_http_status": self.upstream_status,
                "analysis_id": getattr(self, "analysis_id", None),
                "failure_recorded": getattr(self, "failure_recorded", False)}


@contextmanager
def embedding_client_scope():
    if not settings.gemini_api_key.strip():
        raise HostedEmbeddingError("Gemini embedding API key is not configured on the backend.",
                                   "embedding_configuration", 503)
    try:
        with genai.Client(
            api_key=settings.gemini_api_key, vertexai=False,
            http_options=types.HttpOptions(
                base_url="https://generativelanguage.googleapis.com",
                api_version="v1beta", timeout=int(settings.gemini_embedding_timeout_seconds * 1000),
                retry_options=types.HttpRetryOptions(attempts=1),
                client_args={"trust_env": False},
            ),
        ) as client:
            token = _client_scope.set(client)
            try:
                yield client
            finally:
                _client_scope.reset(token)
    except errors.APIError as exc:
        code = exc.code
        category = ("embedding_timeout" if code == 504 else "embedding_rate_limit" if code == 429 else
                    "embedding_authentication" if code in (401, 403) else
                    "embedding_model_unavailable" if code == 404 else "embedding_provider_error")
        status = 504 if code == 504 else 429 if code == 429 else 503 if code and code >= 500 else 502
        # Never include upstream messages, which can contain request text or credentials.
        raise HostedEmbeddingError("Gemini embedding service rejected the request.", category, status, code) from None
    except httpx.TimeoutException:
        raise HostedEmbeddingError("Gemini embedding request timed out.", "embedding_timeout", 504) from None
    except httpx.RequestError:
        raise HostedEmbeddingError("Gemini embedding service is unavailable.", "embedding_connection", 503) from None
    except ValueError:
        raise HostedEmbeddingError("Gemini returned an invalid embedding response.", "embedding_invalid_response") from None


@timed("embedding_request")
def embed_text(text: str) -> list[float]:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Text must be a nonblank string.")
    client = _client_scope.get()
    if client is None:
        with embedding_client_scope():
            return _embed(text)
    return _embed(text)


def _embed(text: str) -> list[float]:
    response = _client_scope.get().models.embed_content(
        model=settings.gemini_embedding_model, contents=text,
        config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY",
                                      output_dimensionality=settings.gemini_embedding_dimensions),
    )
    embeddings = getattr(response, "embeddings", None)
    vector = getattr(embeddings[0], "values", None) if embeddings and len(embeddings) == 1 else None
    if (not isinstance(vector, list) or len(vector) != settings.gemini_embedding_dimensions
            or any(isinstance(value, bool) or not isinstance(value, (int, float))
                   or not math.isfinite(value) for value in vector)
            or not any(vector)):
        raise HostedEmbeddingError("Gemini returned an invalid embedding vector.", "embedding_invalid_response")
    return [float(value) for value in vector]
