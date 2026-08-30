#!/usr/bin/env python3
"""
Hermes-Ecom True Margin Matrix Solver — PROTOCOL-01.

Solves the exact unit economics for any product under EU VAT and customs duty rules.
Calculates net margin, checks the 3x-COGS gate and the >€15 net profit floor,
computes the maximum allowable landed cost, and outputs paste-ready markdown for
products/<name>.md.

Usage:
  python3 scripts/margin_solver.py --retail 34.90 --cost 4.50 --shipping 2.50 --duty 0 --vat 0.19
  python3 scripts/margin_solver.py --table --vat 0.19
  python3 scripts/margin_solver.py --selftest

Stdlib only.
"""
import argparse
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def calc_margin(retail, cost, shipping, duty=0.0, vat=0.19, fee_rate=0.03):
    """
    Computes True Margin Matrix metrics.
    Revenue is ex-VAT: retail / (1 + vat).
    Fee is on gross retail: retail * fee_rate.
    COGS = cost + shipping + duty.
    Net Margin = ex_vat_revenue - COGS - fee.
    """
    if vat > 1:
        vat = vat / 100.0
    if fee_rate > 1:
        fee_rate = fee_rate / 100.0

    cogs = round(cost + shipping + duty, 2)
    ex_vat_rev = round(retail / (1 + vat), 2)
    fee = round(retail * fee_rate, 2)
    net_margin = round(retail / (1 + vat) - cogs - fee, 2)

    gate_3x = net_margin >= round(3 * cogs, 2)
    gate_15 = net_margin > 15.0
    gate_retail = retail >= 20.0

    verdict = "PASS" if (gate_3x and gate_15 and gate_retail) else "FAIL"

    return {
        "retail": retail,
        "cost": cost,
        "shipping": shipping,
        "duty": duty,
        "cogs": cogs,
        "vat": vat,
        "ex_vat_rev": ex_vat_rev,
        "fee": fee,
        "net_margin": net_margin,
        "gate_3x": gate_3x,
        "gate_15": gate_15,
        "gate_retail": gate_retail,
        "verdict": verdict,
    }


def max_landed_cost(retail, vat=0.19, fee_rate=0.03):
    """
    Solves for the maximum landed cost (COGS) where:
    Net Margin >= 3 * COGS AND Net Margin > 15.
    Since Net Margin = Ex_VAT - COGS - Fee:
    1) 4 * COGS <= Ex_VAT - Fee  =>  COGS <= (Ex_VAT - Fee) / 4
    2) Ex_VAT - COGS - Fee > 15   =>  COGS < Ex_VAT - Fee - 15
    """
    if vat > 1:
        vat = vat / 100.0
    if fee_rate > 1:
        fee_rate = fee_rate / 100.0

    ex_vat = retail / (1 + vat)
    fee = retail * fee_rate
    net_avail = ex_vat - fee

    # Bound from 3x COGS rule
    bound_3x = net_avail / 4.0
    # Bound from >15 EUR floor
    bound_15 = net_avail - 15.0

    if bound_15 <= 0:
        return 0.0, 0.0  # Impossible to reach >15 margin at any cost

    allowed_cogs = min(bound_3x, bound_15)
    net_at_cogs = ex_vat - allowed_cogs - fee
    return round(allowed_cogs, 2), round(net_at_cogs, 2)


def generate_buying_table(vat=0.19, fee_rate=0.03):
    tiers = [24.90, 29.90, 34.90, 39.90, 44.90, 49.90]
    rows = []
    for r in tiers:
        max_cogs, net_at_cogs = max_landed_cost(r, vat=vat, fee_rate=fee_rate)
        rows.append((r, max_cogs, net_at_cogs))
    return rows


def format_markdown(res, buying_table=None):
    lines = []
    lines.append("## True Margin Matrix")
    lines.append("`Net Margin = (Retail / (1 + VAT)) − (Product Cost + Shipping + Import Duty) − (0.03 × Retail)`")
    lines.append(f"- Retail price target (VAT-inclusive): €{res['retail']:.2f}")
    lines.append(f"- VAT rate: {res['vat']:.2f}")
    lines.append(f"- Product cost: €{res['cost']:.2f}")
    lines.append(f"- Shipping cost: €{res['shipping']:.2f}")
    lines.append(f"- Import duty per unit: €{res['duty']:.2f}")
    lines.append(f"- COGS (Cost + Shipping + Duty): €{res['cogs']:.2f}")
    lines.append(f"- Ex-VAT Revenue: €{res['ex_vat_rev']:.2f}")
    lines.append(f"- 3% Payment fee: €{res['fee']:.2f}")
    lines.append(f"- Net Margin: {res['net_margin']:.2f}")
    lines.append(f"- 3x COGS Gate (Need ≥ €{3*res['cogs']:.2f}): {'PASS' if res['gate_3x'] else 'FAIL'}")
    lines.append(f"- Floor Gate (Need > €15.00): {'PASS' if res['gate_15'] else 'FAIL'}")
    lines.append(f"- Retail Floor Gate (Need ≥ €20.00): {'PASS' if res['gate_retail'] else 'FAIL'}")
    lines.append(f"- Margin Matrix Verdict: **{res['verdict']}**\n")

    if buying_table:
        lines.append("### Buying Constraint — Maximum Landed Cost Reference")
        lines.append(f"Solving both gates for maximum landed cost at {res['vat']:.0%} VAT:\n")
        lines.append("| Gross retail | Max landed cost | Net margin at that cost |")
        lines.append("|---|---|---|")
        for r, mc, nm in buying_table:
            lines.append(f"| €{r:.2f} | €{mc:.2f} | €{nm:.2f} |")
        lines.append(f"\n**Rule: landed cost must be ≤ {((1/(1+res['vat']) - 0.03)/4):.1%} of the VAT-inclusive retail price.**")

    return "\n".join(lines)


def selftest():
    print("Running margin_solver selftest...")
    # Test 1: Worked example from AGENTS.md
    # retail 49.90, cost 8.20, shipping 3.10, duty 0, DE VAT 19%
    # cogs = 11.30, ex_vat = 41.93, fee = 1.50, net = 29.13, 3x cogs = 33.90 -> FAIL
    r1 = calc_margin(49.90, 8.20, 3.10, duty=0.0, vat=0.19)
    assert abs(r1["net_margin"] - 29.13) <= 0.02, f"r1 net margin error: {r1['net_margin']}"
    assert r1["gate_3x"] is False, "r1 should fail 3x cogs gate"
    assert r1["verdict"] == "FAIL", "r1 verdict should be FAIL"

    # Test 2: Passing case
    # retail 59.90, cost 7.50, shipping 2.50, duty 0, DE VAT 19%
    # cogs = 10.00, ex_vat = 50.34, fee = 1.80, net = 38.54, 3x cogs = 30.00 -> PASS
    r2 = calc_margin(59.90, 7.50, 2.50, duty=0.0, vat=0.19)
    assert abs(r2["net_margin"] - 38.54) <= 0.02, f"r2 net margin error: {r2['net_margin']}"
    assert r2["gate_3x"] is True, "r2 should pass 3x cogs"
    assert r2["gate_15"] is True, "r2 should pass >15"
    assert r2["verdict"] == "PASS", "r2 verdict should be PASS"

    # Test 3: Buying constraint table
    table = generate_buying_table(vat=0.19)
    assert len(table) == 6
    # For €34.90: max landed cost should be €7.07
    r_34 = [row for row in table if row[0] == 34.90][0]
    assert abs(r_34[1] - 7.07) <= 0.05, f"€34.90 max cogs error: {r_34[1]}"

    print("SELFTEST: PASS")
    return 0


def main():
    ap = argparse.ArgumentParser(description="PROTOCOL-01 True Margin Matrix solver")
    ap.add_argument("--retail", type=float, help="Gross VAT-inclusive retail price in EUR")
    ap.add_argument("--cost", type=float, default=0.0, help="Product unit cost in EUR")
    ap.add_argument("--shipping", type=float, default=0.0, help="Shipping cost in EUR")
    ap.add_argument("--duty", type=float, default=0.0, help="Import customs duty per unit in EUR (0 for EU warehouse)")
    ap.add_argument("--vat", type=float, default=0.19, help="Destination VAT rate (default 0.19 for DE)")
    ap.add_argument("--fee", type=float, default=0.03, help="Payment processing fee rate (default 0.03)")
    ap.add_argument("--table", action="store_true", help="Print buying constraint table only")
    ap.add_argument("--markdown", action="store_true", help="Output paste-ready markdown block")
    ap.add_argument("--selftest", action="store_true", help="Run offline unit tests")
    a = ap.parse_args()

    if a.selftest:
        return selftest()

    if a.table:
        table = generate_buying_table(vat=a.vat, fee_rate=a.fee)
        print(f"\nBuying Constraint Table (VAT {a.vat:.0%}, Fee {a.fee:.0%}):")
        print("| Gross retail | Max landed cost | Net margin at that cost |")
        print("|---|---|---|")
        for r, mc, nm in table:
            print(f"| €{r:.2f} | €{mc:.2f} | €{nm:.2f} |")
        return 0

    if a.retail is None:
        ap.error("--retail is required (or use --table / --selftest)")

    res = calc_margin(a.retail, a.cost, a.shipping, duty=a.duty, vat=a.vat, fee_rate=a.fee)
    table = generate_buying_table(vat=a.vat, fee_rate=a.fee)

    if a.markdown:
        print(format_markdown(res, table))
    else:
        print(f"\nTrue Margin Matrix Evaluation — Retail: €{res['retail']:.2f}")
        print(f"  COGS:              €{res['cogs']:.2f} (Product €{res['cost']:.2f} + Ship €{res['shipping']:.2f} + Duty €{res['duty']:.2f})")
        print(f"  Ex-VAT Revenue:    €{res['ex_vat_rev']:.2f} (at {res['vat']:.0%} VAT)")
        print(f"  Payment Fee:       €{res['fee']:.2f} (at {a.fee:.0%})")
        print(f"  Net Margin:        €{res['net_margin']:.2f}")
        print(f"  3x COGS Gate:      {'PASS' if res['gate_3x'] else 'FAIL'} (Need ≥ €{3*res['cogs']:.2f})")
        print(f"  >€15 Floor Gate:   {'PASS' if res['gate_15'] else 'FAIL'}")
        print(f"  VERDICT:           {res['verdict']}\n")
        print("--- Paste into products/<name>.md ---")
        print(format_markdown(res, table))

    return 0 if res["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
