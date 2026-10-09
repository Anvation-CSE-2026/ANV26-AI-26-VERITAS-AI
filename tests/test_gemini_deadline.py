"""Mocked deadline tests; no provider/network calls."""
import sys,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock,patch
import httpx
from google.genai import errors
sys.path[:0]=[str(Path(__file__).resolve().parents[1]/'backend'),str(Path(__file__).parent)]
from app.config import settings
from app.services.gemini_analysis import generate_analysis,GeminiError
from app.services.contract_analysis import analyze_contract
from app.services.playbook import load_playbook
from app.services.storage import save_contract,get_contract,get_failure,get_analysis
from test_contract_analysis import source,valid_draft

class GeminiDeadlineTests(unittest.TestCase):
    def setUp(self):
        self.contract=source();self.book=load_playbook()
        self.factory=MagicMock()
        self.client=self.factory.return_value.__enter__.return_value

    def test_timeout_ms_and_sdk_retry_limit_no_clause_truncation(self):
        self.client.models.generate_content.return_value=SimpleNamespace(text=valid_draft(self.contract).model_dump_json())
        with patch.object(settings,'gemini_api_key','offline-test-key'),patch.object(settings,'gemini_timeout_seconds',180),patch.object(settings,'gemini_max_attempts',1),patch('app.services.gemini_analysis.genai.Client',self.factory):
            result=generate_analysis(self.contract,self.book,[])
        options=self.factory.call_args.kwargs['http_options']
        self.assertEqual(options.timeout,180000)
        self.assertEqual(options.retry_options.attempts,1)
        self.assertEqual(result._gemini_attempts,1)
        self.client.models.generate_content.assert_called_once()
        import json
        payload=json.loads(self.client.models.generate_content.call_args.kwargs['contents'])
        self.assertEqual(payload['contract_clauses'],[c.model_dump() for c in self.contract.clauses])

    def test_upstream_504_and_transport_timeout_one_attempt_no_sleep(self):
        for error in [errors.APIError(504,{}),httpx.ReadTimeout('provider timeout')]:
            with self.subTest(kind=type(error).__name__):
                self.client.models.generate_content.reset_mock()
                self.client.models.generate_content.side_effect=error
                with patch.object(settings,'gemini_api_key','offline-test-key'),patch.object(settings,'gemini_max_attempts',1),patch('app.services.gemini_analysis.genai.Client',self.factory),patch('app.services.gemini_analysis.time.sleep') as sleep:
                    with self.assertRaises(GeminiError) as caught:generate_analysis(self.contract,self.book,[])
                self.assertEqual(caught.exception.status_code,504)
                self.assertEqual(caught.exception.category,'timeout')
                self.assertEqual(caught.exception.attempts,1)
                self.assertIn('uploaded contract is preserved',str(caught.exception))
                self.client.models.generate_content.assert_called_once();sleep.assert_not_called()

    def test_timeout_failure_persisted_upload_retained_no_success_saved(self):
        self.client.models.generate_content.side_effect=errors.APIError(504,{})
        with tempfile.TemporaryDirectory() as folder,patch.object(settings,'database_url',''),patch.object(settings,'storage_path',Path(folder)/'test.sqlite3'),patch.object(settings,'gemini_api_key','offline-test-key'),patch.object(settings,'gemini_max_attempts',1),patch('app.services.contract_analysis.match_policies',return_value=[]),patch('app.services.gemini_analysis.genai.Client',self.factory):
            save_contract(self.contract,b'%PDF-offline-fixture')
            with self.assertRaises(GeminiError) as caught:analyze_contract(self.contract)
            exc=caught.exception
            self.assertTrue(exc.failure_recorded)
            self.assertEqual(get_failure(exc.analysis_id).error_category,'timeout')
            self.assertFalse(get_failure(exc.analysis_id).retries_occurred)
            self.assertIsNone(get_analysis(exc.analysis_id))
            self.assertEqual(get_contract(self.contract.contract_id),self.contract)
            self.client.models.generate_content.assert_called_once()
