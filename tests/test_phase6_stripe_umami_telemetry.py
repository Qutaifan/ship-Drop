"""Phase-6 Test Suite: Pipe 4 — Stripe Express Checkout + Umami Cookieless Telemetry."""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from agency.core.store import Store
from agency.ingestion.stripe_telemetry_ingestion import StripeTelemetryIngestion
from agency.ingestion.umami_telemetry_ingestion import UmamiTelemetryIngestion

ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = ROOT / "fixtures"


class TestStripeWebhookIngestion(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_stripe.db"
        self.store = Store(db_path=self.db_path, data_dir=Path(self.temp_dir))

        with (FIXTURES_DIR / "candidate.sample.json").open("r", encoding="utf-8") as f:
            self.candidate = json.load(f)
        self.store.save_candidate(self.candidate)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # 1. Checkout Session Completed → Revenue Reconciliation
    def test_checkout_session_completed(self) -> None:
        engine = StripeTelemetryIngestion(self.store)
        event = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_unit_001",
                    "amount_total": 6299,  # $62.99 in cents
                    "currency": "usd",
                    "payment_status": "paid",
                    "metadata": {"candidate_id": "cand-cj-sku-magnetic-cord-6p", "sku": "SKU-MAGNETIC-01"},
                    "customer_details": {"address": {"country": "US"}},
                }
            },
        }

        res = engine.process_event(event)
        self.assertEqual(res["status"], "RECONCILED")
        self.assertEqual(res["session_id"], "cs_test_unit_001")
        self.assertAlmostEqual(res["gross_revenue"], 62.99)
        self.assertAlmostEqual(res["stripe_fee"], 2.13, places=2)
        self.assertAlmostEqual(res["net_proceeds"], 60.86, places=2)

        # Verify audit trail
        logs = self.store.get_audit_trail(limit=5)
        stripe_events = [l for l in logs if l.get("event_type") == "STRIPE_CHECKOUT_COMPLETED"]
        self.assertEqual(len(stripe_events), 1)

    # 2. Payment Intent Succeeded → Capture Logged
    def test_payment_intent_succeeded(self) -> None:
        engine = StripeTelemetryIngestion(self.store)
        event = {
            "type": "payment_intent.succeeded",
            "data": {
                "object": {
                    "id": "pi_test_unit_002",
                    "amount": 6299,
                    "currency": "usd",
                    "status": "succeeded",
                }
            },
        }

        res = engine.process_event(event)
        self.assertEqual(res["status"], "CAPTURED")
        self.assertAlmostEqual(res["amount"], 62.99)

        logs = self.store.get_audit_trail(limit=5)
        capture_events = [l for l in logs if l.get("event_type") == "STRIPE_PAYMENT_CAPTURED"]
        self.assertEqual(len(capture_events), 1)

    # 3. Unknown Events Safely Ignored
    def test_unknown_event_ignored(self) -> None:
        engine = StripeTelemetryIngestion(self.store)
        res = engine.process_event({"type": "charge.refunded", "data": {"object": {}}})
        self.assertEqual(res["status"], "IGNORED")


class TestUmamiTelemetryIngestion(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_umami.db"
        self.store = Store(db_path=self.db_path, data_dir=Path(self.temp_dir))
        self.data_dir = Path(self.temp_dir)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # 4. Full Funnel Recording → CVR and Elasticity
    def test_funnel_recording_and_cvr(self) -> None:
        engine = UmamiTelemetryIngestion(self.store, data_dir=self.data_dir)

        for _ in range(100):
            engine.record_event(candidate_id="test-sku", event_type="pageview", price_point=62.99)
        for _ in range(12):
            engine.record_event(candidate_id="test-sku", event_type="checkout_started", price_point=62.99)
        for _ in range(4):
            engine.record_event(candidate_id="test-sku", event_type="checkout_completed", price_point=62.99)

        summary = engine.get_sku_funnel_summary("test-sku")

        self.assertEqual(summary["pageviews"], 100)
        self.assertEqual(summary["checkout_started"], 12)
        self.assertEqual(summary["checkout_completed"], 4)
        self.assertAlmostEqual(summary["real_conversion_rate_percent"], 4.0)
        self.assertAlmostEqual(summary["checkout_initiation_rate_percent"], 12.0)
        self.assertGreater(summary["profit_per_visitor_usd"], 0.0)

    # 5. Price Cohort Tracking
    def test_price_cohort_tracking(self) -> None:
        engine = UmamiTelemetryIngestion(self.store, data_dir=self.data_dir)

        for _ in range(50):
            engine.record_event(candidate_id="cohort-test", event_type="pageview", price_point=59.99)
        for _ in range(2):
            engine.record_event(candidate_id="cohort-test", event_type="checkout_completed", price_point=59.99)

        for _ in range(50):
            engine.record_event(candidate_id="cohort-test", event_type="pageview", price_point=69.99)
        for _ in range(1):
            engine.record_event(candidate_id="cohort-test", event_type="checkout_completed", price_point=69.99)

        summary = engine.get_sku_funnel_summary("cohort-test")

        self.assertIn("59.99", summary["price_cohorts"])
        self.assertIn("69.99", summary["price_cohorts"])
        self.assertEqual(summary["price_cohorts"]["59.99"]["views"], 50)
        self.assertEqual(summary["price_cohorts"]["59.99"]["conversions"], 2)
        self.assertEqual(summary["price_cohorts"]["69.99"]["views"], 50)
        self.assertEqual(summary["price_cohorts"]["69.99"]["conversions"], 1)

    # 6. Invalid Event Type Raises
    def test_invalid_event_type_raises(self) -> None:
        engine = UmamiTelemetryIngestion(self.store, data_dir=self.data_dir)
        with self.assertRaises(ValueError):
            engine.record_event(candidate_id="x", event_type="invalid_event")

    # 7. Audit Trail Populated
    def test_audit_trail_populated(self) -> None:
        engine = UmamiTelemetryIngestion(self.store, data_dir=self.data_dir)
        engine.record_event(candidate_id="audit-test", event_type="pageview")

        logs = self.store.get_audit_trail(limit=5)
        umami_events = [l for l in logs if l.get("event_type") == "UMAMI_TELEMETRY_EVENT"]
        self.assertEqual(len(umami_events), 1)


if __name__ == "__main__":
    unittest.main()
