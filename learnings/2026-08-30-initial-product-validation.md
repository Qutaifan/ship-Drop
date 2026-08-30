# Retrospective — Initial Product Validation Sprint — 2026-08-30

## Linked files
- products/led-sunset-lamp.md
- products/portable-neck-fan.md
- products/cloud-key-holder.md
- reports/2026-08-30-demo-burden-screen.md
- reports/2026-08-30-profitability-validation.md

## 1. Prediction Ledger

No paid campaigns launched, so CTR, CVR, CPA, and campaign actuals are not available. Margin and demand hypotheses were tested directly during PROTOCOL-01.

| Product | Net margin | 3x COGS gate | €15 floor | Retail floor | YouTube median views | Demand verdict |
|---|---:|---|---|---|---:|---|
| LED Sunset Projection Lamp | €17.23 | FAIL (needs ≥€21.00) | PASS | PASS | 249 | FAIL |
| Portable Mini Neck Fan (Bladeless) | €20.28 | FAIL (needs ≥€24.00) | PASS | PASS | 820 | FAIL |
| Cloud-Shaped Magnetic Key Holder | €12.12 | PASS (needs ≥€12.00) | FAIL | FAIL | 851 | FAIL |

## 2. What the data actually revealed

All three candidates failed PROTOCOL-01 before paid acquisition. The LED Sunset Lamp had a stable 32% skeptic ratio but only 249 median YouTube views. The Portable Neck Fan had 68% skeptic ratio, noisy drift, and 820 median views. The Cloud Key Holder had low proof burden at 8% skeptic ratio and stable 4% drift, but only 851 median views. All three therefore failed the demand floor of 2,500 median views.

The margin screen also rejected every candidate: the LED Sunset Lamp and Portable Neck Fan failed the 3x COGS gate, while the Cloud Key Holder passed that gate but failed both the €15 net margin floor and the €20 retail floor.

## 3. Root cause

- [x] Product selection (the demand and unit-economics hypotheses were not viable together)
- [ ] Creative (hook failed to stop the thumb)
- [ ] Landing page (traffic arrived, did not convert)
- [x] Margin math (unit economics were not viable for paid acquisition)
- [ ] Supply chain (lead time / duty / stockout)
- [x] Audience or platform targeting (content demand signal was below the floor)

## 4. Candidate heuristics

| # | Heuristic | Evidence from this campaign |
|---|---|---|
| 1 | Saturated viral novelties under €30 retail fail recent YouTube demand volume (<1,000 median views) and lack the margin buffer for paid Meta acquisition. | Three consecutive candidates failed the YouTube demand floor: 249, 820, and 851 median views. Two failed the 3x COGS gate, and the third failed the €15 and €20 retail floors. |

## 5. Promotion decision

Promote the candidate heuristic to `HEURISTICS.md` as **PROVISIONAL**, n=1 campaign. Do not use it as a hard gate until at least three independent closed campaigns support it.

## 6. Contradictions

No existing heuristic entries were present, so there are no contradictions to resolve.
