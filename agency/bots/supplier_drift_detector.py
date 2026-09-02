"""Supplier Drift Detector - Continuous monitoring and alert emission for supplier instability."""
from __future__ import annotations

import datetime
import re
import uuid
from typing import Any, Dict, List, Optional, Tuple

from agency.core.store import Store


class SupplierDriftDetector:
    """Monitors verified supplier telemetry and emits drift alerts & switch signals."""

    def __init__(self, store: Optional[Store] = None):
        self.store = store or Store()

    def detect_drift(self, verification: Dict[str, Any]) -> Tuple[bool, List[str], str]:
        """Audits verification record against 6 critical supply chain drift types."""
        flags: List[str] = []
        severity = "LOW"

        # 1. Price Spike Drift (>= 8% increase)
        price_drift = float(verification.get("price_drift_percent", 0.0))
        if price_drift >= 0.08:
            flags.append(f"PRICE_SPIKE: Landed product cost increased by {price_drift:+.1%} (threshold >= 8%).")
            severity = "HIGH"

        # 2. Stock Depletion Drift (< 30 units)
        stock = int(verification.get("stock_level", 100))
        if stock < 30:
            flags.append(f"STOCK_DEPLETED: Warehouse stock has dropped to {stock} units (emergency ceiling < 30).")
            severity = "HIGH"

        # 3. Warehouse Relocation (International Fallback)
        wh_type = verification.get("warehouse_type", "domestic")
        wh_country = verification.get("warehouse_country", "US")
        if wh_type != "domestic" or wh_country in ["CN", "HK"]:
            flags.append(f"WAREHOUSE_RELOCATION: Supplier switched fulfillment to {wh_country} ({wh_type}). Violates domestic SLA.")
            severity = "HIGH"

        # 4. Lead Time Inflation (> 7 days shipping max)
        lead_max = int(verification.get("lead_days_max", 5))
        if lead_max > 7:
            flags.append(f"LEAD_TIME_INFLATION: Max shipping time inflated to {lead_max} days (limit <= 7).")
            if severity != "HIGH":
                severity = "MEDIUM"

        # 5. Supplier API Silence
        if verification.get("status") == "API_SILENCE" or verification.get("verification_confidence", 1.0) < 0.30:
            flags.append("SUPPLIER_API_SILENCE: Supplier catalog feed uncontactable or unresponsive.")
            severity = "HIGH"

        # 6. SKU Fragmentation
        if verification.get("status") == "SKU_FRAGMENTATION":
            flags.append("SKU_FRAGMENTATION: Supplier split original listing into fragmented variant costs.")
            if severity != "HIGH":
                severity = "MEDIUM"

        has_drift = len(flags) > 0
        return has_drift, flags, severity

    def scan_and_emit_signals(self) -> List[Dict[str, Any]]:
        """Scans latest verification records for all candidates and emits drift trade signals."""
        drift_signals = []
        candidates = self.store.list_candidates()

        for cand in candidates:
            cid = cand["candidate_id"]
            latest_ver = self.store.get_latest_verification_for_candidate(cid)
            if not latest_ver:
                continue

            has_drift, flags, severity = self.detect_drift(latest_ver)
            if not has_drift:
                continue

            product_name = cand.get("product_name", cid)
            now = datetime.datetime.now(datetime.timezone.utc)
            cid_clean = re.sub(r"[^a-z0-9-]", "-", cid.lower())[:30].strip("-")
            sig_id = f"sig-supplier-drift-{cid_clean}-{uuid.uuid4().hex[:6]}"

            # Determine recommendation based on severity
            if "WAREHOUSE_RELOCATION" in "".join(flags):
                rec_signal_type = "SUPPLIER_SWITCH"
                action_text = f"Switch supplier for '{product_name}' immediately to an authorized domestic warehouse."
            elif "PRICE_SPIKE" in "".join(flags) and float(latest_ver.get("price_drift_percent", 0.0)) > 0.20:
                rec_signal_type = "SELL_KILL"
                action_text = f"Kill campaign for '{product_name}' due to severe landed cost surge destroying net margin."
            else:
                rec_signal_type = "SUPPLIER_SWITCH"
                action_text = f"Review alternative fulfillment options for '{product_name}' to resolve {len(flags)} supplier drift issue(s)."

            drift_signal_data: Dict[str, Any] = {
                "$schema": "../schemas/trade_signal.schema.json",
                "version": "1.0.0",
                "signal_id": sig_id,
                "signal_type": rec_signal_type,
                "candidate_id": cid,
                "product_name": product_name,
                "target_market": "US" if cand.get("market_config_id", "us").startswith("us") else "EU",
                "confidence": "high" if severity == "HIGH" else "medium",
                "scores": {
                    "profit_score": 50.0,
                    "risk_score": 75.0 if severity == "HIGH" else 55.0,
                    "trend_score": 60.0,
                    "opportunity_score": 45.0 if severity == "HIGH" else 55.0,
                    "supplier_score": round(float(latest_ver.get("stability_score", 0.5)) * 100.0, 1),
                },
                "hypothesis": {
                    "predicted_ctr_percent": 2.0,
                    "predicted_cvr_percent": 2.0,
                    "predicted_cpa": 15.00,
                    "predicted_net_margin": 10.00,
                    "target_ad_budget": 0.0,
                    "statement": f"Supplier drift detected: {' | '.join(flags)} Stability score: {latest_ver.get('stability_score')}.",
                },
                "action_plan": {
                    "execution_tier": 3,
                    "recommended_action": action_text,
                    "target_ad_budget": 0.0,
                    "creative_hooks": [
                        "Problem Hook: Halt ad spend until supplier switch is executed.",
                        "Transformation Hook: Re-route fulfillment to secondary domestic warehouse.",
                        "Lifestyle Hook: Update catalog stock parameters to domestic inventory.",
                    ],
                    "contingency_rule": "Auto-pause ad campaign immediately upon supplier drift detection.",
                },
                "approval_status": "PENDING_FOUNDER_REVIEW",
                "created_at": now.isoformat(),
                "created_by": "tracker_bot",
            }

            self.store.save_signal(drift_signal_data)
            drift_signals.append({
                "signal_id": sig_id,
                "candidate_id": cid,
                "product_name": product_name,
                "severity": severity,
                "flags": flags,
                "signal_data": drift_signal_data,
            })

        return drift_signals
