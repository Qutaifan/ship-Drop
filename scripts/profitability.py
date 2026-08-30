#!/usr/bin/env python3
"""
Business-level profitability model — the gate PROTOCOL-01 does not have.

The True Margin Matrix checks net margin against COGS. It never mentions customer
acquisition cost, so a product can clear the 3x-COGS gate and still lose money on
every sale the moment it is advertised. This model closes that hole.

Benchmarks (stated, not assumed — replace when newer data lands):
  Triple Whale, Aug 2025 - Jul 2026, 53,000+ brands
    ecommerce paid median CPA $23.20 | CVR 1.69% | AOV $61.22
    TikTok CPM $4.08 | CTR 0.61% | CVR 1.56% | CPA $17.07 | ROAS 1.51
  Lebesgue 2026: Meta CPM Germany $9.05

Run:  python3 scripts/profitability.py --retail 34.90 --landed 7.07
      python3 scripts/profitability.py --selftest
Stdlib only.
"""
import argparse
import sys

ECOM_CPA_USD = 23.20
TT = {"cpm": 4.08, "ctr": 0.0061, "cvr": 0.0156, "cpa": 17.07, "roas": 1.51}
META_CPM_DE = 9.05
FX = 1.08                      # USD per EUR; conclusions hold across 1.00-1.15
CAC_SAFETY = 2.0               # net margin must cover CAC this many times


def unit(retail, landed, vat=0.19, fee=0.03):
    k = 1 / (1 + vat) - fee
    net = retail * k - landed
    return {"net": net, "cm_rate": net / retail if retail else 0,
            "breakeven_roas": retail / net if net > 0 else float("inf")}


def funnel_cpa(cpm=TT["cpm"], ctr=TT["ctr"], cvr=TT["cvr"]):
    """Bottom-up CPA from the funnel, in USD."""
    return (1 / (ctr * cvr)) / 1000 * cpm


def assess(retail, landed, vat=0.19, fx=FX):
    u = unit(retail, landed, vat)
    cpa_lo = TT["cpa"] / fx                 # reported median, optimistic end
    cpa_hi = funnel_cpa() / fx              # implied by CPM x CTR x CVR
    cpa_mid = ECOM_CPA_USD / fx
    return {**u, "cpa_lo": cpa_lo, "cpa_mid": cpa_mid, "cpa_hi": cpa_hi,
            "best": u["net"] - cpa_lo, "median": u["net"] - cpa_mid,
            "worst": u["net"] - cpa_hi,
            "roas_verdict": "PROFIT" if TT["roas"] > u["breakeven_roas"] else "LOSS",
            "cac_gate": u["net"] >= CAC_SAFETY * cpa_mid,
            "retail_needed": (CAC_SAFETY * cpa_mid + landed) / (1 / (1 + vat) - 0.03)}


def report(retail, landed, vat):
    a = assess(retail, landed, vat)
    print(f"\nPROFITABILITY — retail EUR {retail:.2f}, landed EUR {landed:.2f}, VAT {vat:.0%}\n")
    print(f"  net margin / sale        EUR {a['net']:.2f}")
    print(f"  contribution rate        {a['cm_rate']:.1%} of gross retail")
    print(f"  breakeven ROAS           {a['breakeven_roas']:.2f}x")
    print(f"  TikTok median ROAS       {TT['roas']:.2f}x  ->  {a['roas_verdict']}")
    print(f"\n  CAC is a RANGE, not a number. The benchmark table is internally")
    print(f"  inconsistent: reported median CPA USD {TT['cpa']:.2f} vs USD {funnel_cpa():.2f}")
    print(f"  implied by its own CPM x CTR x CVR — a {funnel_cpa()/TT['cpa']:.1f}x spread.\n")
    for lbl, cpa, res in (("optimistic (reported TikTok CPA)", a["cpa_lo"], a["best"]),
                          ("median (all-ecommerce CPA)", a["cpa_mid"], a["median"]),
                          ("pessimistic (funnel-implied)", a["cpa_hi"], a["worst"])):
        print(f"  {lbl:34} CAC EUR {cpa:5.2f}  ->  EUR {res:+7.2f} / sale")
    print(f"\n  CAC gate (net >= {CAC_SAFETY:.0f}x median CPA): "
          f"{'PASS' if a['cac_gate'] else 'FAIL'}")
    if not a["cac_gate"]:
        print(f"  To pass at this landed cost, retail must be about "
              f"EUR {a['retail_needed']:.2f} — not EUR {retail:.2f}.")
    print(f"\n  Meta DE CPM USD {META_CPM_DE:.2f} vs TikTok USD {TT['cpm']:.2f} "
          f"({META_CPM_DE/TT['cpm']:.1f}x) — test on TikTok first.")
    print("\n  PORTFOLIO — capital to find one winner:")
    for win in (0.05, 0.10, 0.20):
        print(f"    win rate {win:>4.0%}:  EUR {150/win:>6,.0f} (lean)  ..  "
              f"EUR {300/win:>6,.0f} (realistic)")
    return 0 if a["cac_gate"] else 1


def selftest():
    ok = True
    cases = [
        ("breakeven ROAS is retail/net", lambda: abs(unit(34.90, 7.07)["breakeven_roas"] - 34.90/unit(34.90,7.07)["net"]) < 1e-9),
        ("zero landed cost raises net", lambda: unit(34.90, 0)["net"] > unit(34.90, 7.07)["net"]),
        ("thin margin fails the CAC gate", lambda: not assess(34.90, 7.07)["cac_gate"]),
        ("high ticket passes the CAC gate", lambda: assess(89.90, 18.00)["cac_gate"]),
        ("funnel CPA exceeds reported CPA", lambda: funnel_cpa() > TT["cpa"]),
        ("negative net -> infinite breakeven ROAS", lambda: unit(20.00, 30.00)["breakeven_roas"] == float("inf")),
        ("retail_needed actually passes", lambda: assess(assess(34.90,7.07)["retail_needed"]+0.01, 7.07)["cac_gate"]),
    ]
    print("profitability selftest\n")
    for name, fn in cases:
        try: good = fn()
        except Exception as e: good = False; name += f"  ({e})"
        ok = ok and good
        print(f"  {'OK  ' if good else 'FAIL'} {name}")
    print("\nSELFTEST: " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Business-level profitability model")
    ap.add_argument("--retail", type=float, default=34.90)
    ap.add_argument("--landed", type=float, default=7.07)
    ap.add_argument("--vat", type=float, default=0.19)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    sys.exit(selftest() if a.selftest else report(a.retail, a.landed, a.vat))
