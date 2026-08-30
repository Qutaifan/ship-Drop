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
FAIL — rejected on multiple independent gates:
1. **Demand Floor: FAIL.** Multi-pass demand screen on "electric salt and pepper grinder set" yielded 1,671 median views (below the 2,500 threshold).
2. **Unit Economics: FAIL.** At €34.90 retail and €10.50 landed cost, net margin is €17.78, failing the 3x-COGS requirement (€31.50) and failing the 2x CAC profitability gate (median CPA €21.48 requires ~€61.74+ retail).
3. **Return & Regulatory Overhead: FAIL.** High mechanical/electrical failure risk (Criterion 5) plus mandatory EU WEEE/battery compliance obligations create prohibitive operational friction.
