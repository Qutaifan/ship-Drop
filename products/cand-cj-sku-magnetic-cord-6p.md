# Product Validation — Magnetic Cable Organizer 6-Pack Desk Clips

Created 2026-09-03. This candidate was sourced through the newer `data/candidates/`
JSON pipeline (`cand-cj-sku-magnetic-cord-6p.json`) rather than the older
`products/*.md`-first workflow, so it had no file here and could not flow through
`scripts/generate_brief.py`, which gates on this document. Backfilled from the JSON
record after its economics were corrected (see reports/2026-09-03 sweep and
reports/2026-09-02-founder-decision-matrix.md).

## Product
- Name: Magnetic Cable Organizer 6-Pack Desk Clips
- Source/supplier candidate(s): CJ Dropshipping US Domestic Hub (CJ-SKU-MAGNETIC-CORD-6P)
- Retail price target (VAT-inclusive, as the customer pays): $62.99
- VAT rate (destination market, e.g. 0.19 for DE): 0.00
- Product cost: $3.80
- Shipping cost: $3.20
- Import duty per unit: $0.00

## 6-Criteria Screen (PROTOCOL-01 / AGENTS.md §4A)
1. Wow Factor (sub-3s emotional hook?): PASS — magnetic snap-on cable routing is a fast visual payoff, same family as the other desk-organization candidates.
2. Problem Solving (what friction does it resolve?): PASS — desk cable clutter is a persistent, recognizable friction point.
3. Visual Appeal (communicable in silent 9:16 video?): PASS — demand evidence shows 2.1M social video views on this exact format.
4. Healthy Margins (€15–30/sale target; reject <€20 retail): PASS — net margin $54.10 at $62.99 retail on this document's own flat-3%-fee formula (see below).
5. Low Return Potential (simple/durable mechanics?): PASS — no electronics, no sizing, simple magnetic clip mechanics.
6. Low Local Retail Availability: PARTIAL PASS — generic cable clips are locally available; the 6-pack magnetic desk-specific positioning differentiates.

## Competitor Check
- Competitors running ads (need 5–10): 6 recorded, **but sourced via the Meta Ad Library DSA API, which only discloses commercial ads inside the EU/UK** (BRIEF.md §4). These 6 competitor prices are in EUR and reflect EU market activity, not verified US demand. This is a genuine gap, not a formality — the US-market competitor check itself is blocked on the same Meta developer app + identity verification blocker tracked in ClickUp ("Blocker — Create Meta developer app"). Treat this criterion as **unverified for the US market**, not as passed.
- Ads active 30+ days (need ≥3, proves sustained profitability): Not established for US — see above.

## True Margin Matrix
(Retail ÷ (1 + VAT)) − (Product Cost + Shipping + Import Duty) − 3% of gross retail = Net Margin
VAT is collected on the customer's behalf and remitted — it is never revenue.
The payment fee is charged on the GROSS amount, so it is not divided by VAT.
- Net Margin: $54.10 ($62.99 retail − $7.00 COGS − 3% flat fee $1.89, this document's own formula per `scripts/validate_workspace.py`)
- Must be ≥3x COGS and >$15: PASS — COGS multiple 7.73x on this formula

**Note on two coexisting margin models:** `data/candidates/cand-cj-sku-magnetic-cord-6p.json` uses a more granular itemized model (separate payment_fees, packaging_cost, variable_support_cost, return_allowance rather than one flat 3%), which nets to $51.24 after also fixing three unrelated bugs (net_revenue contamination from a sibling record, a break_even_cpa mismatch, an expected_profit_per_order formula bug — see that file's rationale). Both numbers clear every gate; the JSON figure is the operational one used for target_cpa and expected_profit_per_order. This is not a discrepancy to force into agreement — the two files deliberately use different granularity, and both should be read together, not in isolation.

## Regulatory Check
- De Minimis / sourcing region: CJ Dropshipping US Domestic Hub — US-warehouse fulfillment, no per-order direct-from-China import path.
- EU AI Act disclosure needed (AI imagery/support)?: Not applicable — US pilot. Disclose per FTC guidance if AI creative is used.
- FTC dynamic pricing rule-based (not user-tracked)?: Yes — rule-based only.

## Verdict
**FAIL — blocked specifically on the PROTOCOL-01 competitor-durability check, not on margin.**

Margin and creative-readiness criteria all separately PASS at the true, corrected numbers above — this is the only one of the three active US-pilot candidates whose margin clears its own gate (the other two, Magnetic Cable Organizer and Foldable Silicone Bowl, fail at their researched retail). But PROTOCOL-01 requires ≥3 competitor ads verified active 30+ days, and that cannot be honestly established for the US market: the only competitor evidence on file is EU-sourced via the Meta Ad Library DSA API (see Competitor Check above), which does not disclose commercial ads outside the EU/UK. Inventing a US ad-age figure to force a PASS here would repeat exactly the kind of fabricated-certainty error this project has spent two audit rounds finding and correcting elsewhere — so this stays FAIL until the Meta developer app blocker clears and the check can actually be run (BRIEF.md §9.1).

`creative-briefs/cand-cj-sku-magnetic-cord-6p.md` and `campaigns/cand-cj-sku-magnetic-cord-6p.md` have been pre-staged anyway, since the creative work itself doesn't depend on this check and there's no reason to redo it later — but `scripts/validate_workspace.py` will correctly flag both as premature per PROTOCOL-02's "verdict must be PASS" rule until this verdict flips. That is accurate, not a bug: no real ad spend can happen until the Meta blocker clears regardless, so the campaign is inert paperwork either way.
