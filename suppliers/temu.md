# Supplier — Temu Open Platform (API V3.0)

## Supplier
- Name: Temu Open Platform
- Platform: Temu Partner API (programmatic integration)
- Region: **EU endpoint available** — `https://openapi-b-eu.temu.com/openapi/router` (Germany, Italy, France, Spain, UK, etc.)
- Products sourced: Full catalog via API
- Unit cost: API-accessible per SKU
- Shipping cost + method: API-accessible (Temu handles fulfilment)
- Lead time: API-accessible per SKU/warehouse
- MOQ: Dropshipping model — no MOQ
- Reliability signals: Temu's own logistics network; EU warehouse fulfilment confirmed

## STATUS: NOT USABLE — corrected 2026-08-30

**Live probe result**: 0 of 8 V3 product methods are reachable on the EU router.
`temu.local.goods.v3.add` returns **3000027 — "app_key don't have this api permission"**;
the other seven return **3000003 — "type not exists"**.

**Authentication succeeding is not the same as access.** The handshake and MD5
signature validate, which is what the section below records — but the app_key carries
no product-API permission, so no catalog, cost, or fulfilment data can be retrieved.
Every claim below about API-accessible unit cost, shipping and lead time is therefore
**unverified**, and "EU warehouse fulfilment confirmed" is an assertion, not a test
result.

**To unblock**: request V3 product-API permission for this app_key in the Temu partner
console, then re-run `python3 scripts/temu_api.py --probe`.

**Postman**: workspace **Hermes-Ecom** → collection *Hermes-Ecom API Surface* → folder
*Temu EU*. The `goods.v3.add` probe reproduces the 3000027 error; send that response to
Temu support as evidence when requesting permission. Its pre-request script replicates
`generate_signature()` exactly (sorted keys, key+value concatenation, MD5 of
secret+concat+secret, uppercased). Credentials come from the *Hermes-Ecom — credentials*
environment as secret-type variables — never from a file. Until that returns
non-zero reachable methods, Temu cannot be relied on as the EU-warehouse answer to
CJ's freight problem.

## API Integration Status (handshake only — see correction above)
- **API Version**: V3.0 (Live JSON router)
- **Authentication Verified**: Handshake & MD5 signature validated against `https://openapi-b-eu.temu.com/openapi/router`.
- **Payload Format**: `application/json;charset=UTF-8`
- **Automation Client**: `scripts/temu_api.py` (handles timestamping, JSON parameter flattening, MD5 wrapping, and error parsing).
- **App Credentials Configuration**:
  - `TEMUEU_API` (App Key)
  - `TEMUEU_SECRET` (App Secret)
  - `TEMUEU_TOKEN` (Access Token)
- **Endpoints**:
  - **EU: `https://openapi-b-eu.temu.com/openapi/router`** ← **Primary for this project (Jordan Business Location supported)**
  - US: `https://openapi-b-us.temu.com/openapi/router`
  - Global: `https://openapi-b-global.temu.com/openapi/router`

## Postman Integration (from Temu docs)
- **Official Postman Collection**: Temu provides a ready-to-import Postman collection for API testing
- **Import Steps**:
  1. Open Postman → Import → Link / Raw Text / File
  2. Use the collection URL from Temu Partner Platform (after onboarding) or export from their docs
  3. Set environment variables:
     - `base_url`: `https://openapi-b-eu.temu.com/openapi/router`
     - `app_key`: Your Temu app key
     - `app_secret`: Your Temu app secret
     - `access_token`: OAuth token from seller authorization
- **Signature Generation**: Postman pre-request script handles HMAC-SHA256 signing automatically
  - Parameters sorted alphabetically
  - Concatenated as `key=value` pairs
  - Signed with `app_secret`
  - Added as `sign` parameter
## Product Publishing API V3 (`temu.local.goods.v3.add`)
- **Primary Endpoint**: `temu.local.goods.v3.add`
- **Purpose**: Programmatic product publishing & catalog synchronization directly to Temu local/EU storefronts.
- **Payload Capabilities**:
  - Auto-populates Temu catalog database from standardized structured product data.
  - Multi-variant SKU mapping (colors, dimensions, package quantities).
  - Category mapping (`cat_id`), product title (`goods_name`), and rich description (`goods_desc`).
  - Staged product image carousel ingestion (`carousel_image_list` from local ComfyUI/IC-Light renders).
  - Local EU warehouse inventory allocation and localized EUR pricing.

## Key Capabilities (from V3 docs)
- **Product Management**: `temu.local.goods.v3.add` (publish), SKU updates, inventory and price synchronization.
- **Order Management**: `bg.order.list.get`, `bg.order.detail.get` (sync orders, tracking, fulfillment status).
- **Logistics**: EU warehouse fulfillment and tracking integration.
- **Real-time Webhooks**: Inventory threshold triggers, price update confirmations, and buyer orders.
- **DSA Compliance**: Automatic EU ad repository and trader transparency compliance.

## Commercial Terms
- No upfront subscription mentioned in public docs
- Revenue share / commission model (exact rates require partner onboarding)
- Per-order fulfilment fees (shipping, handling) — must enter as COGS in True Margin Matrix
- **Critical**: Verify commission rate + fulfilment fees per SKU before margin calculation

## EU Customs Position (Anti-De Minimis Strategy)
| Fulfilment Route | Duty Behaviour | Per-Order Cost Impact |
|---|---|---|
| Temu EU warehouse (via EU endpoint) | Duty paid once on bulk import; local orders cross no border | **None per order** — aligns with CJ EU warehouse strategy |
| Temu direct-from-China (if any SKU not in EU) | €3 per customs item + import VAT + carrier handling | Recurring, kills thin margins |

**Decision**: Use **EU endpoint + EU warehouse SKUs only**. Any SKU not stocked in EU warehouse is a hard reject for this project.

## Open Items Before Temu Clears PROTOCOL-01
1. **Partner onboarding** — Apply for Temu Partner Platform (EU) access: https://partner-eu.temu.com/
2. **Commission + fee schedule** — Obtain exact per-category commission rates and EU fulfilment fees
3. **EU warehouse coverage check** — Use Product Search API (`goods.search` or equivalent) with `warehouse_type=EU` filter for our 4 candidate products
4. **Sample order** — Assess build quality against Criterion 5 (low return potential)
5. **Competitor gate** — Temu itself is a marketplace; competitor check via Meta Ad Library remains the same (search product keywords, not "Temu")

## Integration Notes for Hermes-Ecom
- **MCP Server**: No public Temu MCP yet. Would need custom wrapper around REST API.
- **Direct HTTP**: Straightforward — POST with HMAC sig. Python example in docs.
- **Firecrawl**: Could scrape Temu product pages for competitive pricing, but API is preferred.
- **Agent-Reach**: Zero-config channels (YouTube, web) can monitor Temu trends; no login channels.

## Documentation Reference
- **Primary**: https://partner.temu.com/documentation?menu_code=38e79b35d2cb463d85619c1c786dd303&sub_menu_code=8311de2b2d434e4d805e88413ab815d8
- **API Reference**: https://partner.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a
- **Partner Platform EU**: https://partner-eu.temu.com/