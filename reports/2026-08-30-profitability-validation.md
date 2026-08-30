# Profitability Validation — 2026-08-30

> **AMENDED 2026-08-30** — the verdict below was overstated. It rested on the TikTok
> median ROAS (1.51x) alone. The same benchmark house's all-paid-channel figures
> (AOV $61.22 ÷ CPA $23.20 = 2.64x) clear our 1.65x breakeven with headroom. The
> correct reading is **channel-dependent, not unviable**. The €34.90 price point fails
> either way; the price-band conclusion stands and is now narrowed to €62–93. See
> `reports/2026-08-30-leverage-and-tech.md`.

**Verdict: the project does not have a viable business model at the price band it has
been selecting for. The unit economics fail on advertising cost, and the existing
gates cannot see it.**

## 1. The structural hole

`PROTOCOL-01` validates net margin against **COGS**. It never mentions **customer
acquisition cost**. A product can clear the 3x-COGS gate, receive a PASS, and lose
money on every sale the moment it is advertised — because the gate does not know
advertising exists.

Every candidate screened so far has been measured against the wrong constraint.

## 2. The numbers, at the current target

Retail €34.90, landed cost €7.07 (the ceiling the buying constraint allows), DE VAT 19%:

| | |
|---|---|
| Net margin per sale | **€21.21** |
| Contribution rate | 60.8% of gross retail |
| **Breakeven ROAS** | **1.65x** |
| TikTok median ROAS (5,900 brands) | **1.51x** |
| Result | **The median advertiser loses money on this cost structure** |

We need to outperform the median advertiser just to reach zero.

## 3. CAC is a range, and the range straddles zero

The benchmark source is internally inconsistent: it reports a median TikTok CPA of
$17.07, while its own CPM × CTR × CVR implies $42.88 — a **2.5x spread**. Any single
CPA number here is false precision, so the honest treatment is a range:

| Scenario | CAC | Result per sale |
|---|---|---|
| Optimistic — reported TikTok CPA | €15.81 | **+€5.41** |
| Median — all-ecommerce CPA (53,000+ brands) | €21.48 | **−€0.27** |
| Pessimistic — funnel-implied | €39.70 | **−€18.49** |

At the median the business breaks exactly even **before a single fixed cost**. There
is no room for WEEE registration, a domain, a failed test, a refund, or a chargeback.

## 4. What would have to be true

To earn 2x contribution over CAC — the minimum that survives variance — the required
CAC is **€10.61**, which means beating the median ecommerce CPA by **51%**. That is
not "run ads competently." That is top-decile performance, sustained, as the
precondition for the model working at all.

**The alternative is to raise the price.** At the same landed cost, retail needs to be
about **€61.74** to clear a 2x CAC gate. At the 20.3% landed-cost ceiling, the general
rule is retail ≈ **€70+**.

This invalidates two rules currently in `AGENTS.md`:
- The €20 retail floor (already shown to be arithmetically wrong; now also
  commercially irrelevant).
- The €30–45 target band every sweep has been screening for.

**The project has been hunting in a price band that cannot support paid acquisition.**

## 5. The capital requirement the free/OSS framing hides

Product testing is a search process, and the search costs money regardless of how free
the software is:

| Win rate | Lean (€150/test) | Realistic (€300/test) |
|---|---|---|
| 5% | €3,000 | €6,000 |
| 10% | €1,500 | €3,000 |
| 20% | €750 | €1,500 |

The free/OSS stack saves perhaps €30–50/month in SaaS. **It does nothing about the
€1,500–€6,000 of ad spend required to find one winner.** That is the real capital
requirement, and it has never appeared in any project document until now.

## 6. Corrected gates

1. **Add a CAC gate to PROTOCOL-01**: net margin ≥ 2× the median CPA benchmark. Run
   `python3 scripts/profitability.py --retail R --landed L` — it exits 1 on failure.
2. **Raise the price band**: target **€70–120 gross retail**, not €30–45. Higher ticket
   is the only structural fix that does not depend on beating the market at ads.
3. **Test on TikTok first**: CPM $4.08 against Meta Germany's $9.05, a 2.2x advantage
   per impression.
4. **Budget the search, not the product.** Decide the testing capital up front and
   treat it as the cost of the experiment, not as overhead to be minimised.

## 7. Effect on the current pipeline

**Electric pepper grinder — FAILS the CAC gate at €34.90.** It is not rescuable by
better creative; the price point cannot carry median acquisition cost. It survives
only if it can retail near €70, which for an electric grinder is plausible only in a
premium positioning with matching product quality — a different product from the one
screened.

No candidate in the workspace currently passes a profitability-aware gate.

## Sources

- Triple Whale, ecommerce and TikTok benchmarks, Aug 2025–Jul 2026, 53,000+ brands — https://www.triplewhale.com/blog/ecommerce-benchmarks · https://www.triplewhale.com/blog/tiktok-benchmarks
- Lebesgue, Facebook CPM by country 2026 — https://lebesgue.io/facebook-ads/facebook-cpm-by-country
