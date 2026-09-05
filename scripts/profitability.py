#!/usr/bin/env python3
"""
Business-level profitability model — PROTOCOL-01 (GCC & Global Multi-Channel).

The True Margin Matrix checks net margin against COGS. It never mentions customer
acquisition cost, so a product can clear the 3x-COGS gate and still lose money on
every sale the moment it is advertised. This model closes that hole across GCC (Snapchat,
TikTok GCC, Meta GCC) and European/US ad networks.

Benchmarks (stated, not assumed — 2025/2026 GCC & Global data):
  Snapchat KSA / GCC:
    CPM $2.80 | CTR 0.95% | CVR 2.20% | CPA $13.40 | ROAS 2.20
  TikTok GCC:
    CPM $3.50 | CTR 0.75% | CVR 1.85% | CPA $15.20 | ROAS 1.85
  Meta GCC:
    CPM $7.50 | CTR 0.80% | CVR 1.90% | CPA $20.30 | ROAS 1.65
  Triple Whale Global paid median:
    CPA $23.20 | CVR 1.69% | AOV $61.22
  TikTok Global:
    CPM $4.08 | CTR 0.61% | CVR 1.56% | CPA $17.07 | ROAS 1.51
  Meta Germany:
    CPM $9.05

Run:  python3 scripts/profitability.py --retail 199.00 --landed 45.00 --currency SAR --vat 0.15
      python3 scripts/profitability.py --retail 34.90 --landed 7.07 --currency EUR --vat 0.19
      python3 scripts/profitability.py --selftest
Stdlib only.
"""
import argparse
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Channel benchmarks in USD
BENCHMARKS = {
    "SNAP_GCC": {"cpm": 2.80, "ctr": 0.0095, "cvr": 0.0220, "cpa": 13.40, "roas": 2.20, "label": "Snapchat KSA/GCC"},
    "TT_GCC":   {"cpm": 3.50, "ctr": 0.0075, "cvr": 0.0185, "cpa": 15.20, "roas": 1.85, "label": "TikTok GCC"},
    "META_GCC": {"cpm": 7.50, "ctr": 0.0080, "cvr": 0.0190, "cpa": 20.30, "roas": 1.65, "label": "Meta GCC"},
    "TT_GLOBAL":{"cpm": 4.08, "ctr": 0.0061, "cvr": 0.0156, "cpa": 17.07, "roas": 1.51, "label": "TikTok Global"},
}

ECOM_CPA_USD = 23.20
TT = BENCHMARKS["TT_GLOBAL"]
SNAP = BENCHMARKS["SNAP_GCC"]
META_CPM_DE = 9.05

# FX rates (units per USD)
FX_RATES = {
    "USD": 1.00,
    "SAR": 3.75,
    "AED": 3.67,
    "KWD": 0.31,
    "QAR": 3.64,
    "EUR": 0.92,   # 1.08 USD per EUR
}

CAC_SAFETY = 2.0


def unit(retail, landed, vat=0.15, fee=0.03):
    k = 1 / (1 + vat) - fee
    net = retail * k - landed
    return {"net": net, "cm_rate": net / retail if retail else 0,
            "breakeven_roas": retail / net if net > 0 else float("inf")}


def funnel_cpa(cpm, ctr, cvr):
    """Bottom-up CPA from the funnel, in USD."""
    return (1 / (ctr * cvr)) / 1000 * cpm


def assess(retail, landed, vat=0.15, currency="SAR"):
    curr = currency.upper()
    fx_rate = FX_RATES.get(curr, 3.75) if curr != "EUR" else (1 / 1.08)
    # Currency conversion helper (USD to target currency)
    def to_curr(usd_val):
        if curr == "EUR":
            return usd_val / 1.08
        return usd_val * fx_rate

    u = unit(retail, landed, vat)

    # Pick regional reference benchmark
    primary_chan = SNAP if curr in ("SAR", "AED", "KWD", "QAR") else TT

    cpa_lo = to_curr(primary_chan["cpa"])
    cpa_hi = to_curr(funnel_cpa(primary_chan["cpm"], primary_chan["ctr"], primary_chan["cvr"]))
    cpa_mid = to_curr(ECOM_CPA_USD)

    cac_gate = u["net"] >= CAC_SAFETY * cpa_mid
    retail_needed = (CAC_SAFETY * cpa_mid + landed) / (1 / (1 + vat) - 0.03)

    return {
        **u,
        "currency": curr,
        "primary_chan": primary_chan,
        "cpa_lo": cpa_lo,
        "cpa_mid": cpa_mid,
        "cpa_hi": cpa_hi,
        "best": u["net"] - cpa_lo,
        "median": u["net"] - cpa_mid,
        "worst": u["net"] - cpa_hi,
        "roas_verdict": "PROFIT" if primary_chan["roas"] > u["breakeven_roas"] else "LOSS",
        "cac_gate": cac_gate,
        "retail_needed": retail_needed,
    }


def report(retail, landed, vat=0.15, currency="SAR"):
    curr = currency.upper()
    a = assess(retail, landed, vat, currency=curr)
    chan = a["primary_chan"]
    sym = curr + " " if curr not in ("EUR", "USD") else ("€" if curr == "EUR" else "$")

    print(f"\nPROFITABILITY — retail {sym}{retail:.2f}, landed {sym}{landed:.2f}, VAT {vat:.0%} ({curr})\n")
    print(f"  net margin / sale        {sym}{a['net']:.2f}")
    print(f"  contribution rate        {a['cm_rate']:.1%} of gross retail")
    print(f"  breakeven ROAS           {a['breakeven_roas']:.2f}x")
    print(f"  {chan['label']} median ROAS  {chan['roas']:.2f}x  ->  {a['roas_verdict']}")
    print(f"\n  CAC RANGE for {curr} (benchmark vs bottom-up funnel):")
    for lbl, cpa, res in ((f"optimistic ({chan['label']} CPA)", a["cpa_lo"], a["best"]),
                          ("median (all-ecommerce benchmark)", a["cpa_mid"], a["median"]),
                          ("pessimistic (funnel-implied)", a["cpa_hi"], a["worst"])):
        print(f"  {lbl:36} CAC {sym}{cpa:6.2f}  ->  {sym}{res:+7.2f} / sale")

    print(f"\n  CAC gate (net >= {CAC_SAFETY:.0f}x median CPA): {'PASS' if a['cac_gate'] else 'FAIL'}")
    if not a["cac_gate"]:
        print(f"  To pass at this landed cost, retail must be about "
              f"{sym}{a['retail_needed']:.2f} — not {sym}{retail:.2f}.")

    if curr in ("SAR", "AED", "KWD", "QAR"):
        print(f"\n  GCC Traffic Stack: Snapchat KSA CPM ${SNAP['cpm']:.2f} vs TikTok GCC ${BENCHMARKS['TT_GCC']['cpm']:.2f} "
              f"-> Test on Snapchat Spotlight/Stories + TikTok GCC first.")
    else:
        print(f"\n  Meta DE CPM ${META_CPM_DE:.2f} vs TikTok ${TT['cpm']:.2f} "
              f"({META_CPM_DE/TT['cpm']:.1f}x) — test on TikTok first.")

    print("\n  PORTFOLIO — capital to find one winner:")
    for win in (0.05, 0.10, 0.20):
        lean_spend = 600 if curr in ("SAR", "AED") else 150
        real_spend = 1200 if curr in ("SAR", "AED") else 300
        print(f"    win rate {win:>4.0%}:  {sym}{lean_spend/win:>7,.0f} (lean)  ..  "
              f"{sym}{real_spend/win:>7,.0f} (realistic)")
    return 0 if a["cac_gate"] else 1


def selftest():
    ok = True
    cases = [
        ("breakeven ROAS is retail/net", lambda: abs(unit(34.90, 7.07, vat=0.19)["breakeven_roas"] - 34.90/unit(34.90,7.07, vat=0.19)["net"]) < 1e-9),
        ("zero landed cost raises net", lambda: unit(34.90, 0, vat=0.19)["net"] > unit(34.90, 7.07, vat=0.19)["net"]),
        ("thin margin fails the CAC gate (EUR)", lambda: not assess(34.90, 7.07, vat=0.19, currency="EUR")["cac_gate"]),
        ("high ticket passes the CAC gate (EUR)", lambda: assess(89.90, 18.00, vat=0.19, currency="EUR")["cac_gate"]),
        ("high ticket passes the CAC gate (SAR)", lambda: assess(249.00, 35.00, vat=0.15, currency="SAR")["cac_gate"]),
        ("funnel CPA exceeds reported CPA", lambda: funnel_cpa(TT["cpm"], TT["ctr"], TT["cvr"]) > TT["cpa"]),
        ("negative net -> infinite breakeven ROAS", lambda: unit(20.00, 30.00)["breakeven_roas"] == float("inf")),
        ("retail_needed actually passes", lambda: assess(assess(34.90, 7.07, vat=0.19, currency="EUR")["retail_needed"]+0.01, 7.07, vat=0.19, currency="EUR")["cac_gate"]),
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
    ap = argparse.ArgumentParser(description="Business-level profitability model (GCC & Global)")
    ap.add_argument("--retail", type=float, default=199.00)
    ap.add_argument("--landed", type=float, default=45.00)
    ap.add_argument("--vat", type=float, default=0.15)
    ap.add_argument("--currency", default="SAR", help="Currency code: SAR, AED, EUR, USD")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    sys.exit(selftest() if a.selftest else report(a.retail, a.landed, a.vat, a.currency))
