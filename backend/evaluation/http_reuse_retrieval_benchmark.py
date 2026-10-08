"""Explicit opt-in, synthetic-only Ollama retrieval comparison; never invokes Gemini."""
import argparse
import hashlib
import json
import platform
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import httpx
from app.config import settings
from app.models.contracts import PolicyMatch
from app.services import policy_matching as retrieval
from app.services.ollama_embeddings import embed_text, cosine_similarity
from app.services.playbook import load_playbook
from app.services.analysis_observability import observation_scope, timed
from evaluation.dataset_loader import load_dataset

REPORT = Path(__file__).parent / 'reports/http-reuse-real-retrieval.json'

@timed('policy_retrieval')
def original_retrieval(contract: Contract, playbook: Playbook) -> list[PolicyMatch]:
    vectors = retrieval.policy_vectors(settings.ollama_base_url, settings.ollama_embedding_model,
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

class Observer:
    def __init__(self):
        self.spans = []
        self.observation_failed = False
    def begin_stage(self, name, started):
        self.spans.append(dict(stage=name, seconds=None, status='running'))
        return len(self.spans)-1
    def event(self, event, **data):
        if event == 'stage_finished':
            self.spans[data['span_id']].update(seconds=data['seconds'], status=data['status'])

def snapshot():
    p = Path(settings.storage_path).resolve()
    return {str(f): hashlib.sha256(f.read_bytes()).hexdigest() if f.exists() else None
            for f in (p, Path(str(p)+'-wal'), Path(str(p)+'-shm'))}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live-ollama', action='store_true')
    args = parser.parse_args()
    if not args.live_ollama:
        parser.error('Explicit --live-ollama is required')
    report = dict(started_at_utc=datetime.now(timezone.utc).isoformat(), live_ollama=True,
                  gemini_calls=0, billing_calls=0, authentication_calls=0, runs=[], warmups=[], status='preflight')
    def save():
        REPORT.parent.mkdir(exist_ok=True)
        REPORT.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    prior = snapshot()
    original_send = httpx.Client.send
    provider_requests = []
    def restricted_send(client, request, **kwargs):
        if (request.url.scheme != 'http' or request.url.host not in ('localhost','127.0.0.1') or
            request.url.port != 11434 or request.url.path not in ('/api/version','/api/tags','/api/ps','/api/embed')):
            raise RuntimeError('Non-Ollama endpoint prohibited by benchmark guard')
        response = original_send(client, request, **kwargs)
        if request.url.path == '/api/embed':
            meta = {}
            if response.status_code == 200:
                payload = response.json()
                meta = {k: payload[k] for k in ('total_duration','load_duration','prompt_eval_count')
                        if isinstance(payload.get(k),(int,float)) and not isinstance(payload.get(k),bool)}
            provider_requests.append(dict(http_status=response.status_code, provider_metadata=meta))
        return response
    def get(path):
        with httpx.Client(timeout=10, trust_env=False) as client:
            response = client.get(settings.ollama_base_url.rstrip('/')+path)
            response.raise_for_status()
            return response.json()
    def residency():
        try:
            return [dict(name=m.get('name'), size_vram=m.get('size_vram'), expires_at=m.get('expires_at'))
                    for m in get('/api/ps').get('models',[]) if m.get('name')==settings.ollama_embedding_model]
        except Exception:
            return None
    def run(function, variant, cache, iteration):
        retrieval.policy_vectors.cache_clear()
        preparation_calls = 0
        if cache == 'warm':
            start = len(provider_requests)
            from app.services.ollama_embeddings import embedding_client_scope
            with embedding_client_scope():
                retrieval.policy_vectors(settings.ollama_base_url, settings.ollama_embedding_model,
                                          tuple(r.category+': '+r.rule for r in book.rules))
            preparation_calls = len(provider_requests)-start
        resident_before = residency()
        observer = Observer()
        offset = len(provider_requests)
        started = time.perf_counter()
        with observation_scope(observer):
            matches = function(contract, book)
        elapsed = time.perf_counter()-started
        assert not observer.observation_failed
        requests = [s for s in observer.spans if s['stage']=='embedding_request']
        expected = 11 if cache=='cold' else 4
        assert len(requests)==expected and len(provider_requests)-offset==expected
        return dict(variant=variant, policy_cache=cache, iteration=iteration,
                    total_retrieval_seconds=elapsed, embedding_request_count=len(requests),
                    embedding_request_seconds=[s['seconds'] for s in requests],
                    provider_requests=provider_requests[offset:],
                    policy_cache_preparation_calls_excluded=preparation_calls,
                    model_resident_before=resident_before, model_resident_after=residency(),
                    results=[m.model_dump() for m in matches])
    try:
        with patch('httpx.Client.send', new=restricted_send):
            assert settings.ollama_base_url.rstrip('/') in ('http://localhost:11434','http://127.0.0.1:11434')
            assert settings.ollama_embedding_model=='qwen3-embedding:0.6b'
            version=get('/api/version').get('version')
            tags=get('/api/tags').get('models',[])
            installed=next(m for m in tags if m.get('name')==settings.ollama_embedding_model)
            vector=embed_text('Synthetic retrieval benchmark warm-up.')
            assert len(vector)==1024
            dataset=load_dataset('synthetic_v1')
            contract=dataset.cases[0].contract
            assert contract.contract_id=='SYN-supplier_red'
            book=load_playbook()
            report['environment']=dict(platform=platform.platform(),python=platform.python_version(),
                httpx_version=httpx.__version__,ollama_version=version,base_url=settings.ollama_base_url,
                model=settings.ollama_embedding_model,model_digest=installed.get('digest'),dimensions=len(vector),
                connect_timeout=settings.ollama_connect_timeout,read_timeout=settings.ollama_read_timeout,
                truncate=False,trust_env=False,top_k=3,contract_id=contract.contract_id,
                playbook_id=book.playbook_id,playbook_version=book.version,
                input_sha256=hashlib.sha256(contract.model_dump_json().encode()).hexdigest(),
                policy_sha256=hashlib.sha256(book.model_dump_json().encode()).hexdigest())
            print('Preflight passed: local installed model, 1024 dimensions, synthetic data; no Gemini/database services.',flush=True)
            for variant,function in [('original',original_retrieval),('optimized',retrieval.match_policies)]:
                report['warmups'].append(run(function,variant,'cold',0))
                print('Initial warm-up completed: '+variant,flush=True)
                save()
            report['status']='running'
            for cache in ('cold','warm'):
                for iteration in range(1,4):
                    variants=[('original',original_retrieval),('optimized',retrieval.match_policies)]
                    if iteration%2==0:
                        variants.reverse()
                    for variant,function in variants:
                        row=run(function,variant,cache,iteration)
                        report['runs'].append(row)
                        save()
                        print(cache+' '+variant+' iteration '+str(iteration)+': '+format(row['total_retrieval_seconds'],'.3f')+' s; '+str(row['embedding_request_count'])+' calls',flush=True)
            baseline=report['runs'][0]['results']
            differences=[]
            max_difference=0.0
            for index,row in enumerate(report['runs']):
                keys=[(m['clause_id'],m['policy_id']) for m in row['results']]
                expected=[(m['clause_id'],m['policy_id']) for m in baseline]
                if keys!=expected:
                    differences.append(dict(run=index,category='id_order_or_top_k'))
                if len(row['results'])!=len(baseline):
                    differences.append(dict(run=index,category='result_count'))
                for a,b in zip(row['results'],baseline):
                    delta=abs(a['similarity']-b['similarity'])
                    max_difference=max(max_difference,delta)
                    if delta>1e-6:
                        differences.append(dict(run=index,category='similarity',clause_id=a['clause_id'],delta=delta))
            report['equivalence']=dict(tolerance=1e-6,identical_ids_order_top_k=not any(d['category']=='id_order_or_top_k' for d in differences),
                all_18_entries_preserved=all(len(row['results'])==18 for row in report['runs']),
                max_absolute_score_difference=max_difference,differences=differences,
                synthetic_clause_ids=[c.clause_id for c in contract.clauses])
            report['medians']={}
            for cache in ('cold','warm'):
                med={v:statistics.median(row['total_retrieval_seconds'] for row in report['runs'] if row['policy_cache']==cache and row['variant']==v) for v in ('original','optimized')}
                med['improvement_percent']=100*(med['original']-med['optimized'])/med['original']
                report['medians'][cache]=med
            report['production_sqlite_unchanged']=snapshot()==prior
            assert report['production_sqlite_unchanged']
            report['status']='completed'
            save()
            print(json.dumps(dict(status=report['status'],medians=report['medians'],equivalence=report['equivalence'],production_sqlite_unchanged=True)),flush=True)
    except BaseException as exc:
        report['status']='interrupted' if isinstance(exc,KeyboardInterrupt) else 'failed'
        report['error_type']=type(exc).__name__
        report['production_sqlite_unchanged']=snapshot()==prior
        save()
        print('Benchmark stopped: '+type(exc).__name__+'; no exception content or credentials logged.',flush=True)
        return 1
    finally:
        retrieval.policy_vectors.cache_clear()
    return 0

if __name__=='__main__':
    raise SystemExit(main())
