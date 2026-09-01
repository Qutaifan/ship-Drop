"""Unit Tests for ORION Market Research Agent."""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from agency.bots.orion_bot import OrionBot
from agency.core.store import Store

ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = ROOT / "fixtures"


class TestOrionBot(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_orion.db"
        self.store = Store(db_path=self.db_path, data_dir=Path(self.temp_dir))

        with (FIXTURES_DIR / "candidate.sample.json").open("r", encoding="utf-8") as f:
            self.candidate = json.load(f)
        self.store.save_candidate(self.candidate)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # 1. Normalization & Formula Calculations
    def test_metric_formulas(self) -> None:
        orion = OrionBot(self.store)

        # Demand formula: (Velocity * 0.4) + (Search * 0.3) + (Intent * 0.3)
        # (80 * 0.4) + (70 * 0.3) + (90 * 0.3) = 32 + 21 + 27 = 80.0
        d_score = orion.calculate_demand_score(trend_velocity=80.0, search_volume=70.0, buyer_intent=90.0)
        self.assertAlmostEqual(d_score, 80.0)

        # Competition formula: (Ads * 0.5) + (Tightness * 0.3) + (Brand * 0.2)
        # (40 * 0.5) + (60 * 0.3) + (20 * 0.2) = 20 + 18 + 4 = 42.0
        c_score = orion.calculate_competition_score(advertiser_count=40.0, price_band_tightness=60.0, brand_dominance=20.0)
        self.assertAlmostEqual(c_score, 42.0)

        # Sourcing formula: (Domestic * 0.4) + (Stability * 0.3) + (Lead * 0.2) + (CostEff * 0.1)
        # (100 * 0.4) + (95 * 0.3) + (85 * 0.2) + (80 * 0.1) = 40 + 28.5 + 17 + 8 = 93.5
        s_score = orion.calculate_sourcing_score(domestic=100.0, stability=95.0, lead_time=85.0, cost_eff=80.0)
        self.assertAlmostEqual(s_score, 93.5)

    # 2. Viability Score Weighting
    def test_viability_score_weighting(self) -> None:
        orion = OrionBot(self.store)

        # Viability: (Demand * 0.35) + ((100 - Comp) * 0.15) + (Source * 0.25) + (Price * 0.15) + (Risk * 0.10)
        # Demand: 80 * 0.35 = 28.0
        # Comp: 40 -> (100 - 40) * 0.15 = 60 * 0.15 = 9.0
        # Source: 90 * 0.25 = 22.5
        # Price: 80 * 0.15 = 12.0
        # Risk: LOW (100) * 0.10 = 10.0
        # Total = 28.0 + 9.0 + 22.5 + 12.0 + 10.0 = 81.5
        v_score = orion.calculate_viability_score(
            demand_score=80.0,
            competition_score=40.0,
            sourcing_score=90.0,
            price_band_potential=80.0,
            risk_level="LOW",
        )
        self.assertAlmostEqual(v_score, 81.5)

    # 3. Governance Hard Filters (Rejections)
    def test_governance_rejections(self) -> None:
        orion = OrionBot(self.store)

        # Saturation rejected
        rej_sat = orion.apply_governance_filters(
            saturation_level="SATURATED", sourcing_score=85.0, risk_level="LOW",
            trend_velocity=70.0, median_competitor_price=50.0, is_breakable=False,
            is_international_only=False, supplier_stability=0.95, lead_time_days=4,
        )
        self.assertTrue(any("Saturation Level" in r for r in rej_sat))

        # Sourcing score < 60 rejected
        rej_src = orion.apply_governance_filters(
            saturation_level="SWEET-SPOT", sourcing_score=55.0, risk_level="LOW",
            trend_velocity=70.0, median_competitor_price=50.0, is_breakable=False,
            is_international_only=False, supplier_stability=0.95, lead_time_days=4,
        )
        self.assertTrue(any("Sourcing Score" in r for r in rej_src))

        # Risk level = EXTREME rejected
        rej_risk = orion.apply_governance_filters(
            saturation_level="SWEET-SPOT", sourcing_score=85.0, risk_level="EXTREME",
            trend_velocity=70.0, median_competitor_price=50.0, is_breakable=False,
            is_international_only=False, supplier_stability=0.95, lead_time_days=4,
        )
        self.assertTrue(any("Risk Level is EXTREME" in r for r in rej_risk))

        # Low velocity trend rejected
        rej_vel = orion.apply_governance_filters(
            saturation_level="SWEET-SPOT", sourcing_score=85.0, risk_level="LOW",
            trend_velocity=15.0, median_competitor_price=50.0, is_breakable=False,
            is_international_only=False, supplier_stability=0.95, lead_time_days=4,
        )
        self.assertTrue(any("Trend Velocity" in r for r in rej_vel))

        # Low competitor price (< $10) rejected
        rej_price = orion.apply_governance_filters(
            saturation_level="SWEET-SPOT", sourcing_score=85.0, risk_level="LOW",
            trend_velocity=70.0, median_competitor_price=8.50, is_breakable=False,
            is_international_only=False, supplier_stability=0.95, lead_time_days=4,
        )
        self.assertTrue(any("Median Competitor Price" in r for r in rej_price))

        # Breakable + international only rejected
        rej_break = orion.apply_governance_filters(
            saturation_level="SWEET-SPOT", sourcing_score=85.0, risk_level="LOW",
            trend_velocity=70.0, median_competitor_price=50.0, is_breakable=True,
            is_international_only=True, supplier_stability=0.95, lead_time_days=4,
        )
        self.assertTrue(any("breakable AND only internationally sourced" in r for r in rej_break))

        # Supplier stability < 0.70 rejected
        rej_stab = orion.apply_governance_filters(
            saturation_level="SWEET-SPOT", sourcing_score=85.0, risk_level="LOW",
            trend_velocity=70.0, median_competitor_price=50.0, is_breakable=False,
            is_international_only=False, supplier_stability=0.65, lead_time_days=4,
        )
        self.assertTrue(any("Supplier stability" in r for r in rej_stab))

        # Lead time > 7 days rejected
        rej_lead = orion.apply_governance_filters(
            saturation_level="SWEET-SPOT", sourcing_score=85.0, risk_level="LOW",
            trend_velocity=70.0, median_competitor_price=50.0, is_breakable=False,
            is_international_only=False, supplier_stability=0.95, lead_time_days=9,
        )
        self.assertTrue(any("Lead time" in r for r in rej_lead))

    # 4. Strict Section 7 Output Schema
    def test_strict_output_schema(self) -> None:
        orion = OrionBot(self.store)
        res = orion.evaluate_opportunity({
            "product_name": "Magnetic Cable Organizer",
            "category": "Workspace & Tech",
            "trend_velocity": 75.0,
            "search_volume": 80.0,
            "buyer_intent": 85.0,
            "advertiser_count": 8,
            "price_band_tightness": 70.0,
            "brand_dominance": 20.0,
            "domestic_availability": True,
            "supplier_stability": 0.98,
            "lead_time_days": 3,
            "cost_efficiency": 85.0,
            "risk_level": "LOW",
            "median_competitor_price": 62.99,
        })

        expected_keys = [
            "product_name",
            "category",
            "demand_score",
            "competition_score",
            "saturation_level",
            "trend_velocity",
            "median_price_band",
            "recommended_retail",
            "recommended_regions",
            "recommended_angles",
            "sourcing_feasibility",
            "risk_level",
            "viability_score",
            "final_recommendation",
        ]
        for key in expected_keys:
            self.assertIn(key, res)

        self.assertIn(res["saturation_level"], ["UNDER", "SWEET-SPOT", "SATURATED", "OVER-SATURATED"])
        self.assertIn(res["trend_velocity"], ["slow", "medium", "fast", "explosive"])
        self.assertIn(res["risk_level"], ["LOW", "MEDIUM", "HIGH", "EXTREME"])
        self.assertIn(res["final_recommendation"], ["APPROVE", "REJECT", "WATCHLIST"])
        self.assertEqual(res["final_recommendation"], "APPROVE")

    # 5. Opportunity Ranking
    def test_opportunity_ranking(self) -> None:
        orion = OrionBot(self.store)
        opp1 = {
            "product_name": "Strong Winner",
            "trend_velocity": 85.0,
            "search_volume": 90.0,
            "buyer_intent": 90.0,
            "advertiser_count": 6,
            "domestic_availability": True,
            "supplier_stability": 0.98,
            "lead_time_days": 3,
            "median_competitor_price": 65.0,
        }
        opp2 = {
            "product_name": "Weak Saturated",
            "trend_velocity": 40.0,
            "search_volume": 40.0,
            "buyer_intent": 40.0,
            "advertiser_count": 28,  # Saturated
            "domestic_availability": False,
            "supplier_stability": 0.60,  # Failed stability
            "lead_time_days": 12,  # Failed lead time
            "median_competitor_price": 12.0,
        }

        ranked = orion.rank_opportunities([opp2, opp1])
        self.assertEqual(ranked[0]["product_name"], "Strong Winner")
        self.assertEqual(ranked[0]["final_recommendation"], "APPROVE")
        self.assertEqual(ranked[1]["product_name"], "Weak Saturated")
        self.assertEqual(ranked[1]["final_recommendation"], "REJECT")


if __name__ == "__main__":
    unittest.main()
