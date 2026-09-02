#!/usr/bin/env python3
"""
US Logistics Coordinator — find cheapest/fastest shipping to maximize margins.

Compares carriers (USPS, UPS, FedEx, regional), zones, service levels.
Outputs optimal shipping choice per destination for margin optimization.
"""
import argparse
import json
from dataclasses import dataclass, asdict
from typing import List, Optional
from pathlib import Path


# ──────────────────────────────────────────────────────────────────────────────
# Carrier rate tables (simplified 2024/2025 base rates — UPDATE BEFORE PRODUCTION)
# Rates are PER PACKAGE for given weight/dimensions. Real rates need API integration.
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class PackageSpecs:
    weight_lb: float
    length_in: float
    width_in: float
    height_in: float
    value_usd: float = 0.0  # for insurance


@dataclass
class ShippingQuote:
    carrier: str
    service: str
    cost_usd: float
    transit_days: int
    tracking: bool
    insurance_included: bool
    notes: str = ""


# Simplified rate engine — replace with live API (EasyPost, Shippo, carrier APIs) for production
def get_quotes(origin_zip: str, dest_zip: str, pkg: PackageSpecs) -> List[ShippingQuote]:
    """
    Returns ranked quotes. In production, call carrier APIs (EasyPost/Shippo) or
    use negotiated rate tables. This is a simplified zone-based approximation.
    """
    # Zone approximation (1-8 for continental US)
    zone = _estimate_zone(origin_zip, dest_zip)
    dim_weight = (pkg.length_in * pkg.width_in * pkg.height_in) / 139  # UPS/FedEx dim divisor
    billable_weight = max(pkg.weight_lb, dim_weight)

    quotes = []

    # ─── USPS ───
    if billable_weight <= 1.0:
        quotes.append(ShippingQuote(
            carrier="USPS", service="First Class Package",
            cost_usd=round(4.50 + zone * 0.75, 2),
            transit_days=2 + zone, tracking=True, insurance_included=(pkg.value_usd <= 100),
            notes=f"Zone {zone}, billed at {billable_weight:.1f} lb"
        ))
    if billable_weight <= 70:
        quotes.append(ShippingQuote(
            carrier="USPS", service="Priority Mail",
            cost_usd=round(9.25 + zone * 1.20, 2),
            transit_days=1 + zone // 2, tracking=True, insurance_included=(pkg.value_usd <= 100),
            notes=f"Zone {zone}, flat-rate box may be cheaper"
        ))
        quotes.append(ShippingQuote(
            carrier="USPS", service="Priority Mail Express",
            cost_usd=round(28.00 + zone * 2.50, 2),
            transit_days=1, tracking=True, insurance_included=(pkg.value_usd <= 100),
            notes="Overnight to most zones"
        ))

    # ─── UPS (Ground / 3-Day Select / 2nd Day Air / Next Day Air) ───
    # Ground approx
    quotes.append(ShippingQuote(
        carrier="UPS", service="Ground",
        cost_usd=round(10.50 + zone * 1.50 + billable_weight * 0.80, 2),
        transit_days=1 + zone, tracking=True, insurance_included=(pkg.value_usd <= 100),
        notes=f"Zone {zone}, {billable_weight:.1f} lb billable"
    ))
    # 3-Day Select
    quotes.append(ShippingQuote(
        carrier="UPS", service="3-Day Select",
        cost_usd=round(18.00 + zone * 2.00 + billable_weight * 1.20, 2),
        transit_days=3, tracking=True, insurance_included=(pkg.value_usd <= 100),
        notes="Guaranteed 3 business days"
    ))
    # 2nd Day Air
    quotes.append(ShippingQuote(
        carrier="UPS", service="2nd Day Air",
        cost_usd=round(25.00 + zone * 3.00 + billable_weight * 1.80, 2),
        transit_days=2, tracking=True, insurance_included=(pkg.value_usd <= 100),
        notes="Guaranteed 2 business days"
    ))
    # Next Day Air
    quotes.append(ShippingQuote(
        carrier="UPS", service="Next Day Air",
        cost_usd=round(45.00 + zone * 5.00 + billable_weight * 2.50, 2),
        transit_days=1, tracking=True, insurance_included=(pkg.value_usd <= 100),
        notes="Guaranteed next business day"
    ))

    # ─── FedEx (Ground / Express Saver / 2Day / Overnight) ───
    quotes.append(ShippingQuote(
        carrier="FedEx", service="Ground",
        cost_usd=round(10.00 + zone * 1.40 + billable_weight * 0.75, 2),
        transit_days=1 + zone, tracking=True, insurance_included=(pkg.value_usd <= 100),
        notes=f"Zone {zone}, {billable_weight:.1f} lb billable"
    ))
    quotes.append(ShippingQuote(
        carrier="FedEx", service="Express Saver (3-Day)",
        cost_usd=round(17.00 + zone * 2.20 + billable_weight * 1.10, 2),
        transit_days=3, tracking=True, insurance_included=(pkg.value_usd <= 100),
        notes="3 business days"
    ))
    quotes.append(ShippingQuote(
        carrier="FedEx", service="2Day",
        cost_usd=round(24.00 + zone * 3.20 + billable_weight * 1.70, 2),
        transit_days=2, tracking=True, insurance_included=(pkg.value_usd <= 100),
        notes="2 business days"
    ))
    quotes.append(ShippingQuote(
        carrier="FedEx", service="Standard Overnight",
        cost_usd=round(42.00 + zone * 4.80 + billable_weight * 2.30, 2),
        transit_days=1, tracking=True, insurance_included=(pkg.value_usd <= 100),
        notes="Next business day"
    ))

    # ─── Regional / Consolidated (e.g., UPS SurePost, FedEx SmartPost, OnTrac, LSO) ───
    if billable_weight <= 5.0 and zone <= 5:
        quotes.append(ShippingQuote(
            carrier="UPS SurePost", service="USPS Final Mile",
            cost_usd=round(6.50 + zone * 0.90, 2),
            transit_days=2 + zone, tracking=True, insurance_included=False,
            notes="Economy, residential-friendly"
        ))
    if billable_weight <= 5.0 and zone <= 5:
        quotes.append(ShippingQuote(
            carrier="FedEx SmartPost", service="USPS Final Mile",
            cost_usd=round(6.00 + zone * 0.85, 2),
            transit_days=2 + zone, tracking=True, insurance_included=False,
            notes="Economy, residential-friendly"
        ))

    # Sort by cost ascending
    quotes.sort(key=lambda q: q.cost_usd)
    return quotes


def _estimate_zone(origin_zip: str, dest_zip: str) -> int:
    """Rough zone from first 3 digits. Production should use carrier zone charts."""
    try:
        o = int(origin_zip[:3])
        d = int(dest_zip[:3])
        diff = abs(o - d)
        if diff == 0: return 1
        if diff <= 50: return 2
        if diff <= 150: return 3
        if diff <= 300: return 4
        if diff <= 600: return 5
        if diff <= 1000: return 6
        if diff <= 1400: return 7
        return 8
    except:
        return 4  # default mid-zone


# ──────────────────────────────────────────────────────────────────────────────
# Margin integration
# ──────────────────────────────────────────────────────────────────────────────

def optimize_shipping_for_margin(
    retail: float,
    state_tax: float,
    product_cost: float,
    pkg: PackageSpecs,
    origin_zip: str,
    dest_zip: str,
    duty: float = 0.0,
    threepl_fee: float = 0.0,
    target_cac: float = 23.50
) -> dict:
    """
    Returns best shipping option that maximizes net margin while meeting CAC gate.
    """
    quotes = get_quotes(origin_zip, dest_zip, pkg)

    results = []
    for q in quotes:
        # Import margin logic
        net_ex_tax = retail / (1 + state_tax)
        landed = product_cost + q.cost_usd + duty + threepl_fee
        payment_fee = 0.029 * retail + 0.30
        net_margin = net_ex_tax - landed - payment_fee

        # CAC gate
        cac_target = 2 * target_cac
        cac_pass = net_margin >= cac_target

        # 3x COGS gate
        cogs_target = 3 * product_cost
        cogs_pass = net_margin >= cogs_target

        results.append({
            "carrier": q.carrier,
            "service": q.service,
            "shipping_cost": q.cost_usd,
            "transit_days": q.transit_days,
            "net_margin": round(net_margin, 2),
            "cac_gate": "PASS" if cac_pass else "FAIL",
            "cogs_gate": "PASS" if cogs_pass else "FAIL",
            "overall": "PASS" if (cac_pass and cogs_pass) else "FAIL",
            "notes": q.notes
        })

    # Filter to PASS, then sort by net_margin descending (maximize profit)
    passing = [r for r in results if r["overall"] == "PASS"]
    passing.sort(key=lambda r: r["net_margin"], reverse=True)

    return {
        "all_options": results,
        "recommended": passing[0] if passing else None,
        "fallback_cheapest": results[0] if results else None,
        "package": asdict(pkg),
        "zone": _estimate_zone(origin_zip, dest_zip)
    }


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description="US Logistics Coordinator — optimize shipping for margin")
    p.add_argument("--retail", type=float, required=True, help="Gross retail price (USD)")
    p.add_argument("--state-tax", type=float, default=0.07, help="State sales tax rate (e.g. 0.07)")
    p.add_argument("--cost", type=float, required=True, help="Product cost (landed, duty-paid)")
    p.add_argument("--origin-zip", type=str, default="90001", help="Origin ZIP (fulfillment center)")
    p.add_argument("--dest-zip", type=str, required=True, help="Destination ZIP (customer)")
    p.add_argument("--weight", type=float, required=True, help="Package weight (lb)")
    p.add_argument("--length", type=float, default=8.0, help="Length (in)")
    p.add_argument("--width", type=float, default=6.0, help="Width (in)")
    p.add_argument("--height", type=float, default=4.0, help="Height (in)")
    p.add_argument("--value", type=float, default=0.0, help="Item value for insurance (USD)")
    p.add_argument("--duty", type=float, default=0.0, help="Duty per unit (USD)")
    p.add_argument("--threepl", type=float, default=0.0, help="3PL pick+pack fee (USD)")
    p.add_argument("--cac", type=float, default=23.50, help="Median CPA benchmark (USD)")
    p.add_argument("--json", action="store_true", help="Output JSON only")
    args = p.parse_args()

    pkg = PackageSpecs(
        weight_lb=args.weight,
        length_in=args.length,
        width_in=args.width,
        height_in=args.height,
        value_usd=args.value
    )

    result = optimize_shipping_for_margin(
        retail=args.retail,
        state_tax=args.state_tax,
        product_cost=args.cost,
        pkg=pkg,
        origin_zip=args.origin_zip,
        dest_zip=args.dest_zip,
        duty=args.duty,
        threepl_fee=args.threepl,
        target_cac=args.cac
    )

    if args.json:
        print(json.dumps(result, indent=2))
        return 0

    # Pretty print
    print("=" * 70)
    print(f"  LOGISTICS COORDINATOR — {args.origin_zip} → {args.dest_zip} (Zone {result['zone']})")
    print("=" * 70)
    print(f"  Package: {args.weight} lb, {args.length}x{args.width}x{args.height} in")
    print(f"  Retail: ${args.retail:.2f} | Cost: ${args.cost:.2f} | Tax: {args.state_tax*100:.1f}%")
    print("-" * 70)

    if result["recommended"]:
        r = result["recommended"]
        print(f"\n  ✅ RECOMMENDED: {r['carrier']} {r['service']}")
        print(f"     Cost: ${r['shipping_cost']:.2f} | Transit: {r['transit_days']} days")
        print(f"     Net Margin: ${r['net_margin']:.2f} | CAC Gate: {r['cac_gate']} | COGS Gate: {r['cogs_gate']}")
        print(f"     Notes: {r['notes']}")
    else:
        print("\n  ❌ NO OPTION PASSES ALL GATES")
        if result["fallback_cheapest"]:
            r = result["fallback_cheapest"]
            print(f"     Cheapest: {r['carrier']} {r['service']} @ ${r['shipping_cost']:.2f}")
            print(f"     Net Margin: ${r['net_margin']:.2f} | CAC: {r['cac_gate']} | COGS: {r['cogs_gate']}")

    print("\n  All Options:")
    for r in result["all_options"]:
        status = "✅" if r["overall"] == "PASS" else "❌"
        print(f"    {status} {r['carrier']:12s} {r['service']:20s} ${r['shipping_cost']:>6.2f}  {r['transit_days']}d  Margin:${r['net_margin']:>6.2f}  CAC:{r['cac_gate']:4s}  COGS:{r['cogs_gate']:4s}")

    print("=" * 70)
    return 0 if result["recommended"] else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())