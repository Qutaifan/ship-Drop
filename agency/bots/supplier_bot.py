"""Supplier Bot - Evaluates fulfillment partners, domestic stock, lead times, and shipping reliability."""
from __future__ import annotations

import datetime
from typing import Any, Dict, List, Optional

from agency.core.scoring_engine import ScoringEngine
from agency.core.store import Store


class SupplierBot:
    """SupplierBot monitors and scores dropship suppliers."""

    def __init__(self, store: Optional[Store] = None, engine: Optional[ScoringEngine] = None):
        self.store = store or Store()
        self.engine = engine or ScoringEngine()

    def register_supplier(
        self,
        supplier_id: str,
        supplier_name: str,
        platform: str,
        warehouse_country: str,
        origin_country: str,
        reliability_rating: float,
        dispute_rate_percent: float,
        processing_days: int,
        shipping_min_days: int,
        shipping_max_days: int,
        shipping_tiers: List[Dict[str, Any]],
        notes: str = "",
    ) -> Dict[str, Any]:
        """Registers and scores a supplier."""
        eu_ready = warehouse_country in ["DE", "PL", "FR", "NL", "ES", "IT"]
        us_stock = warehouse_country == "US"

        raw_data = {
            "supplier_id": supplier_id,
            "supplier_name": supplier_name,
            "platform": platform,
            "warehouse_country": warehouse_country,
            "origin_country": origin_country,
            "reliability_rating": reliability_rating,
            "dispute_rate_percent": dispute_rate_percent,
            "typical_lead_days": {
                "processing_days": processing_days,
                "shipping_min_days": shipping_min_days,
                "shipping_max_days": shipping_max_days,
            },
            "shipping_tiers": shipping_tiers,
            "eu_anti_deminimis_ready": eu_ready,
            "us_domestic_stock": us_stock,
            "score": {
                "total": 0.0,
                "fulfillment_speed": 0.0,
                "cost_competitiveness": 0.0,
                "reliability": 0.0,
                "compliance": 0.0,
            },
            "notes": notes,
            "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }

        # Calculate score using ScoringEngine
        score_res = self.engine.score_supplier(raw_data)
        raw_data["score"] = {
            "total": score_res.total,
            "fulfillment_speed": score_res.fulfillment_speed,
            "cost_competitiveness": score_res.cost_competitiveness,
            "reliability": score_res.reliability,
            "compliance": score_res.compliance,
        }

        self.store.save_supplier(raw_data)
        return raw_data

    def evaluate_all(self) -> Dict[str, Any]:
        results = {}
        for s in self.store.list_suppliers():
            sid = s["supplier_id"]
            score_res = self.engine.score_supplier(s)
            s["score"] = {
                "total": score_res.total,
                "fulfillment_speed": score_res.fulfillment_speed,
                "cost_competitiveness": score_res.cost_competitiveness,
                "reliability": score_res.reliability,
                "compliance": score_res.compliance,
            }
            s["updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
            self.store.save_supplier(s)
            results[sid] = score_res.to_dict()
        return results
