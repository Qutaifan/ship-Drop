# Supplier — CJdropshipping

## Supplier
- Name: CJdropshipping
- Platform: CJdropshipping (own platform, free membership)
- Region (US/EU preferred — Anti-De Minimis strategy): EU warehouses in **Germany and Poland** (stated by CJ, 2026); exact facility addresses and per-SKU stock coverage still UNVERIFIED
- Products sourced: none yet
- Unit cost: UNVERIFIED — per product, must be pulled before any True Margin Matrix run
- Shipping cost + method (consolidated/postal-cleared?): UNVERIFIED on our EU routes
- Lead time: UNVERIFIED
- MOQ: none stated for dropship fulfilment
- Reliability signals (reviews, response time, sample quality): not yet assessed — order a sample before launch
- Red flags: stocking fees accrue daily while inventory sits; inbound/outbound fees vary by warehouse. These are COGS and must enter the True Margin Matrix, not be treated as overhead.

## Commercial terms (verified 2026-08-30)
- **No subscription, no upfront cost** to create an account, source, or list products.
- Charges are per-fulfilment only: shipping, inbound, outbound, stocking, and optional services (assembly, packaging, disposal).
- Membership "levels" are lifetime-spend based and unlock perks; they are not paid tiers.
- **Verdict**: satisfies the free/OSS cost constraint (AGENTS.md §7).

## EU customs position (verified 2026-08-30) — this is why the EU warehouse matters

The EU's €150 duty exemption ended **1 July 2026**, replaced by a **€3 flat duty per customs item** (items sharing a tariff code group into one charge), running to 1 July 2028. Import VAT applies to every consignment regardless of value.

| Fulfilment route | Duty behaviour | Per-order cost impact |
|---|---|---|
| Direct from China | €3 per customs item **on every order**, plus import VAT and a carrier handling fee (~€2) | Recurring, kills thin margins |
| **CJ EU warehouse (DE/PL)** | Duty paid **once** on the bulk import; local orders cross no border | None per order — the reason to use it |
| CJ tax-inclusive B2C shipping | VAT + duty + clearance bundled into one quote | ~**€1.50–2.00 per parcel** (CJ's own estimate) |

**Decision**: source to the EU warehouse wherever the SKU is stocked there. Direct-from-China is a testing-only fallback, and its €3 + VAT + handling must be entered as `Import duty per unit` in the product file — never omitted.

## MCP/API integration status (verified 2026-08-30)
- CJ MCP server cloned and built at `Q:/cj-mcp-server` from `https://github.com/CJ-dropshipping/api-mcp.git`.
- Project-root MCP config written to `config.yaml`.
- Hermes global MCP config also points to `Q:/cj-mcp-server/dist/mcp-server/index.cjs`; restart Hermes for native tool discovery.
- CJ direct-token HTTP mode works for CJ Number `CJ5775672`.
- Product/catalog API calls now work via the direct-token URL format `MCP@CJ5775672@CJ:<token>`.
- Live cost evidence is recorded in `reports/2026-08-30-cj-mcp-cost-check.md`.

## EU warehouse stock check (2026-08-30)
- `search_products(isWarehouse=true, countryCode=DE/PL/FR)` returned **0 products** for all 3 candidates (folding laundry basket, bamboo drawer organizers, cable management box).
- **No EU warehouse stock** available for any top candidate on CJ.

## Competitor gate (Metapi.io — live 2026-08-30)
- **Folding laundry basket**: 11 ads found, 0 true product ads, 0 >30 days — **FAIL**
- **Bamboo drawer organizers**: 0 ads found — **FAIL**
- **Cable management box**: 14 ads found (cable accessories), 1 >30 days — **MARGINAL** (no true cable box ads)

## Open items before any product clears PROTOCOL-01
1. Find alternative EU supplier with stock (Spocket, Droppery, direct EU manufacturers) since CJ EU warehouse = 0.
2. Confirm lead time from alternative EU supplier to DE/FR/NL.
3. Order a sample and assess build quality against criterion 5 (low return potential).
4. Re-run Metapi competitor check for any new candidates from expanded sweep.
