"""Hermes Fake Buyer Journey Simulator: Runs synthetic end-to-end commerce narrative and logs to replay."""
from __future__ import annotations

import datetime
import hashlib
import hmac
import os
import random
import time
from typing import Any, Dict, List, Optional

from agency.core.margin_reconciler import reconcile_margins
from agency.core.sourcing_ranker import SourcingRanker
from agency.core.store import Store
from agency.governance.autonomous_windows import AutonomousWindowManager
from agency.governance.execution_gateway import ExecutionGateway


class FakeBuyerJourneySimulator:
    """Simulates an autonomous end-to-end e-commerce order journey:
    Ad Impression -> Click -> Storefront LCP -> Express Checkout -> Order Routing -> Canary Gate -> CJ Dispatch -> Replay Log.
    """

    def __init__(self, store: Optional[Store] = None):
        self.store = store or Store()
        self.window_mgr = AutonomousWindowManager(self.store)
        self.secret = os.environ.get("HERMES_PROVENANCE_SECRET", "hermes-default-provenance-key-2026").encode("utf-8")

    def _sign(self, text: str) -> str:
        return hmac.new(self.secret, text.encode("utf-8"), hashlib.sha256).hexdigest()

    def simulate_order(
        self,
        candidate_id: str = "cand-cj-sku-magnetic-cord-6p",
        customer_name: str = "Marcus Vance (Synthetic Buyer)",
        customer_country: str = "US",
        traffic_channel: str = "TikTok Ad Hook #1 (Pain-Relief)",
        payment_method: str = "Apple Pay (Stripe Express)",
    ) -> Dict[str, Any]:
        """Executes full synthetic narrative and logs every step to replay."""
        now = datetime.datetime.now(datetime.timezone.utc)
        order_id = f"ord-syn-{now.strftime('%Y%m%d')}-{os.urandom(3).hex()}"
        tracking_num = f"940011189956{random.randint(10000000, 99999999)}"

        # 1. Fetch Candidate
        cand = self.store.get_candidate(candidate_id)
        if not cand:
            raise ValueError(f"Candidate {candidate_id} not found in database.")

        product_name = cand.get("product_name", "Target SKU")
        econ = cand.get("unit_economics", {})
        retail = float(econ.get("gross_selling_price", 62.99))

        narrative_steps: List[Dict[str, Any]] = []

        def log_step(action: str, details: str) -> None:
            ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
            sig = self._sign(f"{order_id}:{action}:{ts}")
            entry = {
                "order_id": order_id,
                "action": action,
                "details": details,
                "timestamp": ts,
                "hmac_signature": sig,
            }
            narrative_steps.append(entry)
            self.store.log_audit(f"SYNTHETIC_BUYER_{action}", entry)

        # Step 1: Ad Exposure & Click
        log_step(
            "AD_CONVERSION",
            f"Ad served on {traffic_channel}. User clicked (Est. CPC: $0.85). Creative hook verified: 3.2s stop rate.",
        )

        # Step 2: Storefront LCP & Frictionless Session
        log_step(
            "STOREFRONT_LANDING",
            f"Customer arrived at Next.js Medusa storefront. LCP: 420ms. Umami cookieless telemetry session assigned.",
        )

        # Step 3: Direct Express Checkout
        log_step(
            "CHECKOUT_INITIATED",
            f"Frictionless zero-account checkout initiated via {payment_method}. Total Cart Gross: ${retail:.2f}.",
        )

        # Step 4: Stripe Payment Capture
        stripe_fee = round((retail * 0.029) + 0.30, 2)
        net_payment_captured = round(retail - stripe_fee, 2)
        log_step(
            "PAYMENT_CAPTURED",
            f"Stripe captured ${retail:.2f} (Fee: ${stripe_fee:.2f} | Net Proceeds: ${net_payment_captured:.2f}).",
        )

        # Step 5: Sourcing Allocation & Selection
        vers = self.store.list_supplier_verifications(candidate_id=candidate_id)
        rank_res = SourcingRanker.rank_candidate_suppliers(cand, verifications=vers)
        top_sup = rank_res["suppliers"][0] if rank_res.get("suppliers") else {}
        sup_id = top_sup.get("supplier_id", "cj-dropshipping-us-domestic-hub")
        landed = float(top_sup.get("metrics", {}).get("landed_cost", 10.14))

        log_step(
            "SOURCING_ALLOCATION",
            f"Sourcing Ranker allocated order to '{sup_id}' (Tier: {top_sup.get('tier', 'PREFERRED_DOMESTIC')}, Stability: {top_sup.get('stability_score', 0.98):.2f}).",
        )

        # Step 6: Canary Gateway & Autonomous Window Verification
        auth_status = self.window_mgr.is_action_authorized("CANARY_ORDER_DISPATCH", sup_id, landed)
        canary_active = auth_status.get("authorized", False)
        log_step(
            "GATEWAY_VERIFICATION",
            f"Execution Gateway checked: Window Active={canary_active} (Remaining spend: ${(auth_status.get('window', {}).get('remaining_spend_limit_usd') or 500):.2f}). Order cleared for automated domestic dispatch.",
        )

        # Step 7: Domestic Warehouse Dispatch
        log_step(
            "DOMESTIC_DISPATCH",
            f"Automated order dispatch routed to CJ US Domestic Hub (USPS Priority Mail, Tracking: {tracking_num}, ETA: 2-4 days).",
        )

        # Step 8: Reconciled Unit Economics P&L
        unit_net_profit = round(retail - landed - stripe_fee, 2)
        cogs_multiple = round(unit_net_profit / landed, 1) if landed > 0 else 0.0
        log_step(
            "MARGIN_RECONCILED",
            f"Settled P&L: Retail ${retail:.2f} - Landed ${landed:.2f} - Processing ${stripe_fee:.2f} = Net Profit ${unit_net_profit:.2f} ({cogs_multiple}x COGS).",
        )

        return {
            "order_id": order_id,
            "candidate_id": candidate_id,
            "product_name": product_name,
            "customer_name": customer_name,
            "customer_country": customer_country,
            "traffic_channel": traffic_channel,
            "payment_method": payment_method,
            "carrier_tracking": tracking_num,
            "unit_economics": {
                "gross_retail": retail,
                "payment_fee": stripe_fee,
                "landed_cogs": landed,
                "net_profit": unit_net_profit,
                "cogs_multiple": cogs_multiple,
                "cac_gate_cleared": unit_net_profit >= 42.96,
            },
            "steps": narrative_steps,
        }
