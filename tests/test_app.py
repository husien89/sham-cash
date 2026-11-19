import os
import tempfile
import unittest
from pathlib import Path

import main
from main import app


class ShamCashTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_db_path = main.DB_PATH
        main.DB_PATH = Path(self.temp_dir.name) / "test.sqlite3"
        main.initialize_database()
        app.config.update(TESTING=True, SECRET_KEY="test-secret-key")
        self.client = app.test_client()

    def tearDown(self):
        main.DB_PATH = self.original_db_path
        self.temp_dir.cleanup()

    def register(self, username="testuser", password="StrongPass123", name="Test User"):
        return self.client.post("/api/register", json={
            "username": username,
            "password": password,
            "name": name,
            "email": "test@example.com",
        })

    def test_health_and_login_flow(self):
        self.assertEqual(self.client.get("/api/health").status_code, 200)
        registered = self.register()
        self.assertEqual(registered.status_code, 201)
        self.assertEqual(registered.get_json()["user"]["balance"], 500)
        self.assertEqual(self.client.get("/api/me").status_code, 200)

        self.client.post("/api/logout", json={})
        login = self.client.post("/api/login", json={"username": "testuser", "password": "StrongPass123"})
        self.assertEqual(login.status_code, 200)

    def test_invalid_amounts_and_recipients_are_rejected(self):
        self.register()
        for invalid in (0, -1, True, 0.001, 100001, "not-a-number", None, float("nan"), float("inf")):
            response = self.client.post("/api/transactions", json={"recipient": "recipient", "amount": invalid})
            self.assertEqual(response.status_code, 400)
        self.assertEqual(self.client.post("/api/transactions", json={"recipient": "missing", "amount": 2}).status_code, 404)
        self.assertEqual(self.client.post("/api/transactions", json={"recipient": "testuser", "amount": 2}).status_code, 400)

    def test_transfer_is_atomic_and_appears_in_both_histories(self):
        self.register("sender", name="Sender")
        self.client.post("/api/logout", json={})
        self.register("recipient", name="Recipient")

        self.client.post("/api/logout", json={})
        self.client.post("/api/login", json={"username": "sender", "password": "StrongPass123"})
        response = self.client.post("/api/transactions", json={"recipient": "recipient", "amount": 12.50})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["balance"], 487.5)
        self.assertEqual(self.client.get("/api/transactions").get_json()["transactions"][0]["direction"], "out")

        self.client.post("/api/logout", json={})
        self.client.post("/api/login", json={"username": "recipient", "password": "StrongPass123"})
        self.assertEqual(self.client.get("/api/me").get_json()["user"]["balance"], 512.5)
        self.assertEqual(self.client.get("/api/transactions").get_json()["transactions"][0]["direction"], "in")

    def test_cross_origin_mutation_is_rejected(self):
        response = self.client.post(
            "/api/register",
            json={"username": "testuser", "password": "StrongPass123", "name": "Test"},
            headers={"Origin": "https://attacker.example"},
        )
        self.assertEqual(response.status_code, 403)

    def test_private_api_requires_authentication(self):
        response = self.client.get("/api/me")
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
