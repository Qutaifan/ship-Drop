"""Sentiment & Demand Bot - Analyzes social momentum, customer reviews, and proof burden."""
from __future__ import annotations

from typing import Any, Dict, Optional

from agency.core.scoring_engine import ScoringEngine
from agency.core.store import Store


class SentimentBot:
    """SentimentBot evaluates proof burden, review sentiment, and viral demand signals."""

    def __init__(self, store: Optional[Store] = None, engine: Optional[ScoringEngine] = None):
        self.store = store or Store()
        self.engine = engine or ScoringEngine()

    def evaluate_candidate(self, candidate_id: str) -> Dict[str, Any]:
        candidate = self.store.get_candidate(candidate_id)
        if not candidate:
            raise ValueError(f"Candidate {candidate_id} not found in store")

        trend_eval = self.engine.score_trend(candidate)
        skeptic_ratio = trend_eval.get("skeptic_ratio", 0.20)

        # High proof burden alert
        high_proof_burden = skeptic_ratio >= 0.50
        summary_verdict = "HIGH_PROOF_BURDEN" if high_proof_burden else "STRONG_DEMAND"

        return {
            "candidate_id": candidate_id,
            "trend_score": trend_eval["score"],
            "skeptic_ratio": skeptic_ratio,
            "high_proof_burden": high_proof_burden,
            "verdict": summary_verdict,
            "competitor_count": trend_eval.get("competitor_count", 0),
        }

    def evaluate_all(self) -> Dict[str, Any]:
        results = {}
        for c in self.store.list_candidates():
            cid = c["candidate_id"]
            results[cid] = self.evaluate_candidate(cid)
        return results
