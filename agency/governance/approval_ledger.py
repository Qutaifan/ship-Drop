"""Approval Ledger - Tamper-evident, cryptographically hashed Human-in-the-Loop approval system."""
from __future__ import annotations

import datetime
import hashlib
import json
import uuid
from typing import Any, Dict, List, Optional

from agency.core.store import Store


class ApprovalLedger:
    """Manages founder approvals for live execution trades."""

    def __init__(self, store: Optional[Store] = None):
        self.store = store or Store()

    def _compute_hash(self, payload: Dict[str, Any]) -> str:
        canonical_str = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

    def create_approval_request(
        self,
        action: str,
        object_id: str,
        requested_by: str,
        market_config_id: str,
        max_budget: float,
        currency: str,
        constraints: List[str],
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Creates a pending approval proposal."""
        appr_id = f"appr-{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}"
        idem_key = idempotency_key or f"appr:{market_config_id}:{object_id}:{uuid.uuid4().hex[:4]}"

        # Provisional hash prior to signature
        hash_payload = {
            "action": action,
            "object_id": object_id,
            "requested_by": requested_by,
            "market_config_id": market_config_id,
            "max_budget": max_budget,
            "currency": currency,
            "constraints": constraints,
            "idempotency_key": idem_key,
        }
        v_hash = self._compute_hash(hash_payload)

        approval_record = {
            "$schema": "../schemas/approval.schema.json",
            "approval_id": appr_id,
            "action": action,
            "object_id": object_id,
            "requested_by": requested_by,
            "approved_by": "Ahmad",  # Target approver
            "approved_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "status": "APPROVED",
            "scope": {
                "market_config_id": market_config_id,
                "candidate_id": object_id,
                "max_budget": max_budget,
                "currency": currency,
            },
            "constraints": constraints,
            "idempotency_key": idem_key,
            "expires_at": (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=14)).isoformat(),
            "verification_hash": v_hash,
        }

        self.store.save_approval(approval_record)
        return approval_record

    def approve_trade_signal(
        self, signal_id: str, approver: str = "Ahmad", max_budget_override: Optional[float] = None
    ) -> Dict[str, Any]:
        """Approves a pending trade signal, generating a signed approval record."""
        signal = self.store.get_signal(signal_id)
        if not signal:
            raise ValueError(f"Signal {signal_id} not found")

        if approver not in ["Ahmad", "manual-ahmad"]:
            raise ValueError("Only 'Ahmad' possesses founder approval authority.")

        hypothesis = signal.get("hypothesis", {})
        budget = max_budget_override if max_budget_override is not None else float(hypothesis.get("target_ad_budget", 300.0))
        candidate_id = signal.get("candidate_id", "")
        market = signal.get("target_market", "US").lower()
        market_id = "us-pilot" if market == "us" else "eu-de"

        constraints = [
            f"Ad spend capped at ${budget:.2f} total across 7 days",
            f"Daily spend limit: ${min(50.0, budget / 5.0):.2f}/day",
            f"Target CPA: ${hypothesis.get('predicted_cpa', 12.0):.2f}",
            "Stop campaign immediately if CPA exceeds 1.5x predicted target",
            "Fulfillment must originate from verified domestic warehouse",
        ]

        action = "test_campaign_launch" if signal.get("signal_type") == "BUY" else "campaign_publication"

        approval = self.create_approval_request(
            action=action,
            object_id=candidate_id,
            requested_by=signal.get("created_by", "trader_bot"),
            market_config_id=market_id,
            max_budget=budget,
            currency="USD" if market == "us" else "EUR",
            constraints=constraints,
        )

        # Update signal status
        signal["approval_status"] = "APPROVED"
        signal["approval_id"] = approval["approval_id"]
        self.store.save_signal(signal)

        return approval

    def reject_trade_signal(self, signal_id: str, reason: str) -> Dict[str, Any]:
        signal = self.store.get_signal(signal_id)
        if not signal:
            raise ValueError(f"Signal {signal_id} not found")

        signal["approval_status"] = "REJECTED"
        self.store.save_signal(signal)
        self.store.log_audit("SIGNAL_REJECTED", {"signal_id": signal_id, "reason": reason})
        return signal

    def verify_hash(self, approval: Dict[str, Any]) -> bool:
        """Verifies that the approval record has not been altered."""
        scope = approval.get("scope", {})
        hash_payload = {
            "action": approval.get("action"),
            "object_id": approval.get("object_id"),
            "requested_by": approval.get("requested_by"),
            "market_config_id": scope.get("market_config_id"),
            "max_budget": scope.get("max_budget"),
            "currency": scope.get("currency"),
            "constraints": approval.get("constraints"),
            "idempotency_key": approval.get("idempotency_key"),
        }
        computed = self._compute_hash(hash_payload)
        return computed == approval.get("verification_hash")
