# Financial, Tax & Shipping Analysis — Phase 3-5 Readiness

**Project:** dropship  
**Market:** US pilot  
**Date:** 2026-09-01  
**Status:** **GAPS IDENTIFIED — NEEDS WORK BEFORE PHASE 5**

---

## Executive Summary

The current `margin_solver_us.py` covers **basic unit economics only**. Critical gaps exist for production-ready financial processes:

| Area | Current State | Production Gap |
|---:|---|---:|
| **Unit economics** | ✅ Basic margin matrix (retail, cost, shipping, duty, 3PL, Stripe) | Single-state tax only |
| **Sales tax** | ⚠️ Single `state_tax` parameter | No nexus detection, no multi-state, no marketplace facilitator rules |
| **De minimis / duty** | ⚠️ `duty` parameter (manual) | No automated Section 301, 232, or de minimis logic (post-July 2026 rules) |
| **Shipping** | ⚠️ Manual `shipping` parameter | New `logistics_coordinator.py` created but uses estimated rates, not live APIs |
| **CAC gate** | ✅ 2× median CPA benchmark | CAC benchmark hardcoded, not channel-specific |
| **Payment fees** | ✅ Stripe 2.9% + $0.30 | No PayPal, Shopify Payments, or international card fees |
| **Returns/refunds** | ❌ Not modeled | No return rate, restocking, reverse logistics cost |
| **3PL fees** | ⚠️ Single `threepl_fee` | No storage, receiving, kitting, or long-term storage fees |

---

## Logistics Coordinator — Test Results

Created `scripts/logistics_coordinator.py` — compares USPS, UPS, FedEx, SurePost, SmartPost across zones.

### Magnetic Cable Organizer ($24.99 retail, $6.80 landed, 0.5 lb, Zone 6)

| Carrier | Service | Cost | Transit | Net Margin | CAC Gate | COGS Gate |
|---|---|---:|---:|---:|---|---|
| **USPS** | **First Class** | **$9.00** | 8 days | **$6.53** | FAIL | FAIL |
| USPS | Priority Mail | $16.45 | 4 days | -$0.92 | FAIL | FAIL |
| FedEx | Ground | $18.77 | 7 days | -$3.24 | FAIL | FAIL |
| UPS | Ground | $19.90 | 7 days | -$4.37 | FAIL | FAIL |

**Result:** No option passes CAC gate ($6.53 < $20 target) or 3×COGS gate ($6.53 < $20.40).

### Foldable Silicone Bowl ($29.99 retail, $9.20 landed, 1.5 lb, Zone 2)

| Carrier | Service | Cost | Transit | Net Margin | CAC Gate | COGS Gate |
|---|---|---:|---:|---:|---|---|
| **FedEx SmartPost** | **Economy** | **$7.70** | 4 days | **$9.96** | FAIL | FAIL |
| **UPS SurePost** | **Economy** | **$8.30** | 4 days | **$9.36** | FAIL | FAIL |
| USPS | Priority Mail | $11.65 | 2 days | $6.01 | FAIL | FAIL |

**Result:** No option passes CAC gate ($9.96 < $24 target) or 3×COGS gate ($9.96 < $27.60).

### Key Insight

**Both top candidates fail CAC and 3×COGS gates with realistic shipping costs.** The original candidate files used optimistic shipping estimates ($2.30–$2.70 domestic) vs. actual carrier rates ($7.70–$9.00+).

---

## Required Fixes Before Phase 5

### 1. Candidate Re-pricing or Cost Reduction

| Candidate | Current Retail | Required Retail (est.) | Or Cost Reduction |
|---|---:|---:|---:|
| Magnetic Cable Organizer | $24.99 | ~$35–40 | Product cost < $4.00 |
| Foldable Silicone Bowl | $29.99 | ~$40–45 | Product cost < $5.50 |

### 2. US Sales Tax Engine (Multi-State Nexus)

Need to implement:
- **Nexus detection** — economic nexus thresholds by state ($100k revenue / 200 transactions typical)
- **Marketplace facilitator rules** — if selling via TikTok Shop/Amazon, they collect
- **Destination-based sourcing** — tax rate by customer ZIP+4
- **TaxJar / Avalara API** or open-source `python-taxjar` integration
- **Filing calendar** — monthly/quarterly/annual by state

### 3. De Minimis & Duty Automation (Post-July 2026)

Current rules (as of July 2026):
- **De minimis eliminated for China/HK** — Section 301 duties apply regardless of value
- **$800 de minimis restricted** — CN-origin goods lose exemption
- **Section 301 tariffs** — 7.5%–25% on many categories
- **Section 232** — steel/aluminum 25%
- **MPF/HMF** — Merchandise Processing Fee + Harbor Maintenance Fee

Need:
- **HTS code lookup** per product
- **Automated duty calculation** = (product_cost + shipping) × duty_rate + MPF
- **Bulk duty payment at 3PL** vs. per-unit (duty = 0 if paid in bulk at 3PL)

### 4. Live Shipping Rate Integration

Replace estimated rates in `logistics_coordinator.py` with:
- **EasyPost API** — multi-carrier, discounted rates, label printing
- **Shippo API** — alternative multi-carrier
- **Direct carrier APIs** — UPS/FedEx/USPS (requires account)
- **Zone-based caching** — cache rates by origin_zip/dest_zip/weight/dimensions

### 5. Returns & Reverse Logistics Model

Add to margin matrix:
```python
return_rate = 0.08  # 8% typical for non-apparel
return_shipping = avg_return_shipping_cost
restocking_fee = 0.15 * product_cost  # or fixed
refund_processing = 0.50  # payment processor refund fee
net_margin_adjusted = net_margin - (return_rate * (return_shipping + restocking_fee + refund_processing))
```

### 6. Complete Financial Process Flow

```
Order Received
    ↓
Payment Captured (Stripe/PayPal) → Fee deducted
    ↓
Sales Tax Calculated (by nexus + destination) → Remitted to state
    ↓
Order Routed to 3PL / CJ US Warehouse
    ↓
Pick + Pack Fee Charged
    ↓
Shipping Label Purchased (live rate) → Carrier picks up
    ↓
Duty/MPF Paid (if not pre-paid in bulk at 3PL)
    ↓
Delivered → Customer
    ↓
[Return Window Opens]
    ↓
Return Initiated → Return Label → 3PL Receives → Inspect → Restock/Disposal
    ↓
Refund Issued → Payment Fee Refunded (partial) → Tax Adjustment Filed
```

---

## Action Items for Phase 3-5

| Priority | Task | Owner | Tool/Integration |
|---:|---|---|---|
| **P0** | Re-price candidates or renegotiate supplier cost | Ahmad | Supplier negotiation |
| **P0** | Integrate live shipping rates (EasyPost) | Dev | `logistics_coordinator.py` + EasyPost API |
| **P1** | Build multi-state sales tax engine | Dev | TaxJar/Avalara API or `python-taxjar` |
| **P1** | Automate duty/de minimis per HTS code | Dev | USITC HTS API + CJ product data |
| **P2** | Model returns/refunds in margin matrix | Dev | Extend `margin_solver_us.py` |
| **P2** | Add 3PL fee schedule (storage, receiving, long-term) | Ops | 3PL contract |
| **P3** | Payment fee matrix (Stripe, PayPal, Shopify Pay, international) | Dev | Extend margin solver |

---

## Current Candidate Viability (with Real Shipping)

| Candidate | Viable at Current Price? | Action Required |
|---|---:|---|
| Magnetic Cable Organizer | ❌ No | Raise to $35+ or reduce cost to <$4 |
| Foldable Silicone Bowl | ❌ No | Raise to $40+ or reduce cost to <$5.50 |
| Magnetic Wristband | ❌ No (CN fulfillment) | Need US warehouse |
| Portable Neck Fan | ❌ No (CN + battery) | Need US warehouse + re-price |

---

## Next Steps

1. **Discuss re-pricing with Ahmad** — candidates need higher retail or lower cost
2. **Integrate EasyPost** for live shipping quotes in `logistics_coordinator.py`
3. **Build tax nexus detector** before Phase 3 storefront launch
4. **Validate HTS codes** for both candidates with CJ supplier

The logistics coordinator is ready at `scripts/logistics_coordinator.py` — it just needs live API keys and updated candidate economics.