"""Local semantic retrieval; all rules remain available to the analyst."""
from functools import lru_cache

from app.config import settings
from app.models.contracts import Contract, Playbook, PolicyMatch
from app.services.ollama_embeddings import cosine_similarity, embed_text


@lru_cache(maxsize=16)
def policy_vectors(base_url: str, model: str, rules: tuple[str, ...]) -> tuple[tuple[float, ...], ...]:
    # URL/model/rule text are cache keys, preventing stale cross-model reuse.
    return tuple(tuple(embed_text(rule)) for rule in rules)


def match_policies(contract: Contract, playbook: Playbook) -> list[PolicyMatch]:
    vectors = policy_vectors(settings.ollama_base_url, settings.ollama_embedding_model,
                             tuple(rule.category + ": " + rule.rule for rule in playbook.rules))
    matches = []
    for clause in contract.clauses:
        vector = embed_text(clause.text)
        ranked = sorted(
            [PolicyMatch(clause_id=clause.clause_id, policy_id=rule.policy_id,
                         similarity=cosine_similarity(vector, list(policy_vector)))
             for rule, policy_vector in zip(playbook.rules, vectors)],
            key=lambda match: match.similarity, reverse=True,
        )
        matches.extend(ranked[:3])
    return matches
