import json
from pathlib import Path
from unittest.mock import patch
import httpx
from app.config import settings
from app.services.ollama_embeddings import embed_text,EmbeddingTimeout,EmbeddingUnavailable,EmbeddingError

RealClient=httpx.Client

class Borrowed:
 def __init__(self,c):self.c=c
 def __enter__(self):return self.c
 def __exit__(self,*args):return False

def run_checks():
 checks=[]
 for mode in ('fresh','pooled'):
  for label,expected in [('read_timeout',EmbeddingTimeout),('connection',EmbeddingUnavailable),('http_status',EmbeddingError)]:
   bodies=[]
   def handle(req):
    bodies.append(json.loads(req.content))
    assert 'authorization' not in req.headers and 'cookie' not in req.headers
    if len(bodies)==1:
     if label=='read_timeout':raise httpx.ReadTimeout('synthetic')
     if label=='connection':raise httpx.ConnectError('synthetic')
     return httpx.Response(503,json={'error':'synthetic'})
    return httpx.Response(200,json={'embeddings':[[1.0]*1024]})
   clients=[]
   def factory(**kwargs):
    if mode=='pooled' and clients:return Borrowed(clients[0])
    c=RealClient(transport=httpx.MockTransport(handle),**kwargs);clients.append(c)
    assert c.timeout.connect==settings.ollama_connect_timeout and c.timeout.read==settings.ollama_read_timeout
    return Borrowed(c) if mode=='pooled' else c
   with patch('app.services.ollama_embeddings.httpx.Client',side_effect=factory):
    try:embed_text('SYNTHETIC INPUT A')
    except expected:pass
    else:raise AssertionError('Wrong error mapping')
    assert embed_text('SYNTHETIC INPUT B')==[1.0]*1024
   assert len(bodies)==2 and bodies[0]['input']!=bodies[1]['input']
   for c in clients:c.close()
   checks.append(dict(lifecycle=mode,error=label,mapped_exception=expected.__name__,subsequent_distinct_input_succeeded=True,timeout_configuration_preserved=True,no_auth_or_cookie_state=True))
 return checks

if __name__=="__main__":
 result=run_checks()
 print(str(len(result))+" offline lifecycle/error recovery checks passed; no live requests.")
