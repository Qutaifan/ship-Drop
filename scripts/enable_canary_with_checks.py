#!/usr/bin/env python3
"""Canary Enablement Runner: Performs pre-flight checks, flips feature flags, and broadcasts Slack announcement."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agency.core.store import Store
from agency.notifications.drift_notifier import DriftNotifier

CANARY_FILE = ROOT / "config" / "canary_cohort.json"
FEATURE_FLAGS_FILE = ROOT / "config" / "feature_flags.json"


def run_smoke_check() -> bool:
    print("  [1/4] Running automated Phase 2 smoke suite...")
    res = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "smoke_phase2.py")],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    if res.returncode != 0:
        print("  ❌ Smoke test failed:\n", res.stdout, res.stderr)
        return False
    print("  ✓ Smoke test passed cleanly.")
    return True


def audit_canary_cohort(store: Store, skus: list[str]) -> list[str]:
    print(f"  [2/4] Auditing telemetry for {len(skus)} canary SKU(s)...")
    issues = []
    for sku in skus:
        cand = store.get_candidate(sku)
        if not cand:
            issues.append(f"Candidate not found: {sku}")
            continue

        ver = store.get_latest_verification_for_candidate(sku)
        if not ver:
            issues.append(f"Missing verification record for: {sku}")
            continue

        score = float(ver.get("stability_score", 0.0))
        if score < 0.85:
            issues.append(f"Low stability ({score:.2f} < 0.85) for {sku}")

        if ver.get("status") in ["OUT_OF_STOCK", "WAREHOUSE_MISMATCH"]:
            issues.append(f"Critical status ({ver.get('status')}) for {sku}")

        drift = abs(float(ver.get("price_drift_percent", 0.0)))
        if drift >= 0.08:
            issues.append(f"Price drift too high ({drift:.1%} >= 8%) for {sku}")

    return issues


def main() -> None:
    print("\n" + "═" * 70)
    print("  🐤 HERMES CANARY COHORT PRE-FLIGHT & ACTIVATION RUNNER")
    print("═" * 70)

    store = Store()

    # Load Canary config
    if not CANARY_FILE.exists():
        print("❌ config/canary_cohort.json missing.")
        sys.exit(1)

    with CANARY_FILE.open("r", encoding="utf-8") as f:
        canary_cfg = json.load(f)

    skus = canary_cfg.get("canary_skus", [])
    if not skus:
        print("❌ No SKUs registered in canary cohort.")
        sys.exit(1)

    # 1. Run Smoke Check
    if not run_smoke_check():
        print("\n🛑 Activation aborted: Smoke test failure.\n")
        sys.exit(1)

    # 2. Audit Cohort Telemetry
    issues = audit_canary_cohort(store, skus)
    if issues:
        print("\n🛑 Activation aborted: Pre-flight telemetry failed:")
        for iss in issues:
            print(f"    - {iss}")
        print()
        sys.exit(1)
    print("  ✓ All canary SKUs cleared stability and margin thresholds.")

    # 3. Flip Feature Flags
    print("  [3/4] Flipping feature flags to active...")
    canary_cfg["canary_enabled"] = True
    with CANARY_FILE.open("w", encoding="utf-8") as f:
        json.dump(canary_cfg, f, indent=2)

    ff: dict = {}
    if FEATURE_FLAGS_FILE.exists():
        with FEATURE_FLAGS_FILE.open("r", encoding="utf-8") as f:
            ff = json.load(f)
    ff["auto_drift_actions"] = True
    with FEATURE_FLAGS_FILE.open("w", encoding="utf-8") as f:
        json.dump(ff, f, indent=2)

    store.log_audit("CANARY_DEPLOYED_BY_FOUNDER", {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "skus": skus,
        "spend_cap": canary_cfg.get("max_automated_spend", 250.0),
    })
    print("  ✓ 'auto_drift_actions' enabled for canary cohort.")

    # 4. Dispatch Slack Announcement
    print("  [4/4] Dispatching Slack deployment broadcast...")
    notifier = DriftNotifier()
    announcement_signal = {
        "signal_id": f"canary-activated-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M')}",
        "candidate_id": "CANARY-COHORT-PHASE1",
        "product_name": f"Canary Autonomous Sourcing Active ({len(skus)} SKUs)",
        "recommended_action": f"Auto-drift actions ENABLED (Cap: ${canary_cfg.get('max_automated_spend', 250.0):.2f})",
        "severity": "MEDIUM",
        "flags": [
            f"Active SKUs: {', '.join(skus)}",
            "Auto-tripwires active: max margin drop $2.00, min stability 0.85",
            "Circuit breaker: python -m agency.cli feature-flag set auto_drift_actions false",
        ],
    }
    notifier.dispatch(announcement_signal)

    print("═" * 70)
    print("  🎉 CANARY COHORT SUCCESSFULLY ACTIVATED")
    print(f"  Monitored SKUs : {len(skus)}")
    print(f"  Spend Limit    : ${canary_cfg.get('max_automated_spend', 250.0):.2f}")
    print("  Kill Switch    : python -m agency.cli feature-flag set auto_drift_actions false")
    print("═" * 70 + "\n")


if __name__ == "__main__":
    main()
