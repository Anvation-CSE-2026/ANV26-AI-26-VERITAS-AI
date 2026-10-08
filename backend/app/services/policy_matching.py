"""Local semantic retrieval; all rules remain available to the analyst."""
from functools import lru_cache

from app.config import settings
from app.services.analysis_observability import timed
from app.models.contracts import Contract, Playbook, PolicyMatch
from app.services.ollama_embeddings import cosine_similarity, embed_text, with_embedding_client


@lru_cache(maxsize=16)
def policy_vectors(base_url: str, model: str, rules: tuple[str, ...]) -> tuple[tuple[float, ...], ...]:
    # URL/model/rule text are cache keys, preventing stale cross-model reuse.
    return tuple(tuple(embed_text(rule)) for rule in rules)


@timed("policy_retrieval")
@with_embedding_client
def match_policies(contract: Contract, playbook: Playbook) -> list[PolicyMatch]:
    vectors = policy_vectors(settings.ollama_base_url, settings.ollama_embedding_model,
                             tuple(rule.category + ": " + rule.rule for rule in playbook.rules))
    matches = []
    # This map belongs only to this retrieval invocation, never another user/request.
    clause_vectors = {}
    for clause in contract.clauses:
        key = (clause.text, settings.ollama_embedding_model, settings.ollama_base_url,
               settings.ollama_connect_timeout, settings.ollama_read_timeout,
               "/api/embed", False, False)  # truncate=False, trust_env=False
        if key not in clause_vectors:
            clause_vectors[key] = embed_text(clause.text)
        vector = clause_vectors[key]
        ranked = sorted(
            [PolicyMatch(clause_id=clause.clause_id, policy_id=rule.policy_id,
                         similarity=cosine_similarity(vector, list(policy_vector)))
             for rule, policy_vector in zip(playbook.rules, vectors)],
            key=lambda match: match.similarity, reverse=True,
        )
        matches.extend(ranked[:3])
    return matches
