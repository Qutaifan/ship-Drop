# Trend Scan — Keyword Momentum — 2026-08-30

**Phase**: OBSERVE (PROTOCOL-01 pre-screen). **Market assumed**: EU.
**No product is validated by this document.** Nothing here has passed the competitor
or margin gates. These are candidates, not verdicts.

---

## 1. Keyword momentum — where search is actually growing

Google Trends YoY growth, via Glimpse:

| Keyword | YoY growth | Retail band | 6-Criteria read |
|---|---|---|---|
| Mouth tape | **+134%** | ~€10–20 | FAIL §4 — under the €20 floor; health-claim exposure |
| Hair texture powder | **+104%** | €15–25 | FAIL — EU cosmetics (CPNP notification) |
| Vanity bag | +66% | €25–45 | WEAK — undifferentiated, high competition |
| Flat back earrings | +65% | €10–20 | FAIL §4 — under the €20 floor |
| Sleep bonnet | +64% | €10–20 | FAIL §4 — under the €20 floor |
| Blue light therapy light | +38% | €40–90 | FAIL — health claims + electrical (see §3) |
| Electric pepper grinder | +32% | €25–45 | CANDIDATE — strong silent demo, but electrical |
| Sleep earbuds | +31% | €50–120 | FAIL §5 — complex electronics, high return rate |
| Hair repair mask | +30% | €15–30 | FAIL — EU cosmetics regulation |
| Hard water shower filter | +20% | €30–50 | **CANDIDATE — strongest under the gates** |
| Glass straw | +18% | €8–15 | FAIL §4 |
| Sauna blanket | +8% | €120–250 | WEAK — heavy freight, electrical safety, return risk |

**The data reveals** that raw search growth and launch-viability are close to
uncorrelated. The three fastest-growing keywords all fail on price floor or
regulation. Trend lists optimize for demand direction; PROTOCOL-01 optimizes for
margin, returns, and compliance. Ranking by growth alone would put us into the
worst three products on the board.

## 2. Competitive saturation — the gate most lists ignore

Active TikTok ad counts by category (Trendtrack, August 2026):

| Category | Leading advertiser | Active TikTok ads | Reading |
|---|---|---|---|
| Beauty/body devices | BASED | **9,400** | Wall, not gap. 3.7M followers, 1.58M monthly visits |
| Shapewear | Feelingirl | 6,644 | Saturated; also FAIL §5 (sizing returns) |
| Tech accessories | MAGIC JOHN | 6,301 | Saturated at the top; long tail may hold |
| Fragrance | Scentiment | 5,434 | Saturated; IP/authenticity risk |
| Apparel | Edikted | 4,191 | FAIL §5 — sizing curves |

PROTOCOL-01 asks for 5–10 competitors with ≥3 ads aged 30+ days as *proof of
sustained profitability*. These categories are far past that threshold — they show
proven demand and a proven inability to enter cheaply. **A category running 9,400
concurrent ads is not a signal to enter; it is a signal that CPMs are bid to the
ceiling by brands with 100x our budget.** The target zone is 5–15 competitors, not
thousands.

## 3. The EU filter that reorders everything

For an EU-first, zero-fixed-cost launch, electrical goods carry obligations most
trend lists never mention:

- **WEEE registration** — required per member state for electrical/electronic goods.
- **Battery regulation** — separate registration and take-back duties for anything
  battery-powered.
- **CE marking / LVD / RoHS** — conformity documentation held by the responsible person.

These are recurring per-country registration costs and administrative overhead. They
break the free/OSS-equivalent cost constraint on the physical side of the business.

**Consequence**: the electric pepper grinder (+32%) drops below the hard water shower
filter (+20%) despite growing faster. Lower growth, no electronics, no WEEE, no
battery directive, and a consumable refill that creates repeat revenue the ad spend
does not have to buy twice.

## 4. Shortlist to take into PROTOCOL-01

| Rank | Candidate | Why it survives | What could kill it |
|---|---|---|---|
| 1 | Hard water shower filter | €30–50 retail clears the floor; no electronics (§5); genuine daily friction (§2); refill = repeat revenue; low local retail availability (§6) | **§3 visual appeal** — the benefit is invisible. Silent 9:16 demo must be solved before spend, likely via before/after on limescale, hair, or glassware |
| 2 | Electric pepper grinder | Best silent-video demo on the board (§1, §3); clears the floor | WEEE + battery registration; motor = return risk (§5) |
| 3 | Tech organizer pouch | Clears the floor at the top of its band; no compliance load | Weak differentiation; low wow factor; back-to-school seasonal |

## 5. Execution gaps — what is NOT known

Grounding requires stating these rather than filling them:

1. **No competitor counts from a primary source.** The ad counts above are a third
   party's aggregate by *category*, not by product. PROTOCOL-01 needs per-product
   counts and ad ages from the **official Meta Ad Library API**.
2. **No supplier costs.** Every retail band above is a secondary-source estimate. The
   True Margin Matrix cannot run without real unit cost, shipping cost, and lead time
   from a named EU-warehouse supplier.
3. **Source contamination.** These lists are read by every dropshipper. Anything
   appearing on them is already being tested at volume. Treat them as a source of
   *hypotheses*, never of edge.
4. **Glimpse growth baseline year is unstated** — YoY is confirmed, the base is not.

## 5b. ADDENDUM — the margin bar moved (added 2026-08-30, same day)

The True Margin Matrix was corrected after this scan was written. It previously omitted VAT, overstating EU net margin by roughly the VAT rate (~21% of stated margin at DE's 19%). Every retail band in §1 and §4 must now be read against the corrected model:

`Net Margin = (Retail / (1 + VAT)) − (Product Cost + Shipping + Import Duty) − (0.03 × Retail)`

Two consequences for this shortlist:

1. **The €20 retail floor is now far too low in practice.** On a worked example with €11.30 COGS, clearing the 3x gate needs roughly **€42+ gross retail**, not €20. Candidates in the €25–35 bands are much tighter than they look here.
2. **Import duty must be sourced away, not absorbed.** Direct-from-China fulfilment adds €3 per customs item plus import VAT and ~€2 handling on every order. Fulfilling from CJ's DE/PL warehouse pays duty once on the bulk import — see `suppliers/cjdropshipping.md`.

Ranking is unchanged, but the hard water shower filter's €30–50 band is now **borderline at the low end** and viable only near the top of it, or on EU-warehouse fulfilment with real supplier costs.

## 5c. SUPERSEDED — shortlist reranked

The §4 ranking was overturned the same day by evidence, not opinion. See
`reports/2026-08-30-demo-burden-screen.md`. The hard water shower filter **fails
criterion 3**: 76% of the top 25 YouTube results are skeptic-framed, the median
explainer runs 4m41, and short form is 8% of the category. The benefit needs a
chemical test to demonstrate, so it cannot carry a 3-second silent hook.

**Current order: 1) electric pepper grinder, 2) hard water shower filter,
3) tech organizer pouch.**

## 6. Next action

Build the Meta Ad Library API client, then run per-product competitor counts on the
three shortlisted candidates. Only products clearing both the competitor gate and the
True Margin Matrix get a `products/<name>.md` file with a PASS verdict.

## Sources

- Trendtrack, *Top 6 Dropshipping Product Trends for August 2026* — https://www.trendtrack.io/blog-post/top-6-dropshipping-product-trends-for-august-2026
- Glimpse, *Google Trends Products* — https://meetglimpse.com/google-trends/products/
- CJdropshipping, *10 Best Dropshipping Products to Sell in August 2026* — https://cjdropshipping.com/blogs/winning-products/10-Best-Dropshipping-Products-to-Sell-in-August-2026
