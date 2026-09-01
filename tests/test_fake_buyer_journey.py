"""Unit Tests for Hermes Fake Buyer Journey Simulation and Replay Integration."""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from agency.bots.fake_buyer_journey import FakeBuyerJourneySimulator
from agency.core.store import Store

ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = ROOT / "fixtures"


class TestFakeBuyerJourney(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_buyer.db"
        self.store = Store(db_path=self.db_path, data_dir=Path(self.temp_dir))

        with (FIXTURES_DIR / "candidate.sample.json").open("r", encoding="utf-8") as f:
            self.candidate = json.load(f)
        self.store.save_candidate(self.candidate)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_synthetic_buyer_journey_execution(self) -> None:
        sim = FakeBuyerJourneySimulator(self.store)
        res = sim.simulate_order(
            candidate_id=self.candidate["candidate_id"],
            customer_name="Test Synthetic Buyer",
            customer_country="US",
        )

        self.assertTrue(res["order_id"].startswith("ord-syn-"))
        self.assertEqual(len(res["steps"]), 8)
        self.assertGreater(res["unit_economics"]["net_profit"], 0.0)
        self.assertTrue(res["carrier_tracking"].startswith("940011189956"))

        # Verify audit logs in Store
        logs = self.store.get_audit_trail(limit=20)
        buyer_events = [l for l in logs if l.get("event_type", "").startswith("SYNTHETIC_BUYER_")]
        self.assertEqual(len(buyer_events), 8)

        # Verify HMAC provenance exists on every step
        for step in res["steps"]:
            self.assertIn("hmac_signature", step)
            self.assertEqual(len(step["hmac_signature"]), 64)


if __name__ == "__main__":
    unittest.main()
