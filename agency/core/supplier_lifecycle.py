"""Hermes Supplier Lifecycle State Machine: Governs operational states and transitions."""
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional


class SupplierState(str, Enum):
    ACTIVE = "ACTIVE"
    WATCHLIST = "WATCHLIST"
    DEGRADED = "DEGRADED"
    CRITICAL = "CRITICAL"
    SUSPENDED = "SUSPENDED"
    RETIRED = "RETIRED"


class SupplierLifecycleManager:
    """Manages state transitions and governance rules for suppliers based on live telemetry."""

    VALID_TRANSITIONS = {
        SupplierState.ACTIVE: [SupplierState.WATCHLIST, SupplierState.DEGRADED, SupplierState.CRITICAL, SupplierState.SUSPENDED, SupplierState.RETIRED],
        SupplierState.WATCHLIST: [SupplierState.ACTIVE, SupplierState.DEGRADED, SupplierState.CRITICAL, SupplierState.SUSPENDED, SupplierState.RETIRED],
        SupplierState.DEGRADED: [SupplierState.WATCHLIST, SupplierState.ACTIVE, SupplierState.CRITICAL, SupplierState.SUSPENDED, SupplierState.RETIRED],
        SupplierState.CRITICAL: [SupplierState.DEGRADED, SupplierState.SUSPENDED, SupplierState.RETIRED],
        SupplierState.SUSPENDED: [SupplierState.DEGRADED, SupplierState.WATCHLIST, SupplierState.ACTIVE, SupplierState.RETIRED],
        SupplierState.RETIRED: [],  # Terminal state without explicit manual intervention
    }

    @staticmethod
    def evaluate_state(
        stability_score: float,
        volatility_index: float = 0.0,
        current_state: SupplierState = SupplierState.ACTIVE,
        manual_override: Optional[SupplierState] = None,
    ) -> Dict[str, Any]:
        """Determines the target lifecycle state from stability and volatility telemetry."""
        if manual_override:
            return {
                "state": manual_override.value,
                "previous_state": current_state.value,
                "transitioned": manual_override != current_state,
                "reason": "Manual operator override",
                "canary_permitted": manual_override in [SupplierState.ACTIVE, SupplierState.WATCHLIST],
                "replacement_required": manual_override in [SupplierState.CRITICAL, SupplierState.SUSPENDED, SupplierState.RETIRED],
            }

        if current_state == SupplierState.RETIRED:
            return {
                "state": SupplierState.RETIRED.value,
                "previous_state": SupplierState.RETIRED.value,
                "transitioned": False,
                "reason": "Supplier is permanently retired",
                "canary_permitted": False,
                "replacement_required": True,
            }

        # Deterministic state evaluation rules:
        target: SupplierState
        reason: str

        if stability_score < 0.70 or volatility_index >= 0.20:
            target = SupplierState.CRITICAL
            reason = f"Critical instability: stability {stability_score:.2f} (<0.70) or volatility index {volatility_index:.3f} (>=0.20)"
        elif stability_score < 0.80:
            target = SupplierState.DEGRADED
            reason = f"Degraded reliability: stability {stability_score:.2f} (between 0.70 and 0.79)"
        elif stability_score < 0.85 or volatility_index >= 0.10:
            target = SupplierState.WATCHLIST
            reason = f"Early drift warning: stability {stability_score:.2f} or volatility index {volatility_index:.3f} (>=0.10)"
        else:
            target = SupplierState.ACTIVE
            reason = f"Healthy domestic supplier: stability {stability_score:.2f} (>=0.85), volatility {volatility_index:.3f}"

        # Transition validation
        allowed_next = SupplierLifecycleManager.VALID_TRANSITIONS.get(current_state, [])
        transitioned = (target != current_state) and (target in allowed_next)
        final_state = target if (transitioned or target == current_state) else current_state

        return {
            "state": final_state.value,
            "previous_state": current_state.value,
            "transitioned": transitioned,
            "reason": reason,
            "canary_permitted": final_state == SupplierState.ACTIVE or (final_state == SupplierState.WATCHLIST and stability_score >= 0.85),
            "replacement_required": final_state in [SupplierState.CRITICAL, SupplierState.SUSPENDED],
        }
