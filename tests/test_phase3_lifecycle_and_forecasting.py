"""Phase-3 Unit and Integration Test Suite: Lifecycle State Machine, Forecasting, Replacement Engine & Canary Scaling."""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from agency.bots.supplier_replacement_engine import SupplierReplacementEngine
from agency.core.competition_matrix import SupplierCompetitionMatrix
from agency.core.store import Store
from agency.core.supplier_forecasting import SupplierHealthForecaster
from agency.core.supplier_lifecycle import SupplierLifecycleManager, SupplierState
from agency.governance.execution_gateway import ExecutionGateway

ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = ROOT / "fixtures"


class TestPhase3LifecycleAndForecasting(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_phase3.db"
        self.store = Store(db_path=self.db_path, data_dir=Path(self.temp_dir))

        with (FIXTURES_DIR / "candidate.sample.json").open("r", encoding="utf-8") as f:
            self.candidate = json.load(f)
        self.store.save_candidate(self.candidate)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # 1. Lifecycle State Machine Transitions
    def test_lifecycle_state_machine_evaluation(self) -> None:
        # Healthy stability -> ACTIVE
        res_active = SupplierLifecycleManager.evaluate_state(stability_score=0.92, volatility_index=0.04)
        self.assertEqual(res_active["state"], SupplierState.ACTIVE.value)
        self.assertTrue(res_active["canary_permitted"])
        self.assertFalse(res_active["replacement_required"])

        # Early drift / high volatility -> WATCHLIST
        res_watch = SupplierLifecycleManager.evaluate_state(stability_score=0.82, volatility_index=0.12)
        self.assertEqual(res_watch["state"], SupplierState.WATCHLIST.value)

        # Degraded reliability -> DEGRADED
        res_degraded = SupplierLifecycleManager.evaluate_state(stability_score=0.74, volatility_index=0.08)
        self.assertEqual(res_degraded["state"], SupplierState.DEGRADED.value)

        # Critical failure -> CRITICAL
        res_crit = SupplierLifecycleManager.evaluate_state(stability_score=0.62, volatility_index=0.22)
        self.assertEqual(res_crit["state"], SupplierState.CRITICAL.value)
        self.assertFalse(res_crit["canary_permitted"])
        self.assertTrue(res_crit["replacement_required"])

        # Manual retirement
        res_ret = SupplierLifecycleManager.evaluate_state(stability_score=0.95, manual_override=SupplierState.RETIRED)
        self.assertEqual(res_ret["state"], SupplierState.RETIRED.value)
        self.assertTrue(res_ret["replacement_required"])

    # 2. Health Forecasting & Preemptive Switch
    def test_supplier_health_forecaster(self) -> None:
        # Downward trajectory: stability burning down, stock burning fast
        timeline = [
            {"ts": "2026-09-01T00:00:00Z", "stability": 0.92, "stock": 400, "product_cost": 5.0, "lead_days_max": 5},
            {"ts": "2026-09-01T04:00:00Z", "stability": 0.86, "stock": 300, "product_cost": 5.2, "lead_days_max": 5},
            {"ts": "2026-09-01T08:00:00Z", "stability": 0.78, "stock": 200, "product_cost": 5.4, "lead_days_max": 6},
        ]
        res = SupplierHealthForecaster.forecast_health(timeline)
        self.assertTrue(res["forecast_valid"])

        # Burn rate is -100 units per step. Stock 200 / 100 = 2 steps = 1 day runout
        self.assertLessEqual(res["projected_7d"]["stock_runout_days"], 7)
        self.assertEqual(res["risk_tier"], "HIGH_RISK_PREEMPTIVE_SWITCH")
        self.assertTrue(res["preemptive_switch_recommended"])

    # 3. Autonomous Supplier Replacement Engine
    def test_supplier_replacement_engine(self) -> None:
        candidate = dict(self.candidate)
        candidate["supplier_evidence"] = [
            {
                "supplier_name": "Failing Primary Hub",
                "product_url": "https://example.com/item-1",
                "quoted_product_cost": 5.00,
                "quoted_shipping_cost": 3.00,
                "warehouse_country": "US",
                "delivery_days_min": 3,
                "delivery_days_max": 5,
                "hs_code": "8504.40",
                "origin_country": "US",
                "landed_cost_confidence": "high",
            },
            {
                "supplier_name": "Healthy Domestic Backup",
                "product_url": "https://example.com/item-2",
                "quoted_product_cost": 5.50,
                "quoted_shipping_cost": 3.20,
                "warehouse_country": "US",
                "delivery_days_min": 3,
                "delivery_days_max": 5,
                "hs_code": "8504.40",
                "origin_country": "US",
                "landed_cost_confidence": "high",
            },
        ]
        self.store.save_candidate(candidate)

        # Inject verification for primary making it critical (stability 0.65)
        crit_ver = {
            "verification_id": "ver-20260901-crit-001",
            "candidate_id": candidate["candidate_id"],
            "supplier_id": "failing-primary-hub",
            "sku": "SKU-CRIT-001",
            "warehouse_country": "US",
            "warehouse_type": "domestic",
            "shipping_method": "USPS",
            "quoted_product_cost": 5.00,
            "quoted_shipping_cost": 3.00,
            "verified_product_cost": 5.00,
            "verified_shipping_cost": 3.00,
            "price_drift_percent": 0.25,
            "duty_percent": 0.0,
            "lead_days_min": 3,
            "lead_days_max": 8,
            "defect_rate_percent": 8.0,
            "stability_score": 0.65,
            "stock_level": 15,
            "packaging_type": "polybag",
            "verification_confidence": 0.95,
            "status": "DRIFT_DETECTED",
            "verified_at": "2026-09-01T08:00:00Z",
            "verified_at_unix": 1788249600,
        }
        self.store.save_supplier_verification(crit_ver)

        engine = SupplierReplacementEngine(self.store)
        res = engine.process_candidate_suppliers(candidate["candidate_id"])

        self.assertTrue(res["switch_triggered"])
        self.assertEqual(res["failover_type"], "QUALIFIED_DOMESTIC_SWITCH")
        self.assertEqual(res["replacement_supplier_id"], "healthy-domestic-backup")
        self.assertIn("sig-supplier-switch-", res["signal_id"])

        # Check that trade signal was logged in store
        saved_sig = self.store.get_signal(res["signal_id"])
        self.assertIsNotNone(saved_sig)
        self.assertEqual(saved_sig["signal_type"], "SUPPLIER_SWITCH")

    # 4. Autonomous Canary Tier Scaling
    def test_canary_dynamic_tier_scaling(self) -> None:
        gateway = ExecutionGateway(self.store)

        # Baseline (0-7 days): allows up to 3 orders / $250
        tier1 = gateway.execute_canary_order_batch(
            candidate_id="cand-001",
            supplier_id="sup-dom-01",
            stability_score=0.95,
            tier="PREFERRED_DOMESTIC",
            order_count=3,
            estimated_spend=75.0,
            consecutive_stable_days=3,
        )
        self.assertTrue(tier1["success"])
        self.assertEqual(tier1["scaling_tier"], "BASELINE_CANARY_TIER_1")

        # Scaled Tier 2 (8-21 days): allows 5 orders / $400
        tier2 = gateway.execute_canary_order_batch(
            candidate_id="cand-001",
            supplier_id="sup-dom-01",
            stability_score=0.95,
            tier="PREFERRED_DOMESTIC",
            order_count=5,
            estimated_spend=320.0,
            consecutive_stable_days=14,
        )
        self.assertTrue(tier2["success"])
        self.assertEqual(tier2["scaling_tier"], "SCALED_DOMESTIC_TIER_2")

        # Trusted Domestic Tier 3 (22+ days): allows 10 orders / $600
        tier3 = gateway.execute_canary_order_batch(
            candidate_id="cand-001",
            supplier_id="sup-dom-01",
            stability_score=0.98,
            tier="PREFERRED_DOMESTIC",
            order_count=10,
            estimated_spend=550.0,
            consecutive_stable_days=30,
        )
        self.assertTrue(tier3["success"])
        self.assertEqual(tier3["scaling_tier"], "TRUSTED_DOMESTIC_TIER_3")

        # Exceed Tier 3 cap ($600 limit): should reject
        over_cap = gateway.execute_canary_order_batch(
            candidate_id="cand-001",
            supplier_id="sup-dom-01",
            stability_score=0.98,
            tier="PREFERRED_DOMESTIC",
            order_count=12,
            estimated_spend=750.0,
            consecutive_stable_days=30,
        )
        self.assertFalse(over_cap["success"])

    # 5. Competition Matrix Generation
    def test_supplier_competition_matrix(self) -> None:
        matrix = SupplierCompetitionMatrix.generate_matrix(self.candidate["candidate_id"], self.store)
        self.assertIn("competition_matrix", matrix)
        self.assertGreaterEqual(len(matrix["competition_matrix"]), 1)
        first_row = matrix["competition_matrix"][0]
        self.assertIn("lifecycle_state", first_row)
        self.assertIn("projected_7d_stability", first_row)
        self.assertIn("stock_runout_days", first_row)


if __name__ == "__main__":
    unittest.main()
