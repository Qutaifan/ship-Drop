# Signal Store Reconciliation — 2026-09-03

Resolves the open question in `reports/2026-09-02-founder-decision-matrix.md` §5:
whether trade signals should be committed state.

Read directly from `data/signals/` on the local machine (241 files).

---

## 1. The pending count is reported three ways

| Source | Pending founder review |
|---|---|
| `agency/cli.py status` on a fresh clone | **0** |
| `docs/founder-signal-shortlist-2026-09-01.md` | **17** |
| **Actual, on disk** | **112** |

The fresh-clone zero is the `.gitignore` gap already documented. The 17 is stale.
112 is the real number.

## 2. Full breakdown of the 241

| approval_status | Count |
|---|---|
| QUARANTINE_48H | 125 |
| PENDING_FOUNDER_REVIEW | **112** |
| APPROVED | 3 |
| REJECTED | 1 |

| signal_type | Count |
|---|---|
| SUPPLIER_SWITCH | 156 |
| BUY | 50 |
| SELL_KILL | 20 |
| TREND_ALERT | 15 |

Across 19 unique `candidate_id`s. `target_market` splits 170 EU / 71 US.

## 3. Roughly half the pending queue is duplicates

The 112 pending signals reduce to **55 distinct** when fingerprinted on
`candidate_id` + `signal_type` + `hypothesis.statement`.

Verified by direct comparison — three `sig-supplier-drift-bamboo-drawer-organizers-*`
files are byte-identical apart from `signal_id` and `created_at`:

```
030f00  created 2026-09-01T04:18:47
0dfce0  created 2026-09-01T04:03:41
2e5c9f  created 2026-09-01T05:23:41
```

Same scores, same hypothesis, same action plan. `tracker_bot` emits a fresh
signal per run for an unchanged condition — there is no idempotency key on
(candidate, type, condition).

The system already detects this after the fact: all 125 quarantined records carry
`quarantine_reason: "superseded_duplicate_pending_signal"`, and all were quarantined
in a single sweep at `2026-09-01T14:48:11.293865+00:00`. New duplicates have
accumulated since — the most recent signal was created `2026-09-02T21:10:50`.

The sweep is a cleanup for a defect that should be prevented at emission.

## 4. Most of the queue is for dead products

Roughly 44 of the 112 pending signals belong to candidates already rejected or
failed at pre-screen:

| Candidate | Pending | State |
|---|---|---|
| cable-management-box | 7 | rejected (BRIEF §7) |
| bamboo-drawer-organizers | 7 | rejected (BRIEF §7) |
| folding-laundry-basket | 7 | rejected (BRIEF §7) |
| cloud-key-holder | 7 | Pre-Screen FAIL |
| led-sunset-lamp | 8 | Pre-Screen FAIL |
| portable-neck-fan | 8 | Pre-Screen FAIL |

Generation never stops when a candidate dies. Every one of these needs a founder
decision it will never deserve.

## 5. `target_market` exists on signals but not on candidates

§4 (P3) of the decision matrix notes that no candidate record carries a `market`
field. Signal records **do** — 170 EU / 71 US across the store.

This narrows that task: the market data exists in the signal layer and can be
backfilled onto candidates from it, rather than reconstructed from prose. Worth
verifying the signal values are themselves correct before trusting them as a source.

## 6. Naming inconsistency

Files named `sig-supplier-drift-*` carry `signal_type: "SUPPLIER_SWITCH"`. There are
also separate `sig-supplier-switch-*` files with the same type. Anything filtering
on the `signal_id` prefix rather than the `signal_type` field will split one category
into two.

---

## Recommendation

**Commit the signal store — but not in its current state.**

Committing 241 files where half are duplicates and a third concern dead candidates
makes the noise permanent and inflicts it on every future reader.

Sequence:

1. Add an idempotency key on (candidate_id, signal_type, condition) at emission
2. Re-run the quarantine sweep to clear the accumulated duplicates
3. Stop generation for rejected / pre-screen-failed candidates
4. Backfill `market` onto candidate records from `target_market`
5. **Then** commit, and remove `data/signals/*.json` from `.gitignore`

The audit log (`data/audit/audit_log.jsonl`) stays tracked either way — it is
currently the only reason signal supersession can be reconstructed at all.

---

*Generated during ClickUp reconciliation session, 2026-09-03. The corresponding
ClickUp task could not be updated — the workspace hit its API rate limit mid-session.*
