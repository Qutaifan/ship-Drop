#!/usr/bin/env python3
"""
US True Margin Matrix - corrected 2026-08-30 (US variant)

Formula:
  Net Margin = (Retail / (1 + State_Tax)) - (Product_Cost + Shipping + Duty + 3PL_Fee) - (0.029 * Retail + 0.30)

Usage:
  python3 margin_solver_us.py --retail 85 --state-tax 0.07 --cost 12 --shipping 5.50 --duty 0 --threepl 3.50
  python3 margin_solver_us.py --retail 85 --state-tax 0.07 --cost 12 --shipping 5.50 --duty 0 --threepl 3.50 --cac 23.50
  python3 margin_solver_us.py --interactive
"""
import argparse
import sys


def true_margin_matrix_us(retail, state_tax, product_cost, shipping, duty, threepl_fee):
    """US True Margin Matrix (USD).

    state_tax: e.g. 0.07 for 7% state sales tax
    duty: dollar amount per unit (Section 301 + other duties). 0 if duty paid in bulk to 3PL.
    threepl_fee: pick+pack fee per order at US 3PL
    """
    if retail <= 0:
        raise ValueError("retail must be > 0")
    if state_tax < 0 or state_tax >= 0.5:
        raise ValueError("state_tax must be in [0, 0.5)")
    if product_cost < 0 or shipping < 0 or duty < 0 or threepl_fee < 0:
        raise ValueError("costs must be non-negative")

    net_ex_tax = retail / (1 + state_tax)
    landed_cost = product_cost + shipping + duty + threepl_fee
    payment_fee = 0.029 * retail + 0.30  # Stripe US 2.9% + $0.30 on gross
    return net_ex_tax - landed_cost - payment_fee


def evaluate_gates(net_margin, product_cost, retail):
    """Return (pass: bool, failures: list[str], notes: list[str])."""
    failures, notes = [], []

    # Gate 1: 3x COGS
    cogs_target = 3 * product_cost
    if net_margin >= cogs_target:
        notes.append(f"OK 3x COGS: ${net_margin:.2f} >= ${cogs_target:.2f}")
    else:
        failures.append(f"3x COGS: ${net_margin:.2f} < ${cogs_target:.2f}")

    # Gate 2: net margin floor
    if net_margin >= 20.0:
        notes.append(f"OK margin floor: ${net_margin:.2f} >= $20.00")
    else:
        failures.append(f"margin floor: ${net_margin:.2f} < $20.00")

    # Gate 3: retail band USD
    if 68 <= retail <= 105:
        notes.append(f"OK retail band: ${retail:.2f} in [$68, $105]")
    else:
        failures.append(f"retail band: ${retail:.2f} not in [$68, $105]")

    return (len(failures) == 0, failures, notes)


def evaluate_cac(net_margin, cac_benchmark=23.50):
    """CAC gate: net margin must be >= 2x median US CPA benchmark."""
    target = 2 * cac_benchmark
    if net_margin >= target:
        return True, f"OK CAC gate: ${net_margin:.2f} >= 2 * ${cac_benchmark:.2f} = ${target:.2f}"
    return False, f"CAC gate: ${net_margin:.2f} < 2 * ${cac_benchmark:.2f} = ${target:.2f}"


def main():
    p = argparse.ArgumentParser(description="US True Margin Matrix calculator")
    p.add_argument("--retail", type=float, help="Gross retail (USD, sales-tax-inclusive)")
    p.add_argument("--state-tax", type=float, default=0.07, help="State sales tax rate (e.g. 0.07 = 7%%)")
    p.add_argument("--cost", type=float, help="Product cost (FOB or landed, post-duty)")
    p.add_argument("--shipping", type=float, help="US domestic shipping cost")
    p.add_argument("--duty", type=float, default=0.0, help="Duty per unit (0 if paid in bulk at 3PL)")
    p.add_argument("--threepl", type=float, default=0.0, help="US 3PL pick+pack fee per order")
    p.add_argument("--cac", type=float, default=23.50, help="Median US CPA benchmark (USD)")
    p.add_argument("--interactive", action="store_true", help="Interactive mode")
    args = p.parse_args()

    if args.interactive or args.retail is None:
        print("US True Margin Matrix - Interactive Mode")
        print("=========================================")
        try:
            args.retail = float(input("Retail (USD gross, sales-tax-inclusive): $"))
            args.state_tax = float(input("State sales tax (e.g. 0.07 for 7%%) [0.07]: ") or "0.07")
            args.cost = float(input("Product cost (landed, duty-paid) USD: $"))
            args.shipping = float(input("US shipping per order: $"))
            args.duty = float(input("Duty per unit (0 if bulk-paid at 3PL) [0]: ") or "0")
            args.threepl = float(input("3PL pick+pack fee [3.50]: $") or "3.50")
        except (EOFError, ValueError):
            print("Aborted.", file=sys.stderr)
            return 2

    if args.cost is None:
        p.error("--cost is required (or use --interactive)")

    net_margin = true_margin_matrix_us(
        retail=args.retail,
        state_tax=args.state_tax,
        product_cost=args.cost,
        shipping=args.shipping,
        duty=args.duty,
        threepl_fee=args.threepl,
    )
    passed_gates, failures, notes = evaluate_gates(net_margin, args.cost, args.retail)
    cac_pass, cac_note = evaluate_cac(net_margin, args.cac)
    overall_pass = passed_gates and cac_pass

    # Print results
    print()
    print("=" * 60)
    print(f"  US TRUE MARGIN MATRIX")
    print("=" * 60)
    print(f"  Inputs")
    print(f"    Retail (gross):      ${args.retail:>8.2f}")
    print(f"    State tax:           {args.state_tax * 100:>7.2f}%")
    print(f"    Product cost:        ${args.cost:>8.2f}")
    print(f"    Shipping:            ${args.shipping:>8.2f}")
    print(f"    Duty:                ${args.duty:>8.2f}")
    print(f"    3PL pick+pack:       ${args.threepl:>8.2f}")
    print(f"    Payment fee (2.9%):  ${0.029 * args.retail + 0.30:>8.2f}")
    print("-" * 60)
    print(f"  Net margin:           ${net_margin:>8.2f}")
    print("=" * 60)
    print()
    print("  Gates:")
    for note in notes:
        print(f"    {note}")
    if not passed_gates:
        print("    FAIL:")
        for f in failures:
            print(f"      - {f}")
    print(f"    {cac_note}")
    print()
    print(f"  Verdict: {'PASS - LAUNCH (US)' if overall_pass else 'FAIL'}")
    print("=" * 60)
    return 0 if overall_pass else 1


if __name__ == "__main__":
    sys.exit(main())
