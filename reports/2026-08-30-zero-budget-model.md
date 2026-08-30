# Zero-Budget Model — 2026-08-30

**Constraint change: no ad spend, ever. The project must run free from start to finish.**

This voids a large part of the prior analysis. Stating that plainly rather than
quietly reworking it.

## 1. What this invalidates

| Prior conclusion | Status |
|---|---|
| CAC gate: net margin ≥ 2× median CPA | **VOID** — there is no CAC without ads |
| Target band €62–93 | **VOID** — the €62 floor existed only to cover CAC |
| Meta Ad Library competitor gate decides the market | **DEMOTED** — it proved *paid-ad* profitability, which is no longer the model |
| Capital requirement €1,500–6,000 | **VOID** — that was ad spend |
| AI-creative inversion above $100 AOV | **VOID** for this model — it was a ROAS finding |

**The €62–93 band was entirely an artefact of paid acquisition.** Remove ads and the
constraint inverts: cheaper products are now *better*, because impulse pricing converts
better from social feeds.

## 2. What the gates become

Without CAC, only two constraints survive from the True Margin Matrix:

- Net margin > €15
- Net margin ≥ 3× COGS (equivalently: landed cost ≤ 20.3% of VAT-inclusive retail)

**Binding floor: retail > €18.51.** Working band reopens to **€25–45**.

| Retail | Landed ceiling | Net (DE VAT) | Net (no VAT) |
|---|---|---|---|
| €24.90 | €5.04 | €15.13 | €19.11 |
| €29.90 | €6.06 | €18.17 | €22.95 |
| €34.90 | €7.07 | €21.21 | €26.78 |
| €44.90 | €9.10 | €27.29 | €34.46 |

The three organiser products killed on CAC grounds are **not automatically revived** —
they died on landed cost and Criterion 6 as well, and both of those still bind.

## 3. What free actually costs: reach

Organic is not free of cost, it is free of *cash*. The currency is posting volume.

Socialinsider, 2M videos across 214,507 profiles: accounts with **1–5K followers average
350 views per post**, down 23% year on year. Follower growth across small accounts is
down 33%. The platform is getting harder for new accounts, not easier.

Modelled at 1.7% site conversion:

| Click-to-store | 30 posts/mo | 60 posts/mo | 90 posts/mo |
|---|---|---|---|
| 1% | 1.8 sales | 3.6 sales | 5.4 sales |
| 2% | 3.6 sales | 7.1 sales | 10.7 sales |
| 3% | 5.4 sales | 10.7 sales | 16.1 sales |

At €21 net margin, 60 posts/month at a 2% click rate is **~€150/month**.

**The click-to-store rate above is an assumption, not a sourced figure.** Treat the
table as structure, not forecast.

**And the median is the wrong number to plan on.** Organic distribution is power-law:
the median post does 350 views and the business is decided by whether *any single post*
breaks out. This is the same hit-rate logic as paid creative testing, except the prize
is free traffic instead of a cheaper CPA. Volume is still the lever.

## 4. The one cost that cannot be zeroed — and how to avoid it

**Selling into the EU from Jordan requires an IOSS intermediary.** A seller not
established in the EU **cannot register for IOSS directly**. Cheapest realistic option
found: ~**€9.90/month** (10 transactions included, €1.50 per transaction beyond).

Skipping IOSS is not a free alternative — it moves the cost onto the customer as
surprise VAT and handling fees at delivery, producing refused and returned parcels. For
a new store with no brand trust, that is worse than the €9.90.

### The MENA alternative removes it entirely

| | EU | Jordan / MENA |
|---|---|---|
| IOSS intermediary | ~€9.90/mo, **mandatory** | Not applicable |
| EU import VAT | Applies | Not applicable |
| €3 flat customs duty per item | Applies | Not applicable |
| WEEE / battery registration | Applies to electricals | Not applicable |
| Meta Ad Library gate | EU/UK only — **but irrelevant without ads** | Irrelevant either way |
| Payment | Stripe/PayPal | PayPal confirmed working from Jordan |

**The constraint that forced EU-first was the Ad Library's EU/UK-only commercial data.
Without ads, that constraint does not exist.** MENA is the only genuinely
zero-cash configuration.

*Unverified*: Jordanian GST/sales-tax registration thresholds for a small online seller.
This must be checked before treating MENA as cost-free — it is the same class of
assumption that the EU IOSS requirement turned out to be.

## 5. The risk to the GPU thesis

The local-GPU advantage was argued on paid creative, where AI content tests at +12% CTR.
**Organic audiences are a different audience.** Social feeds reward content that reads as
authentic and in-the-room; obviously synthetic video tends to be punished, not ignored.

No benchmark was found for AI-generated content performance in *organic* feeds. This is
an open question, and it is load-bearing: if AI video underperforms organically, the
free model's volume advantage weakens badly and the answer becomes filming real product
clips on a phone.

**Test it before scaling on it.** Ship a mixed batch — AI-generated and phone-filmed —
and compare view-through on the same product.

## 6. Revised configuration

```
Market      MENA / Jordan first  (no IOSS, no EU VAT, no WEEE, no duty)
Traffic     Organic social only  (TikTok, Reels, Shorts)
Price band  EUR 25-45            (floor EUR 18.51)
Products    Non-electrical, impulse-priced, visually demonstrable
Supplier    CJdropshipping free tier
Store       Self-hosted, own hardware, free subdomain
Payment     PayPal (2.9% from revenue, no upfront)
Cash cost   EUR 0 upfront
Real cost   ~60 posts/month, sustained
```

## 7. What must change in the workspace

1. Remove the CAC gate from PROTOCOL-01 for this model — it measures a cost we no longer pay.
2. Restore the target band to €25–45; keep the €18.51 hard floor.
3. Demote the Meta Ad Library gate from "decides the market" to optional competitive context.
4. Add an organic-reach reality check: does this product have demonstrable content angles for 60 posts, or does it run out of ideas in ten?
5. Re-verify Jordanian tax thresholds before committing to MENA.

## Sources

- Socialinsider TikTok benchmarks 2026 (2M videos, 214,507 profiles) — https://www.socialinsider.io/social-media-benchmarks/tiktok
- IOSS intermediary requirement for non-EU sellers — https://easproject.com/ioss-intermediary/
- IOSS intermediary pricing comparison 2026 — https://goodvat.com/guides/selling-to-eu/ioss-intermediary-comparison/
