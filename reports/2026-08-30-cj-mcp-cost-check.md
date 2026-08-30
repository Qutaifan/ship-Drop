# CJ MCP Cost Check — 2026-08-30

**Purpose:** use CJ's official MCP/API path to remove the supplier-cost blocker where possible.

**MCP path used:** official `CJ-dropshipping/api-mcp` server, direct-token HTTP mode for CJ account `CJ5775672`.

**Security note:** the access token is intentionally not recorded in this repo report.

## Setup Verified

| Check | Result |
|---|---|
| MCP server source | `https://github.com/CJ-dropshipping/api-mcp.git` |
| Local checkout | `Q:/cj-mcp-server` |
| Runtime | Node.js `>=20`, local Node verified as available |
| HTTP server | `http://localhost:3009/mcp` |
| Direct-token auth | **WORKING** — `check_login_status` returns URL direct token mode for `CJ5775672` |
| Search API | **WORKING** — `search_products` returns live CJ catalog results |
| Variant API | **WORKING** — `get_product_variants` returns variant IDs, weights, prices |
| Freight API | **WORKING** — `calculate_freight` returns Germany freight options |

## Buying Constraint Reference

At DE VAT 19%, the maximum landed cost allowed by the True Margin Matrix is:

| Gross retail | Max landed cost |
|---|---:|
| €24.90 | €5.04 |
| €29.90 | €6.06 |
| €34.90 | €7.07 |
| €39.90 | €8.08 |
| €44.90 | €9.10 |

`Landed cost = CJ variant sell price + freight + import duty/clearance if not already included.`

## Live CJ Evidence — Germany Destination

| Candidate | CJ product / variant checked | Product price (USD) | Lowest freight to DE (USD) | Best method / time | Landed cost before duty | Constraint result |
|---|---|---:|---:|---|---:|---|
| Folding laundry basket | `CJYD219063801AZ` — Foldable moisture-proof stripes basket | $2.63 | $8.64 | CJPacket Ordinary I / 8–18d | **$11.27** | **FAIL** — above €9.10 even at €44.90 |
| Folding laundry basket alt | `CJJT149560501AZ` — Round waterproof single layer basket | $5.87 | $7.60 | CJPacket Ordinary I / 8–18d | **$13.47** | **FAIL** |
| Folding laundry basket alt | `CJYD239731301AZ` — Double-layer foldable basket | $6.62 | $25.14 | YunExpress Ordinary / 6–8d | **$31.76** | **FAIL** |
| Cable management box / bag | `CJJT107047201AZ` — Cable organizer travel bag | $3.95 | $7.68 | CJPacket Ordinary I / 8–18d | **$11.63** | **FAIL** for current target |
| Cable management small box | `CJYD237724401AZ` — Data cable power bank storage box | $0.56 | $4.93 | CJPacket Eub / 12–50d | **$5.49** | **MARGIN-POSSIBLE**, but product mismatch: small 13.5×9×5cm box, weak €30–45 retail plausibility |
| Drawer organizer proxy | `CJJT110132001AZ` — Desktop/makeup stackable drawer organizer | $1.92 | $8.82 | CJPacket Ordinary I / 8–18d | **$10.74** | **FAIL** at €44.90 |

## What The Data Reveals

1. **The direct-token MCP path works.** The previous `Invalid API key or access token` blocker is resolved when the supplied `MCP@CJ5775672@CJ:<token>` URL format is used.
2. **Freight kills the current top candidates from China-origin CJ stock.** The products are cheap enough at SKU level, but Germany parcel freight alone exceeds the landed-cost ceiling for most candidates.
3. **EU warehouse filtering is still the key.** Direct-from-China prices do not satisfy the ≤20.3% landed-cost rule for bulky organizers. These candidates only remain viable if there is true EU warehouse stock with materially lower local shipping.
4. **The small cable box is numerically viable but commercially weak.** It clears the raw landed-cost ceiling at €29.90+, but the product is too small/basic to justify the €30–45 target without bundling or a stronger premium angle.

## Decision

No product receives a PASS verdict. The competitor gate is still unrun, and the CJ supplier-cost evidence currently rejects the obvious China-origin variants.

**Actionable next filter:** search only CJ global warehouse / EU-stocked products and discard bulky items unless EU-local freight puts landed cost under €7.07 at a €34.90 target.

## Raw Evidence Files

- `reports/cj-direct-token-product-search.json`
- `reports/cj-direct-token-cost-evidence.json`
- `reports/cj-variants-raw.txt`
- `reports/cj-freight-de-raw.txt`
