"""Comprehensive test suite for Phase 1 (Schemas) and Phase 2 (Core Foundation: SQLite Store & Pure Scoring Engine)."""
from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from agency.bots.trader_bot import TraderBot
from agency.config.settings import Settings
from agency.core.scoring_engine import (
    final_score,
    profit_score,
    risk_score,
    supplier_score,
    trend_score,
    visibility_score,
)
from agency.core.store import Store
from agency.governance.approval_ledger import ApprovalLedger
from agency.governance.execution_gateway import ExecutionGateway
from agency.governance.policy_engine import PolicyEngine

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS_DIR = ROOT / "schemas"
FIXTURES_DIR = ROOT / "fixtures"


class TestAgencySystem(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_dropship.db"
        self.store = Store(db_path=self.db_path, data_dir=Path(self.temp_dir))
        self.policy = PolicyEngine(self.store)
        self.ledger = ApprovalLedger(self.store)
        self.gateway = ExecutionGateway(self.store, self.policy, self.ledger)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _load_json(self, p: Path) -> dict:
        with p.open("r", encoding="utf-8") as f:
            return json.load(f)

    # ══════════════════════════════════════════════════════════════════════════
    # PHASE 1: CONTRACTS (SCHEMAS)
    # ══════════════════════════════════════════════════════════════════════════

    def test_supplier_schema(self) -> None:
        schema = self._load_json(SCHEMAS_DIR / "supplier.schema.json")
        sample = self._load_json(FIXTURES_DIR / "supplier.sample.json")
        validator = Draft202012Validator(schema)
        errors = list(validator.iter_errors(sample))
        self.assertEqual(errors, [], f"supplier.sample.json failed schema validation: {errors}")
        self.assertEqual(sample.get("version"), "1.0.0")

    def test_signal_schema(self) -> None:
        schema = self._load_json(SCHEMAS_DIR / "trade_signal.schema.json")
        sample = self._load_json(FIXTURES_DIR / "trade_signal.sample.json")
        validator = Draft202012Validator(schema)
        errors = list(validator.iter_errors(sample))
        self.assertEqual(errors, [], f"trade_signal.sample.json failed schema validation: {errors}")
        self.assertEqual(sample.get("version"), "1.0.0")
        self.assertIn(sample["signal_type"], ["BUY", "SELL_KILL", "SUPPLIER_SWITCH", "TREND_ALERT"])

    def test_approval_schema(self) -> None:
        schema = self._load_json(SCHEMAS_DIR / "approval.schema.json")
        sample = self._load_json(FIXTURES_DIR / "approval.sample.json")
        validator = Draft202012Validator(schema)
        errors = list(validator.iter_errors(sample))
        self.assertEqual(errors, [], f"approval.sample.json failed schema validation: {errors}")
        self.assertEqual(sample.get("version"), "1.0.0")
        self.assertEqual(sample["approved_by"], "Ahmad")
        self.assertEqual(len(sample["verification_hash"]), 64)

    # ══════════════════════════════════════════════════════════════════════════
    # PHASE 2: PURE SCORING ENGINE TESTS (NO SIDE EFFECTS, NO DB, NO APIS)
    # ══════════════════════════════════════════════════════════════════════════

    def test_profit_score(self) -> None:
        # Gross $29.99, Cost $6.00, Shipping $3.20, Net Margin $17.54
        res = profit_score(
            gross_price=29.99,
            product_cost=6.00,
            shipping_cost=3.20,
            net_margin=17.54,
            currency="USD",
        )
        self.assertIsInstance(res, dict)
        self.assertGreaterEqual(res["score"], 60.0)
        self.assertGreaterEqual(res["cogs_multiple"], 1.9)
        self.assertGreaterEqual(res["cac_multiple"], 1.4)
        self.assertEqual(res["net_margin"], 17.54)

        # Failure case: negative net margin
        bad_res = profit_score(gross_price=10.0, product_cost=8.0, shipping_cost=4.0, net_margin=-2.0)
        self.assertEqual(bad_res["score"], 0.0)

    def test_risk_score(self) -> None:
        # Safe domestic candidate without electronics or breakables
        safe_res = risk_score(has_domestic_warehouse=True, is_electronics=False, is_fragile=False)
        self.assertEqual(safe_res["score"], 10.0)
        self.assertEqual(safe_res["safety_score"], 90.0)

        # Risky candidate: China direct + electronics + fragile + apparel sizing
        high_risk_res = risk_score(
            has_domestic_warehouse=False,
            is_electronics=True,
            is_fragile=True,
            is_apparel=True,
            compliance_unknowns_count=2,
        )
        self.assertGreater(high_risk_res["score"], 70.0)
        self.assertLess(high_risk_res["safety_score"], 30.0)
        self.assertTrue(len(high_risk_res["risk_flags"]) >= 4)

    def test_trend_score(self) -> None:
        # Healthy competition (8 competitors) + low skeptic ratio (15%)
        strong_trend = trend_score(competitor_count=8, has_social_momentum=True, has_search_momentum=True, skeptic_ratio=0.15)
        self.assertGreaterEqual(strong_trend["score"], 80.0)

        # High skepticism penalty (65% skeptic ratio)
        skeptic_trend = trend_score(competitor_count=8, skeptic_ratio=0.65)
        self.assertLess(skeptic_trend["score"], 60.0)

    def test_supplier_score(self) -> None:
        # Prime US domestic warehouse
        prime_sup = supplier_score(
            processing_days=1,
            shipping_max_days=5,
            avg_shipping_cost=4.80,
            reliability_rating=4.8,
            dispute_rate_percent=1.0,
            is_domestic=True,
            is_tracked=True,
        )
        self.assertGreaterEqual(prime_sup["score"], 85.0)

        # Slow international fulfillment with high dispute rate
        slow_sup = supplier_score(
            processing_days=4,
            shipping_max_days=18,
            avg_shipping_cost=16.00,
            reliability_rating=3.2,
            dispute_rate_percent=6.5,
            is_domestic=False,
        )
        self.assertLess(slow_sup["score"], 50.0)

    def test_visibility_score(self) -> None:
        # High profit, low risk, high trend, high supplier
        vis = visibility_score(p_score=85.0, r_score=15.0, t_score=80.0, s_score=90.0)
        self.assertGreaterEqual(vis["score"], 80.0)
        self.assertFalse(vis["hard_gate_tripped"])

        # Hard gate trigger: profit score < 40
        vis_gated = visibility_score(p_score=25.0, r_score=15.0, t_score=80.0, s_score=90.0)
        self.assertTrue(vis_gated["hard_gate_tripped"])
        self.assertLessEqual(vis_gated["score"], 45.0)

    def test_final_score(self) -> None:
        p = profit_score(29.99, 6.0, 3.20, 17.54)
        r = risk_score(has_domestic_warehouse=True)
        t = trend_score(competitor_count=7, skeptic_ratio=0.18)
        s = supplier_score(1, 5, 4.80, 4.8, 1.0, is_domestic=True)

        fin = final_score(p, r, t, s)
        self.assertIn(fin["verdict"], ["PRIME_OPPORTUNITY", "VIABLE"])
        self.assertGreaterEqual(fin["opportunity_score"], 70.0)
        self.assertEqual(fin["profit_score"], p["score"])

    # ══════════════════════════════════════════════════════════════════════════
    # PHASE 2: SQLITE STORE & REPOSITORY TESTS
    # ══════════════════════════════════════════════════════════════════════════

    def test_sqlite_connection(self) -> None:
        self.assertTrue(self.db_path.exists())
        with self.store._get_connection() as conn:
            tables = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
            for expected in ["candidates", "suppliers", "signals", "approvals", "audit_log"]:
                self.assertIn(expected, tables)

    def test_candidate_repository(self) -> None:
        candidate_data = self._load_json(FIXTURES_DIR / "candidate.sample.json")
        saved_file = self.store.save_candidate(candidate_data)
        self.assertTrue(saved_file.exists())

        # Retrieve from SQLite
        loaded = self.store.get_candidate("sample-candidate")
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["product_name"], "Sample Product Fixture")

        # List
        all_cands = self.store.list_candidates()
        self.assertEqual(len(all_cands), 1)

        # Delete
        self.assertTrue(self.store.delete_candidate("sample-candidate"))
        self.assertIsNone(self.store.get_candidate("sample-candidate"))

    def test_supplier_repository(self) -> None:
        supplier_data = self._load_json(FIXTURES_DIR / "supplier.sample.json")
        self.store.save_supplier(supplier_data)

        loaded = self.store.get_supplier("cj-us-warehouse-01")
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["supplier_name"], "CJ Dropshipping US East Warehouse")

        self.assertEqual(len(self.store.list_suppliers()), 1)
        self.assertTrue(self.store.delete_supplier("cj-us-warehouse-01"))
        self.assertIsNone(self.store.get_supplier("cj-us-warehouse-01"))

    def test_signal_repository(self) -> None:
        signal_data = self._load_json(FIXTURES_DIR / "trade_signal.sample.json")
        self.store.save_signal(signal_data)

        loaded = self.store.get_signal("sig-buy-magnetic-cable-organizer")
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["signal_type"], "BUY")

        buys = self.store.list_signals(signal_type="BUY")
        self.assertEqual(len(buys), 1)
        self.assertTrue(self.store.delete_signal("sig-buy-magnetic-cable-organizer"))

    def test_approval_repository(self) -> None:
        approval_data = self._load_json(FIXTURES_DIR / "approval.sample.json")
        self.store.save_approval(approval_data)

        loaded = self.store.get_approval("appr-20260901-test-launch-01")
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["approved_by"], "Ahmad")
        self.assertEqual(loaded["status"], "APPROVED")

        self.assertTrue(self.store.delete_approval("appr-20260901-test-launch-01"))

    def test_audit_queries(self) -> None:
        self.store.log_audit("TEST_EVENT", {"param": "value1"})
        self.store.log_audit("TEST_EVENT", {"param": "value2"})
        self.store.log_audit("OTHER_EVENT", {"param": "value3"})

        trail = self.store.get_audit_trail(limit=10)
        self.assertEqual(len(trail), 3)

        filtered = self.store.get_audit_trail(limit=10, event_type="TEST_EVENT")
        self.assertEqual(len(filtered), 2)

    # ══════════════════════════════════════════════════════════════════════════
    # PHASE 3: GOVERNANCE & EXECUTION GATEWAY TESTS
    # ══════════════════════════════════════════════════════════════════════════

    def test_policy_block(self) -> None:
        # Tier 4 action without approval MUST be blocked
        permitted, reason = self.policy.is_action_permitted("ad_spend", "scout_bot", None)
        self.assertFalse(permitted)
        self.assertIn("requires explicit approval from Ahmad", reason)

    def test_policy_allow(self) -> None:
        # Tier 0 and Tier 1 read actions are permitted autonomously
        permitted, _ = self.policy.is_action_permitted("web_search", "scout_bot")
        self.assertTrue(permitted)

    def test_ledger_append(self) -> None:
        req = self.ledger.create_approval_request(
            action="test_campaign_launch",
            object_id="test-obj",
            requested_by="trader_bot",
            market_config_id="us-pilot",
            max_budget=200.0,
            currency="USD",
            constraints=["Test constraint"],
        )
        self.assertIn("approval_id", req)
        self.assertTrue(self.ledger.verify_hash(req))

    def test_execution_gateway(self) -> None:
        req = self.ledger.create_approval_request(
            action="test_campaign_launch",
            object_id="test-obj",
            requested_by="trader_bot",
            market_config_id="us-pilot",
            max_budget=200.0,
            currency="USD",
            constraints=["Test constraint"],
        )
        exec_res = self.gateway.execute_live_action(
            action="test_campaign_launch",
            object_id="test-obj",
            requested_by="trader_bot",
            requested_spend=150.0,
            approval_id=req["approval_id"],
        )
        self.assertTrue(exec_res["success"])
        self.assertFalse(exec_res["blocked"])


if __name__ == "__main__":
    unittest.main()
