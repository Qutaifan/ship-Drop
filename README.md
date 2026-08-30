# Dropshiping — Workspace

Hermes-Ecom operates in this project. Persona + protocols: see `AGENTS.md`.
Portable copy-paste system prompt for other LLMs: `HERMES-PROMPT.md`.

## Structure

- `products/` — one file per candidate product, scored against the 6-Criteria formula (PROTOCOL-01)
- `creative-briefs/` — "3+1" ad hook sets + landing page frameworks per validated product (PROTOCOL-02)
- `suppliers/` — sourcing options, pricing, lead times, compliance notes (De Minimis / EU AI Act / FTC)
- `campaigns/` — live/past campaign tracking: spend, CTR, margin actuals vs. hypothesis
- `reports/` — periodic margin/performance rollups
- `learnings/` — post-campaign retrospectives + `HEURISTICS.md`, the accumulated knowledge base (PROTOCOL-03)
- `scripts/` — operational & validation tooling:
  - `margin_solver.py` — True Margin Matrix & Buying Constraint solver
  - `demand_screen.py` — multi-pass YouTube demand & proof-burden screening
  - `generate_brief.py` — PROTOCOL-02 "3+1" creative brief scaffolder
  - `learning_loop.py` — PROTOCOL-03 retrospective & heuristics engine
  - `ad_library.py` — Meta Ad Library Graph API competitor gate
  - `ebay_api.py` — eBay Browse API market research & pricing intelligence
  - `temu_api.py` — Temu Open Platform EU V3 API client
  - `r2_storage.py` — Cloudflare R2 / S3 storage & media uploader
  - `validate_workspace.py` — PROTOCOL-01..03 pipeline integrity
  - `validate_infra.py` — infra/ definitions + AGENTS/prompt parity
  - `selftest.py` — proves validators fail on bad input
  - `verify_sweep.py` — YouTube sweep arithmetic auditor
- `infra/` — Docker Compose stack, Cloudflare Tunnel config, and bootstrap steps for the self-hosted storefront
- `_to_delete/` — build artifacts and temp files staged for removal; safe to delete by hand (this session cannot delete files on disk)

## Workflow

1. Candidate product → `products/<product-name>.md` → run PROTOCOL-01 pre-screen (`demand_screen.py`) & margin matrix (`margin_solver.py`)
2. Competitor check → `scripts/ad_library.py` → verify sustained profitability
3. If it passes → `creative-briefs/<product-name>.md` → generate the 3+1 brief (`scripts/generate_brief.py`)
4. Once live → `campaigns/<product-name>.md` → track actuals against numeric hypothesis
5. Weekly → `reports/<date>.md` → rollup
6. On Kill/Scale/Iterate → `learnings/<date>-<product>.md` → run PROTOCOL-03 → promote heuristics into `learnings/HEURISTICS.md`

The loop closes at step 6: PROTOCOL-01 reads `HEURISTICS.md` during ORIENT, so every closed campaign tightens the next product's scoring.

## Validation

```
python3 scripts/validate_workspace.py   # PROTOCOL-01..03 pipeline integrity
python3 scripts/validate_infra.py       # infra/ definitions + AGENTS/prompt parity
python3 scripts/selftest.py             # proves both validators fail on bad input
```

Stdlib only (PyYAML optional — infra checks downgrade gracefully without it). Checks template integrity, True Margin Matrix arithmetic, the PROTOCOL-01 competitor gates, pipeline referential integrity (no orphan briefs, no campaign without a brief), numeric hypotheses, closed campaigns missing a retrospective, and the `HEURISTICS.md` status lifecycle. Exit code 0 = clean, 1 = at least one error. Run it before every commit.
