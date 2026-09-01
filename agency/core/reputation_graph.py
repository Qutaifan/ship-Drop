"""Hermes Supplier Reputation & Network Graph: Maps shared warehouses, logistics nodes, and systemic risk."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Set

from agency.core.store import Store


class SupplierReputationGraph:
    """Builds and analyzes a network graph of suppliers, warehouses, logistics carriers, and SKUs."""

    def __init__(self, store: Optional[Store] = None):
        self.store = store or Store()

    def build_network_graph(self) -> Dict[str, Any]:
        """Constructs adjacency nodes and edges across suppliers, warehouses, carriers, and candidates."""
        candidates = self.store.list_candidates()
        verifications = self.store.list_supplier_verifications(limit=200)

        nodes: Dict[str, Dict[str, Any]] = {}
        edges: List[Dict[str, Any]] = []

        # Maps for quick aggregation
        supplier_skus: Dict[str, Set[str]] = {}
        warehouse_suppliers: Dict[str, Set[str]] = {}
        carrier_suppliers: Dict[str, Set[str]] = {}

        # 1. Process candidate SKU associations
        for c in candidates:
            cid = c.get("candidate_id", "cand-unknown")
            nodes[f"sku:{cid}"] = {
                "id": cid,
                "type": "SKU",
                "label": c.get("product_name", cid),
                "market": "US" if "us" in c.get("market_config_id", "") else "EU",
            }

            for sup in c.get("supplier_evidence", []):
                sname = sup.get("supplier_name", "unknown")
                sid = sname.lower().replace(" ", "-")
                supplier_skus.setdefault(sid, set()).add(cid)

                wh_code = f"WH-{sup.get('warehouse_country', 'US')}-{sid[:10]}"
                carrier = sup.get("shipping_method", "USPS")

                warehouse_suppliers.setdefault(wh_code, set()).add(sid)
                carrier_suppliers.setdefault(carrier, set()).add(sid)

                # Add edges
                edges.append({"source": f"sku:{cid}", "target": f"supplier:{sid}", "relation": "SOURCED_FROM"})
                edges.append({"source": f"supplier:{sid}", "target": f"warehouse:{wh_code}", "relation": "FULFILLED_AT"})
                edges.append({"source": f"supplier:{sid}", "target": f"carrier:{carrier}", "relation": "SHIPPED_VIA"})

        # 2. Add Supplier nodes with recent telemetry
        for sid, skus in supplier_skus.items():
            recent_v = [v for v in verifications if v.get("supplier_id") == sid]
            stab = recent_v[0].get("stability_score", 0.90) if recent_v else 0.90
            status = recent_v[0].get("status", "VERIFIED_PASS") if recent_v else "VERIFIED_PASS"

            nodes[f"supplier:{sid}"] = {
                "id": sid,
                "type": "SUPPLIER",
                "label": sid.replace("-", " ").title(),
                "sku_count": len(skus),
                "stability_score": stab,
                "status": status,
                "systemic_exposure_percent": round((len(skus) / max(1, len(candidates))) * 100.0, 1),
            }

        # 3. Add Warehouse nodes
        for wh, sups in warehouse_suppliers.items():
            nodes[f"warehouse:{wh}"] = {
                "id": wh,
                "type": "WAREHOUSE",
                "label": wh,
                "supplier_count": len(sups),
                "impact_radius_suppliers": list(sups),
            }

        # 4. Add Carrier nodes
        for car, sups in carrier_suppliers.items():
            nodes[f"carrier:{car}"] = {
                "id": car,
                "type": "CARRIER",
                "label": car,
                "supplier_count": len(sups),
            }

        return {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "nodes": nodes,
            "edges": edges,
            "systemic_summary": {
                "total_skus": len(candidates),
                "total_suppliers": len(supplier_skus),
                "total_warehouses": len(warehouse_suppliers),
                "total_carriers": len(carrier_suppliers),
            },
        }

    def assess_systemic_risk(self, degraded_supplier_id: str) -> Dict[str, Any]:
        """Calculates systemic risk blast radius if a specific supplier fails."""
        graph = self.build_network_graph()
        nodes = graph["nodes"]
        sup_key = f"supplier:{degraded_supplier_id}"
        sup_node = nodes.get(sup_key)

        if not sup_node:
            return {
                "supplier_id": degraded_supplier_id,
                "found_in_graph": False,
                "affected_skus": [],
                "affected_sku_count": 0,
                "systemic_risk_level": "NEGLIGIBLE",
            }

        # Find directly connected SKUs
        affected_skus = []
        for edge in graph["edges"]:
            if edge["target"] == sup_key and edge["relation"] == "SOURCED_FROM":
                sku_id = edge["source"].replace("sku:", "")
                affected_skus.append(sku_id)

        sku_exposure = sup_node.get("systemic_exposure_percent", 0.0)
        risk_level = "CRITICAL_PORTFOLIO" if sku_exposure >= 40.0 else "ELEVATED" if sku_exposure >= 20.0 else "ISOLATED"

        return {
            "supplier_id": degraded_supplier_id,
            "found_in_graph": True,
            "stability_score": sup_node.get("stability_score", 0.0),
            "affected_skus": affected_skus,
            "affected_sku_count": len(affected_skus),
            "portfolio_exposure_percent": sku_exposure,
            "systemic_risk_level": risk_level,
            "recommended_action": "MULTI_SKU_REBALANCE" if len(affected_skus) > 1 else "SINGLE_SKU_SWITCH",
        }
