"""Phase-5 Test Suite: Dynamic Pricing, Demand Forecasting, Supplier Negotiation & Global Portfolio Optimizer."""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from agency.bots.global_portfolio_optimizer import GlobalPortfolioOptimizer
from agency.bots.negotiation_simulator import SupplierNegotiationSimulator
from agency.core.demand_forecasting import DemandForecastingEngine
from agency.core.dynamic_pricing import DynamicPricingEngine
from agency.core.store import Store

ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = ROOT / "fixtures"


class TestPhase5EconomicOptimization(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_phase5.db"
        self.store = Store(db_path=self.db_path, data_dir=Path(self.temp_dir))

        with (FIXTURES_DIR / "candidate.sample.json").open("r", encoding="utf-8") as f:
            self.candidate = json.load(f)
        self.store.save_candidate(self.candidate)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # 1. Dynamic Pricing Engine
    def test_dynamic_pricing_optimization(self) -> None:
        # Landed cost $10.00, stock 150 -> price should land in [$62, $93]
        res = DynamicPricingEngine.optimize_price(
            current_retail=29.99,
            landed_cost=10.00,
            stock_depth=150,
            elasticity_coefficient=1.5,
        )

        self.assertGreaterEqual(res["recommended_retail"], 62.00)
        self.assertLessEqual(res["recommended_retail"], 93.00)
        self.assertGreaterEqual(res["projected_unit_margin"], 42.96)  # CAC Gate 2x CPA ($21.48 * 2)
        self.assertTrue(res["cac_gate_cleared"])
        self.assertGreaterEqual(res["cogs_multiple"], 3.0)  # 3x COGS rule

    # 2. Scarcity Pricing Rule
    def test_dynamic_pricing_scarcity_rule(self) -> None:
        # Stock depth = 10 units (low stock) should protect inventory
        res_low = DynamicPricingEngine.optimize_price(
            current_retail=65.00,
            landed_cost=12.00,
            stock_depth=10,
        )
        self.assertGreaterEqual(res_low["recommended_retail"], 62.00)
        self.assertTrue(res_low["cac_gate_cleared"])

    # 3. Demand Forecasting Engine
    def test_demand_forecasting_calculations(self) -> None:
        res = DemandForecastingEngine.forecast_demand(
            daily_ad_spend=60.0,
            cpc=0.80,
            predicted_cvr_percent=2.5,
            current_stock=200,
            lead_time_days=5,
        )

        self.assertGreater(res["daily_demand_units"], 0.0)
        self.assertGreater(res["weekly_demand_units"], 0)
        self.assertGreater(res["monthly_demand_units"], 0)
        self.assertGreater(res["reorder_point_units"], 0)
        self.assertFalse(res["reorder_needed"])  # Stock 200 > ROP

        # Test stockout trigger: current stock 5 units
        res_low = DemandForecastingEngine.forecast_demand(
            daily_ad_spend=60.0,
            cpc=0.80,
            predicted_cvr_percent=2.5,
            current_stock=5,
            lead_time_days=5,
        )
        self.assertTrue(res_low["reorder_needed"])

    # 4. Supplier Negotiation Simulator
    def test_supplier_negotiation_simulator(self) -> None:
        res = SupplierNegotiationSimulator.simulate_volume_tiers(
            supplier_id="cj-dropshipping-us-domestic-hub",
            sku="SKU-TEST-01",
            current_product_cost=7.00,
            current_shipping_cost=3.00,
            monthly_volume=250,
        )

        self.assertEqual(len(res["volume_scenarios"]), 4)
        self.assertEqual(res["target_negotiation_tier"], "TIER_3_DOMESTIC_PRESTOCK")
        self.assertGreater(res["projected_annual_margin_expansion"], 0.0)
        self.assertIn("copy_ready_pitch", res["negotiation_brief"])
        self.assertIn("SKU-TEST-01", res["negotiation_brief"]["copy_ready_pitch"])

    # 5. Global Portfolio Optimizer
    def test_global_portfolio_optimizer(self) -> None:
        optimizer = GlobalPortfolioOptimizer(self.store)
        res = optimizer.optimize_portfolio(total_monthly_marketing_budget=2000.0)

        self.assertEqual(res["catalog_sku_count"], 1)
        self.assertGreater(res["portfolio_monthly_gross_revenue"], 0.0)
        self.assertGreater(res["portfolio_monthly_net_margin"], 0.0)
        self.assertGreaterEqual(res["portfolio_average_stability"], 0.85)
        self.assertEqual(len(res["skus"]), 1)
        self.assertEqual(res["skus"][0]["allocated_ad_budget_pct"], 50.0)


if __name__ == "__main__":
    unittest.main()
