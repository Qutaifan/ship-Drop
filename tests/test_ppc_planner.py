"""Unit Tests for Hermes PPC Strategy Planner Bot & Veo Credit Guard."""
from __future__ import annotations

import unittest

from agency.bots.ppc_planner_bot import PPCPlannerBot
from scripts.flow_credit_check import evaluate_veo_budget


class TestPPCPlannerBot(unittest.TestCase):
    # 1. Financial Framework & ROAS Math
    def test_financial_framework_calculations(self) -> None:
        # Retail: $100, Landed: $20, Payment fee (3%): $3 -> Margin: $77 (77%)
        # Break-even ROAS: 1 / 0.77 = 1.30x
        # Target ROAS: 1.30 * 1.65 = 2.15x
        # Landed ratio: 20% (passes US 24.2% rule)
        # Margin ($77) >= $42.96 (passes CAC gate)
        fin = PPCPlannerBot.calculate_financial_framework(retail=100.0, landed=20.0)

        self.assertEqual(fin["retail_price"], 100.0)
        self.assertEqual(fin["landed_cost"], 20.0)
        self.assertEqual(fin["payment_fee"], 3.0)
        self.assertEqual(fin["gross_margin_usd"], 77.0)
        self.assertAlmostEqual(fin["profit_margin_percent"], 77.0)
        self.assertEqual(fin["landed_cost_ratio_percent"], 20.0)
        self.assertTrue(fin["us_24pct_landed_rule_passed"])
        self.assertAlmostEqual(fin["break_even_roas"], 1.30, places=1)
        self.assertGreater(fin["target_roas"], fin["break_even_roas"])
        self.assertEqual(fin["max_cpa_usd"], 77.0)
        self.assertTrue(fin["cac_gate_cleared"])

    # 2. US 24.2% Landed Rule Violation Flagging
    def test_us_landed_rule_violation(self) -> None:
        # Retail: $50, Landed: $20 -> Landed ratio = 40% > 24.2%
        fin = PPCPlannerBot.calculate_financial_framework(retail=50.0, landed=20.0)
        self.assertFalse(fin["us_24pct_landed_rule_passed"])
        self.assertEqual(fin["landed_cost_ratio_percent"], 40.0)

    # 3. Mode A: Build Strategy Channel Splits
    def test_mode_a_splits_by_archetype(self) -> None:
        # Demo product (e.g. cable clips) -> TikTok 60%
        strat_demo = PPCPlannerBot.build_strategy(
            product_name="Magnetic Clip",
            retail=62.99,
            landed=7.0,
            monthly_budget=1000.0,
            product_type="demo",
        )
        self.assertEqual(strat_demo["platform_allocations"]["tiktok"]["allocation_percent"], 60.0)
        self.assertEqual(strat_demo["platform_allocations"]["meta"]["allocation_percent"], 25.0)
        self.assertEqual(strat_demo["platform_allocations"]["google"]["allocation_percent"], 15.0)
        self.assertGreater(strat_demo["blended_projected_roas"], 1.5)

        # Search product (e.g. jar sealer utility) -> Google 55%
        strat_search = PPCPlannerBot.build_strategy(
            product_name="Jar Sealer",
            retail=74.99,
            landed=15.0,
            monthly_budget=1000.0,
            product_type="search",
        )
        self.assertEqual(strat_search["platform_allocations"]["google"]["allocation_percent"], 55.0)
        self.assertEqual(strat_search["platform_allocations"]["meta"]["allocation_percent"], 30.0)
        self.assertEqual(strat_search["platform_allocations"]["tiktok"]["allocation_percent"], 15.0)

    # 4. Mode B: Optimization Actions
    def test_mode_b_optimization_actions(self) -> None:
        live_data = [
            {"platform": "TikTok Ads", "spend": 500.0, "revenue": 1400.0, "conversions": 25},   # ROAS 2.8 -> SCALE
            {"platform": "Meta Ads", "spend": 400.0, "revenue": 850.0, "conversions": 15},     # ROAS 2.12 -> MAINTAIN
            {"platform": "Google Ads", "spend": 300.0, "revenue": 200.0, "conversions": 3},    # ROAS 0.67 -> CUT/PAUSE
        ]

        audit = PPCPlannerBot.optimize_campaigns(live_data, target_roas=2.0)
        self.assertEqual(audit["total_spend"], 1200.0)
        self.assertEqual(audit["total_revenue"], 2450.0)
        self.assertAlmostEqual(audit["blended_roas"], 2.04)

        # Check action determinations
        p_map = {p["platform"]: p["action"] for p in audit["platforms"]}
        self.assertIn("SCALE", p_map["TikTok Ads"])
        self.assertIn("MAINTAIN", p_map["Meta Ads"])
        self.assertIn("CUT", p_map["Google Ads"])

    # 5. Veo Credit Guard
    def test_veo_credit_guard(self) -> None:
        # 1 Quality clip = 100 credits -> Approved with 500 credits
        ok_res = evaluate_veo_budget(model="quality", clips=1, remaining_credits=500)
        self.assertTrue(ok_res["approved"])
        self.assertEqual(ok_res["total_credits_required"], 100)
        self.assertEqual(ok_res["estimated_total_cost_usd"], 2.00)

        # 10 Quality clips = 1000 credits -> Rejected with 500 credits
        fail_res = evaluate_veo_budget(model="quality", clips=10, remaining_credits=500)
        self.assertFalse(fail_res["approved"])
        self.assertEqual(fail_res["max_clips_possible"], 5)


if __name__ == "__main__":
    unittest.main()
