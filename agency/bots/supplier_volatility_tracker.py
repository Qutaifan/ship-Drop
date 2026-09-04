"""Hermes Supplier Volatility Tracker: Analyzes stability curves and generates health timelines."""
from __future__ import annotations

import json
import math
import statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from agency.core.store import Store

ROOT = Path(__file__).resolve().parents[2]
TIMELINE_DIR = ROOT / "data" / "supplier_health"


class SupplierVolatilityTracker:
    def __init__(self, store: Optional[Store] = None):
        self.store = store or Store()
        TIMELINE_DIR.mkdir(parents=True, exist_ok=True)

    def analyze_supplier(self, supplier_id: str, candidate_id: Optional[str] = None) -> Dict[str, Any]:
        """Calculates volatility metrics and produces health timeline for a supplier."""
        # Query verifications for supplier
        all_vers = self.store.list_supplier_verifications(candidate_id=candidate_id, limit=100)
        sup_vers = [v for v in all_vers if v.get("supplier_id") == supplier_id]

        if not sup_vers:
            # Check candidate level if none matched by supplier_id
            if candidate_id:
                sup_vers = all_vers
            else:
                sup_vers = []

        # Sort chronologically
        sup_vers = sorted(sup_vers, key=lambda x: x.get("verified_at", x.get("created_at", "")))

        timeline_points = []
        stability_scores = []
        stock_levels = []
        price_costs = []
        lead_times = []

        for v in sup_vers:
            ts = v.get("verified_at", v.get("created_at", datetime.now(timezone.utc).isoformat()))
            stab = float(v.get("stability_score", 0.90))
            stock = int(v.get("stock_level", 100))
            cost = float(v.get("verified_product_cost", 10.0))
            lead = int(v.get("lead_days_max", 5))

            timeline_points.append({
                "ts": ts,
                "stability": stab,
                "stock": stock,
                "product_cost": cost,
                "lead_days_max": lead,
                "status": v.get("status", "VERIFIED_PASS"),
            })

            stability_scores.append(stab)
            stock_levels.append(stock)
            price_costs.append(cost)
            lead_times.append(lead)

        if not stability_scores:
            # Synthesize single baseline point if virgin supplier
            timeline_points.append({
                "ts": datetime.now(timezone.utc).isoformat(),
                "stability": 0.95,
                "stock": 300,
                "product_cost": 7.0,
                "lead_days_max": 5,
                "status": "BASELINE",
            })
            stability_scores = [0.95]
            stock_levels = [300]
            price_costs = [7.0]
            lead_times = [5]

        # Compute volatility metrics
        latest_stab = stability_scores[-1]
        oldest_stab = stability_scores[0]
        stability_drift = round(latest_stab - oldest_stab, 3)

        volatility_index = (
            round(statistics.stdev(stability_scores), 3)
            if len(stability_scores) > 1
            else 0.0
        )

        stock_velocity = (
            round((stock_levels[-1] - stock_levels[0]) / max(1, len(stock_levels)), 1)
        )

        cost_drift_percent = (
            round(((price_costs[-1] - price_costs[0]) / price_costs[0]) * 100.0, 2)
            if price_costs[0] > 0
            else 0.0
        )

        lead_time_inflation_days = lead_times[-1] - lead_times[0]

        # Governance switch evaluation:
        # If stability drops below 0.75 or volatility index > 0.15
        switch_recommended = (latest_stab < 0.75) or (volatility_index >= 0.15)
        switch_reason = None
        if latest_stab < 0.75:
            switch_reason = f"Supplier stability ({latest_stab:.2f}) dropped below 0.75 governance floor"
        elif volatility_index >= 0.15:
            switch_reason = f"Supplier stability volatility index ({volatility_index:.2f}) exceeds 0.15 safety limit"

        result = {
            "supplier_id": supplier_id,
            "candidate_id": candidate_id,
            "sample_count": len(timeline_points),
            "latest_metrics": {
                "stability": latest_stab,
                "stock": stock_levels[-1],
                "lead_days_max": lead_times[-1],
                "product_cost": price_costs[-1],
            },
            "volatility_curves": {
                "stability_drift": stability_drift,
                "volatility_index": volatility_index,
                "stock_velocity_units_per_audit": stock_velocity,
                "price_drift_percent": cost_drift_percent,
                "lead_time_inflation_days": lead_time_inflation_days,
            },
            "governance": {
                "switch_recommended": switch_recommended,
                "switch_reason": switch_reason,
                "canary_blocked": switch_recommended,
            },
            "timeline": timeline_points,
        }

        # Save health timeline JSON artifact
        clean_sup = supplier_id.lower().replace(" ", "-")
        out_file = TIMELINE_DIR / f"{clean_sup}.timeline.json"
        with out_file.open("w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

        return result

    def emit_supplier_switch_proposal(
        self,
        candidate_id: str,
        degraded_supplier_id: str,
        replacement_supplier_id: str,
        reason: str,
    ) -> Dict[str, Any]:
        """Generates a formal SUPPLIER_SWITCH trade signal proposal for Founder sign-off."""
        cand = self.store.get_candidate(candidate_id) or {}
        pname = cand.get("product_name", candidate_id)
        now_str = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        sig_id = f"sig-supplier-switch-{candidate_id[:16]}-{now_str}"
        statement = f"Automated governance switch: Primary supplier {degraded_supplier_id} degraded ({reason}). Rerouting allocation to qualified backup {replacement_supplier_id}."

        # Idempotency: skip if an unresolved signal for this exact condition already
        # exists. Added 2026-09-03 — see Store.has_active_duplicate_signal.
        if self.store.has_active_duplicate_signal(candidate_id, "SUPPLIER_SWITCH", statement):
            return {}

        signal_payload: Dict[str, Any] = {
            "$schema": "../schemas/trade_signal.schema.json",
            "signal_id": sig_id,
            "signal_type": "SUPPLIER_SWITCH",
            "candidate_id": candidate_id,
            "product_name": pname,
            "target_market": "US",
            "confidence": "high",
            "scores": {
                "profit_score": 75.0,
                "risk_score": 40.0,
                "trend_score": 80.0,
                "opportunity_score": 78.0,
                "supplier_score": 50.0,
            },
            "hypothesis": {
                "predicted_ctr_percent": 2.5,
                "predicted_cvr_percent": 2.2,
                "predicted_cpa": 15.0,
                "predicted_net_margin": 14.5,
                "target_ad_budget": 0.0,
                "statement": statement,
            },
            "action_plan": {
                "recommended_action": f"Switch primary fulfillment from {degraded_supplier_id} to {replacement_supplier_id} to protect margin and delivery SLA.",
                "execution_tier": 2,
                "creative_hooks": [
                    "Hook 1: Guaranteed fast domestic shipping",
                    "Hook 2: Premium inspected packaging",
                    "Hook 3: Problem solver before/after",
                ],
                "suggested_supplier_id": replacement_supplier_id,
                "contingency_rule": "If replacement supplier defect rate exceeds 2.5%, pause listing.",
            },
            "approval_status": "PENDING_FOUNDER_REVIEW",
            "approval_id": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "created_by": "tracker_bot",
            "sourcing_rank": {
                "tier": "QUALIFIED_BACKUP",
                "stability": 0.88,
                "lead_time_days": 6,
                "margin_projection": 12.50,
                "actionability": 45.0,
            },
        }

        self.store.save_signal(signal_payload)
        self.store.log_audit("SUPPLIER_SWITCH_SIGNAL_EMITTED", {
            "signal_id": sig_id,
            "candidate_id": candidate_id,
            "degraded_supplier": degraded_supplier_id,
            "replacement_supplier": replacement_supplier_id,
            "reason": reason,
        })
        return signal_payload
