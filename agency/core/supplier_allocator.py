"""Hermes Multi-Supplier Allocation Engine: Computes resilient order routing distributions."""
from __future__ import annotations

from typing import Any, Dict, List


class SupplierAllocator:
    """Calculates order allocation percentages across ranked suppliers to ensure supply redundancy."""

    @staticmethod
    def compute_allocation(ranked_suppliers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Distributes 100% order volume across qualified suppliers.
        
        Strategy:
        - PREFERRED_DOMESTIC (primary): Receives 70-85% volume (default 80%).
        - QUALIFIED_BACKUP (secondary): Receives 15-30% volume (default 20%) to keep supplier account active.
        - HIGH_RISK_MONITOR / REJECTED_UNVIABLE: 0% allocation.
        - If only 1 qualified supplier exists: 100% to that supplier.
        - If no preferred domestic exists, but backup exists: 100% to backup (with cautionary flag).
        - If all suppliers unviable: 0% allocation, flags ALLOCATION_BLOCKED.
        """
        if not ranked_suppliers:
            return {
                "allocations": {},
                "primary_supplier_id": None,
                "strategy": "EMPTY_SUPPLIERS",
                "redundancy_active": False,
                "status": "ALLOCATION_BLOCKED",
            }

        preferred = [s for s in ranked_suppliers if s.get("tier") == "PREFERRED_DOMESTIC"]
        backup = [s for s in ranked_suppliers if s.get("tier") == "QUALIFIED_BACKUP"]

        allocations: Dict[str, float] = {}

        if preferred and backup:
            # Multi-supplier resilience: 80% primary, 20% backup
            primary_id = preferred[0]["supplier_id"]
            backup_id = backup[0]["supplier_id"]
            allocations[primary_id] = 80.0
            allocations[backup_id] = 20.0
            for s in ranked_suppliers:
                if s["supplier_id"] not in allocations:
                    allocations[s["supplier_id"]] = 0.0

            return {
                "allocations": allocations,
                "primary_supplier_id": primary_id,
                "backup_supplier_id": backup_id,
                "strategy": "DUAL_SOURCE_RESILIENT_80_20",
                "redundancy_active": True,
                "status": "ALLOCATION_HEALTHY",
            }

        elif preferred:
            # Single primary available
            primary_id = preferred[0]["supplier_id"]
            allocations[primary_id] = 100.0
            for s in ranked_suppliers:
                if s["supplier_id"] != primary_id:
                    allocations[s["supplier_id"]] = 0.0

            return {
                "allocations": allocations,
                "primary_supplier_id": primary_id,
                "backup_supplier_id": None,
                "strategy": "SINGLE_PREFERRED_DOMESTIC_100",
                "redundancy_active": False,
                "status": "ALLOCATION_HEALTHY",
            }

        elif backup:
            # Backup only available
            primary_id = backup[0]["supplier_id"]
            allocations[primary_id] = 100.0
            for s in ranked_suppliers:
                if s["supplier_id"] != primary_id:
                    allocations[s["supplier_id"]] = 0.0

            return {
                "allocations": allocations,
                "primary_supplier_id": primary_id,
                "backup_supplier_id": None,
                "strategy": "BACKUP_ONLY_CONTINGENCY_100",
                "redundancy_active": False,
                "status": "ALLOCATION_WARNING_NO_PRIMARY",
            }

        else:
            # All suppliers are HIGH_RISK or REJECTED
            for s in ranked_suppliers:
                allocations[s["supplier_id"]] = 0.0

            return {
                "allocations": allocations,
                "primary_supplier_id": None,
                "backup_supplier_id": None,
                "strategy": "ZERO_ALLOCATION_ALL_UNVIABLE",
                "redundancy_active": False,
                "status": "ALLOCATION_BLOCKED",
            }
