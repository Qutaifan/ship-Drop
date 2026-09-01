"""Hermes Predictive Drift Engine: Forecasts stability collapse and drift velocity before degradation occurs."""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional


class PredictiveDriftEngine:
    """Multi-agent predictive drift modeling combining volatility, burn rates, and acceleration curves."""

    @staticmethod
    def evaluate_predictive_drift(
        stability_history: List[float],
        stock_history: List[int],
        cost_history: List[float],
        defect_history: List[float],
        audit_interval_hours: float = 4.0,
        demand_side_pressure_score: float = 0.0,
    ) -> Dict[str, Any]:
        """Calculates multi-dimensional predictive drift metrics."""
        n = len(stability_history)
        if n < 2:
            return {
                "predictive_drift_score": 5.0,
                "collapse_probability": 0.02,
                "stockout_horizon_days": 999,
                "cost_inflation_weekly_percent": 0.0,
                "defect_acceleration": 0.0,
                "demand_side_pressure_score": demand_side_pressure_score,
                "action_recommendation": "STABLE",
                "risk_tier": "LOW",
                "reasons": [],
            }

        # 1. Stability trajectory & collapse probability
        stab_deltas = [stability_history[i] - stability_history[i - 1] for i in range(1, n)]
        avg_stab_delta_per_audit = sum(stab_deltas) / len(stab_deltas)
        current_stab = stability_history[-1]

        # 7-day projection (42 audits at 4h cadence)
        audits_in_7d = int(7 * 24 / max(1.0, audit_interval_hours))
        projected_stab_7d = max(0.0, min(1.0, current_stab + (avg_stab_delta_per_audit * audits_in_7d)))

        # Sigmoid collapse probability centered at 0.75 threshold
        # If projected_stab_7d is 0.75, P = 0.50; if < 0.65, P -> 1.0; if > 0.85, P -> 0.0
        z = (0.75 - projected_stab_7d) * 12.0
        collapse_probability = round(1.0 / (1.0 + math.exp(-z)), 3)

        # 2. Stock runout horizon
        stock_deltas = [stock_history[i] - stock_history[i - 1] for i in range(1, n)]
        avg_stock_burn_per_audit = -sum(stock_deltas) / len(stock_deltas)
        current_stock = stock_history[-1]

        if avg_stock_burn_per_audit > 0:
            audits_to_zero = current_stock / avg_stock_burn_per_audit
            stockout_horizon_days = max(1, int(round((audits_to_zero * audit_interval_hours) / 24.0)))
        else:
            stockout_horizon_days = 999

        # 3. Cost inflation velocity (compounded weekly)
        cost_deltas = [cost_history[i] - cost_history[i - 1] for i in range(1, n)]
        avg_cost_delta = sum(cost_deltas) / len(cost_deltas)
        current_cost = cost_history[-1]
        weekly_cost_delta = avg_cost_delta * audits_in_7d
        cost_inflation_weekly_pct = round((weekly_cost_delta / current_cost) * 100.0, 2) if current_cost > 0 else 0.0

        # 4. Defect acceleration
        defect_deltas = [defect_history[i] - defect_history[i - 1] for i in range(1, n)]
        defect_acceleration = round(sum(defect_deltas) / len(defect_deltas), 3)

        # 5. Composite Predictive Drift Score (0.0 - 100.0)
        p_score = (collapse_probability * 40.0)
        p_score += (min(25.0, (14.0 / max(1, stockout_horizon_days)) * 25.0) if stockout_horizon_days <= 14 else 0.0)
        p_score += (min(15.0, max(0.0, cost_inflation_weekly_pct * 1.5)))
        p_score += (min(10.0, max(0.0, defect_acceleration * 20.0)))
        p_score += (min(10.0, max(0.0, demand_side_pressure_score * 0.10)))
        composite_score = round(min(100.0, max(0.0, p_score)), 1)

        # Recommendation
        reasons = []
        if demand_side_pressure_score >= 60.0:
            reasons.append(f"Elevated Meta DSA competitor pressure ({demand_side_pressure_score:.1f}/100) accelerating margin compression")

        if composite_score >= 60.0 or collapse_probability >= 0.70 or stockout_horizon_days <= 5:
            recommendation = "PREEMPTIVE_SWITCH_URGENT"
            risk_tier = "CRITICAL_PREEMPTIVE"
            if collapse_probability >= 0.70:
                reasons.append(f"Stability collapse probability is {collapse_probability:.1%} within 7 days")
            if stockout_horizon_days <= 5:
                reasons.append(f"Stockout imminent in {stockout_horizon_days} days")
        elif composite_score >= 35.0 or stockout_horizon_days <= 14 or cost_inflation_weekly_pct >= 5.0:
            recommendation = "MONITOR_TIGHTEN_CADENCE"
            risk_tier = "ELEVATED"
            reasons.append("Moderate drift momentum detected; tighten audit schedule to 1 hour")
        else:
            recommendation = "STABLE"
            risk_tier = "LOW"
            reasons.append("All predictive drift vectors within safe operating parameters")

        return {
            "predictive_drift_score": composite_score,
            "collapse_probability": collapse_probability,
            "projected_stability_7d": projected_stab_7d,
            "stockout_horizon_days": stockout_horizon_days,
            "cost_inflation_weekly_percent": cost_inflation_weekly_pct,
            "defect_acceleration": defect_acceleration,
            "action_recommendation": recommendation,
            "risk_tier": risk_tier,
            "reasons": reasons,
        }
