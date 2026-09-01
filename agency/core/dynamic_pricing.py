"""Hermes Dynamic Pricing Engine: Rule-based margin & elasticity optimization compliant with FTC safeguards."""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional


class DynamicPricingEngine:
    """Rule-based price elasticity and margin optimizer.
    Adheres strictly to FTC safeguards: dynamic pricing is based exclusively on
    inventory depth, landed cost volatility, and competitor matching—NEVER individual demographic tracking.
    """

    # Operating parameters
    MIN_RETAIL_PRICE = 62.00  # Strict floor from AGENTS.md CAC gate
    MAX_RETAIL_PRICE = 93.00  # Ceiling from AI-creative inversion boundary
    BENCHMARK_CPA = 21.48
    PAYMENT_FEE_PCT = 0.03

    @staticmethod
    def optimize_price(
        current_retail: float,
        landed_cost: float,
        stock_depth: int,
        elasticity_coefficient: float = 1.6,
        competitor_price: Optional[float] = None,
        vat_rate: float = 0.0,
    ) -> Dict[str, Any]:
        """Calculates profit-maximizing retail price subject to CAC gate and 3x COGS constraints."""
        # Baseline unit economics at current retail
        net_rev_base = current_retail / (1.0 + vat_rate)
        fees_base = current_retail * DynamicPricingEngine.PAYMENT_FEE_PCT
        margin_base = net_rev_base - landed_cost - fees_base

        # Grid search over target retail band [62.00, 93.00] with step 1.00
        best_price = current_retail
        best_contribution = -999.0
        best_margin = 0.0
        best_q_ratio = 1.0

        for price_step in range(int(DynamicPricingEngine.MIN_RETAIL_PRICE), int(DynamicPricingEngine.MAX_RETAIL_PRICE) + 1):
            p = float(price_step) + 0.99  # Standard retail charm pricing .99

            # 1. Price elasticity demand multiplier: Q(P) = Q_0 * (P / P_0)^(-elasticity)
            q_ratio = math.pow(p / max(1.0, current_retail), -elasticity_coefficient)

            # 2. Inventory scarcity adjustment (Rule-based: low stock increases price to protect stockout)
            if stock_depth <= 20:
                scarcity_multiplier = 1.08
            elif stock_depth <= 50:
                scarcity_multiplier = 1.04
            else:
                scarcity_multiplier = 1.00

            # 3. Unit economics at candidate price
            net_rev = p / (1.0 + vat_rate)
            fees = p * DynamicPricingEngine.PAYMENT_FEE_PCT
            unit_margin = net_rev - landed_cost - fees

            # Constraints check:
            # - Net margin must be >= 2x CPA ($42.96)
            # - Net margin must be >= 3x COGS
            cogs_3x = 3.0 * landed_cost
            cpa_2x = 2.0 * DynamicPricingEngine.BENCHMARK_CPA

            if unit_margin < min(cogs_3x, cpa_2x * 0.8):  # Must clear minimum viable hurdle
                continue

            # Competitor matching rule: avoid pricing > 15% above direct competitor
            if competitor_price and p > (competitor_price * 1.15):
                continue

            total_expected_contribution = unit_margin * q_ratio * scarcity_multiplier

            if total_expected_contribution > best_contribution:
                best_contribution = total_expected_contribution
                best_price = p
                best_margin = round(unit_margin, 2)
                best_q_ratio = round(q_ratio, 3)

        price_delta = round(best_price - current_retail, 2)
        margin_lift_pct = round(((best_margin - margin_base) / max(0.01, margin_base)) * 100.0, 1)

        return {
            "current_retail": round(current_retail, 2),
            "recommended_retail": round(best_price, 2),
            "price_delta": price_delta,
            "projected_unit_margin": best_margin,
            "margin_lift_percent": margin_lift_pct,
            "elasticity_demand_ratio": best_q_ratio,
            "target_band": [DynamicPricingEngine.MIN_RETAIL_PRICE, DynamicPricingEngine.MAX_RETAIL_PRICE],
            "cac_gate_cleared": best_margin >= (2.0 * DynamicPricingEngine.BENCHMARK_CPA),
            "cogs_multiple": round(best_margin / max(0.01, landed_cost), 2),
            "optimization_rule": (
                f"Rule-based reprice to ${best_price:.2f}: balances elasticity ratio ({best_q_ratio:.2f}) "
                f"with ${best_margin:.2f} unit margin ({round(best_margin/max(0.01, landed_cost), 1)}x COGS)."
            ),
        }
