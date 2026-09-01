"""Hermes Multi-SKU Portfolio Rebalancing Engine: Rebalances entire product catalog upon systemic supplier drift."""
from __future__ import annotations

import datetime
from typing import Any, Dict, List, Optional

from agency.bots.supplier_replacement_engine import SupplierReplacementEngine
from agency.core.reputation_graph import SupplierReputationGraph
from agency.core.store import Store


class PortfolioRebalancer:
    """Orchestrates portfolio-wide supplier rebalancing across multiple affected SKUs."""

    def __init__(self, store: Optional[Store] = None):
        self.store = store or Store()
        self.graph = SupplierReputationGraph(self.store)
        self.replacement_engine = SupplierReplacementEngine(self.store)

    def rebalance_supplier(self, degraded_supplier_id: str, reason: str = "Systemic stability degradation") -> Dict[str, Any]:
        """Identifies all SKUs dependent on the degraded supplier and produces a coordinated rebalancing batch."""
        risk_assessment = self.graph.assess_systemic_risk(degraded_supplier_id)
        affected_skus = risk_assessment.get("affected_skus", [])

        if not affected_skus:
            return {
                "degraded_supplier_id": degraded_supplier_id,
                "status": "NO_AFFECTED_SKUS",
                "message": f"No active SKUs in portfolio currently depend on supplier {degraded_supplier_id}.",
                "rebalanced_sku_count": 0,
            }

        sku_results: List[Dict[str, Any]] = []
        total_margin_delta = 0.0
        successful_switches = 0
        emergency_pauses = 0

        now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d%H%M%S")
        batch_id = f"batch-rebalance-{degraded_supplier_id[:12]}-{now_str}"

        for sku_id in affected_skus:
            rep_res = self.replacement_engine.process_candidate_suppliers(sku_id)
            if rep_res.get("switch_triggered"):
                ftype = rep_res.get("failover_type")
                if ftype == "QUALIFIED_DOMESTIC_SWITCH":
                    successful_switches += 1
                    delta = float(rep_res.get("margin_delta", 0.0))
                    total_margin_delta += delta
                    sku_results.append({
                        "candidate_id": sku_id,
                        "status": "REPLACED",
                        "replacement_supplier": rep_res.get("replacement_supplier_id"),
                        "margin_delta": delta,
                        "signal_id": rep_res.get("signal_id"),
                    })
                elif ftype == "EMERGENCY_PAUSE_NO_BACKUP":
                    emergency_pauses += 1
                    sku_results.append({
                        "candidate_id": sku_id,
                        "status": "PAUSED_NO_BACKUP",
                        "signal_id": rep_res.get("signal_id"),
                    })

        # Save batch audit trail
        self.store.log_audit("PORTFOLIO_REBALANCE_EXECUTED", {
            "batch_id": batch_id,
            "degraded_supplier": degraded_supplier_id,
            "affected_sku_count": len(affected_skus),
            "successful_switches": successful_switches,
            "emergency_pauses": emergency_pauses,
            "total_margin_delta": round(total_margin_delta, 2),
            "reason": reason,
        })

        return {
            "batch_id": batch_id,
            "degraded_supplier_id": degraded_supplier_id,
            "affected_sku_count": len(affected_skus),
            "successful_switches": successful_switches,
            "emergency_pauses": emergency_pauses,
            "net_portfolio_margin_delta": round(total_margin_delta, 2),
            "sku_details": sku_results,
            "summary": (
                f"Portfolio rebalancing complete: {successful_switches} SKU(s) rerouted to domestic backup, "
                f"{emergency_pauses} paused. Net margin delta: ${total_margin_delta:+.2f}."
            ),
        }
