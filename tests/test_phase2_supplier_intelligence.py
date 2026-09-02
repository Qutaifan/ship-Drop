"""Test Suite for Phase 2: Autonomous Supplier Intelligence & Margin Optimization."""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from agency.bots.supplier_drift_detector import SupplierDriftDetector
from agency.bots.supplier_verification_bot import (
    SupplierVerificationBot,
    compute_stability_score,
)
from agency.core.margin_reconciler import (
    MarginReconciler,
    calculate_packaging_uplift,
    reconcile_margins,
)
from agency.core.store import Store

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS_DIR = ROOT / "schemas"
FIXTURES_DIR = ROOT / "fixtures"


class TestPhase2SupplierIntelligence(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_phase2.db"
        self.store = Store(db_path=self.db_path, data_dir=Path(self.temp_dir))
        self.bot = SupplierVerificationBot(self.store)
        self.detector = SupplierDriftDetector(self.store)
        self.reconciler = MarginReconciler()

        # Seed candidate into store
        with (FIXTURES_DIR / "candidate.sample.json").open("r", encoding="utf-8") as f:
            self.sample_candidate = json.load(f)
        self.store.save_candidate(self.sample_candidate)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _load_json(self, p: Path) -> dict:
        with p.open("r", encoding="utf-8") as f:
            return json.load(f)

    # 1. Schema Validation
    def test_supplier_verification_schema(self) -> None:
        schema = self._load_json(SCHEMAS_DIR / "supplier_verification.schema.json")
        sample = self._load_json(FIXTURES_DIR / "supplier_verification.sample.json")
        validator = Draft202012Validator(schema)
        errors = list(validator.iter_errors(sample))
        self.assertEqual(errors, [], f"supplier_verification.sample.json failed schema validation: {errors}")
        self.assertEqual(sample["version"], "1.0.0")
        self.assertIn("stability_score", sample)
        self.assertIn("shipping_method", sample)

    # 2. Stability Score Formula Verification
    def test_stability_score_formula(self) -> None:
        # Perfect supplier: 0 drift, 200+ stock, 0% defect, domestic
        perfect = compute_stability_score(price_drift_percent=0.0, stock_level=300, defect_rate_percent=0.0, warehouse_type="domestic")
        self.assertEqual(perfect, 1.00)

        # Degraded supplier: 15% drift, 40 stock, 3% defect, international
        degraded = compute_stability_score(price_drift_percent=0.15, stock_level=40, defect_rate_percent=3.0, warehouse_type="international_transit")
        self.assertLess(degraded, 0.60)
        self.assertGreater(degraded, 0.30)

    # 3. Store Repository CRUD & Indexing
    def test_store_verification_crud_and_indexing(self) -> None:
        sample = self._load_json(FIXTURES_DIR / "supplier_verification.sample.json")
        saved_file = self.store.save_supplier_verification(sample)
        self.assertTrue(saved_file.exists())

        # Retrieve
        loaded = self.store.get_supplier_verification(sample["verification_id"])
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["stock_level"], sample["stock_level"])

        # Latest query
        latest = self.store.get_latest_verification_for_candidate(sample["candidate_id"])
        self.assertIsNotNone(latest)
        self.assertEqual(latest["verification_id"], sample["verification_id"])

        # Index verification via SQLite
        with self.store._get_connection() as conn:
            indexes = [row[1] for row in conn.execute("PRAGMA index_list('supplier_verifications')").fetchall()]
            self.assertIn("idx_verification_candidate", indexes)
            self.assertIn("idx_verification_status", indexes)
            self.assertIn("idx_verification_time", indexes)

        # Delete
        self.assertTrue(self.store.delete_supplier_verification(sample["verification_id"]))
        self.assertIsNone(self.store.get_supplier_verification(sample["verification_id"]))

    # 4. Margin Reconciler Math & Volatility Buffer
    def test_margin_reconciliation_math(self) -> None:
        unit_econ = {
            "gross_selling_price": 29.99,
            "currency": "USD",
            "product_cost": 6.00,
            "shipping_cost": 3.50,
            "contribution_before_ads": 15.00,
        }
        ver = {
            "verified_product_cost": 6.20,
            "verified_shipping_cost": 3.50,
            "duty_percent": 0.0,
            "packaging_type": "custom_box",
            "warehouse_country": "US",
            "warehouse_type": "domestic",
        }
        res = reconcile_margins(unit_econ, ver, shipping_volatility_percent=0.04)

        rec = res["reconciled_economics"]
        self.assertEqual(rec["packaging_uplift"], 0.45)
        # 3.50 * 1.04 = 3.64
        self.assertEqual(rec["verified_shipping_cost"], 3.64)
        self.assertEqual(rec["total_landed_cost"], round(6.20 + 3.64 + 0.0 + 0.45, 2))
        self.assertGreater(rec["reconciled_net_margin"], 12.00)
        self.assertGreater(rec["cogs_multiple"], 1.0)
        self.assertFalse(res["compression_flag"])
        self.assertEqual(res["status"], "MARGIN_STABLE")

    # 5. Margin Compression Flagging
    def test_margin_compression_flag(self) -> None:
        unit_econ = {
            "gross_selling_price": 29.99,
            "currency": "USD",
            "product_cost": 6.00,
            "shipping_cost": 3.50,
            "contribution_before_ads": 15.00,
        }
        # Sourcing cost surged to $13.00 + shipping $6.00
        surged_ver = {
            "verified_product_cost": 13.00,
            "verified_shipping_cost": 6.00,
            "duty_percent": 0.0,
            "packaging_type": "custom_box",
            "warehouse_country": "US",
            "warehouse_type": "domestic",
        }
        res = reconcile_margins(unit_econ, surged_ver)
        self.assertTrue(res["compression_flag"])
        self.assertEqual(res["status"], "MARGIN_COMPRESSED")
        self.assertLess(res["margin_delta"], -5.00)

    # 6. Supplier Verification Bot Real-Time Execution
    def test_supplier_verification_bot_execution(self) -> None:
        rec = self.bot.verify_candidate_supplier("sample-candidate")
        self.assertIn("verification_id", rec)
        self.assertEqual(rec["candidate_id"], "sample-candidate")
        self.assertIn(rec["status"], ["VERIFIED_PASS", "DRIFT_DETECTED", "OUT_OF_STOCK", "WAREHOUSE_MISMATCH"])
        self.assertGreaterEqual(rec["stability_score"], 0.0)

    # 7. Drift Detection: Price Spike (>= 8%)
    def test_drift_detector_price_spike(self) -> None:
        ver = {
            "price_drift_percent": 0.12,  # 12% price hike
            "stock_level": 200,
            "warehouse_type": "domestic",
            "warehouse_country": "US",
            "lead_days_max": 5,
        }
        has_drift, flags, severity = self.detector.detect_drift(ver)
        self.assertTrue(has_drift)
        self.assertEqual(severity, "HIGH")
        self.assertTrue(any("PRICE_SPIKE" in f for f in flags))

    # 8. Drift Detection: Stock Depletion (< 30 units)
    def test_drift_detector_stock_depletion(self) -> None:
        ver = {
            "price_drift_percent": 0.01,
            "stock_level": 15,  # Critical inventory
            "warehouse_type": "domestic",
            "warehouse_country": "US",
            "lead_days_max": 5,
        }
        has_drift, flags, severity = self.detector.detect_drift(ver)
        self.assertTrue(has_drift)
        self.assertEqual(severity, "HIGH")
        self.assertTrue(any("STOCK_DEPLETED" in f for f in flags))

    # 9. Drift Detection: Warehouse Relocation (International Switch)
    def test_drift_detector_warehouse_relocation(self) -> None:
        ver = {
            "price_drift_percent": 0.0,
            "stock_level": 500,
            "warehouse_type": "international_transit",
            "warehouse_country": "CN",
            "lead_days_max": 14,
        }
        has_drift, flags, severity = self.detector.detect_drift(ver)
        self.assertTrue(has_drift)
        self.assertEqual(severity, "HIGH")
        self.assertTrue(any("WAREHOUSE_RELOCATION" in f for f in flags))

    # 10. Drift Detector Scan & Signal Emission
    def test_drift_scan_and_signal_emission(self) -> None:
        # Create a candidate with drifted verification
        drifted_ver = {
            "$schema": "../schemas/supplier_verification.schema.json",
            "version": "1.0.0",
            "verification_id": "ver-20260901-test-drift",
            "candidate_id": "sample-candidate",
            "supplier_id": "cj-us-east",
            "sku": "SKU-SAMPLE-DRIFT",
            "verified_at": "2026-09-01T06:00:00Z",
            "verified_at_unix": 1788242400,
            "stock_level": 12,  # Low stock
            "warehouse_country": "CN",  # Relocated to CN
            "warehouse_type": "international_transit",
            "shipping_method": "CN ePacket",
            "quoted_product_cost": 5.00,
            "verified_product_cost": 6.50,
            "quoted_shipping_cost": 3.00,
            "verified_shipping_cost": 4.50,
            "price_drift_percent": 0.30,  # 30% surge
            "duty_percent": 0.0,
            "lead_days_min": 10,
            "lead_days_max": 18,
            "defect_rate_percent": 3.5,
            "packaging_type": "polybag",
            "verification_confidence": 0.90,
            "stability_score": 0.35,
            "status": "DRIFT_DETECTED",
            "verification_notes": "Stock exhausted in US; defaulting to CN direct fulfillment.",
        }
        self.store.save_supplier_verification(drifted_ver)

        emitted = self.detector.scan_and_emit_signals()
        self.assertGreaterEqual(len(emitted), 1)
        drift_sig = emitted[0]
        self.assertEqual(drift_sig["candidate_id"], "sample-candidate")
        self.assertEqual(drift_sig["severity"], "HIGH")

        # Verify signal was saved in store
        saved_sig = self.store.get_signal(drift_sig["signal_id"])
        self.assertIsNotNone(saved_sig)
        self.assertEqual(saved_sig["approval_status"], "PENDING_FOUNDER_REVIEW")


if __name__ == "__main__":
    unittest.main()
