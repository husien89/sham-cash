import os
import tempfile
import unittest

from main import app, initialize_database, Path


class ShamCashTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        import main
        main.DB_PATH = Path(os.environ.get("DATABASE_PATH", self.temp_dir.name)) / "test.sqlite3"
        main.initialize_database()
        app.config.update(TESTING=True, SECRET_KEY="test-secret-key")
        self.client = app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def register(self, username="testuser", password="StrongPass123", name="Test User"):
        return self.client.post("/api/register", json={
            "username": username,
            "password": password,
            "name": name,
            "email": "test@example.com",
        })

    def test_health_endpoint(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)

    def test_register_login_and_current_user(self):
        registered = self.register()
        self.assertEqual(registered.status_code, 201)
        self.assertEqual(registered.get_json()["user"]["balance"], 500)
        self.assertEqual(self.client.get("/api/me").status_code, 200)

        self.client.post("/api/logout", json={})
        login = self.client.post("/api/login", json={"username": "testuser", "password": "StrongPass123"})
        self.assertEqual(login.status_code, 200)

    def test_invalid_amounts_are_rejected(self):
        self.register()
        for invalid in (0, -1, True, 0.001, 100001, "not-a-number", None):
            response = self.client.post("/api/transactions", json={"recipient": "recipient", "amount": invalid})
            self.assertEqual(response.status_code, 400)

    def test_atomic_wallet_transfer(self):
        self.register("sender", name="Sender")
        self.client.post("/api/logout", json={})
        self.register("recipient", name="Recipient")

        self.client.post("/api/logout", json={})
        self.client.post("/api/login", json={"username": "sender", "password": "StrongPass123"})
        response = self.client.post("/api/transactions", json={"recipient": "recipient", "amount": 12.50})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["balance"], 487.5)

        me = self.client.get("/api/me")
        self.assertEqual(me.get_json()["user"]["balance"], 487.5)

        self.client.post("/api/logout", json={})
        self.client.post("/api/login", json={"username": "recipient", "password": "StrongPass123"})
        me = self.client.get("/api/me")
        self.assertEqual(me.get_json()["user"]["balance"], 512.5)

    def test_login_required_for_private_api(self):
        self.client.post("/api/logout", json={})
        response = self.client.get("/api/me")
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
