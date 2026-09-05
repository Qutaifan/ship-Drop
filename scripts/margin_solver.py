#!/usr/bin/env python3
"""
Hermes-Ecom True Margin Matrix Solver — PROTOCOL-01 (GCC & Global Support).

Solves the exact unit economics for any product under GCC (KSA 15%, UAE 5%, Kuwait 0%)
or EU VAT and customs duty rules. Supports both Prepaid (Apple Pay/Mada) and COD modes.
Calculates net margin, checks the 3x-COGS gate and the net profit floor (>60 SAR / >€15),
computes the maximum allowable landed cost, and outputs paste-ready markdown for
products/<name>.md.

Usage:
  python3 scripts/margin_solver.py --retail 199.00 --cost 30.00 --shipping 20.00 --vat 0.15 --currency SAR
  python3 scripts/margin_solver.py --retail 199.00 --cost 30.00 --shipping 20.00 --mode cod --rto 0.15 --currency SAR
  python3 scripts/margin_solver.py --table --vat 0.15 --currency SAR
  python3 scripts/margin_solver.py --selftest

Stdlib only.
"""
import argparse
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

CURRENCY_SYMBOLS = {
    "SAR": "SAR ",
    "AED": "AED ",
    "EUR": "€",
    "USD": "$",
    "KWD": "KWD ",
    "QAR": "QAR ",
    "BHD": "BHD ",
    "OMR": "OMR ",
}

COUNTRY_VAT = {
    "KSA": 0.15,
    "SA": 0.15,
    "UAE": 0.05,
    "AE": 0.05,
    "BH": 0.10,
    "OM": 0.05,
    "KW": 0.00,
    "QA": 0.00,
    "DE": 0.19,
    "EU": 0.19,
}


def get_floors(currency="SAR"):
    curr = currency.upper()
    if curr == "SAR":
        return {"profit_floor": 60.0, "retail_floor": 80.0}
    elif curr == "AED":
        return {"profit_floor": 60.0, "retail_floor": 80.0}
    elif curr == "KWD":
        return {"profit_floor": 5.0, "retail_floor": 7.0}
    elif curr in ("QAR", "BHD", "OMR"):
        return {"profit_floor": 60.0, "retail_floor": 80.0}
    elif curr == "USD":
        return {"profit_floor": 16.0, "retail_floor": 20.0}
    else:  # EUR default
        return {"profit_floor": 15.0, "retail_floor": 20.0}


def calc_margin(retail, cost, shipping, duty=0.0, vat=0.15, fee_rate=0.03,
                mode="prepaid", cod_fee=0.0, rto_rate=0.0, currency="SAR"):
    """
    Computes True Margin Matrix metrics.
    Revenue is ex-VAT: retail / (1 + vat).
    Fee is on gross retail: retail * fee_rate.
    COGS = cost + shipping + duty.
    In COD mode: Net accounts for RTO (Return to Origin) rate and COD courier handling fee.
    """
    if vat > 1:
        vat = vat / 100.0
    if fee_rate > 1:
        fee_rate = fee_rate / 100.0
    if rto_rate > 1:
        rto_rate = rto_rate / 100.0

    floors = get_floors(currency)
    profit_floor = floors["profit_floor"]
    retail_floor = floors["retail_floor"]

    cogs = round(cost + shipping + duty, 2)
    ex_vat_rev = round(retail / (1 + vat), 2)
    fee = round(retail * fee_rate, 2)

    if mode == "cod" and rto_rate > 0:
        rto_cost = round(rto_rate * (shipping * 0.5 + cost * 0.1), 2)
        net_margin = round(ex_vat_rev - cogs - fee - cod_fee - rto_cost, 2)
    else:
        net_margin = round(ex_vat_rev - cogs - fee, 2)

    gate_3x = net_margin >= round(3 * cogs, 2)
    gate_floor = net_margin > profit_floor
    gate_retail = retail >= retail_floor

    verdict = "PASS" if (gate_3x and gate_floor and gate_retail) else "FAIL"

    return {
        "retail": retail,
        "cost": cost,
        "shipping": shipping,
        "duty": duty,
        "cogs": cogs,
        "vat": vat,
        "ex_vat_rev": ex_vat_rev,
        "fee": fee,
        "mode": mode,
        "cod_fee": cod_fee,
        "rto_rate": rto_rate,
        "net_margin": net_margin,
        "currency": currency.upper(),
        "profit_floor": profit_floor,
        "retail_floor": retail_floor,
        "gate_3x": gate_3x,
        "gate_floor": gate_floor,
        "gate_15": gate_floor,  # backward compatibility alias
        "gate_retail": gate_retail,
        "verdict": verdict,
    }


def max_landed_cost(retail, vat=0.15, fee_rate=0.03, currency="SAR"):
    """
    Solves for the maximum landed cost (COGS) where:
    Net Margin >= 3 * COGS AND Net Margin > profit_floor.
    """
    if vat > 1:
        vat = vat / 100.0
    if fee_rate > 1:
        fee_rate = fee_rate / 100.0

    floors = get_floors(currency)
    profit_floor = floors["profit_floor"]

    ex_vat = retail / (1 + vat)
    fee = retail * fee_rate
    net_avail = ex_vat - fee

    bound_3x = net_avail / 4.0
    bound_floor = net_avail - profit_floor

    if bound_floor <= 0:
        return 0.0, 0.0

    allowed_cogs = min(bound_3x, bound_floor)
    net_at_cogs = ex_vat - allowed_cogs - fee
    return round(allowed_cogs, 2), round(net_at_cogs, 2)


def generate_buying_table(vat=0.15, fee_rate=0.03, currency="SAR"):
    curr = currency.upper()
    if curr in ("SAR", "AED", "QAR"):
        tiers = [149.00, 199.00, 249.00, 299.00, 349.00, 399.00]
    elif curr == "KWD":
        tiers = [12.00, 16.00, 20.00, 25.00, 30.00, 35.00]
    else:
        tiers = [24.90, 29.90, 34.90, 39.90, 44.90, 49.90]

    rows = []
    for r in tiers:
        max_cogs, net_at_cogs = max_landed_cost(r, vat=vat, fee_rate=fee_rate, currency=currency)
        rows.append((r, max_cogs, net_at_cogs))
    return rows


def format_markdown(res, buying_table=None):
    curr = res.get("currency", "SAR")
    sym = CURRENCY_SYMBOLS.get(curr, f"{curr} ")
    p_floor = res.get("profit_floor", 60.0)
    r_floor = res.get("retail_floor", 80.0)

    lines = []
    lines.append("## True Margin Matrix")
    lines.append("`Net Margin = (Retail / (1 + VAT)) − (Product Cost + Shipping + Import Duty) − (Payment Fee / COD Surcharge)`")
    lines.append(f"- Retail price target (VAT-inclusive): {sym}{res['retail']:.2f}")
    lines.append(f"- VAT rate: {res['vat']:.2f}")
    lines.append(f"- Product cost: {sym}{res['cost']:.2f}")
    lines.append(f"- Shipping cost: {sym}{res['shipping']:.2f}")
    lines.append(f"- Import duty per unit: {sym}{res['duty']:.2f}")
    lines.append(f"- COGS (Cost + Shipping + Duty): {sym}{res['cogs']:.2f}")
    lines.append(f"- Ex-VAT Revenue: {sym}{res['ex_vat_rev']:.2f}")
    lines.append(f"- Payment / Processing fee: {sym}{res['fee']:.2f}")
    if res.get("mode") == "cod" and res.get("rto_rate", 0) > 0:
        lines.append(f"- COD Fee + RTO Buffer ({res['rto_rate']:.0%} RTO): {sym}{res['cod_fee']:.2f}")
    lines.append(f"- Net Margin: {res['net_margin']:.2f}")
    lines.append(f"- 3x COGS Gate (Need ≥ {sym}{3*res['cogs']:.2f}): {'PASS' if res['gate_3x'] else 'FAIL'}")
    lines.append(f"- Profit Floor Gate (Need > {sym}{p_floor:.2f}): {'PASS' if res['gate_floor'] else 'FAIL'}")
    lines.append(f"- Retail Floor Gate (Need ≥ {sym}{r_floor:.2f}): {'PASS' if res['gate_retail'] else 'FAIL'}")
    lines.append(f"- Margin Matrix Verdict: **{res['verdict']}**\n")

    if buying_table:
        lines.append("### Buying Constraint — Maximum Landed Cost Reference")
        lines.append(f"Solving both gates for maximum landed cost at {res['vat']:.0%} VAT ({curr}):\n")
        lines.append("| Gross retail | Max landed cost | Net margin at that cost |")
        lines.append("|---|---|---|")
        for r, mc, nm in buying_table:
            lines.append(f"| {sym}{r:.2f} | {sym}{mc:.2f} | {sym}{nm:.2f} |")
        lines.append(f"\n**Rule: landed cost must be ≤ {((1/(1+res['vat']) - 0.03)/4):.1%} of the VAT-inclusive retail price.**")

    return "\n".join(lines)


def selftest():
    print("Running margin_solver selftest...")
    # Test 1: Worked EU example from AGENTS.md
    # retail 49.90, cost 8.20, shipping 3.10, duty 0, DE VAT 19%, EUR
    # cogs = 11.30, ex_vat = 41.93, fee = 1.50, net = 29.13, 3x cogs = 33.90 -> FAIL
    r1 = calc_margin(49.90, 8.20, 3.10, duty=0.0, vat=0.19, currency="EUR")
    assert abs(r1["net_margin"] - 29.13) <= 0.02, f"r1 net margin error: {r1['net_margin']}"
    assert r1["gate_3x"] is False, "r1 should fail 3x cogs gate"
    assert r1["verdict"] == "FAIL", "r1 verdict should be FAIL"

    # Test 2: EU Passing case
    r2 = calc_margin(59.90, 7.50, 2.50, duty=0.0, vat=0.19, currency="EUR")
    assert abs(r2["net_margin"] - 38.54) <= 0.02, f"r2 net margin error: {r2['net_margin']}"
    assert r2["gate_3x"] is True, "r2 should pass 3x cogs"
    assert r2["gate_floor"] is True, "r2 should pass >15"
    assert r2["verdict"] == "PASS", "r2 verdict should be PASS"

    # Test 3: GCC KSA Passing case (199 SAR retail, 30 SAR cost, 15 SAR ship, 15% VAT)
    r3 = calc_margin(199.00, 30.00, 15.00, duty=0.0, vat=0.15, currency="SAR")
    assert r3["cogs"] == 45.00
    assert abs(r3["net_margin"] - 122.07) <= 0.05

    # Test 4: GCC KSA High-ticket Passing case (249 SAR retail, 25 SAR cost, 20 SAR ship, 15% VAT)
    r4 = calc_margin(249.00, 25.00, 20.00, duty=0.0, vat=0.15, currency="SAR")
    assert r4["gate_3x"] is True
    assert r4["gate_floor"] is True
    assert r4["verdict"] == "PASS"

    # Test 5: Buying constraint table
    table = generate_buying_table(vat=0.15, currency="SAR")
    assert len(table) == 6

    print("SELFTEST: PASS")
    return 0


def main():
    ap = argparse.ArgumentParser(description="PROTOCOL-01 True Margin Matrix solver (GCC & Global)")
    ap.add_argument("--retail", type=float, help="Gross VAT-inclusive retail price")
    ap.add_argument("--cost", type=float, default=0.0, help="Product unit cost")
    ap.add_argument("--shipping", type=float, default=0.0, help="Shipping cost")
    ap.add_argument("--duty", type=float, default=0.0, help="Import customs duty per unit")
    ap.add_argument("--vat", type=float, default=None, help="Destination VAT rate (default 0.15 for KSA, or from --country)")
    ap.add_argument("--country", default="KSA", help="Destination country code (KSA, UAE, KW, QA, BH, OM, DE)")
    ap.add_argument("--currency", default="SAR", help="Currency code (SAR, AED, KWD, EUR, USD)")
    ap.add_argument("--fee", type=float, default=0.03, help="Payment processing fee rate (default 0.03)")
    ap.add_argument("--mode", default="prepaid", choices=["prepaid", "cod"], help="Payment mode: prepaid or cod")
    ap.add_argument("--cod-fee", type=float, default=0.0, help="COD handling fee per order")
    ap.add_argument("--rto", type=float, default=0.0, help="Estimated Return-To-Origin rate for COD (e.g. 0.15 for 15%%)")
    ap.add_argument("--table", action="store_true", help="Print buying constraint table only")
    ap.add_argument("--markdown", action="store_true", help="Output paste-ready markdown block")
    ap.add_argument("--selftest", action="store_true", help="Run offline unit tests")
    a = ap.parse_args()

    if a.selftest:
        return selftest()

    vat_rate = a.vat if a.vat is not None else COUNTRY_VAT.get(a.country.upper(), 0.15)
    currency = a.currency.upper()

    if a.table:
        table = generate_buying_table(vat=vat_rate, fee_rate=a.fee, currency=currency)
        sym = CURRENCY_SYMBOLS.get(currency, f"{currency} ")
        print(f"\nBuying Constraint Table (VAT {vat_rate:.0%}, Fee {a.fee:.0%}, Currency {currency}):")
        print("| Gross retail | Max landed cost | Net margin at that cost |")
        print("|---|---|---|")
        for r, mc, nm in table:
            print(f"| {sym}{r:.2f} | {sym}{mc:.2f} | {sym}{nm:.2f} |")
        return 0

    if a.retail is None:
        ap.error("--retail is required (or use --table / --selftest)")

    res = calc_margin(a.retail, a.cost, a.shipping, duty=a.duty, vat=vat_rate,
                      fee_rate=a.fee, mode=a.mode, cod_fee=a.cod_fee,
                      rto_rate=a.rto, currency=currency)
    table = generate_buying_table(vat=vat_rate, fee_rate=a.fee, currency=currency)
    sym = CURRENCY_SYMBOLS.get(currency, f"{currency} ")

    if a.markdown:
        print(format_markdown(res, table))
    else:
        print(f"\nTrue Margin Matrix Evaluation — Retail: {sym}{res['retail']:.2f} ({currency})")
        print(f"  COGS:              {sym}{res['cogs']:.2f} (Product {sym}{res['cost']:.2f} + Ship {sym}{res['shipping']:.2f} + Duty {sym}{res['duty']:.2f})")
        print(f"  Ex-VAT Revenue:    {sym}{res['ex_vat_rev']:.2f} (at {res['vat']:.0%} VAT)")
        print(f"  Payment Fee:       {sym}{res['fee']:.2f} (at {a.fee:.0%})")
        if res.get("mode") == "cod" and res.get("rto_rate", 0) > 0:
            print(f"  COD & RTO Buffer:  {sym}{res['cod_fee']:.2f} ({res['rto_rate']:.0%} RTO)")
        print(f"  Net Margin:        {sym}{res['net_margin']:.2f}")
        print(f"  3x COGS Gate:      {'PASS' if res['gate_3x'] else 'FAIL'} (Need ≥ {sym}{3*res['cogs']:.2f})")
        print(f"  Profit Floor Gate: {'PASS' if res['gate_floor'] else 'FAIL'} (Need > {sym}{res['profit_floor']:.2f})")
        print(f"  VERDICT:           {res['verdict']}\n")
        print("--- Paste into products/<name>.md ---")
        print(format_markdown(res, table))

    return 0 if res["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
