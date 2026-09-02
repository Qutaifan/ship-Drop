# US Market Configuration

## Market Context
- **Currency**: USD
- **De Minimis**: $800 exemption RESTRICTED (Executive Order 2025; CBP enforcement per Section 321)
- **Duty**: Full duty applies to every direct-to-consumer shipment from China
- **Sales Tax**: State-by-state nexus (Economic + Physical); destination-based sourcing since 2018 (Wayfair)
- **VAT Equivalent**: N/A (no federal VAT; state sales tax only)
- **Payment Processing**: Stripe US, 2.9% + $0.30 per transaction
- **Shipping**: 2-5 day standard domestic, 1-2 day Priority Mail

## Pricing Band (USD)
- **Target retail**: $68 - $105 (mirrors EUR 62-93 target band)
- **CAC benchmark**: ~$23.50 (slightly higher than EU's EUR 21.48 due to higher CPMs on Meta/TikTok US)
- **Net margin floor**: $20 per sale, 3x COGS minimum
- **Payment fee**: 2.9% + $0.30 on gross (NOT divided by sales tax)

## True Margin Matrix (US)
```python
# Sales tax is REMITTED, never earned. Same principle as EU VAT.
# Retail = USD gross (sales tax-inclusive at checkout)
# Net = (Retail - Sales_Tax) - (Product_Cost + Shipping + Duty + 0.029*Retail + $0.30) - Platform_Fee
```

**Worked example**: $85.00 retail, 7% state sales tax, $12 COGS, $4.50 shipping, 25% duty on $12 = $3.00, 2.9% + $0.30 payment.
- Net = ($85 / 1.07) - ($12 + $4.50 + $3.00) - ($2.465 + $0.30) = $79.44 - $19.50 - $2.77 = **$57.18** ✅ PASS

## US-Specific Validation Gates

### Sales Tax Compliance
- **Nexus Threshold**: Varies by state (CA: $500K sales; TX: $500K; NY: $500K + 100 transactions; FL: $100K; most others: $100K or 200 transactions)
- **Marketplace Facilitator Laws**: Most platforms (Amazon, eBay, Etsy) collect/remit tax automatically
- **Direct e-commerce**: YOU must collect/remit where you have nexus
- **Tool**: TaxJar or Avalara (paid) — free alternative: register in highest-volume states manually + spreadsheet

### Duty & Customs (US)
- **Section 321 de Minimis**: SUSPENDED for China-origin goods per Executive Order 2025
- **Duty rates**: HTS chapter rates; consumer goods typically 0-25% (apparel high, electronics often 0%)
- **MPF (Merchandise Processing Fee)**: 0.3464% of value, min $31.67, max $614.35 per entry
- **HMMPF (China-specific)**: Additional 25% on Section 301 list products
- **Strategy**: Bulk import to US 3PL → per-order duty paid ONCE on the bulk import

### US 3PL (Third-Party Logistics) — REQUIRED
- **Why**: Pay duty once on bulk import, store domestically, ship per-order with NO additional duty
- **Free/cheap options**:
  - Amazon FBA (Small & Light: $0.30/unit fulfillment)
  - ShipBob (pay-as-you-go: ~$5 pick+pack + shipping)
  - ShipMonk ($0 onboarding, pay-per-use)
  - Deliverr (now part of Flexport) — 2-day shipping
  - eBay Fulfilled by eBay — free storage 30 days
- **COGS impact**: US 3PL adds ~$3-7 per order vs. direct China → must be in margin math

### Sales Tax Registrations
- **First states to register**: CA, TX, NY, FL, IL (cover ~40% of US e-commerce)
- **Free filing**: Many states have free sales tax filing portals
- **Streamlined Sales Tax (SST)**: Single registration covers 24 states — FREE

## Ad Library Validation (US-SPECIFIC)
**CRITICAL**: Per AGENTS.md, the Meta Ad Library API **does not return commercial US ads**. The DSA ad-repository rules that compel EU/UK data do not apply to the US. The ad_type=ALL endpoint returns political/social-issue ads only for US.

**Therefore: PROTOCOL-01 competitor gates for US must be counted BY HAND** in the Meta Ad Library web UI.

**Manual procedure** (record findings in `reports/YYYY-MM-DD-us-ad-library-manual-<product>.md`):
1. Open facebook.com/ads/library
2. Country: United States
3. Category: All ads
4. Search: exact product name + key feature words
5. Filter: Active ads
6. Count: distinct page names running ads
7. For each: capture first-seen date, last-seen date, ad count, page likes
8. Require 5-10 distinct competitors, 3+ with 30+ days active

**TikTok Creative Center**: US ads ARE visible at ads.tiktok.com/business/creativecenter — count there in parallel.

## Pricing Display (FTC)
- **FTC Act Section 5**: Total price (incl. shipping + mandatory fees) must be shown before checkout
- **"Free shipping" claims**: Must be truthful; cannot be offset by inflated product price
- **Sale price references**: Must show original price, must have actually sold at that price recently
- **Comparison pricing**: Must have substantial sales at the comparison price

## Compliance Risks
- **CPSIA**: Children's products require tracking labels + safety testing
- **FCC**: Electronic products need FCC certification (RF emitters)
- **Proposition 65 (CA)**: Cancer/reproductive harm warnings required for specific chemicals
- **State-specific**: CT, NJ, NY have additional consumer protection rules
- **FTC Endorsement Guides**: #ad disclosures on all influencer/UGC content
- **CAN-SPAM Act**: Unsolicited emails with working opt-out
- **TCPA**: Text message marketing requires prior express written consent

## Currency & Payment
- **Multi-currency**: Stripe handles USD primary; auto-conversion adds 1% fee
- **Display**: Show prices in USD for US visitors
- **Refunds**: Process in original payment currency within state-mandated timelines

## Customer Service Hours
- **Time zones**: Eastern + Pacific = cover 95% of population
- **Response SLA**: 24h email, 4h chat (industry standard)
- **Returns**: 30 days standard, free returns required by many states (CA, NJ for online)

## Shipping Carriers (US)
- **USPS**: First Class <1lb, Priority Mail 1-3 days, free pickup
- **UPS**: Ground 1-5 days, Next Day Air premium
- **FedEx**: Home Delivery (residential), Ground Commercial
- **Discount rates**: Stamps.com ($19.99/mo) for USPS commercial pricing, free ShipStation tier
