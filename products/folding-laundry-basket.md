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

**FAIL — re-confirmed 2026-08-30 on a second PROTOCOL-01 review.**

### Demand screen (re-run 2026-08-30)
Query `"folding laundry basket organizer"`: median duration 175s, short-form 20%,
skeptic ratio 12% (stable, drift 8%), median views 25,287. Screen verdict: **PASS**.

**That PASS is not evidence about the product.** The same product returned a median of
405 views under `"folding laundry basket"` and 2,868 under another run of the same
query. A one-word change to the query moves the demand metric roughly 60x. The demand
floor is **query-sensitive, not product-sensitive**, and cannot revive a candidate on
its own. Logged as a known limitation of the screen.

### True Margin Matrix — real CJ landed costs
`Net = (Retail / 1.19) - landed - (0.03 x Retail)`   →  net = 0.8103 x Retail - landed

| CJ variant | Landed (EUR) | Retail for net > EUR 15 | Retail for net >= 3x COGS | **Binding** | Net @ EUR 34.90 |
|---|---|---|---|---|---|
| CJYD219063801AZ ($2.63 + $8.64) | 10.44 | 31.39 | **51.51** | **EUR 51.51** | 17.85 → FAIL |
| CJJT149560501AZ ($5.87 + $7.60) | 12.47 | 33.90 | **61.57** | **EUR 61.57** | 15.81 → FAIL |
| CJYD239731301AZ ($6.62 + $25.14) | 29.41 | 54.80 | **145.16** | **EUR 145.16** | -1.13 → FAIL |

The 3x-COGS gate binds in every case, not the EUR 15 floor. The cheapest sourced
variant needs **EUR 51.51 retail** to clear both gates.

### Why that is fatal
A folding laundry basket is an IKEA, Action, Lidl and Kaufland staple selling at
EUR 10-15. Criterion 6 fails, and local availability caps the achievable price far
below the EUR 51.51 the cost base demands. The gap is not closeable by creative,
positioning or a better supplier variant — all three sourced variants fail, and the
cheapest one fails by EUR 16.61 of retail price.

**Freight, not product cost, is the killer**: $7.60-$25.14 per parcel against product
costs of $2.63-$6.62.

### Verdict
**FAIL.** No further work. Revisit only if CJ EU-warehouse stock removes the freight
line entirely — and even then Criterion 6 still binds.
