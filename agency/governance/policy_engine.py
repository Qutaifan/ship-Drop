"""Policy Engine - Enforces MCP access tiers and Human-in-the-Loop constraints."""
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from agency.core.store import Store

TIER_MAP = {
    # Tier 0 - Local file generation, schema validation, testing
    "write_candidate_doc": 0,
    "run_unit_test": 0,
    "run_schema_validator": 0,
    "calculate_margin": 0,
    "read_heuristics": 0,

    # Tier 1 - Public web read, market intelligence, demand screening
    "web_search": 1,
    "demand_screen": 1,
    "ad_library_public_query": 1,
    "agent_reach_youtube": 1,
    "crawlee_public_scrape": 1,

    # Tier 2 - Account read-only (supplier catalog & inventory reads)
    "cj_catalog_search": 2,
    "cj_inventory_read": 2,
    "cj_freight_calculate": 2,
    "ebay_price_read": 2,

    # Tier 3 - Account mutation (modifies store or supplier state)
    "cj_save_to_shop": 3,
    "medusa_sync_product": 3,
    "update_candidate_status": 3,

    # Tier 4 - Financial & Customer Impact (Live spend, orders, deployments, messaging)
    "ad_spend": 4,
    "campaign_publication": 4,
    "test_campaign_launch": 4,
    "supplier_order_submission": 4,
    "public_storefront_publish": 4,
    "customer_messaging": 4,
    "price_change": 4,
    "new_country_launch": 4,
}


class PolicyEngine:
    """Enforces Tool Access Policy and Approval Policy."""

    def __init__(self, store: Optional[Store] = None):
        self.store = store or Store()

    def get_action_tier(self, action: str) -> int:
        return TIER_MAP.get(action, 4)  # default to Tier 4 (deny by default)

    def is_action_permitted(
        self, action: str, requested_by: str, approval_id: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Evaluates whether an action is permitted under the MCP governance model."""
        tier = self.get_action_tier(action)

        # Tier 0 and Tier 1: Autonomous research tools are always permitted
        if tier <= 1:
            return True, f"Tier {tier} read/research action permitted autonomously."

        # Tier 2: Account read permitted for research profiles
        if tier == 2:
            return True, f"Tier 2 account read permitted for {requested_by}."

        # Tier 3 & Tier 4: STRICT HUMAN APPROVAL REQUIRED
        if not approval_id:
            self.store.log_audit("BLOCKED_UNAPPROVED_ACTION", {
                "action": action,
                "tier": tier,
                "requested_by": requested_by,
                "reason": "Missing founder approval token",
            })
            return False, f"BLOCKED: Action '{action}' (Tier {tier}) requires explicit approval from Ahmad before execution."

        # Verify the approval record in the ledger
        approval = self.store.get_approval(approval_id)
        if not approval:
            self.store.log_audit("BLOCKED_INVALID_APPROVAL", {
                "action": action,
                "approval_id": approval_id,
                "reason": "Approval record not found",
            })
            return False, f"BLOCKED: Approval record '{approval_id}' not found."

        if approval.get("status") != "APPROVED":
            return False, f"BLOCKED: Approval '{approval_id}' has status '{approval.get('status')}'; must be 'APPROVED'."

        if approval.get("approved_by") not in ["Ahmad", "manual-ahmad"]:
            return False, f"BLOCKED: Approval must be signed by 'Ahmad', got '{approval.get('approved_by')}'."

        if approval.get("action") != action:
            return False, f"BLOCKED: Approval is for action '{approval.get('action')}', not requested '{action}'."

        self.store.log_audit("PERMITTED_APPROVED_ACTION", {
            "action": action,
            "tier": tier,
            "approval_id": approval_id,
            "approved_by": approval.get("approved_by"),
        })
        return True, f"PERMITTED: Action '{action}' authorized under approval '{approval_id}' by {approval.get('approved_by')}."
