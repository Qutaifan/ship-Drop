"""Hermes Autonomous Supplier Replacement Engine: Orchestrates automated failover when suppliers degrade."""
from __future__ import annotations

import datetime
from typing import Any, Dict, List, Optional

from agency.core.sourcing_ranker import SourcingRanker
from agency.core.store import Store
from agency.core.supplier_allocator import SupplierAllocator
from agency.core.supplier_lifecycle import SupplierLifecycleManager, SupplierState


class SupplierReplacementEngine:
    """Detects degraded suppliers, runs failover simulation, and emits switch proposals."""

    def __init__(self, store: Optional[Store] = None):
        self.store = store or Store()

    def process_candidate_suppliers(self, candidate_id: str) -> Dict[str, Any]:
        """Evaluates lifecycle of candidate suppliers and triggers replacement if primary is degraded."""
        cand = self.store.get_candidate(candidate_id)
        if not cand:
            return {"status": "ERROR", "reason": f"Candidate {candidate_id} not found"}

        # Run ranking across suppliers
        verifications = self.store.list_supplier_verifications(candidate_id=candidate_id)
        rank_result = SourcingRanker.rank_candidate_suppliers(cand, verifications=verifications)
        suppliers = rank_result.get("suppliers", [])

        if not suppliers:
            return {"status": "NO_SUPPLIERS", "candidate_id": candidate_id}

        primary_id_target = (
            cand.get("current_supplier_id")
            or cand.get("selected_supplier_id")
            or (cand.get("supplier_evidence", [{}])[0].get("supplier_name", "").lower().replace(" ", "-") if cand.get("supplier_evidence") else None)
        )
        primary = next((s for s in suppliers if s["supplier_id"] == primary_id_target), suppliers[0])
        p_stab = float(primary.get("stability_score", 0.90))
        p_id = primary.get("supplier_id")

        # Evaluate lifecycle state
        lifecycle = SupplierLifecycleManager.evaluate_state(stability_score=p_stab)

        if not lifecycle.get("replacement_required", False) and p_stab >= 0.75:
            return {
                "candidate_id": candidate_id,
                "primary_supplier_id": p_id,
                "primary_state": lifecycle["state"],
                "switch_triggered": False,
                "message": f"Primary supplier {p_id} is in state {lifecycle['state']} ({p_stab:.2f} stability). No switch needed.",
            }

        # Primary is degraded or critical! Orchestrate automated replacement
        # Filter out primary from available replacements
        alternatives = [s for s in suppliers if s["supplier_id"] != p_id and s["tier"] in ["PREFERRED_DOMESTIC", "QUALIFIED_BACKUP"]]

        if not alternatives:
            # Emergency: No qualified fallback available! Pause listing to protect budget.
            pause_sig_id = f"sig-pause-{candidate_id[:16]}-{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d%H%M%S')}"
            pause_statement = f"EMERGENCY PAUSE: Primary supplier {p_id} degraded ({lifecycle['reason']}) and zero qualified backup domestic suppliers exist."
            # Idempotency: added 2026-09-03, see Store.has_active_duplicate_signal.
            if self.store.has_active_duplicate_signal(candidate_id, "SELL_KILL", pause_statement):
                return {
                    "candidate_id": candidate_id,
                    "primary_supplier_id": p_id,
                    "switch_triggered": False,
                    "message": "Emergency pause condition unchanged; an unresolved signal for it already exists.",
                }
            pause_signal = {
                "$schema": "../schemas/trade_signal.schema.json",
                "signal_id": pause_sig_id,
                "signal_type": "SELL_KILL",
                "candidate_id": candidate_id,
                "product_name": cand.get("product_name", candidate_id),
                "target_market": "US",
                "confidence": "high",
                "scores": {"profit_score": 0.0, "risk_score": 90.0, "trend_score": 50.0, "opportunity_score": 20.0, "supplier_score": 10.0},
                "hypothesis": {"predicted_ctr_percent": 0.0, "predicted_cvr_percent": 0.0, "predicted_cpa": 0.0, "predicted_net_margin": 0.0, "target_ad_budget": 0.0, "statement": pause_statement},
                "action_plan": {"recommended_action": "Pause active ads and freeze listings until alternative domestic source is vetted.", "execution_tier": 1, "creative_hooks": [], "suggested_supplier_id": None, "contingency_rule": "Maintain pause until manual supplier verification completes."},
                "approval_status": "PENDING_FOUNDER_REVIEW",
                "approval_id": None,
                "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "created_by": "tracker_bot",
            }
            self.store.save_signal(pause_signal)
            self.store.log_audit("EMERGENCY_LISTING_PAUSE_TRIGGERED", {"candidate_id": candidate_id, "degraded_supplier": p_id, "signal_id": pause_sig_id})
            return {
                "candidate_id": candidate_id,
                "primary_supplier_id": p_id,
                "switch_triggered": True,
                "failover_type": "EMERGENCY_PAUSE_NO_BACKUP",
                "signal_id": pause_sig_id,
            }

        # Best replacement selected
        best_replacement = alternatives[0]
        repl_id = best_replacement["supplier_id"]

        # Run allocation simulation
        new_alloc = SupplierAllocator.compute_allocation(alternatives)

        # Run margin simulation
        old_margin = float(primary["metrics"]["projected_net_margin"])
        new_margin = float(best_replacement["metrics"]["projected_net_margin"])
        margin_delta = round(new_margin - old_margin, 2)

        # Emit formal switch proposal
        now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d%H%M%S")
        switch_sig_id = f"sig-supplier-switch-{candidate_id[:16]}-{now_str}"
        switch_statement = (
            f"Automated replacement: Primary supplier {p_id} fell to state {lifecycle['state']} ({lifecycle['reason']}). "
            f"Rerouting fulfillment to {repl_id} (Stability: {best_replacement['stability_score']:.2f}, Margin: ${new_margin:.2f}, Net Delta: ${margin_delta:+.2f})."
        )
        # Idempotency: added 2026-09-03, see Store.has_active_duplicate_signal. If the
        # margin figures are unchanged the statement matches exactly and this is a
        # no-op; a materially different margin naturally produces a new statement.
        if self.store.has_active_duplicate_signal(candidate_id, "SUPPLIER_SWITCH", switch_statement):
            return {
                "candidate_id": candidate_id,
                "primary_supplier_id": p_id,
                "replacement_supplier_id": repl_id,
                "switch_triggered": False,
                "message": "Switch condition unchanged; an unresolved signal for it already exists.",
            }
        switch_signal: Dict[str, Any] = {
            "$schema": "../schemas/trade_signal.schema.json",
            "signal_id": switch_sig_id,
            "signal_type": "SUPPLIER_SWITCH",
            "candidate_id": candidate_id,
            "product_name": cand.get("product_name", candidate_id),
            "target_market": "US",
            "confidence": "high",
            "scores": {
                "profit_score": 80.0,
                "risk_score": 25.0,
                "trend_score": 75.0,
                "opportunity_score": 82.0,
                "supplier_score": float(best_replacement["stability_score"] * 100.0),
            },
            "hypothesis": {
                "predicted_ctr_percent": 2.5,
                "predicted_cvr_percent": 2.2,
                "predicted_cpa": 15.0,
                "predicted_net_margin": new_margin,
                "target_ad_budget": 0.0,
                "statement": switch_statement,
            },
            "action_plan": {
                "recommended_action": f"Approve supplier switch from {p_id} to {repl_id} (Allocation: {new_alloc.get('strategy')}).",
                "execution_tier": 2,
                "creative_hooks": [
                    "Guaranteed fast domestic tracked delivery",
                    "Premium factory-sealed packaging",
                    "Satisfaction guarantee",
                ],
                "suggested_supplier_id": repl_id,
                "contingency_rule": f"Auto-pause if replacement lead time exceeds {best_replacement['metrics']['lead_days_max'] + 2} days.",
            },
            "approval_status": "PENDING_FOUNDER_REVIEW",
            "approval_id": None,
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "created_by": "tracker_bot",
            "sourcing_rank": {
                "tier": best_replacement["tier"],
                "stability": best_replacement["stability_score"],
                "lead_time_days": best_replacement["metrics"]["lead_days_max"],
                "margin_projection": new_margin,
                "actionability": best_replacement["actionability_score"],
            },
        }

        self.store.save_signal(switch_signal)
        self.store.log_audit("SUPPLIER_REPLACEMENT_ORCHESTRATED", {
            "signal_id": switch_sig_id,
            "candidate_id": candidate_id,
            "degraded_supplier": p_id,
            "replacement_supplier": repl_id,
            "margin_delta": margin_delta,
            "new_allocation_strategy": new_alloc.get("strategy"),
        })

        return {
            "candidate_id": candidate_id,
            "primary_supplier_id": p_id,
            "replacement_supplier_id": repl_id,
            "switch_triggered": True,
            "failover_type": "QUALIFIED_DOMESTIC_SWITCH",
            "margin_delta": margin_delta,
            "new_allocation": new_alloc["allocations"],
            "signal_id": switch_sig_id,
        }
