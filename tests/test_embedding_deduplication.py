"""Offline equivalence/isolation tests and explicitly simulated retrieval measurements."""
import contextlib
import hashlib
import io
import json
import math
import statistics
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
from app.config import settings
from app.models.contracts import PolicyMatch
from app.services import policy_matching as retrieval
from app.services.ollama_embeddings import EmbeddingError, EmbeddingTimeout, EmbeddingUnavailable, cosine_similarity
from evaluation.dataset_loader import load_dataset
from evaluation.offline_guard import no_network


def reference_retrieval(contract, playbook):
    """Pre-change retrieval loop: each clause always makes its own embedding call."""
    vectors = retrieval.policy_vectors(settings.ollama_base_url, settings.ollama_embedding_model,
                                      tuple(r.category + ': ' + r.rule for r in playbook.rules))
    matches = []
    for clause in contract.clauses:
        vector = retrieval.embed_text(clause.text)
        ranked = sorted([PolicyMatch(clause_id=clause.clause_id, policy_id=rule.policy_id,
                          similarity=cosine_similarity(vector, list(policy_vector)))
                         for rule, policy_vector in zip(playbook.rules, vectors)],
                        key=lambda match: match.similarity, reverse=True)
        matches.extend(ranked[:3])
    return matches


def fake_vector(text):
    digest = hashlib.sha256(text.encode()).digest()
    return [((digest[i % len(digest)] - 127) / 128) for i in range(1024)]


class DeduplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset = load_dataset()
        from app.services.playbook import load_playbook
        cls.book = load_playbook()

    def setUp(self):
        retrieval.policy_vectors.cache_clear()
        self.addCleanup(retrieval.policy_vectors.cache_clear)
        self.contract = self.dataset.cases[0].contract.model_copy(deep=True)

    def test_identical_text_once_and_clauses_ids_order_preserved(self):
        before = self.contract.model_dump()
        with no_network(), patch.object(retrieval, 'embed_text', side_effect=fake_vector) as embed:
            matches = retrieval.match_policies(self.contract, self.book)
        self.assertEqual(embed.call_count, 11)
        texts = [c.args[0] for c in embed.call_args_list]
        self.assertEqual(texts.count(self.contract.clauses[0].text), 1)
        self.assertEqual(self.contract.model_dump(), before)
        self.assertEqual([m.clause_id for m in matches],
                         [c.clause_id for c in self.contract.clauses for _ in range(3)])
        self.assertEqual(len(matches), 18)

    def test_different_whitespace_and_unicode_are_not_normalized(self):
        self.contract.clauses = self.contract.clauses[:4]
        for clause, text in zip(self.contract.clauses, ['Clause', 'Clause ', 'Clause\n', 'Ｃlause']):
            clause.text = text
        with no_network(), patch.object(retrieval, 'embed_text', side_effect=fake_vector) as embed:
            retrieval.match_policies(self.contract, self.book)
        self.assertEqual([c.args[0] for c in embed.call_args_list[7:]],
                         ['Clause', 'Clause ', 'Clause\n', 'Ｃlause'])

    def test_separate_requests_have_separate_clause_caches(self):
        with no_network(), patch.object(retrieval, 'embed_text', side_effect=fake_vector) as embed:
            first = retrieval.match_policies(self.contract, self.book)
            cold = embed.call_count
            second = retrieval.match_policies(self.contract, self.book)
        self.assertEqual(cold, 11)
        self.assertEqual(embed.call_count - cold, 4)
        self.assertEqual(first, second)

    def test_configuration_changes_do_not_share_local_entries(self):
        # Change one dimension between two identical clauses inside one invocation.
        for field, replacement in [('ollama_embedding_model', 'synthetic-other-model'),
                                   ('ollama_base_url', 'http://synthetic-other:11434'),
                                   ('ollama_connect_timeout', 6.0), ('ollama_read_timeout', 121.0)]:
            with self.subTest(field=field):
                contract = self.contract.model_copy(deep=True)
                contract.clauses = [contract.clauses[0], contract.clauses[2]]
                count = 0
                def embed(text):
                    nonlocal count
                    count += 1
                    if count == 1:
                        setattr(settings, field, replacement)
                    return fake_vector(text)
                with no_network(), patch.object(settings, field, getattr(settings, field)), \
                     patch.object(retrieval, 'policy_vectors', return_value=tuple(tuple(fake_vector(r.rule)) for r in self.book.rules)), \
                     patch.object(retrieval, 'embed_text', side_effect=embed):
                    retrieval.match_policies(contract, self.book)
                self.assertEqual(count, 2)

    def test_all_fixture_rankings_and_scores_match_original_loop(self):
        for case in self.dataset.cases:
            with self.subTest(contract_id=case.contract.contract_id), no_network(), \
                 patch.object(retrieval, 'embed_text', side_effect=fake_vector):
                retrieval.policy_vectors.cache_clear()
                expected = reference_retrieval(case.contract, self.book)
                retrieval.policy_vectors.cache_clear()
                actual = retrieval.match_policies(case.contract, self.book)
                self.assertEqual([(x.clause_id, x.policy_id) for x in actual],
                                 [(x.clause_id, x.policy_id) for x in expected])
                for left, right in zip(actual, expected):
                    self.assertTrue(math.isclose(left.similarity, right.similarity, rel_tol=1e-12, abs_tol=1e-12))

    def test_equal_scores_keep_playbook_tie_order(self):
        with no_network(), patch.object(retrieval, 'embed_text', return_value=[1.0, 0.0]):
            actual = retrieval.match_policies(self.contract, self.book)
        self.assertEqual([m.policy_id for m in actual[:3]], [r.policy_id for r in self.book.rules[:3]])

    def test_errors_propagate_and_next_request_recomputes(self):
        for error in (EmbeddingTimeout('synthetic timeout'), EmbeddingUnavailable('synthetic unavailable'),
                      EmbeddingError('synthetic invalid embedding')):
            with self.subTest(error=type(error).__name__), no_network():
                with patch.object(retrieval, 'policy_vectors', return_value=tuple(tuple(fake_vector(r.rule)) for r in self.book.rules)), \
                     patch.object(retrieval, 'embed_text', side_effect=[fake_vector('header'), error]) as embed:
                    with self.assertRaises(type(error)) as raised:
                        retrieval.match_policies(self.contract, self.book)
                    self.assertIs(raised.exception, error)
                    self.assertEqual(embed.call_count, 2)
                with patch.object(retrieval, 'embed_text', side_effect=fake_vector) as embed:
                    retrieval.match_policies(self.contract, self.book)
                    self.assertEqual(embed.call_count, 11)
                retrieval.policy_vectors.cache_clear()

    def test_no_sensitive_text_is_logged(self):
        self.contract.clauses[0].text = 'SYNTHETIC PRIVATE CLAUSE SENTINEL'
        out, err = io.StringIO(), io.StringIO()
        with no_network(), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), \
             patch.object(retrieval, 'embed_text', side_effect=fake_vector):
            retrieval.match_policies(self.contract, self.book)
        self.assertEqual(out.getvalue(), '')
        self.assertEqual(err.getvalue(), '')


def measure_simulated_performance():
    """Comparable mock-only cold/warm runs, never real service performance."""
    dataset = load_dataset()
    contract = dataset.cases[0].contract
    from app.services.playbook import load_playbook
    book = load_playbook()
    vectors = {text: fake_vector(text) for text in
               [r.category + ': ' + r.rule for r in book.rules] + [c.text for c in contract.clauses]}
    samples = {'cold': {'before': [], 'after': []}, 'warm': {'before': [], 'after': []}}
    results = []
    for state in samples:
        for iteration in range(5):
            # Alternate order to reduce systematic before/after scheduling bias.
            order = [('before', reference_retrieval), ('after', retrieval.match_policies)]
            if iteration % 2:
                order.reverse()
            for label, function in order:
                retrieval.policy_vectors.cache_clear()
                def embed(text):
                    time.sleep(0.02)  # Explicitly simulated constant per-request cost.
                    return vectors[text][:]
                with no_network(), patch.object(retrieval, 'embed_text', side_effect=embed) as mock:
                    if state == 'warm':
                        retrieval.policy_vectors(settings.ollama_base_url, settings.ollama_embedding_model,
                                                 tuple(r.category + ': ' + r.rule for r in book.rules))
                        mock.reset_mock()
                    started = time.perf_counter()
                    matches = function(contract, book)
                    elapsed = time.perf_counter() - started
                    calls = mock.call_count
                expected = 13 if state == 'cold' and label == 'before' else 11 if state == 'cold' else 6 if label == 'before' else 4
                assert calls == expected
                samples[state][label].append(dict(seconds=elapsed, embedding_calls=calls))
                results.append(matches)
    assert all(result == results[0] for result in results)
    retrieval.policy_vectors.cache_clear()
    report = dict(label='SIMULATED MOCK TIMING — NOT REAL OLLAMA PERFORMANCE', contract_id=contract.contract_id,
                  dimension=1024, simulated_request_delay_seconds=0.02, repeats_per_variant=5,
                  network_blocked=True, live_services_used=False, equivalent_rankings_and_scores=True,
                  samples=samples, median_seconds={s: {l: statistics.median(x['seconds'] for x in rows)
                                                     for l, rows in v.items()} for s, v in samples.items()})
    path = Path(__file__).resolve().parents[1] / 'backend/evaluation/reports/embedding-deduplication-simulated.json'
    path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k != 'samples'}, indent=2))


if __name__ == '__main__':
    if '--measure' in sys.argv:
        measure_simulated_performance()
    else:
        unittest.main()
