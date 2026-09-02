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
    if scout.skipped:
        print(f"  ⚠️  Skipped {len(scout.skipped)} dossier(s) — no economics ingested:")
        for name, reason in scout.skipped:
            print(f"    - {name}: {reason}")
        print()
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
def cmd_sourcing_rank(store: Store, args: argparse.Namespace) -> None:
    from agency.core.sourcing_ranker import SourcingRanker

    cid = getattr(args, "candidate", None) or getattr(args, "sku", None)
    if not cid:
        print("❌ Error: --candidate or --sku is required.")
        sys.exit(1)

    cand = store.get_candidate(cid)
    if not cand:
        print(f"❌ Candidate '{cid}' not found.")
        sys.exit(1)

    verifications = store.list_supplier_verifications(candidate_id=cid)
    res = SourcingRanker.rank_candidate_suppliers(cand, verifications=verifications, primary_metric=getattr(args, "metric", "stability_score"))

    if getattr(args, "json", False):
        print(json.dumps(res, indent=2))
        return

    print("\n" + "═" * 80)
    print(f"  🏭 SOURCING RANKER — {cand.get('product_name')} ({cid})")
    print(f"  Evaluation Market: {res['evaluation_market']} | Metric: {res['primary_ranking_metric']}")
    print("═" * 80)
    for s in res["suppliers"]:
        c_badge = "✅ YES" if s["canary_eligible"] else "❌ NO"
        print(f"  {s['rank']}. {s['supplier_name']:<32} | Tier: {s['tier']:<18} | Stab: {s['stability_score']:.2f} | Net: ${s['metrics']['projected_net_margin']:.2f} | Canary: {c_badge}")
        print(f"     Landed: ${s['metrics']['landed_cost']:.2f} | Lead: {s['metrics']['lead_days_max']}d | Stock: {s['metrics']['stock_level']} | Defect: {s['metrics']['defect_rate_percent']}% | Actionability: {s['actionability_score']}")
    print("-" * 80)
    print(f"  Selected Supplier: {res['selected_supplier_id']} (Allocation: {res['recommended_allocation_percent']}%)")
    print("═" * 80 + "\n")


def cmd_sourcing_volatility(store: Store, args: argparse.Namespace) -> None:
    from agency.bots.supplier_volatility_tracker import SupplierVolatilityTracker

    sup_id = getattr(args, "supplier", None)
    cid = getattr(args, "candidate", None)
    if not sup_id and not cid:
        print("❌ Error: --supplier or --candidate is required.")
        sys.exit(1)

    tracker = SupplierVolatilityTracker(store)
    res = tracker.analyze_supplier(supplier_id=sup_id or "primary-supplier", candidate_id=cid)

    if getattr(args, "json", False):
        print(json.dumps(res, indent=2))
        return

    print("\n" + "═" * 75)
    print(f"  📈 SUPPLIER VOLATILITY CURVES & TIMELINE: {res['supplier_id']}")
    print("═" * 75)
    curves = res["volatility_curves"]
    print(f"  Stability Drift (Window)      : {curves['stability_drift']:+.3f}")
    print(f"  Stability Volatility Index    : {curves['volatility_index']:.3f} (Threshold: 0.150)")
    print(f"  Stock Velocity (units/audit)  : {curves['stock_velocity_units_per_audit']:+.1f}")
    print(f"  Product Cost Drift            : {curves['price_drift_percent']:+.2f}%")
    print(f"  Lead Time Inflation           : {curves['lead_time_inflation_days']:+d} days")
    print("-" * 75)
    gov = res["governance"]
    if gov["switch_recommended"]:
        print(f"  ⚠️ GOVERNANCE ALERT: {gov['switch_reason']}")
        print(f"     Action: SUPPLIER_SWITCH recommended. Canary execution BLOCKED.")
    else:
        print("  ✓ Telemetry stable. No governance switch needed. Canary permitted.")
    print("-" * 75)
    print("  Recent Timeline Points:")
    for pt in res["timeline"][-5:]:
        print(f"    [{pt['ts'][:19]}] Stab: {pt['stability']:.2f} | Stock: {pt['stock']:<4} | Cost: ${pt['product_cost']:.2f} | Lead: {pt['lead_days_max']}d | {pt['status']}")
    print("═" * 75 + "\n")


def cmd_sourcing_lifecycle(store: Store, args: argparse.Namespace) -> None:
    from agency.bots.supplier_volatility_tracker import SupplierVolatilityTracker
    from agency.core.supplier_lifecycle import SupplierLifecycleManager

    sup_id = getattr(args, "supplier", None)
    cid = getattr(args, "candidate", None)
    tracker = SupplierVolatilityTracker(store)
    vol = tracker.analyze_supplier(supplier_id=sup_id or "primary-supplier", candidate_id=cid)
    stab = vol["latest_metrics"]["stability"]
    v_idx = vol["volatility_curves"]["volatility_index"]

    res = SupplierLifecycleManager.evaluate_state(stability_score=stab, volatility_index=v_idx)
    if getattr(args, "json", False):
        print(json.dumps(res, indent=2))
        return

    print("\n" + "═" * 75)
    print(f"  🏷️ SUPPLIER LIFECYCLE STATE: {vol['supplier_id']}")
    print("═" * 75)
    print(f"  Operational State    : {res['state']}")
    print(f"  Stability Score      : {stab:.2f}")
    print(f"  Volatility Index     : {v_idx:.3f}")
    print(f"  Canary Permitted     : {'✅ YES' if res['canary_permitted'] else '❌ BLOCKED'}")
    print(f"  Replacement Required : {'⚠️ YES' if res['replacement_required'] else '✓ NO'}")
    print(f"  Diagnostic Reason    : {res['reason']}")
    print("═" * 75 + "\n")


def cmd_sourcing_forecast(store: Store, args: argparse.Namespace) -> None:
    from agency.bots.supplier_volatility_tracker import SupplierVolatilityTracker
    from agency.core.supplier_forecasting import SupplierHealthForecaster

    sup_id = getattr(args, "supplier", None)
    cid = getattr(args, "candidate", None)
    tracker = SupplierVolatilityTracker(store)
    vol = tracker.analyze_supplier(supplier_id=sup_id or "primary-supplier", candidate_id=cid)
    res = SupplierHealthForecaster.forecast_health(vol.get("timeline", []))

    if getattr(args, "json", False):
        print(json.dumps(res, indent=2))
        return

    print("\n" + "═" * 75)
    print(f"  🔮 SUPPLIER HEALTH FORECAST: {vol['supplier_id']}")
    print("═" * 75)
    curr = res.get("current_metrics", {})
    p7d = res.get("projected_7d", {})
    print(f"  Current Stability    : {curr.get('stability', 0):.2f}  ──▶  7-Day Projection : {p7d.get('stability', 0):.2f}")
    print(f"  Current Stock Depth  : {curr.get('stock', 0):<4}  ──▶  Runout Forecast  : {p7d.get('stock_runout_days', 999)} day(s)")
    print(f"  Current Lead Time    : {curr.get('lead_days', 5)}d   ──▶  Lead Trajectory  : {p7d.get('lead_days_max', 5)}d")
    print(f"  Price Acceleration   : {p7d.get('price_acceleration_percent', 0.0):+.2f}% per week")
    print(f"  Forecast Risk Tier   : {res.get('risk_tier')}")
    if res.get("preemptive_switch_recommended"):
        print("  ⚠️ PREEMPTIVE SWITCH RECOMMENDED:")
        for r in res.get("preemptive_switch_reasons", []):
            print(f"     - {r}")
    else:
        print("  ✓ Forecast trajectories safe. No preemptive failover indicated.")
    print("═" * 75 + "\n")


def cmd_sourcing_matrix(store: Store, args: argparse.Namespace) -> None:
    from agency.core.competition_matrix import SupplierCompetitionMatrix

    cid = getattr(args, "candidate", None) or getattr(args, "sku", None)
    if not cid:
        print("❌ Error: --candidate or --sku is required.")
        sys.exit(1)

    matrix = SupplierCompetitionMatrix.generate_matrix(candidate_id=cid, store=store)
    if getattr(args, "json", False):
        print(json.dumps(matrix, indent=2))
        return

    print("\n" + "═" * 90)
    print(f"  📊 SKU SUPPLIER COMPETITION MATRIX — {matrix.get('product_name')} ({cid})")
    print(f"  Allocation Strategy: {matrix.get('allocation_strategy')} | Suppliers Audited: {matrix.get('supplier_count')}")
    print("═" * 90)
    for row in matrix.get("competition_matrix", []):
        c_badge = "✅" if row["canary_eligible"] else "❌"
        print(f"  {row['rank']}. {row['supplier_name']:<30} | State: {row['lifecycle_state']:<10} | Alloc: {row['allocation_percent']:>4.1f}% | Stab: {row['stability_score']:.2f} (7d: {row['projected_7d_stability']:.2f})")
        print(f"     Landed: ${row['landed_cost']:.2f} | Net: ${row['projected_net_margin']:.2f} | Runout: {row['stock_runout_days']}d | Defect: {row['defect_rate_percent']}% | Canary: {c_badge}")
    print("═" * 90 + "\n")


def cmd_sourcing_predict_drift(store: Store, args: argparse.Namespace) -> None:
    from agency.bots.supplier_volatility_tracker import SupplierVolatilityTracker
    from agency.core.predictive_drift import PredictiveDriftEngine

    sup_id = getattr(args, "supplier", None)
    cid = getattr(args, "candidate", None)
    tracker = SupplierVolatilityTracker(store)
    vol = tracker.analyze_supplier(supplier_id=sup_id or "primary-supplier", candidate_id=cid)
    timeline = vol.get("timeline", [])

    stabs = [float(p.get("stability", 0.9)) for p in timeline]
    stocks = [int(p.get("stock", 100)) for p in timeline]
    costs = [float(p.get("product_cost", 10.0)) for p in timeline]
    defects = [1.2 for _ in timeline]

    res = PredictiveDriftEngine.evaluate_predictive_drift(stabs, stocks, costs, defects)
    if getattr(args, "json", False):
        print(json.dumps(res, indent=2))
        return

    print("\n" + "═" * 75)
    print(f"  ⚡ PREDICTIVE DRIFT FORECAST: {vol['supplier_id']}")
    print("═" * 75)
    print(f"  Predictive Drift Score     : {res['predictive_drift_score']}/100")
    print(f"  Risk Tier                  : {res['risk_tier']}")
    print(f"  Stability Collapse Prob    : {res['collapse_probability']:.1%}")
    print(f"  7-Day Projected Stability  : {res['projected_stability_7d']:.2f}")
    print(f"  Stockout Runout Horizon    : {res['stockout_horizon_days']} day(s)")
    print(f"  Cost Inflation Velocity    : {res['cost_inflation_weekly_percent']:+.2f}% / week")
    print(f"  Action Recommendation      : {res['action_recommendation']}")
    print("-" * 75)
    for r in res.get("reasons", []):
        print(f"  - {r}")
    print("═" * 75 + "\n")


def cmd_sourcing_reputation(store: Store, args: argparse.Namespace) -> None:
    from agency.core.reputation_graph import SupplierReputationGraph

    graph_engine = SupplierReputationGraph(store)
    sup_id = getattr(args, "supplier", None)

    if sup_id:
        risk = graph_engine.assess_systemic_risk(sup_id)
        if getattr(args, "json", False):
            print(json.dumps(risk, indent=2))
            return
        print("\n" + "═" * 75)
        print(f"  🌐 SUPPLIER SYSTEMIC RISK & REPUTATION: {sup_id}")
        print("═" * 75)
        print(f"  Stability Score      : {risk.get('stability_score', 0):.2f}")
        print(f"  Portfolio Exposure   : {risk.get('portfolio_exposure_percent', 0):.1f}% of catalog")
        print(f"  Affected SKU Count   : {risk.get('affected_sku_count', 0)}")
        print(f"  Systemic Risk Level  : {risk.get('systemic_risk_level')}")
        print(f"  Recommended Action   : {risk.get('recommended_action')}")
        if risk.get("affected_skus"):
            print(f"  Connected SKUs       : {', '.join(risk.get('affected_skus'))}")
        print("═" * 75 + "\n")
        return

    g = graph_engine.build_network_graph()
    if getattr(args, "json", False):
        print(json.dumps(g, indent=2))
        return

    summary = g["systemic_summary"]
    print("\n" + "═" * 75)
    print("  🌐 SUPPLIER & LOGISTICS REPUTATION GRAPH")
    print("═" * 75)
    print(f"  Graph Topology       : {g['node_count']} Nodes | {g['edge_count']} Edges")
    print(f"  Active SKUs          : {summary['total_skus']}")
    print(f"  Sourcing Partners    : {summary['total_suppliers']}")
    print(f"  Fulfillment Hubs     : {summary['total_warehouses']}")
    print(f"  Carrier Networks     : {summary['total_carriers']}")
    print("-" * 75)
    print("  Supplier Hubs:")
    for k, v in g["nodes"].items():
        if v["type"] == "SUPPLIER":
            print(f"    - {v['label']:<32} | Exposure: {v['systemic_exposure_percent']:>4.1f}% | SKUs: {v['sku_count']} | Stab: {v['stability_score']:.2f}")
    print("═" * 75 + "\n")


def cmd_sourcing_rebalance(store: Store, args: argparse.Namespace) -> None:
    from agency.bots.portfolio_rebalancer import PortfolioRebalancer

    sup_id = getattr(args, "supplier", None)
    if not sup_id:
        print("❌ Error: --supplier is required.")
        sys.exit(1)

    reason = getattr(args, "reason", "Autonomous drift mitigation")
    rebalancer = PortfolioRebalancer(store)
    res = rebalancer.rebalance_supplier(sup_id, reason=reason)

    if getattr(args, "json", False):
        print(json.dumps(res, indent=2))
        return

    print("\n" + "═" * 80)
    print(f"  🔄 MULTI-SKU PORTFOLIO REBALANCING BATCH: {sup_id}")
    print("═" * 80)
    print(f"  Batch ID             : {res.get('batch_id')}")
    print(f"  Affected SKUs        : {res.get('affected_sku_count')}")
    print(f"  Switches Rerouted    : {res.get('successful_switches')}")
    print(f"  Emergency Pauses     : {res.get('emergency_pauses')}")
    print(f"  Net Margin Delta     : ${res.get('net_portfolio_margin_delta', 0.0):+.2f}")
    print(f"  Summary              : {res.get('summary')}")
    print("-" * 80)
    for s in res.get("sku_details", []):
        print(f"    - {s['candidate_id']:<35} ──▶ Status: {s['status']:<15} (Signal: {s.get('signal_id', 'N/A')})")
    print("═" * 80 + "\n")


def cmd_governance_window(store: Store, args: argparse.Namespace) -> None:
    from agency.governance.autonomous_windows import AutonomousWindowManager

    mgr = AutonomousWindowManager(store)
    sub = getattr(args, "subaction", "list")

    if sub == "grant":
        hrs = getattr(args, "hours", 2.0)
        cap = getattr(args, "cap", 500.0)
        actor = getattr(args, "actor", "Founder")
        win = mgr.grant_window(founder_actor=actor, duration_hours=hrs, spend_cap=cap)
        print("\n" + "═" * 75)
        print("  🔐 AUTONOMOUS EXECUTION WINDOW GRANTED")
        print("═" * 75)
        print(f"  Window ID            : {win['window_id']}")
        print(f"  Authorized By        : {win['authorized_by']}")
        print(f"  Duration             : {win['duration_hours']} hour(s)")
        print(f"  Spend Cap            : ${win['spend_cap']:.2f}")
        print(f"  Expires At (UTC)     : {win['expires_at']}")
        print(f"  Cryptographic Token  : {win['cryptographic_token'][:16]}...")
        print("═" * 75 + "\n")

    elif sub == "revoke":
        win_id = getattr(args, "id", None)
        if not win_id:
            print("❌ Error: --id is required to revoke window.")
            sys.exit(1)
        ok = mgr.revoke_window(win_id)
        if ok:
            print(f"\n🛑 Window {win_id} REVOKED immediately.\n")
        else:
            print(f"\n❌ Window {win_id} not found.\n")

    else:
        # List windows
        from agency.config.settings import WINDOWS_FILE
        windows_file = WINDOWS_FILE
        if windows_file.exists():
            with windows_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {"active_windows": []}

        print("\n" + "═" * 80)
        print("  🔐 ACTIVE AUTONOMOUS EXECUTION WINDOWS")
        print("═" * 80)
        wins = data.get("active_windows", [])
        if not wins:
            print("  (No autonomous execution windows currently active)")
        for w in wins:
            print(f"  ID: {w['window_id']} | Status: {w['status']:<8} | Cap: ${w['spend_cap']:.2f} | Consumed: ${w.get('consumed_spend', 0.0):.2f}")
            print(f"      Expires: {w['expires_at']} | Actor: {w['authorized_by']}")
        print("═" * 80 + "\n")


def cmd_pricing_optimize(store: Store, args: argparse.Namespace) -> None:
    from agency.core.dynamic_pricing import DynamicPricingEngine

    cid = getattr(args, "candidate", None) or getattr(args, "sku", None)
    if not cid:
        print("❌ Error: --candidate or --sku is required.")
        sys.exit(1)

    cand = store.get_candidate(cid)
    if not cand:
        print(f"❌ Error: Candidate {cid} not found.")
        sys.exit(1)

    econ = cand.get("unit_economics", {})
    retail = float(econ.get("gross_selling_price", 79.99))
    landed = float(econ.get("product_cost", 10.0)) + float(econ.get("shipping_cost", 4.0))
    stock = 250
    elast = getattr(args, "elasticity", 1.6)

    comp_evidence = cand.get("competitor_evidence", [])
    comp_prices = [float(e["observed_price"]) for e in comp_evidence if e.get("observed_price")]
    comp_price = sorted(comp_prices)[len(comp_prices) // 2] if comp_prices else getattr(args, "competitor", None)

    res = DynamicPricingEngine.optimize_price(
        current_retail=retail,
        landed_cost=landed,
        stock_depth=stock,
        elasticity_coefficient=elast,
        competitor_price=comp_price,
    )
    if getattr(args, "json", False):
        print(json.dumps(res, indent=2))
        return

    if getattr(args, "save", False):
        if "unit_economics" not in cand:
            cand["unit_economics"] = {}
        cand["unit_economics"]["gross_selling_price"] = res["recommended_retail"]
        cand["unit_economics"]["contribution_before_ads"] = res["projected_unit_margin"]
        cand["unit_economics"]["expected_profit_per_order"] = res["projected_unit_margin"]
        store.save_candidate(cand)
        print(f"  ✓ Saved optimized retail ${res['recommended_retail']:.2f} into candidate economics.")

    print("\n" + "═" * 75)
    print(f"  🏷️ DYNAMIC PRICING OPTIMIZATION: {cand.get('product_name')} ({cid})")
    print("═" * 75)
    print(f"  Current Retail Price : ${res['current_retail']:.2f}")
    print(f"  Optimized Retail     : ${res['recommended_retail']:.2f} (Delta: {res['price_delta']:+.2f})")
    print(f"  Projected Unit Margin: ${res['projected_unit_margin']:.2f} ({res['cogs_multiple']:.1f}x COGS)")
    print(f"  Margin Expansion     : {res['margin_lift_percent']:+.1f}%")
    print(f"  Demand Multiplier    : {res['elasticity_demand_ratio']:.2f}x baseline")
    if comp_price:
        print(f"  Competitor Anchor    : ${comp_price:.2f} (from Meta DSA ads)")
    print(f"  CAC Gate Cleared     : {'✅ YES' if res['cac_gate_cleared'] else '❌ NO'}")
    print("  FTC Rule Safeguard   : Non-profiling, inventory/elasticity rule-based")
    print("-" * 75)
    print(f"  Strategy: {res['optimization_rule']}")
    print("═" * 75 + "\n")


def cmd_dsa_ingest(store: Store, args: argparse.Namespace) -> None:
    from agency.ingestion.dsa_ad_ingestion import DSAAdIngestionPipeline

    cid = getattr(args, "candidate", None) or getattr(args, "sku", "cand-temp")
    query = getattr(args, "query", None)
    if not query:
        cand = store.get_candidate(cid)
        query = cand.get("product_name") if cand else cid

    countries = [c.strip() for c in getattr(args, "countries", "DE,FR,NL").split(",")]
    res = DSAAdIngestionPipeline.ingest_for_candidate(candidate_id=cid, query=query, countries=countries)

    if getattr(args, "save", False):
        cand = store.get_candidate(cid)
        if cand:
            cand["competitor_evidence"] = res["competitor_evidence"]
            store.save_candidate(cand)
            print(f"  ✓ Saved {len(res['competitor_evidence'])} competitor ad evidence items into candidate {cid}.")

    if getattr(args, "json", False):
        print(json.dumps(res, indent=2))
        return

    print("\n" + "═" * 80)
    print(f"  🔍 META AD LIBRARY DSA COMMERCIAL AD INGESTION: {query}")
    print(f"  Candidate ID: {cid} | Target Markets: {','.join(countries)}")
    print("═" * 80)
    print(f"  DSA Protocol Verdict : {res['dsa_protocol_verdict']}")
    print(f"  Market Saturation    : {res['saturation_status']}")
    print(f"  Distinct Advertisers : {res['distinct_advertisers']} (Min required: 5)")
    print(f"  Total Active Ads     : {res['total_active_ads']}")
    print(f"  Sustained (30d+) Ads : {res['sustained_30d_ads']} (Min required: 3)")
    print(f"  Median Competitor Prc: €{res['median_competitor_price']:.2f}")
    print(f"  DSA Demand Multiplier: {res['dsa_demand_multiplier']}x")
    print(f"  Competitive Pressure : {res['demand_side_pressure_score']}/100")
    print("-" * 80)
    print("  Competitor Creatives Extracted:")
    for ad in res["competitor_evidence"][:5]:
        print(f"    - {ad['competitor_name'][:28]:<28} | Observed: €{ad['observed_price']:.2f} | Conf: {ad['confidence']}")
    print("═" * 80 + "\n")


def cmd_cj_ingest(store: Store, args: argparse.Namespace) -> None:
    from agency.ingestion.cj_inventory_ingestion import CJInventoryIngestionPipeline

    sup_id = getattr(args, "supplier", "cj-dropshipping-us-domestic-hub")
    sku = getattr(args, "sku", "SKU-MAGNETIC-01")
    cid = getattr(args, "candidate", None) or "cand-cj-sku-magnetic-cord-6p"
    cost = getattr(args, "cost", None)
    stock = getattr(args, "stock", None)
    lead = getattr(args, "lead", None)

    rec = CJInventoryIngestionPipeline.ingest_and_verify(
        candidate_id=cid,
        supplier_id=sup_id,
        sku=sku,
        override_stock=stock,
        override_lead_max=lead,
        override_product_cost=cost,
    )

    if getattr(args, "save", False):
        store.save_supplier_verification(rec)
        print(f"  ✓ Saved verified CJ telemetry {rec['verification_id']} into database.")

    if getattr(args, "json", False):
        print(json.dumps(rec, indent=2))
        return

    print("\n" + "═" * 80)
    print(f"  📦 CJDROPSHIPPING LIVE DOMESTIC WAREHOUSE TELEMETRY: {sup_id}")
    print(f"  SKU: {sku} | Candidate: {cid} | Verification ID: {rec['verification_id']}")
    print("═" * 80)
    print(f"  Warehouse Origin     : {rec['warehouse_country']} ({rec['warehouse_type']})")
    print(f"  Shipping Route       : {rec['shipping_method']} (Delivery: {rec['lead_days_min']}-{rec['lead_days_max']} days)")
    print(f"  Live Stock Level     : {rec['stock_level']} units")
    print(f"  Verified Unit Cost   : ${rec['verified_product_cost']:.2f} (Quoted: ${rec['quoted_product_cost']:.2f} | Drift: {rec['price_drift_percent']:+.1%})")
    print(f"  Verified Freight Cost: ${rec['verified_shipping_cost']:.2f} (Import Duty: {rec['duty_percent']}%)")
    print(f"  Stability Score      : {rec['stability_score']:.2f} / 1.00")
    print(f"  Audit Status         : {rec['status']}")
    print(f"  HMAC Provenance Sig  : {rec['hmac_signature'][:16]}...")
    print("═" * 80 + "\n")


def cmd_ui_serve(store: Store, args: argparse.Namespace) -> None:
    from agency.api.server import run_hermes_api_server

    port = getattr(args, "port", 8080)
    host = getattr(args, "host", "127.0.0.1")
    run_hermes_api_server(host=host, port=port)


def cmd_buyer_simulate(store: Store, args: argparse.Namespace) -> None:
    from agency.bots.fake_buyer_journey import FakeBuyerJourneySimulator

    cid = getattr(args, "candidate", None) or "cand-cj-sku-magnetic-cord-6p"
    cust = getattr(args, "customer", "Marcus Vance (Synthetic Buyer)")
    country = getattr(args, "country", "US")

    sim = FakeBuyerJourneySimulator(store)
    res = sim.simulate_order(candidate_id=cid, customer_name=cust, customer_country=country)

    if getattr(args, "json", False):
        print(json.dumps(res, indent=2))
        return

    print("\n" + "═" * 80)
    print(f"  🛒 AUTONOMOUS BUYER JOURNEY REPLAY: {res['order_id']}")
    print(f"  Customer: {res['customer_name']} ({res['customer_country']}) | SKU: {res['candidate_id']}")
    print("═" * 80)
    for idx, step in enumerate(res["steps"], start=1):
        print(f"  {idx}. [{step['action']}]")
        print(f"     {step['details']}")
        print(f"     Timestamp: {step['timestamp']} | HMAC: {step['hmac_signature'][:16]}...")
        print("-" * 80)

    econ = res["unit_economics"]
    print("  📊 UNIT P&L RECONCILIATION:")
    print(f"     Gross Retail Captured : ${econ['gross_retail']:.2f}")
    print(f"     Stripe Processing Fee : -${econ['payment_fee']:.2f}")
    print(f"     Landed Sourcing COGS  : -${econ['landed_cogs']:.2f}")
    print(f"     Net Operating Profit  : +${econ['net_profit']:.2f} ({econ['cogs_multiple']}x COGS)")
    print(f"     CAC Gate Cleared (>=$42.96): {'✅ PASS' if econ['cac_gate_cleared'] else '❌ FAIL'}")
    print(f"     USPS Tracking Number  : {res['carrier_tracking']}")
    print("═" * 80 + "\n")


def cmd_medusa_sync(store: Store, args: argparse.Namespace) -> None:
    from agency.ingestion.medusa_storefront_sync import MedusaStorefrontSync

    cid = getattr(args, "candidate", None) or "cand-cj-sku-magnetic-cord-6p"
    publish = getattr(args, "publish", False)
    dry_run = getattr(args, "dry_run", False)

    sync_engine = MedusaStorefrontSync(store)
    res = sync_engine.sync_candidate(candidate_id=cid, publish=publish, dry_run=dry_run)

    if getattr(args, "json", False):
        print(json.dumps(res, indent=2))
        return

    print("\n" + "═" * 80)
    print(f"  🛍️ MEDUSA V2 STOREFRONT CATALOG SYNCHRONIZATION")
    print(f"  Candidate ID: {cid} | Status: {res['status']}")
    print("═" * 80)
    if res.get("status") == "DRY_RUN":
        p = res["payload"]
        print("  Mode: DRY RUN (Preview Only)")
        print(f"  Handle               : {p['handle']}")
        print(f"  Title                : {p['title']}")
        print(f"  Status               : {p['status']}")
        print(f"  USD Price (Cents)    : {p['variants'][0]['prices'][0]['amount']} (${p['variants'][0]['prices'][0]['amount']/100:.2f})")
        print(f"  Stock Inventory      : {p['variants'][0]['inventory_quantity']} units")
        print(f"  EU AI Act Notice     : Attached in description")
    else:
        print(f"  Medusa Product ID    : {res['medusa_product_id']}")
        print(f"  Product Handle (URL) : /{res['handle']}")
        print(f"  Synchronized Retail  : ${res['retail_price_usd']:.2f}")
        print(f"  Synchronized Stock   : {res['stock_inventory']} units (Verified Domestic)")
        print(f"  Storefront State     : {res['listing_status'].upper()}")
        print(f"  Local Catalog Export : {res['local_catalog_export']}")
        print(f"  Remote Medusa Backend: {'CONNECTED' if res['remote_api_connected'] else 'LOCAL_EXPORT_READY'}")
        print(f"  HMAC Provenance Sig  : {res['hmac_provenance'][:16]}...")
    print("═" * 80 + "\n")


def cmd_stripe_webhook(store: Store, args: argparse.Namespace) -> None:
    from agency.ingestion.stripe_telemetry_ingestion import StripeTelemetryIngestion

    cid = getattr(args, "candidate", "cand-cj-sku-magnetic-cord-6p")
    amount = getattr(args, "amount", 62.99)
    event_type = getattr(args, "event_type", "checkout.session.completed")

    # Synthesize a test event payload
    test_event = {
        "type": event_type,
        "data": {
            "object": {
                "id": f"cs_test_hermes_{cid[-8:]}",
                "amount_total": int(round(amount * 100)),
                "currency": "usd",
                "payment_status": "paid",
                "metadata": {"candidate_id": cid, "sku": "SKU-MAGNETIC-01"},
                "customer_details": {"address": {"country": "US"}},
            }
        },
    }

    engine = StripeTelemetryIngestion(store)
    res = engine.process_event(test_event)

    if getattr(args, "json", False):
        print(json.dumps(res, indent=2))
        return

    print("\n" + "═" * 80)
    print(f"  💳 STRIPE SANDBOX WEBHOOK PROCESSED")
    print(f"  Event: {res['event_type']} | Status: {res['status']}")
    print("═" * 80)
    if res["status"] == "RECONCILED":
        print(f"  Session ID           : {res['session_id']}")
        print(f"  Candidate ID         : {res['candidate_id']}")
        print(f"  Gross Revenue        : ${res['gross_revenue']:.2f}")
        print(f"  Stripe Fee (2.9%+30c): -${res['stripe_fee']:.2f}")
        print(f"  Net Proceeds         : +${res['net_proceeds']:.2f}")
    elif res["status"] == "CAPTURED":
        print(f"  Payment Intent ID    : {res['payment_intent_id']}")
        print(f"  Amount Captured      : ${res['amount']:.2f}")
    else:
        print(f"  Message: {res.get('message', 'N/A')}")
    print("═" * 80 + "\n")


def cmd_umami_event(store: Store, args: argparse.Namespace) -> None:
    from agency.ingestion.umami_telemetry_ingestion import UmamiTelemetryIngestion

    cid = getattr(args, "candidate", "cand-cj-sku-magnetic-cord-6p")
    event_type = getattr(args, "event_type", "pageview")
    price = getattr(args, "price", 62.99)
    count = getattr(args, "count", 1)

    engine = UmamiTelemetryIngestion(store)
    res = None
    for _ in range(count):
        res = engine.record_event(candidate_id=cid, event_type=event_type, price_point=price)

    if getattr(args, "json", False):
        print(json.dumps(res, indent=2))
        return

    print("\n" + "═" * 80)
    print(f"  📊 UMAMI COOKIELESS CONVERSION FUNNEL: {cid}")
    print("═" * 80)
    print(f"  Pageviews            : {res['pageviews']}")
    print(f"  Checkout Started     : {res['checkout_started']}")
    print(f"  Checkout Completed   : {res['checkout_completed']}")
    print(f"  Initiation Rate      : {res['checkout_initiation_rate_percent']}%")
    print(f"  Real CVR             : {res['real_conversion_rate_percent']}%")
    print(f"  Profit per Visitor   : ${res['profit_per_visitor_usd']:.2f}")
    print(f"  Empirical Elasticity : {res['empirical_elasticity_coefficient']}")
    if res.get("price_cohorts"):
        print("  ─── Price Cohort Performance ───")
        for p, c in sorted(res["price_cohorts"].items()):
            cvr = round((c["conversions"] / max(1, c["views"])) * 100, 2)
            print(f"    ${p} → {c['views']} views, {c['conversions']} conversions ({cvr}% CVR)")
    print("═" * 80 + "\n")


def cmd_conversion_summary(store: Store, args: argparse.Namespace) -> None:
    from agency.ingestion.umami_telemetry_ingestion import UmamiTelemetryIngestion

    cid = getattr(args, "candidate", "cand-cj-sku-magnetic-cord-6p")
    res = UmamiTelemetryIngestion(store).get_sku_funnel_summary(cid)

    if getattr(args, "json", False):
        print(json.dumps(res, indent=2))
        return

    print("\n" + "═" * 80)
    print(f"  📈 LIVE CONVERSION & ELASTICITY DASHBOARD: {cid}")
    print("═" * 80)
    print(f"  Sessions (Pageviews) : {res['pageviews']}")
    print(f"  Checkout Initiated   : {res['checkout_started']} ({res['checkout_initiation_rate_percent']}%)")
    print(f"  Orders Completed     : {res['checkout_completed']} ({res['real_conversion_rate_percent']}% CVR)")
    print(f"  Profit per Visitor   : ${res['profit_per_visitor_usd']:.2f}")
    print(f"  Elasticity (ε)       : {res['empirical_elasticity_coefficient']}")
    print("═" * 80 + "\n")


def cmd_orion_eval(store: Store, args: argparse.Namespace) -> None:
    from agency.bots.orion_bot import OrionBot

    cid = getattr(args, "candidate", None) or "cand-cj-sku-magnetic-cord-6p"
    orion = OrionBot(store)
    res = orion.evaluate_candidate(cid)

    if getattr(args, "json", False):
        print(json.dumps(res, indent=2))
        return

    print("\n" + "═" * 80)
    print(f"  🌌 ORION MARKET RESEARCH EVALUATION: {res['product_name']}")
    print(f"  Category: {res['category']} | Recommendation: {res['final_recommendation']}")
    print("═" * 80)
    print(f"  Demand Score         : {res['demand_score']}/100 (Velocity: {res['trend_velocity']})")
    print(f"  Competition Score    : {res['competition_score']}/100 (Saturation: {res['saturation_level']})")
    print(f"  Sourcing Feasibility : {res['sourcing_feasibility']}/100")
    print(f"  Risk Level           : {res['risk_level']}")
    print(f"  Price Band           : {res['median_price_band']} (Recommended: {res['recommended_retail']})")
    print(f"  Recommended Regions  : {', '.join(res['recommended_regions'])}")
    print(f"  Recommended Angles   : {', '.join(res['recommended_angles'])}")
    print(f"  ────────────────────────────────────────────────────────")
    print(f"  🏆 FINAL VIABILITY SCORE : {res['viability_score']}/100")
    print(f"  DECISION VERDICT         : {res['final_recommendation']}")
    if res.get("governance_rejection_reasons"):
        print(f"  ⚠️ Governance Rejections :")
        for r in res["governance_rejection_reasons"]:
            print(f"     - {r}")
    print("═" * 80 + "\n")


def cmd_orion_rank(store: Store, args: argparse.Namespace) -> None:
    from agency.bots.orion_bot import OrionBot

    orion = OrionBot(store)
    candidates = store.list_candidates()
    if not candidates:
        print("No candidates found in store to rank.")
        return

    results = [orion.evaluate_candidate(c["candidate_id"]) for c in candidates]
    ranked = sorted(results, key=lambda x: (x["final_recommendation"] == "APPROVE", x["viability_score"]), reverse=True)

    if getattr(args, "json", False):
        print(json.dumps(ranked, indent=2))
        return

    print("\n" + "═" * 90)
    print("  🌌 ORION MARKET RESEARCH OPPORTUNITY RANKING")
    print("═" * 90)
    print(f"  {'Rank':<5} {'Product Name':<35} {'Demand':<8} {'Comp':<8} {'Source':<8} {'Viability':<10} {'Verdict'}")
    print("  " + "─" * 85)
    for idx, r in enumerate(ranked, start=1):
        print(f"  {idx:<5} {r['product_name'][:33]:<35} {r['demand_score']:<8.1f} {r['competition_score']:<8.1f} {r['sourcing_feasibility']:<8.1f} {r['viability_score']:<10.1f} {r['final_recommendation']}")
    print("═" * 90 + "\n")


def cmd_ppc_plan(store: Store, args: argparse.Namespace) -> None:
    from agency.bots.ppc_planner_bot import PPCPlannerBot

    cid = getattr(args, "candidate", None) or "cand-cj-sku-magnetic-cord-6p"
    cand = store.get_candidate(cid)

    econ = cand.get("unit_economics", {}) if cand else {}
    retail = getattr(args, "retail", None)
    if retail is None:
        retail = float(econ.get("gross_selling_price", 62.99))

    landed = getattr(args, "landed", None)
    if landed is None:
        landed = float(econ.get("product_cost", 6.50)) + float(econ.get("shipping_cost", 3.50))

    budget = getattr(args, "budget", 1500.0)
    p_type = getattr(args, "type", "demo")
    name = cand.get("product_name", cid) if cand else cid

    plan = PPCPlannerBot.build_strategy(
        product_name=name,
        retail=retail,
        landed=landed,
        monthly_budget=budget,
        product_type=p_type,
    )

    if getattr(args, "json", False):
        print(json.dumps(plan, indent=2))
        return

    fin = plan["financial_framework"]
    print("\n" + "═" * 80)
    print(f"  📊 CROSS-PLATFORM PPC CAMPAIGN PLANNER: {plan['product_name']}")
    print(f"  Primary Channel: {plan['primary_channel']} | Monthly Budget: ${plan['monthly_budget_usd']:.2f}")
    print("═" * 80)
    print("  ─── 1. FINANCIAL & ROAS TARGETS ───")
    print(f"  Retail Price            : ${fin['retail_price']:.2f}")
    print(f"  Landed COGS             : ${fin['landed_cost']:.2f} ({fin['landed_cost_ratio_percent']}% of retail)")
    print(f"  US 24.2% Landed Rule    : {'✅ PASS' if fin['us_24pct_landed_rule_passed'] else '⚠️ WARNING (Landed > 24.2% of retail)'}")
    print(f"  Gross Profit Margin     : ${fin['gross_margin_usd']:.2f} ({fin['profit_margin_percent']}%)")
    print(f"  Break-Even ROAS         : {fin['break_even_roas']}x (Every $1 in ads must return ${fin['break_even_roas']:.2f})")
    print(f"  Target ROAS (1.65x BE)  : {fin['target_roas']}x")
    print(f"  Max Break-Even CPA      : ${fin['max_cpa_usd']:.2f}")
    print(f"  Target CPA              : ${fin['target_cpa_usd']:.2f}")
    print(f"  CAC Gate Cleared        : {'✅ PASS (Margin >= 2x Median CPA)' if fin['cac_gate_cleared'] else '❌ FAIL'}")

    print("\n  ─── 2. MULTI-PLATFORM BUDGET ALLOCATION ───")
    for k, a in plan["platform_allocations"].items():
        print(f"  • {a['platform_name']}")
        print(f"    Split: {a['allocation_percent']}% | Budget: ${a['monthly_budget_usd']:.2f}/mo (${a['daily_budget_usd']:.2f}/day)")
        print(f"    Benchmark ROAS: {a['benchmark_roas']}x | Projected Rev: ${a['projected_gross_revenue']:.2f}")
        print(f"    Role: {a['best_for']}")

    print("\n  ─── 3. PROJECTED MONTHLY PERFORMANCE ───")
    print(f"  Total Ad Spend          : ${plan['monthly_budget_usd']:.2f}")
    print(f"  Projected Gross Revenue : ${plan['projected_monthly_revenue']:.2f}")
    print(f"  Blended Projected ROAS  : {plan['blended_projected_roas']}x")
    print(f"  Projected Net Profit    : ${plan['projected_monthly_net_profit']:.2f}")
    print("═" * 80 + "\n")


def cmd_demand_forecast(store: Store, args: argparse.Namespace) -> None:
    from agency.core.demand_forecasting import DemandForecastingEngine

    cid = getattr(args, "candidate", None) or getattr(args, "sku", None)
    spend = getattr(args, "spend", 50.0)
    cpc = getattr(args, "cpc", 0.85)
    cvr = getattr(args, "cvr", 2.2)

    res = DemandForecastingEngine.forecast_demand(daily_ad_spend=spend, cpc=cpc, predicted_cvr_percent=cvr)
    if getattr(args, "json", False):
        print(json.dumps(res, indent=2))
        return

    print("\n" + "═" * 75)
    print(f"  📈 DEMAND & INVENTORY FORECAST: {cid or 'Catalog Target'}")
    print("═" * 75)
    print(f"  Daily Order Demand   : {res['daily_demand_units']} unit(s) / day")
    print(f"  Weekly Order Volume  : {res['weekly_demand_units']} units")
    print(f"  Monthly Order Volume : {res['monthly_demand_units']} units")
    print(f"  Safety Stock Buffer  : {res['safety_stock_units']} units")
    print(f"  Reorder Trigger Point: {res['reorder_point_units']} units")
    print(f"  Inventory Runway     : {res['inventory_runway_days']} days (Current Stock: {res['current_stock_units']})")
    print(f"  Reorder Status       : {'⚠️ REORDER NEEDED' if res['reorder_needed'] else '✓ ADEQUATE'}")
    print("-" * 75)
    am = res["ad_channel_metrics"]
    print(f"  Ad Channel: {am['daily_clicks']} clicks/day @ ${am['expected_cpa']:.2f} CPA (Uplift: {am['organic_uplift_multiplier']}x)")
    print("═" * 75 + "\n")


def cmd_sourcing_negotiate(store: Store, args: argparse.Namespace) -> None:
    from agency.bots.negotiation_simulator import SupplierNegotiationSimulator

    sup_id = getattr(args, "supplier", "cj-domestic-hub")
    sku = getattr(args, "sku", "SKU-TARGET")
    cost = getattr(args, "cost", 6.50)
    ship = getattr(args, "shipping", 3.50)
    vol = getattr(args, "volume", 150)

    res = SupplierNegotiationSimulator.simulate_volume_tiers(
        supplier_id=sup_id,
        sku=sku,
        current_product_cost=cost,
        current_shipping_cost=ship,
        monthly_volume=vol,
    )
    if getattr(args, "json", False):
        print(json.dumps(res, indent=2))
        return

    print("\n" + "═" * 80)
    print(f"  🤝 SUPPLIER VOLUME-TIER NEGOTIATION SIMULATOR: {sup_id} ({sku})")
    print("═" * 80)
    print(f"  Current Cost Baseline: ${res['current_product_cost']:.2f} unit + ${res['current_shipping_cost']:.2f} ship")
    print(f"  Target Run-Rate      : {res['monthly_volume_projection']} units / month")
    print(f"  Target Volume Tier   : {res['target_negotiation_tier']}")
    print(f"  Annual Margin Growth : ${res['projected_annual_margin_expansion']:,.2f}")
    print("-" * 80)
    print("  Volume Discount Scenarios:")
    for sc in res["volume_scenarios"]:
        print(f"    - {sc['tier']:<24} (MOQ {sc['moq_range']:<9}): -{sc['discount_percent']:>4.1f}% ──▶ ${sc['target_unit_cost']:.2f} unit (Save: ${sc['annual_savings']:,.2f}/yr)")
    print("-" * 80)
    print("  Copy-Ready Supplier Pitch Brief:")
    pitch = res['negotiation_brief']['copy_ready_pitch'].replace('\n', '\n    ')
    print(f"    \"{pitch}\"")
    print("═" * 80 + "\n")


def cmd_portfolio_optimize(store: Store, args: argparse.Namespace) -> None:
    from agency.bots.global_portfolio_optimizer import GlobalPortfolioOptimizer

    budget = getattr(args, "budget", 3000.0)
    opt = GlobalPortfolioOptimizer(store)
    res = opt.optimize_portfolio(total_monthly_marketing_budget=budget)

    if getattr(args, "json", False):
        print(json.dumps(res, indent=2))
        return

    print("\n" + "═" * 90)
    print("  🧠 GLOBAL PORTFOLIO OPTIMIZER — MACRO CAPITAL & MARGIN ENGINE")
    print("═" * 90)
    print(f"  Catalog SKUs Evaluated : {res['catalog_sku_count']}")
    print(f"  Monthly Ad Budget      : ${res['total_monthly_marketing_budget']:,.2f}")
    print(f"  Projected Monthly Orders: {res['portfolio_monthly_demand_orders']:,} orders")
    print(f"  Gross Revenue Potential: ${res['portfolio_monthly_gross_revenue']:,.2f}")
    print(f"  Net Profit Contribution: ${res['portfolio_monthly_net_margin']:,.2f} ({res['blended_cogs_multiple']}x COGS)")
    print(f"  Sourcing Stability Avg : {res['portfolio_average_stability']:.2f}")
    print("-" * 90)
    print("  SKU Capital Allocation & Profit Ranking:")
    for idx, s in enumerate(res.get("skus", []), 1):
        print(f"    {idx}. {s['product_name'][:30]:<30} | Price: ${s['optimized_retail']:.2f} | Net: ${s['unit_margin']:.2f} | Mo Orders: {s['monthly_demand_units']} | Profit: ${s['projected_monthly_margin']:,.2f} | Ad Alloc: {s['allocated_ad_budget_pct']}%")
    print("═" * 90 + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Dropship Agency - Autonomous Intelligence & Trade Terminal")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("status", help="Display agency operational status")
    scan_parser = subparsers.add_parser("scan", help="Scan candidate documents and product databases")
    scan_parser.add_argument("--query", "-q", help="Search CJ domestic catalog for query")
    scan_parser.add_argument("--warehouse", "-w", default="US", help="Target warehouse (US/DE)")

    subparsers.add_parser("score", help="Calculate opportunity scores across all products")
    subparsers.add_parser("review", help="Interactively review and approve pending trade signals")

    # Sourcing Ranker Command
    rank_parser = subparsers.add_parser("sourcing:rank", aliases=["sourcing-rank", "rank"], help="Rank competing suppliers for candidate")
    rank_parser.add_argument("--candidate", "--sku", dest="candidate", help="Target candidate ID or SKU")
    rank_parser.add_argument("--metric", default="stability_score", choices=["stability_score", "net_margin", "lead_time"], help="Primary sorting metric")
    rank_parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # Sourcing Volatility Command
    vol_parser = subparsers.add_parser("sourcing:volatility", aliases=["sourcing-volatility", "volatility"], help="Analyze supplier stability curves and volatility")
    vol_parser.add_argument("--supplier", "-s", help="Supplier ID to analyze")
    vol_parser.add_argument("--candidate", "-c", help="Candidate ID to filter audits")
    vol_parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # Sourcing Lifecycle Command
    life_parser = subparsers.add_parser("sourcing:lifecycle", aliases=["sourcing-lifecycle", "lifecycle"], help="Inspect supplier lifecycle state machine")
    life_parser.add_argument("--supplier", "-s", help="Supplier ID to inspect")
    life_parser.add_argument("--candidate", "-c", help="Candidate ID to filter audits")
    life_parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # Sourcing Forecast Command
    fc_parser = subparsers.add_parser("sourcing:forecast", aliases=["sourcing-forecast", "forecast"], help="Preemptively forecast supplier health and depletion")
    fc_parser.add_argument("--supplier", "-s", help="Supplier ID to forecast")
    fc_parser.add_argument("--candidate", "-c", help="Candidate ID to filter audits")
    fc_parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # Sourcing Matrix Command
    mat_parser = subparsers.add_parser("sourcing:matrix", aliases=["sourcing-matrix", "matrix"], help="Produce SKU-level multi-supplier competition matrix")
    mat_parser.add_argument("--candidate", "--sku", dest="candidate", help="Target candidate ID or SKU")
    mat_parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # Phase-4 Predictive Drift Command
    pdrift_parser = subparsers.add_parser("sourcing:predict-drift", aliases=["sourcing-predict-drift", "predict-drift"], help="Multi-agent predictive drift and collapse modeling")
    pdrift_parser.add_argument("--supplier", "-s", help="Supplier ID to evaluate")
    pdrift_parser.add_argument("--candidate", "-c", help="Candidate ID to filter audits")
    pdrift_parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # Phase-4 Reputation Graph Command
    rep_parser = subparsers.add_parser("sourcing:reputation", aliases=["sourcing-reputation", "reputation"], help="Inspect supplier and logistics reputation graph and systemic risk")
    rep_parser.add_argument("--supplier", "-s", help="Specific supplier ID to evaluate blast radius")
    rep_parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # Phase-4 Portfolio Rebalancing Command
    reb_parser = subparsers.add_parser("sourcing:rebalance", aliases=["sourcing-rebalance", "rebalance"], help="Orchestrate portfolio-wide multi-SKU supplier rebalancing")
    reb_parser.add_argument("--supplier", "-s", required=True, help="Degraded supplier ID to failover")
    reb_parser.add_argument("--reason", default="Autonomous systemic drift rebalance", help="Audit reason")
    reb_parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # Phase-4 Founder Autonomous Execution Window Command
    win_parser = subparsers.add_parser("governance:window", aliases=["governance-window", "window"], help="Manage time-boxed Founder autonomous execution windows")
    win_parser.add_argument("subaction", choices=["list", "grant", "revoke"], nargs="?", default="list", help="Window action")
    win_parser.add_argument("--hours", type=float, default=2.0, help="Window duration in hours")
    win_parser.add_argument("--cap", type=float, default=500.0, help="Hard spend limit in USD")
    win_parser.add_argument("--actor", default="Founder", help="Authorizing founder actor")
    win_parser.add_argument("--id", help="Window ID to revoke")

    # Phase-5 Dynamic Pricing Command
    price_parser = subparsers.add_parser("pricing:optimize", aliases=["pricing-optimize", "pricing"], help="Rule-based margin & elasticity dynamic pricing optimizer")
    price_parser.add_argument("--candidate", "--sku", dest="candidate", help="Target candidate ID or SKU")
    price_parser.add_argument("--elasticity", type=float, default=1.6, help="Price elasticity coefficient")
    price_parser.add_argument("--save", action="store_true", help="Save optimized retail price into candidate record")
    price_parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # Phase-5 Demand Forecasting Command
    df_parser = subparsers.add_parser("demand:forecast", aliases=["demand-forecast", "demand"], help="Forecast order demand, safety stock, and reorder point")
    df_parser.add_argument("--candidate", "--sku", dest="candidate", help="Target candidate ID or SKU")
    df_parser.add_argument("--spend", type=float, default=50.0, help="Target daily ad spend in USD")
    df_parser.add_argument("--cpc", type=float, default=0.85, help="Estimated CPC in USD")
    df_parser.add_argument("--cvr", type=float, default=2.2, help="Predicted conversion rate %")
    df_parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # Phase-5 Supplier Negotiation Simulator Command
    neg_parser = subparsers.add_parser("sourcing:negotiate", aliases=["sourcing-negotiate", "negotiate"], help="Simulate volume discounts and draft supplier negotiation pitch")
    neg_parser.add_argument("--supplier", "-s", default="cj-domestic-hub", help="Supplier ID")
    neg_parser.add_argument("--sku", default="SKU-TARGET", help="Target SKU")
    neg_parser.add_argument("--cost", type=float, default=6.50, help="Current product unit cost")
    neg_parser.add_argument("--shipping", type=float, default=3.50, help="Current shipping cost")
    neg_parser.add_argument("--volume", type=int, default=150, help="Projected monthly order volume")
    neg_parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # Phase-5 Global Portfolio Optimizer Command
    glob_parser = subparsers.add_parser("portfolio:optimize", aliases=["portfolio-optimize", "optimize"], help="Global capital allocation and portfolio-wide margin optimizer")
    glob_parser.add_argument("--budget", type=float, default=3000.0, help="Total monthly marketing budget in USD")
    glob_parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # Phase-6 Meta Ad Library DSA Ingestion Command
    dsa_parser = subparsers.add_parser("dsa:ingest", aliases=["dsa-ingest", "dsa"], help="Ingest commercial competitor ads from Meta Ad Library under DSA")
    dsa_parser.add_argument("--candidate", "--sku", dest="candidate", help="Target candidate ID or SKU")
    dsa_parser.add_argument("--query", "-q", help="Search query for commercial ads")
    dsa_parser.add_argument("--countries", default="DE,FR,NL", help="Target EU/UK countries comma-separated (default: DE,FR,NL)")
    dsa_parser.add_argument("--save", action="store_true", help="Save extracted competitor evidence to candidate record in database")
    dsa_parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # Phase-6 CJdropshipping Live Inventory Ingestion Command
    cj_parser = subparsers.add_parser("cj:ingest", aliases=["cj-ingest", "cj"], help="Ingest real-time domestic warehouse stock & costs from CJdropshipping")
    cj_parser.add_argument("--supplier", "-s", default="cj-dropshipping-us-domestic-hub", help="Supplier ID")
    cj_parser.add_argument("--sku", default="SKU-MAGNETIC-01", help="CJ SKU or Variant ID")
    cj_parser.add_argument("--candidate", "-c", default="cand-cj-sku-magnetic-cord-6p", help="Associated Candidate ID")
    cj_parser.add_argument("--stock", type=int, help="Override stock level for test simulation")
    cj_parser.add_argument("--lead", type=int, help="Override lead time days for test simulation")
    cj_parser.add_argument("--cost", type=float, help="Override product cost for test simulation")
    cj_parser.add_argument("--save", action="store_true", help="Save verification record directly into database")
    cj_parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # Phase-6 Hermes Desktop UI Telemetry Server Command
    ui_parser = subparsers.add_parser("ui:serve", aliases=["ui", "serve"], help="Start Hermes Desktop Telemetry API Server")
    ui_parser.add_argument("--port", "-p", type=int, default=8080, help="HTTP server port (default: 8080)")
    ui_parser.add_argument("--host", default="127.0.0.1", help="HTTP server host (default: 127.0.0.1)")

    # Phase-6 Synthetic Buyer Journey Simulator Command
    buyer_parser = subparsers.add_parser("buyer:simulate", aliases=["buyer-simulate", "buyer"], help="Run synthetic buyer journey simulation and log to replay feed")
    buyer_parser.add_argument("--candidate", "--sku", dest="candidate", default="cand-cj-sku-magnetic-cord-6p", help="Target candidate ID")
    buyer_parser.add_argument("--customer", default="Marcus Vance (Synthetic Buyer)", help="Customer persona name")
    buyer_parser.add_argument("--country", default="US", help="Customer destination country")
    buyer_parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # Phase-6 Medusa v2 Storefront Sync Command
    medusa_parser = subparsers.add_parser("medusa:sync", aliases=["medusa-sync", "medusa"], help="Sync candidate pricing, variants, and stock into Medusa v2")
    medusa_parser.add_argument("--candidate", "--sku", dest="candidate", default="cand-cj-sku-magnetic-cord-6p", help="Target candidate ID")
    medusa_parser.add_argument("--publish", action="store_true", help="Set product status to published (default: draft)")
    medusa_parser.add_argument("--dry-run", action="store_true", help="Preview Medusa payload without writing")
    medusa_parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # Phase-6 Stripe Sandbox Webhook CLI Command
    stripe_parser = subparsers.add_parser("stripe:webhook", aliases=["stripe-webhook", "stripe"], help="Simulate/process a Stripe sandbox webhook event")
    stripe_parser.add_argument("--candidate", "--sku", dest="candidate", default="cand-cj-sku-magnetic-cord-6p", help="Target candidate ID")
    stripe_parser.add_argument("--amount", type=float, default=62.99, help="Checkout gross amount in USD")
    stripe_parser.add_argument("--event-type", dest="event_type", default="checkout.session.completed", help="Stripe event type")
    stripe_parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # Phase-6 Umami Telemetry Event CLI Command
    umami_parser = subparsers.add_parser("umami:event", aliases=["umami-event", "umami"], help="Record a cookieless Umami telemetry event (pageview, checkout_started, checkout_completed)")
    umami_parser.add_argument("--candidate", "--sku", dest="candidate", default="cand-cj-sku-magnetic-cord-6p", help="Target candidate ID")
    umami_parser.add_argument("--event-type", dest="event_type", default="pageview", choices=["pageview", "checkout_started", "checkout_completed"], help="Umami event type")
    umami_parser.add_argument("--price", type=float, default=62.99, help="Price point at which event occurred")
    umami_parser.add_argument("--count", type=int, default=1, help="Number of events to record (batch mode)")
    umami_parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # Phase-6 Conversion & Elasticity Summary CLI Command
    conv_parser = subparsers.add_parser("conversion:summary", aliases=["conversion-summary", "conversion"], help="Display live funnel CVR, profit-per-visitor, and empirical elasticity")
    conv_parser.add_argument("--candidate", "--sku", dest="candidate", default="cand-cj-sku-magnetic-cord-6p", help="Target candidate ID")
    conv_parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # ORION Market Research Agent Commands
    orion_eval_parser = subparsers.add_parser("orion:eval", aliases=["orion-eval", "orion"], help="Evaluate product opportunity with ORION Market Research Agent")
    orion_eval_parser.add_argument("--candidate", "--sku", dest="candidate", default="cand-cj-sku-magnetic-cord-6p", help="Target candidate ID")
    orion_eval_parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    orion_rank_parser = subparsers.add_parser("orion:rank", aliases=["orion-rank"], help="Rank all catalog opportunities with ORION Market Research Agent")
    orion_rank_parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # PPC Cross-Platform Strategy Planner Command
    ppc_parser = subparsers.add_parser("ppc:plan", aliases=["ppc-plan", "ppc"], help="Generate multi-platform PPC strategy & ROAS framework (TikTok, Meta, Google)")
    ppc_parser.add_argument("--candidate", "--sku", dest="candidate", default="cand-cj-sku-magnetic-cord-6p", help="Target candidate ID")
    ppc_parser.add_argument("--retail", type=float, help="Override gross retail price")
    ppc_parser.add_argument("--landed", type=float, help="Override landed cost")
    ppc_parser.add_argument("--budget", type=float, default=1500.0, help="Monthly marketing budget in USD (default: $1500)")
    ppc_parser.add_argument("--type", choices=["demo", "search", "visual"], default="demo", help="Product behavior archetype")
    ppc_parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")

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
        "sourcing:rank": cmd_sourcing_rank,
        "sourcing-rank": cmd_sourcing_rank,
        "rank": cmd_sourcing_rank,
        "sourcing:volatility": cmd_sourcing_volatility,
        "sourcing-volatility": cmd_sourcing_volatility,
        "volatility": cmd_sourcing_volatility,
        "sourcing:lifecycle": cmd_sourcing_lifecycle,
        "sourcing-lifecycle": cmd_sourcing_lifecycle,
        "lifecycle": cmd_sourcing_lifecycle,
        "sourcing:forecast": cmd_sourcing_forecast,
        "sourcing-forecast": cmd_sourcing_forecast,
        "forecast": cmd_sourcing_forecast,
        "sourcing:matrix": cmd_sourcing_matrix,
        "sourcing-matrix": cmd_sourcing_matrix,
        "matrix": cmd_sourcing_matrix,
        "sourcing:predict-drift": cmd_sourcing_predict_drift,
        "sourcing-predict-drift": cmd_sourcing_predict_drift,
        "predict-drift": cmd_sourcing_predict_drift,
        "sourcing:reputation": cmd_sourcing_reputation,
        "sourcing-reputation": cmd_sourcing_reputation,
        "reputation": cmd_sourcing_reputation,
        "sourcing:rebalance": cmd_sourcing_rebalance,
        "sourcing-rebalance": cmd_sourcing_rebalance,
        "rebalance": cmd_sourcing_rebalance,
        "governance:window": cmd_governance_window,
        "governance-window": cmd_governance_window,
        "window": cmd_governance_window,
        "pricing:optimize": cmd_pricing_optimize,
        "pricing-optimize": cmd_pricing_optimize,
        "pricing": cmd_pricing_optimize,
        "demand:forecast": cmd_demand_forecast,
        "demand-forecast": cmd_demand_forecast,
        "demand": cmd_demand_forecast,
        "sourcing:negotiate": cmd_sourcing_negotiate,
        "sourcing-negotiate": cmd_sourcing_negotiate,
        "negotiate": cmd_sourcing_negotiate,
        "portfolio:optimize": cmd_portfolio_optimize,
        "portfolio-optimize": cmd_portfolio_optimize,
        "optimize": cmd_portfolio_optimize,
        "dsa:ingest": cmd_dsa_ingest,
        "dsa-ingest": cmd_dsa_ingest,
        "dsa": cmd_dsa_ingest,
        "cj:ingest": cmd_cj_ingest,
        "cj-ingest": cmd_cj_ingest,
        "cj": cmd_cj_ingest,
        "ui:serve": cmd_ui_serve,
        "ui": cmd_ui_serve,
        "serve": cmd_ui_serve,
        "buyer:simulate": cmd_buyer_simulate,
        "buyer-simulate": cmd_buyer_simulate,
        "buyer": cmd_buyer_simulate,
        "medusa:sync": cmd_medusa_sync,
        "medusa-sync": cmd_medusa_sync,
        "medusa": cmd_medusa_sync,
        "stripe:webhook": cmd_stripe_webhook,
        "stripe-webhook": cmd_stripe_webhook,
        "stripe": cmd_stripe_webhook,
        "umami:event": cmd_umami_event,
        "umami-event": cmd_umami_event,
        "umami": cmd_umami_event,
        "conversion:summary": cmd_conversion_summary,
        "conversion-summary": cmd_conversion_summary,
        "conversion": cmd_conversion_summary,
        "orion:eval": cmd_orion_eval,
        "orion-eval": cmd_orion_eval,
        "orion": cmd_orion_eval,
        "orion:rank": cmd_orion_rank,
        "orion-rank": cmd_orion_rank,
        "ppc:plan": cmd_ppc_plan,
        "ppc-plan": cmd_ppc_plan,
        "ppc": cmd_ppc_plan,
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
