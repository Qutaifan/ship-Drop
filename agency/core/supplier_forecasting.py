"""Hermes Supplier Health Forecasting Module: Preemptively projects stability, stock depletion, and drift."""
from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class SupplierHealthForecaster:
    """Projects future supplier telemetry curves using linear velocity extrapolation."""

    @staticmethod
    def forecast_health(timeline_points: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculates 7-day stability projection, stock runout date, and inflation trajectory."""
        if not timeline_points:
            return {
                "forecast_valid": False,
                "reason": "Insufficient timeline data points",
                "current_metrics": {"stability": 0.90, "stock": 100, "lead_days": 5, "cost": 10.0},
                "projected_7d": {
                    "stability": 0.90,
                    "lead_days_max": 5,
                    "stock_runout_days": 999,
                    "price_acceleration_percent": 0.0,
                },
                "risk_tier": "LOW_RISK",
                "preemptive_switch_recommended": False,
            }

        # Sort chronologically
        pts = sorted(timeline_points, key=lambda x: x.get("ts", ""))
        latest = pts[-1]
        current_stab = float(latest.get("stability", 0.90))
        current_stock = int(latest.get("stock", 100))
        current_lead = int(latest.get("lead_days_max", 5))
        current_cost = float(latest.get("product_cost", 10.0))

        if len(pts) < 2:
            return {
                "forecast_valid": True,
                "confidence": 0.50,
                "current_metrics": {
                    "stability": current_stab,
                    "stock": current_stock,
                    "lead_days": current_lead,
                    "cost": current_cost,
                },
                "projected_7d": {
                    "stability": current_stab,
                    "lead_days_max": current_lead,
                    "stock_runout_days": 999,
                    "price_acceleration_percent": 0.0,
                },
                "risk_tier": "LOW_RISK",
                "preemptive_switch_recommended": False,
            }

        # Calculate deltas across the sample window
        oldest = pts[0]
        n_steps = max(1, len(pts) - 1)
        stab_delta_per_step = (current_stab - float(oldest.get("stability", current_stab))) / n_steps
        stock_delta_per_step = (current_stock - int(oldest.get("stock", current_stock))) / n_steps
        cost_delta_per_step = (current_cost - float(oldest.get("product_cost", current_cost))) / n_steps
        lead_delta_per_step = (current_lead - int(oldest.get("lead_days_max", current_lead))) / n_steps

        # 7-day projection (assuming ~4 audit cycles per day or normalized daily rate)
        # We normalize 1 step ≈ 4 hours (6 steps/day = 42 steps/week) or treat step as audit interval
        projected_stability_7d = round(max(0.0, min(1.0, current_stab + (stab_delta_per_step * 7.0))), 2)
        projected_lead_7d = max(1, int(round(current_lead + (lead_delta_per_step * 7.0))))

        # Stock runout days
        stock_burn_per_step = -stock_delta_per_step if stock_delta_per_step < 0 else 0.0
        if stock_burn_per_step > 0:
            stock_runout_steps = current_stock / stock_burn_per_step
            stock_runout_days = max(1, int(round(stock_runout_steps / 4.0)))  # 4 audits per day
        else:
            stock_runout_days = 999

        # Cost drift acceleration
        price_acceleration_pct = (
            round(((cost_delta_per_step * 7.0) / current_cost) * 100.0, 2)
            if current_cost > 0
            else 0.0
        )

        # Risk tier assignment
        preemptive_switch = False
        risk_tier = "LOW_RISK"
        reasons = []

        if projected_stability_7d < 0.75:
            risk_tier = "HIGH_RISK_PREEMPTIVE_SWITCH"
            preemptive_switch = True
            reasons.append(f"Projected 7-day stability ({projected_stability_7d:.2f}) falls below 0.75 floor")

        if stock_runout_days <= 7:
            risk_tier = "HIGH_RISK_PREEMPTIVE_SWITCH"
            preemptive_switch = True
            reasons.append(f"Critical stock runout projected in {stock_runout_days} day(s)")

        if not preemptive_switch and (projected_stability_7d < 0.82 or stock_runout_days <= 14 or price_acceleration_pct >= 5.0):
            risk_tier = "MEDIUM_RISK"
            reasons.append("Moderate stability drift or elevated cost acceleration")

        return {
            "forecast_valid": True,
            "confidence": 0.85 if len(pts) >= 3 else 0.65,
            "current_metrics": {
                "stability": current_stab,
                "stock": current_stock,
                "lead_days": current_lead,
                "cost": current_cost,
            },
            "projected_7d": {
                "stability": projected_stability_7d,
                "lead_days_max": projected_lead_7d,
                "stock_runout_days": stock_runout_days,
                "price_acceleration_percent": price_acceleration_pct,
            },
            "risk_tier": risk_tier,
            "preemptive_switch_recommended": preemptive_switch,
            "preemptive_switch_reasons": reasons,
        }
