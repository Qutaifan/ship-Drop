"""Hermes Sourcing Ranker: Evaluates, tiers, and prioritizes competing suppliers in real-time."""
from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from agency.bots.supplier_verification_bot import compute_stability_score
from agency.core.margin_reconciler import reconcile_margins

ROOT = Path(__file__).resolve().parents[2]


def calculate_actionability_score(
    stability_score: float,
    margin_delta: float,
    retail_price: float,
    severity: str = "MEDIUM",
) -> float:
    """Computes urgency/actionability score (0.0 - 100.0) based on stability and margin impact."""
    sev_weight = {"HIGH": 1.2, "MEDIUM": 1.0, "LOW": 0.7}.get(severity.upper(), 1.0)
    stability_penalty = max(0.0, 1.0 - stability_score)
    margin_ratio = abs(margin_delta) / retail_price if retail_price > 0 else 0.0
    raw_score = sev_weight * stability_penalty * 100.0 * (1.0 + margin_ratio)
    return round(min(100.0, max(0.0, raw_score)), 1)


def determine_supplier_tier(
    stability: float,
    metrics: Dict[str, Any],
    is_domestic: bool,
    reconciliation_status: str,
) -> str:
    """Classifies supplier into one of four operational tiers."""
    stock = metrics.get("stock_level", 0)
    lead_max = metrics.get("lead_days_max", 14)
    defect_rate = metrics.get("defect_rate_percent", 5.0)
    margin = metrics.get("projected_net_margin", 0.0)

    # 1. Unviable check
    if stock < 30 or margin < 10.00 or stability < 0.40:
        return "REJECTED_UNVIABLE"

    # 2. Preferred Domestic
    if is_domestic and stability >= 0.85 and lead_max <= 5 and defect_rate <= 2.0 and margin >= 10.00 and stock >= 100 and reconciliation_status != "MARGIN_COMPRESSED":
        return "PREFERRED_DOMESTIC"

    # 3. Qualified Backup
    if is_domestic and stability >= 0.75 and lead_max <= 7 and margin >= 10.00:
        return "QUALIFIED_BACKUP"

    # 4. Otherwise High Risk / Monitor (international transit or moderate stability)
    return "HIGH_RISK_MONITOR"


class SourcingRanker:
    @staticmethod
    def rank_candidate_suppliers(
        candidate: Dict[str, Any],
        verifications: Optional[List[Dict[str, Any]]] = None,
        primary_metric: str = "stability_score",
    ) -> Dict[str, Any]:
        """Ranks all candidate supplier options for a product and emits a validated Sourcing Ranker payload."""
        cid = candidate.get("candidate_id", "cand-unknown")
        market = "US" if "us" in candidate.get("market_config_id", "us-pilot").lower() else "EU"
        econ = candidate.get("unit_economics", {})
        retail = float(econ.get("gross_selling_price", 29.99))

        raw_suppliers = candidate.get("supplier_evidence", [])
        if not raw_suppliers:
            # Fallback default supplier if none attached
            raw_suppliers = [{
                "supplier_name": "Primary Domestic Hub",
                "supplier_id": "primary-domestic-hub",
                "warehouse_country": "US" if market == "US" else "DE",
                "warehouse_type": "domestic",
                "quoted_product_cost": float(econ.get("product_cost", 6.00)),
                "quoted_shipping_cost": float(econ.get("shipping_cost", 3.50)),
                "shipping_method": "USPS" if market == "US" else "EU DPD",
                "lead_days_min": 3,
                "lead_days_max": 5,
                "defect_rate_percent": 1.2,
                "stock_level": 300,
            }]

        ranked_list: List[Dict[str, Any]] = []

        for sup in raw_suppliers:
            sup_id = sup.get("supplier_id", sup.get("supplier_name", "sup-unknown").lower().replace(" ", "-"))
            wh_country = sup.get("warehouse_country", "US" if market == "US" else "DE")
            wh_type = sup.get("warehouse_type", "domestic" if wh_country in ["US", "DE", "PL", "FR", "NL"] else "international_transit")
            is_dom = (wh_type == "domestic")

            # Check if recent verified telemetry exists
            matched_ver = None
            if verifications:
                for v in verifications:
                    if v.get("supplier_id") == sup_id:
                        matched_ver = v
                        break
                if not matched_ver:
                    for v in verifications:
                        if v.get("candidate_id") == cid and not v.get("supplier_id"):
                            matched_ver = v
                            break

            cost = float(matched_ver.get("verified_product_cost") if matched_ver else sup.get("quoted_product_cost", econ.get("product_cost", 6.00)))
            ship = float(matched_ver.get("verified_shipping_cost") if matched_ver else sup.get("quoted_shipping_cost", econ.get("shipping_cost", 3.50)))
            stock = int(matched_ver.get("stock_level") if matched_ver else sup.get("stock_level", 250))
            drift = float(matched_ver.get("price_drift_percent", 0.0)) if matched_ver else 0.0
            defect = float(matched_ver.get("defect_rate_percent") if matched_ver else sup.get("defect_rate_percent", 1.5))
            lead_max = int(matched_ver.get("lead_days_max") if matched_ver else sup.get("lead_days_max", 5 if is_dom else 14))
            packaging = str(matched_ver.get("packaging_type") if matched_ver else sup.get("packaging_type", "polybag"))

            # 1. Run margin reconciliation
            rec_input_ver = {
                "verified_product_cost": cost,
                "verified_shipping_cost": ship,
                "packaging_type": packaging,
                "warehouse_country": wh_country,
                "warehouse_type": wh_type,
                "duty_percent": 0.0,
            }
            recon_res = reconcile_margins(econ, rec_input_ver)
            rec_econ = recon_res["reconciled_economics"]
            net_margin = rec_econ["reconciled_net_margin"]
            landed_cost = rec_econ["total_landed_cost"]
            cogs_mult = rec_econ["cogs_multiple"]
            recon_status = recon_res["status"]

            # 2. Compute stability score
            stab_score = compute_stability_score(drift, stock, defect, wh_type)

            # 3. Actionability / Urgency score
            act_score = calculate_actionability_score(stab_score, recon_res["margin_delta"], retail)

            metrics_obj = {
                "landed_cost": landed_cost,
                "projected_net_margin": net_margin,
                "cogs_multiple": cogs_mult,
                "stock_level": stock,
                "lead_days_max": lead_max,
                "warehouse_country": wh_country,
                "warehouse_type": wh_type,
                "defect_rate_percent": defect,
            }

            tier = determine_supplier_tier(stab_score, metrics_obj, is_dom, recon_status)
            canary_ok = (tier == "PREFERRED_DOMESTIC" and stab_score >= 0.85 and stock >= 100)

            ranked_list.append({
                "supplier_id": sup_id,
                "supplier_name": sup.get("supplier_name", sup_id),
                "stability_score": stab_score,
                "actionability_score": act_score,
                "metrics": metrics_obj,
                "tier": tier,
                "canary_eligible": canary_ok,
                "reconciliation_status": recon_status,
            })

        # Sort by primary metric
        if primary_metric == "net_margin":
            ranked_list.sort(key=lambda s: s["metrics"]["projected_net_margin"], reverse=True)
        elif primary_metric == "lead_time":
            ranked_list.sort(key=lambda s: s["metrics"]["lead_days_max"])
        else:
            # Default: stability score descending, then margin descending
            ranked_list.sort(key=lambda s: (s["stability_score"], s["metrics"]["projected_net_margin"]), reverse=True)

        from agency.core.supplier_allocator import SupplierAllocator
        alloc_res = SupplierAllocator.compute_allocation(ranked_list)
        alloc_map = alloc_res.get("allocations", {})

        # Assign ranks & allocation percentages
        for idx, item in enumerate(ranked_list, start=1):
            item["rank"] = idx
            item["allocation_percent"] = alloc_map.get(item["supplier_id"], 0.0)

        top_choice = alloc_res.get("primary_supplier_id") or ranked_list[0]["supplier_id"]
        primary_alloc = alloc_map.get(top_choice, 100.0)

        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        return {
            "$schema": "../schemas/sourcing_ranker.schema.json",
            "version": "1.0.0",
            "candidate_id": cid,
            "ranked_at": now,
            "evaluation_market": market,
            "primary_ranking_metric": primary_metric,
            "suppliers": ranked_list,
            "selected_supplier_id": top_choice,
            "recommended_allocation_percent": primary_alloc,
            "allocation_strategy": alloc_res.get("strategy", "SINGLE_SOURCE"),
            "allocations": alloc_map,
            "ranking_notes": f"Automated ranking produced across {len(ranked_list)} supplier option(s). Top selection: {top_choice} (Strategy: {alloc_res.get('strategy')}).",
        }
