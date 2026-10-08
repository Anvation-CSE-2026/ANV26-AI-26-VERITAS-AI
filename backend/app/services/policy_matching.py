"""Provider-isolated semantic retrieval; all rules remain available to the analyst."""
from functools import lru_cache

from app.config import settings
from app.services.analysis_observability import timed
from app.models.contracts import Contract, Playbook, PolicyMatch
from app.services.embeddings import (
    cosine_similarity, embed_text, with_embedding_client, embedding_cache_key,
    ensure_embedding_configuration,
)


@lru_cache(maxsize=16)
def _policy_vectors(configuration: tuple, rules: tuple[str, ...]) -> tuple[tuple[float, ...], ...]:
    ensure_embedding_configuration(configuration)
    vectors = tuple(tuple(embed_text(rule)) for rule in rules)
    ensure_embedding_configuration(configuration)
    return vectors


def policy_vectors(base_url: str, model: str, rules: tuple[str, ...]) -> tuple[tuple[float, ...], ...]:
    # Preserve the legacy interface; all effective provider settings participate in identity.
    return _policy_vectors(embedding_cache_key(), rules)


policy_vectors.cache_clear = _policy_vectors.cache_clear
policy_vectors.cache_info = _policy_vectors.cache_info


@timed("policy_retrieval")
@with_embedding_client
def match_policies(contract: Contract, playbook: Playbook) -> list[PolicyMatch]:
    configuration = embedding_cache_key()
    vectors = policy_vectors(settings.ollama_base_url, settings.ollama_embedding_model,
                             tuple(rule.category + ": " + rule.rule for rule in playbook.rules))
    matches = []
    # This map belongs only to this retrieval invocation, never another user/request.
    clause_vectors = {}
    for clause in contract.clauses:
        ensure_embedding_configuration(configuration)
        key = (clause.text, configuration)
        if key not in clause_vectors:
            clause_vectors[key] = embed_text(clause.text)
        vector = clause_vectors[key]
        ensure_embedding_configuration(configuration)
        ranked = sorted(
            [PolicyMatch(clause_id=clause.clause_id, policy_id=rule.policy_id,
                         similarity=cosine_similarity(vector, list(policy_vector)))
             for rule, policy_vector in zip(playbook.rules, vectors)],
            key=lambda match: match.similarity, reverse=True,
        )
        matches.extend(ranked[:3])
    return matches
