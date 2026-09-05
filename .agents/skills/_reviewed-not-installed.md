# Nexscope eCommerce-Skills — Review Notes (2026-08-30)

Reviewed `https://github.com/nexscope-ai/eCommerce-Skills` against the
AGENTS.md stack and our 5 custom skills (now archived under
`.agents/skills/_archive/`). Outcome: **one of nine candidates
adopted**, eight not installed.

## Decision

Adopt **`ecommerce-ppc-strategy-planner`** (533 lines). All other
candidates are either prompt-only guidance with no executable code,
or contain Amazon-FBA-shaped math incompatible with our Medusa v2 +
CJdropshipping stack.

Heuristic logged as **H-002 (SUPPORTED, n=1)** in
`learnings/HEURISTICS.md`.

## Per-skill review

| Skill | Lines | Decision | Reason |
|---|---|---|---|
| `dropshipping-product-research` | 63 | Skip | Prompt-only. "Use the frameworks and methodology below" — no frameworks, no methodology. Body is capabilities list + install command. Worse than our archived `ecommerce-validator` (which at least references `margin_solver.py` + `profitability.py`). |
| `profit-margin-calculator-amazon` | 243 + 547-line Python | Skip | Amazon-FBA-specific math: referral fees by category, FBA fulfilment fee, FBA storage fee. None apply to EU dropshipping on Medusa + CJdropshipping. Even Nexscope's only executable skill doesn't fit our business model. |
| `product-review-analysis` | 320 | Skip (for now) | Substantive review-mining framework. Useful as background reading. Doesn't replace the hook-mining pattern in our archived `crawlee-scraper` skill because it doesn't address the anti-bot / proxy-rotation / merchant-scope rules we need. |
| `ecommerce-landing-page` | 64 | Skip | Empty structure. No PROTOCOL-02 alignment, no Stripe Express wiring, no EU tax disclosure, no R2 image loader. Our `medusa-v2-storefront` skill (archived) had more, even before the rewrite the audit calls for. |
| `market-gap-analysis` | 63 | Skip | Prompt-only. Useful as a checklist the agent can apply during ORIENT, but no executable gate. Keep an eye on it if Nexscope ships a v2 with substance. |
| `ecommerce-ppc-strategy-planner` | **533** | **ADOPT** | Best fit of the lot. ROAS financial framework, break-even ROAS calculation, platform recommendation by buyer behavior, cross-platform budget allocation, ad-copy generation. Real methodology, not just capability lists. Complements our `profitability.py` (which gates by hard numeric thresholds) by adding the *qualitative* platform-selection reasoning the script can't express. **Install at `.agents/skills/ecommerce-ppc-strategy-planner/SKILL.md`.** |
| `product-launch-strategy` | 64 | Skip | Empty structure. |
| `ecommerce-video-marketing` | 36 | Skip | Empty structure. |
| `competitor-price-analysis` | 252 | Skip (for now) | Substantive competitor pricing methodology. Useful background but doesn't replace Meta Ad Library API integration (which is what our archived `ecommerce-validator` referenced via `scripts/ad_library.py`). |

## Why prompt-only isn't enough

The PROTOCOL-01 gate logic in `AGENTS.md §4A` requires **executable
checks that fail closed**:

| Gate | Source of truth | Nexscope equivalent |
|---|---|---|
| Net margin ≥ 3× COGS and >€15 | `scripts/margin_solver.py` (exit 1 on fail) | None — `profit-margin-calculator-amazon` returns a status enum but the agent can ignore it |
| Net margin ≥ 2× median CPA (CAC gate) | `scripts/profitability.py` (exit 1 on fail) | None — `ecommerce-ppc-strategy-planner` calculates break-even ROAS in prose, no exit code |
| 5–10 competitors, ≥3 ads active 30+ days | `scripts/ad_library.py` | None |
| EU customs (€3 flat duty, import VAT) | `scripts/margin_solver.py --duty 3 --vat 0.19` | None — Nexscope's calculator is Amazon-shaped |
| PROTOCOL-03 learning loop | `scripts/learning_loop.py` + `learnings/HEURISTICS.md` | None |

A prompt-only skill **recommends**; it does not **enforce**. An agent
can still produce a PASS verdict on a failing candidate. The scripts
prevent that.

## What changes in `.agents/skills/`

```
.agents/skills/
├── _archive/                       ← 5 custom skills preserved for rollback
│   ├── comfyui-product-staging/
│   ├── crawlee-scraper/
│   ├── ecommerce-validator/
│   ├── medusa-v2-storefront/
│   └── remotion-video-ads/
├── ecommerce-ppc-strategy-planner/ ← NEW: Nexscope, MIT, 533 lines
│   └── SKILL.md
├── veo-flow-ads/                   ← Kept (winner-phase re-shoot; no Nexscope equivalent)
└── _reviewed-not-installed.md      ← this file
```

## Rollback

If Nexscope adoption proves unhelpful, restore the archived set with:

```bash
mv .agents/skills/_archive/* .agents/skills/
```

The 5 archived skills are byte-identical to the versions committed at
`903dd50 feat(validation): evaluate electric pepper grinder and folding laundry basket…`.