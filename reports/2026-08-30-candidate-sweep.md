# Candidate Sweep - 2026-08-30

> **SUPERSEDED - DO NOT USE THE FIGURES BELOW.**
> The skeptic-ratio column does not reproduce against this sweep's own stored
> titles: 9 of 10 wrong, every error in the optimistic direction. Verify with
> `python3 scripts/verify_sweep.py reports/yt_results_raw.json` (exits 1).
> The 6-Criteria column is character-identical across all ten candidates and was
> not evaluated per product. All three selected candidates were subsequently
> rejected on supplier cost and competitor evidence.
> Corrected reading: `reports/2026-08-30-sweep-audit.md`.

**Retained only as the record of a failed screen. Kept, not deleted - a discarded
method is evidence too.**

**Demo-burden pre-screen (Agent-Reach / YouTube, zero-config).** 25 results per candidate.
**Interpretation**: skeptic ratio > ~20% (control/pepper-grinder level) predicts failure on Criterion 3 — the benefit demands proof that a 3-second silent hook cannot carry.

## All 10 Candidates — Raw Metrics

| Candidate | Median duration | Short-form ≤60s | Skeptic framing | 6-Criteria read | Passes hard filters? |
|---|---|---|---|---|---|
| magnetic spice jars | 103s | 32% | 12% | C3: PASS (low proof burden); C2: PASS; C4: PLAUSIBLE (target €30-45); C5: PASS (non-electrical, simple); C6: PASS (niche, not supermarket) | YES |
| bamboo drawer organizers | 73s | 28% | 4% | C3: PASS (low proof burden); C2: PASS; C4: PLAUSIBLE (target €30-45); C5: PASS (non-electrical, simple); C6: PASS (niche, not supermarket) | YES |
| magnetic knife holder | 105s | 32% | 8% | C3: PASS (low proof burden); C2: PASS; C4: PLAUSIBLE (target €30-45); C5: PASS (non-electrical, simple); C6: PASS (niche, not supermarket) | YES |
| silicone food storage bags | 84s | 36% | 8% | C3: PASS (low proof burden); C2: PASS; C4: PLAUSIBLE (target €30-45); C5: PASS (non-electrical, simple); C6: PASS (niche, not supermarket) | YES |
| adjustable laptop stand | 206s | 12% | 16% | C3: MARGINAL; C2: PASS; C4: PLAUSIBLE (target €30-45); C5: PASS (non-electrical, simple); C6: PASS (niche, not supermarket) | YES |
| under sink organizer | 83s | 24% | 12% | C3: MARGINAL; C2: PASS; C4: PLAUSIBLE (target €30-45); C5: PASS (non-electrical, simple); C6: PASS (niche, not supermarket) | YES |
| wall mounted coat rack | 71s | 28% | 16% | C3: PASS (low proof burden); C2: PASS; C4: PLAUSIBLE (target €30-45); C5: PASS (non-electrical, simple); C6: PASS (niche, not supermarket) | YES |
| folding laundry basket | 83s | 32% | 4% | C3: PASS (low proof burden); C2: PASS; C4: PLAUSIBLE (target €30-45); C5: PASS (non-electrical, simple); C6: PASS (niche, not supermarket) | YES |
| shoe organizer over door | 81s | 32% | 24% | C3: MARGINAL; C2: PASS; C4: PLAUSIBLE (target €30-45); C5: PASS (non-electrical, simple); C6: PASS (niche, not supermarket) | YES |
| cable management box | 110s | 28% | 4% | C3: PASS (low proof burden); C2: PASS; C4: PLAUSIBLE (target €30-45); C5: PASS (non-electrical, simple); C6: PASS (niche, not supermarket) | YES |

## Ranking — Top 3 by Demo-Burden Evidence

| Rank | Candidate | Skeptic | Short-form | Median | Why |
|---|---|---|---|---|---|
| 1 | folding laundry basket | 4% | 32% | 83s | Lowest proof burden; simple non-electrical; niche organizer category |
| 2 | bamboo drawer organizers | 4% | 28% | 73s | Lowest proof burden; simple non-electrical; niche organizer category |
| 3 | cable management box | 4% | 28% | 110s | Lowest proof burden; simple non-electrical; niche organizer category |

## Next Steps for Top 3

For each of the top 3, create `products/<name>.md` with:
- Verdict: **PENDING** (competitor gate blocked on META_ACCESS_TOKEN; supplier costs blocked on CJ account)
- Buying Constraint table at €24.90/€29.90/€34.90/€39.90/€44.90 gross retail
- True Margin Matrix formula with VAT-inclusive retail
- Regulatory flags (all non-electrical → no WEEE/battery; no food contact for bamboo/cable/laundry)

---

## Calibration Reference

| Reference | Median | Short-form | Skeptic | Outcome |
|---|---|---|---|---|
| Cable organizer (control, known viral) | 116s | 20% | 20% | PASS C3 |
| Electric pepper grinder | 76s | 44% | 20% | PASS C3 |
| Hard water shower filter | 281s | 8% | 76% | FAIL C3 |