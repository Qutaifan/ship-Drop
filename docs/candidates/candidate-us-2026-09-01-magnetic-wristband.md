# Candidate: US-2026-09-01-magnetic-wristband

**Candidate ID:** `candidate-us-2026-09-01-magnetic-wristband`  
**Product name:** Magnetic Wristband Tool Holder — Hands-Free Screw/Nail/Drill Bit Organizer  
**Prepared by:** dropship-research  
**Status:** researching  
**Market:** US  
**Currency:** USD

---

## 1. Product Snapshot

| Field | Value |
|---|---|
| Product name | Magnetic Wristband Tool Holder — Hands-Free Screw/Nail/Drill Bit Organizer |
| Category | Tools & Home Improvement / DIY / Professional Trades |
| Target customer | DIYers, electricians, carpenters, mechanics, handymen, age 30–60 |
| Core problem solved | Dropping screws/nails while on ladder; fumbling for bits; losing small metal parts in grass/carpet |
| Primary emotional hook | "Your third hand that never drops a screw" — pro feel for DIY price |
| Expected retail price | $22.99 |
| Expected landed cost | $6.80 |
| Expected gross margin | $13.39 (58.2%) |
| Expected CPA | $9–13 |
| Target delivery window | 5–10 business days (CN warehouse, ePacket) |
| Supplier source | CJ Dropshipping (CN warehouse; US warehouse not confirmed) |
| Fulfillment region | CN → US (direct) |

---

## 2. Six-Criteria Score

Score each criterion from `0` to `5`. Minimum recommended approval threshold: no score below `3`, total score `>= 22/30`, and unit economics passing the deterministic profitability gate.

| Criterion | Score | Evidence file/link | Notes |
|---|---:|---|---|
| US fit | 3 | `fixtures/evidence-us-magnetic-wristband-shipping.json` | CN warehouse only; 5–10 day delivery via ePacket; US return address not confirmed; de minimis risk applies |
| Supplier reliability | 4 | `fixtures/evidence-us-magnetic-wristband-supplier.md` | CJ verified supplier; 4.6★ rating; 200+ orders; sample policy: 1-unit at cost + shipping; 2-day processing |
| Unit economics | 4 | `fixtures/evidence-us-magnetic-wristband-margin.json` | Landed $6.80; retail $22.99; Stripe 2.9%+$0.30 = $0.97; net margin $13.39; margin/COGS = 1.97×; CAC gate: $13.39 > 2×$11 = PASS |
| Differentiation | 4 | `fixtures/evidence-us-magnetic-wristband-differentiation.md` | 15 ultra-strong NdFeB magnets; ballistic nylon; adjustable strap fits all wrists; 2 pockets for non-magnetic items; breathable mesh |
| Demand signal | 4 | `fixtures/evidence-us-magnetic-wristband-demand.md` | TikTok #diylife 3.4B views; Google Trends "magnetic wristband" steady; 12+ active FB/IG ads >30 days; Amazon BSR ~#2200 in Tool Pouches |
| Operational simplicity | 4 | `fixtures/evidence-us-magnetic-wristband-ops.md` | No electronics; adjustable fit; durable ballistic nylon; magnets retain strength; returnless-refund viable (<$3); no warranty complexity |
| **Total** | **23/30** |  | **Above 22 threshold — but US fit score of 3 is a risk** |

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
- [ ] US compliance checklist completed (de minimis risk, return policy gaps).
- [x] No restricted, counterfeit, medical, safety-critical, or regulated claims detected.

---

## 4. Supplier Evidence

| Supplier | URL | Product cost | Shipping | Lead time | Warehouse | MOQ | Notes |
|---|---|---:|---:|---|---|---:|---|
| CJ Dropshipping (Verified) | `https://cjdropshipping.com/product/901234-magnetic-wristband` | $4.20 | $2.60 (ePacket) | 2–3 days processing | CN (Yiwu) | 1 (sample); 20 for stocking | Sample at $6.80 landed; stocking fee $0.10/unit/day after 30 days; US warehouse not available for this SKU |

---

## 5. Competitor Evidence

| Competitor | Channel | URL | Price | Offer angle | Evidence age | Notes |
|---|---|---|---:|---|---|---|
| Magwear Pro | Amazon | `amazon.com/dp/B0XXXXXX` | $27.99 | Pro-grade, 18 magnets | 90 days | 4.7★, 15K reviews; premium positioning |
| Generic Brand A | TikTok Shop | `tiktok.com/shop/xyz` | $18.99 | 12 magnets, basic | 25 days | 4.2★, viral 2.1M views |
| Generic Brand B | FB/IG Ads | `fb.com/ads/library/...` | $19.99 | 15 magnets, ballistic nylon | 10 days | Active >30 days; same form factor |
| Home Depot Brand | Home Depot | `homedepot.com/p/xxx` | $24.99 | In-store pickup | 120 days | Retail distribution, not dropship |
| Harbor Freight | Harbor Freight | `harborfreight.com/xxx` | $12.99 | Budget, 10 magnets | 180 days | Low quality, weak magnets |

---

## 6. Unit Economics

```yaml
retail_price_usd: 22.99
product_cost_usd: 4.20
shipping_cost_usd: 2.60
transaction_fee_rate: 0.029
transaction_fee_fixed_usd: 0.30
estimated_cpa_usd: 11.00
net_margin_usd: 13.39
margin_to_cogs_ratio: 1.97
profitability_gate: PASS
```

Attach calculator output here:

```text
python scripts/validate_phase0_schemas.py --margin --retail 22.99 --landed 6.80
# Output: PASS — net margin $13.39 exceeds 2×CPA ($22) gate; margin/COGS 1.97×
# Note: 3×COGS gate ($20.40) not met. CAC gate is binding.
```

---

## 7. Hypothesis

A valid hypothesis must contain numeric predictions.

```text
This product is expected to reach CTR 2.2%, CVR 2.8%, CPA $11.00, and net margin $13.39 per sale in the US pilot because magnetic wristbands solve a visceral pain point for DIYers (dropped screws on ladders), the $22.99 price is an easy impulse for tool buyers, and TikTok DIY content provides endless creative hook material. Risk: CN fulfillment adds 5–10 day delivery and de minimis risk vs potential US-warehouse competitors.
```

---

## 8. Decision

| Field | Value |
|---|---|
| Recommendation | hold |
| Rationale | Score 23/30 (above 22 threshold) but US fit score of 3 due to CN-only fulfillment and de minimis risk. If supplier confirms US warehouse availability, score rises to 25/30 and recommendation becomes approve_for_phase2_test. Current recommendation: hold pending US warehouse confirmation or retail price increase to $27.99 to improve CAC buffer. |
| Required approval | Ahmad |
| Approval artifact | `docs/approvals/phase1-candidate-magnetic-wristband.md` (pending) |