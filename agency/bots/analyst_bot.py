"""Analyst Bot - Quantitative margin analysis, CAC gates, and profit evaluation."""
from __future__ import annotations

from typing import Any, Dict, Optional

from agency.core.scoring_engine import ScoringEngine
from agency.core.store import Store


class AnalystBot:
    """Analyst Bot applies quantitative margin formulas and CAC gates."""

    def __init__(self, store: Optional[Store] = None, engine: Optional[ScoringEngine] = None):
        self.store = store or Store()
        self.engine = engine or ScoringEngine()

    def analyze_candidate(self, candidate_id: str) -> Dict[str, Any]:
        """Runs quantitative margin math and returns detailed evaluation."""
        candidate = self.store.get_candidate(candidate_id)
        if not candidate:
            raise ValueError(f"Candidate {candidate_id} not found in store")

        econ = candidate.get("unit_economics", {})
        market = candidate.get("market_config_id", "us-pilot")
        profit_eval = self.engine.score_profit(econ, market)

        # Update candidate with calculated fields
        if profit_eval["score"] >= 65.0:
            status = "VALIDATION_READY"
            recommendation = "founder_review"
        elif profit_eval["score"] >= 45.0:
            status = "HOLD"
            recommendation = "hold"
        else:
            status = "REJECTED"
            recommendation = "reject"

        candidate["status"] = status
        candidate["recommendation"] = recommendation
        candidate["rationale"] = (
            f"AnalystBot Profit Score: {profit_eval['score']}/100. "
            f"Net Margin: ${profit_eval['net_margin']:.2f}, "
            f"COGS Multiple: {profit_eval['cogs_multiple']}x, "
            f"CAC Buffer: {profit_eval['cac_multiple']}x CPA."
        )

        self.store.save_candidate(candidate)
        return {
            "candidate_id": candidate_id,
            "status": status,
            "recommendation": recommendation,
            "profit_evaluation": profit_eval,
        }

    def analyze_all(self) -> Dict[str, Any]:
        results = {}
        for c in self.store.list_candidates():
            cid = c["candidate_id"]
            results[cid] = self.analyze_candidate(cid)
        return results
