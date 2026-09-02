"""Opportunity Scoring Engine - Pure Functions Only.

No database calls. No API calls. No side effects. 100% deterministic mathematical calculations.

Functions:
1. profit_score()
2. risk_score()
3. trend_score()
4. supplier_score()
5. visibility_score()
6. final_score()
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

# Benchmark Constants
MEDIAN_CPA_USD = 12.00
MEDIAN_CPA_EUR = 21.48
EU_MIN_PRICE = 62.00
EU_MAX_PRICE = 93.00
US_MIN_PRICE = 20.00
US_MAX_PRICE = 99.00


def profit_score(
    gross_price: float,
    product_cost: float,
    shipping_cost: float,
    net_margin: float,
    currency: str = "USD",
    duty: float = 0.0,
) -> Dict[str, Any]:
    """Pure function: Computes Profit Score (0-100) from unit economics."""
    landed_cost = product_cost + shipping_cost + duty
    if gross_price <= 0 or landed_cost <= 0 or net_margin <= 0:
        return {
            "score": 0.0,
            "cogs_multiple": 0.0,
            "net_margin": round(net_margin, 2),
            "cac_multiple": 0.0,
            "subscores": {"cogs_score": 0.0, "margin_mag_score": 0.0, "cac_score": 0.0, "price_band_score": 0.0},
        }

    # 1. Margin vs COGS multiple (Target >= 3.0x COGS, min 2.0x) - max 30 pts
    cogs_multiple = net_margin / landed_cost if landed_cost > 0 else 0
    if cogs_multiple >= 3.0:
        cogs_s = 30.0
    elif cogs_multiple >= 2.0:
        cogs_s = 20.0 + 10.0 * ((cogs_multiple - 2.0) / 1.0)
    elif cogs_multiple >= 1.5:
        cogs_s = 10.0 + 10.0 * ((cogs_multiple - 1.5) / 0.5)
    else:
        cogs_s = max(0.0, cogs_multiple * 6.0)

    # 2. Net margin magnitude (Target >= 15.00 EUR/USD) - max 25 pts
    if net_margin >= 25.0:
        margin_mag_s = 25.0
    elif net_margin >= 15.0:
        margin_mag_s = 15.0 + 10.0 * ((net_margin - 15.0) / 10.0)
    elif net_margin > 0:
        margin_mag_s = 15.0 * (net_margin / 15.0)
    else:
        margin_mag_s = 0.0

    # 3. CAC Buffer Gate (Net margin must be >= 2x median CPA) - max 25 pts
    median_cpa = MEDIAN_CPA_EUR if currency == "EUR" else MEDIAN_CPA_USD
    cac_multiple = net_margin / median_cpa if median_cpa > 0 else 0
    if cac_multiple >= 2.0:
        cac_s = 25.0
    elif cac_multiple >= 1.5:
        cac_s = 15.0 + 10.0 * ((cac_multiple - 1.5) / 0.5)
    elif cac_multiple >= 1.0:
        cac_s = 5.0 + 10.0 * ((cac_multiple - 1.0) / 0.5)
    else:
        cac_s = 0.0

    # 4. Target retail pricing band - max 20 pts
    min_p = EU_MIN_PRICE if currency == "EUR" else US_MIN_PRICE
    max_p = EU_MAX_PRICE if currency == "EUR" else US_MAX_PRICE

    if min_p <= gross_price <= max_p:
        price_band_s = 20.0
    elif gross_price < min_p:
        price_band_s = max(0.0, 20.0 * (gross_price / min_p))
    else:
        price_band_s = max(5.0, 20.0 - (gross_price - max_p) * 0.3)

    total = round(min(100.0, max(0.0, cogs_s + margin_mag_s + cac_s + price_band_s)), 1)
    return {
        "score": total,
        "cogs_multiple": round(cogs_multiple, 2),
        "net_margin": round(net_margin, 2),
        "cac_multiple": round(cac_multiple, 2),
        "subscores": {
            "cogs_score": round(cogs_s, 1),
            "margin_mag_score": round(margin_mag_s, 1),
            "cac_score": round(cac_s, 1),
            "price_band_score": round(price_band_s, 1),
        },
    }


def risk_score(
    has_domestic_warehouse: bool,
    is_electronics: bool = False,
    is_fragile: bool = False,
    is_apparel: bool = False,
    has_ip_risk: bool = False,
    compliance_unknowns_count: int = 0,
) -> Dict[str, Any]:
    """Pure function: Computes Risk Score (0-100, where 0 is safest) and Safety Score (100 - risk)."""
    base_risk = 10.0
    flags: List[str] = []

    if not has_domestic_warehouse:
        base_risk += 30.0
        flags.append("Non-domestic fulfillment (De Minimis customs duty & carrier clearance risk)")

    if compliance_unknowns_count > 0:
        base_risk += min(25.0, compliance_unknowns_count * 8.0)
        flags.append(f"{compliance_unknowns_count} compliance unknown(s) flagged")

    if is_electronics:
        base_risk += 18.0
        flags.append("Electronics / Battery component (WEEE / return hazard)")

    if is_fragile:
        base_risk += 20.0
        flags.append("Fragile material (Breakage transit risk)")

    if is_apparel:
        base_risk += 22.0
        flags.append("Sizing variations (Apparel sizing return curve)")

    if has_ip_risk:
        base_risk += 40.0
        flags.append("Trademark / copyright conflict risk")

    final_risk = round(min(100.0, max(5.0, base_risk)), 1)
    return {
        "score": final_risk,
        "safety_score": round(100.0 - final_risk, 1),
        "has_domestic_warehouse": has_domestic_warehouse,
        "risk_flags": flags,
    }


def trend_score(
    competitor_count: int,
    has_social_momentum: bool = True,
    has_search_momentum: bool = True,
    skeptic_ratio: float = 0.20,
) -> Dict[str, Any]:
    """Pure function: Computes Trend & Demand Score (0-100)."""
    score = 0.0

    # Competitor saturation curve
    if 4 <= competitor_count <= 12:
        score += 35.0
    elif 1 <= competitor_count < 4:
        score += 20.0
    elif competitor_count > 15:
        score += 15.0
    else:
        score += 5.0

    # Social and search momentum
    score += 25.0 if has_social_momentum else 10.0
    score += 20.0 if has_search_momentum else 10.0

    # Skeptic ratio screen
    if skeptic_ratio < 0.25:
        score += 20.0
    elif skeptic_ratio < 0.40:
        score += 12.0
    elif skeptic_ratio < 0.50:
        score += 5.0
    else:
        score -= 25.0

    final_trend = round(min(100.0, max(0.0, score)), 1)
    return {
        "score": final_trend,
        "competitor_count": competitor_count,
        "has_social_momentum": has_social_momentum,
        "has_search_momentum": has_search_momentum,
        "skeptic_ratio": skeptic_ratio,
    }


def supplier_score(
    processing_days: int,
    shipping_max_days: int,
    avg_shipping_cost: float,
    reliability_rating: float,
    dispute_rate_percent: float,
    is_domestic: bool,
    is_tracked: bool = True,
) -> Dict[str, Any]:
    """Pure function: Computes Supplier Score (0-100)."""
    # Speed
    speed = 100.0
    if processing_days > 2:
        speed -= (processing_days - 2) * 15.0
    if shipping_max_days > 7:
        speed -= (shipping_max_days - 7) * 8.0
    speed = max(0.0, min(100.0, speed))

    # Cost
    cost_s = max(20.0, min(100.0, 110.0 - avg_shipping_cost * 8.0))

    # Reliability
    rel = (reliability_rating / 5.0) * 60.0 + max(0.0, (5.0 - dispute_rate_percent) * 8.0)
    rel = max(0.0, min(100.0, rel))

    # Compliance
    comp = 50.0 + (40.0 if is_domestic else 0.0) + (10.0 if is_tracked else 0.0)
    comp = max(0.0, min(100.0, comp))

    total = round(0.30 * speed + 0.25 * cost_s + 0.25 * rel + 0.20 * comp, 1)
    return {
        "score": total,
        "fulfillment_speed": round(speed, 1),
        "cost_competitiveness": round(cost_s, 1),
        "reliability": round(rel, 1),
        "compliance": round(comp, 1),
    }


def visibility_score(
    p_score: float,
    r_score: float,
    t_score: float,
    s_score: float,
) -> Dict[str, Any]:
    """Pure function: Computes Agentic Visibility / Opportunity Index (0-100)."""
    safety = 100.0 - r_score
    raw = (0.35 * p_score) + (0.25 * safety) + (0.25 * t_score) + (0.15 * s_score)
    gate_tripped = False

    # Hard gate capping
    if p_score < 40.0:
        raw = min(raw, 45.0)
        gate_tripped = True
    if r_score > 70.0:
        raw = min(raw, 40.0)
        gate_tripped = True

    final_val = round(min(100.0, max(0.0, raw)), 1)
    return {
        "score": final_val,
        "raw_score": round(raw, 1),
        "hard_gate_tripped": gate_tripped,
    }


def final_score(
    profit_res: Dict[str, Any],
    risk_res: Dict[str, Any],
    trend_res: Dict[str, Any],
    supplier_res: Dict[str, Any],
) -> Dict[str, Any]:
    """Pure function: Synthesizes subscores into final opportunity assessment and verdict."""
    p_score = profit_res["score"]
    r_score = risk_res["score"]
    t_score = trend_res["score"]
    s_score = supplier_res["score"]

    vis_res = visibility_score(p_score, r_score, t_score, s_score)
    opp_score = vis_res["score"]

    if opp_score >= 80.0 and p_score >= 65.0 and r_score <= 40.0:
        verdict = "PRIME_OPPORTUNITY"
    elif opp_score >= 65.0 and p_score >= 50.0:
        verdict = "VIABLE"
    elif opp_score >= 45.0:
        verdict = "HOLD"
    else:
        verdict = "REJECT"

    return {
        "opportunity_score": opp_score,
        "profit_score": p_score,
        "risk_score": r_score,
        "trend_score": t_score,
        "supplier_score": s_score,
        "verdict": verdict,
        "details": {
            "profit": profit_res,
            "risk": risk_res,
            "trend": trend_res,
            "supplier": supplier_res,
            "visibility": vis_res,
        },
    }


# High-Level Object Wrapper for backwards-compatibility with Bot callers
class ScoringEngine:
    """Wrapper that translates dictionary models into pure function calls."""

    def score_profit(self, unit_econ: Dict[str, Any], market: str = "US") -> Dict[str, Any]:
        gross = float(unit_econ.get("gross_selling_price", 0.0))
        cost = float(unit_econ.get("product_cost", 0.0))
        ship = float(unit_econ.get("shipping_cost", 0.0))
        duty = float(unit_econ.get("duty", 0.0))
        net = float(unit_econ.get("contribution_before_ads", unit_econ.get("expected_profit_per_order", 0.0)))
        currency = unit_econ.get("currency", "USD")
        return profit_score(gross, cost, ship, net, currency, duty)

    def score_risk(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        supplier_ev = candidate.get("supplier_evidence", [])
        mkt = candidate.get("market_config_id", "")
        has_dom = any(
            (mkt.startswith("us") and s.get("warehouse_country") == "US")
            or (mkt.startswith("eu") and s.get("warehouse_country") in ["DE", "PL", "FR", "NL", "ES", "IT"])
            for s in supplier_ev
        )
        pname = candidate.get("product_name", "").lower()
        is_elec = any(w in pname for w in ["battery", "electric", "motor", "electronic", "rechargeable"])
        is_frag = any(w in pname for w in ["glass", "ceramic", "porcelain", "crystal", "fragile"])
        is_app = any(w in pname for w in ["shirt", "pants", "dress", "shoes", "jacket", "hoodie", "ring"])
        is_ip = any(w in pname for w in ["disney", "marvel", "nike", "apple", "lego", "dyson"])
        unknowns = len(candidate.get("compliance_unknowns", []))

        return risk_score(has_dom, is_elec, is_frag, is_app, is_ip, unknowns)

    def score_trend(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        comp_count = len(candidate.get("competitor_evidence", []))
        has_soc = any(d.get("signal_type") == "video" for d in candidate.get("demand_evidence", []))
        has_src = any(d.get("signal_type") == "trend" for d in candidate.get("demand_evidence", []))
        skeptic = 0.20
        for d in candidate.get("demand_evidence", []):
            if "skeptic" in d.get("metric_name", "").lower():
                try:
                    skeptic = float(d.get("metric_value", 0.20))
                except (ValueError, TypeError):
                    pass
        return trend_score(comp_count, has_soc, has_src, skeptic)

    def score_supplier(self, supplier: Dict[str, Any]) -> Any:
        lead = supplier.get("typical_lead_days", {})
        proc = lead.get("processing_days", 3)
        ship_max = lead.get("shipping_max_days", 14)
        tiers = supplier.get("shipping_tiers", [])
        avg_cost = sum(t.get("base_cost", 10.0) for t in tiers) / max(1, len(tiers))
        rating = supplier.get("reliability_rating", 4.0)
        dispute = supplier.get("dispute_rate_percent", 3.0)
        is_dom = supplier.get("us_domestic_stock", False) or supplier.get("eu_anti_deminimis_ready", False)
        is_track = any(t.get("tracked", True) for t in tiers)

        res = supplier_score(proc, ship_max, avg_cost, rating, dispute, is_dom, is_track)
        # Adapt to expected return format
        class SupplierResult:
            def __init__(self, d: Dict[str, Any]):
                self.total = d["score"]
                self.fulfillment_speed = d["fulfillment_speed"]
                self.cost_competitiveness = d["cost_competitiveness"]
                self.reliability = d["reliability"]
                self.compliance = d["compliance"]
                self.verdict = "PREFERRED" if self.total >= 80 else ("ACCEPTABLE" if self.total >= 65 else "HIGH_RISK")
            def to_dict(self):
                return {"total": self.total, "fulfillment_speed": self.fulfillment_speed, "cost_competitiveness": self.cost_competitiveness, "reliability": self.reliability, "compliance": self.compliance, "verdict": self.verdict}
        return SupplierResult(res)

    def score_candidate(self, candidate: Dict[str, Any], supplier: Optional[Dict[str, Any]] = None) -> Any:
        p_res = self.score_profit(candidate.get("unit_economics", {}), candidate.get("market_config_id", "us-pilot"))
        r_res = self.score_risk(candidate)
        t_res = self.score_trend(candidate)
        if supplier:
            s_res = self.score_supplier(supplier)
            s_dict = s_res.to_dict()
            s_dict["score"] = s_res.total
        else:
            s_dict = {"score": 80.0 if r_res["has_domestic_warehouse"] else 50.0}

        fin = final_score(p_res, r_res, t_res, s_dict)
        class CandidateScores:
            def __init__(self, f: Dict[str, Any]):
                self.profit_score = f["profit_score"]
                self.risk_score = f["risk_score"]
                self.trend_score = f["trend_score"]
                self.supplier_score = f["supplier_score"]
                self.opportunity_score = f["opportunity_score"]
                self.verdict = f["verdict"]
                self.details = f["details"]
        return CandidateScores(fin)
