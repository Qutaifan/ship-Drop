# Dropshipping — Full Project Brief (GCC & Global Strategy)

**Updated 2026-08-30 · Status: GCC Market Pivot, zero spend committed**

---

## 1. What this project is

An autonomous e-commerce growth and retail arbitrage operation run by **Hermes-Ecom** focused on the **Gulf Countries (GCC: Saudi Arabia / KSA, UAE, Kuwait, Qatar, Bahrain, Oman)** and international high-velocity commerce. Products are screened, costed, and gated by explicit rules; nothing advances on judgement alone. The workspace is the source of truth and automated validators enforce it.

**Governing constraint set by the owner: free and open-source path only.** Every unavoidable cost is named rather than buried.

## 2. Where it actually stands

| Metric | Status |
|---|---|
| Products validated (PASS) | **0** |
| Products rejected with evidence | 4 |
| Products pending | 0 (pipeline cleared for GCC catalog search) |
| Ad spend committed | **$0 / 0 SAR** |
| Storefront deployed | Scaffolded (Medusa v2 + Next.js RTL) |
| Active ad networks | Snapchat Ads (GCC priority) + TikTok GCC + Meta |

**Nothing has been wasted.** Previous candidate products were eliminated before budget was spent on hard evidence. That is the validation engine working as designed.

---

## 3. The pipeline

```
products/        PROTOCOL-01  screen, cost, gate      → PASS / FAIL
creative-briefs/ PROTOCOL-02  3+1 Arabic brief        (requires PASS)
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
| `profitability.py` | Multi-channel CAC gate (Snapchat KSA, TikTok GCC, Meta) |
| `ad_library.py`, `demand_screen.py`, `margin_solver.py`, `generate_brief.py`, `learning_loop.py` | Operational pipeline stages |

---

## 4. GCC Market Strategy & Decisions

### Funnel Architecture: 1-Page RTL Arabic Fast Funnel

- **Prepaid Flow**: 1-Tap Apple Pay (>70% mobile market share in KSA/UAE), Mada (Saudi debit), Tabby / Tamara (BNPL), and KNET.
- **Cash on Delivery (COD) Flow**: 3-field simple checkout (Name, Mobile, City/District) paired with automated post-order WhatsApp address verification to keep RTO (Return to Origin) below 12–15%.
- **Mobile Experience**: Arabic Right-to-Left (RTL) layout, sub-1.2s LCP, trust badges (fast delivery, 14-day warranty), floating WhatsApp customer reassurance chat.

### Paid Traffic Engine: Snapchat & TikTok GCC Priority

- **Snapchat Ads**: #1 social commerce driver in Saudi Arabia and Kuwait. Highest penetration, lowest CPMs ($2.80 vs Meta's $7.50+), top-performing 9:16 vertical story & spotlight placements.
- **TikTok Ads GCC**: Short-form UGC hooks with Arabic voiceovers / text overlays.
- **Meta / Instagram Ads**: UAE, Qatar, and retargeting campaigns.

### Sourcing & Fulfillment: Direct Middle East Express Lines

- **CJdropshipping Middle East Lines**: CJPacket Middle East, AJEX, iMile, SMSA, and Aramex direct air lines (5–9 days delivery) with integrated COD collection.
- **GCC Local Warehousing (3PL)**: Pre-stocking proven winners in Dubai or Riyadh for 1–3 day delivery and zero NDR risk.

### Creative Engine: Google Flow / Veo 3.1 on Google AI Pro

- **Test Phase**: Veo 3.1 Lite (10 credits/clip, ~$0.20) and Fast (20 credits/clip, ~$0.40) on Ahmad's Google AI Pro subscription (~1,000 credits/month). Rapid iteration of 40+ ad concepts/month.
- **Winner Phase**: Re-shoot proven winning hooks in Veo 3.1 Quality (100 credits/clip, ~$2.00) with native audio and cinematic resolution.

---

## 5. Unit Economics & Pricing Band

### Formula
```
Net Margin = (Retail / (1 + VAT)) − (Product Cost + Shipping + Import Duty) − (Payment Fee / COD Surcharge)
```

- **Target Retail Price Band**: **180 SAR – 380 SAR (~$48 – $100 USD / ~EUR 62–93)**.
- **Floor**: Set by the CAC gate (net margin must be ≥ 2x median CPA to guarantee profitability under ad variance).
- **Ceiling**: Set by the AI-creative threshold (~$100 AOV) where automated vertical creative maintains superior ROAS.

---

## 6. What to do next, in order

1. **Sourcing Scan on CJ Middle East Lines**: Identify high-perceived-value home, organization, and lifestyle products in the **180 SAR – 380 SAR** retail band with landed costs ≤ 20–25% of retail.
2. **Run PROTOCOL-01 Screens**: Execute `scripts/demand_screen.py` and `scripts/margin_solver.py` for each candidate.
3. **Scaffold 3+1 Arabic Briefs**: Use `scripts/generate_brief.py` to generate Snapchat/TikTok vertical hooks and 1-page checkout wireframes.
4. **Deploy Storefront & Launch Test Campaigns**: Deploy Medusa v2 Next.js RTL storefront on Cloudflare Tunnel and test with $150–$300 test budget per winner candidate.
