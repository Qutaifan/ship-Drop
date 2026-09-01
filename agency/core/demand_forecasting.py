"""Hermes Demand Forecasting Module: Integrates paid ad performance, search momentum, and inventory velocity."""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional


class DemandForecastingEngine:
    """Predicts forward order demand from ad spend, CVR, search volume momentum, and seasonality."""

    @staticmethod
    def forecast_demand(
        daily_ad_spend: float,
        cpc: float,
        predicted_cvr_percent: float,
        search_momentum_score: float = 50.0,
        seasonality_factor: float = 1.0,
        current_stock: int = 100,
        lead_time_days: int = 5,
        dsa_demand_multiplier: float = 1.0,
    ) -> Dict[str, Any]:
        """Calculates expected weekly/monthly order volume and reorder point."""
        # Estimated daily clicks from ad budget
        effective_cpc = max(0.20, cpc)
        daily_clicks = daily_ad_spend / effective_cpc

        # Expected daily orders from paid traffic
        cvr_dec = max(0.005, predicted_cvr_percent / 100.0)
        daily_paid_orders = daily_clicks * cvr_dec

        # Organic search momentum multiplier (momentum score 50 = 1.0x baseline, 100 = 1.3x)
        organic_uplift = 1.0 + (max(0.0, min(100.0, search_momentum_score) - 50.0) / 200.0)

        # Total adjusted daily demand including Meta DSA competitor validation multiplier
        daily_demand = daily_paid_orders * organic_uplift * seasonality_factor * dsa_demand_multiplier
        weekly_demand = int(round(daily_demand * 7.0))
        monthly_demand = int(round(daily_demand * 30.0))

        # Reorder Point (ROP) = (Lead Time in Days * Daily Demand) + Safety Buffer
        # Safety buffer = 3 days of peak demand
        safety_stock = int(round(daily_demand * 3.0))
        reorder_point = max(10, int(round((lead_time_days * daily_demand) + safety_stock)))

        days_runway = int(round(current_stock / max(0.1, daily_demand)))
        reorder_needed = current_stock <= reorder_point

        return {
            "daily_demand_units": round(daily_demand, 1),
            "weekly_demand_units": weekly_demand,
            "monthly_demand_units": monthly_demand,
            "reorder_point_units": max(10, reorder_point),
            "safety_stock_units": max(5, safety_stock),
            "current_stock_units": current_stock,
            "inventory_runway_days": days_runway,
            "reorder_needed": reorder_needed,
            "ad_channel_metrics": {
                "daily_clicks": round(daily_clicks, 1),
                "expected_cpa": round(daily_ad_spend / max(0.1, daily_demand), 2),
                "organic_uplift_multiplier": round(organic_uplift, 2),
                "seasonality_factor": seasonality_factor,
            },
        }
