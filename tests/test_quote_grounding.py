"""Offline regression: whitespace-only evidence recovery, never fuzzy acceptance."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path[:0] = [str(Path(__file__).resolve().parents[1] / 'backend'), str(Path(__file__).parent)]
from app.config import settings
from app.models.contracts import AnalysisDraft
from app.services.contract_analysis import analyze_contract
from app.services.evidence import EvidenceError, verify_analysis
from app.services.gemini_analysis import SYSTEM_INSTRUCTION
from app.services.playbook import load_playbook
from app.services.storage import save_contract, get_contract, get_failure, get_analysis
from test_contract_analysis import source, valid_draft

class QuoteGroundingTests(unittest.TestCase):
    def setUp(self):
        self.contract = source()
        self.book = load_playbook()
        self.draft = valid_draft(self.contract)

    def verify(self, draft):
        return verify_analysis(draft, self.contract, self.book)

    def finding_only(self):
        d = self.draft.model_copy(deep=True)
        d.obligations = []
        return d

    def test_exact_quotes_and_json_roundtrip_preserved(self):
        parsed = AnalysisDraft.model_validate_json(self.draft.model_dump_json())
        self.assertEqual(parsed.findings[0].evidence_quote, self.draft.findings[0].evidence_quote)
        self.assertEqual(self.verify(parsed)[2], [])

    def test_pdf_newlines_and_unicode_whitespace_restore_exact_source(self):
        for separator in [' ', '\r\n', '\t', '\u00a0']:
            d = self.finding_only()
            original = d.findings[0].evidence_quote
            self.assertIn('\n', original)
            d.findings[0].evidence_quote = original.replace('\n', separator)
            proposed = d.findings[0].evidence_quote
            accepted, _, rejected = self.verify(d)
            self.assertEqual(rejected, [])
            self.assertEqual(accepted[0].evidence_quote, original)
            self.assertEqual(accepted[0].source_facts.evidence_quote, original)
            self.assertEqual(d.findings[0].evidence_quote, proposed)  # Raw proposal not mutated.

    def test_obligation_quote_newlines_restore_source(self):
        d = self.draft.model_copy(deep=True)
        d.findings = []
        original = d.obligations[0].evidence_quote
        d.obligations[0].evidence_quote = original.replace('\n', ' ')
        _, obligations, rejected = self.verify(d)
        self.assertEqual(rejected, [])
        self.assertEqual(obligations[0].evidence_quote, original)

    def test_incorrect_ids_pages_and_offsets_still_rejected(self):
        for field, value, reason in [('clause_id','invented','unknown_clause_id'),('page_number',99,'wrong_page_number')]:
            d = self.finding_only()
            setattr(d.findings[0],field,value)
            with self.assertRaises(EvidenceError) as caught: self.verify(d)
            self.assertEqual(caught.exception.rejections[0].reason,reason)
        broken = self.contract.model_copy(deep=True)
        clause = next(c for c in broken.clauses if c.clause_id == self.draft.findings[0].clause_id)
        clause.start_offset += 1
        with self.assertRaises(EvidenceError) as caught:
            verify_analysis(self.finding_only(),broken,self.book)
        self.assertEqual(caught.exception.rejections[0].reason,'source_offset_mismatch')

    def test_other_clause_quote_is_not_reassigned_even_if_unique(self):
        d = self.finding_only()
        d.findings[0].evidence_quote = self.draft.obligations[0].evidence_quote.replace('\n',' ')
        with self.assertRaises(EvidenceError) as caught: self.verify(d)
        self.assertEqual(caught.exception.rejections[0].reason,'quote_not_in_original_clause')

    def test_paraphrases_punctuation_case_and_token_changes_fail(self):
        for quote in ['Supplier has a small cap on its liability.', self.draft.findings[0].evidence_quote.lower(), self.draft.findings[0].evidence_quote.replace('100','101'), self.draft.findings[0].evidence_quote.replace('.','!')]:
            d = self.finding_only(); d.findings[0].evidence_quote=quote
            with self.assertRaises(EvidenceError): self.verify(d)

    def test_mixed_supported_and_unsupported_stay_partial(self):
        good = self.draft.findings[0].model_copy(deep=True)
        good.evidence_quote = good.evidence_quote.replace('\n',' ')
        bad = good.model_copy(update={'evidence_quote':'An invented promise.'})
        d = AnalysisDraft(findings=[good,bad],obligations=[])
        findings, _, rejected = self.verify(d)
        self.assertEqual(len(findings),1)
        self.assertEqual(len(rejected),1)
        self.assertEqual(rejected[0].evidence_status,'unsupported')
        with tempfile.TemporaryDirectory() as folder, patch.object(settings,'storage_path',Path(folder)/'test.sqlite3'), patch('app.services.contract_analysis.match_policies',return_value=[]), patch('app.services.contract_analysis.generate_analysis',return_value=d) as generate:
            result = analyze_contract(self.contract)
            self.assertEqual(result.status,'partial')
            self.assertEqual(len(result.findings),1)
            generate.assert_called_once()

    def test_total_failure_preserves_upload_saves_only_failure_and_does_not_retry(self):
        d = self.draft.model_copy(deep=True)
        d.findings[0].evidence_quote = 'Unsupported finding.'
        d.obligations[0].evidence_quote = 'Unsupported obligation.'
        with tempfile.TemporaryDirectory() as folder, patch.object(settings,'storage_path',Path(folder)/'test.sqlite3'), patch('app.services.contract_analysis.match_policies',return_value=[]), patch('app.services.contract_analysis.generate_analysis',return_value=d) as generate:
            save_contract(self.contract,b'%PDF-synthetic-fixture')
            with self.assertRaises(EvidenceError) as caught: analyze_contract(self.contract)
            exc = caught.exception
            self.assertTrue(exc.failure_recorded)
            self.assertEqual(len(exc.rejections),2)
            self.assertIsNone(get_analysis(exc.analysis_id))
            self.assertEqual(get_failure(exc.analysis_id).failed_stage,'evidence_verification')
            self.assertEqual(get_contract(self.contract.contract_id),self.contract)
            self.assertIn('uploaded contract is preserved',str(exc))
            generate.assert_called_once()

    def test_omission_never_promoted_to_verified_quote(self):
        item=self.draft.findings[0].model_copy(update={'finding_status':'missing','clause_id':None,'page_number':None,'evidence_quote':None})
        findings, _, _ = self.verify(AnalysisDraft(findings=[item],obligations=[]))
        self.assertFalse(findings[0].evidence_verified)
        self.assertFalse(findings[0].absence_confirmed)
        self.assertEqual(findings[0].evidence_status,'needs_review')

    def test_prompt_requires_verbatim_clause_evidence(self):
        self.assertIn('Every evidence quotation must be copied verbatim',SYSTEM_INSTRUCTION)
        self.assertIn('Do not paraphrase, summarize or invent evidence',SYSTEM_INSTRUCTION)
        self.assertIn('contract_clauses[].text',SYSTEM_INSTRUCTION)
