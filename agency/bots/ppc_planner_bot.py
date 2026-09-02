"""Hermes Cross-Platform E-Commerce PPC Strategy Planner Bot.

Implements Mode A (Build from scratch) and Mode B (Optimize live campaigns)
across Google Shopping, Meta Ads, and TikTok Ads using quantitative ROAS math.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

PLATFORM_BENCHMARKS = {
    "google": {"name": "Google Ads (Shopping / PMax)", "avg_roas": 4.5, "top_roas": 6.0, "best_for": "High-intent searchers"},
    "meta": {"name": "Meta Ads (FB/IG Advantage+)", "avg_roas": 2.2, "top_roas": 4.5, "best_for": "Visual aesthetics & retargeting"},
    "tiktok": {"name": "TikTok Ads (Spark / Video)", "avg_roas": 1.4, "top_roas": 2.2, "best_for": "Viral discovery & demo proof"},
}


class PPCPlannerBot:
    """PPC Strategy Planner: Determines channel allocation, ROAS targets, and campaign architecture."""

    @classmethod
    def calculate_financial_framework(cls, retail: float, landed: float, payment_fee_pct: float = 0.03) -> Dict[str, Any]:
        """Calculates Break-even ROAS, Target ROAS, Max CPA, and CAC gate status."""
        retail = max(1.0, float(retail))
        fee = round(retail * payment_fee_pct, 2)
        gross_margin = round(retail - landed - fee, 2)
        margin_pct = max(0.01, round(gross_margin / retail, 4))

        break_even_roas = round(1.0 / margin_pct, 2)
        target_roas = round(break_even_roas * 1.65, 2)
        max_cpa = gross_margin
        target_cpa = round(max_cpa * 0.65, 2)
        cac_gate_cleared = gross_margin >= 42.96  # 2x $21.48 median CPA gate

        # US 24.2% landed cost rule check
        landed_ratio_pct = round((landed / retail) * 100.0, 1)
        us_landed_rule_passed = landed_ratio_pct <= 24.2

        return {
            "retail_price": retail,
            "landed_cost": landed,
            "payment_fee": fee,
            "gross_margin_usd": gross_margin,
            "profit_margin_percent": round(margin_pct * 100.0, 1),
            "landed_cost_ratio_percent": landed_ratio_pct,
            "us_24pct_landed_rule_passed": us_landed_rule_passed,
            "break_even_roas": break_even_roas,
            "target_roas": target_roas,
            "max_cpa_usd": max_cpa,
            "target_cpa_usd": target_cpa,
            "cac_gate_cleared": cac_gate_cleared,
        }

    @classmethod
    def build_strategy(
        cls,
        product_name: str,
        retail: float,
        landed: float,
        monthly_budget: float = 1500.0,
        product_type: str = "demo",
    ) -> Dict[str, Any]:
        """Mode A: Builds multi-platform cross-channel launch strategy from scratch."""
        fin = cls.calculate_financial_framework(retail=retail, landed=landed)
        p_type = product_type.lower()

        # Platform budget allocation split
        if "search" in p_type or "utility" in p_type:
            split = {"google": 0.55, "meta": 0.30, "tiktok": 0.15}
            primary_channel = "Google Shopping & Performance Max"
        elif "visual" in p_type or "lifestyle" in p_type:
            split = {"meta": 0.55, "tiktok": 0.30, "google": 0.15}
            primary_channel = "Meta Advantage+ Shopping & Instagram Reels"
        else:  # Demo / problem solver
            split = {"tiktok": 0.60, "meta": 0.25, "google": 0.15}
            primary_channel = "TikTok Video Ads & Spark Ads"

        allocations = {}
        for plat, pct in split.items():
            b_amt = round(monthly_budget * pct, 2)
            daily = round(b_amt / 30.0, 2)
            bench = PLATFORM_BENCHMARKS[plat]
            projected_rev = round(b_amt * bench["avg_roas"], 2)
            allocations[plat] = {
                "platform_name": bench["name"],
                "allocation_percent": round(pct * 100.0, 1),
                "monthly_budget_usd": b_amt,
                "daily_budget_usd": daily,
                "benchmark_roas": bench["avg_roas"],
                "projected_gross_revenue": projected_rev,
                "best_for": bench["best_for"],
            }

        total_projected_rev = round(sum(a["projected_gross_revenue"] for a in allocations.values()), 2)
        blended_roas = round(total_projected_rev / max(1.0, monthly_budget), 2)
        projected_profit = round(total_projected_rev * (fin["profit_margin_percent"] / 100.0) - monthly_budget, 2)

        return {
            "mode": "BUILD_STRATEGY",
            "product_name": product_name,
            "product_type": product_type,
            "primary_channel": primary_channel,
            "monthly_budget_usd": monthly_budget,
            "financial_framework": fin,
            "platform_allocations": allocations,
            "projected_monthly_revenue": total_projected_rev,
            "projected_monthly_net_profit": projected_profit,
            "blended_projected_roas": blended_roas,
        }

    @classmethod
    def optimize_campaigns(cls, current_performance: List[Dict[str, Any]], target_roas: float = 2.0) -> Dict[str, Any]:
        """Mode B: Audits live performance across platforms and generates rebalancing actions."""
        total_spend = 0.0
        total_revenue = 0.0
        audited_platforms = []

        for p in current_performance:
            name = p.get("platform", "unknown")
            spend = float(p.get("spend", 0.0))
            revenue = float(p.get("revenue", 0.0))
            conversions = int(p.get("conversions", 0))

            total_spend += spend
            total_revenue += revenue
            roas = round(revenue / spend, 2) if spend > 0 else 0.0
            cpa = round(spend / conversions, 2) if conversions > 0 else spend

            if roas >= target_roas * 1.25:
                action = "SCALE_BUDGET (+20% every 48h)"
                recommendation = "Top performer generating sovereign cashflow. Scale winning hooks."
            elif roas >= target_roas:
                action = "MAINTAIN & ITERATE"
                recommendation = "Profitable. Test new hook variations to counter creative fatigue."
            elif roas >= target_roas * 0.75:
                action = "OPTIMIZE_OR_TRIM"
                recommendation = "Near break-even. Trim high-CPA placements and refresh UGC."
            else:
                action = "CUT_OR_PAUSE (-50% or kill)"
                recommendation = "Bleeding capital below break-even. Reallocate budget to winning channels."

            audited_platforms.append({
                "platform": name,
                "spend": spend,
                "revenue": revenue,
                "conversions": conversions,
                "actual_roas": roas,
                "actual_cpa": cpa,
                "action": action,
                "recommendation": recommendation,
            })

        blended_roas = round(total_revenue / total_spend, 2) if total_spend > 0 else 0.0

        return {
            "mode": "OPTIMIZE_CAMPAIGNS",
            "total_spend": round(total_spend, 2),
            "total_revenue": round(total_revenue, 2),
            "blended_roas": blended_roas,
            "target_roas": target_roas,
            "platforms": audited_platforms,
        }
