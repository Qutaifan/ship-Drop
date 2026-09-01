"""Hermes SKU Supplier Competition Matrix: Evaluates side-by-side multi-vendor telemetry for a product."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from agency.bots.supplier_volatility_tracker import SupplierVolatilityTracker
from agency.core.sourcing_ranker import SourcingRanker
from agency.core.store import Store
from agency.core.supplier_forecasting import SupplierHealthForecaster
from agency.core.supplier_lifecycle import SupplierLifecycleManager


class SupplierCompetitionMatrix:
    """Produces comprehensive side-by-side competition matrix for all suppliers of a SKU."""

    @staticmethod
    def generate_matrix(candidate_id: str, store: Optional[Store] = None) -> Dict[str, Any]:
        store = store or Store()
        cand = store.get_candidate(candidate_id)
        if not cand:
            return {"error": f"Candidate {candidate_id} not found"}

        verifications = store.list_supplier_verifications(candidate_id=candidate_id)
        rank_result = SourcingRanker.rank_candidate_suppliers(cand, verifications=verifications)
        ranked_suppliers = rank_result.get("suppliers", [])

        tracker = SupplierVolatilityTracker(store)

        matrix_rows = []
        for s in ranked_suppliers:
            sup_id = s["supplier_id"]
            vol_analysis = tracker.analyze_supplier(supplier_id=sup_id, candidate_id=candidate_id)
            forecast = SupplierHealthForecaster.forecast_health(vol_analysis.get("timeline", []))
            lifecycle = SupplierLifecycleManager.evaluate_state(
                stability_score=s["stability_score"],
                volatility_index=vol_analysis["volatility_curves"]["volatility_index"],
            )

            matrix_rows.append({
                "rank": s["rank"],
                "supplier_id": sup_id,
                "supplier_name": s["supplier_name"],
                "tier": s["tier"],
                "lifecycle_state": lifecycle["state"],
                "allocation_percent": s.get("allocation_percent", 0.0),
                "stability_score": s["stability_score"],
                "volatility_index": vol_analysis["volatility_curves"]["volatility_index"],
                "projected_7d_stability": forecast["projected_7d"]["stability"],
                "stock_runout_days": forecast["projected_7d"]["stock_runout_days"],
                "landed_cost": s["metrics"]["landed_cost"],
                "projected_net_margin": s["metrics"]["projected_net_margin"],
                "lead_days_max": s["metrics"]["lead_days_max"],
                "stock_level": s["metrics"]["stock_level"],
                "defect_rate_percent": s["metrics"]["defect_rate_percent"],
                "canary_eligible": s["canary_eligible"] and lifecycle["canary_permitted"],
                "forecast_risk": forecast["risk_tier"],
            })

        return {
            "candidate_id": candidate_id,
            "product_name": cand.get("product_name", candidate_id),
            "allocation_strategy": rank_result.get("allocation_strategy", "SINGLE_SOURCE"),
            "supplier_count": len(matrix_rows),
            "competition_matrix": matrix_rows,
        }
