"""Local embeddings for retrieval and clause/policy comparison; no chat calls."""
import math
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
from threading import get_ident

import httpx

from app.config import settings
from app.services.analysis_observability import timed


class EmbeddingError(RuntimeError):
    """Ollama failed or returned an invalid embedding."""


class EmbeddingUnavailable(EmbeddingError):
    pass


class EmbeddingTimeout(EmbeddingError):
    pass


_client_scope = ContextVar("ollama_retrieval_client", default=None)


def _client_key():
    return (settings.ollama_base_url, settings.ollama_embedding_model,
            settings.ollama_connect_timeout, settings.ollama_read_timeout, get_ident())


def _new_client():
    return httpx.Client(timeout=httpx.Timeout(settings.ollama_read_timeout,
                        connect=settings.ollama_connect_timeout), trust_env=False)


@contextmanager
def embedding_client_scope():
    """A new synchronous client for one retrieval; never borrow a parent scope."""
    try:
        with _new_client() as client:
            token = _client_scope.set((_client_key(), client))
            try:
                yield
            finally:
                _client_scope.reset(token)
    except httpx.TimeoutException as exc:
        raise EmbeddingTimeout("Ollama embedding request timed out.") from exc
    except httpx.RequestError as exc:
        raise EmbeddingUnavailable("Unable to connect to the Ollama embedding service.") from exc


def with_embedding_client(function):
    @wraps(function)
    def wrapped(*args, **kwargs):
        with embedding_client_scope():
            return function(*args, **kwargs)
    return wrapped


@contextmanager
def _request_client():
    scoped = _client_scope.get()
    if scoped is not None and scoped[0] == _client_key():
        client = scoped[1]
        # Fresh clients previously never sent cookies from another embedding response.
        client.cookies.clear()
        yield client
    else:
        with _new_client() as client:
            yield client


@timed("embedding_request")
def embed_text(text: str) -> list[float]:
    """Embed one nonblank text using Ollama's /api/embed endpoint."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Text must be a nonblank string.")
    try:
        with _request_client() as client:
            response = client.post(
                settings.ollama_base_url.rstrip("/") + "/api/embed",
                json={"model": settings.ollama_embedding_model, "input": text, "truncate": False},
            )
            response.raise_for_status()
    except httpx.TimeoutException as exc:
        raise EmbeddingTimeout("Ollama embedding request timed out.") from exc
    except httpx.HTTPStatusError as exc:
        raise EmbeddingError(f"Ollama embedding request failed (HTTP {exc.response.status_code}).") from exc
    except httpx.RequestError as exc:
        raise EmbeddingUnavailable("Unable to connect to the Ollama embedding service.") from exc
    try:
        payload = response.json()
        vectors = payload["embeddings"]
        if not isinstance(vectors, list) or len(vectors) != 1:
            raise ValueError("Expected one embedding.")
        vector = vectors[0]
        if not isinstance(vector, list) or not vector:
            raise ValueError("Expected a nonempty vector.")
        if any(isinstance(v, bool) or not isinstance(v, (float, int)) or not math.isfinite(v) for v in vector):
            raise ValueError("Invalid vector values.")
        if not any(vector):
            raise ValueError("Zero vector.")
        return [float(v) for v in vector]
    except (ValueError, KeyError, TypeError, OverflowError) as exc:
        raise EmbeddingError("Ollama returned an invalid embedding response.") from exc


def cosine_similarity(left: list[float], right: list[float]) -> float:
    """Compare embeddings from the same model; similarity is not legal compliance."""
    if not left or not right or len(left) != len(right):
        raise ValueError("Vectors must be nonempty and have matching dimensions.")
    if any(isinstance(v, bool) or not isinstance(v, (float, int)) or not math.isfinite(v) for v in [*left, *right]):
        raise ValueError("Vectors must contain finite numbers.")
    left_norm, right_norm = math.hypot(*left), math.hypot(*right)
    if not left_norm or not right_norm or not math.isfinite(left_norm) or not math.isfinite(right_norm):
        raise ValueError("Vectors must have finite, nonzero norms.")
    score = math.fsum((a / left_norm) * (b / right_norm) for a, b in zip(left, right))
    return max(-1.0, min(1.0, score))
