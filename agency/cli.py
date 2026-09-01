"""Dropship Agency CLI - Autonomous Profit Intelligence & Human-in-the-Loop Trade Terminal."""
from __future__ import annotations

import argparse
import json
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
from agency.bots.supplier_drift_detector import SupplierDriftDetector
from agency.bots.supplier_verification_bot import SupplierVerificationBot
from agency.bots.tracker_bot import TrackerBot
from agency.bots.trader_bot import TraderBot
from agency.core.margin_reconciler import MarginReconciler
from agency.core.scoring_engine import ScoringEngine
from agency.core.store import Store
from agency.governance.approval_ledger import ApprovalLedger
from agency.governance.execution_gateway import ExecutionGateway
from agency.governance.policy_engine import PolicyEngine


def cmd_status(store: Store, args: argparse.Namespace) -> None:
    candidates = store.list_candidates()
    suppliers = store.list_suppliers()
    signals = store.list_signals()
    approvals = store.list_approvals()
    audits = store.get_audit_trail(limit=5)

    print("\n" + "=" * 65)
    print("  🚀 DROPSHIP PROFIT INTELLIGENCE SYSTEM — OPERATING STATUS")
    print("=" * 65)
    print(f"  • Ingested Candidates : {len(candidates)}")
    print(f"  • Verified Suppliers   : {len(suppliers)}")
    print(f"  • Active Trade Signals : {len(signals)}")
    pending_signals = [s for s in signals if s.get("approval_status") == "PENDING_FOUNDER_REVIEW"]
    print(f"    - Pending Founder Review : {len(pending_signals)}")
    print(f"  • Recorded Approvals   : {len(approvals)}")
    approved_count = len([a for a in approvals if a.get("status") == "APPROVED"])
    print(f"    - Active Approved Tokens : {approved_count}")
    print("=" * 65)

    if pending_signals:
        print("\n  ⚠️  PENDING SIGNALS REQUIRING AHMAD REVIEW:")
        for s in pending_signals:
            print(f"    [{s['signal_type']}] {s['signal_id']}: {s['product_name']} (Score: {s['scores']['opportunity_score']})")

    print("\n  🛡️  RECENT AUDIT TRAIL (Last 5 events):")
    for event in audits:
        print(f"    {event['timestamp'][:19]} | {event['event_type']} | {json.dumps(event['details'])[:60]}...")
    print("=" * 65 + "\n")


def cmd_scan(store: Store, args: argparse.Namespace) -> None:
    print("\n🔍 ScoutBot: Scanning product dossiers and candidate databases...")
    scout = ScoutBot(store)

    if getattr(args, "query", None):
        print(f"  Querying CJ Domestic Catalog for: '{args.query}' (Warehouse: {args.warehouse})...")
        items = scout.search_cj_catalog(args.query, warehouse=args.warehouse)
        print(f"  Found {len(items)} catalog match(es). Ingesting...")
        for item in items:
            cand = scout.ingest_catalog_candidate(item)
            print(f"  ✓ Ingested: [{cand['candidate_id']}] {cand['product_name']} (${cand['unit_economics']['gross_selling_price']})")
        print()
        return

    discovered = scout.scan_all_existing()
    print(f"✅ Discovered & Normalized {len(discovered)} product candidates into store.\n")
    for c in discovered:
        print(f"  - [{c['candidate_id']}] {c['product_name']} ({c['market_config_id']}) -> Status: {c['status']}")


def cmd_score(store: Store, args: argparse.Namespace) -> None:
    engine = ScoringEngine()
    candidates = store.list_candidates()
    suppliers = store.list_suppliers()

    print("\n" + "=" * 82)
    print("  📊 OPPORTUNITY SCORING MATRIX (Profit, Risk, Trend, Opportunity)")
    print("=" * 82)
    print(f"  {'Candidate ID':<35} {'Profit':<8} {'Risk':<8} {'Trend':<8} {'Opp Score':<11} {'Verdict':<10}")
    print("-" * 82)

    for c in candidates:
        matching_sup = suppliers[0] if suppliers else None
        scores = engine.score_candidate(c, matching_sup)
        print(
            f"  {c['candidate_id'][:34]:<35} "
            f"{scores.profit_score:<8.1f} "
            f"{scores.risk_score:<8.1f} "
            f"{scores.trend_score:<8.1f} "
            f"{scores.opportunity_score:<11.1f} "
            f"{scores.verdict:<10}"
        )
    print("=" * 82 + "\n")


def cmd_signals(store: Store, args: argparse.Namespace) -> None:
    signals = store.list_signals(status=args.status, signal_type=args.type)
    print("\n" + "=" * 85)
    print(f"  🎯 TRADE RECOMMENDATION SIGNALS ({len(signals)} found)")
    print("=" * 85)
    for s in signals:
        h = s.get("hypothesis", {})
        print(f"  ID       : {s['signal_id']}")
        print(f"  Type     : {s['signal_type']} | Market: {s['target_market']} | Confidence: {s['confidence']}")
        print(f"  Product  : {s['product_name']} ({s['candidate_id']})")
        print(f"  Scores   : Opp={s['scores']['opportunity_score']} | Profit={s['scores']['profit_score']} | Risk={s['scores']['risk_score']}")
        print(f"  Forecast : CTR={h.get('predicted_ctr_percent')}% | CVR={h.get('predicted_cvr_percent')}% | CPA=${h.get('predicted_cpa'):.2f} | Net=${h.get('predicted_net_margin'):.2f}")
        print(f"  Action   : {s['action_plan']['recommended_action']}")
        print(f"  Status   : {s['approval_status']}")
        print("-" * 85)
    print()


def cmd_propose(store: Store, args: argparse.Namespace) -> None:
    trader = TraderBot(store)
    signal = trader.generate_recommendation(args.candidate_id)
    if signal:
        print(f"\n✅ Trade Proposal generated: {signal['signal_id']}")
        print(f"   Product : {signal['product_name']}")
        print(f"   Type    : {signal['signal_type']}")
        print(f"   Status  : {signal['approval_status']}")
        print(f"   Action  : {signal['action_plan']['recommended_action']}\n")
    else:
        print(f"❌ Failed to generate signal for {args.candidate_id}")


def cmd_review(store: Store, args: argparse.Namespace) -> None:
    """Walks through pending trade signals interactively for founder approval."""
    signals = store.list_signals(status="PENDING_FOUNDER_REVIEW")
    if not signals:
        print("\n✨ No trade signals pending founder review.\n")
        return

    print("\n" + "═" * 72)
    print(f"  🎯 INTERACTIVE FOUNDER TRADE REVIEW ({len(signals)} pending signals)")
    print("═" * 72)

    ledger = ApprovalLedger(store)
    for idx, signal in enumerate(signals, 1):
        h = signal.get("hypothesis", {})
        budget = float(h.get("target_ad_budget", 300.0))
        print(f"\n[{idx}/{len(signals)}] Signal: {signal['signal_id']}")
        print(f"  Product     : {signal.get('product_name')}")
        print(f"  Type        : {signal.get('signal_type')} (Market: {signal.get('target_market')})")
        print(f"  Scores      : Opp={signal['scores']['opportunity_score']} | Profit={signal['scores']['profit_score']} | Risk={signal['scores']['risk_score']}")
        print(f"  Forecast    : CTR={h.get('predicted_ctr_percent')}% | CVR={h.get('predicted_cvr_percent')}% | CPA=${h.get('predicted_cpa'):.2f} | Net=${h.get('predicted_net_margin'):.2f}")
        print(f"  Target Spend: ${budget:.2f}")
        print(f"  Action      : {signal.get('action_plan', {}).get('recommended_action')}")

        if not sys.stdin.isatty():
            print("  [Non-interactive terminal — skipping prompt]")
            continue

        try:
            choice = input("\n  Decision for Ahmad: [A]pprove / [R]eject / [S]kip / [Q]uit? ").strip().lower()
            if choice == "a":
                appr = ledger.approve_trade_signal(signal["signal_id"], approver="Ahmad", max_budget_override=budget)
                print(f"  ✅ Approved: {appr['approval_id']} (Hash: {appr['verification_hash'][:24]}...)")
            elif choice == "r":
                reason = input("  Rejection reason: ").strip() or "Rejected during founder review."
                ledger.reject_trade_signal(signal["signal_id"], reason)
                print(f"  🚫 Rejected: {signal['signal_id']}")
            elif choice == "q":
                print("  Review session ended.\n")
                break
            else:
                print("  Skipped.")
        except (KeyboardInterrupt, EOFError):
            print("\n  Review session aborted.\n")
            break


def cmd_approve(store: Store, args: argparse.Namespace) -> None:
    approver = args.by or "Ahmad"
    ledger = ApprovalLedger(store)
    signal = store.get_signal(args.signal_id)
    if not signal:
        print(f"\n❌ Signal '{args.signal_id}' not found.")
        sys.exit(1)

    h = signal.get("hypothesis", {})
    budget = args.budget or float(h.get("target_ad_budget", 300.0))

    # Review Summary Display
    print("\n" + "═" * 68)
    print("  📋 FOUNDER TRADE APPROVAL GATE")
    print("═" * 68)
    print(f"  Signal ID   : {signal['signal_id']}")
    print(f"  Product     : {signal.get('product_name')}")
    print(f"  Signal Type : {signal.get('signal_type')} (Confidence: {signal.get('confidence')})")
    print(f"  Forecast    : CTR={h.get('predicted_ctr_percent')}% | CVR={h.get('predicted_cvr_percent')}% | CPA=${h.get('predicted_cpa'):.2f} | Net=${h.get('predicted_net_margin'):.2f}")
    print(f"  Target Spend: ${budget:.2f} {signal.get('target_market', 'USD')}")
    print(f"  Action      : {signal.get('action_plan', {}).get('recommended_action')}")
    print("═" * 68)

    # Interactive confirmation prompt if not bypassed with --yes
    if not getattr(args, "yes", False) and sys.stdin.isatty():
        try:
            confirm = input(f"\nAuthorize live execution as Founder '{approver}'? [y/N]: ").strip().lower()
            if confirm not in ["y", "yes"]:
                print("❌ Authorization aborted by founder.\n")
                return
        except (KeyboardInterrupt, EOFError):
            print("\n❌ Authorization cancelled.\n")
            return

    try:
        approval = ledger.approve_trade_signal(args.signal_id, approver=approver, max_budget_override=budget)
        print("\n" + "=" * 65)
        print("  ✅ TRADE PROPOSAL APPROVED BY FOUNDER")
        print("=" * 65)
        print(f"  Approval ID : {approval['approval_id']}")
        print(f"  Signal ID   : {args.signal_id}")
        print(f"  Approved By : {approval['approved_by']} at {approval['approved_at']}")
        print(f"  Max Budget  : ${approval['scope']['max_budget']:.2f} {approval['scope']['currency']}")
        print(f"  Hash Token  : {approval['verification_hash']}")
        print("  Constraints :")
        for c in approval["constraints"]:
            print(f"    - {c}")
        print("=" * 65 + "\n")
    except Exception as e:
        print(f"\n❌ Approval failed: {e}\n")
        sys.exit(1)


def cmd_reject(store: Store, args: argparse.Namespace) -> None:
    ledger = ApprovalLedger(store)
    reason = args.reason or "Rejected by founder review."
    signal = ledger.reject_trade_signal(args.signal_id, reason)
    print(f"\n🚫 Signal {args.signal_id} marked REJECTED. Reason: {reason}\n")


def cmd_execute(store: Store, args: argparse.Namespace) -> None:
    signal = store.get_signal(args.signal_id)
    if not signal:
        print(f"❌ Signal {args.signal_id} not found.")
        sys.exit(1)

    appr_id = signal.get("approval_id")
    gateway = ExecutionGateway(store)

    action = "test_campaign_launch" if signal.get("signal_type") == "BUY" else "campaign_publication"
    spend = float(signal.get("hypothesis", {}).get("target_ad_budget", 50.0))

    print(f"\n🚀 Attempting execution for signal '{args.signal_id}'...")
    res = gateway.execute_live_action(
        action=action,
        object_id=signal.get("candidate_id", ""),
        requested_by=signal.get("created_by", "trader_bot"),
        requested_spend=spend,
        approval_id=appr_id,
        live_mode=args.live,
    )

    if res["success"]:
        print(f"✅ EXECUTION SUCCESSFUL [{res['mode']}]")
        print(f"   Execution ID : {res['execution_id']}")
        print(f"   Authorized By: {res['authorized_by']}")
        print(f"   Action       : {res['action']}")
        print(f"   Message      : {res['message']}\n")
    else:
        print(f"🛑 EXECUTION BLOCKED BY GOVERNANCE GATEWAY")
        print(f"   Reason : {res['reason']}")
        print("   Status : Safe autonomous hold enforced.\n")
        sys.exit(1)


def cmd_audit(store: Store, args: argparse.Namespace) -> None:
    print("\n" + "=" * 65)
    print("  🛡️  MCP GOVERNANCE & SECURITY AUDIT")
    print("=" * 65)
    policy = PolicyEngine(store)
    ledger = ApprovalLedger(store)

    # 1. Check Tool Access Policy
    print("  [1/3] Auditing Tool Access Tiers...")
    test_cases = [
        ("write_candidate_doc", "autonomous_agent", None, True),
        ("web_search", "autonomous_agent", None, True),
        ("ad_spend", "unapproved_agent", None, False),  # must be blocked
        ("supplier_order_submission", "unapproved_agent", None, False),  # must be blocked
    ]
    tier_errors = 0
    for action, req_by, appr, expected in test_cases:
        permitted, reason = policy.is_action_permitted(action, req_by, appr)
        if permitted != expected:
            print(f"    ❌ FAILED: action '{action}' expected permitted={expected}, got {permitted}")
            tier_errors += 1
        else:
            print(f"    ✓ Passed: '{action}' correctly {'permitted' if expected else 'blocked'}")

    # 2. Check Cryptographic Hash Integrity of Approvals
    print("\n  [2/3] Verifying Approval Ledger Cryptographic Integrity...")
    hash_errors = 0
    approvals = store.list_approvals()
    for a in approvals:
        if not ledger.verify_hash(a):
            print(f"    ❌ TAMPER DETECTED in approval {a['approval_id']}")
            hash_errors += 1
        else:
            print(f"    ✓ Intact: {a['approval_id']} (Signed by {a['approved_by']})")

    # 3. Check Live Risk Limits
    print("\n  [3/3] Auditing Live Risk & De-Minimis Guardrails...")
    market_config = ROOT / "config" / "markets" / "us-pilot.json"
    if market_config.exists():
        with market_config.open("r", encoding="utf-8") as f:
            m_data = json.load(f)
            limits = m_data.get("live_risk_limits", {})
            if any(limits.values()):
                print("    ❌ Live risk limits enabled in config!")
            else:
                print("    ✓ All live risk limits are safely set to FALSE")

    print("=" * 65)
    if tier_errors == 0 and hash_errors == 0:
        print("  🎉 AUDIT RESULT: CLEAN & SECURE (Human-in-the-loop enforced)")
    else:
        print(f"  ❌ AUDIT RESULT: FAILED ({tier_errors} tier errors, {hash_errors} hash errors)")
        sys.exit(1)
    print("=" * 65 + "\n")


def cmd_verify(store: Store, args: argparse.Namespace) -> None:
    bot = SupplierVerificationBot(store)
    if args.candidate_id:
        print(f"\n🔍 Auditing supplier reality for: {args.candidate_id}...")
        res = bot.verify_candidate_supplier(args.candidate_id)
        print("\n" + "═" * 65)
        print("  🏭 SUPPLIER REALITY AUDIT REPORT")
        print("═" * 65)
        print(f"  Verification ID : {res['verification_id']}")
        print(f"  Candidate ID    : {res['candidate_id']}")
        print(f"  Supplier / SKU  : {res['supplier_id']} ({res['sku']})")
        print(f"  Stock Level     : {res['stock_level']} units in {res['warehouse_country']} ({res['warehouse_type']})")
        print(f"  Quoted vs Real  : Product ${res['quoted_product_cost']:.2f} -> ${res['verified_product_cost']:.2f} (Drift: {res['price_drift_percent']:+.1%})")
        print(f"  Shipping        : ${res['verified_shipping_cost']:.2f} via {res['shipping_method']} ({res['lead_days_min']}-{res['lead_days_max']} days)")
        print(f"  Packaging Grade : {res['packaging_type']} | Defect Rate: {res['defect_rate_percent']}%")
        print(f"  Stability Score : {res['stability_score']:.2f} / 1.00 (Confidence: {res['verification_confidence']:.0%})")
        print(f"  Status Verdict  : {res['status']}")
        print(f"  Notes           : {res['verification_notes']}")
        print("═" * 65 + "\n")
    else:
        print("\n🔍 Auditing supplier reality across all candidates...")
        results = bot.verify_all_candidates()
        print(f"✅ Verified {len(results)} candidate supplier(s).\n")
        print(f"  {'Candidate ID':<34} {'Stock':<8} {'Route':<14} {'Stability':<10} {'Status':<16}")
        print("-" * 84)
        for r in results:
            route_str = f"{r['warehouse_country']} ({r['warehouse_type'][:3]})"
            print(f"  {r['candidate_id'][:33]:<34} {r['stock_level']:<8} {route_str:<14} {r['stability_score']:<10.2f} {r['status']:<16}")
        print()


def cmd_reconcile(store: Store, args: argparse.Namespace) -> None:
    candidate = store.get_candidate(args.candidate_id)
    if not candidate:
        print(f"\n❌ Candidate '{args.candidate_id}' not found.")
        sys.exit(1)

    latest_ver = store.get_latest_verification_for_candidate(args.candidate_id)
    if not latest_ver:
        print(f"\n⚠️ No prior verification found for '{args.candidate_id}'. Running live verification first...")
        bot = SupplierVerificationBot(store)
        latest_ver = bot.verify_candidate_supplier(args.candidate_id)

    reconciler = MarginReconciler()
    res = reconciler.reconcile_candidate(candidate, latest_ver)
    rec = res["reconciled_economics"]
    init = res["initial_economics"]

    print("\n" + "═" * 70)
    print(f"  💰 MARGIN RECONCILIATION REPORT: {candidate.get('product_name')}")
    print("═" * 70)
    print(f"  Status Verdict         : {res['status']}")
    print(f"  Compression Warning    : {'⚠️ COMPRESSION FLAGGED' if res['compression_flag'] else '✓ MARGIN SAFE'}")
    print(f"  Net Margin Delta       : {res['margin_delta']:+.2f} {rec['currency']}")
    print("-" * 70)
    print(f"  {'Metric':<28} {'Theoretical':<18} {'Verified & Buffered':<20}")
    print("-" * 70)
    init_prod = float(init.get('initial_product_cost') or 0.0)
    init_ship = float(init.get('initial_shipping_cost') or 0.0)
    init_margin = float(init.get('initial_net_margin') or 0.0)
    print(f"  {'Product Sourcing Cost':<28} ${init_prod:<17.2f} ${rec['verified_product_cost']:<19.2f}")
    print(f"  {'Shipping & Carrier':<28} ${init_ship:<17.2f} ${rec['verified_shipping_cost']:<19.2f}")
    print(f"  {'Packaging Uplift':<28} ${0.00:<17.2f} ${rec['packaging_uplift']:<19.2f}")
    print(f"  {'Total Landed Cost':<28} ${init_prod + init_ship:<17.2f} ${rec['total_landed_cost']:<19.2f}")
    print(f"  {'Net Margin Per Order':<28} ${init_margin:<17.2f} ${rec['reconciled_net_margin']:<19.2f}")
    print(f"  {'COGS Multiple':<28} {'—':<18} {rec['cogs_multiple']:<19.2f}x")
    print(f"  {'Break-Even CPA':<28} {'—':<18} ${rec['break_even_cpa']:<19.2f}")
    print(f"  {'Expected ROAS':<28} {'—':<18} {rec['expected_roas']:<19.2f}x")
    print("═" * 70 + "\n")


def cmd_drift(store: Store, args: argparse.Namespace) -> None:
    detector = SupplierDriftDetector(store)
    drift_events = detector.scan_and_emit_signals()

    if getattr(args, "json", False):
        print(json.dumps(drift_events, indent=2))
        return

    print("\n" + "═" * 75)
    print(f"  🚨 CONTINUOUS SUPPLIER DRIFT MONITOR ({len(drift_events)} alerts detected)")
    print("═" * 75)
    if not drift_events:
        print("  ✓ No supplier drift detected across active candidates. All fulfillment channels stable.")
    else:
        for event in drift_events:
            print(f"\n  • Candidate : {event['product_name']} ({event['candidate_id']})")
            print(f"    Severity  : [{event['severity']}] | Action: {event['signal_data']['signal_type']}")
            print(f"    Signal ID : {event['signal_id']}")
            print("    Drift Flags:")
            for flag in event["flags"]:
                print(f"      - {flag}")
    print("\n" + "═" * 75 + "\n")


def cmd_ver_history(store: Store, args: argparse.Namespace) -> None:
    records = store.list_supplier_verifications(candidate_id=args.candidate_id)
    print("\n" + "═" * 75)
    print(f"  📜 VERIFICATION AUDIT HISTORY: {args.candidate_id} ({len(records)} entries)")
    print("═" * 75)
    if not records:
        print("  No verification records found.")
    else:
        for r in records:
            print(f"  [{r['verified_at'][:19]}] Verification ID: {r['verification_id']} | verified_at: {r['verified_at']} | Status Verdict: {r['status']:<15} | Stock Level: {r['stock_level']:<4} | Stability Score: {r['stability_score']:.2f}")
    print("═" * 75 + "\n")


def cmd_revert_verifications(store: Store, args: argparse.Namespace) -> None:
    cid = args.candidate_id
    count = args.count or 1
    reason = args.reason or "Rollback initiated by operator."
    records = store.list_supplier_verifications(candidate_id=cid, limit=count)
    if not records:
        print(f"\n❌ No verification records found to revert for '{cid}'.\n")
        return

    print(f"\n⚠️ Reverting last {len(records)} verification(s) for candidate '{cid}'...")
    for r in records:
        store.delete_supplier_verification(r["verification_id"])
        print(f"  ✓ Deleted verification: {r['verification_id']} ({r['verified_at'][:19]})")

    store.log_audit("VERIFICATIONS_REVERTED", {
        "candidate_id": cid,
        "count": len(records),
        "reason": reason,
        "actor": getattr(args, "actor", "Founder"),
    })

    # Re-reconcile with new latest if available
    new_latest = store.get_latest_verification_for_candidate(cid)
    cand = store.get_candidate(cid)
    if new_latest and cand:
        rec = MarginReconciler().reconcile_candidate(cand, new_latest)
        print(f"  ✓ Reconciled with previous verified state: Margin ${rec['reconciled_economics']['reconciled_net_margin']:.2f} ({rec['status']})")
    print(f"✅ Reversion complete. Reason logged to audit trail.\n")


def cmd_feature_flag(store: Store, args: argparse.Namespace) -> None:
    ff_path = ROOT / "config" / "feature_flags.json"
    flags: Dict[str, Any] = {}
    if ff_path.exists():
        with ff_path.open("r", encoding="utf-8") as f:
            flags = json.load(f)

    if args.action == "get" or not args.action:
        if getattr(args, "name", None):
            print(f"{args.name}: {flags.get(args.name)}")
        else:
            print("\nActive Feature Flags:")
            for k, v in flags.items():
                print(f"  - {k:<28}: {v}")
            print()
    elif args.action == "set":
        if not args.name or args.value is None:
            print("❌ Error: 'set' requires <name> and <value>.")
            sys.exit(1)
        raw_val = args.value.lower()
        parsed_val: Any = raw_val
        if raw_val in ["true", "1", "yes", "on"]:
            parsed_val = True
        elif raw_val in ["false", "0", "no", "off"]:
            parsed_val = False
        flags[args.name] = parsed_val
        ff_path.parent.mkdir(parents=True, exist_ok=True)
        with ff_path.open("w", encoding="utf-8") as f:
            json.dump(flags, f, indent=2)
        store.log_audit("FEATURE_FLAG_CHANGED", {"flag": args.name, "value": parsed_val, "actor": "Founder"})
        print(f"✅ Feature flag '{args.name}' set to: {parsed_val}\n")


def cmd_approve_signal(store: Store, args: argparse.Namespace) -> None:
    sig = store.get_signal(args.signal_id)
    if not sig:
        print(f"\n❌ Signal '{args.signal_id}' not found.")
        sys.exit(1)

    actor = args.actor or "Founder"
    action = args.action.upper()
    ledger = ApprovalLedger(store)

    if action in ["APPROVE_SUPPLIER_SWITCH", "APPROVE_BUY", "APPROVE"]:
        appr = ledger.approve_trade_signal(args.signal_id, approver="Ahmad")
        print("\n" + "=" * 65)
        print(f"  ✅ SIGNAL APPROVED: {action}")
        print("=" * 65)
        print(f"  Approval ID : {appr['approval_id']}")
        print(f"  Signal ID   : {args.signal_id}")
        print(f"  Actor       : {actor} (Founder sign-off recorded)")
        print(f"  Hash Token  : {appr['verification_hash']}")
        print("=" * 65 + "\n")
    elif action in ["PAUSE_LISTING", "SELL_KILL"]:
        ledger.reject_trade_signal(args.signal_id, f"Listing paused by {actor}")
        cand = store.get_candidate(sig["candidate_id"])
        if cand:
            cand["status"] = "HOLD"
            cand["recommendation"] = "hold"
            cand["rationale"] = f"Listing paused by {actor} (SELL_KILL executed)."
            store.save_candidate(cand)
        print(f"\n🛑 Signal marked REJECTED and product listing placed on HOLD for '{sig.get('product_name')}'.\n")
    elif action in ["DEFER", "QUARANTINE"]:
        sig["approval_status"] = "QUARANTINE_48H"
        store.save_signal(sig)
        store.log_audit("SIGNAL_QUARANTINED", {"signal_id": args.signal_id, "actor": actor, "duration": "48h"})
        print(f"\n⏳ Signal {args.signal_id} deferred to 48-hour quarantine state.\n")
    else:
        print(f"❌ Unknown action: {action}. Use APPROVE_SUPPLIER_SWITCH, PAUSE_LISTING, or DEFER.")
        sys.exit(1)


def cmd_worker(store: Store, args: argparse.Namespace) -> None:
    from agency.workers.supplier_workers import SupplierWorkerDaemon
    daemon = SupplierWorkerDaemon(
        store=store,
        verify_interval=getattr(args, "verify_interval", 14400),
        drift_interval=getattr(args, "drift_interval", 3600),
    )
    daemon.start(run_once=getattr(args, "once", False))


def cmd_rotate_verifications(store: Store, args: argparse.Namespace) -> None:
    from agency.core.provenance import rotate_verifications
    archive_dir = ROOT / "data" / "archives"
    days = getattr(args, "days", 90)
    print(f"\n📦 Archiving and rotating verifications older than {days} days...")
    purged, arc_file = rotate_verifications(store.db_path, retention_days=days, archive_dir=archive_dir)
    store.log_audit("VERIFICATIONS_ROTATED", {"retention_days": days, "purged_count": purged, "archive_file": str(arc_file) if arc_file else None})
    if arc_file:
        print(f"  ✓ Archived {purged} record(s) to: {arc_file}")
    else:
        print(f"  ✓ No records older than {days} days to rotate.")
    print("═" * 65 + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Dropship Agency - Autonomous Intelligence & Trade Terminal")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("status", help="Display agency operational status")
    scan_parser = subparsers.add_parser("scan", help="Scan candidate documents and product databases")
    scan_parser.add_argument("--query", "-q", help="Search CJ domestic catalog for query")
    scan_parser.add_argument("--warehouse", "-w", default="US", help="Target warehouse (US/DE)")

    subparsers.add_parser("score", help="Calculate opportunity scores across all products")
    subparsers.add_parser("review", help="Interactively review and approve pending trade signals")

    # Phase 2 Supplier Intelligence Commands
    ver_parser = subparsers.add_parser("verify", help="Audit supplier reality for a candidate")
    ver_parser.add_argument("candidate_id", nargs="?", help="Target candidate ID (optional: runs all if omitted)")

    rec_parser = subparsers.add_parser("reconcile", help="Reconcile theoretical margins with verified landed costs")
    rec_parser.add_argument("candidate_id", help="Target candidate ID")

    drift_parser = subparsers.add_parser("drift", help="Scan for supplier price/stock/route drift")
    drift_parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    hist_parser = subparsers.add_parser("ver-history", help="Show chronological supplier verification log")
    hist_parser.add_argument("candidate_id", help="Target candidate ID")

    # Emergency & Triage Commands
    revert_parser = subparsers.add_parser("revert-verifications", help="Revert last N verifications for a candidate")
    revert_parser.add_argument("candidate_id", help="Candidate ID to revert")
    revert_parser.add_argument("--count", "-n", type=int, default=1, help="Number of verifications to delete")
    revert_parser.add_argument("--reason", default="Rollback initiated by operator", help="Audit justification")
    revert_parser.add_argument("--actor", default="Founder", help="Operator actor name")

    ff_parser = subparsers.add_parser("feature-flag", help="Manage operational feature flags")
    ff_parser.add_argument("action", choices=["get", "set"], help="Action: get or set")
    ff_parser.add_argument("name", nargs="?", help="Feature flag name")
    ff_parser.add_argument("value", nargs="?", help="Value to set (true/false)")

    appr_sig_parser = subparsers.add_parser("approve-signal", help="Founder triage approval for a specific signal")
    appr_sig_parser.add_argument("signal_id", help="Signal ID to triage")
    appr_sig_parser.add_argument("--action", required=True, help="Action: APPROVE_SUPPLIER_SWITCH | PAUSE_LISTING | DEFER")
    appr_sig_parser.add_argument("--actor", default="Founder", help="Approving actor (default: Founder)")

    # Worker Daemon & Archival Commands
    worker_parser = subparsers.add_parser("worker", help="Start background supplier verification and drift worker")
    worker_parser.add_argument("--once", action="store_true", help="Run a single cycle and exit (for cron/testing)")
    worker_parser.add_argument("--verify-interval", type=int, default=14400, help="Verification interval in seconds (default: 14400 = 4h)")
    worker_parser.add_argument("--drift-interval", type=int, default=3600, help="Drift scan interval in seconds (default: 3600 = 1h)")

    rotate_parser = subparsers.add_parser("rotate-verifications", help="Archive and rotate verification telemetry older than N days")
    rotate_parser.add_argument("--days", type=int, default=90, help="Retention threshold in days (default: 90)")

    sig_parser = subparsers.add_parser("signals", help="List trade recommendation signals")
    sig_parser.add_argument("--status", choices=["PENDING_FOUNDER_REVIEW", "APPROVED", "REJECTED", "EXECUTED", "QUARANTINE_48H"])
    sig_parser.add_argument("--type", choices=["BUY", "SELL_KILL", "SUPPLIER_SWITCH", "TREND_ALERT"])

    prop_parser = subparsers.add_parser("propose", help="Generate trade proposal for a candidate")
    prop_parser.add_argument("candidate_id", help="Target candidate ID")

    appr_parser = subparsers.add_parser("approve", help="Approve trade signal (Founder Sign-Off)")
    appr_parser.add_argument("signal_id", help="Signal ID to approve")
    appr_parser.add_argument("--by", default="Ahmad", help="Approver identity (must be Ahmad)")
    appr_parser.add_argument("--budget", type=float, help="Optional budget override")
    appr_parser.add_argument("-y", "--yes", action="store_true", help="Non-interactive approval (bypass prompt)")

    rej_parser = subparsers.add_parser("reject", help="Reject trade signal")
    rej_parser.add_argument("signal_id", help="Signal ID to reject")
    rej_parser.add_argument("--reason", help="Rejection rationale")

    exec_parser = subparsers.add_parser("execute", help="Execute approved trade signal")
    exec_parser.add_argument("signal_id", help="Signal ID to execute")
    exec_parser.add_argument("--live", action="store_true", help="Run in live mode (defaults to simulated)")

    subparsers.add_parser("audit", help="Run governance and security audit")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    store = Store()
    commands = {
        "status": cmd_status,
        "scan": cmd_scan,
        "score": cmd_score,
        "review": cmd_review,
        "verify": cmd_verify,
        "reconcile": cmd_reconcile,
        "drift": cmd_drift,
        "ver-history": cmd_ver_history,
        "revert-verifications": cmd_revert_verifications,
        "feature-flag": cmd_feature_flag,
        "approve-signal": cmd_approve_signal,
        "worker": cmd_worker,
        "rotate-verifications": cmd_rotate_verifications,
        "signals": cmd_signals,
        "propose": cmd_propose,
        "approve": cmd_approve,
        "reject": cmd_reject,
        "execute": cmd_execute,
        "audit": cmd_audit,
    }

    cmd_fn = commands.get(args.command)
    if cmd_fn:
        cmd_fn(store, args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
