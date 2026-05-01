import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch
from app import create_app

class MetricsApiTests(unittest.TestCase):

    def setUp(self):
        self.app = create_app(testing=True)
        self.client = self.app.test_client()

    def test_home_route(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["message"], "Monitoring API is running")

    def test_health_route(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "healthy")

    def test_post_metrics_without_json(self):
        response = self.client.post("/metrics")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "No JSON data received")

    def test_post_metrics_missing_fields(self):
        response = self.client.post("/metrics", json={
            "device_name": "monserver01",
            "cpu_usage": 10
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing fields", response.get_json()["error"])

    @patch("app.routes.get_db_connection")
    def test_post_metrics_success(self, mock_get_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1, datetime(2026, 4, 30, 18, 0, 0))

        mock_get_connection.return_value = mock_conn

        response = self.client.post("/metrics", json={
            "device_name": "monserver01",
            "cpu_usage": 10.5,
            "memory_usage": 40.2,
            "disk_usage": 60.1,
            "status": "OK"
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["device_name"], "monserver01")
        self.assertEqual(response.get_json()["status"], "OK")

    @patch("app.routes.get_db_connection")
    def test_get_metrics_success(self, mock_get_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            (1, "monserver01", 10.5, 40.2, 60.1, "OK", datetime(2026, 4, 30, 18, 0, 0))
        ]

        mock_get_connection.return_value = mock_conn

        response = self.client.get("/metrics")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()[0]["device_name"], "monserver01")
        self.assertEqual(response.get_json()[0]["status"], "OK")

if __name__ == "__main__":
    unittest.main()