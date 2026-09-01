"""Unit and integration tests for Multi-Supplier Allocation and Volatility Tracking."""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from agency.bots.supplier_volatility_tracker import SupplierVolatilityTracker
from agency.core.sourcing_ranker import SourcingRanker
from agency.core.store import Store
from agency.core.supplier_allocator import SupplierAllocator

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS_DIR = ROOT / "schemas"
FIXTURES_DIR = ROOT / "fixtures"


class TestSupplierAllocationAndVolatility(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_alloc.db"
        self.store = Store(db_path=self.db_path, data_dir=Path(self.temp_dir))

        with (FIXTURES_DIR / "candidate.sample.json").open("r", encoding="utf-8") as f:
            self.candidate = json.load(f)
        self.store.save_candidate(self.candidate)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # 1. Dual-source resilient allocation (80/20)
    def test_multi_supplier_allocation_80_20(self) -> None:
        suppliers = [
            {"supplier_id": "primary-hub", "tier": "PREFERRED_DOMESTIC"},
            {"supplier_id": "backup-hub", "tier": "QUALIFIED_BACKUP"},
            {"supplier_id": "china-direct", "tier": "HIGH_RISK_MONITOR"},
        ]
        res = SupplierAllocator.compute_allocation(suppliers)
        self.assertEqual(res["status"], "ALLOCATION_HEALTHY")
        self.assertTrue(res["redundancy_active"])
        self.assertEqual(res["allocations"]["primary-hub"], 80.0)
        self.assertEqual(res["allocations"]["backup-hub"], 20.0)
        self.assertEqual(res["allocations"]["china-direct"], 0.0)
        self.assertEqual(res["strategy"], "DUAL_SOURCE_RESILIENT_80_20")

    # 2. Single supplier 100% allocation
    def test_single_supplier_allocation_100(self) -> None:
        suppliers = [
            {"supplier_id": "primary-hub", "tier": "PREFERRED_DOMESTIC"},
            {"supplier_id": "china-direct", "tier": "HIGH_RISK_MONITOR"},
        ]
        res = SupplierAllocator.compute_allocation(suppliers)
        self.assertEqual(res["status"], "ALLOCATION_HEALTHY")
        self.assertFalse(res["redundancy_active"])
        self.assertEqual(res["allocations"]["primary-hub"], 100.0)
        self.assertEqual(res["allocations"]["china-direct"], 0.0)

    # 3. All unviable blocked
    def test_all_unviable_allocation_blocked(self) -> None:
        suppliers = [
            {"supplier_id": "china-direct", "tier": "HIGH_RISK_MONITOR"},
            {"supplier_id": "depleted-hub", "tier": "REJECTED_UNVIABLE"},
        ]
        res = SupplierAllocator.compute_allocation(suppliers)
        self.assertEqual(res["status"], "ALLOCATION_BLOCKED")
        self.assertIsNone(res["primary_supplier_id"])
        self.assertEqual(res["allocations"]["china-direct"], 0.0)

    # 4. Volatility tracking & timeline generation
    def test_volatility_tracking_and_timeline(self) -> None:
        cid = self.candidate["candidate_id"]
        sup_id = "test-volatile-supplier"

        base_ver = {
            "warehouse_country": "US",
            "warehouse_type": "domestic",
            "shipping_method": "USPS",
            "quoted_product_cost": 5.00,
            "quoted_shipping_cost": 3.50,
            "verified_shipping_cost": 3.50,
            "price_drift_percent": 0.0,
            "duty_percent": 0.0,
            "lead_days_min": 3,
            "defect_rate_percent": 1.0,
            "packaging_type": "polybag",
            "verification_confidence": 0.95,
        }

        ver1 = {
            **base_ver,
            "verification_id": "ver-20260901-test-001",
            "candidate_id": cid,
            "supplier_id": sup_id,
            "sku": "SKU-TEST-001",
            "stability_score": 0.95,
            "stock_level": 300,
            "verified_product_cost": 5.00,
            "lead_days_max": 5,
            "status": "VERIFIED_PASS",
            "verified_at": "2026-09-01T00:00:00Z",
            "verified_at_unix": 1788220800,
        }
        ver2 = {
            **base_ver,
            "verification_id": "ver-20260901-test-002",
            "candidate_id": cid,
            "supplier_id": sup_id,
            "sku": "SKU-TEST-001",
            "stability_score": 0.90,
            "stock_level": 270,
            "verified_product_cost": 5.20,
            "lead_days_max": 5,
            "status": "VERIFIED_PASS",
            "verified_at": "2026-09-01T04:00:00Z",
            "verified_at_unix": 1788235200,
        }
        ver3 = {
            **base_ver,
            "verification_id": "ver-20260901-test-003",
            "candidate_id": cid,
            "supplier_id": sup_id,
            "sku": "SKU-TEST-001",
            "stability_score": 0.72,  # Dropped below 0.75
            "stock_level": 210,
            "verified_product_cost": 5.80,
            "lead_days_max": 7,
            "status": "DRIFT_DETECTED",
            "verified_at": "2026-09-01T08:00:00Z",
            "verified_at_unix": 1788249600,
        }

        self.store.save_supplier_verification(ver1)
        self.store.save_supplier_verification(ver2)
        self.store.save_supplier_verification(ver3)

        tracker = SupplierVolatilityTracker(self.store)
        res = tracker.analyze_supplier(supplier_id=sup_id, candidate_id=cid)

        curves = res["volatility_curves"]
        self.assertAlmostEqual(curves["stability_drift"], -0.23, places=2)
        self.assertGreater(curves["volatility_index"], 0.10)
        self.assertEqual(res["sample_count"], 3)

        # Governance rule: stability 0.72 < 0.75 -> switch recommended!
        gov = res["governance"]
        self.assertTrue(gov["switch_recommended"])
        self.assertTrue(gov["canary_blocked"])
        self.assertIn("dropped below 0.75", gov["switch_reason"])

        # Timeline artifact existence
        timeline_file = ROOT / "data" / "supplier_health" / f"{sup_id}.timeline.json"
        self.assertTrue(timeline_file.exists())

    # 5. Governance switch proposal generation
    def test_emit_supplier_switch_proposal(self) -> None:
        tracker = SupplierVolatilityTracker(self.store)
        sig = tracker.emit_supplier_switch_proposal(
            candidate_id=self.candidate["candidate_id"],
            degraded_supplier_id="flapping-primary-hub",
            replacement_supplier_id="stable-backup-hub",
            reason="Stability dropped to 0.71 (<0.75 floor)",
        )
        self.assertEqual(sig["signal_type"], "SUPPLIER_SWITCH")
        self.assertEqual(sig["action_plan"]["suggested_supplier_id"], "stable-backup-hub")
        self.assertIn("sourcing_rank", sig)

        # Validate against trade_signal.schema.json
        with (SCHEMAS_DIR / "trade_signal.schema.json").open("r", encoding="utf-8") as f:
            schema = json.load(f)
        validator = Draft202012Validator(schema)
        errors = list(validator.iter_errors(sig))
        self.assertEqual(errors, [], f"Switch signal failed schema: {errors}")

    # 6. Sourcing Ranker Multi-Supplier Allocation Integration
    def test_sourcing_ranker_multi_allocation_integration(self) -> None:
        candidate = dict(self.candidate)
        candidate["supplier_evidence"] = [
            {
                "supplier_name": "Primary US Domestic East",
                "supplier_id": "primary-us-east",
                "warehouse_country": "US",
                "warehouse_type": "domestic",
                "quoted_product_cost": 5.50,
                "quoted_shipping_cost": 3.20,
                "shipping_method": "USPS",
                "lead_days_min": 3,
                "lead_days_max": 5,
                "defect_rate_percent": 1.0,
                "stock_level": 500,
            },
            {
                "supplier_name": "Qualified Backup West",
                "supplier_id": "backup-us-west",
                "warehouse_country": "US",
                "warehouse_type": "domestic",
                "quoted_product_cost": 6.00,
                "quoted_shipping_cost": 3.50,
                "shipping_method": "UPS",
                "lead_days_min": 4,
                "lead_days_max": 6,
                "defect_rate_percent": 1.8,
                "stock_level": 150,
            },
        ]

        res = SourcingRanker.rank_candidate_suppliers(candidate)
        self.assertEqual(res["allocation_strategy"], "DUAL_SOURCE_RESILIENT_80_20")
        self.assertEqual(res["allocations"]["primary-us-east"], 80.0)
        self.assertEqual(res["allocations"]["backup-us-west"], 20.0)

        # Validate full schema compliance with allocation fields
        with (SCHEMAS_DIR / "sourcing_ranker.schema.json").open("r", encoding="utf-8") as f:
            schema = json.load(f)
        validator = Draft202012Validator(schema)
        errors = list(validator.iter_errors(res))
        self.assertEqual(errors, [], f"Sourcing ranker with allocation failed schema: {errors}")


if __name__ == "__main__":
    unittest.main()
