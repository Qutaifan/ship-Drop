# Live-Gate Review Pack — US Top 2 Candidates

## Scope

This pack prepares the **exact approval objects** required before any live ad write.

- `candidate-us-2026-09-01-magnetic-cable-organizer`
- `candidate-us-2026-09-01-foldable-silicone-bowl`

Live execution remains blocked until Ahmad separately approves the exact campaign scope below.

---

## Refreshed Signal Set

| Candidate | Refreshed signal ID | Signal type | CTR | CVR | Predicted CPA | Signal-level net margin | Target budget |
|---|---|---|---:|---:|---:|---:|---:|
| `candidate-us-2026-09-01-magnetic-cable-organizer` | `sig-buy-candidate-us-2026-09-01-magnet-500f28` | BUY | 2.1% | 2.5% | $40.66 | $58.09 | $300 |
| `candidate-us-2026-09-01-foldable-silicone-bowl` | `sig-buy-candidate-us-2026-09-01-foldab-460ef9` | BUY | 2.1% | 2.5% | $38.98 | $55.69 | $300 |

**Superseded signals quarantined for 48h**
- `sig-buy-candidate-us-2026-09-01-magnet-b84a3f`
- `sig-buy-candidate-us-2026-09-01-foldab-923f7a`

---

## Economics Reconciliation

| Candidate | Workspace True Margin Matrix | Signal-level net margin | Difference | Explanation |
|---|---:|---:|---:|---|
| Magnetic Cable Organizer | $61.09 | $58.09 | $3.00 | signal model includes refund/support/return allowances for launch gating |
| Foldable Silicone Bowl Set | $58.69 | $55.69 | $3.00 | signal model includes refund/support/return allowances for launch gating |

---

## Proposed Exact Campaign Approval Objects

These are **proposed internal launch objects**, not yet-created platform campaigns.

| Candidate | Proposed internal campaign label | Platform mix | Spend cap | Auto-pause rule |
|---|---|---|---:|---|
| `candidate-us-2026-09-01-magnetic-cable-organizer` | `phase4-us-magnetic-cable-organizer-test-001` | TikTok 60% / Meta 25% / Google 15% | $300 | pause if CPA > $60.99 or CTR < 1.3% |
| `candidate-us-2026-09-01-foldable-silicone-bowl` | `phase4-us-foldable-silicone-bowl-test-001` | TikTok 60% / Meta 25% / Google 15% | $300 | pause if CPA > $58.47 or CTR < 1.3% |

---

## PPC Planner Verification

### Magnetic Cable Organizer
- Retail: $69.99
- Landed COGS: $6.80
- Gross margin: $61.09
- Target ROAS: 1.90x
- Planner target CPA: $39.71
- Projected net profit at $300 budget: $240.82

### Foldable Silicone Bowl Set
- Retail: $69.99
- Landed COGS: $9.20
- Gross margin: $58.69
- Target ROAS: 1.96x
- Planner target CPA: $38.15
- Projected net profit at $300 budget: $219.76

---

## Required Founder Decision For Live Gate

Approve or reject these exact objects:

1. `sig-buy-candidate-us-2026-09-01-magnet-500f28` with campaign label `phase4-us-magnetic-cable-organizer-test-001`
2. `sig-buy-candidate-us-2026-09-01-foldab-460ef9` with campaign label `phase4-us-foldable-silicone-bowl-test-001`

If approved later, the next controlled step is to create the live campaigns under a separate execution window with the same spend caps and pause rules.
