"""Phase-6 Test Suite: CJdropshipping Domestic Warehouse Live Telemetry Ingestion."""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from agency.bots.supplier_volatility_tracker import SupplierVolatilityTracker
from agency.core.demand_forecasting import DemandForecastingEngine
from agency.core.store import Store
from agency.core.supplier_forecasting import SupplierHealthForecaster
from agency.core.supplier_lifecycle import SupplierLifecycleManager, SupplierState
from agency.ingestion.cj_inventory_ingestion import CJInventoryIngestionPipeline

ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = ROOT / "fixtures"


class TestPhase6CJInventoryIngestion(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_phase6_cj.db"
        self.store = Store(db_path=self.db_path, data_dir=Path(self.temp_dir))

        with (FIXTURES_DIR / "candidate.sample.json").open("r", encoding="utf-8") as f:
            self.candidate = json.load(f)
        self.store.save_candidate(self.candidate)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # 1. Schema-Compliant Normalization & Verification Storage
    def test_cj_telemetry_normalization_and_store(self) -> None:
        rec = CJInventoryIngestionPipeline.ingest_and_verify(
            candidate_id=self.candidate["candidate_id"],
            supplier_id="cj-dropshipping-us-domestic-hub",
            sku="SKU-MAGNETIC-01",
            quoted_product_cost=6.50,
            quoted_shipping_cost=3.50,
            country="US",
        )

        self.assertTrue(rec["verification_id"].startswith("ver-"))
        self.assertEqual(rec["warehouse_country"], "US")
        self.assertEqual(rec["warehouse_type"], "domestic")
        self.assertEqual(rec["shipping_method"], "USPS")
        self.assertEqual(rec["duty_percent"], 0.0)
        self.assertGreaterEqual(rec["stability_score"], 0.85)
        self.assertEqual(rec["status"], "VERIFIED_PASS")
        self.assertIn("hmac_signature", rec)

        # Ensure Store successfully validates against supplier_verification.schema.json without errors
        self.store.save_supplier_verification(rec)
        saved = self.store.list_supplier_verifications(candidate_id=self.candidate["candidate_id"])
        self.assertEqual(len(saved), 1)
        self.assertEqual(saved[0]["verification_id"], rec["verification_id"])

    # 2. Volatility Tracking Across Shifting CJ Telemetry
    def test_cj_volatility_tracking_with_depleting_inventory(self) -> None:
        cid = self.candidate["candidate_id"]
        sid = "cj-dropshipping-us-domestic-hub"

        # Audit 1: Healthy stock 400, lead 4 days, cost $6.00
        audit1 = CJInventoryIngestionPipeline.ingest_and_verify(
            candidate_id=cid, supplier_id=sid, sku="SKU-MAGNETIC-01",
            quoted_product_cost=6.00, override_stock=400, override_lead_max=4, override_product_cost=6.00,
        )
        audit1["verified_at"] = "2026-09-01T00:00:00Z"
        audit1["verified_at_unix"] = 1788220800
        self.store.save_supplier_verification(audit1)

        # Audit 2: Rapid burn down to 150 units, lead times up to 6 days
        audit2 = CJInventoryIngestionPipeline.ingest_and_verify(
            candidate_id=cid, supplier_id=sid, sku="SKU-MAGNETIC-01",
            quoted_product_cost=6.00, override_stock=150, override_lead_max=6, override_product_cost=6.00,
        )
        audit2["verified_at"] = "2026-09-01T04:00:00Z"
        audit2["verified_at_unix"] = 1788235200
        self.store.save_supplier_verification(audit2)

        tracker = SupplierVolatilityTracker(self.store)
        analysis = tracker.analyze_supplier(supplier_id=sid, candidate_id=cid)

        # Stock burn: 400 - 150 = -250 units
        self.assertLess(analysis["volatility_curves"]["stock_velocity_units_per_audit"], 0.0)
        self.assertEqual(analysis["volatility_curves"]["lead_time_inflation_days"], 2)

    # 3. Supplier Lifecycle State Transitions from Real CJ Drift
    def test_cj_lifecycle_degradation_transition(self) -> None:
        # CJ reports 30% price drift and delivery blowing out to 9 days
        drift_rec = CJInventoryIngestionPipeline.ingest_and_verify(
            candidate_id=self.candidate["candidate_id"],
            supplier_id="cj-dropshipping-us-domestic-hub",
            sku="SKU-MAGNETIC-01",
            quoted_product_cost=5.00,
            override_product_cost=6.80,  # +36% drift
            override_lead_max=9,
            override_stock=25,
        )

        self.assertEqual(drift_rec["status"], "DRIFT_DETECTED")
        self.assertLess(drift_rec["stability_score"], 0.70)

        # Evaluate lifecycle state machine
        state_eval = SupplierLifecycleManager.evaluate_state(
            stability_score=drift_rec["stability_score"],
            current_state=SupplierState.ACTIVE,
        )

        self.assertEqual(state_eval["state"], SupplierState.CRITICAL.value)
        self.assertFalse(state_eval["canary_permitted"])
        self.assertTrue(state_eval["replacement_required"])

    # 4. Inventory Runway Forecasting when CJ Stock Shifts
    def test_cj_runway_forecasting(self) -> None:
        # Healthy 350 stock
        f_healthy = DemandForecastingEngine.forecast_demand(
            daily_ad_spend=50.0,
            cpc=0.85,
            predicted_cvr_percent=2.0,
            current_stock=350,
            lead_time_days=4,
        )
        self.assertGreaterEqual(f_healthy["inventory_runway_days"], 50)
        self.assertFalse(f_healthy["reorder_needed"])

        # Low stock of 5 units
        f_depleted = DemandForecastingEngine.forecast_demand(
            daily_ad_spend=50.0,
            cpc=0.85,
            predicted_cvr_percent=2.0,
            current_stock=5,
            lead_time_days=4,
        )
        self.assertLessEqual(f_depleted["inventory_runway_days"], 10)
        self.assertTrue(f_depleted["reorder_needed"])


if __name__ == "__main__":
    unittest.main()
