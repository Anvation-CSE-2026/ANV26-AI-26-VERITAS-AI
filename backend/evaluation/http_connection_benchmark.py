"""Opt-in synthetic local-only fresh versus pooled HTTP client benchmark."""
import argparse,json,hashlib,math,platform,statistics,time
from pathlib import Path
from unittest.mock import patch
import httpx
from app.config import settings
from app.services.ollama_embeddings import embed_text,EmbeddingTimeout,EmbeddingUnavailable,EmbeddingError
OUT=Path(__file__).parent/'reports/http-connection-benchmark.json'
TEXT='Synthetic supplier must notify the synthetic company within 48 hours of a data breach.'

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--live-ollama',action='store_true');args=p.parse_args()
 if not args.live_ollama:p.error('Explicit --live-ollama required')
 report=dict(status='preflight',iterations=5,requests_per_iteration=3,runs=[],errors=[],gemini_calls=0)
 def save():
  OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 db=Path(settings.storage_path).resolve()
 paths=[db,Path(str(db)+'-wal'),Path(str(db)+'-shm')]
 before={str(x):hashlib.sha256(x.read_bytes()).hexdigest() if x.exists() else None for x in paths}
 timeout=httpx.Timeout(settings.ollama_read_timeout,connect=settings.ollama_connect_timeout)
 def client():return httpx.Client(timeout=timeout,trust_env=False)
 def request(c):
  trace=[]
  def event(name,info):trace.append((name,time.perf_counter()))
  started=time.perf_counter()
  r=c.post(settings.ollama_base_url.rstrip('/')+'/api/embed',json=dict(model=settings.ollama_embedding_model,input=TEXT,truncate=False),extensions={'trace':event})
  latency=time.perf_counter()-started;r.raise_for_status();data=r.json();v=data['embeddings'][0]
  assert len(data['embeddings'])==1 and len(v)==1024 and any(v) and all(isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x) for x in v)
  connect=[t for n,t in trace if n.endswith('connect_tcp.started')];finished=[t for n,t in trace if n.endswith('connect_tcp.complete')]
  return v,dict(request_seconds=latency,connect_tcp_count=len(connect),connect_tcp_seconds=sum(b-a for a,b in zip(connect,finished)),http_status=r.status_code,provider_total_duration_ns=data.get('total_duration'),provider_load_duration_ns=data.get('load_duration'),cookies_received=len(c.cookies))
 try:
  assert settings.ollama_base_url.rstrip('/')=='http://localhost:11434' and settings.ollama_embedding_model=='qwen3-embedding:0.6b'
  with client() as c:
   version=c.get(settings.ollama_base_url+'/api/version');version.raise_for_status()
   tags=c.get(settings.ollama_base_url+'/api/tags');tags.raise_for_status()
   installed=next(m for m in tags.json()['models'] if m.get('name')==settings.ollama_embedding_model)
   baseline,_=request(c)
  report['environment']=dict(platform=platform.platform(),python=platform.python_version(),httpx=httpx.__version__,ollama=version.json()['version'],model=settings.ollama_embedding_model,digest=installed.get('digest'),dimensions=1024,url=settings.ollama_base_url,connect_timeout=settings.ollama_connect_timeout,read_timeout=settings.ollama_read_timeout,trust_env=False,truncate=False,retries=0,input_sha256=hashlib.sha256(TEXT.encode()).hexdigest())
  print('Preflight passed; local model/dimensions verified. No Gemini or database services.',flush=True)
  report['status']='running';maxdelta=0.0
  for i in range(1,6):
   order=['fresh','pooled'] if i%2 else ['pooled','fresh']
   for variant in order:
    row=dict(iteration=i,variant=variant,client_creation_seconds=[],requests=[],close_seconds=[],warmup=None)
    if variant=='pooled':
     begin=time.perf_counter();c=client();row['client_creation_seconds'].append(time.perf_counter()-begin)
     _,row['warmup']=request(c)
    else:
     with client() as warm:_,row['warmup']=request(warm)
    started=time.perf_counter()
    try:
     for j in range(3):
      if variant=='fresh':
       begin=time.perf_counter();c=client();row['client_creation_seconds'].append(time.perf_counter()-begin)
      v,measurement=request(c);row['requests'].append(measurement)
      maxdelta=max(maxdelta,max(abs(a-b) for a,b in zip(v,baseline)))
      assert maxdelta<=1e-6
      if variant=='fresh':
       begin=time.perf_counter();c.close();row['close_seconds'].append(time.perf_counter()-begin)
    finally:
     if variant=='pooled':
      begin=time.perf_counter();c.close();row['close_seconds'].append(time.perf_counter()-begin)
    row['measured_total_seconds']=time.perf_counter()-started
    # Pooled construction is before connection warm-up; include it separately for fairness.
    row['setup_inclusive_seconds']=row['measured_total_seconds']+(sum(row['client_creation_seconds']) if variant=='pooled' else 0)
    report['runs'].append(row);save()
    print(variant+' iteration '+str(i)+': '+format(row['measured_total_seconds'],'.3f')+' s; connections='+str(sum(x['connect_tcp_count'] for x in row['requests'])),flush=True)
  summary={}
  for variant in ('fresh','pooled'):
   rows=[r for r in report['runs'] if r['variant']==variant];lat=[r['measured_total_seconds'] for r in rows]
   summary[variant]=dict(median_total_seconds=statistics.median(lat),median_setup_inclusive_seconds=statistics.median(r['setup_inclusive_seconds'] for r in rows),minimum_total_seconds=min(lat),maximum_total_seconds=max(lat),sample_stdev_seconds=statistics.stdev(lat),median_client_creation_seconds=statistics.median(t for r in rows for t in r['client_creation_seconds']),median_request_seconds=statistics.median(x['request_seconds'] for r in rows for x in r['requests']),measured_connections=sum(x['connect_tcp_count'] for r in rows for x in r['requests']),measured_requests=sum(len(r['requests']) for r in rows))
  report['summary']=summary;report['improvement_percent']=100*(summary['fresh']['median_setup_inclusive_seconds']-summary['pooled']['median_setup_inclusive_seconds'])/summary['fresh']['median_setup_inclusive_seconds']
  report['correctness']=dict(max_absolute_vector_difference=maxdelta,tolerance=1e-6,all_dimensions_1024=True,all_http_status_200=True,no_cookies_received=all(x['cookies_received']==0 for r in report['runs'] for x in [r['warmup'],*r['requests']]),distinct_client_per_iteration=True)
  from evaluation.http_connection_safety import run_checks
  report['offline_error_mapping_checks']=run_checks()
  report['production_sqlite_unchanged']=before=={str(x):hashlib.sha256(x.read_bytes()).hexdigest() if x.exists() else None for x in paths};assert report['production_sqlite_unchanged']
  report['status']='completed';save();print(json.dumps(dict(status=report['status'],summary=summary,improvement_percent=report['improvement_percent'],correctness=report['correctness'])),flush=True)
 except Exception as exc:
  report['status']='failed';report['errors'].append(dict(type=type(exc).__name__));save();print('Stopped: '+type(exc).__name__+'; no exception content logged.',flush=True);return 1
 return 0
if __name__=='__main__':raise SystemExit(main())
