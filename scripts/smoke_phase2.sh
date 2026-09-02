#!/usr/bin/env bash
# scripts/smoke_phase2.sh
# Purpose: Run Phase 2 smoke checks for supplier verification, reconciliation, drift scan, and history.
# Exit codes: 0=all good, 1=any check failed

set -euo pipefail
IFS=$'\n\t'

# Configurable variables
DB_PATH="${DB_PATH:-data/dropship.db}"
SAMPLE_CANDIDATE="${SAMPLE_CANDIDATE:-cand-cj-sku-magnetic-cord-6p}"
TIMEOUT_CLI="${TIMEOUT_CLI:-20}"   # seconds per CLI call
TMPDIR="$(mktemp -d)"
LOG="$TMPDIR/smoke_phase2.log"
FAIL=0

echo "Phase2 smoke test started at $(date -u +"%Y-%m-%dT%H:%M:%SZ")" | tee "$LOG"

run_cmd() {
  local cmd="$1"
  local outfile="$2"
  echo ">>> Running: $cmd" | tee -a "$LOG"
  if timeout "$TIMEOUT_CLI" bash -c "$cmd" > "$outfile" 2>&1; then
    echo "OK: $cmd" | tee -a "$LOG"
    return 0
  else
    echo "FAIL: $cmd (see $outfile)" | tee -a "$LOG"
    FAIL=1
    return 1
  fi
}

# 1) Verify candidate
OUT1="$TMPDIR/verify.out"
run_cmd "python -m agency.cli verify $SAMPLE_CANDIDATE" "$OUT1"

# Basic assertions on verify output
grep -E "Status Verdict|Stability Score|Stock Level" "$OUT1" >/dev/null || { echo "ASSERTION FAILED: verify output missing expected fields" | tee -a "$LOG"; FAIL=1; }

# 2) Reconcile margins
OUT2="$TMPDIR/reconcile.out"
run_cmd "python -m agency.cli reconcile $SAMPLE_CANDIDATE" "$OUT2"
grep -E "Net Margin|Total Landed Cost|Expected ROAS" "$OUT2" >/dev/null || { echo "ASSERTION FAILED: reconcile output missing expected fields" | tee -a "$LOG"; FAIL=1; }

# 3) Drift scan (JSON mode)
OUT3="$TMPDIR/drift.out"
run_cmd "python -m agency.cli drift --json" "$OUT3"
# Ensure JSON is valid and contains an array or object
python - <<PY >> "$LOG" 2>&1
import sys, json
try:
    j=json.load(open("$OUT3"))
    if not isinstance(j, (list, dict)):
        print("ASSERTION FAILED: drift output JSON not list/dict", file=sys.stderr); sys.exit(2)
except Exception as e:
    print("ASSERTION FAILED: drift output JSON parse error:", e, file=sys.stderr); sys.exit(2)
print("Drift JSON OK")
PY || FAIL=1

# 4) Verification history
OUT4="$TMPDIR/verhistory.out"
run_cmd "python -m agency.cli ver-history $SAMPLE_CANDIDATE" "$OUT4"
grep -E "Verification ID|verified_at|Status Verdict" "$OUT4" >/dev/null || { echo "ASSERTION FAILED: ver-history output missing expected fields" | tee -a "$LOG"; FAIL=1; }

# 5) Feature flag sanity check
OUT5="$TMPDIR/ff.out"
run_cmd "python -m agency.cli feature-flag get" "$OUT5"
grep -E "auto_drift_actions" "$OUT5" >/dev/null || { echo "ASSERTION FAILED: feature-flag output missing auto_drift_actions" | tee -a "$LOG"; FAIL=1; }

# Finalize
if [ "$FAIL" -eq 0 ]; then
  echo "SMOKE TEST PASSED: All Phase 2 checks OK" | tee -a "$LOG"
  cat "$LOG"
  rm -rf "$TMPDIR"
  exit 0
else
  echo "SMOKE TEST FAILED: See $LOG and $TMPDIR for details" | tee -a "$LOG"
  echo "Log files:" | tee -a "$LOG"
  ls -1 "$TMPDIR" | tee -a "$LOG"
  cat "$LOG"
  exit 1
fi
