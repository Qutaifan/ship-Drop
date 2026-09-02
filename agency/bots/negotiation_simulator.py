"""Hermes Autonomous Supplier Negotiation Simulator: Models volume tiers, counteroffers, and negotiation briefs."""
from __future__ import annotations

from typing import Any, Dict, List, Optional


class SupplierNegotiationSimulator:
    """Simulates supplier volume-tier cost curves and drafts data-backed negotiation proposals."""

    @staticmethod
    def simulate_volume_tiers(
        supplier_id: str,
        sku: str,
        current_product_cost: float,
        current_shipping_cost: float,
        monthly_volume: int = 150,
    ) -> Dict[str, Any]:
        """Calculates volume discount scenarios and factory counteroffer boundaries."""
        tiers = [
            {"tier_name": "TIER_1_ON_DEMAND", "min_moq": 1, "max_moq": 49, "discount_pct": 0.0},
            {"tier_name": "TIER_2_COMMITTED_BUFFER", "min_moq": 50, "max_moq": 199, "discount_pct": 6.5},
            {"tier_name": "TIER_3_DOMESTIC_PRESTOCK", "min_moq": 200, "max_moq": 499, "discount_pct": 12.0},
            {"tier_name": "TIER_4_WHOLESALE_SCALE", "min_moq": 500, "max_moq": 9999, "discount_pct": 18.5},
        ]

        scenarios = []
        for t in tiers:
            d_pct = t["discount_pct"]
            discounted_cost = round(current_product_cost * (1.0 - (d_pct / 100.0)), 2)
            unit_saving = round(current_product_cost - discounted_cost, 2)
            monthly_saving = round(unit_saving * monthly_volume, 2)
            annual_saving = round(monthly_saving * 12.0, 2)

            scenarios.append({
                "tier": t["tier_name"],
                "moq_range": f"{t['min_moq']}-{t['max_moq']}",
                "discount_percent": d_pct,
                "target_unit_cost": discounted_cost,
                "landed_cost": round(discounted_cost + current_shipping_cost, 2),
                "monthly_savings": monthly_saving,
                "annual_savings": annual_saving,
            })

        # Match current volume to optimal target tier
        target_tier = scenarios[1] if monthly_volume < 200 else scenarios[2] if monthly_volume < 500 else scenarios[3]

        # Draft professional negotiation message for supplier
        pitch_dialogue = (
            f"Hello Supplier Agent,\n\n"
            f"We are scaling our domestic marketing campaigns for SKU '{sku}'. "
            f"Our live run-rate is currently tracking at approximately {monthly_volume} units per month, "
            f"with planned scaling to 300+ units within 60 days.\n\n"
            f"To consolidate 100% of our order volume with your domestic warehouse, we are requesting a volume-tier "
            f"unit price of ${target_tier['target_unit_cost']:.2f} (a {target_tier['discount_percent']}% discount "
            f"from current ${current_product_cost:.2f}). In return, we are prepared to commit to consistent daily automated "
            f"fulfillment batches and priority reorders.\n\n"
            f"Please confirm if you can lock in this tier for our account."
        )

        return {
            "supplier_id": supplier_id,
            "sku": sku,
            "current_product_cost": current_product_cost,
            "current_shipping_cost": current_shipping_cost,
            "monthly_volume_projection": monthly_volume,
            "target_negotiation_tier": target_tier["tier"],
            "projected_annual_margin_expansion": target_tier["annual_savings"],
            "volume_scenarios": scenarios,
            "negotiation_brief": {
                "strategy": "Volume-commitment lock-in with pre-stock incentive",
                "recommended_ask_cost": target_tier["target_unit_cost"],
                "walkaway_ceiling_cost": round(current_product_cost * 0.96, 2),
                "copy_ready_pitch": pitch_dialogue,
            },
        }
