# Dropshipping — Full Project Brief (US Market Strategy)

**Updated 2026-08-31 · Status: US Market Pivot, zero spend committed — GCC retired**

---
## 1. What this project is

An autonomous e-commerce growth and retail arbitrage operation run by **Hermes-Ecom** focused on the **United States** high-velocity DTC market. Products are screened, costed, and gated by explicit rules; nothing advances on judgement alone. The workspace is the source of truth and automated validators enforce it.

**Governing constraint set by the owner: free and open-source path only.** Every unavoidable cost is named rather than buried.
## 2. Where it actually stands

| Metric | Status |
|---|---|
| Products validated (PASS) | **0** |
| Products rejected with evidence | 8 (all prior GCC/EU candidates FAIL — see products/*.md) |
| Products pending | 0 (pipeline cleared for US catalog search) |
| Ad spend committed | **$0** |
| Storefront deployed | Scaffolded (Medusa v2 + Next.js) |
| Active ad networks | TikTok US + Meta US (manual Ad Library) |

**Nothing has been wasted.** Previous candidates were eliminated before budget was spent on hard evidence. Pivot to US reuses same gates with VAT 0%, USD pricing, and US fulfillment.

---

## 3. The pipeline

```
products/        PROTOCOL-01  screen, cost, gate      → PASS / FAIL
creative-briefs/ PROTOCOL-02  3+1 English brief        (requires PASS)
campaigns/       live tracking vs numeric hypothesis
reports/         rollups and research
learnings/       PROTOCOL-03  retrospective → HEURISTICS.md
```

Each stage gates the next and the gates are enforced. A brief cannot exist without a PASS. A campaign cannot exist without a brief. A closed campaign must produce a retrospective.

### Validation Tooling

| Script | Purpose |
|---|---|
| `validate_workspace.py` | Pipeline integrity, multi-currency margin arithmetic, gate compliance |
| `validate_infra.py` | Compose structure, env coverage, AGENTS/prompt parity |
| `verify_sweep.py` | Recomputes research sweep metrics from raw data |
| `selftest.py` | 24 deliberate defects — proves validators catch bad input |
| `profitability.py` | US CAC gate (TikTok US, Meta US, ECOM median) — run with `--currency USD --vat 0` |
| `ad_library.py`, `demand_screen.py`, `margin_solver.py`, `generate_brief.py`, `learning_loop.py` | Operational pipeline stages — note: `ad_library.py` is EU/UK-automated only; US requires manual Meta Ad Library web UI |

---

## 4. US Market Strategy & Decisions

### Funnel Architecture: 1-Page LTR Fast Funnel (English)
- **Express Checkout**: Shop Pay (~40% of Shopify checkouts), Apple Pay, PayPal (~30% US ecom), Google Pay, Stripe 2.9% + $0.30
- **No COD** — US is 99% prepaid. Standard email + address form.
- **Mobile Experience**: English LTR, sub-1.2s LCP, trust badges (Free US shipping, 30-day returns, 2-year warranty), reviews + UGC social proof.

### Paid Traffic Engine: TikTok US + Meta US
- **TikTok Ads US**: Primary test channel — lowest CPM ($4.08 vs Meta US $9-15), 9:16 UGC hooks with English voiceover. First gate for every candidate.
- **Meta Ads US (Facebook/Instagram Reels)**: Retargeting + scaling. Higher CPM but broader intent. Manual Ad Library verification required (Graph API returns only EU/UK commercial ads).
- **Snapchat retired** — GCC-only channel, not relevant for US pivot.

### Sourcing & Fulfillment: US Domestic Priority
- **CJ US Warehouses (Los Angeles / New Jersey)**: 2–5 day domestic delivery via USPS/UPS, duty paid once on bulk import, easy returns. Preferred for all PASS candidates.
- **Direct from China (test only)**: 7–12 days via CJPacket/YunExpress. **De minimis $800 restricted since 2026** — expect duty + MPF + HMF per parcel. Testing only, not scaling.
- **US 3PL for winners**: ShipBob / Deliverr for 1–2 day winners (pre-stock bulk).

### Creative Engine: Google Flow / Veo 3.1 on Google AI Pro
- **Test Phase**: Veo 3.1 Lite (10 credits/clip, ~$0.20) and Fast (20 credits/clip, ~$0.40) on Google AI Pro (~1,000 credits/month). Rapid iteration of 40+ ad concepts/month.
- **Winner Phase**: Re-shoot proven winning hooks in Veo 3.1 Quality (100 credits/clip, ~$2.00) with native audio and cinematic resolution.

---

## 5. Unit Economics & Pricing Band (US)

### Formula
```
Net Margin = (Retail / (1 + VAT)) − (Product Cost + Shipping + Import Duty) − Payment Fee
US: VAT = 0, so Net = Retail − COGS − 2.9%*Retail − $0.30
```

- **Target Retail Price Band**: **$62 – $99 gross retail (extended $69–$119, hard ceiling $100 for AI creative)**.
- **Floor**: Set by the CAC gate (net margin must be ≥ 2x median CPA). At landed $8, need ~$56 retail; at landed $12, need ~$60 retail. Practical floor **$62**.
- **Ceiling**: Set by the AI-creative threshold (~$100 AOV) where AI vertical creative loses to human creative (ROAS 3.1x vs 3.7x).
- **US landed rule**: Landed cost must be **≤ 24.2% of retail** (VAT 0%, fee 3%). At $69.99 → max landed $16.94; at $49.99 → max $12.10. Tighter than it looks once CAC is applied.
- **CAC benchmarks (USD, 2025/26)**: TikTok Global CPA $17.07, ECOM median $23.20, funnel-implied $42.88. Gate: net ≥ $46.40 (2× median). Test on TikTok first (CPM $4.08 vs Meta DE $9.05, Meta US ~$12-15).

| Retail | Max landed (24.2%) | Net at max landed | CAC gate (need $46.40) |
|---|---|---|---|
| $49.99 | $12.10 | $36.30 | FAIL |
| $62.00 | $15.00 | $44.82 | FAIL (borderline) |
| $69.99 | $16.94 | $50.58 | PASS |
| $89.99 | $21.78 | $65.50 | PASS |

---

## 6. What to do next, in order

1. **Sourcing Scan on CJ US Warehouses**: Identify high-perceived-value home, organization, and lifestyle products in the **$62–$99** retail band with landed costs ≤ 24.2% of retail (ideally $8-16 landed at $69-89 retail).
2. **Run PROTOCOL-01 Screens**: Execute `scripts/demand_screen.py` and `scripts/margin_solver.py --currency USD --vat 0` + `profitability.py --currency USD --vat 0` for each candidate. Manual Meta Ad Library US + TikTok Creative Center US for competitor check.
3. **Scaffold 3+1 English Briefs**: Use `scripts/generate_brief.py` to generate TikTok/Meta US vertical hooks and 1-page LTR checkout wireframes.
4. **Deploy Storefront & Launch Test Campaigns**: Deploy Medusa v2 Next.js storefront on Cloudflare Tunnel and test with $150–$300 test budget per winner candidate (expect $1,500–$6,000 search capital to find one winner at 5-10% win rate).
