"""Phase-6 Test Suite: Hermes Desktop Telemetry API Bridge & UI Data Hydration."""
from __future__ import annotations

import json
import shutil
import tempfile
import threading
import time
import urllib.request
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path

from agency.api.server import HermesAPIHandler
from agency.core.store import Store

ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = ROOT / "fixtures"


class TestHermesDesktopBridge(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp_dir = tempfile.mkdtemp()
        cls.db_path = Path(cls.temp_dir) / "test_desktop.db"
        cls.store = Store(db_path=cls.db_path, data_dir=Path(cls.temp_dir))

        with (FIXTURES_DIR / "candidate.sample.json").open("r", encoding="utf-8") as f:
            cls.candidate = json.load(f)
        cls.store.save_candidate(cls.candidate)

        # Point handler to test store
        HermesAPIHandler.store = cls.store

        # Start live test server on ephemeral port
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), HermesAPIHandler)
        cls.port = cls.server.server_address[1]
        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()
        time.sleep(0.1)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        shutil.rmtree(cls.temp_dir, ignore_errors=True)

    def _get(self, path: str) -> dict:
        url = f"http://127.0.0.1:{self.port}{path}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            self.assertEqual(resp.status, 200)
            return json.loads(resp.read().decode("utf-8"))

    def _post(self, path: str, payload: dict) -> dict:
        url = f"http://127.0.0.1:{self.port}{path}"
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            self.assertEqual(resp.status, 200)
            return json.loads(resp.read().decode("utf-8"))

    # 1. Overview Telemetry & 5 Intelligence Rings
    def test_telemetry_overview_endpoint(self) -> None:
        data = self._get("/api/v1/telemetry/overview")
        self.assertIn("intelligence_rings", data)
        self.assertIn("system_vitals", data)

        rings = data["intelligence_rings"]
        self.assertIn("ring_1_stability", rings)
        self.assertIn("ring_2_volatility", rings)
        self.assertIn("ring_3_lifecycle", rings)
        self.assertIn("ring_4_network", rings)
        self.assertIn("ring_5_economic", rings)

        vitals = data["system_vitals"]
        self.assertGreater(vitals["monthly_gross_revenue"], 0.0)
        self.assertGreater(vitals["blended_cogs_multiple"], 1.0)

    # 2. SKU Intelligence Grid
    def test_sourcing_skus_endpoint(self) -> None:
        data = self._get("/api/v1/sourcing/skus")
        self.assertIn("skus", data)
        self.assertGreaterEqual(data["sku_count"], 1)

    # 3. 3D Network Graph
    def test_network_graph_endpoint(self) -> None:
        data = self._get("/api/v1/network/graph")
        self.assertIn("nodes", data)
        self.assertIn("edges", data)

    # 4. Economic Brain Portfolio
    def test_economic_portfolio_endpoint(self) -> None:
        data = self._get("/api/v1/economic/portfolio?budget=2000.0")
        self.assertIn("portfolio_monthly_gross_revenue", data)
        self.assertIn("portfolio_monthly_net_margin", data)
        self.assertEqual(data["total_monthly_marketing_budget"], 2000.0)

    # 5. Autonomous Window Grant & Revocation Loop
    def test_autonomous_window_grant_and_revoke(self) -> None:
        # Grant window
        grant_res = self._post("/api/v1/governance/window/grant", {"actor": "Founder", "hours": 1.5, "spend_cap": 250.0})
        win_id = grant_res["window_id"]
        self.assertTrue(win_id.startswith("win-"))

        # Check list
        wins_data = self._get("/api/v1/governance/windows")
        self.assertGreaterEqual(len(wins_data["active_windows"]), 1)

        # Revoke window
        revoke_res = self._post("/api/v1/governance/window/revoke", {"window_id": win_id})
        self.assertTrue(revoke_res["success"])

    # 6. Replay Log Feed
    def test_replay_log_endpoint(self) -> None:
        data = self._get("/api/v1/telemetry/replay")
        self.assertIn("events", data)


if __name__ == "__main__":
    unittest.main()
