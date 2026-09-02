"""Autonomous Pipeline Runner - Executes the full multi-bot research, analysis, scoring, and trade recommendation loop."""
from __future__ import annotations

import datetime
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from agency.bots.analyst_bot import AnalystBot
from agency.bots.risk_bot import RiskBot
from agency.bots.scout_bot import ScoutBot
from agency.bots.sentiment_bot import SentimentBot
from agency.bots.supplier_bot import SupplierBot
from agency.bots.tracker_bot import TrackerBot
from agency.bots.trader_bot import TraderBot
from agency.core.scoring_engine import ScoringEngine
from agency.core.store import Store


def run_intelligence_pipeline() -> None:
    store = Store()
    engine = ScoringEngine()

    print("\n" + "=" * 80)
    print("  🚀 INITIATING AUTONOMOUS DROPSHIP PROFIT INTELLIGENCE PIPELINE")
    print("=" * 80)

    # 1. SupplierBot: Register and evaluate baseline suppliers
    print("\n[Step 1/6] 🏭 SupplierBot: Evaluating supplier fulfillment networks...")
    sup_bot = SupplierBot(store, engine)
    sup_bot.register_supplier(
        supplier_id="cj-us-warehouse-01",
        supplier_name="CJ Dropshipping US East Warehouse (NJ/CA)",
        platform="cjdropshipping",
        warehouse_country="US",
        origin_country="CN",
        reliability_rating=4.8,
        dispute_rate_percent=1.2,
        processing_days=1,
        shipping_min_days=3,
        shipping_max_days=6,
        shipping_tiers=[
            {"carrier": "USPS", "service_name": "USPS Ground Advantage", "base_cost": 4.85, "currency": "USD", "tracked": True},
            {"carrier": "USPS", "service_name": "Priority Mail", "base_cost": 8.95, "currency": "USD", "tracked": True},
        ],
        notes="US domestic inventory; avoids international customs and de minimis fees.",
    )
    sup_bot.register_supplier(
        supplier_id="cj-eu-warehouse-01",
        supplier_name="CJ Dropshipping Germany Warehouse (Frankfurt)",
        platform="cjdropshipping",
        warehouse_country="DE",
        origin_country="CN",
        reliability_rating=4.7,
        dispute_rate_percent=1.5,
        processing_days=2,
        shipping_min_days=2,
        shipping_max_days=5,
        shipping_tiers=[
            {"carrier": "DHL", "service_name": "DHL Paket Domestic", "base_cost": 5.20, "currency": "EUR", "tracked": True},
            {"carrier": "Hermes", "service_name": "Hermes Standard", "base_cost": 4.60, "currency": "EUR", "tracked": True},
        ],
        notes="EU warehouse; bypasses the 1 July 2026 EUR 3 flat import duty on China direct imports.",
    )
    print(f"  ✓ Registered and scored {len(store.list_suppliers())} fulfillment hubs.")

    # 2. ScoutBot: Discover and ingest candidates
    print("\n[Step 2/6] 🔍 ScoutBot: Scanning product dossiers and market libraries...")
    scout_bot = ScoutBot(store)
    candidates = scout_bot.scan_all_existing()
    print(f"  ✓ Discovered and normalized {len(candidates)} candidate products.")

    # 3. AnalystBot: Quantitative margins & CAC gates
    print("\n[Step 3/6] 📈 AnalystBot: Running True Margin Matrix and CAC validation...")
    analyst_bot = AnalystBot(store, engine)
    analyst_results = analyst_bot.analyze_all()
    print(f"  ✓ Evaluated unit economics for {len(analyst_results)} candidates.")

    # 4. SentimentBot & RiskBot: Demand proof burden & compliance audit
    print("\n[Step 4/6] 🛡️ RiskBot & SentimentBot: Auditing compliance and proof burden...")
    risk_bot = RiskBot(store, engine)
    risk_results = risk_bot.audit_all()

    sentiment_bot = SentimentBot(store, engine)
    sentiment_results = sentiment_bot.evaluate_all()
    print(f"  ✓ Audited {len(risk_results)} candidates for customs, return risks, and skeptic ratios.")

    # 5. TrackerBot: Market saturation & health check
    print("\n[Step 5/6] 📡 TrackerBot: Monitoring competitor longevity and saturation...")
    tracker_bot = TrackerBot(store)
    alerts = tracker_bot.monitor_all()
    if alerts:
        print(f"  ⚠️ {len(alerts)} candidate health alert(s) detected:")
        for a in alerts:
            for trig in a["active_triggers"]:
                print(f"     - [{trig['severity']}] {a['product_name']}: {trig['message']}")
    else:
        print("  ✓ No critical saturation or health alerts detected.")

    # 6. TraderBot: Generate Trade Recommendation Signals
    print("\n[Step 6/6] 🎯 TraderBot: Generating actionable trade recommendation signals...")
    trader_bot = TraderBot(store, engine)
    signals = trader_bot.evaluate_all()
    print(f"  ✓ Generated {len(signals)} trade recommendation signals.")

    # Executive Output Summary
    print("\n" + "=" * 80)
    print("  🏆 EXECUTIVE OPPORTUNITY LEADERBOARD")
    print("=" * 80)
    print(f"  {'Product Name':<32} {'Opp Score':<11} {'Profit':<8} {'Risk':<8} {'Verdict':<12} {'Signal'}")
    print("-" * 80)

    for c in store.list_candidates():
        scores = engine.score_candidate(c, store.list_suppliers()[0])
        sig = next((s for s in signals if s["candidate_id"] == c["candidate_id"]), None)
        sig_type = sig["signal_type"] if sig else "NONE"
        print(
            f"  {c['product_name'][:31]:<32} "
            f"{scores.opportunity_score:<11.1f} "
            f"{scores.profit_score:<8.1f} "
            f"{scores.risk_score:<8.1f} "
            f"{scores.verdict:<12} "
            f"{sig_type}"
        )
    print("=" * 80)
    print("\n  👉 Use 'python -m agency.cli signals' to view signal briefs.")
    print("  👉 Use 'python -m agency.cli approve <signal_id>' to authorize a test.")
    print("  👉 Human-in-the-loop protection: No ad spend or order submission can occur without Ahmad's approval.\n")


if __name__ == "__main__":
    run_intelligence_pipeline()
