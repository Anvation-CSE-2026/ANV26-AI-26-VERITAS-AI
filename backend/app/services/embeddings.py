"""Provider selection and vector-space identity for semantic matching only."""
import hashlib
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps

from app.config import settings
from app.services import ollama_embeddings
from app.services.ollama_embeddings import EmbeddingError, cosine_similarity

_configuration = ContextVar("embedding_configuration", default=None)


def embedding_model() -> str:
    return (settings.gemini_embedding_model if settings.embedding_provider == "gemini"
            else settings.ollama_embedding_model)


def embedding_cache_key() -> tuple:
    """No text normalization or plaintext credentials in cache identities."""
    if settings.embedding_provider == "ollama":
        return ("ollama", settings.ollama_embedding_model, settings.ollama_base_url,
                settings.ollama_connect_timeout, settings.ollama_read_timeout,
                "/api/embed", False, False)
    if settings.embedding_provider == "gemini":
        return ("gemini", settings.gemini_embedding_model,
                "https://generativelanguage.googleapis.com", "v1beta",
                "SEMANTIC_SIMILARITY", settings.gemini_embedding_dimensions,
                settings.gemini_embedding_timeout_seconds, 1, False,
                hashlib.sha256(settings.gemini_api_key.encode()).hexdigest())
    raise EmbeddingError("Unknown embedding provider.")


def ensure_embedding_configuration(expected: tuple) -> None:
    # Refuse to compare policy/clause vectors if configuration changes mid-retrieval.
    if embedding_cache_key() != expected:
        raise EmbeddingError("Embedding configuration changed during retrieval; vectors were not compared.")


@contextmanager
def embedding_client_scope():
    key = embedding_cache_key()
    token = _configuration.set(key)
    try:
        if key[0] == "ollama":
            with ollama_embeddings.embedding_client_scope():
                yield
        else:
            from app.services.gemini_embeddings import embedding_client_scope as gemini_scope
            with gemini_scope():
                yield
        ensure_embedding_configuration(key)
    finally:
        _configuration.reset(token)


def with_embedding_client(function):
    @wraps(function)
    def wrapped(*args, **kwargs):
        with embedding_client_scope():
            return function(*args, **kwargs)
    return wrapped


def embed_text(text: str) -> list[float]:
    key = _configuration.get() or embedding_cache_key()
    ensure_embedding_configuration(key)
    if key[0] == "ollama":
        vector = ollama_embeddings.embed_text(text)
    else:
        from app.services.gemini_embeddings import embed_text as gemini_embed
        vector = gemini_embed(text)
    ensure_embedding_configuration(key)
    return vector
