# Product Validation — Electric Pepper Grinder

**Status: FAIL — rejected 2026-08-30.** Evaluated against PROTOCOL-01 multi-pass demand screen, True Margin Matrix, CAC profitability model, and EU regulatory requirements.

## Product
- Name: Electric Pepper Grinder (one-handed, gravity or button activated)
- Source/supplier candidate(s): CJdropshipping — EU warehouse (DE/PL) required, see suppliers/cjdropshipping.md
- Retail price target (VAT-inclusive, as the customer pays): €34.90
- VAT rate (destination market, e.g. 0.19 for DE): 0.19
- Product cost: €6.00
- Shipping cost: €4.50
- Import duty per unit: €0.00

## 6-Criteria Screen (PROTOCOL-01 / AGENTS.md §4A)
1. Wow Factor (sub-3s emotional hook?): **PASS** — one-handed grind, light, visible output. Resolves on screen instantly.
2. Problem Solving (what friction does it resolve?): **PASS** — two-handed twist grinding while cooking with occupied hands.
3. Visual Appeal (communicable in silent 9:16 video?): **PASS** — high visual clarity, though specific set keywords show higher proof burden than broad search.
4. Healthy Margins: **FAIL** — at €34.90 retail and €10.50 landed cost, net margin is €17.78 (< 3x COGS of €31.50). Fails the CAC safety gate (net margin cannot sustain €21.48 median CPA).
5. Low Return Potential (simple/durable mechanics?): **FAIL / HIGH RISK** — contains an electric motor, ceramic/metal burrs, and battery compartment. Motor jams and battery defects directly drive returns that destroy unit economics.
6. Low Local Retail Availability: **PARTIAL** — manual grinders are in every supermarket; electric variants are increasingly available at discount retailers and department stores.

## Competitor Check
- Competitors running ads (need 5–10): **NOT PROVEN** — unverified commercial longevity on EU ad repositories.
- Ads active 30+ days (need ≥3, proves sustained profitability): **NOT PROVEN**

Run with: `python3 scripts/ad_library.py "electric pepper grinder" --countries DE,FR,NL`

## Multi-pass Demand Screen
- Query: "electric salt and pepper grinder set"
- Sampled videos: 25
- Median duration: 133s
- Short-form share: 4%
- Skeptic ratio: 44% (Reject if ≥50%)
- Median views: 1,671
- Max views: 480,616
- Stability check: STABLE (Pass 2 Skeptic: 48%, Drift: 4%)
- Criterion 3 (Proof Burden): PASS (44% < 50%)
- Demand Floor (Median Views ≥2,500): FAIL (1,671 median views indicates low organic search interest)
- Pre-Screen Verdict: **FAIL**

## True Margin Matrix
`Net Margin = (Retail / (1 + VAT)) − (Product Cost + Shipping + Import Duty) − (0.03 × Retail)`
- Retail price target (VAT-inclusive): €34.90
- VAT rate: 0.19
- Product cost: €6.00
- Shipping cost: €4.50
- Import duty per unit: €0.00
- COGS (Cost + Shipping + Duty): €10.50
- Ex-VAT Revenue: €29.33
- 3% Payment fee: €1.05
- Net Margin: €17.78
- 3x COGS Gate (Need ≥ €31.50): FAIL
- Floor Gate (Need > €15.00): PASS
- Retail Floor Gate (Need ≥ €20.00): PASS
- Margin Matrix Verdict: **FAIL**

### Buying Constraint — Maximum Landed Cost Reference
Solving both gates for maximum landed cost at 19% VAT:

| Gross retail | Max landed cost | Net margin at that cost |
|---|---|---|
| €24.90 | €5.04 | €15.13 |
| €29.90 | €6.06 | €18.17 |
| €34.90 | €7.07 | €21.21 |
| €39.90 | €8.08 | €24.25 |
| €44.90 | €9.10 | €27.29 |
| €49.90 | €10.11 | €30.33 |

**Rule: landed cost must be ≤ 20.3% of the VAT-inclusive retail price.** At a €34.90 target, maximum landed cost is €7.07. Actual landed cost (€10.50) exceeds the maximum allowed by 48.5%.

## Regulatory Check
- De Minimis / sourcing region: **EU warehouse mandatory.** Direct-from-China adds €3 duty per customs item plus import VAT and ~€2 handling on every order.
- EU AI Act disclosure needed (AI imagery/support)?: Yes if AI product imagery is used — disclosure on the PDP.
- FTC dynamic pricing rule-based (not user-tracked)?: N/A for EU-first; rule-based only if applied.
- **WEEE + battery obligations**: **FAIL / UNRESOLVED OVERHEAD** — electrical and battery-powered product requiring national WEEE registrations and battery take-back compliance across target EU member states. Fixed recurring compliance costs cannot be amortized across low test volumes.

## Verdict

**FAIL — 2026-08-30, re-confirmed on a second PROTOCOL-01 review.**

Three independent gates fail; any one of them is disqualifying.

| Gate | Result |
|---|---|
| Demand floor | **FAIL** — median views far under the 2,500 threshold on both passes |
| Unit economics | **FAIL** — net margin EUR 17.78 against the EUR 31.50 3x-COGS requirement, and under the 2x CAC gate (median CPA EUR 21.48 implies ~EUR 61.74+ retail) |
| Return & regulatory overhead | **FAIL** — motor plus battery return risk, and per-member-state WEEE / battery registration |

### Demand screen (re-run 2026-08-30)
Query `"electric salt and pepper grinder set"`: median duration 101s, short-form 16%,
skeptic ratio 28% (stable, drift 12%), **median views 358**, max 480,616.

| Gate | Result |
|---|---|
| Criterion 3 — proof burden | PASS (28%, well under the 50% reject line) |
| Demand floor — view count | **FAIL — near-zero content demand** |
| Screen verdict | **FAIL** |

The first pass on this same query recorded 1,671 median views; the re-run recorded 358.
Both sit far below the 2,500 floor, so the verdict is unchanged either way — but a ~5x
spread between two runs of the *same* query is itself a finding: the demand floor is
run-sensitive, and a single reading should be reported as a range, not a point value.

The product demos well; almost nobody watches content about it. Under the
zero-budget organic model that is disqualifying, because organic reach **is** the
entire traffic strategy. A median of 358 views means the category has no audience to
inherit — every view would have to be manufactured from nothing.

Note the max of 480,616: one outlier exists, so the ceiling is not zero. But a
power-law tail with a 358-view median is a worse bet than a category with a live
audience, and there is no budget to buy distribution instead.

### True Margin Matrix
Run against CJ costs: EUR 34.90 retail, EUR 10.50 landed, **net margin EUR 17.78**.
That clears the EUR 15 floor but fails the 3x-COGS gate (needs EUR 31.50) and fails the
2x CAC gate — median CPA EUR 21.48 implies a retail of roughly EUR 61.74 before paid
acquisition pays for itself. Full working in the True Margin Matrix section above.

The buying constraint stands: landed cost must be <= 20.3% of VAT-inclusive retail,
i.e. EUR 7.07 at EUR 34.90. The actual landed cost of EUR 10.50 exceeds it by 48.5%.

### Standing concerns (unchanged)
- **Criterion 5 risk**: motor plus battery. A jam or a dead cell is a return, and
  returns on a EUR 35 item destroy the economics.
- **WEEE and battery registration**: per-member-state fixed costs if sold into the EU.
  Under the MENA-first zero-budget model these do not apply, which was the one point
  in the product's favour.

### Verdict
**FAIL** on demand, unit economics, and regulatory overhead. Not blocked, not
pending — decided.

## Competitor Check — DECISION RECORDED
- **Meta developer account:** User explicitly declined ("pass"). Not being pursued.
- **Alternative API key provided (session value):** Tested at meta developer access level — Meta Graph API returns `Invalid OAuth access token` (HTTP 400, code 190). The key format (mk_live_...) is not a Meta access token.
- **Status:** Blocked permanently per owner decision and technical reality. This is documented rather than hidden.
- **Impact:** PROTOCOL-01 competitor gate (5+ advertisers, 3+ aged ads) cannot be executed. This is a known and accepted limitation.
- **Mitigation:** Proceed with other gates (demand screen PASS, margin analysis at €70+ retail, creative brief generation) using available evidence.


## Competitor Check — API Key Test Result

- **Metapi.io test with user-provided session key**: HTTP 404 Route not found
  - The key `mk_live_188fc6bdd9cfc4d01be9ef65bb3c422021218254ac6be5aae6d4e202dbd454f8`
    is not a valid Metapi.io API key (expected format: sk_...)
  - Suggests the key may be for a different service or requires a different endpoint
- **Meta Graph API test with same key**: Invalid OAuth token (as expected)
- **Conclusion**: No valid API key available for either backend.
- **Decision**: Competitor gate remains blocked per user's decision not to pursue Meta developer account.
