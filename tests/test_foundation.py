import sys
import unittest
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
from app.main import app


class FoundationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://test')

    async def asyncTearDown(self):
        await self.client.aclose()

    async def test_health_contract_and_no_secrets(self):
        response = await self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'status': 'ok', 'service': 'VERITAS AI',
            'version': '0.1.0', 'environment': 'development',
        })

    async def test_allowed_cors_preflight(self):
        response = await self.client.options('/health', headers={
            'Origin': 'http://localhost:5173',
            'Access-Control-Request-Method': 'GET',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['access-control-allow-origin'], 'http://localhost:5173')

    async def test_unapproved_origin(self):
        response = await self.client.options('/health', headers={
            'Origin': 'https://unapproved.example',
            'Access-Control-Request-Method': 'GET',
        })
        self.assertEqual(response.status_code, 400)
        self.assertNotIn('access-control-allow-origin', response.headers)


if __name__ == '__main__':
    unittest.main()
