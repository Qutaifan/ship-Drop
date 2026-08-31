# US Market - Supply Chain & Fulfilment

## The De Minimis Problem (US)
- **Before Aug 2025**: $800 de minimis → ship direct from China, no duty
- **After Aug 2025 (Executive Order 2025)**: $800 de minimis RESTRICTED for China-origin goods
- **Reality**: Every direct shipment from China now incurs Section 301 duty + MPF + HMMPF
- **Conclusion**: US 3PL (bulk import → domestic fulfillment) is mandatory for China-origin products

## Recommended US 3PL Providers (Free/Cheap)

### Tier 1: Pay-Per-Use (Best for New Product Testing)
| Provider | Min Cost | Free Tier | Notes |
|---|---|---|---|
| **ShipBob** | $0 setup | 30-day free storage | 2-day shipping, US-wide |
| **ShipMonk** | $0 setup | First month free | 2-day shipping, integrations |
| **Amazon FBA Small & Light** | $0 setup | — | For products <$15, <12oz |
| **Deliverr (Flexport)** | $0 setup | — | 2-day by default, no minimums |
| **eBay Fulfilled by eBay** | $0 setup | 30 days free storage | eBay-only, free listing |

### Tier 2: Bulk Storage (Best for Scaling)
| Provider | Cost | Notes |
|---|---|---|
| **Flexport** | Per CBM | Container freight + warehousing |
| **ShipHero** | $499/mo + per-unit | Self-serve |
| **Ruby Has** | Custom quote | Enterprise |

### Tier 3: Marketplace Native
- **Amazon FBA** (if selling on Amazon): Massive fulfillment network, $0 setup
- **Walmart Fulfilled Services** (FWS): Growing, US-only
- **Shopify Fulfillment Network**: Newer, integrated with Shopify
- **TikTok Shop US**: Built-in fulfillment, US-only

## Bulk Import Logistics

### Process
1. **Source product from CJdropshipping / Alibaba** (free, per-fulfilment)
2. **Negotiate FOB China pricing** (vs. landed)
3. **Container or LCL freight** to US 3PL warehouse
4. **Customs clearance**: Section 301 duty paid on entire shipment
5. **3PL receives** inventory, stores, ships per-order

### Freight Forwarders (China → US)
- **Flexport**: Best digital experience, transparent pricing
- **Freightos**: Marketplace, instant quotes
- **Easyship**: Built for SMB e-com
- **China freight forwarder via CJ**: CJdropshipping has freight service for bulk

### Costs to Budget
- **Product cost**: $X per unit (FOB China)
- **International freight**: $1-3 per unit (LCL, varies by volume)
- **Section 301 duty**: 7.5-25% on product cost (depends on HTS)
- **MPF**: 0.3464% of value, min $31.67, max $614.35 per entry
- **Customs broker**: $50-200 per entry (or use freight forwarder)
- **3PL inbound receiving**: $25-100 per pallet
- **3PL storage**: $0.10-0.50 per cubic foot per month
- **3PL pick+pack**: $2-5 per order
- **US outbound shipping**: $4-7 standard, $8-12 expedited

**Total landed cost per unit** (example, 1000 units):
- Product: $8.00
- Freight: $1.50
- Duty (25%): $2.00
- 3PL storage (1 month): $0.50
- 3PL pick+pack: $3.50
- US shipping: $5.00
- **Total**: **$20.50 per order**

This is the COGS number that goes into the US True Margin Matrix.

## HTS Code Lookup (Critical for Duty)

Section 301 tariff rates depend on HTS code. Common categories:

| Category | Typical HTS | Section 301 Rate |
|---|---|---|
| Plastic household goods | 3924.10 | 25% List 4A |
| Steel articles | 7326.20 | 25% List 3 |
| Aluminum articles | 7615.10 | 10% (decreased from 25%) |
| Wood furniture | 9403.30 | 25% List 4A |
| Textiles/apparel | 6100-6200 | Often 7.5-25% |
| Electronics | 8500-8504 | Often 0% or 25% |
| Toys | 9503 | 0% or 7.5% |
| Kitchen gadgets | 3924.10 | 25% |

**Look up actual HTS**: https://hts.usitc.gov (free, official)

## Inventory Strategy (US)

### Per-Product Thresholds
- **Min launch order**: 100-300 units (test inventory)
- **Reorder point**: 2-3 weeks of sales velocity remaining
- **Safety stock**: 1-2 weeks (longer for slow-movers)
- **Max single shipment**: 3-6 months velocity (avoid storage fees)

### Lead Time
- **China → US freight**: 14-30 days (sea), 3-5 days (air premium)
- **3PL receive + check-in**: 1-3 days
- **Per-order fulfillment**: 1-2 days

**Total**: ~4-6 weeks from "place order" to "customer receives" for the FIRST order. Subsequent orders: 2-3 days.

## US 3PL Integration

### API-First Providers
- **ShipBob**: REST API, Shopify/WooCommerce plugins
- **ShipMonk**: API + plugins
- **Amazon FBA**: Send to Amazon (no per-order API)
- **Deliverr**: API + Shopify plugin

### Order Flow (Automated)
1. Customer orders on storefront
2. Order pushed to 3PL (API or plugin)
3. 3PL picks, packs, ships
4. Tracking number returned to customer
5. Inventory decremented automatically

### Free Inventory Sync
- **Shopify** + ShipBob plugin: Free
- **Medusa** + custom webhook: ~$0 to set up
- **WooCommerce** + ShipStation: Free tier
- **Amazon FBA**: Inventory pushes one-way to FBA

## Cost Comparison: US 3PL vs Direct-from-China

### Direct from China (NO LONGER VIABLE)
- Product: $8.00
- Shipping: $3.10
- Duty: 25% = $2.00
- MPF per shipment: ~$31.67 / 100 units = $0.32 per unit
- HMMPF (Section 301): Often 25% additional = $2.00
- **Total**: ~$15.42 per order
- Lead time: 7-21 days
- Customer experience: Poor
- **Verdict**: Dead strategy post-2025

### US 3PL Bulk Import
- Product: $8.00
- Freight amortized: $1.50
- Duty (paid once on bulk): $0.00 per order (amortized)
- 3PL pick+pack: $3.50
- US shipping: $5.00
- **Total**: ~$18.00 per order
- Lead time: 2-3 days
- Customer experience: Excellent
- **Verdict**: The only viable US strategy

## Anti-Patterns to Avoid

- ❌ **Assumes de minimis still works** — Section 321 is restricted for China goods
- ❌ **Direct ship from China to US customer** — every order incurs full duty stack
- ❌ **Single 3PL** with no backup — holidays, capacity issues
- ❌ **No inventory buffer** — stockout = 7-21 day refill, lost sales
- ❌ **Failing to register in nexus states** — back liability
- ❌ **Paying retail rates for freight** — use freight forwarders + LCL
- ❌ **Ignoring HTS classification** — mis-classification = penalty

## Quick Start (US Market)

1. **Pick 3PL**: ShipBob (free to start) or Amazon FBA (if also selling on Amazon)
2. **Source product**: CJdropshipping (existing supplier, free)
3. **Order first batch**: 100-300 units, air freight for speed
4. **Customs broker**: Use CJ's freight service or Flexport
5. **Configure storefront**: US pricing, sales tax, 30-day return policy
6. **Set up CAPI**: Facebook + TikTok Conversions API for attribution
7. **Launch test campaign**: $500-1000, US targeting
8. **Monitor & restock**: Daily sales check, reorder at 2 weeks remaining
