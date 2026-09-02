"""Phase-6 Test Suite: Medusa v2 Storefront Live Synchronization."""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from agency.core.store import Store
from agency.ingestion.medusa_storefront_sync import MedusaStorefrontSync

ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = ROOT / "fixtures"


class TestPhase6MedusaSync(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_medusa.db"
        self.store = Store(db_path=self.db_path, data_dir=Path(self.temp_dir))

        with (FIXTURES_DIR / "candidate.sample.json").open("r", encoding="utf-8") as f:
            self.candidate = json.load(f)
        self.store.save_candidate(self.candidate)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # 1. Payload Structure & Cent-Level Math
    def test_medusa_payload_generation(self) -> None:
        sync_engine = MedusaStorefrontSync(self.store)
        payload = sync_engine.build_medusa_payload(
            candidate=self.candidate,
            verified_telemetry={
                "stock_level": 350,
                "supplier_id": "cj-dropshipping-us-domestic-hub",
                "stability_score": 0.98,
                "verified_product_cost": 6.50,
                "verified_shipping_cost": 3.50,
                "sku": "SKU-MAGNETIC-01",
            },
            publish=False,
        )

        self.assertEqual(payload["status"], "draft")
        self.assertEqual(payload["handle"], "sample-product-fixture")
        self.assertIn("generative AI", payload["description"])  # EU AI Act disclosure check

        # Variant checks
        self.assertEqual(len(payload["variants"]), 1)
        var = payload["variants"][0]
        self.assertEqual(var["sku"], "SKU-MAGNETIC-01")
        self.assertEqual(var["inventory_quantity"], 350)
        self.assertTrue(var["manage_inventory"])

        # Price cents check (e.g. $24.99 or $62.99)
        usd_price = next(p for p in var["prices"] if p["currency_code"] == "usd")
        self.assertIsInstance(usd_price["amount"], int)
        self.assertGreater(usd_price["amount"], 2000)  # > $20.00 in cents

        # Metadata provenance
        meta = payload["metadata"]
        self.assertEqual(meta["primary_supplier_id"], "cj-dropshipping-us-domestic-hub")
        self.assertEqual(meta["stability_score"], 0.98)
        self.assertIn("sync_provenance_hmac", meta)
        self.assertEqual(len(meta["sync_provenance_hmac"]), 64)

    # 2. Local Catalog Export and Storefront Sync
    def test_candidate_storefront_sync(self) -> None:
        sync_engine = MedusaStorefrontSync(self.store)
        res = sync_engine.sync_candidate(candidate_id=self.candidate["candidate_id"], publish=True)

        self.assertEqual(res["status"], "SYNCED")
        self.assertEqual(res["listing_status"], "published")
        self.assertGreater(res["retail_price_usd"], 20.0)
        self.assertTrue(Path(res["local_catalog_export"]).exists())

        # Verify audit event in Store
        logs = self.store.get_audit_trail(limit=10)
        medusa_events = [l for l in logs if l.get("event_type") == "MEDUSA_STOREFRONT_SYNCED"]
        self.assertEqual(len(medusa_events), 1)
        self.assertEqual(medusa_events[0]["details"]["candidate_id"], self.candidate["candidate_id"])

    # 3. Dry Run Preview Safety
    def test_dry_run_safety(self) -> None:
        sync_engine = MedusaStorefrontSync(self.store)
        res = sync_engine.sync_candidate(candidate_id=self.candidate["candidate_id"], dry_run=True)

        self.assertEqual(res["status"], "DRY_RUN")
        self.assertIn("payload", res)
        self.assertFalse(res["medusa_backend_connected"])


if __name__ == "__main__":
    unittest.main()
