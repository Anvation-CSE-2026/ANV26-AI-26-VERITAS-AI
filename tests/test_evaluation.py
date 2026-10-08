"""Independent evaluator tests: known examples, never provider calls."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"backend"))
from pydantic import ValidationError
from app.models.contracts import Contract, PageText, Clause
from evaluation.schema import Annotation, EvidenceSpan, Prediction, Outcome, Case, Dataset
from evaluation.evidence_metrics import check_evidence, summarize, normalize
from evaluation.risk_metrics import score_case, one_to_one, metrics
from evaluation.dataset_loader import load_dataset, validate_case
from evaluation.evaluator import evaluate
from evaluation.runner import main

TEXT="Supplier must notify Company within 8 days."
POLICY="POL-DATA-001"

def contract():
    return Contract(contract_id="TEST",filename="test.pdf",
        pages=[PageText(page_number=1,text=TEXT),PageText(page_number=2,text="Other material.")],
        clauses=[Clause(clause_id="C1",page_number=1,text=TEXT,start_offset=0,end_offset=len(TEXT))],warnings=[])

def gold(state="risk",fid="G1",category="data_protection"):
    spans=[] if state=="missing" else [EvidenceSpan(clause_id="C1",page_number=1,quote=TEXT)]
    return Annotation(contract_id="TEST",finding_id=fid,risk_category=category,
        expected_severity=None if state=="ambiguous" else "low" if state=="non_risk" else "high",
        expected_clause_text=TEXT if spans else None,expected_page_number=1 if spans else None,
        explanation="Synthetic rule comparison.",risk_present={"risk":True,"missing":True,"non_risk":False,"ambiguous":None}[state],
        annotation_state=state,annotation_confidence="medium",reviewer_status="pending_manual_review",
        policy_id=POLICY,evidence_spans=spans)

def pred(pid="P1",**kwargs):
    data=dict(prediction_id=pid,risk_category="data_protection",severity="high",
              evidence_quote=TEXT,page_number=1,clause_id="C1",policy_id=POLICY)
    data.update(kwargs)
    return Prediction(**data)

def dataset(annotations=None):
    return Dataset(dataset_id="test",version="1",cases=[Case(contract=contract(),
        annotations=annotations if annotations is not None else [gold()],pdf_path="unused")],
        policy_ids=[POLICY],fixture_outcomes=[])

class EvidenceMetricTests(unittest.TestCase):
    def check(self,p):
        return check_evidence(p,contract(),{POLICY})

    def test_exact_match(self):
        r=self.check(pred())
        self.assertTrue(r["supported"])
        self.assertTrue(r["exact_match"])
        self.assertTrue(r["correct_page"])

    def test_whitespace_normalized_match_not_production_verified(self):
        r=self.check(pred(evidence_quote=TEXT.replace(" ","\n")))
        self.assertFalse(r["exact_match"])
        self.assertTrue(r["normalized_match"])
        self.assertTrue(r["normalized_correct_page"])
        self.assertFalse(r["supported"])
        self.assertEqual(normalize(" A\t B\nC "),"A B C")

    def test_wrong_page_keeps_quote_existence_separate(self):
        r=self.check(pred(page_number=2))
        self.assertTrue(r["exact_match"])
        self.assertFalse(r["correct_page"])
        self.assertIn("wrong_page",r["reasons"])

    def test_fabricated_quote(self):
        r=self.check(pred(evidence_quote="Supplier guarantees perfection."))
        self.assertFalse(r["normalized_match"])
        self.assertIn("fabricated_quote",r["reasons"])

    def test_missing_fields_and_nonexistent_page_or_clause(self):
        r=self.check(pred(evidence_quote=None,page_number=None,clause_id=None,policy_id=None))
        self.assertEqual(set(r["reasons"]),{"unknown_or_missing_policy","empty_or_missing_quote","missing_page","missing_clause"})
        r=self.check(pred(page_number=999,clause_id="UNKNOWN"))
        self.assertIn("nonexistent_page",r["reasons"])
        self.assertIn("nonexistent_clause",r["reasons"])

    def test_missing_clause_has_no_fabricated_evidence(self):
        r=self.check(pred(finding_status="missing",evidence_quote=None,page_number=None,clause_id=None))
        self.assertTrue(r["supported"])
        self.assertFalse(r["quote_eligible"])
        self.assertTrue(r["omission_not_confirmed"])
        self.assertIsNone(summarize([r])["exact_quote_match_rate"])
        bad=self.check(pred(finding_status="missing"))
        self.assertIn("fabricated_evidence_for_omission",bad["reasons"])

    def test_evidence_counts_each_record_once_despite_multiple_errors(self):
        r=self.check(pred(evidence_quote="",page_number=999,clause_id="NO"))
        s=summarize([r],rejected_finding_count=1)
        self.assertEqual(s["unsupported_evidence_count"],2)
        self.assertEqual(s["evidence_verification_failure_rate"],1)

class RiskMetricTests(unittest.TestCase):
    def test_duplicate_prediction_one_to_one(self):
        s=score_case([pred("P1"),pred("P2")],[gold()])
        self.assertEqual((s["detection"]["tp"],s["detection"]["fp"],s["detection"]["fn"]),(1,1,0))

    def test_one_prediction_cannot_match_two_gold(self):
        s=score_case([pred()],[gold(fid="G1"),gold(fid="G2")])
        self.assertEqual(s["detection"]["tp"],1)
        self.assertEqual(s["detection"]["fn"],1)

    def test_missing_expected_risk(self):
        s=score_case([],[gold()])
        self.assertEqual(s["detection"]["fn"],1)
        self.assertIsNone(s["detection"]["precision"])
        self.assertEqual(s["detection"]["recall"],0)

    def test_false_positive_on_non_risk(self):
        s=score_case([pred()],[gold("non_risk")])
        self.assertEqual(s["detection"]["fp"],1)
        self.assertEqual(s["non_risk_false_positives"],["P1"])

    def test_ambiguous_separate_and_duplicates_not_all_ignored(self):
        s=score_case([pred("P1"),pred("P2")],[gold("ambiguous")])
        self.assertEqual(s["detection"]["tp"],0)
        self.assertEqual(s["detection"]["fp"],1)
        self.assertEqual(len(s["ambiguous_predictions_excluded"]),1)
        self.assertEqual(s["ambiguous_gold_count"],1)

    def test_category_and_severity_separate_from_detection(self):
        s=score_case([pred(risk_category="liability",severity="medium")],[gold()])
        self.assertEqual(s["detection"]["tp"],1)
        self.assertEqual(s["per_category"]["data_protection"]["fn"],1)
        self.assertEqual(s["per_category"]["liability"]["fp"],1)
        self.assertFalse(s["matches"][0]["category_correct"])
        self.assertFalse(s["matches"][0]["severity_correct"])

    def test_quote_existence_does_not_override_reviewed_negative(self):
        self.assertTrue(check_evidence(pred(),contract(),{POLICY})["supported"])
        self.assertEqual(score_case([pred()],[gold("non_risk")])["detection"]["fp"],1)

    def test_omission_matches_policy_only_without_quote(self):
        p=pred(finding_status="missing",evidence_quote=None,page_number=None,clause_id=None)
        self.assertEqual(score_case([p],[gold("missing")])["detection"]["tp"],1)
        p.policy_id="WRONG"
        self.assertEqual(score_case([p],[gold("missing")])["detection"]["fn"],1)

    def test_zero_denominators(self):
        m=metrics(0,0,0)
        self.assertIsNone(m["precision"])
        self.assertIsNone(m["recall"])
        self.assertIsNone(m["f1"])

    def test_maximum_cardinality_avoids_greedy_matching_loss(self):
        a=gold(fid="A"); b=gold(fid="B")
        b.evidence_spans=[EvidenceSpan(clause_id="C2",page_number=2,quote="Different quote")]
        flexible=pred("F",evidence_quote="Different quote",page_number=2)
        specific=pred("S")
        self.assertEqual(len(one_to_one([flexible,specific],[a,b])),2)

class DatasetAndAggregationTests(unittest.TestCase):
    def test_dataset_validation_and_pdf_roundtrip(self):
        d=load_dataset()
        self.assertEqual(len(d.cases),12)
        self.assertEqual(sum(len(c.annotations) for c in d.cases),42)
        self.assertIn("governing_law",{g.risk_category for c in d.cases for g in c.annotations})
        for c in d.cases:
            validate_case(c,set(d.policy_ids))

    def test_missing_pdf_pages(self):
        c=Case(contract=contract(),annotations=[gold()],pdf_path="unused")
        c.contract.pages[1].page_number=3
        with self.assertRaisesRegex(ValueError,"Missing"):
            validate_case(c,{POLICY})

    def test_invalid_schema_and_fabricated_gold(self):
        data=gold().model_dump()
        data["risk_present"]=False
        with self.assertRaises(ValidationError):
            Annotation.model_validate(data)
        data=gold("missing").model_dump()
        data["expected_clause_text"]="Invented"
        with self.assertRaises(ValidationError):
            Annotation.model_validate(data)
        c=Case(contract=contract(),annotations=[gold()],pdf_path="unused")
        c.annotations[0].evidence_spans[0].quote="Invented"
        with self.assertRaises(ValueError):
            validate_case(c,{POLICY})

    def test_empty_dataset(self):
        d=Dataset(dataset_id="empty",version="1",cases=[],policy_ids=[],fixture_outcomes=[])
        s=evaluate(d,[])
        self.assertEqual(s["dataset_size"],0)
        self.assertIsNone(s["micro_f1"])
        self.assertIsNone(s["macro_f1"])
        self.assertIsNone(s["evidence"]["unsupported_evidence_rate"])
        self.assertIsNone(s["average_processing_seconds"])

    def test_partial_and_failed_analyses_keep_false_negatives(self):
        d=dataset([gold(),gold(fid="G2")])
        s=evaluate(d,[Outcome(contract_id="TEST",status="partial",predictions=[pred()],rejected_finding_count=1)])
        self.assertEqual(s["detection"]["fn"],1)
        self.assertEqual(s["reliability"]["partial"],1)
        self.assertEqual(s["evidence"]["unsupported_evidence_count"],1)
        s=evaluate(d,[Outcome(contract_id="TEST",status="failed",error_category="synthetic_failure")])
        self.assertEqual(s["detection"]["fn"],2)
        self.assertEqual(s["reliability"]["failed"],1)

    def test_missing_outcome_not_silently_dropped(self):
        with self.assertRaises(ValueError):
            evaluate(dataset(),[])
        with self.assertRaises(ValidationError):
            Outcome(contract_id="TEST",status="failed",predictions=[pred()])

    def test_multiple_findings_and_cross_page_target(self):
        d=load_dataset()
        split=next(c for c in d.cases if c.contract.contract_id=="SYN-services_split")
        self.assertEqual(len(split.annotations[0].evidence_spans),2)
        o=next(o for o in d.fixture_outcomes if o.contract_id==split.contract.contract_id)
        scored=score_case(o.predictions,split.annotations)
        self.assertEqual(scored["detection"]["tp"],1)
        self.assertEqual(len(scored["matches"]),1)
        self.assertTrue(check_evidence(o.predictions[0],split.contract,set(d.policy_ids))["supported"])

    def test_fixture_counts_are_computed_and_stable(self):
        d=load_dataset()
        s=evaluate(d,d.fixture_outcomes)
        self.assertEqual(s["annotated_risks"],24)
        self.assertEqual((s["detection"]["tp"],s["detection"]["fp"],s["detection"]["fn"]),(17,3,7))
        self.assertEqual(s["reliability"]["failed"],1)
        self.assertEqual(s["reliability"]["partial"],1)
        self.assertIsNone(s["input_tokens"])
        self.assertIsNone(s["estimated_cost_usd"])
        self.assertIsNone(s["average_processing_seconds"])

    def test_report_cli_offline_does_not_call_network_or_import_live_adapter(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch("socket.socket.connect",side_effect=AssertionError("Network forbidden")), patch("socket.create_connection",side_effect=AssertionError("Network forbidden")):
                self.assertEqual(main(["--dataset","synthetic_v1","--output",temp]),0)
            data=json.loads((Path(temp)/"synthetic_v1-fixture.json").read_text(encoding="utf-8"))
            self.assertFalse(data["metadata"]["live_services_used"])
            self.assertIsNone(data["metadata"]["model_identifier"])
            self.assertTrue(data["metadata"]["prompt_sha256"])
            self.assertEqual(len(list(Path(temp).glob("*"))),3)
            self.assertNotIn("evaluation.live_adapter",sys.modules)

    def test_csv_includes_evidence_reliability_and_missing_ids(self):
        import csv
        from evaluation.runner import write_reports, metadata
        d=load_dataset()
        with tempfile.TemporaryDirectory() as temp:
            paths=write_reports(dict(metadata=metadata(d,"fixture"),summary=evaluate(d,d.fixture_outcomes)),Path(temp))
            with paths[1].open(encoding="utf-8",newline="") as f:
                rows=list(csv.DictReader(f))
            metrics_present={r["metric"] for r in rows}
            self.assertIn("unsupported_evidence_count",metrics_present)
            self.assertIn("estimated_cost_usd",metrics_present)
            self.assertIn("failed",metrics_present)
            self.assertTrue(any(r["scope"]=="missed_gold" for r in rows))
            self.assertTrue(any(r["scope"]=="unmatched_prediction" for r in rows))

    def test_network_guard_blocks_external_and_ollama_connections(self):
        import socket
        from evaluation.offline_guard import no_network
        with no_network():
            with self.assertRaises(AssertionError):
                socket.create_connection(("localhost",11434))
            with socket.socket() as s:
                with self.assertRaises(AssertionError):
                    s.connect(("127.0.0.1",11434))

    def test_network_guard_allows_asyncio_internal_socketpair(self):
        import asyncio
        from evaluation.offline_guard import no_network
        async def local():
            return 7
        with no_network():
            self.assertEqual(asyncio.run(local()),7)

    def test_manifest_integrity_detects_tampering(self):
        from evaluation.dataset_loader import FIXTURES
        import shutil
        with tempfile.TemporaryDirectory() as temp:
            dest=Path(temp)/"fixtures"
            shutil.copytree(FIXTURES,dest)
            (dest/"predictions.json").write_text("[]",encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"integrity"):
                load_dataset(fixtures_root=dest)

    def test_confusion_and_supported_detection(self):
        s=evaluate(dataset(),[Outcome(contract_id="TEST",status="completed",
            predictions=[pred(evidence_quote="Invented",risk_category="payment",severity="medium")])])
        self.assertEqual(s["detection"]["tp"],1)
        self.assertEqual(s["supported_evidence_detection"]["tp"],0)
        self.assertEqual(s["supported_evidence_detection"]["fn"],1)
        self.assertEqual(s["category_confusion"],[dict(gold="data_protection",predicted="payment",count=1)])

if __name__=="__main__":
    unittest.main()
