import unittest
from fastapi.testclient import TestClient
from backend.app import app

class TestFeedstockAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health(self):
        res = self.client.get('/api/health')
        self.assertEqual(res.status_code, 200)
        self.assertIn('status', res.json())

    def test_samples_list(self):
        res = self.client.get('/api/samples')
        self.assertEqual(res.status_code, 200)
        self.assertGreater(len(res.json()), 0)

    def test_sample_inspection(self):
        samples = self.client.get('/api/samples').json()
        target = samples[0]['filename']
        res = self.client.post(f'/api/inspect/sample/{target}')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn('verdict', data)
        self.assertIn('visualizations', data)

    def test_analytics(self):
        res = self.client.get('/api/analytics')
        self.assertEqual(res.status_code, 200)
        self.assertIn('model_performance', res.json())

    def test_history_and_csv(self):
        res = self.client.get('/api/history')
        self.assertEqual(res.status_code, 200)
        csv_res = self.client.get('/api/report/csv')
        self.assertEqual(csv_res.status_code, 200)

if __name__ == '__main__':
    unittest.main()
