"""ORION - Market Research Agent for Hermes-Ecom.

Identifies, evaluates, and ranks product opportunities using structured market intelligence.
Produces deterministic, governance-compliant output for downstream agents (SCOUT, PRICER, FORECASTER, ALLOCATOR).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from agency.core.store import Store

ROOT = Path(__file__).resolve().parents[2]


class OrionBot:
    """ORION: Market Research Agent for Hermes-Ecom.
    Executes the 6-stage evaluation pipeline according to strict governance and metric formulas.
    """

    RISK_MAP = {
        "LOW": 100.0,
        "MEDIUM": 70.0,
        "HIGH": 40.0,
        "EXTREME": 0.0,
    }

    def __init__(self, store: Optional[Store] = None):
        self.store = store or Store()

    # ────────────────────────────────────────────────────────
    # SECTION 2 — NORMALIZATION HELPERS (0–100 SCALE)
    # ────────────────────────────────────────────────────────

    @staticmethod
    def normalize_demand(
        trend_velocity: float,
        search_volume: float,
        buyer_intent: float,
    ) -> Tuple[float, float, float]:
        """Normalize demand inputs to 0-100."""
        # trend_velocity: expected 0-100, cap if necessary
        norm_velocity = max(0.0, min(100.0, float(trend_velocity)))
        # search_volume: if raw volume > 100 (e.g. 50,000 monthly), scale log or clamp
        if search_volume > 100:
            # Scaled: 100,000+ = 100, 10,000 = 70, 1,000 = 40
            import math
            norm_search = max(0.0, min(100.0, (math.log10(max(1.0, search_volume)) - 2.0) * 33.3))
        else:
            norm_search = max(0.0, min(100.0, float(search_volume)))
        norm_intent = max(0.0, min(100.0, float(buyer_intent)))
        return round(norm_velocity, 2), round(norm_search, 2), round(norm_intent, 2)

    @staticmethod
    def normalize_competition(
        advertiser_count: float,
        price_band_tightness: float,
        brand_dominance: float,
    ) -> Tuple[float, float, float]:
        """Normalize competition inputs to 0-100."""
        # advertiser count: 0-20+ ads scaled to 0-100
        if advertiser_count <= 25:
            norm_ads = max(0.0, min(100.0, float(advertiser_count) * 4.0))
        else:
            norm_ads = 100.0
        norm_tightness = max(0.0, min(100.0, float(price_band_tightness)))
        norm_brand = max(0.0, min(100.0, float(brand_dominance)))
        return round(norm_ads, 2), round(norm_tightness, 2), round(norm_brand, 2)

    @staticmethod
    def normalize_sourcing(
        domestic_available: bool,
        stability: float,
        lead_time_days: int,
        cost_efficiency: float,
    ) -> Tuple[float, float, float, float]:
        """Normalize sourcing feasibility to 0-100."""
        norm_domestic = 100.0 if domestic_available else 0.0
        # stability: 0.0 - 1.0 or 0 - 100
        norm_stability = (stability * 100.0) if stability <= 1.0 else stability
        norm_stability = max(0.0, min(100.0, float(norm_stability)))

        # lead time invert scale: shorter = higher
        # 1-3 days = 100, 4 days = 85, 5 days = 70, 6 days = 55, 7 days = 40, >14 days = 0
        if lead_time_days <= 3:
            norm_lead = 100.0
        elif lead_time_days <= 7:
            norm_lead = max(40.0, 100.0 - (lead_time_days - 3) * 15.0)
        else:
            norm_lead = max(0.0, 40.0 - (lead_time_days - 7) * 5.0)

        norm_efficiency = max(0.0, min(100.0, float(cost_efficiency)))
        return norm_domestic, round(norm_stability, 2), round(norm_lead, 2), round(norm_efficiency, 2)

    @classmethod
    def normalize_risk(cls, risk_level: str) -> float:
        """LOW -> 100, MEDIUM -> 70, HIGH -> 40, EXTREME -> 0."""
        return cls.RISK_MAP.get(risk_level.upper(), 70.0)

    # ────────────────────────────────────────────────────────
    # SECTION 3 — METRIC FORMULAS
    # ────────────────────────────────────────────────────────

    @staticmethod
    def calculate_demand_score(trend_velocity: float, search_volume: float, buyer_intent: float) -> float:
        """Demand Score = (Trend Velocity × 0.4) + (Search Volume × 0.3) + (Buyer Intent × 0.3)"""
        score = (trend_velocity * 0.4) + (search_volume * 0.3) + (buyer_intent * 0.3)
        return round(max(0.0, min(100.0, score)), 2)

    @staticmethod
    def calculate_competition_score(advertiser_count: float, price_band_tightness: float, brand_dominance: float) -> float:
        """Competition Score = (Advertiser Count × 0.5) + (Price Band Tightness × 0.3) + (Brand Dominance × 0.2)"""
        score = (advertiser_count * 0.5) + (price_band_tightness * 0.3) + (brand_dominance * 0.2)
        return round(max(0.0, min(100.0, score)), 2)

    @staticmethod
    def calculate_sourcing_score(domestic: float, stability: float, lead_time: float, cost_eff: float) -> float:
        """Sourcing Score = (Domestic Availability × 0.4) + (Stability × 0.3) + (Lead Time × 0.2) + (Cost Efficiency × 0.1)"""
        score = (domestic * 0.4) + (stability * 0.3) + (lead_time * 0.2) + (cost_eff * 0.1)
        return round(max(0.0, min(100.0, score)), 2)

    # ────────────────────────────────────────────────────────
    # SECTION 4 & 5 — GOVERNANCE FILTERS & WEIGHTING MODEL
    # ────────────────────────────────────────────────────────

    @classmethod
    def apply_governance_filters(
        cls,
        saturation_level: str,
        sourcing_score: float,
        risk_level: str,
        trend_velocity: float,
        median_competitor_price: float,
        is_breakable: bool,
        is_international_only: bool,
        supplier_stability: float,
        lead_time_days: int,
    ) -> List[str]:
        """Returns list of rejection reasons if any governance rule is violated."""
        rejections: List[str] = []

        if saturation_level.upper() in ["SATURATED", "OVER-SATURATED"]:
            rejections.append(f"Saturation Level is {saturation_level}")

        if sourcing_score < 60.0:
            rejections.append(f"Sourcing Score {sourcing_score} < 60.0 threshold")

        if risk_level.upper() == "EXTREME":
            rejections.append("Risk Level is EXTREME (auto-reject)")

        if trend_velocity < 20.0:
            rejections.append(f"Trend Velocity {trend_velocity} < 20.0 (low-velocity trend)")

        if median_competitor_price < 10.0:
            rejections.append(f"Median Competitor Price ${median_competitor_price:.2f} < $10.00 (low-margin category)")

        if is_breakable and is_international_only:
            rejections.append("Product is breakable AND only internationally sourced (high return/customs risk)")

        stab_val = supplier_stability if supplier_stability <= 1.0 else supplier_stability / 100.0
        if stab_val < 0.70:
            rejections.append(f"Supplier stability {stab_val:.2f} < 0.70 threshold")

        if lead_time_days > 7:
            rejections.append(f"Lead time {lead_time_days} days > 7 days threshold")

        return rejections

    @classmethod
    def calculate_viability_score(
        cls,
        demand_score: float,
        competition_score: float,
        sourcing_score: float,
        price_band_potential: float,
        risk_level: str,
    ) -> float:
        """Viability Score =
        (Demand × 0.35) +
        ((100 - Competition) × 0.15) +
        (Sourcing × 0.25) +
        (Price Band Potential × 0.15) +
        (Risk Modifier × 0.10)
        """
        risk_mod = cls.normalize_risk(risk_level)
        comp_inv = max(0.0, 100.0 - competition_score)
        v_score = (
            (demand_score * 0.35)
            + (comp_inv * 0.15)
            + (sourcing_score * 0.25)
            + (price_band_potential * 0.15)
            + (risk_mod * 0.10)
        )
        return round(max(0.0, min(100.0, v_score)), 2)

    # ────────────────────────────────────────────────────────
    # SECTION 6 & 7 — PIPELINE & OUTPUT GENERATION
    # ────────────────────────────────────────────────────────

    def evaluate_opportunity(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        """Executes full ORION evaluation pipeline and returns strict Section 7 schema."""
        product_name = signals.get("product_name", "Target SKU")
        category = signals.get("category", "General Home & Utility")

        # 1. Raw signals extraction
        raw_velocity = float(signals.get("trend_velocity", 65.0))
        raw_search = float(signals.get("search_volume", 75.0))
        raw_intent = float(signals.get("buyer_intent", 80.0))

        raw_advertisers = float(signals.get("advertiser_count", 8.0))
        raw_tightness = float(signals.get("price_band_tightness", 60.0))
        raw_dominance = float(signals.get("brand_dominance", 30.0))

        domestic_avail = bool(signals.get("domestic_availability", True))
        raw_stability = float(signals.get("supplier_stability", 0.95))
        lead_time = int(signals.get("lead_time_days", 4))
        raw_cost_eff = float(signals.get("cost_efficiency", 85.0))

        risk_level = signals.get("risk_level", "LOW").upper()
        median_price = float(signals.get("median_competitor_price", 64.99))
        price_spread = signals.get("price_band_spread", (55.0, 75.0))
        price_potential = float(signals.get("price_band_potential", 80.0))

        is_breakable = bool(signals.get("is_breakable", False))
        is_international_only = not domestic_avail

        # Saturation level determination
        sat_input = signals.get("saturation_level")
        if sat_input:
            saturation_level = sat_input.upper()
        elif raw_advertisers <= 3:
            saturation_level = "UNDER"
        elif raw_advertisers <= 15:
            saturation_level = "SWEET-SPOT"
        elif raw_advertisers <= 25:
            saturation_level = "SATURATED"
        else:
            saturation_level = "OVER-SATURATED"

        # 2. Normalize
        norm_v, norm_s, norm_i = self.normalize_demand(raw_velocity, raw_search, raw_intent)
        norm_ads, norm_tight, norm_brand = self.normalize_competition(raw_advertisers, raw_tightness, raw_dominance)
        norm_dom, norm_stab, norm_lead, norm_eff = self.normalize_sourcing(
            domestic_avail, raw_stability, lead_time, raw_cost_eff
        )

        # 3. Compute Metrics
        demand_score = self.calculate_demand_score(norm_v, norm_s, norm_i)
        competition_score = self.calculate_competition_score(norm_ads, norm_tight, norm_brand)
        sourcing_score = self.calculate_sourcing_score(norm_dom, norm_stab, norm_lead, norm_eff)

        # 4. Governance Filters
        rejections = self.apply_governance_filters(
            saturation_level=saturation_level,
            sourcing_score=sourcing_score,
            risk_level=risk_level,
            trend_velocity=norm_v,
            median_competitor_price=median_price,
            is_breakable=is_breakable,
            is_international_only=is_international_only,
            supplier_stability=raw_stability,
            lead_time_days=lead_time,
        )

        # 5. Compute Viability Score
        viability_score = self.calculate_viability_score(
            demand_score=demand_score,
            competition_score=competition_score,
            sourcing_score=sourcing_score,
            price_band_potential=price_potential,
            risk_level=risk_level,
        )

        # 6. Recommendation
        if rejections:
            final_rec = "REJECT"
        elif viability_score >= 75.0:
            final_rec = "APPROVE"
        elif viability_score >= 55.0:
            final_rec = "WATCHLIST"
        else:
            final_rec = "REJECT"

        # Velocity classification
        if norm_v >= 85.0:
            velocity_str = "explosive"
        elif norm_v >= 60.0:
            velocity_str = "fast"
        elif norm_v >= 35.0:
            velocity_str = "medium"
        else:
            velocity_str = "slow"

        # Price band formatting
        if isinstance(price_spread, (list, tuple)) and len(price_spread) == 2:
            price_band_str = f"${int(price_spread[0])}–${int(price_spread[1])}"
        else:
            price_band_str = f"${int(median_price * 0.85)}–${int(median_price * 1.15)}"

        rec_retail = f"${signals.get('recommended_retail_price', median_price):.2f}"
        rec_regions = signals.get("recommended_regions", ["US", "EU", "UK"])
        rec_angles = signals.get("recommended_angles", ["pain point", "aesthetic", "utility"])

        output: Dict[str, Any] = {
            "product_name": product_name,
            "category": category,
            "demand_score": demand_score,
            "competition_score": competition_score,
            "saturation_level": saturation_level,
            "trend_velocity": velocity_str,
            "median_price_band": price_band_str,
            "recommended_retail": rec_retail,
            "recommended_regions": rec_regions,
            "recommended_angles": rec_angles,
            "sourcing_feasibility": sourcing_score,
            "risk_level": risk_level,
            "viability_score": viability_score,
            "final_recommendation": final_rec,
        }

        if rejections:
            output["governance_rejection_reasons"] = rejections

        # Audit log in store
        self.store.log_audit("ORION_OPPORTUNITY_EVALUATED", {
            "product_name": product_name,
            "viability_score": viability_score,
            "final_recommendation": final_rec,
            "rejections": rejections,
        })

        return output

    def evaluate_candidate(self, candidate_id: str) -> Dict[str, Any]:
        """Pulls candidate and verified supplier telemetry from Store and evaluates with ORION."""
        cand = self.store.get_candidate(candidate_id)
        if not cand:
            raise ValueError(f"Candidate {candidate_id} not found in store.")

        # Extract verified supplier data
        verifications = self.store.list_supplier_verifications(candidate_id=candidate_id)
        top_ver = verifications[0] if verifications else {}

        # Extract competitor DSA evidence
        comp_evidence = cand.get("competitor_evidence", [])
        adv_count = len(comp_evidence)
        observed_prices = [e.get("observed_price", 0.0) for e in comp_evidence if e.get("observed_price", 0.0) > 0]
        median_price = (
            sorted(observed_prices)[len(observed_prices) // 2]
            if observed_prices
            else float(cand.get("unit_economics", {}).get("gross_selling_price", 62.99))
        )

        stability = float(top_ver.get("stability_score", 0.95))
        lead_time = int(top_ver.get("lead_days_max", 4))
        origin = top_ver.get("origin_country", "US")
        domestic = origin in ["US", "DE", "NL", "FR", "ES", "IT"]

        signals = {
            "product_name": cand.get("product_name", candidate_id),
            "category": cand.get("category", "Home Organization & Workspace"),
            "trend_velocity": 75.0,
            "search_volume": 80.0,
            "buyer_intent": 85.0,
            "advertiser_count": adv_count if adv_count > 0 else 6,
            "price_band_tightness": 70.0,
            "brand_dominance": 25.0,
            "domestic_availability": domestic,
            "supplier_stability": stability,
            "lead_time_days": lead_time,
            "cost_efficiency": 85.0,
            "risk_level": "LOW",
            "median_competitor_price": median_price,
            "recommended_retail_price": float(cand.get("unit_economics", {}).get("gross_selling_price", median_price)),
            "recommended_regions": ["US", "EU"],
            "recommended_angles": ["pain point", "aesthetic", "utility"],
        }

        return self.evaluate_opportunity(signals)

    def rank_opportunities(self, candidates_or_signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ranks a list of opportunities by viability_score descending."""
        evaluated = [self.evaluate_opportunity(s) for s in candidates_or_signals]
        return sorted(evaluated, key=lambda x: (x["final_recommendation"] == "APPROVE", x["viability_score"]), reverse=True)
