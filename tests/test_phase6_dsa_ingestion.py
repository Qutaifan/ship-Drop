"""Phase-6 Test Suite: Meta Ad Library DSA Ingestion Pipeline & Downstream Economic Wiring."""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from agency.bots.global_portfolio_optimizer import GlobalPortfolioOptimizer
from agency.core.demand_forecasting import DemandForecastingEngine
from agency.core.dynamic_pricing import DynamicPricingEngine
from agency.core.predictive_drift import PredictiveDriftEngine
from agency.core.store import Store
from agency.ingestion.dsa_ad_ingestion import DSAAdIngestionPipeline

ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = ROOT / "fixtures"


class TestPhase6DSAIngestion(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_phase6.db"
        self.store = Store(db_path=self.db_path, data_dir=Path(self.temp_dir))

        with (FIXTURES_DIR / "candidate.sample.json").open("r", encoding="utf-8") as f:
            self.candidate = json.load(f)
        self.store.save_candidate(self.candidate)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # 1. Price Extraction & Ad Normalization
    def test_dsa_price_extraction_and_normalization(self) -> None:
        raw_ads = DSAAdIngestionPipeline.generate_mock_dsa_ads("desk organizer")
        self.assertEqual(len(raw_ads), 6)

        res = DSAAdIngestionPipeline.normalize_dsa_ads(
            raw_ads=raw_ads,
            candidate_id="cand-test-dsa",
            query="desk organizer",
        )

        self.assertEqual(res["candidate_id"], "cand-test-dsa")
        self.assertEqual(res["dsa_protocol_verdict"], "PASS")
        self.assertEqual(res["saturation_status"], "VALIDATED_SWEET_SPOT")
        self.assertEqual(res["distinct_advertisers"], 6)
        self.assertEqual(res["sustained_30d_ads"], 4)
        self.assertGreater(res["median_competitor_price"], 40.0)
        self.assertGreater(res["dsa_demand_multiplier"], 1.0)
        self.assertGreater(res["demand_side_pressure_score"], 0.0)

        # Check competitor_evidence format adheres to candidate schema
        for item in res["competitor_evidence"]:
            self.assertIn("source_url", item)
            self.assertIn("competitor_name", item)
            self.assertIn("observed_price", item)
            self.assertEqual(item["currency"], "EUR")
            self.assertEqual(item["extraction_method"], "meta-ad-library-dsa-api")
            self.assertIn(item["confidence"], ["low", "medium", "high"])

    # 2. Downstream Demand Forecasting Wiring
    def test_dsa_demand_forecasting_multiplier(self) -> None:
        # Baseline demand without multiplier
        base_demand = DemandForecastingEngine.forecast_demand(
            daily_ad_spend=50.0,
            cpc=0.85,
            predicted_cvr_percent=2.0,
            dsa_demand_multiplier=1.0,
        )

        # Demand with 1.25x DSA competitor validation multiplier
        boosted_demand = DemandForecastingEngine.forecast_demand(
            daily_ad_spend=50.0,
            cpc=0.85,
            predicted_cvr_percent=2.0,
            dsa_demand_multiplier=1.25,
        )

        self.assertGreater(boosted_demand["daily_demand_units"], base_demand["daily_demand_units"])
        self.assertGreater(boosted_demand["weekly_demand_units"], base_demand["weekly_demand_units"])

    # 3. Downstream Dynamic Pricing Competitor Guardrail
    def test_dsa_dynamic_pricing_competitor_band(self) -> None:
        # If competitor anchor is $70.00, price cannot exceed 1.15 * 70 = $80.50
        pricing = DynamicPricingEngine.optimize_price(
            current_retail=49.99,
            landed_cost=10.00,
            stock_depth=200,
            competitor_price=70.00,
        )
        self.assertLessEqual(pricing["recommended_retail"], 80.50)
        self.assertGreaterEqual(pricing["recommended_retail"], 62.00)
        self.assertTrue(pricing["cac_gate_cleared"])

    # 4. Downstream Predictive Drift Competitive Pressure
    def test_dsa_predictive_drift_pressure(self) -> None:
        stabs = [0.95, 0.94, 0.93, 0.92]
        stocks = [1000, 950, 900, 850]
        costs = [5.0, 5.0, 5.0, 5.0]
        defects = [1.0, 1.0, 1.0, 1.0]

        # Zero competitor pressure
        res_low_p = PredictiveDriftEngine.evaluate_predictive_drift(
            stabs, stocks, costs, defects, demand_side_pressure_score=0.0
        )

        # High competitor saturation pressure (80/100)
        res_high_p = PredictiveDriftEngine.evaluate_predictive_drift(
            stabs, stocks, costs, defects, demand_side_pressure_score=80.0
        )

        self.assertGreater(res_high_p["predictive_drift_score"], res_low_p["predictive_drift_score"])
        self.assertIn("Elevated Meta DSA competitor pressure", " ".join(res_high_p["reasons"]))

    # 5. Downstream Global Portfolio Optimization with Competitor Evidence
    def test_dsa_portfolio_optimization_integration(self) -> None:
        cand = dict(self.candidate)
        cand["competitor_evidence"] = [
            {
                "source_url": "https://facebook.com/ads/1",
                "competitor_name": "Euro Desk Official",
                "product_url": None,
                "observed_price": 72.00,
                "currency": "EUR",
                "extraction_method": "meta-ad-library-dsa-api",
                "confidence": "high",
            }
        ]
        self.store.save_candidate(cand)

        optimizer = GlobalPortfolioOptimizer(self.store)
        res = optimizer.optimize_portfolio(total_monthly_marketing_budget=1500.0)

        self.assertEqual(res["catalog_sku_count"], 1)
        self.assertGreater(res["portfolio_monthly_gross_revenue"], 0.0)
        self.assertLessEqual(res["skus"][0]["optimized_retail"], 82.80)  # Competitor 72.00 * 1.15 = 82.80


if __name__ == "__main__":
    unittest.main()
