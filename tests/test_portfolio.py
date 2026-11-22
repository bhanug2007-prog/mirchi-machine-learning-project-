from datetime import datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.portfolio import IST, create_portfolio_router


class PortfolioTest(unittest.TestCase):
    def test_private_inventory_and_fresh_target_alerts(self):
        today = datetime.now(IST).date()

        def quote_lookup(market, variety):
            quote_date = today if variety == "Red New" else today - timedelta(days=5)
            return {"modal_price": 18000, "date": quote_date.isoformat()}

        with TemporaryDirectory() as directory:
            app = FastAPI()
            app.include_router(create_portfolio_router(quote_lookup, sqlite_path=Path(directory) / "test.db"))
            with TestClient(app) as client:
                self.check_portfolio(client, today)

    def check_portfolio(self, client, today):
        root = "/api/portfolio"

        def create_account(username):
            credentials = {"username": username, "password": "synthetic-test-password"}
            self.assertEqual(client.post(f"{root}/register", json=credentials).status_code, 201)
            self.assertEqual(client.post(f"{root}/register", json=credentials).status_code, 409)
            response = client.post(f"{root}/login", json=credentials)
            self.assertEqual(response.headers["Cache-Control"], "no-store")
            return {"Authorization": "Bearer " + response.json()["token"]}

        first, second = create_account("first"), create_account("second")
        self.assertEqual(client.get(root).status_code, 401)
        lot = {
            "variety": "Red New", "market": "Guntur APMC", "location": "Inkolllu", "quintals": 50,
            "target_price": 18000, "storage_type": "Cold storage", "storage_rate": 30,
            "stored_since": (today - timedelta(days=12)).isoformat(),
        }
        created = client.post(f"{root}/lots", json=lot, headers=first)
        self.assertEqual(created.status_code, 201, created.text)
        endpoint = f"{root}/lots/{created.json()['id']}"
        self.assertEqual(client.get(root, headers=second).json(), {"lots": [], "alerts": []})
        self.assertEqual(client.put(endpoint, json=lot, headers=second).status_code, 404)
        self.assertEqual(client.delete(endpoint, headers=second).status_code, 404)

        for _ in range(2):
            result = client.get(root, headers=first).json()
            self.assertEqual(len(result["alerts"]), 1)
            self.assertEqual(result["lots"][0]["storage_cost"], 18000)
            self.assertEqual(result["lots"][0]["market_value"], 900000)

        self.assertEqual(client.put(endpoint, json={**lot, "variety": "Red"}, headers=first).status_code, 200)
        result = client.get(root, headers=first).json()
        self.assertEqual([alert["variety"] for alert in result["alerts"]], ["Red New"])
        self.assertFalse(result["lots"][0]["quote_fresh"])
        self.assertEqual(client.delete(endpoint, headers=first).status_code, 200)
        self.assertEqual(client.get(root, headers=first).json(), {"lots": [], "alerts": []})
        self.assertEqual(client.post(f"{root}/logout", headers=first).status_code, 200)
        self.assertEqual(client.get(root, headers=first).status_code, 401)
