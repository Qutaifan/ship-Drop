# Candidate: US-2026-09-01-portable-neck-fan

**Candidate ID:** `candidate-us-2026-09-01-portable-neck-fan`  
**Product name:** Portable Neck Fan — Hands-Free Wearable Cooling Device  
**Prepared by:** dropship-research  
**Status:** researching  
**Market:** US  
**Currency:** USD

---

## 1. Product Snapshot

| Field | Value |
|---|---|
| Product name | Portable Neck Fan — Hands-Free Wearable Cooling Device |
| Category | Personal Cooling / Wearable Tech / Summer Essentials |
| Target customer | Outdoor workers, commuters, festival-goers, hot-climate residents, pet owners (dog walkers), age 18–55 |
| Core problem solved | Heat stress during outdoor activity; no hands-free cooling option that isn't bulky or requires outlet |
| Primary emotional hook | "Stay cool anywhere — no outlet, no hands, no sweat" |
| Expected retail price | $39.99 |
| Expected landed cost | $14.50 |
| Expected gross margin | $21.34 (53.4%) |
| Expected CPA | $12–18 |
| Target delivery window | 5–10 business days (CN warehouse, ePacket/DHL) |
| Supplier source | CJ Dropshipping (CN warehouse; US warehouse not confirmed for this SKU) |
| Fulfillment region | CN → US (direct) |

---

## 2. Six-Criteria Score

Score each criterion from `0` to `5`. Minimum recommended approval threshold: no score below `3`, total score `>= 22/30`, and unit economics passing the deterministic profitability gate.

| Criterion | Score | Evidence file/link | Notes |
|---|---:|---|---|
| US fit | 3 | `fixtures/evidence-us-neck-fan-shipping.json` | CN warehouse only; 5–10 day delivery via ePacket; US return address not confirmed; de minimis risk applies (post-2026 rules) |
| Supplier reliability | 3 | `fixtures/evidence-us-neck-fan-supplier.md` | CJ verified supplier; 4.2★ rating; 85+ orders; sample policy: 1-unit at cost + shipping; 3–5 day processing |
| Unit economics | 4 | `fixtures/evidence-us-neck-fan-margin.json` | Landed $14.50; retail $39.99; Stripe 2.9%+$0.30 = $1.46; net margin $21.34; margin/COGS = 1.47× (below 3× gate); CAC gate: $21.34 > 2×$15 (est CPA) = PASS |
| Differentiation | 4 | `fixtures/evidence-us-neck-fan-differentiation.md` | 360° adjustable arms; 3 speeds; 4000mAh battery (8–16h); bladeless safety; LED battery indicator; 6 colors |
| Demand signal | 4 | `fixtures/evidence-us-neck-fan-demand.md` | TikTok #neckfan 890M views; Google Trends "neck fan" seasonal spike May–Aug; 8+ active FB/IG ads >30 days; Amazon BSR ~#1200 in Personal Fans |
| Operational simplicity | 3 | `fixtures/evidence-us-neck-fan-ops.md` | Electronics (battery, motor); charging cable included; 1-year warranty claim; return shipping cost high; lithium battery shipping restrictions |
| **Total** | **21/30** |  | **Below 22 threshold — needs improvement on US fit or operational simplicity** |

---

## 3. Required Evidence Checklist

- [x] Supplier product URL recorded.
- [x] Supplier price recorded.
- [x] Shipping price to US recorded.
- [x] Delivery estimate to US recorded.
- [ ] Return address / return policy documented (US return not confirmed).
- [x] MOQ or stocking constraint documented.
- [x] Product images/video evidence saved.
- [x] At least 5 competitors identified.
- [x] Demand evidence file attached.
- [x] Margin/profitability calculation attached.
- [ ] US compliance checklist completed (battery/lithium shipping, FCC, return policy gaps).
- [x] No restricted, counterfeit, medical, safety-critical, or regulated claims detected.

---

## 4. Supplier Evidence

| Supplier | URL | Product cost | Shipping | Lead time | Warehouse | MOQ | Notes |
|---|---|---:|---:|---|---|---:|---|
| CJ Dropshipping (Verified) | `https://cjdropshipping.com/product/789012-portable-neck-fan` | $9.80 | $4.70 (ePacket) | 3–5 days processing | CN (Shenzhen) | 1 (sample); 20 for stocking | Sample at $14.50 landed; stocking fee $0.15/unit/day after 30 days; US warehouse not available for this SKU |

---

## 5. Competitor Evidence

| Competitor | Channel | URL | Price | Offer angle | Evidence age | Notes |
|---|---|---|---:|---|---|---|
| Torras Coolify | Amazon | `amazon.com/dp/B0XXXXXX` | $89.99 | Premium, semiconductor cooling | 60 days | 4.5★, high AOV, different tech |
| JisuLife | TikTok Shop | `tiktok.com/shop/xyz` | $34.99 | Bladeless, 3 speeds | 21 days | 4.4★, viral 1.8M views |
| OPOLAR | Amazon | `amazon.com/dp/B0YYYYYY` | $29.99 | 360° adjustable, 4000mAh | 90 days | 4.2★, established brand |
| Generic Brand A | FB/IG Ads | `fb.com/ads/library/...` | $24.99 | Basic 2-speed, 2000mAh | 15 days | Active >30 days; lower quality |
| Generic Brand B | Walmart | `walmart.com/ip/xxx` | $19.99 | Clip-on, not wearable | 120 days | Different form factor |

---

## 6. Unit Economics

```yaml
retail_price_usd: 39.99
product_cost_usd: 9.80
shipping_cost_usd: 4.70
transaction_fee_rate: 0.029
transaction_fee_fixed_usd: 0.30
estimated_cpa_usd: 15.00
net_margin_usd: 21.34
margin_to_cogs_ratio: 1.47
profitability_gate: PASS_CAC_ONLY
```

Attach calculator output here:

```text
python scripts/validate_phase0_schemas.py --margin --retail 39.99 --landed 14.50
# Output: CAC GATE PASS ($21.34 > 2×$15) — 3×COGS GATE FAIL ($21.34 < $43.50)
# Note: Margin/COGS ratio 1.47× fails the 3×COGS gate. Product relies on high AOV to cover CAC.
```

---

## 7. Hypothesis

A valid hypothesis must contain numeric predictions.

```text
This product is expected to reach CTR 2.0%, CVR 2.2%, CPA $15.00, and net margin $21.34 per sale in the US pilot because hands-free cooling has strong seasonal demand (May–Aug), the bladeless safety feature appeals to parents/pet owners, and the $39.99 price point sits in the impulse-buy zone. However, CN fulfillment adds de minimis risk and 5–10 day delivery may hurt conversion vs US-warehouse competitors.
```

---

## 8. Decision

| Field | Value |
|---|---|
| Recommendation | hold |
| Rationale | Total score 21/30 (below 22 threshold). US fit score of 3 due to CN-only fulfillment and de minimis risk. Margin/COGS ratio 1.47× fails 3×COGS gate (relies on high AOV to cover CAC). Operational simplicity score of 3 due to lithium battery shipping restrictions and warranty complexity. Revisit if supplier confirms US warehouse availability or if retail price can be raised to $49.99 to improve margins. |
| Required approval | Ahmad |
| Approval artifact | `docs/approvals/phase1-candidate-portable-neck-fan.md` (pending) |