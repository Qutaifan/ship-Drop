"""Tracker Bot - Continuous monitoring of competitor longevity, market saturation, and performance drift."""
from __future__ import annotations

import datetime
from typing import Any, Dict, List, Optional

from agency.core.store import Store


class TrackerBot:
    """TrackerBot continuously tracks market conditions and performance metrics."""

    def __init__(self, store: Optional[Store] = None):
        self.store = store or Store()

    def check_candidate_health(self, candidate_id: str) -> Dict[str, Any]:
        """Audits candidate health and identifies trend shifts or saturation risks."""
        candidate = self.store.get_candidate(candidate_id)
        if not candidate:
            raise ValueError(f"Candidate {candidate_id} not found")

        comp_ev = candidate.get("competitor_evidence", [])
        num_comp = len(comp_ev)

        econ = candidate.get("unit_economics", {})
        net_margin = econ.get("contribution_before_ads", econ.get("expected_profit_per_order", 0.0))

        triggers = []
        if num_comp > 15:
            triggers.append({"type": "SATURATION_ALERT", "severity": "HIGH", "message": f"Competitor count ({num_comp}) exceeds saturation limit (15)"})
        elif num_comp < 3:
            triggers.append({"type": "DEMAND_WARNING", "severity": "MEDIUM", "message": f"Few competitors ({num_comp}); unverified commercial interest"})

        if net_margin < 12.0:
            triggers.append({"type": "MARGIN_COMPRESSION", "severity": "CRITICAL", "message": f"Net margin (${net_margin:.2f}) too thin for paid acquisition"})

        return {
            "candidate_id": candidate_id,
            "product_name": candidate.get("product_name"),
            "status": candidate.get("status"),
            "active_triggers": triggers,
            "checked_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }

    def monitor_all(self) -> List[Dict[str, Any]]:
        results = []
        for c in self.store.list_candidates():
            res = self.check_candidate_health(c["candidate_id"])
            if res["active_triggers"]:
                results.append(res)
        return results
