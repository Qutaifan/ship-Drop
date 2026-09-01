"""Phase-4 Test Suite: Predictive Drift Modeling, Supplier Reputation Graph, Portfolio Rebalancer & Autonomous Windows."""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from agency.bots.portfolio_rebalancer import PortfolioRebalancer
from agency.core.predictive_drift import PredictiveDriftEngine
from agency.core.reputation_graph import SupplierReputationGraph
from agency.core.store import Store
from agency.governance.autonomous_windows import AutonomousWindowManager

ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = ROOT / "fixtures"


class TestPhase4PredictiveAndPortfolio(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_phase4.db"
        self.store = Store(db_path=self.db_path, data_dir=Path(self.temp_dir))

        with (FIXTURES_DIR / "candidate.sample.json").open("r", encoding="utf-8") as f:
            self.candidate = json.load(f)
        self.store.save_candidate(self.candidate)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # 1. Predictive Drift Engine
    def test_predictive_drift_modeling_stable(self) -> None:
        stabs = [0.95, 0.95, 0.94, 0.95]
        stocks = [2000, 1995, 1990, 1985]
        costs = [5.0, 5.0, 5.0, 5.0]
        defects = [1.0, 1.0, 1.1, 1.0]

        res = PredictiveDriftEngine.evaluate_predictive_drift(stabs, stocks, costs, defects)
        self.assertLess(res["predictive_drift_score"], 25.0)
        self.assertLess(res["collapse_probability"], 0.20)
        self.assertEqual(res["action_recommendation"], "STABLE")

    def test_predictive_drift_modeling_critical_decay(self) -> None:
        # Rapidly degrading telemetry: stability drops 0.04 each step, inventory crashing
        stabs = [0.95, 0.88, 0.82, 0.74]
        stocks = [500, 300, 150, 40]
        costs = [5.0, 5.3, 5.7, 6.2]
        defects = [1.0, 2.0, 3.5, 5.0]

        res = PredictiveDriftEngine.evaluate_predictive_drift(stabs, stocks, costs, defects)
        self.assertGreaterEqual(res["predictive_drift_score"], 60.0)
        self.assertGreaterEqual(res["collapse_probability"], 0.70)
        self.assertLessEqual(res["stockout_horizon_days"], 5)
        self.assertEqual(res["action_recommendation"], "PREEMPTIVE_SWITCH_URGENT")

    # 2. Supplier Reputation Graph
    def test_supplier_reputation_graph_construction(self) -> None:
        graph_engine = SupplierReputationGraph(self.store)
        graph = graph_engine.build_network_graph()

        self.assertIn("node_count", graph)
        self.assertIn("edges", graph)
        self.assertGreater(graph["node_count"], 0)

        # Check systemic risk calculation for sample candidate's supplier
        # In candidate.sample.json, supplier is "Sample Supplier" -> slug "sample-supplier"
        risk = graph_engine.assess_systemic_risk("sample-supplier")
        self.assertTrue(risk["found_in_graph"])
        self.assertEqual(risk["affected_sku_count"], 1)

    # 3. Portfolio Rebalancer
    def test_portfolio_rebalancer_execution(self) -> None:
        rebalancer = PortfolioRebalancer(self.store)
        res = rebalancer.rebalance_supplier("sample-supplier", reason="Test degradation")

        self.assertIn("batch_id", res)
        self.assertEqual(res["degraded_supplier_id"], "sample-supplier")
        self.assertEqual(res["affected_sku_count"], 1)

    # 4. Autonomous Execution Windows
    def test_founder_autonomous_execution_windows(self) -> None:
        mgr = AutonomousWindowManager(self.store, secret_key="test-secret-key-phase4")

        # Grant 2-hour window with $500 cap
        win = mgr.grant_window(founder_actor="Ahmad", duration_hours=2.0, spend_cap=500.0)
        self.assertEqual(win["authorized_by"], "Ahmad")
        self.assertEqual(win["spend_cap"], 500.0)
        self.assertIn("cryptographic_token", win)

        # Verify authorized action within budget
        auth_res = mgr.is_action_authorized(
            action="CANARY_ORDER_DISPATCH",
            sku_id="cand-001",
            spend_amount=75.0,
        )
        self.assertTrue(auth_res["authorized"])
        self.assertEqual(auth_res["window_id"], win["window_id"])

        # Consume spend
        consumed = mgr.consume_spend(win["window_id"], 75.0)
        self.assertTrue(consumed)

        # Attempt to authorize action that exceeds remaining cap ($500 - $75 = $425 remaining; request $450)
        auth_over = mgr.is_action_authorized(
            action="CANARY_ORDER_DISPATCH",
            sku_id="cand-001",
            spend_amount=450.0,
        )
        self.assertFalse(auth_over["authorized"])

        # Revoke window
        revoked = mgr.revoke_window(win["window_id"], reason="Test revocation")
        self.assertTrue(revoked)

        # Verify action is blocked after revocation
        auth_after_rev = mgr.is_action_authorized(
            action="CANARY_ORDER_DISPATCH",
            sku_id="cand-001",
            spend_amount=10.0,
        )
        self.assertFalse(auth_after_rev["authorized"])


if __name__ == "__main__":
    unittest.main()
