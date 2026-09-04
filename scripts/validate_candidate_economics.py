#!/usr/bin/env python3
"""Reconcile every candidate's stored unit economics against its own components.

`validate_phase0_schemas.py` checks that a candidate record has the right shape.
Shape is not correctness: a record can carry every required field and still state
a contribution margin that its own cost lines do not produce. That is what this
script checks, for the live records in `data/candidates/` rather than one fixture.

The identities, taken from `validate_candidate_semantics` in
`scripts/validate_phase0_schemas.py`:

    net_revenue               = gross_selling_price - sales_tax_liability
                                - discounts - refund_allowance
    contribution_before_ads   = net_revenue - product_cost - shipping_cost - duty
                                - payment_fees - packaging_cost
                                - variable_support_cost - return_allowance
    break_even_cpa            = contribution_before_ads
    target_cpa                = contribution_before_ads * safety_factor
    expected_profit_per_order = contribution_before_ads - target_cpa

Why this exists: on 2026-08-30 a candidate sweep reported figures that did not
reproduce against its own stored data — 9 of 10 wrong, every error in the
optimistic direction (`reports/2026-08-30-sweep-audit.md`). `verify_sweep.py` was
written to catch that class of error in demand data. This is the same check for
unit economics, which is where the money actually is.

Known-bad records are listed in KNOWN_DEBT so this script can run in CI without
being blocked by pre-existing data defects. New and edited records are held to
the identities. A record in KNOWN_DEBT that starts reconciling is also an error —
that keeps the list shrinking instead of rotting.

Run:  python3 scripts/validate_candidate_economics.py
Exit 0 = every record outside KNOWN_DEBT reconciles, 1 = at least one does not.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES_DIR = ROOT / "data" / "candidates"
TOLERANCE = 0.02

# Records that do not reconcile as of 2026-09-02, quarantined so CI stays honest
# about the state of the data instead of hiding it. Each entry must name a cause.
# Findings are written up in reports/2026-09-02-founder-decision-matrix.md.
# Do not add to this list to make a failure go away — fix the record.
KNOWN_DEBT: dict[str, str] = {
    # Fixed 2026-09-03: retail corrected to researched $24.99/$29.99, payment_fees
    # recalculated for the new price, expected_profit_per_order corrected to
    # subtract target_cpa. Both now reconcile and fail the CAC gate honestly
    # rather than passing on placeholder numbers. See
    # reports/2026-09-02-founder-decision-matrix.md §3 for the original finding.
    #   candidate-us-2026-09-01-magnetic-cable-organizer
    #   candidate-us-2026-09-01-foldable-silicone-bowl
    # Fixed 2026-09-03: return_allowance was omitted from contribution on both.
    #   candidate-us-2026-09-01-magnetic-wristband  (+1.81 → corrected, HOLD stands)
    #   candidate-us-2026-09-01-portable-neck-fan    (+1.65 → corrected, still fails CAC gate)
    # Fixed 2026-09-03: net_revenue was contaminated with a value from the
    # sibling magnetic-cable-organizer record, break_even_cpa did not match
    # contribution_before_ads, and expected_profit_per_order did not subtract
    # target_cpa. Corrected figures still clear every gate.
    #   cand-cj-sku-magnetic-cord-6p
    #
    # Records migrated from the EU products/*.md workspace, which stored one
    # net-margin figure rather than the US contribution model's cost lines.
    # Left as-is: EU market is not in current scope.
    "cloud-key-holder": "legacy EU record; single net-margin figure, not the US cost model",
    "led-sunset-lamp": "legacy EU record; single net-margin figure, not the US cost model",
    "portable-neck-fan": "legacy EU record; single net-margin figure, not the US cost model",
}


def recompute(econ: dict[str, Any]) -> dict[str, float]:
    """The five derived figures, from the record's own component costs."""
    net_revenue = (
        econ["gross_selling_price"]
        - econ["sales_tax_liability"]
        - econ["discounts"]
        - econ["refund_allowance"]
    )
    contribution = (
        net_revenue
        - econ["product_cost"]
        - econ["shipping_cost"]
        - econ["duty"]
        - econ["payment_fees"]
        - econ["packaging_cost"]
        - econ["variable_support_cost"]
        - econ["return_allowance"]
    )
    target_cpa = contribution * econ["safety_factor"]
    return {
        "net_revenue": net_revenue,
        "contribution_before_ads": contribution,
        "break_even_cpa": contribution,
        "target_cpa": target_cpa,
        "expected_profit_per_order": contribution - target_cpa,
    }


def check_record(path: Path) -> list[str]:
    """Discrepancies between a record's stated figures and its own components."""
    data = json.loads(path.read_text(encoding="utf-8"))
    econ = data.get("unit_economics")
    if not isinstance(econ, dict):
        return ["no unit_economics block"]

    try:
        expected = recompute(econ)
    except KeyError as exc:
        return [f"unit_economics missing field {exc}"]

    problems = []
    for field, want in expected.items():
        got = econ.get(field)
        if got is None:
            problems.append(f"{field}: absent, components give {want:.2f}")
            continue
        if abs(got - want) > TOLERANCE:
            # Direction matters more than magnitude: errors that all run the same
            # way are a broken formula, not scattered typos.
            way = "overstated" if got > want else "understated"
            problems.append(f"{field}: states {got:.2f}, components give {want:.2f} ({way} {abs(got-want):+.2f})")
    return problems


def main() -> int:
    if not CANDIDATES_DIR.is_dir():
        print(f"missing {CANDIDATES_DIR.relative_to(ROOT).as_posix()}/")
        return 1

    records = sorted(CANDIDATES_DIR.glob("*.json"))
    print(f"Candidate unit-economics reconciliation — {len(records)} record(s)\n")

    failures: list[str] = []
    overstated = 0
    debt_now_clean: list[str] = []
    clean = 0
    known_bad = 0

    for path in records:
        data = json.loads(path.read_text(encoding="utf-8"))
        cid = data.get("candidate_id", path.stem)
        problems = check_record(path)
        overstated += sum(1 for p in problems if "overstated" in p)

        if not problems:
            clean += 1
            if cid in KNOWN_DEBT:
                debt_now_clean.append(cid)
                print(f"  [FIXED] {cid} — reconciles now; remove it from KNOWN_DEBT")
            continue

        if cid in KNOWN_DEBT:
            known_bad += 1
            print(f"  [DEBT] {cid} — {KNOWN_DEBT[cid]}")
            continue

        failures.append(cid)
        print(f"  [ERROR] {cid}")
        for problem in problems:
            print(f"      {problem}")

    print(f"\n{clean} reconcile, {len(records) - clean} do not "
          f"({known_bad} known, {len(failures)} new)")

    if overstated > 1:
        print(f"\n  [NOTE] {overstated} discrepanc{'y' if overstated == 1 else 'ies'} overstate the "
              f"figure. Errors that all run in the profitable direction are a broken "
              f"formula, not scattered typos — see reports/2026-08-30-sweep-audit.md "
              f"for the same pattern in demand data.")

    for cid in debt_now_clean:
        failures.append(cid)

    print("RESULT: " + ("FAIL" if failures else "PASS"))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
