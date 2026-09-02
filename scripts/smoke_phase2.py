#!/usr/bin/env python3
"""Cross-platform automated smoke test runner for Phase 2 supplier intelligence."""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = "cand-cj-sku-magnetic-cord-6p"


def run_cli(args: list[str]) -> tuple[int, str]:
    cmd = [sys.executable, "-m", "agency.cli"] + args
    res = subprocess.run(
        cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return res.returncode, res.stdout + res.stderr


def main() -> None:
    now_str = datetime.now(timezone.utc).isoformat()
    print(f"Phase 2 Smoke Test started at {now_str}")
    failures = 0

    # 1) Verify candidate
    print(f">>> Running: verify {CANDIDATE}")
    code, out = run_cli(["verify", CANDIDATE])
    if code != 0 or not re.search(r"Status Verdict|Stability Score|Stock Level", out):
        print(f"FAIL: verify output missing expected fields (code={code})")
        failures += 1
    else:
        print("OK: verify passed")

    # 2) Reconcile margins
    print(f">>> Running: reconcile {CANDIDATE}")
    code, out = run_cli(["reconcile", CANDIDATE])
    if code != 0 or not re.search(r"Net Margin|Total Landed Cost|Expected ROAS", out):
        print(f"FAIL: reconcile output missing expected fields (code={code})")
        failures += 1
    else:
        print("OK: reconcile passed")

    # 3) Drift scan (JSON mode)
    print(">>> Running: drift --json")
    code, out = run_cli(["drift", "--json"])
    if code != 0:
        print(f"FAIL: drift --json returned non-zero code {code}")
        failures += 1
    else:
        try:
            j = json.loads(out)
            if not isinstance(j, (list, dict)):
                print("FAIL: drift output JSON not list/dict")
                failures += 1
            else:
                print("OK: drift JSON passed")
        except Exception as e:
            print(f"FAIL: drift output JSON parse error: {e}")
            failures += 1

    # 4) Verification history
    print(f">>> Running: ver-history {CANDIDATE}")
    code, out = run_cli(["ver-history", CANDIDATE])
    if code != 0 or not re.search(r"Verification ID|verified_at|Status Verdict", out):
        print(f"FAIL: ver-history output missing expected fields (code={code})")
        failures += 1
    else:
        print("OK: ver-history passed")

    # 5) Feature flag sanity check
    print(">>> Running: feature-flag get")
    code, out = run_cli(["feature-flag", "get"])
    if code != 0 or not re.search(r"auto_drift_actions", out):
        print(f"FAIL: feature-flag output missing auto_drift_actions (code={code})")
        failures += 1
    else:
        print("OK: feature-flag passed")

    if failures == 0:
        print("\n✨ SMOKE TEST PASSED: All Phase 2 checks OK")
        sys.exit(0)
    else:
        print(f"\n❌ SMOKE TEST FAILED: {failures} check(s) failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
