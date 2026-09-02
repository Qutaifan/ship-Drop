"""Background Worker Daemon for Supplier Verification and Continuous Drift Scanning."""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from agency.bots.supplier_drift_detector import SupplierDriftDetector
from agency.bots.supplier_verification_bot import SupplierVerificationBot
from agency.core.provenance import sign_payload
from agency.core.store import Store

FEATURE_FLAGS_FILE = ROOT / "config" / "feature_flags.json"


def get_feature_flags() -> dict:
    if FEATURE_FLAGS_FILE.exists():
        try:
            with FEATURE_FLAGS_FILE.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "auto_drift_actions": False,
        "quarantine_mode": True,
        "verification_worker_enabled": True,
    }


class SupplierWorkerDaemon:
    def __init__(
        self,
        store: Store,
        verify_interval: int = 14400,  # 4 hours
        drift_interval: int = 3600,     # 1 hour
    ) -> None:
        self.store = store
        self.verify_bot = SupplierVerificationBot(store)
        self.drift_detector = SupplierDriftDetector(store)
        self.verify_interval = verify_interval
        self.drift_interval = drift_interval
        self.last_verify_time = 0.0
        self.last_drift_time = 0.0

    def run_verification_cycle(self) -> int:
        """Run candidate supplier verification with exponential backoff & jitter on retries."""
        flags = get_feature_flags()
        if not flags.get("verification_worker_enabled", True):
            print("  [Worker] Supplier verification worker is disabled by feature flag.")
            return 0

        print(f"\n[{datetime.now(timezone.utc).isoformat()}] 🏭 Starting scheduled Supplier Verification cycle...")
        candidates = self.store.list_candidates()
        count = 0
        for cand in candidates:
            cid = cand.get("candidate_id")
            if not cid:
                continue

            max_retries = 3
            backoff_base = 1.5
            for attempt in range(max_retries):
                try:
                    res = self.verify_bot.verify_candidate_supplier(cid)
                    # Sign verification payload for provenance
                    sig = sign_payload(res)
                    res["hmac_signature"] = sig
                    self.store.save_supplier_verification(res)
                    count += 1
                    break
                except Exception as e:
                    # Exponential backoff with random jitter: (1.5 ^ attempt) + random(0, 1)
                    jitter = random.uniform(0.1, 1.0)
                    delay = (backoff_base ** attempt) + jitter
                    print(f"  ⚠️ Verification attempt {attempt + 1} failed for {cid}: {e}. Retrying in {delay:.2f}s...")
                    time.sleep(delay)

        self.store.log_audit("WORKER_VERIFICATION_CYCLE_COMPLETED", {"verified_count": count})
        print(f"  ✅ Verified {count} candidate supplier(s).\n")
        return count

    def run_drift_scan_cycle(self) -> int:
        """Run continuous supplier drift detector."""
        print(f"\n[{datetime.now(timezone.utc).isoformat()}] 🚨 Starting scheduled Supplier Drift Scan cycle...")
        drift_signals = self.drift_detector.scan_and_emit_signals()
        flags = get_feature_flags()
        auto_actions = flags.get("auto_drift_actions", False)

        from agency.notifications.drift_notifier import DriftNotifier
        notifier = DriftNotifier()

        for sig in drift_signals:
            print(f"  • Drift detected for {sig['product_name']}: [{sig['severity']}] -> {sig['signal_data']['action_plan']['recommended_action']}")
            if auto_actions:
                print(f"    [Auto-Action Active] Proposed signal {sig['signal_id']} routed to executor.")
            else:
                print(f"    [Founder Gate Active] Proposed signal {sig['signal_id']} queued for Ahmad's review.")
            notifier.dispatch(sig)

        self.store.log_audit("WORKER_DRIFT_SCAN_CYCLE_COMPLETED", {
            "alerts_count": len(drift_signals),
            "auto_actions": auto_actions,
        })
        print(f"  ✅ Drift scan complete. {len(drift_signals)} alert(s) detected.\n")
        return len(drift_signals)

    def start(self, run_once: bool = False) -> None:
        """Start the worker loop or run once."""
        print("═" * 70)
        print("  🚀 HERMES SUPPLIER INTELLIGENCE WORKER DAEMON")
        print(f"  Verification Interval: {self.verify_interval}s ({self.verify_interval // 3600}h)")
        print(f"  Drift Scan Interval  : {self.drift_interval}s ({self.drift_interval // 3600}h)")
        print("═" * 70)

        if run_once:
            self.run_verification_cycle()
            self.run_drift_scan_cycle()
            print("✨ Worker single-cycle run complete.")
            return

        while True:
            now = time.time()
            # Verification cycle
            if now - self.last_verify_time >= self.verify_interval:
                self.run_verification_cycle()
                self.last_verify_time = now

            # Drift scan cycle
            if now - self.last_drift_time >= self.drift_interval:
                self.run_drift_scan_cycle()
                self.last_drift_time = now

            # Sleep between checks (10s resolution)
            time.sleep(10)


def main() -> None:
    parser = argparse.ArgumentParser(description="Hermes Supplier Intelligence Background Worker")
    parser.add_argument("--once", action="store_true", help="Run a single cycle and exit (ideal for cron)")
    parser.add_argument("--verify-interval", type=int, default=14400, help="Verification interval in seconds (default: 14400 = 4h)")
    parser.add_argument("--drift-interval", type=int, default=3600, help="Drift scan interval in seconds (default: 3600 = 1h)")
    args = parser.parse_args()

    store = Store()
    daemon = SupplierWorkerDaemon(
        store=store,
        verify_interval=args.verify_interval,
        drift_interval=args.drift_interval,
    )
    try:
        daemon.start(run_once=args.once)
    except KeyboardInterrupt:
        print("\n🛑 Worker daemon gracefully stopped.")


if __name__ == "__main__":
    main()
