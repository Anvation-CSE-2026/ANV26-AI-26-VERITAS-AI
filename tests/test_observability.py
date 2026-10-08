"""Offline observability tests; external services always mocked/network blocked."""
import contextlib
import copy
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"backend"))
from app.models.contracts import AnalysisDraft, RiskDraft, ObligationDraft
from app.services.analysis_observability import observation_scope, stage, emit, _observer
from app.services.evidence import verify_analysis, EvidenceError
from app.services.playbook import load_playbook
from app.config import settings
from evaluation.dataset_loader import load_dataset
from evaluation.tracing import TraceCollector, reason_details, redact
from evaluation.offline_guard import no_network

def case():
    return load_dataset().cases[0]

def draft(source,invalid=False):
    liability=source.clauses[1]
    indemnity=source.clauses[3]
    base=dict(risk_level="high",clause_category="liability",explanation="Synthetic cap risk.",
              evidence_quote=liability.text,page_number=1,clause_id=liability.clause_id,
              policy_id="POL-LIAB-001",recommended_action="Review synthetic cap.")
    items=[RiskDraft(**base)]
    if invalid:
        bad=dict(base,evidence_quote="This quote does not exist.")
        items.append(RiskDraft(**bad))
        bad=dict(base,page_number=2)
        items.append(RiskDraft(**bad))
        bad=dict(base,evidence_quote=None)
        items.append(RiskDraft(**bad))
    items.append(RiskDraft(risk_level="medium",clause_category="termination",explanation="Potential omission only.",
        finding_status="missing",policy_id="POL-TERM-001",recommended_action="Review omission."))
    obligations=[ObligationDraft(description="Synthetic indemnity.",evidence_quote=indemnity.text,
        page_number=2,clause_id=indemnity.clause_id,responsible_party="Company",deadline=None)]
    if invalid:
        obligations.append(ObligationDraft(description="Invalid source party.",evidence_quote=indemnity.text,
            page_number=2,clause_id=indemnity.clause_id,responsible_party="ImaginaryPerson",deadline=None))
    return AnalysisDraft(findings=items,obligations=obligations)

class ObservabilityTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.c=case()

    def collector(self):
        return TraceCollector(self.c,"offline-test",output_root=Path(self.temp.name)/"private")

    def verify(self,collector,value):
        with observation_scope(collector):
            return verify_analysis(value,self.c.contract,load_playbook())

    def test_default_disabled_and_no_raw_output(self):
        self.assertIsNone(_observer.get())
        output=io.StringIO()
        with contextlib.redirect_stdout(output),contextlib.redirect_stderr(output):
            verify_analysis(draft(self.c.contract,True),self.c.contract,load_playbook())
        self.assertEqual(output.getvalue(),"")
        self.assertEqual(list(Path(self.temp.name).rglob("trace.json")),[])

    def test_decisions_unchanged_and_counts_reconcile(self):
        d=draft(self.c.contract,True)
        without=verify_analysis(d,self.c.contract,load_playbook())
        collector=self.collector()
        with_trace=self.verify(collector,d)
        self.assertEqual(without,with_trace)
        payload=collector.finish()
        self.assertEqual(payload["counts"]["findings"],dict(proposed=5,retained=2,rejected=3,unverified=0))
        self.assertEqual(payload["counts"]["obligations"],dict(proposed=2,retained=1,rejected=1,unverified=0))
        for counts in payload["counts"].values():
            self.assertEqual(counts["proposed"],counts["retained"]+counts["rejected"]+counts["unverified"])

    def test_every_rejection_has_code_stage_and_original_reason(self):
        collector=self.collector()
        self.verify(collector,draft(self.c.contract,True))
        rejected=[i for i in collector.finish()["items"] if i["retained"] is False]
        self.assertEqual(len(rejected),4)
        for item in rejected:
            self.assertTrue(item["rejection_reason_code"])
            self.assertTrue(item["original_verifier_reason"])
            self.assertTrue(item["diagnostic"])
            self.assertEqual(item["rejection_stage"],"evidence_verification")
            self.assertEqual(item["final_status"],"rejected")

    def test_quote_page_and_missing_evidence_distinguished(self):
        collector=self.collector()
        self.verify(collector,draft(self.c.contract,True))
        rows=collector.finish()["items"]
        self.assertEqual(rows[1]["rejection_reason_code"],"QUOTE_NOT_FOUND")
        self.assertEqual(rows[2]["rejection_reason_code"],"PAGE_MISMATCH")
        self.assertEqual(rows[3]["rejection_reason_code"],"MISSING_EVIDENCE")
        self.assertEqual(rows[3]["evidence_validation"]["evidence_state"],"missing")
        self.assertIsNone(rows[3]["evidence_validation"]["quotation_matches_extracted_text"])
        self.assertNotIn("hallucination",json.dumps(rows).lower())

    def test_omission_is_not_verified_absence(self):
        collector=self.collector()
        self.verify(collector,draft(self.c.contract))
        omission=collector.finish()["items"][1]
        self.assertEqual(omission["final_status"],"retained")
        self.assertEqual(omission["evidence_validation"]["evidence_state"],"not_applicable")
        self.assertTrue(omission["evidence_validation"]["evidence_verification_not_applicable"])
        self.assertFalse(omission["evidence_validation"]["evidence_verification_succeeded"])
        self.assertFalse(omission["final"]["evidence_verified"])
        self.assertEqual(omission["final"]["evidence_status"],"needs_review")

    def test_trace_ids_and_original_explanations_quotes_retained(self):
        collector=self.collector()
        d=draft(self.c.contract,True)
        self.verify(collector,d)
        payload,path=collector.write()
        stored=json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload,stored)
        ids=[i["item_id"] for i in stored["items"]]
        self.assertEqual(len(ids),len(set(ids)))
        self.assertTrue(all(i.startswith(collector.trace_id+":") for i in ids))
        self.assertEqual(stored["items"][1]["proposed"]["evidence_quote"],d.findings[1].evidence_quote)
        self.assertEqual(stored["items"][1]["proposed"]["explanation"],d.findings[1].explanation)
        self.assertEqual(stored["contract_id"],self.c.contract.contract_id)

    def test_stage_timings_nonnegative_nested_and_context_reset(self):
        collector=self.collector()
        with observation_scope(collector),stage("total_analysis"):
            with stage("policy_retrieval"):
                with stage("embedding_request"):
                    pass
        spans=collector.finish()["stages"]
        self.assertTrue(all(s["seconds"]>=0 for s in spans))
        self.assertEqual(spans[2]["parent_span_id"],spans[1]["span_id"])
        self.assertIsNone(_observer.get())

    def test_provider_usage_exact_not_estimated(self):
        collector=self.collector()
        self.assertEqual(collector.finish()["token_usage"]["total_tokens"],None)
        with observation_scope(collector):
            emit("usage",response=SimpleNamespace(model_version="mock-model",usage_metadata=SimpleNamespace(
                prompt_token_count=10,candidates_token_count=5,total_token_count=17)))
        usage=collector.finish()["token_usage"]
        self.assertEqual((usage["input_tokens"],usage["output_tokens"],usage["total_tokens"]),(10,5,17))
        with observation_scope(collector):
            emit("usage",response=SimpleNamespace(usage_metadata=None))
        self.assertIsNone(collector.finish()["token_usage"]["input_tokens"])

    def test_invalid_schema_event_does_not_fabricate_item_count(self):
        collector=self.collector()
        with observation_scope(collector):
            emit("structured_failure")
        payload=collector.finish()
        self.assertEqual(payload["diagnostics"][0]["reason_code"],"INVALID_SCHEMA")
        self.assertIsNone(payload["counts"]["findings"]["proposed"])
        self.assertEqual(payload["items"],[])

    def test_all_rejected_analysis_keeps_diagnostics(self):
        d=draft(self.c.contract)
        d.findings=[d.findings[0]]
        d.findings[0].evidence_quote="Invented"
        d.obligations=[]
        collector=self.collector()
        with self.assertRaises(EvidenceError):
            self.verify(collector,d)
        payload=collector.finish()
        self.assertEqual(payload["counts"]["findings"]["rejected"],1)
        self.assertEqual(payload["items"][0]["original_verifier_reason"],"quote_not_in_original_clause")

    def test_source_gate_rejects_nonfixture_and_changed_source(self):
        modified=copy.deepcopy(self.c)
        modified.contract.pages[0].text="Real customer content must not be traced."
        with self.assertRaises(ValueError):
            TraceCollector(modified,"offline",output_root=Path(self.temp.name)/"private")
        collector=self.collector()
        d=draft(self.c.contract)
        with observation_scope(collector):
            emit("proposed",draft=d,contract=modified.contract)
        self.assertTrue(collector.observation_failed)
        self.assertEqual(collector.items,[])

    def test_secret_and_common_pii_redaction(self):
        with patch.object(settings,"gemini_api_key","private-api-value"):
            text=redact("private-api-value user@example.test +1 212-555-0199 Bearer abc.defghi")
        self.assertNotIn("private-api-value",text)
        self.assertNotIn("user@example.test",text)
        self.assertNotIn("212-555-0199",text)
        self.assertNotIn("abc.defghi",text)

    def test_unknown_reason_is_not_invented(self):
        code,message=reason_details("new_unknown_reason",{})
        self.assertEqual(code,"UNKNOWN_REJECTION")
        self.assertIn("not inferred",message)

    def test_observer_failure_does_not_change_verification_result(self):
        collector=self.collector()
        with patch.object(collector,"event",side_effect=RuntimeError("do not log me")):
            observed=self.verify(collector,draft(self.c.contract))
        expected=verify_analysis(draft(self.c.contract),self.c.contract,load_playbook())
        self.assertEqual(observed,expected)
        self.assertTrue(collector.observation_failed)

    def test_acl_failure_prevents_writing_sensitive_trace(self):
        if os.name!="nt":
            self.skipTest("Windows ACL test")
        with patch("evaluation.tracing.subprocess.run",side_effect=OSError("ACL unavailable")):
            with self.assertRaises(OSError):
                self.collector()
        self.assertEqual(list(Path(self.temp.name).rglob("trace.json")),[])

    def test_run_id_cannot_escape_private_directory(self):
        with self.assertRaises(ValueError):
            TraceCollector(self.c,"../outside",output_root=Path(self.temp.name)/"private")

    def test_mocked_pipeline_partial_trace_and_timings(self):
        from evaluation.live_adapter import run_live
        from evaluation.schema import Dataset
        import evaluation.tracing as tracing
        d=load_dataset()
        d.cases=d.cases[:1]
        d.fixture_outcomes=d.fixture_outcomes[:1]
        prior=settings.storage_path
        original=TraceCollector
        def local_collector(c,run_id):
            return original(c,run_id,output_root=Path(self.temp.name)/"private")
        from app.services.policy_matching import policy_vectors
        policy_vectors.cache_clear()
        self.addCleanup(policy_vectors.cache_clear)
        response=SimpleNamespace(text=draft(self.c.contract,True).model_dump_json(),model_version="offline-mock",
            usage_metadata=SimpleNamespace(prompt_token_count=11,candidates_token_count=7,total_token_count=20))
        embedding_response=SimpleNamespace(raise_for_status=lambda:None,json=lambda:{"embeddings":[[1.0,0.2]]})
        with no_network(),patch.object(tracing,"TraceCollector",side_effect=local_collector),\
             patch.object(settings,"gemini_api_key","test-only-key"),\
             patch("app.services.ollama_embeddings.httpx.Client") as ollama,\
             patch("app.services.gemini_analysis.genai.Client") as gemini:
            ollama.return_value.__enter__.return_value.post.return_value=embedding_response
            gemini.return_value.__enter__.return_value.models.generate_content.return_value=response
            outcomes=run_live(d,trace_enabled=True,run_id="offline-mocked")
        self.assertEqual(settings.storage_path,prior)
        self.assertEqual(outcomes[0].status,"partial")
        self.assertFalse(outcomes[0].trace_observation_failed)
        trace=json.loads(Path(outcomes[0].trace_file).read_text(encoding="utf-8"))
        self.assertEqual(trace["counts"]["findings"]["proposed"],5)
        self.assertEqual(trace["counts"]["obligations"]["rejected"],1)
        for item in trace["items"]:
            if item["item_type"]=="finding" and item["retained"]:
                self.assertTrue(item["evaluation_prediction_id"].startswith("SYN-supplier_red-LIVE-"))
        stages={s["stage"] for s in trace["stages"]}
        self.assertTrue({"pdf_extraction","policy_retrieval","evidence_verification","persistence_contract",
                         "persistence_analysis","persistence_retrieval","total_analysis"}.issubset(stages))
        self.assertEqual(outcomes[0].input_tokens,11)
        self.assertEqual(outcomes[0].total_tokens,20)
        self.assertEqual(len([s for s in trace["stages"] if s["stage"]=="embedding_request"]),11)
        self.assertIn("gemini_generation",stages)

    def test_raw_text_is_private_not_printed_with_active_observer(self):
        collector=self.collector()
        output=io.StringIO()
        with contextlib.redirect_stdout(output),contextlib.redirect_stderr(output):
            self.verify(collector,draft(self.c.contract,True))
            collector.write()
        self.assertEqual(output.getvalue(),"")
        self.assertEqual(len(list(Path(self.temp.name).rglob("trace.json"))),1)

    def test_stage_hook_failure_is_observational_only(self):
        collector=self.collector()
        with patch.object(collector,"begin_stage",side_effect=RuntimeError("observer failed")):
            actual=self.verify(collector,draft(self.c.contract))
        expected=verify_analysis(draft(self.c.contract),self.c.contract,load_playbook())
        self.assertEqual(actual,expected)
        self.assertTrue(collector.observation_failed)

    def test_zero_provider_usage_is_zero_not_missing(self):
        collector=self.collector()
        with observation_scope(collector):
            emit("usage",response=SimpleNamespace(usage_metadata=SimpleNamespace(
                prompt_token_count=0,candidates_token_count=0,total_token_count=0)))
        self.assertEqual(collector.finish()["token_usage"]["total_tokens"],0)

    def test_all_reason_codes_have_honest_mapping(self):
        from evaluation.tracing import REASONS
        for original,(code,diagnostic) in REASONS.items():
            value=dict(clause_id="exists",page_number=1,evidence_quote="Text")
            mapped,message=reason_details(original,value)
            self.assertEqual(mapped,code)
            self.assertEqual(message,diagnostic)
        self.assertNotIn("DUPLICATE_FINDING",{v[0] for v in REASONS.values()})
        self.assertNotIn("UNSUPPORTED_CLAIM",{v[0] for v in REASONS.values()})

    def test_cli_trace_requires_explicit_live_flag_without_network(self):
        from evaluation.runner import main
        with no_network(),contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as raised:
                main(["--trace","--dry-run"])
        self.assertEqual(raised.exception.code,2)

    def test_real_gemini_wrapper_with_mocked_response_captures_usage(self):
        from app.services.gemini_analysis import generate_analysis
        d=draft(self.c.contract)
        response=SimpleNamespace(text=d.model_dump_json(),model_version="mock-model",
            usage_metadata=SimpleNamespace(prompt_token_count=11,candidates_token_count=7,total_token_count=20))
        collector=self.collector()
        with no_network(),observation_scope(collector),patch.object(settings,"gemini_api_key","test-only-key"),\
             patch("app.services.gemini_analysis.genai.Client") as client:
            client.return_value.__enter__.return_value.models.generate_content.return_value=response
            generated=generate_analysis(self.c.contract,load_playbook(),[])
            verify_analysis(generated,self.c.contract,load_playbook())
        payload=collector.finish()
        self.assertEqual(payload["token_usage"]["total_tokens"],20)
        self.assertTrue({"gemini_generation","structured_response_parsing"}.issubset({s["stage"] for s in payload["stages"]}))

if __name__=="__main__":
    unittest.main()
