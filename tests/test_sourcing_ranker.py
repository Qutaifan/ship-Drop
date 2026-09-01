"""Unit and integration test suite for Hermes Sourcing Ranker and Canary Gateway."""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from agency.bots.trader_bot import TraderBot
from agency.core.sourcing_ranker import (
    SourcingRanker,
    calculate_actionability_score,
    determine_supplier_tier,
)
from agency.core.store import Store
from agency.governance.execution_gateway import ExecutionGateway

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS_DIR = ROOT / "schemas"
FIXTURES_DIR = ROOT / "fixtures"


class TestSourcingRanker(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_ranker.db"
        self.store = Store(db_path=self.db_path, data_dir=Path(self.temp_dir))

        # Seed candidate
        with (FIXTURES_DIR / "candidate.sample.json").open("r", encoding="utf-8") as f:
            self.candidate = json.load(f)
        self.store.save_candidate(self.candidate)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _load_json(self, p: Path) -> dict:
        with p.open("r", encoding="utf-8") as f:
            return json.load(f)

    # 1. Actionability score math
    def test_actionability_score_math(self) -> None:
        # High stability (0.95), low margin delta ($0.20 on $30 retail)
        low_act = calculate_actionability_score(stability_score=0.95, margin_delta=-0.20, retail_price=30.0, severity="LOW")
        self.assertLess(low_act, 10.0)

        # Degraded stability (0.30), large margin drop ($6.00 on $30 retail), HIGH severity
        high_act = calculate_actionability_score(stability_score=0.30, margin_delta=-6.00, retail_price=30.0, severity="HIGH")
        self.assertGreater(high_act, 80.0)

    # 2. Tier classification
    def test_determine_supplier_tier(self) -> None:
        # Preferred domestic: stability 0.95, lead 4d, defect 1.2%, margin $15, stock 250
        tier_pref = determine_supplier_tier(
            stability=0.95,
            metrics={"stock_level": 250, "lead_days_max": 4, "defect_rate_percent": 1.2, "projected_net_margin": 15.0},
            is_domestic=True,
            reconciliation_status="MARGIN_STABLE",
        )
        self.assertEqual(tier_pref, "PREFERRED_DOMESTIC")

        # Qualified backup: stability 0.78, lead 6d, margin $11, stock 150
        tier_backup = determine_supplier_tier(
            stability=0.78,
            metrics={"stock_level": 150, "lead_days_max": 6, "defect_rate_percent": 2.0, "projected_net_margin": 11.0},
            is_domestic=True,
            reconciliation_status="MARGIN_STABLE",
        )
        self.assertEqual(tier_backup, "QUALIFIED_BACKUP")

        # High risk monitor: international transit
        tier_monitor = determine_supplier_tier(
            stability=0.60,
            metrics={"stock_level": 500, "lead_days_max": 14, "defect_rate_percent": 3.0, "projected_net_margin": 12.0},
            is_domestic=False,
            reconciliation_status="MARGIN_STABLE",
        )
        self.assertEqual(tier_monitor, "HIGH_RISK_MONITOR")

    # 3. Margin compression automatic rejection
    def test_margin_compression_rejection(self) -> None:
        # User's exact compression case: retail 39.99, net margin $8.12 (< $10), compression_flag = True
        tier_compressed = determine_supplier_tier(
            stability=0.88,
            metrics={"stock_level": 300, "lead_days_max": 4, "defect_rate_percent": 1.0, "projected_net_margin": 8.12},
            is_domestic=True,
            reconciliation_status="MARGIN_COMPRESSED",
        )
        self.assertEqual(tier_compressed, "REJECTED_UNVIABLE")

        # Stock depleted (< 30 units) rejection
        tier_stockout = determine_supplier_tier(
            stability=0.90,
            metrics={"stock_level": 12, "lead_days_max": 4, "defect_rate_percent": 1.0, "projected_net_margin": 15.0},
            is_domestic=True,
            reconciliation_status="MARGIN_STABLE",
        )
        self.assertEqual(tier_stockout, "REJECTED_UNVIABLE")

    # 4. SourcingRanker ranking output & Schema Validation
    def test_sourcing_ranker_schema_compliance(self) -> None:
        candidate = dict(self.candidate)
        candidate["supplier_evidence"] = [
            {
                "supplier_name": "CJ US Domestic East Hub",
                "supplier_id": "cj-us-domestic-east",
                "warehouse_country": "US",
                "warehouse_type": "domestic",
                "quoted_product_cost": 5.50,
                "quoted_shipping_cost": 3.20,
                "shipping_method": "USPS",
                "lead_days_min": 3,
                "lead_days_max": 5,
                "defect_rate_percent": 1.1,
                "stock_level": 400,
            },
            {
                "supplier_name": "Shenzhen Transit Factory",
                "supplier_id": "shenzhen-factory-direct",
                "warehouse_country": "CN",
                "warehouse_type": "international_transit",
                "quoted_product_cost": 4.00,
                "quoted_shipping_cost": 4.80,
                "shipping_method": "CN ePacket",
                "lead_days_min": 10,
                "lead_days_max": 16,
                "defect_rate_percent": 3.2,
                "stock_level": 2000,
            },
        ]

        res = SourcingRanker.rank_candidate_suppliers(candidate)
        schema = self._load_json(SCHEMAS_DIR / "sourcing_ranker.schema.json")
        validator = Draft202012Validator(schema)
        errors = list(validator.iter_errors(res))
        self.assertEqual(errors, [], f"Sourcing ranker output failed schema validation: {errors}")

        self.assertEqual(res["suppliers"][0]["supplier_id"], "cj-us-domestic-east")
        self.assertEqual(res["suppliers"][0]["tier"], "PREFERRED_DOMESTIC")
        self.assertTrue(res["suppliers"][0]["canary_eligible"])
        self.assertEqual(res["suppliers"][1]["tier"], "HIGH_RISK_MONITOR")
        self.assertFalse(res["suppliers"][1]["canary_eligible"])

    # 5. TraderBot integration with SourcingRanker
    def test_trader_bot_sourcing_rank_payload(self) -> None:
        bot = TraderBot(self.store)
        sig = bot.generate_recommendation(self.candidate["candidate_id"])
        self.assertIsNotNone(sig)

        self.assertIn("sourcing_rank", sig)
        s_rank = sig["sourcing_rank"]
        self.assertIn(s_rank["tier"], ["PREFERRED_DOMESTIC", "QUALIFIED_BACKUP", "HIGH_RISK_MONITOR", "REJECTED_UNVIABLE"])
        self.assertGreaterEqual(s_rank["stability"], 0.0)
        self.assertGreaterEqual(s_rank["actionability"], 0.0)

        # Validate signal against trade_signal.schema.json
        schema = self._load_json(SCHEMAS_DIR / "trade_signal.schema.json")
        validator = Draft202012Validator(schema)
        errors = list(validator.iter_errors(sig))
        self.assertEqual(errors, [], f"Trade signal failed schema validation: {errors}")

    # 6. ExecutionGateway Canary Order Batch Logic
    def test_execution_gateway_canary_order_batch(self) -> None:
        gateway = ExecutionGateway(self.store)

        # Allowed canary order: PREFERRED_DOMESTIC, stability 0.92, 3 orders, $60 spend
        allowed = gateway.execute_canary_order_batch(
            candidate_id="sample-candidate",
            supplier_id="cj-us-domestic",
            stability_score=0.92,
            tier="PREFERRED_DOMESTIC",
            order_count=3,
            estimated_spend=60.0,
        )
        self.assertTrue(allowed["success"])
        self.assertTrue(allowed["canary_permitted"])
        self.assertEqual(allowed["order_count"], 3)

        # Rejected canary order: tier is HIGH_RISK_MONITOR
        rejected_tier = gateway.execute_canary_order_batch(
            candidate_id="sample-candidate",
            supplier_id="cn-transit-supplier",
            stability_score=0.90,
            tier="HIGH_RISK_MONITOR",
            order_count=3,
            estimated_spend=60.0,
        )
        self.assertFalse(rejected_tier["success"])
        self.assertFalse(rejected_tier["canary_permitted"])

        # Rejected canary order: spend cap exceeded (> $250)
        rejected_spend = gateway.execute_canary_order_batch(
            candidate_id="sample-candidate",
            supplier_id="cj-us-domestic",
            stability_score=0.95,
            tier="PREFERRED_DOMESTIC",
            order_count=10,
            estimated_spend=350.0,
        )
        self.assertFalse(rejected_spend["success"])
        self.assertFalse(rejected_spend["canary_permitted"])


if __name__ == "__main__":
    unittest.main()
