"""Execution Gateway - Guarded dispatcher for live actions requiring human approval."""
from __future__ import annotations

import datetime
from typing import Any, Dict, Optional, Tuple

from agency.core.store import Store
from agency.governance.approval_ledger import ApprovalLedger
from agency.governance.policy_engine import PolicyEngine


class ExecutionGateway:
    """Guards live execution tools and enforces Human-in-the-Loop gates."""

    def __init__(
        self,
        store: Optional[Store] = None,
        policy: Optional[PolicyEngine] = None,
        ledger: Optional[ApprovalLedger] = None,
    ):
        self.store = store or Store()
        self.policy = policy or PolicyEngine(self.store)
        self.ledger = ledger or ApprovalLedger(self.store)

    def execute_live_action(
        self,
        action: str,
        object_id: str,
        requested_by: str,
        requested_spend: float = 0.0,
        approval_id: Optional[str] = None,
        live_mode: bool = False,
    ) -> Dict[str, Any]:
        """Attempts to execute a live state-changing action.
        
        If approval is missing, invalid, or expired, execution is immediately BLOCKED.
        """
        permitted, message = self.policy.is_action_permitted(action, requested_by, approval_id)
        if not permitted:
            return {
                "success": False,
                "blocked": True,
                "action": action,
                "object_id": object_id,
                "reason": message,
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            }

        # Retrieve approval record
        approval = self.store.get_approval(approval_id)  # type: ignore[arg-type]
        if not approval:
            return {
                "success": False,
                "blocked": True,
                "action": action,
                "reason": "Approval record could not be retrieved.",
            }

        # Check cryptographic tamper verification
        if not self.ledger.verify_hash(approval):
            self.store.log_audit("TAMPER_DETECTED", {
                "approval_id": approval_id,
                "action": action,
                "reason": "Verification hash mismatch; approval data was altered.",
            })
            return {
                "success": False,
                "blocked": True,
                "action": action,
                "reason": "SECURITY ALERT: Approval verification hash mismatch. Tamper detected.",
            }

        # Check budget limits
        scope = approval.get("scope", {})
        max_budget = float(scope.get("max_budget", 0.0) or 0.0)
        if requested_spend > max_budget:
            return {
                "success": False,
                "blocked": True,
                "action": action,
                "reason": f"Requested spend (${requested_spend:.2f}) exceeds approved limit (${max_budget:.2f}).",
            }

        # Safe execution / sandbox execution dispatch
        execution_id = f"exec-{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d%H%M%S')}"
        mode = "LIVE" if live_mode else "SANDBOX_SIMULATED"

        # Update approval status to CONSUMED
        approval["status"] = "CONSUMED"
        self.store.save_approval(approval)

        self.store.log_audit("ACTION_EXECUTED", {
            "execution_id": execution_id,
            "action": action,
            "object_id": object_id,
            "approval_id": approval_id,
            "mode": mode,
            "spend": requested_spend,
        })

        return {
            "success": True,
            "blocked": False,
            "execution_id": execution_id,
            "action": action,
            "object_id": object_id,
            "mode": mode,
            "authorized_by": approval.get("approved_by"),
            "approved_at": approval.get("approved_at"),
            "constraints": approval.get("constraints"),
            "message": f"Successfully executed action '{action}' under founder authorization {approval_id} ({mode}).",
        }
