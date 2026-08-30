# Product Validation — Folding Laundry Basket

**Status: PENDING — competitor gate not run.** Everything runnable without a Meta access token is complete. The verdict stays open until the Ad Library gate executes.

## Product
- Name: Folding Laundry Basket (collapsible, fabric/mesh, pop-up frame)
- Source/supplier candidate(s): CJdropshipping — EU warehouse (DE/PL) required, see suppliers/cjdropshipping.md
- Retail price target (VAT-inclusive, as the customer pays): UNVERIFIED — see Buying Constraint below
- VAT rate (destination market, e.g. 0.19 for DE): 0.19
- Product cost: UNVERIFIED — requires CJ account
- Shipping cost: UNVERIFIED — requires CJ account
- Import duty per unit: 0 if fulfilled from CJ's EU warehouse; €3 per customs item if shipped direct from China

## 6-Criteria Screen (PROTOCOL-01 / AGENTS.md §4A)
1. Wow Factor (sub-3s emotional hook?): **PASS** — instant pop-open, satisfying transformation from flat to full basket.
2. Problem Solving (what friction does it resolve?): **PASS** — bulky laundry hampers eat floor space; this collapses to 2 cm when not in use.
3. Visual Appeal (communicable in silent 9:16 video?): **PASS — evidenced, not assumed.** Demo-burden screen: median video 83s, 32% of top results are ≤60s short-form, only 4% skeptic-framed — well within the proven-viral band (control/pepper-grinder at 20%). See reports/2026-08-30-candidate-sweep.md.
4. Healthy Margins: **CONDITIONAL** — depends entirely on landed cost. See Buying Constraint.
5. Low Return Potential (simple/durable mechanics?): **PASS** — no electronics, no moving parts beyond spring steel frame; fabric/mesh is durable and washable.
6. Low Local Retail Availability: **PARTIAL** — basic laundry baskets are everywhere; *collapsible pop-up* designs are not yet supermarket stock. Erodes over time.

## Competitor Check (Metapi.io — live data 2026-08-30)
- Competitors running ads (need 5–10): **11 ads found** across 3 distinct pages (Women's Lifestyle, Sovely, Lucky Catch) — **PASS**
- Ads active 30+ days (need ≥3, proves sustained profitability): **0 ads with >30 day run** — **FAIL** (all campaigns started 2026-08-20 or later, none older than 10 days)
- Metapi task: `iesuIvugrWAiXv6y` (DE, active, all ad types, eu_data=true)

**Key finding**: The "Denise Whitfield" laundry detergent ad creative is running on Women's Lifestyle and Sovely pages — this is a **detergent/cleaner** ad, not a folding laundry basket product ad. Lucky Catch ads are mobile game ads ("White text...", CTA: "Play game"). **No true folding laundry basket competitor ads found** in current DE Ad Library snapshot.

Run with: `python3 scripts/ad_library.py "folding laundry basket" --countries DE,FR,NL`

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

**Rule: landed cost must be ≤ 20.3% of the VAT-inclusive retail price.** The 3x-COGS gate binds at every price point — the >€15 floor never becomes the constraint above €24.90. Below **€18.51 gross retail the >€15 net gate is unreachable at any cost**, even a free product, which is the real floor criterion 4 should state rather than €20.

**Consequence for sourcing**: at a €34.90 target, total landed cost must not exceed €7.07. If CJ quotes €6 product + €3 EU shipping, the product **fails** — and it fails by a margin no ad creative can recover. This number is the buying constraint, not an aspiration.

## Regulatory Check
- De Minimis / sourcing region: **EU warehouse mandatory.** Direct-from-China adds €3 duty per customs item plus import VAT and ~€2 handling on every order, which alone consumes ~70% of the €7.07 cost budget at a €34.90 retail.
- EU AI Act disclosure needed (AI imagery/support)?: Yes if AI product imagery is used — disclosure on the PDP.
- FTC dynamic pricing rule-based (not user-tracked)?: N/A for EU-first; rule-based only if applied.
- **WEEE + battery obligations**: **NONE** — non-electrical, no battery.
- **Textile / REACH**: Fabric/mesh may contact skin — verify AZO-dye-free and REACH compliance for EU.

## Verdict
**FAIL** — rejected 2026-08-30 on independent lines of evidence. Not blocked; decided.

1. **Supplier cost: FAIL.** CJ live freight to Germany, three variants checked: landed $11.27, $13.47 and $31.76 against a EUR 9.10 ceiling at EUR 44.90 retail - the most generous price point on the board. Freight alone breaks it. Evidence: `reports/2026-08-30-cj-mcp-cost-check.md`.

2. **Competitor gate: not run** for this candidate, and it does not matter. A product that cannot be landed under the ceiling fails before the gate becomes relevant.

3. **Criterion 6 (low local retail availability): FAIL.** Stocked by IKEA, Action, Lidl and Kaufland. Local availability caps the achievable price, which drags Criterion 4 down with it — the margin model needs EUR 30-45 gross retail and the shelf price is a fraction of that. No creative recovers a product whose market price is a third of what the unit economics require.

**Provenance note**: this candidate entered the pipeline through the 2026-08-30 candidate sweep, whose skeptic-ratio figures did not reproduce against its own stored data (9 of 10 wrong, every error optimistic). See `reports/2026-08-30-sweep-audit.md`. The ranking that selected it was not evidence.
