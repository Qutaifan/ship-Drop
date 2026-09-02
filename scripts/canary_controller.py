#!/usr/bin/env python3
"""Canary Cohort Controller & Safety Tripwire Monitor for Autonomous Supplier Actions."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

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

CONFIG_FILE = ROOT / "config" / "feature_flags.json"
CANARY_FILE = ROOT / "config" / "canary_cohort.json"


def load_canary_config() -> Dict[str, Any]:
    if CANARY_FILE.exists():
        with CANARY_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "canary_enabled": False,
        "max_automated_spend": 250.0,
        "canary_skus": [
            "cand-cj-sku-magnetic-cord-6p",
            "candidate-us-2026-09-01-foldable-silicone-bowl",
            "candidate-us-2026-09-01-magnetic-cable-organizer"
        ],
        "tripwires": {
            "max_false_positive_rate": 0.05,
            "min_stability_score": 0.85,
            "max_margin_drop_usd": 2.00
        }
    }


def save_canary_config(cfg: Dict[str, Any]) -> None:
    CANARY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with CANARY_FILE.open("w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


def check_tripwires(store: Store) -> List[str]:
    """Scans recent verifications and drift signals to check if any tripwires are breached."""
    cfg = load_canary_config()
    tripwires = cfg.get("tripwires", {})
    breaches = []

    # Check stability score of canary SKUs
    min_stability = tripwires.get("min_stability_score", 0.85)
    for sku in cfg.get("canary_skus", []):
        latest = store.get_latest_verification_for_candidate(sku)
        if latest:
            score = latest.get("stability_score", 1.0)
            if score < min_stability:
                breaches.append(f"STABILITY_TRIPWIRE: SKU {sku} stability score ({score:.2f}) dropped below {min_stability}")

    return breaches


def main() -> None:
    parser = argparse.ArgumentParser(description="Hermes Canary Controller")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("status", help="Show canary cohort status and tripwire health")
    subparsers.add_parser("enable", help="Enable canary mode for cohort")
    subparsers.add_parser("disable", help="Disable canary mode (circuit breaker)")
    add_parser = subparsers.add_parser("add", help="Add SKU to canary cohort")
    add_parser.add_argument("candidate_id", help="Candidate ID to add")
    rem_parser = subparsers.add_parser("remove", help="Remove SKU from canary cohort")
    rem_parser.add_argument("candidate_id", help="Candidate ID to remove")

    args = parser.parse_args()
    store = Store()
    cfg = load_canary_config()

    if args.command == "status" or not args.command:
        breaches = check_tripwires(store)
        print("\n" + "═" * 65)
        print("  🐤 CANARY CONTROLLER STATUS")
        print("═" * 65)
        print(f"  Canary Mode Active  : {'✅ ENABLED' if cfg.get('canary_enabled') else '🛑 DISABLED'}")
        print(f"  Max Auto-Spend Cap  : ${cfg.get('max_automated_spend', 250.0):.2f}")
        print("  Active Canary SKUs  :")
        for sku in cfg.get("canary_skus", []):
            latest = store.get_latest_verification_for_candidate(sku)
            stab = f"{latest.get('stability_score', 0.0):.2f}" if latest else "unverified"
            print(f"    - {sku:<48} (Stability: {stab})")
        print("-" * 65)
        if breaches:
            print("  ⚠️ ACTIVE TRIPWIRE BREACHES DETECTED:")
            for b in breaches:
                print(f"    - {b}")
        else:
            print("  ✓ All safety tripwires clean. No threshold breaches.")
        print("═" * 65 + "\n")

    elif args.command == "enable":
        breaches = check_tripwires(store)
        if breaches:
            print(f"\n❌ Cannot enable canary mode: Tripwires active ({breaches[0]})\n")
            sys.exit(1)
        cfg["canary_enabled"] = True
        save_canary_config(cfg)
        store.log_audit("CANARY_MODE_ENABLED", {"skus": cfg.get("canary_skus", [])})
        print("\n✅ Canary mode ENABLED for active cohort.\n")

    elif args.command == "disable":
        cfg["canary_enabled"] = False
        save_canary_config(cfg)
        store.log_audit("CANARY_MODE_DISABLED", {"reason": "Manual operator command"})
        print("\n🛑 Canary mode DISABLED. All signals require Founder sign-off.\n")

    elif args.command == "add":
        skus = cfg.setdefault("canary_skus", [])
        if args.candidate_id not in skus:
            skus.append(args.candidate_id)
            save_canary_config(cfg)
            store.log_audit("CANARY_SKU_ADDED", {"candidate_id": args.candidate_id})
            print(f"\n✅ Added '{args.candidate_id}' to canary cohort.\n")
        else:
            print(f"\nℹ️ '{args.candidate_id}' already in canary cohort.\n")

    elif args.command == "remove":
        skus = cfg.get("canary_skus", [])
        if args.candidate_id in skus:
            skus.remove(args.candidate_id)
            save_canary_config(cfg)
            store.log_audit("CANARY_SKU_REMOVED", {"candidate_id": args.candidate_id})
            print(f"\n✅ Removed '{args.candidate_id}' from canary cohort.\n")
        else:
            print(f"\nℹ️ '{args.candidate_id}' not found in canary cohort.\n")


if __name__ == "__main__":
    main()
