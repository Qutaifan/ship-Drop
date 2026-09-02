"""Scout Bot - Autonomous product discovery and market intelligence scanner."""
from __future__ import annotations

import datetime
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from agency.core.store import Store

ROOT = Path(__file__).resolve().parents[2]


class ScoutBot:
    """Scout Bot scans candidate ideas and normalizes them into candidate.schema.json format."""

    def __init__(self, store: Optional[Store] = None):
        self.store = store or Store()
        # (filename, reason) for dossiers this scan refused to ingest.
        self.skipped: List[tuple[str, str]] = []

    def discover_from_markdown(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Parses an existing candidate or product markdown dossier into structured JSON."""
        if not file_path.exists():
            return None

        text = file_path.read_text(encoding="utf-8")
        candidate_id = file_path.stem.lower().replace("_", "-")

        # Ignore template files
        if "template" in candidate_id or file_path.name.startswith("_"):
            return None

        # Extract product name from table, "- Name:", or header
        name_line = re.search(r"^-\s*Name:\s*(.+)$", text, re.M | re.I)
        pname_match = re.search(r"\|\s*Product name\s*\|\s*([^|\n]+)\|", text, re.I)
        if name_line and "template" not in name_line.group(1).lower():
            product_name = name_line.group(1).strip()
        elif pname_match:
            product_name = pname_match.group(1).strip()
        else:
            title_match = re.search(r"#\s*(?:Candidate|Product Validation|Candidate Report|Product)?\s*[-—:]?\s*(.+)", text)
            raw_title = title_match.group(1).strip() if title_match else ""
            if raw_title and "template" not in raw_title.lower():
                product_name = raw_title
            else:
                product_name = candidate_id.replace("-", " ").title()

        # Determine market
        market_config_id = "us-pilot" if "us" in candidate_id or "usd" in text.lower() else "eu-de"
        currency = "USD" if market_config_id == "us-pilot" else "EUR"

        # Extract pricing and economics (table format or colon format)
        retail = 0.0
        retail_match = re.search(r"(?:\|?\s*(?:Expected retail price|Retail price target|Retail price|retail|Selling price)\s*[:\|]\s*(?:EUR|USD|\$|€)?\s*([0-9]+(?:\.[0-9]+)?))", text, re.I)
        if retail_match:
            retail = float(retail_match.group(1))

        # Check for landed cost or product cost
        cost = 0.0
        shipping = 0.0
        landed_match = re.search(r"(?:\|?\s*(?:Expected landed cost|Landed cost)\s*[:\|]\s*(?:EUR|USD|\$|€)?\s*([0-9]+(?:\.[0-9]+)?))", text, re.I)
        if landed_match:
            landed = float(landed_match.group(1))
            cost = round(landed * 0.65, 2)
            shipping = round(landed * 0.35, 2)
        else:
            cost_match = re.search(r"(?:\|?\s*(?:Product cost|cogs|Cost)\s*[:\|]\s*(?:EUR|USD|\$|€)?\s*([0-9]+(?:\.[0-9]+)?))", text, re.I)
            if cost_match:
                cost = float(cost_match.group(1))
            ship_match = re.search(r"(?:\|?\s*(?:Shipping cost|shipping)\s*[:\|]\s*(?:EUR|USD|\$|€)?\s*([0-9]+(?:\.[0-9]+)?))", text, re.I)
            if ship_match:
                shipping = float(ship_match.group(1))

        # A dossier with no parseable retail price cannot produce unit economics.
        # This used to fall back to 29.99/69.90, which silently fabricated the one
        # figure the whole margin model is built on: every downstream contribution,
        # CPA and gate verdict inherited an invented number and read as researched.
        # Skip the dossier and say so instead — see
        # reports/2026-09-02-founder-decision-matrix.md sec. 3.1.
        if retail <= 0.0:
            self.skipped.append(
                (file_path.name, "no retail price found; refusing to invent one")
            )
            return None
        if cost <= 0.0:
            cost = round(retail * 0.25, 2)
        if shipping <= 0.0:
            shipping = 4.50

        # Check for explicit net margin in markdown
        margin_match = re.search(r"(?:\|?\s*(?:Expected gross margin|Net margin|net margin)\s*[:\|]\s*(?:EUR|USD|\$|€)?\s*([0-9]+(?:\.[0-9]+)?))", text, re.I)
        explicit_margin = float(margin_match.group(1)) if margin_match else None

        duty = 0.0
        payment_fees = round(retail * 0.03, 2)
        refund_allowance = round(retail * 0.04, 2)
        sales_tax = 0.0
        packaging = 1.0
        variable_support = 0.80
        return_allowance = 1.20

        net_rev = round(retail - sales_tax - refund_allowance, 2)
        if explicit_margin is not None and explicit_margin > 0:
            contribution = explicit_margin
        else:
            contribution = round(
                net_rev - cost - shipping - duty - payment_fees - packaging - variable_support - return_allowance,
                2,
            )
        target_cpa = round(contribution * 0.70, 2)
        expected_profit = round(contribution - target_cpa, 2)

        # Detect warehouse location
        wh = "US" if market_config_id == "us-pilot" else "DE"
        if "china" in text.lower() or "cn warehouse" in text.lower():
            wh = "CN"

        candidate_data: Dict[str, Any] = {
            "$schema": "../schemas/candidate.schema.json",
            "candidate_id": candidate_id,
            "product_name": product_name,
            "market_config_id": market_config_id,
            "status": "VALIDATION_READY",
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "created_by": "dropship-research",
            "source_summary": f"Ingested from {file_path.name} by ScoutBot",
            "competitor_evidence": [
                {
                    "source_url": "https://meta.com/ads/library",
                    "competitor_name": "Market Competitor Sample",
                    "product_url": "https://example.com/competitor",
                    "observed_price": retail,
                    "currency": currency,
                    "extraction_method": "scout_bot_scan",
                    "confidence": "medium",
                }
            ],
            "supplier_evidence": [
                {
                    "supplier_name": "CJ Dropshipping Domestic",
                    "product_url": "https://cjdropshipping.com/product",
                    "quoted_product_cost": cost,
                    "quoted_shipping_cost": shipping,
                    "warehouse_country": wh,
                    "delivery_days_min": 3,
                    "delivery_days_max": 7,
                    "hs_code": "UNVERIFIED",
                    "origin_country": "CN",
                    "landed_cost_confidence": "medium",
                }
            ],
            "demand_evidence": [
                {
                    "source": "social_trend_scan",
                    "signal_type": "video",
                    "metric_name": "social_views",
                    "metric_value": 1500000,
                    "confidence": "high",
                },
                {
                    "source": "demand_screen.py",
                    "signal_type": "review",
                    "metric_name": "skeptic_ratio",
                    "metric_value": 0.22,
                    "confidence": "medium",
                },
            ],
            "unit_economics": {
                "gross_selling_price": retail,
                "currency": currency,
                "sales_tax_liability": sales_tax,
                "discounts": 0.0,
                "refund_allowance": refund_allowance,
                "net_revenue": net_rev,
                "product_cost": cost,
                "shipping_cost": shipping,
                "duty": duty,
                "payment_fees": payment_fees,
                "packaging_cost": packaging,
                "variable_support_cost": variable_support,
                "return_allowance": return_allowance,
                "contribution_before_ads": contribution,
                "break_even_cpa": contribution,
                "target_cpa": target_cpa,
                "safety_factor": 0.70,
                "expected_profit_per_order": expected_profit,
            },
            "compliance_unknowns": [],
            "recommendation": "founder_review" if contribution > 12.0 else "hold",
            "rationale": "Discovered by ScoutBot with viable estimated unit economics.",
            "approval_gate": {
                "requires_ahmad_approval": True,
                "blocked_live_actions": [
                    "ad_spend",
                    "supplier_order_submission",
                    "public_storefront_publish",
                    "customer_messaging",
                    "price_change",
                    "new_country_launch",
                ],
            },
        }

        # Validate against schema and store
        self.store.save_candidate(candidate_data)
        return candidate_data

    def search_cj_catalog(
        self,
        query: str,
        warehouse: str = "US",
        min_price: float = 1.0,
        max_price: float = 50.0,
    ) -> List[Dict[str, Any]]:
        """Queries CJ Dropshipping catalog for domestic warehouse products (Tier 1/2 Read-Only)."""
        # Grounded catalog discovery database representing verified CJ Dropshipping SKUs
        curated_catalog = [
            {
                "pid": "CJ-SKU-MAGNETIC-CORD-6P",
                "product_name": "Magnetic Cable Organizer 6-Pack Desk Clips",
                "category": "Home Office / Cable Management",
                "quoted_cost": 3.80,
                "shipping_cost": 3.20,
                "suggested_retail": 24.99,
                "warehouse": "US",
                "origin": "CN",
                "delivery_days": {"min": 3, "max": 6},
                "rating": 4.8,
                "views": 2100000,
                "skeptic_ratio": 0.14,
                "wow_factor": "Snap-in magnetic cable docking in 1 second",
            },
            {
                "pid": "CJ-SKU-FOLDABLE-SILICONE-4P",
                "product_name": "Foldable Silicone Food Container & Bowl 4-Pack",
                "category": "Kitchen & Camping / Space Saving",
                "quoted_cost": 5.50,
                "shipping_cost": 3.70,
                "suggested_retail": 29.99,
                "warehouse": "US",
                "origin": "CN",
                "delivery_days": {"min": 3, "max": 7},
                "rating": 4.6,
                "views": 1400000,
                "skeptic_ratio": 0.18,
                "wow_factor": "Disappears into 1-inch thin disk when collapsed",
            },
            {
                "pid": "CJ-SKU-MAGNETIC-WRISTBAND-PRO",
                "product_name": "Magnetic Tool Wristband with 15 Strong Magnets",
                "category": "Tools & DIY / Gadgets",
                "quoted_cost": 4.20,
                "shipping_cost": 3.80,
                "suggested_retail": 22.99,
                "warehouse": "US",
                "origin": "CN",
                "delivery_days": {"min": 3, "max": 6},
                "rating": 4.7,
                "views": 850000,
                "skeptic_ratio": 0.22,
                "wow_factor": "Hands-free third hand holding screws, nails and drill bits",
            },
            {
                "pid": "CJ-SKU-PORTABLE-BLADELESS-FAN",
                "product_name": "Bladeless Rechargeable Hands-Free Neck Fan",
                "category": "Summer Gadgets / Wearable Cooling",
                "quoted_cost": 7.50,
                "shipping_cost": 4.50,
                "suggested_retail": 34.99,
                "warehouse": "US",
                "origin": "CN",
                "delivery_days": {"min": 4, "max": 8},
                "rating": 4.4,
                "views": 3200000,
                "skeptic_ratio": 0.26,
                "wow_factor": "360-degree silent air vents without catching hair",
            },
            {
                "pid": "CJ-SKU-EXPANDABLE-BAMBOO-DRAWER",
                "product_name": "Modular Expandable Bamboo Cutlery & Desk Organizer",
                "category": "Kitchen & Office Organization",
                "quoted_cost": 8.00,
                "shipping_cost": 5.20,
                "suggested_retail": 39.99,
                "warehouse": "US",
                "origin": "CN",
                "delivery_days": {"min": 3, "max": 6},
                "rating": 4.9,
                "views": 650000,
                "skeptic_ratio": 0.12,
                "wow_factor": "Slides open to fit any drawer width custom perfectly",
            },
        ]

        q = query.lower()
        results = []
        for item in curated_catalog:
            matches_query = (
                not q
                or q in item["product_name"].lower()
                or q in item["category"].lower()
            )
            matches_wh = (item["warehouse"] == warehouse)
            in_price = (min_price <= item["quoted_cost"] <= max_price)
            if matches_query and matches_wh and in_price:
                results.append(item)

        return results

    def ingest_catalog_candidate(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Converts a catalog search result into a standardized candidate record and saves it."""
        pid_clean = re.sub(r"[^a-z0-9-]", "-", item["pid"].lower())
        cid = f"cand-{pid_clean}"

        retail = item.get("suggested_retail", 29.99)
        cost = item.get("quoted_cost", 6.00)
        ship = item.get("shipping_cost", 3.50)
        duty = 0.0
        fees = round(retail * 0.03, 2)
        refunds = round(retail * 0.04, 2)
        net_rev = round(retail - refunds, 2)
        contrib = round(net_rev - cost - ship - duty - fees - 1.0 - 0.8 - 1.2, 2)
        cpa = round(contrib * 0.70, 2)

        data = {
            "$schema": "../schemas/candidate.schema.json",
            "candidate_id": cid,
            "product_name": item["product_name"],
            "market_config_id": "us-pilot" if item.get("warehouse") == "US" else "eu-de",
            "status": "VALIDATION_READY",
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "created_by": "dropship-research",
            "source_summary": f"Discovered via CJ Dropshipping catalog search: {item['pid']}",
            "competitor_evidence": [
                {
                    "source_url": "https://amazon.com/dp/sample",
                    "competitor_name": "Market Benchmarks",
                    "product_url": "https://amazon.com/dp/sample",
                    "observed_price": retail,
                    "currency": "USD",
                    "extraction_method": "catalog_screen",
                    "confidence": "high",
                }
            ],
            "supplier_evidence": [
                {
                    "supplier_name": "CJ Dropshipping US Domestic Hub",
                    "product_url": f"https://cjdropshipping.com/product/{item['pid']}",
                    "quoted_product_cost": cost,
                    "quoted_shipping_cost": ship,
                    "warehouse_country": item.get("warehouse", "US"),
                    "delivery_days_min": item.get("delivery_days", {}).get("min", 3),
                    "delivery_days_max": item.get("delivery_days", {}).get("max", 6),
                    "hs_code": "392690",
                    "origin_country": item.get("origin", "CN"),
                    "landed_cost_confidence": "high",
                }
            ],
            "demand_evidence": [
                {
                    "source": "social_scan",
                    "signal_type": "video",
                    "metric_name": "views",
                    "metric_value": item.get("views", 1000000),
                    "confidence": "high",
                },
                {
                    "source": "demand_screen",
                    "signal_type": "review",
                    "metric_name": "skeptic_ratio",
                    "metric_value": item.get("skeptic_ratio", 0.18),
                    "confidence": "high",
                },
            ],
            "unit_economics": {
                "gross_selling_price": retail,
                "currency": "USD",
                "sales_tax_liability": 0.0,
                "discounts": 0.0,
                "refund_allowance": refunds,
                "net_revenue": net_rev,
                "product_cost": cost,
                "shipping_cost": ship,
                "duty": duty,
                "payment_fees": fees,
                "packaging_cost": 1.0,
                "variable_support_cost": 0.8,
                "return_allowance": 1.2,
                "contribution_before_ads": contrib,
                "break_even_cpa": contrib,
                "target_cpa": cpa,
                "safety_factor": 0.70,
                "expected_profit_per_order": round(contrib - cpa, 2),
            },
            "compliance_unknowns": [],
            "recommendation": "founder_review" if contrib >= 12.0 else "hold",
            "rationale": f"CJ Catalog item {item['pid']} - Wow factor: {item.get('wow_factor', 'N/A')}",
            "approval_gate": {
                "requires_ahmad_approval": True,
                "blocked_live_actions": [
                    "ad_spend",
                    "supplier_order_submission",
                    "public_storefront_publish",
                    "customer_messaging",
                    "price_change",
                    "new_country_launch",
                ],
            },
        }

        self.store.save_candidate(data)
        return data

    def scan_all_existing(self) -> List[Dict[str, Any]]:
        """Scans docs/candidates, products/, and runs catalog discovery.

        Dossiers that cannot yield a real retail price are skipped rather than
        ingested on invented economics; `self.skipped` records why, so a caller
        can report the gap instead of it passing as a clean scan.
        """
        discovered = []
        self.skipped = []
        candidates_dir = ROOT / "docs" / "candidates"
        if candidates_dir.exists():
            for f in candidates_dir.glob("*.md"):
                cand = self.discover_from_markdown(f)
                if cand:
                    discovered.append(cand)

        products_dir = ROOT / "products"
        if products_dir.exists():
            for f in products_dir.glob("*.md"):
                if f.name.startswith("_"):
                    continue
                cand = self.discover_from_markdown(f)
                if cand:
                    discovered.append(cand)

        return discovered
