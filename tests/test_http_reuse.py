import contextlib,io,json,sys,unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier,Lock
from unittest.mock import patch
import httpx
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
from app.services import ollama_embeddings as embedding
from app.services import policy_matching as retrieval
from app.services.playbook import load_playbook
from evaluation.dataset_loader import load_dataset
from evaluation.offline_guard import no_network

class HttpReuseTests(unittest.TestCase):
 def setUp(self):
  self.contract=load_dataset().cases[0].contract;self.book=load_playbook()
  retrieval.policy_vectors.cache_clear();self.addCleanup(retrieval.policy_vectors.cache_clear)
  self.clients=[];self.calls=[]
 def factory(self,handler=None):
  def handle(request):
   self.calls.append(json.loads(request.content))
   if handler:return handler(request)
   return httpx.Response(200,json={'embeddings':[[1.0,0.2]]},headers={'set-cookie':'unexpected=synthetic'})
  c=httpx.Client(transport=httpx.MockTransport(handle),timeout=httpx.Timeout(120,connect=5),trust_env=False)
  self.clients.append(c);return c
 def test_reuse_closure_dedup_and_separate_requests(self):
  with no_network(),patch.object(embedding,'_new_client',side_effect=self.factory):
   first=retrieval.match_policies(self.contract,self.book)
   self.assertEqual(len(self.clients),1);self.assertEqual(len(self.calls),11)
   second=retrieval.match_policies(self.contract,self.book)
  self.assertEqual(first,second);self.assertEqual(len(self.clients),2);self.assertEqual(len(self.calls),15)
  self.assertTrue(all(c.is_closed for c in self.clients));self.assertIsNone(embedding._client_scope.get())
 def test_fresh_and_pooled_vectors_scores_order_top_k_equivalent(self):
  with no_network(),patch.object(embedding,'_new_client',side_effect=self.factory):
   expected=retrieval.match_policies.__wrapped__.__wrapped__(self.contract,self.book)
   retrieval.policy_vectors.cache_clear()
   actual=retrieval.match_policies(self.contract,self.book)
  self.assertEqual(expected,actual);self.assertEqual(len(actual),18)
  self.assertEqual([x.clause_id for x in actual],[c.clause_id for c in self.contract.clauses for _ in range(3)])
  self.assertTrue(all(c.is_closed for c in self.clients))
 def test_error_classifications_no_retry_and_cleanup(self):
  for kind in ('timeout','connection','http','invalid'):
   self.clients=[];self.calls=[];retrieval.policy_vectors.cache_clear()
   def fail(req):
    if kind=='timeout':raise httpx.ReadTimeout('synthetic')
    if kind=='connection':raise httpx.ConnectError('synthetic')
    return httpx.Response(503 if kind=='http' else 200,json={'embeddings':[]})
   cls={'timeout':embedding.EmbeddingTimeout,'connection':embedding.EmbeddingUnavailable,'http':embedding.EmbeddingError,'invalid':embedding.EmbeddingError}[kind]
   with self.subTest(kind=kind),no_network(),patch.object(embedding,'_new_client',side_effect=lambda:self.factory(fail)):
    with self.assertRaises(cls):retrieval.match_policies(self.contract,self.book)
   self.assertEqual(len(self.calls),1);self.assertTrue(self.clients[0].is_closed);self.assertIsNone(embedding._client_scope.get())
 def test_interrupt_cleanup(self):
  def stop(req):raise KeyboardInterrupt()
  with no_network(),patch.object(embedding,'_new_client',side_effect=lambda:self.factory(stop)):
   with self.assertRaises(KeyboardInterrupt):retrieval.match_policies(self.contract,self.book)
  self.assertTrue(self.clients[0].is_closed);self.assertIsNone(embedding._client_scope.get())
 def test_timeout_payload_and_cookie_isolation(self):
  def handle(req):
   self.assertNotIn('cookie',req.headers);self.assertNotIn('authorization',req.headers)
   self.assertEqual(req.extensions['timeout'],{'connect':5,'read':120,'write':120,'pool':120})
   self.assertFalse(json.loads(req.content)['truncate'])
   return httpx.Response(200,json={'embeddings':[[1.0,0.2]]},headers={'set-cookie':'unexpected=synthetic'})
  with no_network(),patch.object(embedding,'_new_client',side_effect=lambda:self.factory(handle)):
   with embedding.embedding_client_scope():
    self.assertEqual(embedding.embed_text('synthetic A'),embedding.embed_text('synthetic B'))
  self.assertEqual(len(self.clients),1);self.assertEqual([r['input'] for r in self.calls],['synthetic A','synthetic B'])
 def test_concurrent_retrievals_have_separate_clients(self):
  barrier=Barrier(2);lock=Lock();requests={}
  def factory():
   c=None
   def handle(req):
    with lock:
     count=requests.get(id(c),0);requests[id(c)]=count+1
    if count==0:barrier.wait(timeout=10)
    return httpx.Response(200,json={'embeddings':[[1.0,0.2]]})
   c=httpx.Client(transport=httpx.MockTransport(handle));self.clients.append(c);return c
  vectors=tuple((1.0,0.2) for _ in self.book.rules)
  with no_network(),patch.object(embedding,'_new_client',side_effect=factory),patch.object(retrieval,'policy_vectors',return_value=vectors):
   with ThreadPoolExecutor(max_workers=2) as executor:
    futures=[executor.submit(retrieval.match_policies,self.contract,self.book) for _ in range(2)]
    results=[f.result(timeout=15) for f in futures]
  self.assertEqual(results[0],results[1]);self.assertEqual(len(self.clients),2)
  self.assertEqual(sorted(requests.values()),[4,4]);self.assertTrue(all(c.is_closed for c in self.clients))
 def test_nested_scope_and_standalone_do_not_borrow_closed_client(self):
  with no_network(),patch.object(embedding,'_new_client',side_effect=self.factory):
   with embedding.embedding_client_scope():
    embedding.embed_text('A')
    with embedding.embedding_client_scope():embedding.embed_text('B')
    self.assertTrue(self.clients[1].is_closed);self.assertFalse(self.clients[0].is_closed)
    embedding.embed_text('C')
   embedding.embed_text('D')
  self.assertEqual(len(self.clients),3);self.assertTrue(all(c.is_closed for c in self.clients))
 def test_scope_creation_failure_preserves_timeout_mapping(self):
  with patch.object(embedding,'_new_client',side_effect=httpx.ConnectTimeout('synthetic')):
   with self.assertRaises(embedding.EmbeddingTimeout):retrieval.match_policies(self.contract,self.book)
  self.assertIsNone(embedding._client_scope.get())
 def test_actual_client_factory_preserves_configuration(self):
  from app.config import settings
  real_client=httpx.Client
  captured=[]
  def factory(**kwargs):
   captured.append(kwargs)
   return real_client(transport=httpx.MockTransport(lambda r:httpx.Response(200,json={'embeddings':[[1.0,0.2]]})),**kwargs)
  with no_network(),patch('app.services.ollama_embeddings.httpx.Client',side_effect=factory):
   with embedding.embedding_client_scope():
    embedding.embed_text('synthetic')
  self.assertEqual(len(captured),1)
  self.assertFalse(captured[0]['trust_env'])
  self.assertEqual(captured[0]['timeout'].as_dict(),{'connect':settings.ollama_connect_timeout,'read':settings.ollama_read_timeout,'write':settings.ollama_read_timeout,'pool':settings.ollama_read_timeout})
 def test_no_sensitive_text_in_output(self):
  out=io.StringIO();err=io.StringIO()
  with no_network(),contextlib.redirect_stdout(out),contextlib.redirect_stderr(err),patch.object(embedding,'_new_client',side_effect=self.factory):
   retrieval.match_policies(self.contract,self.book)
  self.assertEqual(out.getvalue()+err.getvalue(),'')

if __name__=='__main__':unittest.main()
