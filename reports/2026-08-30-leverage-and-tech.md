# Leverage Analysis & Tech Upgrade — 2026-08-30

Only one thing decides whether this business works: **CAC = CPM ÷ (CTR × CVR)**.
Every tool below is ranked by its effect on that equation. Tools that do not move
CTR, CVR or CPM are not upgrades, however good they are.

## 0. Correction to the profitability verdict

The earlier report concluded "not profitable." That was **too strong, and it rested on
one channel's median.** The fuller picture:

| Source | Implied ROAS | Our breakeven | Verdict |
|---|---|---|---|
| TikTok median (5,900 brands) | 1.51x | 1.65x | Loss |
| All-paid ecommerce (AOV $61.22 ÷ CPA $23.20) | **2.64x** | 1.65x | **Profit, with headroom** |

The same benchmark house reports both. The honest reading is **channel-dependent, not
doomed**: TikTok is 2.2x cheaper per impression but converts materially worse. The
€34.90 price point fails on either. The fix remains price, and it is better supported
than the first report allowed.

**Note on why price works.** Breakeven ROAS stays 1.65x at every price point when
landed cost sits at the 20.3% ceiling — the ratio is scale-invariant. Higher ticket
helps because **CAC is roughly absolute while margin scales with price**, not because
the ratio improves. Market median CAC/AOV is 38%; our breakeven ratio is 60.7%. That
headroom is the actual margin of safety, and it only holds if CAC scales
sub-proportionally with price — an assumption to test, not to trust.

## 1. The tension nobody would have predicted

Two structural advantages are in direct conflict:

- **CAC math** says go higher ticket: retail ≥ ~€62 to cover 2x median CPA.
- **AI creative economics** says stay under $100 AOV (≈ €93):

| AOV band | AI ROAS | Human ROAS | AI conversion penalty |
|---|---|---|---|
| Under $100 | 4.0–4.8x | 4.1–4.5x | parity |
| $100–$500 | 3.1x | 3.7x | **−8%** |
| Over $500 | 2.3x | 3.1x | **−14%** |

*Source: 50,000+ ad variations, Q3 2025–Q1 2026.*

**The viable window is €62–€93 gross retail.** Below it CAC eats the margin; above it
the zero-marginal-cost creative advantage — the RTX 4060 — starts costing more in
performance than it saves in production. This narrows the earlier €70–120
recommendation, which straddled the boundary.

## 2. The real competitive advantage is volume, not the free stack

Creative hit rate is **~5% market-wide, ~3.8% under $10k/month spend**. That makes
creative a search problem:

| Creatives shipped | Chance of ≥1 winner | Expected winners |
|---|---|---|
| 5 | 18% | 0.2 |
| 10 | 32% | 0.4 |
| 20 | 54% | 0.8 |
| **40** | **79%** | **1.5** |

*"At a 5% win rate, 40 ads a month produce two winners; five ads produce almost none."*

Industry benchmark is one new ad per **$3,000** of monthly spend — a cost structure
that scales with budget. **A local GPU breaks that link.** Producing 40 creatives on
an RTX 4060 costs electricity. That, not the €30/month saved on SaaS, is the only
genuine edge this project has.

## 3. Ranked upgrades

| # | Upgrade | Mechanism | Effect on CAC | Cost |
|---|---|---|---|---|
| 1 | **Creative volume: 40+/month** | Raises the odds of finding a top-decile hook | Largest single lever — a 2x CTR hook halves CAC | Electricity |
| 2 | **Veo 3.1 Lite (Pro sub) for test phase** | 100 clips/month, ~$0.20/clip, native audio | Enables #1 at the cost of the existing €19.99 Pro subscription, no new vendor | €0 incremental |
| 3 | **AI creative, sub-$100 AOV only** | +12% CTR (1.08% vs 0.96%), −15% CPC on Meta | CAC €21.48 → €19.18 | Free |
| 4 | **Hook-rate instrumentation** | 3-sec views ÷ impressions; <25% fix, 30–40% good, 40%+ elite | Makes #1 measurable instead of guesswork | Free |
| 5 | **Page speed / CVR work** | CVR is the other multiplier in the denominator | +10% CVR → CAC €19.18 → €17.44 | Free (Medusa/Next.js already chosen) |
| 6 | **Refresh every 7–14 days** | Counters fatigue; 20–35% monthly churn is normal | Prevents CAC drift upward | Free |

Compounded at €79.90 retail: baseline **+€27.08/sale** → with AI creative and page
speed **+€31.12** → with a top-decile hook **+€38.79**.

## 4. What is NOT an upgrade

- More product-discovery tooling. Product selection was never the binding constraint;
  four candidates have already died on cost and competitor evidence, not on discovery.
- Anything above $100 AOV that leans on AI creative — it inverts the advantage.
- Paid ad-intelligence SaaS. It informs; it does not move CTR, CVR or CPM.

## 5. Verification needed before relying on any of this

1. **Wan 2.2 path is closed on this laptop** — VRAM ceiling prevents local Wan 2.2 1.3B (which needs 8GB at minimum, plus extra for VAE). Removed from the pipeline 2026-08-30; Veo Lite/Fast on Pro covers the test phase at ~$0.20–$0.40/clip. The earlier "Wan 2.2 TI2V-5B VAE mismatch" finding is now academic.
2. The AI-vs-human creative study is vendor-adjacent (AdCreative.ai benchmark). Treat the +12% CTR as directional, not settled.
   the +12% CTR as directional, not settled.
3. Hit rates come from accounts spending far more than this project will. A 3.8% rate
   at sub-$10k spend is the relevant figure, and it may be optimistic at €0 history.

## Sources

- Meta creative benchmarks 2026 (hook rate, hit rate, volume) — https://taylorsicard.com/blog/meta-ads-creative-benchmarks-2026
- AI ad creative benchmarks 2026 (CTR/ROAS by AOV) — https://www.digitalapplied.com/blog/ai-ad-creative-benchmark-2026-ctr-roas-data
- Open-source video models 2026 (VRAM, licences) — https://findaivideo.com/blog/best-open-source-ai-video-models-2026-wan-ltx
- Triple Whale ecommerce & TikTok benchmarks — https://www.triplewhale.com/blog/ecommerce-benchmarks
