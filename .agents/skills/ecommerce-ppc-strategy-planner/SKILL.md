---
name: ecommerce-ppc-strategy-planner
description: "Cross-platform PPC strategy planner for ecommerce businesses. Analyzes your product and margins, recommends the right advertising platforms (Google Ads, Meta Ads, TikTok Ads), calculates ROAS targets, allocates budget across channels, and generates platform-specific campaign briefs with ad copy and creative direction. Two modes: (A) Build — design a multi-platform ad strategy from scratch, (B) Optimize — audit existing cross-platform campaigns and reallocate budget. Works for Shopify, Medusa v2, WooCommerce, and standalone stores. No API key required."
metadata: {"nexscope":{"emoji":"📊","category":"ecommerce"}}
---

# E-Commerce PPC Strategy Planner 📊

Plan your cross-platform advertising strategy: which platforms to use, how much to spend on each, and what campaigns to run. Generates actionable briefs for Google Ads, Meta Ads, and TikTok Ads — with ad copy and creative direction included.

## Two Operational Modes

| Mode | When to Use | Input | Output |
|------|-------------|-------|--------|
| **A — Build** | Launching ads for a new SKU / testing phase | Product retail price + landed cost + monthly budget + buyer behavior type | Platform mix recommendation + budget split + campaign structures + platform-specific ad copy briefs |
| **B — Optimize** | Scaling winners / auditing running campaigns | Per-platform ROAS / CPA / spend data | Cross-platform audit + budget reallocation matrix (scale winners, pause bleeders) + tactical actions |

---

## Capabilities & Quantitative Formulas

### 1. Financial Framework & ROAS Modeling
- **Net Profit Margin**:
  $$\text{Margin \%} = \frac{\text{Retail} - \text{Landed COGS} - \text{Payment Fee}}{\text{Retail}}$$
- **Break-even ROAS**:
  $$\text{Break-even ROAS} = \frac{1}{\text{Profit Margin \%}} = \frac{\text{Retail}}{\text{Gross Margin \$$}}$$
  *(e.g., At 70% gross profit margin, Break-even ROAS = $1 / 0.70 = 1.43\times$)*
- **Target ROAS**:
  $$\text{Target ROAS} = 1.50\times \text{ to } 2.00\times \text{ Break-even ROAS}$$
  *(Ensures healthy net operating cashflow after ad spend)*
- **Maximum Break-Even CPA**:
  $$\text{Max CPA} = \text{Retail} \times \text{Profit Margin \%} = \text{Net Contribution Before Ads}$$
- **Target CPA**:
  $$\text{Target CPA} = \text{Max CPA} \times 0.65 \text{ to } 0.70$$

---

### 2. Platform ROAS Benchmarks & Suitability Matrix

| Platform | Average ROAS | Top Quartile | Best For | Funnel Position |
|----------|:-----------:|:------------:|----------|-----------------|
| **Google Ads (Shopping / PMax)** | 4.5x | 6.0x+ | High-intent searchers (already actively looking for utility/solution) | Bottom of Funnel (Capture) |
| **Meta Ads (FB/IG Reels/Feed)** | 2.2x | 4.0–5.0x | Visual aesthetics, lifestyle, impulse buys, retargeting ($3.6\times$) | Mid-to-Bottom of Funnel |
| **TikTok Ads / Spark Ads** | 1.4x | 2.0x+ | High visual proof burden, demo-driven problem-solvers, viral novelty | Top of Funnel (Discovery) |

---

## Mode A Workflow (Build Strategy from Scratch)

1. **Collect Product & Financial Profile**:
   - Gross Retail Price ($R$), Landed COGS ($L$), Payment Gateway Fee (~3%).
   - Monthly Testing/Scaling Budget.
   - Core Behavioral Category: **Search-Driven** (problem-aware), **Visual/Lifestyle** (aspiration), or **Demo-Driven** (instant wow-factor).

2. **Compute Financial Framework**:
   - Calculate Break-even ROAS, Target ROAS, and Target CPA.
   - Verify candidate clears the Hermes **CAC Gate**: $\text{Gross Margin} \ge 2\times \text{Median CPA}$.

3. **Determine Multi-Platform Budget Split**:
   - **Visual / Demo Product (e.g., Cable Organizer, Desk Gear)**:
     - 60% TikTok / Spark Ads (Top-of-funnel creative testing)
     - 25% Meta Ads (Lookalikes, Advantage+ Shopping, IG Reels)
     - 15% Google Shopping / PMax (Intent capture for brand searches)
   - **Search-Driven Problem Solver (e.g., Jar Sealer, Jewelry Cleaner)**:
     - 50% Google PMax / Standard Shopping
     - 35% Meta Ads
     - 15% TikTok Ads

4. **Generate Platform Campaign Briefs**:
   - **TikTok Campaign**: CBO, 3 Ad Groups (Broad, Interest/Hashtag Stack, Spark Creator), 3+1 Creative Briefs.
   - **Meta Campaign**: Advantage+ Shopping Campaign (ASC) + 1 Retargeting Ad Set (Visitors 30D / ATC 14D).
   - **Google Campaign**: Performance Max with asset group signals (Competitor URL audiences + high-intent in-market terms).

---

## Mode B Workflow (Cross-Platform Optimization)

1. **Audit Live Metrics**:
   - Ingest Spend, Revenue, Impressions, Clicks, Conversions per platform from Umami / Stripe / Ad Managers.
2. **Evaluate Performance Against ROAS Targets**:
   - If $\text{Platform ROAS} > 1.25 \times \text{Target ROAS}$: **SCALE** (+20% budget every 48 hours).
   - If $\text{Break-even ROAS} \le \text{Platform ROAS} \le \text{Target ROAS}$: **OPTIMIZE** (Refresh creative hooks, trim non-converting placements).
   - If $\text{Platform ROAS} < \text{Break-even ROAS}$: **KILL / REALLOCATE** (Cut budget by 50% or pause, reallocate capital to winning platform).
