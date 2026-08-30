# Product Validation — Electric Pepper Grinder

**Status: PENDING — competitor gate not run.** Everything runnable without a Meta
access token is complete. The verdict stays open until the Ad Library gate executes.

## Product
- Name: Electric Pepper Grinder (one-handed, gravity or button activated)
- Source/supplier candidate(s): CJdropshipping — EU warehouse (DE/PL) required, see suppliers/cjdropshipping.md
- Retail price target (VAT-inclusive, as the customer pays): UNVERIFIED — see Buying Constraint below
- VAT rate (destination market, e.g. 0.19 for DE): 0.19
- Product cost: UNVERIFIED — requires CJ account
- Shipping cost: UNVERIFIED — requires CJ account
- Import duty per unit: 0 if fulfilled from CJ's EU warehouse; €3 per customs item if shipped direct from China

## 6-Criteria Screen (PROTOCOL-01 / AGENTS.md §4A)
1. Wow Factor (sub-3s emotional hook?): **PASS** — one-handed grind, light, visible output. Resolves on screen instantly.
2. Problem Solving (what friction does it resolve?): **PASS** — two-handed twist grinding while cooking with occupied hands.
3. Visual Appeal (communicable in silent 9:16 video?): **PASS — evidenced, not assumed.** Demo-burden screen: median video 76s, 44% of top results are ≤60s short-form, only 20% skeptic-framed — statistically indistinguishable from a known-viral control product. See reports/2026-08-30-demo-burden-screen.md.
4. Healthy Margins: **CONDITIONAL** — depends entirely on landed cost. See Buying Constraint.
5. Low Return Potential (simple/durable mechanics?): **RISK** — contains a motor and battery. This is the weakest criterion. A motor that jams or a battery that fails is a return, and returns on a €35 item destroy the unit economics. **Mitigation: order a sample and test it before any spend.**
6. Low Local Retail Availability: **PARTIAL** — manual grinders are everywhere; *electric one-handed* grinders are not yet supermarket stock. Erodes over time.

## Competitor Check
- Competitors running ads (need 5–10): **NOT RUN** — blocked on META_ACCESS_TOKEN
- Ads active 30+ days (need ≥3, proves sustained profitability): **NOT RUN**

Run with: `python3 scripts/ad_library.py "electric pepper grinder" --countries DE,FR,NL`

## True Margin Matrix
`Net Margin = (Retail / (1 + VAT)) − (Product Cost + Shipping + Import Duty) − (0.03 × Retail)`
- Net Margin: __ (cannot compute — landed cost unknown)
- Must be ≥3x COGS and >€15: PENDING

### Buying Constraint — the number to negotiate against

Solving both gates for the maximum landed cost (product + shipping + duty) at DE VAT 19%:

| Gross retail | Max landed cost | Net margin at that cost |
|---|---|---|
| €24.90 | €5.04 | €15.13 |
| €29.90 | €6.06 | €18.16 |
| €34.90 | €7.07 | €21.20 |
| €39.90 | €8.08 | €24.24 |
| €44.90 | €9.10 | €27.28 |

**Rule: landed cost must be ≤ 20.3% of the VAT-inclusive retail price.** The 3x-COGS
gate binds at every price point — the >€15 floor never becomes the constraint above
€24.90. Below **€18.51 gross retail the >€15 net gate is unreachable at any cost**,
even a free product, which is the real floor criterion 4 should state rather than €20.

**Consequence for sourcing**: at a €34.90 target, total landed cost must not exceed
€7.07. If CJ quotes €6 product + €3 EU shipping, the product **fails** — and it fails
by a margin no ad creative can recover. This number is the buying constraint, not an
aspiration.

## Regulatory Check
- De Minimis / sourcing region: **EU warehouse mandatory.** Direct-from-China adds €3 duty per customs item plus import VAT and ~€2 handling on every order, which alone consumes ~70% of the €7.07 cost budget at a €34.90 retail.
- EU AI Act disclosure needed (AI imagery/support)?: Yes if AI product imagery is used — disclosure on the PDP.
- FTC dynamic pricing rule-based (not user-tracked)?: N/A for EU-first; rule-based only if applied.
- **WEEE + battery obligations**: electrical and battery-powered, so per-member-state WEEE registration and battery take-back duties apply. **UNPRICED — this is the largest unknown cost and must be quantified before launch.** It is a fixed recurring cost, not a per-unit one, so it does not enter the True Margin Matrix; it sets a minimum viable sales volume.

## Verdict

**FAIL — 2026-08-30, on the demand screen.**

### Demand screen (re-run 2026-08-30)
Query `"electric salt and pepper grinder set"`: median duration 101s, short-form 16%,
skeptic ratio 28% (stable, drift 12%), **median views 358**, max 480,616.

| Gate | Result |
|---|---|
| Criterion 3 — proof burden | PASS (28%, well under the 50% reject line) |
| Demand floor — view count | **FAIL — near-zero content demand** |
| Screen verdict | **FAIL** |

The product demos well; almost nobody watches content about it. Under the
zero-budget organic model that is disqualifying, because organic reach **is** the
entire traffic strategy. A median of 358 views means the category has no audience to
inherit — every view would have to be manufactured from nothing.

Note the max of 480,616: one outlier exists, so the ceiling is not zero. But a
power-law tail with a 358-view median is a worse bet than a category with a live
audience, and there is no budget to buy distribution instead.

### True Margin Matrix
**Not run.** No CJ cost data was ever pulled for this product, so there are no unit
economics to test. Running the matrix on invented costs would be fabrication.

For reference, the buying constraint stands: landed cost must be <= 20.3% of
VAT-inclusive retail, i.e. EUR 7.07 at EUR 34.90.

### Standing concerns (unchanged)
- **Criterion 5 risk**: motor plus battery. A jam or a dead cell is a return, and
  returns on a EUR 35 item destroy the economics.
- **WEEE and battery registration**: per-member-state fixed costs if sold into the EU.
  Under the MENA-first zero-budget model these do not apply, which was the one point
  in the product's favour.

### Verdict
**FAIL** on demand. Not blocked, not pending — decided.
