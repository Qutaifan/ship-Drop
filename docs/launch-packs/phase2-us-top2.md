# Phase 2 Staging Launch Pack — US Top 2 Candidates

## Scope

- `candidate-us-2026-09-01-magnetic-cable-organizer`
- `candidate-us-2026-09-01-foldable-silicone-bowl`

This pack is for **staging preparation only**.

---

## Artifact Map

| Candidate | Product file | Creative brief | Campaign file |
|---|---|---|---|
| Magnetic Cable Organizer | `products/candidate-us-2026-09-01-magnetic-cable-organizer.md` | `creative-briefs/candidate-us-2026-09-01-magnetic-cable-organizer.md` | `campaigns/candidate-us-2026-09-01-magnetic-cable-organizer.md` |
| Foldable Silicone Bowl Set | `products/candidate-us-2026-09-01-foldable-silicone-bowl.md` | `creative-briefs/candidate-us-2026-09-01-foldable-silicone-bowl.md` | `campaigns/candidate-us-2026-09-01-foldable-silicone-bowl.md` |

---

## Staging Tasks

### 1. Creative production
- Produce 3 hooks per candidate from the prepared briefs.
- Render vertical 9:16 variations locally.
- Apply disclosure text when AI imagery is used: `Product imagery assisted by generative AI`.

### 2. Landing page staging
- One product page per candidate.
- Above-the-fold hero, benefits, proof, express checkout, FAQ, returns.
- Use staging URLs only.
- Do not publish publicly.

### 3. Tracking setup
- Define event names before creative traffic:
  - `view_product`
  - `begin_checkout`
  - `purchase_intent`
- Keep analytics self-hosted only for this phase.

### 4. Campaign placeholders
- Both campaign files already include numeric hypotheses and empty actuals tables.
- Do not mark `Kill / Scale / Iterate` until real results exist.

---

## Pre-Live Checklist

- [x] Ahmad signs `docs/phase2-approval.md`
- [x] Top-2 BUY signals re-generated against current product economics
- [ ] Staging storefront verified manually
- [ ] Creative exports rendered successfully
- [ ] Supplier profile separation remains intact
- [ ] Budget cap and expiry recorded per campaign

---

## Command Verification Already Completed

```bash
npm test
python scripts/selftest.py
python agency/run_pipeline.py
python agency/cli.py status
python agency/cli.py audit
```

All of the above completed successfully in this session except live approvals, which remain intentionally pending.
