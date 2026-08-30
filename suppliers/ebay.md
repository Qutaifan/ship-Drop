# Channel & Market Intelligence — eBay Developers REST API

## 1. Overview
- **Name**: eBay Developers Program (REST API)
- **Role in Hermes-Ecom**:
  1. **Market Intelligence & Price Discovery (OBSERVE)**: Query active market pricing, sold listings, and shipping origins across EU marketplaces (eBay Germany `EBAY_DE`, eBay France `EBAY_FR`, eBay UK `EBAY_GB`).
  2. **Multi-Channel Storefront & Fulfillment (ACT)**: Automated listing via Inventory API (`sell/inventory/v1`) with local EU warehouse fulfillment (CJdropshipping / EU wholesale).
- **Free Tier Limits**: Up to **25,000 to 1,500,000 API calls/day** at **€0 cost**.

---

## 2. Dropshipping Policy Compliance (2026 Rules)
- **PERMITTED (Wholesale Dropshipping)**: Fulfilling orders directly from wholesale suppliers/warehouses (CJdropshipping EU warehouse, verified manufacturers).
- **STRICTLY PROHIBITED (Retail Arbitrage)**: Purchasing items from retail marketplaces (Amazon, Walmart, AliExpress consumer checkout) to ship directly to eBay customers.
- **Accurate Item Location**: Listings must declare exact item location (e.g. Frankfurt / Warsaw warehouse), matching actual carrier tracking origins (DHL / Hermes).

---

## 3. EU Regulatory & Tax Handling
- **VAT & IOSS**: eBay operates as a Deemed Reseller / Marketplace Facilitator in the EU. For cross-border consignments under €150, eBay automatically collects and remits destination VAT under its own IOSS number.
- **EU Warehouse Dispatch**: Domestic EU orders (e.g. DE warehouse to DE customer) carry zero import duty and use standard domestic carrier labels.
- **GPSR Compliance (General Product Safety Regulation)**: Listings include manufacturer/importer contacts and safety warnings via the `sell/inventory/v1/inventory_item` API.

---

## 4. API Architecture & Authentication

### A. Authentication Flows (OAuth 2.0)
- **Application Token (Client Credentials Grant)**:
  - Used for **Browse API / Market Research** (read-only catalog data, no user login required).
  - Endpoint: `https://api.ebay.com/identity/v1/oauth2/token`
  - Headers: `Authorization: Basic <base64(AppID:CertID)>`
  - Body: `grant_type=client_credentials&scope=https://api.ebay.com/oauth/api_scope`

- **User Token (Authorization Code Grant)**:
  - Used for **Inventory & Fulfillment APIs** (listing products, syncing orders).

### B. Key Endpoints

| API | Base URL / Path | Purpose |
|---|---|---|
| **Browse API** | `/buy/browse/v1/item_summary/search` | Query competitor pricing, item location, and shipping terms |
| **Inventory API** | `/sell/inventory/v1/inventory_item/{sku}` | Create/update product listings, inventory levels, and prices |
| **Offer API** | `/sell/inventory/v1/offer` | Publish inventory items to specific eBay marketplaces (`EBAY_DE`, `EBAY_GB`) |
| **Fulfillment API** | `/sell/fulfillment/v1/order` | Retrieve orders and post carrier tracking numbers |

---

## 5. Implementation in Hermes-Ecom

- **Tooling**: `scripts/ebay_api.py` (queries live market pricing, filters by EU warehouse locations, and calculates competitive price floors).
- **Environment Variables**:
  - `EBAY_CLIENT_ID` (App ID)
  - `EBAY_CLIENT_SECRET` (Cert ID)
  - `EBAY_MARKETPLACE` (Defaults to `EBAY_DE`)
