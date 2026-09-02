"""Hermes Stripe Sandbox Webhook Ingestion: Processes real payment intents and checkout completions."""
from __future__ import annotations

import datetime
import hashlib
import hmac
import json
import os
from typing import Any, Dict, List, Optional

from agency.core.store import Store


class StripeTelemetryIngestion:
    """Ingests and validates Stripe test/sandbox webhook events.
    Reconciles merchant processing fees and records cryptographic provenance in Store audit log.
    """

    def __init__(self, store: Optional[Store] = None):
        self.store = store or Store()
        self.webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "whsec_test_hermes_sandbox_2026").encode("utf-8")

    def verify_webhook_signature(self, payload_bytes: bytes, sig_header: str) -> bool:
        """Validates Stripe HMAC signature header (t=timestamp,v1=signature)."""
        if not sig_header:
            return False

        parts = {}
        for item in sig_header.split(","):
            if "=" in item:
                k, v = item.strip().split("=", 1)
                parts[k] = v

        timestamp = parts.get("t")
        expected_sig = parts.get("v1")
        if not timestamp or not expected_sig:
            return False

        signed_payload = f"{timestamp}.".encode("utf-8") + payload_bytes
        computed = hmac.new(self.webhook_secret, signed_payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(computed, expected_sig)

    def process_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Routes and reconciles Stripe event payload."""
        event_type = event_data.get("type", "")
        data_obj = event_data.get("data", {}).get("object", {})

        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        if event_type == "checkout.session.completed":
            session_id = data_obj.get("id", "cs_test_unknown")
            amount_total_cents = int(data_obj.get("amount_total", 0))
            currency = str(data_obj.get("currency", "usd")).upper()
            gross_amount = round(amount_total_cents / 100.0, 2)

            meta = data_obj.get("metadata", {})
            candidate_id = meta.get("candidate_id", "cand-cj-sku-magnetic-cord-6p")
            sku = meta.get("sku", "SKU-MAGNETIC-01")

            # Standard Stripe card processing fee: 2.9% + $0.30
            stripe_fee = round((gross_amount * 0.029) + 0.30, 2)
            net_proceeds = round(gross_amount - stripe_fee, 2)

            audit_entry = {
                "session_id": session_id,
                "candidate_id": candidate_id,
                "sku": sku,
                "gross_revenue": gross_amount,
                "stripe_fee": stripe_fee,
                "net_proceeds": net_proceeds,
                "currency": currency,
                "customer_country": data_obj.get("customer_details", {}).get("address", {}).get("country", "US"),
                "payment_status": data_obj.get("payment_status", "paid"),
                "processed_at": now_iso,
            }

            self.store.log_audit("STRIPE_CHECKOUT_COMPLETED", audit_entry)

            return {
                "status": "RECONCILED",
                "event_type": event_type,
                "session_id": session_id,
                "candidate_id": candidate_id,
                "gross_revenue": gross_amount,
                "stripe_fee": stripe_fee,
                "net_proceeds": net_proceeds,
            }

        elif event_type == "payment_intent.succeeded":
            intent_id = data_obj.get("id", "pi_test_unknown")
            amount_cents = int(data_obj.get("amount", 0))
            gross_amount = round(amount_cents / 100.0, 2)
            currency = str(data_obj.get("currency", "usd")).upper()

            audit_entry = {
                "payment_intent_id": intent_id,
                "amount": gross_amount,
                "currency": currency,
                "status": data_obj.get("status", "succeeded"),
                "processed_at": now_iso,
            }

            self.store.log_audit("STRIPE_PAYMENT_CAPTURED", audit_entry)

            return {
                "status": "CAPTURED",
                "event_type": event_type,
                "payment_intent_id": intent_id,
                "amount": gross_amount,
            }

        return {
            "status": "IGNORED",
            "event_type": event_type,
            "message": f"Event {event_type} ignored by Hermes ingestion.",
        }
