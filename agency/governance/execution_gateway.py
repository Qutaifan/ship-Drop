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

    def execute_canary_order_batch(
        self,
        candidate_id: str,
        supplier_id: str,
        stability_score: float,
        tier: str,
        order_count: int = 3,
        estimated_spend: float = 60.0,
        consecutive_stable_days: int = 0,
    ) -> Dict[str, Any]:
        """Canary execution logic with autonomous scaling:
        - Baseline (0-7 days): 3 orders, cap $250.00
        - Scaled Tier 2 (8-21 days): 5 orders, cap $400.00
        - Scaled Tier 3 (22+ days): 10 orders, cap $600.00 ('TRUSTED_DOMESTIC')
        """
        if tier != "PREFERRED_DOMESTIC" or stability_score < 0.85:
            return {
                "success": False,
                "canary_permitted": False,
                "reason": f"Canary execution rejected: supplier tier is {tier} (requires PREFERRED_DOMESTIC) and stability is {stability_score:.2f} (requires >=0.85).",
            }

        # Determine dynamic scaling tier
        if consecutive_stable_days >= 22:
            scaling_tier = "TRUSTED_DOMESTIC_TIER_3"
            max_canary_orders = 10
            canary_spend_cap = 600.0
        elif consecutive_stable_days >= 8:
            scaling_tier = "SCALED_DOMESTIC_TIER_2"
            max_canary_orders = 5
            canary_spend_cap = 400.0
        else:
            scaling_tier = "BASELINE_CANARY_TIER_1"
            max_canary_orders = 3
            canary_spend_cap = 250.0

        if order_count > max_canary_orders or estimated_spend > canary_spend_cap:
            return {
                "success": False,
                "canary_permitted": False,
                "scaling_tier": scaling_tier,
                "reason": f"Canary limits for {scaling_tier} exceeded: requested {order_count} orders (${estimated_spend:.2f}), max allowed is {max_canary_orders} orders (${canary_spend_cap:.2f}).",
            }

        canary_id = f"canary-exec-{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d%H%M%S')}"
        self.store.log_audit("CANARY_BATCH_DISPATCHED", {
            "canary_id": canary_id,
            "candidate_id": candidate_id,
            "supplier_id": supplier_id,
            "orders": order_count,
            "spend": estimated_spend,
            "stability_score": stability_score,
            "scaling_tier": scaling_tier,
            "status": "DISPATCHED_TO_TRACKER",
        })

        return {
            "success": True,
            "canary_permitted": True,
            "canary_id": canary_id,
            "candidate_id": candidate_id,
            "supplier_id": supplier_id,
            "order_count": order_count,
            "estimated_spend": estimated_spend,
            "scaling_tier": scaling_tier,
            "max_allowed_orders": max_canary_orders,
            "active_spend_cap": canary_spend_cap,
            "status": "QUEUED_FOR_TRACKER_MONITORING",
            "message": f"Canary batch of {order_count} order(s) approved under {scaling_tier} (Spend cap: ${canary_spend_cap:.2f}).",
        }
