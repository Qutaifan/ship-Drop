# Founder Decision Matrix — 2026-09-02

**Scope:** verification of the Phase 2 US pilot staging decision set before approval.
**Method:** every figure below was recomputed from the records in `data/candidates/`
and `docs/candidates/`. Nothing is carried over from a prior summary.

---

## 1. Headline

**Neither candidate queued for Phase 2 staging approval clears its own CAC gate.**

Both were put forward on unit economics computed from a `$69.99` placeholder retail
price. Their own candidate documents record the researched retail as `$24.99` and
`$29.99`. Recomputed at the researched prices, both fail the gate their approval
packs report as PASS.

This is not a reason to stop the pilot. It is a reason not to approve it on these
numbers. The recommendation in §4 is to correct the records and re-run the gate,
which is a short piece of work, not a re-plan.

---

## 2. What was verified

| Check | Result |
|---|---|
| Unit test suite (`unittest discover -s tests -t .`) | **129 pass** (92 pre-existing + 37 added) |
| JSON Schema validation, fixtures | 8/8 pass |
| JSON Schema validation, live records | **24/24 pass** (`data/candidates/`, `data/suppliers/`, `data/approvals/`) |
| Unit-economics reconciliation, live candidates | **11 of 19 reconcile; 8 do not** |
| `validate_workspace.py` / `validate_infra.py` / `selftest.py` | PASS / PASS / PASS (24/24 negatives caught) |

Two caveats on the "92 tests pass" claim as previously reported:

1. **The suite did not run from a clean checkout.** `jsonschema` is imported
   unguarded by `agency/core/store.py`, but no dependency manifest existed
   anywhere in the repository. Without it the suite collects 19 of 92 tests and
   the other 14 modules error on import. CI never installed it either — the
   workflow's install step was `if [ -f requirements.txt ]`, and the file did not
   exist. Fixed by adding `requirements.txt` and making the install unconditional.
2. **"Zero schema violations across `data/candidates/`" was not established by any
   committed tool.** `validate_phase0_schemas.py` checked a hardcoded list of 8
   fixtures; the 19 live candidate records were never validated. They do all pass —
   verified — but nothing enforced it. The validator now covers the live
   directories, so the claim is now checked rather than asserted.

---

## 3. The economics defects

### 3.1 Placeholder retail price on both staging candidates

| Product | Retail in `docs/candidates/*.md` | `gross_selling_price` in `data/candidates/*.json` |
|---|---:|---:|
| Magnetic Cable Organizer | $24.99 | **$69.99** |
| Foldable Silicone Bowl Set | $29.99 | **$69.99** |

Supplier and shipping costs match exactly between the two sources ($4.50/$2.30 and
$6.50/$2.70), so these are the same records — only the retail price diverges. Both
JSON records carry the same `$69.99`, which is the signature of a placeholder that
was never replaced.

### 3.2 Per-order profit is stated without subtracting the target CPA

The model's own identity is `expected_profit_per_order = contribution_before_ads −
target_cpa`. In both staging records, `expected_profit_per_order` is set equal to
`contribution_before_ads`:

| Product | Stated per-order profit | Model's own formula | Overstatement |
|---|---:|---:|---:|
| Magnetic Cable Organizer | $58.09 | $17.43 | **3.3×** |
| Foldable Silicone Bowl Set | $55.69 | $16.71 | **3.3×** |

The same record computes `target_cpa` correctly ($40.66 and $38.98) and then does
not apply it. The `magnetic-wristband` record *does* apply it, so this is an
inconsistency between records, not a deliberate convention.

### 3.3 The CAC gate fails on the researched numbers

Recomputed at the retail prices in the candidate documents:

| Product | Net margin | Median CPA used | Gate (2× CPA) | Result | Shortfall |
|---|---:|---:|---:|---|---:|
| Magnetic Cable Organizer | $15.44 | $8.50 | $17.00 | **FAIL** | −$1.56 |
| Magnetic Cable Organizer | $15.44 | $12.00 *(configured)* | $24.00 | **FAIL** | −$8.56 |
| Foldable Silicone Bowl Set | $17.54 | $12.00 | $24.00 | **FAIL** | −$6.46 |

Both candidate documents state this gate as **PASS**. The arithmetic does not
support it: `15.44 > 17.00` and `17.54 > 24.00` are both false.

The cable organizer's pack also uses a median CPA of `$8.50`, where
`agency/config/settings.py` sets `MEDIAN_CPA_USD = 12.00`. At the configured
figure the shortfall is $8.56, not $1.56.

### 3.4 COGS multiples are below the configured floor

`TARGET_COGS_MULTIPLE = 3.00`, `MIN_COGS_MULTIPLE = 2.00`.

| Product | Margin / COGS | vs minimum 2.00× | vs target 3.00× |
|---|---:|---|---|
| Magnetic Cable Organizer | 2.27× | pass | **fail** |
| Foldable Silicone Bowl Set | 1.91× | **fail** | **fail** |

### 3.5 Direction of the errors

Across the 19 live candidates, **20 discrepancies were found and every one
overstates the figure.** None understate.

This is the pattern `reports/2026-08-30-sweep-audit.md` recorded in the demand
sweep — 9 of 10 wrong, every error optimistic — and the reason `verify_sweep.py`
exists. Errors that all run the profitable direction indicate a formula applied
wrongly, not scattered typos. `scripts/validate_candidate_economics.py` now
applies that same check to unit economics.

---

## 4. Decision matrix

| Priority | Item | Recommended action | Basis |
|---|---|---|---|
| **P0** | `candidate-us-2026-09-01-magnetic-cable-organizer`<br>`candidate-us-2026-09-01-foldable-silicone-bowl` | **Correct the records, then re-run the gate — do not approve staging yet** | Both carry a $69.99 placeholder retail; both fail the CAC gate at their researched prices (§3.3) |
| **P1** | Re-price or re-source the top 2 | **Founder decision required** | To clear 2×$12 CPA the cable organizer needs ≈$27.50 net margin at $24.99 retail, which the current landed cost cannot yield. Either raise retail, cut landed cost, or accept a lower CAC target |
| **P2** | `sig-sell-kill-cand-cj-sku-magnetic-wristband-556c05` | **Confirm kill** — unchanged | Contribution is $11.58, not the stated $13.39 (`return_allowance` omitted). The correction makes the kill *more* clearly right, not less |
| **P3** | `sig-supplier-switch-candidate-electric-jar-vacuum-d9a82d` | **Defer** | Classified US re-sourcing in one summary and EU-defer in the shortlist. No candidate record carries a `market` field, so neither is derivable from data — resolve the classification before spending founder time |
| **P4** | EU backlog signals | **Defer** — unchanged | Operating contract is US-first (`docs/operating-contract.md`) |
| **P5** | Duplicate candidate records | **Merge** | 3 products have two records each under different `candidate_id`s (jar vacuum sealer, thermal sticker printer, ultrasonic cleaner) |

### Signal IDs — the shortlist is stale

`docs/founder-signal-shortlist-2026-09-01.md` names `…magnet-b84a3f` and
`…foldab-923f7a` as the Priority-1 approvals. Both were quarantined at
`2026-09-01T15:06:46` with reason `superseded_by_phase2_economics_refresh`.

The live signals are `…magnet-500f28` and `…foldab-460ef9`, which is what
`docs/phase2-approval.md` and the launch-gate review reference. **Approve against
the `500f28` / `460ef9` pair**; the shortlist document has been corrected.

---

## 5. Reproducibility gap

`agency/cli.py status` reports **0 active trade signals, 0 pending founder review**
on a fresh clone, while the shortlist cites 17 pending.

The cause is `.gitignore`: `data/signals/*.json` and `*.db` are both excluded. The
signal set backing every decision above exists only on the machine that generated
it. Anyone reviewing this repository — or any future session — cannot reproduce the
17-signal state or verify the shortlist against it.

The audit log (`data/audit/audit_log.jsonl`) *is* tracked, which is the only reason
the supersession in §4 could be established at all.

**Recommendation:** either commit the signal store, or treat the audit log as the
system of record and regenerate signals from it on demand. Deciding this is a
prerequisite for any second reviewer.

---

## 6. What changed in this pass

- `requirements.txt` added; `jsonschema` was an undeclared hard dependency.
- CI now runs on pull requests, installs dependencies unconditionally, runs schema
  validation and the unit suite, and fails if a test run modifies tracked files.
- `scripts/validate_phase0_schemas.py` extended from 8 fixtures to 8 fixtures plus
  24 live records.
- `scripts/validate_candidate_economics.py` added, with the 8 unreconciled records
  quarantined in a declared list so the debt is visible and shrinking rather than
  silent.
- Test suite made hermetic. It previously wrote to `data/audit/audit_log.jsonl`,
  `data/medusa_catalog/products.json`, and `config/autonomous_windows.json` on
  every run.
- `agency/api/server.py`: handler collaborators were bound to the import-time
  `Store`, so injecting a different store moved only some endpoints.
  `/telemetry/overview` and `/economic/portfolio` kept reading the live data
  directory — meaning two bridge tests were asserting against real repository data
  rather than their own fixture, and passed for the wrong reason.
- 37 tests added (16 for `margin_solver`, 17 for the economics reconciler, 4
  isolation guards).

---

## 7. Open items for the founder

1. **Re-price or re-source the top 2**, then re-run the gate. Nothing else in the
   pilot can be decided until this is settled.
2. **Confirm the median CPA** to gate against — `$8.50` and `$12.00` are both in
   use, and the choice changes the cable organizer's shortfall by $7.
3. **Decide whether signals are committed state** (§5).
4. **Resolve the market classification** — no candidate record carries a `market`
   field, so the US/EU split driving the defer decisions is not in the data.
