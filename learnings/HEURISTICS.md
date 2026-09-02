# HEURISTICS — Hermes-Ecom Accumulated Knowledge Base

**This file is read at the start of every PROTOCOL-01 run.** It is the agent's memory across campaigns and the mechanism by which it improves. It is written only by PROTOCOL-03, only from closed-campaign evidence.

## Status lifecycle

| Status | Meaning | Rule |
|---|---|---|
| `PROVISIONAL` | Observed in 1 campaign | Apply as a tiebreaker only — never as a gate |
| `SUPPORTED` | Held in ≥3 campaigns, no contradictions | Apply as a scoring modifier in PROTOCOL-01 |
| `CONTESTED` | Contradicted at least once | Flag it, do not act on it, seek a decisive test |
| `RETIRED` | Falsified | Keep the row — a retired heuristic is evidence too |

**Never delete a row.** Retired entries prevent relearning a dead idea.

## Ledger

| ID | Heuristic | Status | n | Supporting | Contradicting | Last reviewed |
|---|---|---|---|---|---|---|
| H-001 | Saturated viral novelties under €30 retail fail recent YouTube demand volume (<1,000 median views) and lack the margin buffer for paid Meta acquisition. | PROVISIONAL | 1 | LED Sunset Lamp, Portable Neck Fan, Cloud Key Holder | None | 2026-08-30 |
| *(empty — populated by the first PROTOCOL-03 retrospective; IDs run H-001, H-002, …)* | | | | | | |

Tracks the agent's own forecasting bias across campaigns. If predicted CTR runs consistently above actual, PROTOCOL-01 hypotheses must be discounted by the running mean error before a launch decision.

| Campaign | Date | Metric | Predicted | Actual | Error % |
|---|---|---|---|---|---|
| *(empty)* |  |  |  |  |  |

**Running bias**: CTR — n/a · CVR — n/a · Margin — n/a
