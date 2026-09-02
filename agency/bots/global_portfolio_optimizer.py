"""Hermes Global Portfolio Optimizer: Macro-level capital allocation, demand balancing, and margin maximization."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from agency.core.demand_forecasting import DemandForecastingEngine
from agency.core.dynamic_pricing import DynamicPricingEngine
from agency.core.sourcing_ranker import SourcingRanker
from agency.core.store import Store


class GlobalPortfolioOptimizer:
    """The 'Brain Above the Brain': Optimizes pricing, capital allocation, and supplier stability across all catalog SKUs."""

    def __init__(self, store: Optional[Store] = None):
        self.store = store or Store()

    def optimize_portfolio(self, total_monthly_marketing_budget: float = 3000.0) -> Dict[str, Any]:
        """Runs holistic portfolio-wide optimization across pricing, demand, and risk."""
        candidates = self.store.list_candidates()
        if not candidates:
            return {"status": "EMPTY_PORTFOLIO", "message": "No candidates available for portfolio optimization."}

        verifications = self.store.list_supplier_verifications(limit=200)

        optimized_skus = []
        total_projected_orders = 0
        total_projected_net_margin = 0.0
        total_projected_revenue = 0.0
        stability_accumulator = 0.0

        # Evaluate each SKU
        for cand in candidates:
            cid = cand.get("candidate_id", "cand-unknown")
            econ = cand.get("unit_economics", {})
            current_retail = float(econ.get("gross_selling_price", 79.99))
            landed = float(econ.get("product_cost", 10.0)) + float(econ.get("shipping_cost", 4.0))

            # 1. Rank suppliers
            rank_res = SourcingRanker.rank_candidate_suppliers(cand, verifications=verifications)
            top_sup = rank_res["suppliers"][0] if rank_res.get("suppliers") else None
            stab = top_sup["stability_score"] if top_sup else 0.90
            stock = top_sup["metrics"]["stock_level"] if top_sup else 200

            # 2. Extract competitor signals from competitor evidence (DSA ads)
            comp_evidence = cand.get("competitor_evidence", [])
            comp_prices = [float(e["observed_price"]) for e in comp_evidence if e.get("observed_price")]
            median_comp_price = sorted(comp_prices)[len(comp_prices) // 2] if comp_prices else None
            aged_comp_count = sum(1 for e in comp_evidence if e.get("confidence") == "high")
            dsa_multiplier = round(1.0 + min(0.40, aged_comp_count * 0.05), 2)

            # 3. Dynamic Pricing optimization with competitor band guardrail
            pricing = DynamicPricingEngine.optimize_price(
                current_retail=current_retail,
                landed_cost=landed,
                stock_depth=stock,
                competitor_price=median_comp_price,
            )

            # 4. Demand Forecasting weighted by Meta DSA demand multiplier
            sku_daily_budget = (total_monthly_marketing_budget / max(1, len(candidates))) / 30.0
            demand = DemandForecastingEngine.forecast_demand(
                daily_ad_spend=sku_daily_budget,
                cpc=0.85,
                predicted_cvr_percent=2.2,
                current_stock=stock,
                dsa_demand_multiplier=dsa_multiplier,
            )

            m_units = demand["monthly_demand_units"]
            unit_margin = pricing["projected_unit_margin"]
            sku_net_profit = round(m_units * unit_margin, 2)
            sku_rev = round(m_units * pricing["recommended_retail"], 2)

            total_projected_orders += m_units
            total_projected_net_margin += sku_net_profit
            total_projected_revenue += sku_rev
            stability_accumulator += stab

            optimized_skus.append({
                "candidate_id": cid,
                "product_name": cand.get("product_name", cid),
                "primary_supplier": top_sup["supplier_name"] if top_sup else "N/A",
                "stability_score": stab,
                "current_retail": current_retail,
                "optimized_retail": pricing["recommended_retail"],
                "unit_margin": unit_margin,
                "monthly_demand_units": m_units,
                "projected_monthly_margin": sku_net_profit,
                "inventory_runway_days": demand["inventory_runway_days"],
                "cogs_multiple": pricing["cogs_multiple"],
            })

        # Sort SKUs by monthly net profit contribution
        optimized_skus.sort(key=lambda s: s["projected_monthly_margin"], reverse=True)

        # Dynamic capital allocation: 50% to #1, 30% to #2, 20% distributed to remaining
        for idx, sku in enumerate(optimized_skus):
            if idx == 0:
                sku["allocated_ad_budget_pct"] = 50.0
            elif idx == 1:
                sku["allocated_ad_budget_pct"] = 30.0
            else:
                remaining_pct = 20.0 / max(1, len(optimized_skus) - 2)
                sku["allocated_ad_budget_pct"] = round(remaining_pct, 1)

        avg_stability = round(stability_accumulator / max(1, len(candidates)), 2)

        return {
            "catalog_sku_count": len(candidates),
            "total_monthly_marketing_budget": total_monthly_marketing_budget,
            "portfolio_monthly_demand_orders": total_projected_orders,
            "portfolio_monthly_gross_revenue": round(total_projected_revenue, 2),
            "portfolio_monthly_net_margin": round(total_projected_net_margin, 2),
            "portfolio_average_stability": avg_stability,
            "blended_cogs_multiple": round(total_projected_net_margin / max(1.0, total_projected_revenue - total_projected_net_margin), 2),
            "skus": optimized_skus,
        }
