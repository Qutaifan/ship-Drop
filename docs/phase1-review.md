# Phase 1 Review — Candidate Shortlist

**Project:** dropship  
**Market:** US pilot  
**Review date:** 2026-09-01  
**Prepared by:** dropship-research  
**Approval owner:** Ahmad  
**Status:** approved_for_phase2_staging_only

---

## Candidate Summary

| Rank | Candidate ID | Product | Score | Net Margin | Est. CPA | Recommendation |
|---|---|---|---:|---:|---:|---|
| 1 | `candidate-us-2026-09-01-magnetic-cable-organizer` | Magnetic Cable Organizer 6-Pack | 27/30 | $15.44 | $10.00 | approve_for_phase2_test |
| 2 | `candidate-us-2026-09-01-foldable-silicone-bowl` | Foldable Silicone Bowl Set 4-Pack | 27/30 | $17.54 | $12.00 | approve_for_phase2_test |
| 3 | `candidate-us-2026-09-01-magnetic-wristband` | Magnetic Wristband Tool Holder | 23/30 | $13.39 | $11.00 | hold |
| 4 | `candidate-us-2026-09-01-portable-neck-fan` | Portable Neck Fan | 21/30 | $21.34 | $15.00 | hold |

---

## Top Candidates Detail (Approve for Phase 2)

### 1. `candidate-us-2026-09-01-magnetic-cable-organizer`

**Six-criteria breakdown:**

- **US fit:** 5/5 — CJ US warehouse (NJ/CA); 3–7 day delivery; returnless refund viable
- **Supplier reliability:** 4/5 — CJ verified; 4.7★; sample at cost; 2-day processing
- **Unit economics:** 5/5 — Landed $6.80; retail $24.99; net margin $15.44; 2.27× COGS; passes 2×CPA gate
- **Differentiation:** 4/5 — Magnetic base + silicone clips; no adhesive; 6 colors; stronger magnet
- **Demand signal:** 4/5 — TikTok #desksetup 2.1B views; 12+ active FB/IG ads >30 days; Amazon BSR #800
- **Operational simplicity:** 5/5 — No sizing; no electronics; durable; returnless refund < $3

**Key evidence files:**

- `fixtures/evidence-us-cable-organizer-shipping.json`
- `fixtures/evidence-us-cable-organizer-supplier.md`
- `fixtures/evidence-us-cable-organizer-margin.json`
- `fixtures/evidence-us-cable-organizer-differentiation.md`
- `fixtures/evidence-us-cable-organizer-demand.md`
- `fixtures/evidence-us-cable-organizer-ops.md`
- `docs/candidates/candidate-us-2026-09-01-magnetic-cable-organizer.md`

**Hypothesis:**

> This product is expected to reach CTR 2.5%, CVR 3.0%, CPA $10.00, and net margin $15.44 per sale in the US pilot because magnetic desk organization has proven viral demand on TikTok (#desksetup 2.1B views), the 6-pack color variety creates perceived value above $20, and CJ US warehouse fulfillment eliminates de minimis risk while delivering 3–7 day shipping that meets US customer expectations.

### 2. `candidate-us-2026-09-01-foldable-silicone-bowl`

**Six-criteria breakdown:**

- **US fit:** 5/5 — CJ US warehouse (CA); 3–7 day delivery; returnless refund viable
- **Supplier reliability:** 4/5 — CJ verified; 4.5★; sample at cost; 2-day processing
- **Unit economics:** 5/5 — Landed $9.20; retail $29.99; net margin $17.54; 1.91× COGS; passes 2×CPA gate
- **Differentiation:** 4/5 — 4 sizes (500ml–2.5L); BPA-free platinum silicone; -40°F to 446°F; microwave/dishwasher safe
- **Demand signal:** 4/5 — TikTok #spaceavingkitchen 1.2B views; 10+ active FB/IG ads >30 days; Amazon BSR #1500
- **Operational simplicity:** 5/5 — No electronics; no sizing; FDA-grade silicone; durable; returnless refund < $3

**Key evidence files:**

- `fixtures/evidence-us-silicone-bowl-shipping.json`
- `fixtures/evidence-us-silicone-bowl-supplier.md`
- `fixtures/evidence-us-silicone-bowl-margin.json`
- `fixtures/evidence-us-silicone-bowl-differentiation.md`
- `fixtures/evidence-us-silicone-bowl-demand.md`
- `fixtures/evidence-us-silicone-bowl-ops.md`
- `docs/candidates/candidate-us-2026-09-01-foldable-silicone-bowl.md`

**Hypothesis:**

> This product is expected to reach CTR 2.8%, CVR 3.2%, CPA $12.00, and net margin $17.54 per sale in the US pilot because collapsible kitchenware has evergreen demand from small-space living trends, the 4-pack with lids creates high perceived value at $29.99, and CJ US warehouse fulfillment delivers 3–7 day shipping that converts impulse buyers.

---

## Hold Candidates (Pending Improvement)

### 3. `candidate-us-2026-09-01-magnetic-wristband`

**Score:** 23/30 — Above 22 threshold but **US fit = 3** (CN warehouse only, de minimis risk)

**Path to approve:** Supplier confirms US warehouse availability → score becomes 25/30 → approve_for_phase2_test  
**Alternative:** Increase retail to $27.99 to improve CAC buffer

### 4. `candidate-us-2026-09-01-portable-neck-fan`

**Score:** 21/30 — **Below 22 threshold**

**Blockers:** US fit = 3 (CN fulfillment, de minimis risk); Margin/COGS = 1.47× (fails 3×COGS gate); Operations = 3 (lithium battery, warranty)  
**Path to approve:** US warehouse confirmation + retail price increase to $49.99

---

## Phase 2 Test Plan Request

If approved for top 2 candidates, Phase 2 will execute:

1. **Creative production:** 3 hooks (problem, transformation, lifestyle) per product via ComfyUI + Remotion on local RTX 4060
2. **Ad test budget:** $300–500 over 7 days per product on TikTok Spark Ads / FB/IG (US, 22–50, interests: home office, kitchen, DIY, organization)
3. **Landing page:** Single-product pages on Medusa/Next.js staging (Cloudflare Tunnel)
4. **KPIs:** CTR ≥ 2.0%, CVR ≥ 2.5%, CPA ≤ $15.00 per product
5. **Kill/Scale/Iterate criteria:**
   - **Kill:** CPA > $20 after $300 spend or CVR < 1.5%
   - **Iterate:** CPA $15–20 or CTR 1.5–2.0% — test new hook/angle
   - **Scale:** CPA ≤ $15 and CVR ≥ 2.5% — increase daily budget to $100/day per product

**Bundle opportunity:** Magnetic Cable Organizer + Foldable Silicone Bowl share "organized home" audience — test bundle upsell in Phase 2.

---

## CJ MCP Token Status

The CJ MCP token that appeared in chat is **not rotated yet** per Ahmad's decision. It will be rotated before any Phase 4+ live supplier workflows. Phase 1 and Phase 2 research/test activities do not require live supplier authentication.

---

## Approval Request

```yaml
approval_id: phase1-review-top2-candidates-001
action: approve_phase2_test
object_id: candidate-us-2026-09-01-magnetic-cable-organizer,candidate-us-2026-09-01-foldable-silicone-bowl
requested_by: dropship-research
approved_by: Ahmad
approved_at: 2026-09-01T17:57:42+03:00
scope:
  market_config_id: us-pilot
  candidate_id: candidate-us-2026-09-01-magnetic-cable-organizer,candidate-us-2026-09-01-foldable-silicone-bowl
  max_budget: 1000
  currency: USD
constraints:
  - test budget only; no scale spend without separate approval
  - use staging storefront only (no public publish)
  - creative assets generated locally (ComfyUI/Remotion)
  - pixel/tracking via self-hosted Umami only
  - no CJ authentication from main profile; supplier ops isolated
expires_at: 2026-09-15T23:59:59-04:00
```

---

## Sign-Off

| Role | Name | Decision | Date | Notes |
|---|---|---|---|---|
| Approval owner | Ahmad | Approved for Phase 2 staging only | 2026-09-01 | No live spend, no public publish, no supplier writes |