# Product Validation — Folding Laundry Basket

**Status: FAIL — rejected 2026-08-30.** Evaluated against PROTOCOL-01 multi-pass demand screen, True Margin Matrix, supplier freight economics, and retail availability.

## Product
- Name: Folding Laundry Basket (collapsible, fabric/mesh, pop-up frame)
- Source/supplier candidate(s): CJdropshipping (`CJYD219063801AZ` / `CJJT149560501AZ`) — see suppliers/cjdropshipping.md
- Retail price target (VAT-inclusive, as the customer pays): €34.90
- VAT rate (destination market, e.g. 0.19 for DE): 0.19
- Product cost: €2.44
- Shipping cost: €8.00
- Import duty per unit: €0.00

## 6-Criteria Screen (PROTOCOL-01 / AGENTS.md §4A)
1. Wow Factor (sub-3s emotional hook?): **PASS** — instant pop-open, satisfying transformation from flat to full basket.
2. Problem Solving (what friction does it resolve?): **PASS** — bulky laundry hampers eat floor space; this collapses to 2 cm when not in use.
3. Visual Appeal (communicable in silent 9:16 video?): **PASS — evidenced, not assumed.** Multi-pass demand screen: median video 175s, 20% short-form share, 12% skeptic-framed (reject if ≥50%), 15,465 median views. Passes proof-burden and demand-floor gates.
4. Healthy Margins: **FAIL** — landed freight kills unit economics. Landed cost of €10.44 ($11.27) yields a net margin of €17.84 at €34.90 retail, failing the 3x-COGS gate (€31.32 required).
5. Low Return Potential (simple/durable mechanics?): **PASS** — no electronics, no moving parts beyond spring steel frame; fabric/mesh is durable and washable.
6. Low Local Retail Availability: **FAIL** — ubiquitous commodity stocked at IKEA, Action, Lidl, and Kaufland at €5–15, capping realistic retail price ceiling below viable margin thresholds.

## Competitor Check (Metapi.io — live data 2026-08-30)
- Competitors running ads (need 5–10): **11 ads found** across 3 distinct pages (Women's Lifestyle, Sovely, Lucky Catch) — **PASS**
- Ads active 30+ days (need ≥3, proves sustained profitability): **0 ads with >30 day run** — **FAIL** (all campaigns started 2026-08-20 or later, none older than 10 days)
- Metapi task: `iesuIvugrWAiXv6y` (DE, active, all ad types, eu_data=true)

**Key finding**: The "Denise Whitfield" laundry detergent ad creative is running on Women's Lifestyle and Sovely pages — this is a **detergent/cleaner** ad, not a folding laundry basket product ad. Lucky Catch ads are mobile game ads ("White text...", CTA: "Play game"). **No true folding laundry basket competitor ads found** in current DE Ad Library snapshot.

Run with: `python3 scripts/ad_library.py "folding laundry basket" --countries DE,FR,NL`

## Multi-pass Demand Screen
- Query: "folding laundry basket organizer"
- Sampled videos: 25
- Median duration: 175s
- Short-form share: 20%
- Skeptic ratio: 12% (Reject if ≥50%)
- Median views: 15,465
- Max views: 248,035
- Stability check: STABLE (Pass 2 Skeptic: 24%, Drift: 12%)
- Criterion 3 (Proof Burden): PASS (12% < 50%)
- Demand Floor (Median Views ≥2,500): PASS (15,465 median views confirms strong organic interest)
- Pre-Screen Verdict: **PASS**

## True Margin Matrix
`Net Margin = (Retail / (1 + VAT)) − (Product Cost + Shipping + Import Duty) − (0.03 × Retail)`
- Retail price target (VAT-inclusive): €34.90
- VAT rate: 0.19
- Product cost: €2.44
- Shipping cost: €8.00
- Import duty per unit: €0.00
- COGS (Cost + Shipping + Duty): €10.44
- Ex-VAT Revenue: €29.33
- 3% Payment fee: €1.05
- Net Margin: €17.84
- 3x COGS Gate (Need ≥ €31.32): FAIL
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

**Rule: landed cost must be ≤ 20.3% of the VAT-inclusive retail price.** At a €34.90 target, maximum landed cost is €7.07. Actual landed cost (€10.44) exceeds the maximum allowed by 47.7%.

## Regulatory Check
- De Minimis / sourcing region: **EU warehouse mandatory.** Direct-from-China adds €3 duty per customs item plus import VAT and ~€2 handling on every order, which alone consumes ~70% of the €7.07 cost budget at a €34.90 retail.
- EU AI Act disclosure needed (AI imagery/support)?: Yes if AI product imagery is used — disclosure on the PDP.
- FTC dynamic pricing rule-based (not user-tracked)?: N/A for EU-first; rule-based only if applied.
- **WEEE + battery obligations**: **NONE** — non-electrical, no battery.
- **Textile / REACH**: Fabric/mesh may contact skin — verify AZO-dye-free and REACH compliance for EU.

## Verdict
FAIL — rejected 2026-08-30 on independent lines of evidence:
1. **Supplier freight cost: FAIL.** CJ live parcel freight to Germany ($8.64) brings landed cost to $11.27 (€10.44). At €34.90 retail, net margin of €17.84 fails the 3x-COGS gate (€31.32 required). To clear 3x-COGS, retail would need to exceed €51.43. Evidence: `reports/2026-08-30-cj-mcp-cost-check.md`.
2. **Criterion 6 (Low Local Retail Availability): FAIL.** Stocked broadly by IKEA, Action, Lidl, and Kaufland at €5–15. Local availability caps achievable retail price, making the required >€50 price point commercially unfeasible.
3. **Competitor Gate: FAIL.** 11 competitor ads found in DE Ad Library, but 0 are true folding laundry basket product ads and 0 have run 30+ days.
