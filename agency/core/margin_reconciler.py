"""Margin Reconciliation Engine - Reconciles theoretical candidate economics with verified supplier truth.

Pure mathematical calculations without side effects.
Features:
- Landed cost reconciliation (real product cost + real shipping + duty)
- Shipping volatility buffer (3-5%)
- Packaging cost uplift (custom box, kraft box, mailer)
- FX conversion support (USD/EUR/CNY)
- EU 2026 customs duty (€3 flat per item if China-direct) and VAT handling
- Margin compression detection
"""
from __future__ import annotations

from typing import Any, Dict, Optional


def calculate_packaging_uplift(packaging_type: str) -> float:
    """Returns packaging cost uplift based on package grade."""
    packaging_map = {
        "custom_box": 0.45,
        "kraft_box": 0.30,
        "bubble_mailer": 0.15,
        "polybag": 0.00,
    }
    return packaging_map.get(packaging_type.lower(), 0.00)


def reconcile_margins(
    unit_economics: Dict[str, Any],
    verification: Dict[str, Any],
    shipping_volatility_percent: float = 0.04,
    fx_rate_used: float = 1.0,
    fx_rate_source: str = "ECB_DAILY",
) -> Dict[str, Any]:
    """Pure function: Reconciles theoretical unit economics with verified supplier metrics."""
    retail = float(unit_economics.get("gross_selling_price", 29.99))
    currency = unit_economics.get("currency", "USD").upper()

    # 1. Verified Sourcing Costs
    raw_prod_cost = float(verification.get("verified_product_cost", unit_economics.get("product_cost", 6.00)))
    raw_ship_cost = float(verification.get("verified_shipping_cost", unit_economics.get("shipping_cost", 3.50)))
    duty_pct = float(verification.get("duty_percent", 0.0))
    pkg_type = verification.get("packaging_type", "polybag")
    wh_country = verification.get("warehouse_country", "US")
    wh_type = verification.get("warehouse_type", "domestic")

    # FX conversion
    base_prod_cost = round(raw_prod_cost * fx_rate_used, 2)

    # Shipping volatility buffer
    buffered_ship_cost = round(raw_ship_cost * (1.0 + shipping_volatility_percent), 2)

    # Duty calculation: 2026 EU anti-de-minimis rule: €3 flat per item if imported from non-EU origin
    if currency == "EUR" and wh_country != "DE" and wh_type != "domestic":
        duty = 3.00
    else:
        duty = round(base_prod_cost * (duty_pct / 100.0), 2)

    pkg_uplift = calculate_packaging_uplift(pkg_type)
    total_landed = round(base_prod_cost + buffered_ship_cost + duty + pkg_uplift, 2)

    # 2. Revenue & Net Margin Calculation
    vat_rate = 0.19 if currency == "EUR" else 0.00
    vat_inclusive_factor = 1.0 + vat_rate
    net_revenue_ex_vat = retail / vat_inclusive_factor

    payment_fee = round(0.03 * retail, 2)  # Charged on gross retail
    refund_allowance = float(unit_economics.get("refund_allowance", round(retail * 0.04, 2)))
    variable_support = float(unit_economics.get("variable_support_cost", 0.80))
    return_allowance = float(unit_economics.get("return_allowance", 1.20))
    packaging_base = float(unit_economics.get("packaging_cost", 1.00))

    fixed_deductions = payment_fee + refund_allowance + variable_support + return_allowance + packaging_base
    reconciled_margin = round(net_revenue_ex_vat - total_landed - fixed_deductions, 2)

    # Initial baseline comparison
    initial_margin = float(unit_economics.get("contribution_before_ads", unit_economics.get("expected_profit_per_order", 15.0)))
    margin_diff = round(reconciled_margin - initial_margin, 2)
    cogs_multiple = round(reconciled_margin / total_landed, 2) if total_landed > 0 else 0.0

    init_cogs = float(unit_economics.get("product_cost", 1.0)) + float(unit_economics.get("shipping_cost", 1.0))
    initial_cogs_multiple = round(initial_margin / init_cogs, 2) if init_cogs > 0 else 1.0

    break_even_cpa = max(0.0, reconciled_margin)
    target_cpa = round(break_even_cpa * 0.70, 2)
    expected_roas = round(retail / target_cpa, 2) if target_cpa > 0 else 0.0

    # Compression Detection: margin drops by >= $2.00, or healthy margin degrades below 2x COGS, or margin < $10
    compression_flag = (margin_diff <= -2.00) or (initial_cogs_multiple >= 2.0 and cogs_multiple < 2.0) or (reconciled_margin < 10.00)
    verdict = "MARGIN_COMPRESSED" if compression_flag else "MARGIN_STABLE"

    return {
        "status": verdict,
        "compression_flag": compression_flag,
        "margin_delta": margin_diff,
        "reconciled_economics": {
            "gross_selling_price": retail,
            "currency": currency,
            "verified_product_cost": base_prod_cost,
            "verified_shipping_cost": buffered_ship_cost,
            "shipping_volatility_buffer": round(buffered_ship_cost - raw_ship_cost, 2),
            "duty": duty,
            "packaging_uplift": pkg_uplift,
            "total_landed_cost": total_landed,
            "net_revenue_ex_vat": round(net_revenue_ex_vat, 2),
            "reconciled_net_margin": reconciled_margin,
            "cogs_multiple": cogs_multiple,
            "break_even_cpa": break_even_cpa,
            "target_cpa": target_cpa,
            "expected_roas": expected_roas,
            "fx_rate_used": fx_rate_used,
            "fx_rate_source": fx_rate_source,
        },
        "initial_economics": {
            "initial_net_margin": initial_margin,
            "initial_product_cost": unit_economics.get("product_cost"),
            "initial_shipping_cost": unit_economics.get("shipping_cost"),
        },
    }


class MarginReconciler:
    """Class wrapper for managing candidate margin reconciliation."""

    def __init__(self, volatility_buffer: float = 0.04):
        self.volatility_buffer = volatility_buffer

    def reconcile_candidate(self, candidate: Dict[str, Any], verification: Dict[str, Any]) -> Dict[str, Any]:
        econ = candidate.get("unit_economics", {})
        return reconcile_margins(econ, verification, shipping_volatility_percent=self.volatility_buffer)
