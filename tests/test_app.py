import os
import tempfile
import unittest

from main import app, get_db


class ShamCashTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        os.environ["DATABASE_PATH"] = os.path.join(self.temp_dir.name, "test.sqlite3")
        import main
        main.DB_PATH = main.Path(os.environ["DATABASE_PATH"])
        main.initialize_database()
        app.config.update(TESTING=True, SECRET_KEY="test-secret-key")
        self.client = app.test_client()

    def tearDown(self):
        os.environ.pop("DATABASE_PATH", None)
        self.temp_dir.cleanup()

    def register(self, username="testuser", password="StrongPass123"):
        return self.client.post("/api/register", json={
            "username": username,
            "password": password,
            "name": "Test User",
            "email": "test@example.com",
        })

    def test_health_endpoint(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)

    def test_register_login_and_current_user(self):
        registered = self.register()
        self.assertEqual(registered.status_code, 201)
        self.assertEqual(registered.get_json()["user"]["balance"], 500)

        me = self.client.get("/api/me")
        self.assertEqual(me.status_code, 200)

        logout = self.client.post("/api/logout", json={})
        self.assertEqual(logout.status_code, 200)

        login = self.client.post("/api/login", json={
            "username": "testuser",
            "password": "StrongPass123",
        })
        self.assertEqual(login.status_code, 200)

    def test_transaction_rejects_invalid_amount(self):
        self.register()
        for invalid in (0, -1, True, 0.001, 100001, "not-a-number"):
            response = self.client.post("/api/transactions", json={
                "name": "Recipient",
                "amount": invalid,
            })
            self.assertEqual(response.status_code, 400)

    def test_transaction_updates_balance(self):
        self.register()
        response = self.client.post("/api/transactions", json={
            "name": "Recipient",
            "amount": 12.50,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["balance"], 487.5)

        me = self.client.get("/api/me")
        self.assertEqual(me.get_json()["user"]["balance"], 487.5)

    def test_login_required_for_private_api(self):
        self.client.post("/api/logout", json={})
        response = self.client.get("/api/me")
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
