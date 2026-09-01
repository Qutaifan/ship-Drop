"""Trader Bot - Generates trade signals (BUY, SELL/KILL, SUPPLIER_SWITCH, TREND_ALERT) with numeric hypotheses."""
from __future__ import annotations

import datetime
import re
import uuid
from typing import Any, Dict, List, Optional

from agency.core.scoring_engine import ScoringEngine
from agency.core.store import Store


class TraderBot:
    """TraderBot synthesizes intelligence into actionable trade signals requiring founder approval."""

    def __init__(self, store: Optional[Store] = None, engine: Optional[ScoringEngine] = None):
        self.store = store or Store()
        self.engine = engine or ScoringEngine()

    def generate_recommendation(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        candidate = self.store.get_candidate(candidate_id)
        if not candidate:
            raise ValueError(f"Candidate {candidate_id} not found")

        # Find best supplier for candidate if available
        suppliers = self.store.list_suppliers()
        matching_supplier = suppliers[0] if suppliers else None

        scores = self.engine.score_candidate(candidate, matching_supplier)
        econ = candidate.get("unit_economics", {})
        retail = float(econ.get("gross_selling_price", 29.99))
        net_margin = float(econ.get("contribution_before_ads", econ.get("expected_profit_per_order", 15.0)))
        product_name = candidate.get("product_name", "Product Candidate")
        market = candidate.get("market_config_id", "us-pilot")

        # Demand & Risk specifics from scores details
        trend_details = scores.details.get("trend", {})
        risk_details = scores.details.get("risk", {})
        skeptic_ratio = trend_details.get("skeptic_ratio", 0.20)
        comp_count = trend_details.get("competitor_count", 1)
        has_domestic = risk_details.get("has_domestic_warehouse", False)

        # Dynamic metric predictions
        predicted_ctr = round(2.8 if skeptic_ratio < 0.20 else 2.1, 1)
        if retail <= 35.0:
            predicted_cvr = 3.2
        elif retail <= 75.0:
            predicted_cvr = 2.5
        else:
            predicted_cvr = 1.8

        target_cpa = float(econ.get("target_cpa", 10.50 if market.startswith("us") else 18.00))
        predicted_cpa = round(target_cpa, 2)
        expected_roas = round(retail / predicted_cpa, 2) if predicted_cpa > 0 else 2.5

        # Decision Matrix Thresholds (Calibrated per AGENTS.md)
        if comp_count > 15:
            # Saturation Gate Tripped
            signal_type = "SELL_KILL"
            confidence = "high"
            target_budget = 0.0
            statement = (
                f"Candidate {product_name} fails saturation gate: {comp_count} active advertisers (>15 limit). "
                f"Market is oversaturated; customer acquisition costs will exceed margin."
            )
            action = "Kill candidate due to excessive competitive saturation (>15 advertisers)."
            tier = 2

        elif skeptic_ratio >= 0.50:
            # Proof Burden Gate Tripped (Criterion 3)
            signal_type = "SELL_KILL"
            confidence = "high"
            target_budget = 0.0
            statement = (
                f"Candidate {product_name} fails Criterion 3 Proof Burden: Skeptic-framing ratio is {skeptic_ratio:.0%} (>=50% ceiling). "
                f"Product requires excessive visual explanation that cannot convert on a 3-second silent hook."
            )
            action = "Kill candidate from creative pipeline due to heavy demo proof burden."
            tier = 2

        elif scores.profit_score < 40.0 or net_margin < 12.0:
            # Margin Gate Tripped
            signal_type = "SELL_KILL"
            confidence = "high"
            target_budget = 0.0
            statement = (
                f"Candidate {product_name} fails viability gates: Profit Score {scores.profit_score}/100, "
                f"Net Margin ${net_margin:.2f} (under minimum threshold). Unit economics cannot absorb paid CPA."
            )
            action = "Kill candidate to protect ad budget."
            tier = 2

        elif scores.opportunity_score >= 75.0 and scores.profit_score >= 60.0 and scores.risk_score <= 40.0 and has_domestic:
            # High-Confidence BUY Signal
            signal_type = "BUY"
            confidence = "high" if scores.opportunity_score >= 82.0 else "medium"
            target_budget = 300.0
            statement = (
                f"Candidate {product_name} clears all commercial gates with Opportunity Score {scores.opportunity_score}/100. "
                f"Predicted performance: {predicted_ctr}% CTR, {predicted_cvr}% CVR, ${predicted_cpa:.2f} CPA, "
                f"${net_margin:.2f} net margin (Expected ROAS {expected_roas:.2f}x) under verified domestic fulfillment."
            )
            action = f"Approve ${target_budget:.0f} 7-day creative testing campaign across short-form vertical video (TikTok Spark Ads / Reels)."
            tier = 4

        elif not has_domestic:
            # Supply Chain Optimization Needed
            signal_type = "SUPPLIER_SWITCH"
            confidence = "medium"
            target_budget = 0.0
            statement = (
                f"Candidate {product_name} displays viable consumer demand (Trend: {scores.trend_score}/100), "
                f"but lacks domestic warehouse fulfillment, creating customs duty, import VAT, and carrier delay risks."
            )
            action = "Switch supplier source from China-direct origin to an authorized EU/US domestic warehouse."
            tier = 3

        else:
            # Trend Alert / Monitoring
            signal_type = "TREND_ALERT"
            confidence = "medium"
            target_budget = 0.0
            statement = (
                f"Emerging trend momentum detected for {product_name} (Trend Score: {scores.trend_score}/100). "
                f"Category is maturing; monitor competitor volume and supplier pricing before launching test."
            )
            action = "Monitor category ad velocity and request supplier price breaks for 14 days."
            tier = 1

        sig_clean = signal_type.lower().replace("_", "-")
        cid_clean = re.sub(r"[^a-z0-9-]", "-", candidate_id.lower())[:30].strip("-")
        signal_id = f"sig-{sig_clean}-{cid_clean}-{uuid.uuid4().hex[:6]}"

        signal_data: Dict[str, Any] = {
            "$schema": "../schemas/trade_signal.schema.json",
            "signal_id": signal_id,
            "signal_type": signal_type,
            "candidate_id": candidate_id,
            "product_name": product_name,
            "target_market": "US" if "us" in market else "EU",
            "confidence": confidence,
            "scores": {
                "profit_score": scores.profit_score,
                "risk_score": scores.risk_score,
                "trend_score": scores.trend_score,
                "opportunity_score": scores.opportunity_score,
                "supplier_score": scores.supplier_score,
            },
            "hypothesis": {
                "predicted_ctr_percent": predicted_ctr,
                "predicted_cvr_percent": predicted_cvr,
                "predicted_cpa": predicted_cpa,
                "predicted_net_margin": net_margin,
                "target_ad_budget": target_budget,
                "statement": statement,
            },
            "action_plan": {
                "recommended_action": action,
                "execution_tier": tier,
                "creative_hooks": [
                    f"Hook 1: Pain point & daily friction solved by {product_name}",
                    f"Hook 2: Rapid visual before-and-after transformation in under 3 seconds",
                    f"Hook 3: Minimalist lifestyle aesthetic and unboxing appeal",
                ],
                "suggested_supplier_id": matching_supplier.get("supplier_id") if matching_supplier else None,
                "contingency_rule": f"Auto-pause if CPA exceeds ${predicted_cpa * 1.5:.2f} or CTR drops below {predicted_ctr * 0.6:.1f}%.",
            },
            "approval_status": "PENDING_FOUNDER_REVIEW",
            "approval_id": None,
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "created_by": "trader_bot",
        }

        self.store.save_signal(signal_data)
        return signal_data

    def evaluate_all(self) -> List[Dict[str, Any]]:
        signals = []
        for c in self.store.list_candidates():
            sig = self.generate_recommendation(c["candidate_id"])
            if sig:
                signals.append(sig)
        return signals
