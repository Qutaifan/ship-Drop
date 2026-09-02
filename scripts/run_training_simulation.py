"""Hermes-Ecom Full Autonomous Training Run: Sourcing to Global Portfolio."""
from __future__ import annotations

import subprocess
import sys

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

CAND = "cand-cj-sku-magnetic-cord-6p"
SUP = "cj-dropshipping-us-domestic-hub"
SKU = "SKU-MAGNETIC-01"

COMMANDS = [
    ("Step 1: Live CJ Domestic Warehouse Telemetry Ingestion", [
        sys.executable, "-m", "agency.cli", "cj:ingest", "--supplier", SUP, "--sku", SKU, "--candidate", CAND, "--save"
    ]),
    ("Step 2: Meta Ad Library DSA Commercial Competitor Ingestion", [
        sys.executable, "-m", "agency.cli", "dsa:ingest", "--candidate", CAND, "--query", "magnetic cable organizer", "--save"
    ]),
    ("Step 3: Dynamic Pricing Optimization under CAC Gate & Competitor Anchor", [
        sys.executable, "-m", "agency.cli", "pricing:optimize", "--candidate", CAND, "--save"
    ]),
    ("Step 4: Sourcing Supplier Ranking & Allocation", [
        sys.executable, "-m", "agency.cli", "sourcing:rank", "--candidate", CAND
    ]),
    ("Step 5: Real DSA + CJ Demand Forecasting", [
        sys.executable, "-m", "agency.cli", "demand:forecast", "--candidate", CAND, "--spend", "60"
    ]),
    ("Step 6: Supplier Volume Negotiation Simulation", [
        sys.executable, "-m", "agency.cli", "sourcing:negotiate", "--supplier", SUP, "--sku", SKU, "--volume", "250"
    ]),
    ("Step 7: Global Portfolio Optimization", [
        sys.executable, "-m", "agency.cli", "portfolio:optimize", "--budget", "3500"
    ]),
]

def main() -> None:
    print("=" * 80)
    print("🚀 HERMES-ECOM AUTONOMOUS TRAINING RUN: SOURCING TO GLOBAL PORTFOLIO")
    print("=" * 80)

    for title, cmd in COMMANDS:
        print(f"\n>>> {title}")
        ret = subprocess.run(cmd)
        if ret.returncode != 0:
            print(f"❌ Error executing: {' '.join(cmd)}")
            sys.exit(ret.returncode)

    print("=" * 80)
    print("✨ TRAINING RUN COMPLETE — ALL PIPES GROUNDED IN LIVE DATA")
    print("=" * 80)

if __name__ == "__main__":
    main()
