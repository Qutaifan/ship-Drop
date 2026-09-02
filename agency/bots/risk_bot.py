"""Risk Bot - Regulatory compliance, anti-de-minimis, customs duty, and operational risk auditor."""
from __future__ import annotations

from typing import Any, Dict, Optional

from agency.core.scoring_engine import ScoringEngine
from agency.core.store import Store


class RiskBot:
    """RiskBot audits compliance, anti-de-minimis rules, and operational hazards."""

    def __init__(self, store: Optional[Store] = None, engine: Optional[ScoringEngine] = None):
        self.store = store or Store()
        self.engine = engine or ScoringEngine()

    def audit_candidate(self, candidate_id: str) -> Dict[str, Any]:
        candidate = self.store.get_candidate(candidate_id)
        if not candidate:
            raise ValueError(f"Candidate {candidate_id} not found in store")

        risk_eval = self.engine.score_risk(candidate)

        # Update candidate unknowns if needed
        flags = risk_eval.get("risk_flags", [])
        if flags and not candidate.get("compliance_unknowns"):
            candidate["compliance_unknowns"] = flags
            self.store.save_candidate(candidate)

        return {
            "candidate_id": candidate_id,
            "risk_score": risk_eval["score"],
            "safety_score": risk_eval["safety_score"],
            "has_domestic_warehouse": risk_eval.get("has_domestic_warehouse", False),
            "risk_flags": flags,
            "is_high_risk": risk_eval["score"] >= 60.0,
        }

    def audit_all(self) -> Dict[str, Any]:
        results = {}
        for c in self.store.list_candidates():
            cid = c["candidate_id"]
            results[cid] = self.audit_candidate(cid)
        return results
