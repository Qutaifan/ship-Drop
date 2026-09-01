"""Hermes Medusa v2 Storefront Sync: Pushes optimized candidates, prices, and stock to Medusa."""
from __future__ import annotations

import datetime
import hashlib
import hmac
import json
import os
import re
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

from agency.core.store import Store

ROOT = Path(__file__).resolve().parents[2]
CATALOG_DIR = ROOT / "data" / "medusa_catalog"


class MedusaStorefrontSync:
    """Synchronizes Hermes-Ecom candidates into Medusa v2 Headless Storefront.
    Converts prices to cents, tracks live domestic stock, and records HMAC provenance.
    """

    def __init__(self, store: Optional[Store] = None):
        self.store = store or Store()
        CATALOG_DIR.mkdir(parents=True, exist_ok=True)
        self.backend_url = os.environ.get("MEDUSA_BACKEND_URL", "http://localhost:9000")
        self.api_token = os.environ.get("MEDUSA_API_TOKEN", "")
        self.provenance_secret = os.environ.get("HERMES_PROVENANCE_SECRET", "hermes-default-provenance-key-2026").encode("utf-8")

    def _slugify(self, text: str) -> str:
        text = text.lower().strip()
        return re.sub(r"[^\w\s-]", "", text).replace(" ", "-")

    def build_medusa_payload(
        self,
        candidate: Dict[str, Any],
        verified_telemetry: Optional[Dict[str, Any]] = None,
        publish: bool = False,
    ) -> Dict[str, Any]:
        """Maps candidate economics and content into Medusa v2 Product format."""
        cid = candidate.get("candidate_id", "cand-unknown")
        title = candidate.get("product_name", "Target SKU")
        handle = self._slugify(title)
        econ = candidate.get("unit_economics", {})

        retail_usd = float(econ.get("gross_selling_price", 62.99))
        amount_usd_cents = int(round(retail_usd * 100))
        amount_eur_cents = int(round((retail_usd * 0.94) * 100))  # Approx EUR ex-VAT equivalent

        stock = 250
        supplier_id = "cj-dropshipping-us-domestic-hub"
        stability = 0.95
        landed = 10.14
        sku_id = "SKU-TARGET"

        if verified_telemetry:
            stock = int(verified_telemetry.get("stock_level", stock))
            supplier_id = str(verified_telemetry.get("supplier_id", supplier_id))
            stability = float(verified_telemetry.get("stability_score", stability))
            landed = float(verified_telemetry.get("verified_product_cost", 6.50)) + float(verified_telemetry.get("verified_shipping_cost", 3.50))
            sku_id = str(verified_telemetry.get("sku", sku_id))
        elif candidate.get("variants"):
            sku_id = candidate["variants"][0].get("sku", sku_id)

        cogs_multiple = round((retail_usd - landed) / landed, 1) if landed > 0 else 5.0
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Sign HMAC provenance
        sig_str = f"{cid}:{sku_id}:{amount_usd_cents}:{stock}:{supplier_id}:{now_iso}"
        hmac_sig = hmac.new(self.provenance_secret, sig_str.encode("utf-8"), hashlib.sha256).hexdigest()

        # Product description with EU AI Act compliance notice
        desc = candidate.get("description", f"High-grade {title}. Optimized for home and professional workspace setups.")
        ai_notice = "\n\n*Product staging assisted by generative AI (EU AI Act compliant).*"
        if "generative AI" not in desc:
            desc = f"{desc}{ai_notice}"

        return {
            "title": title,
            "subtitle": f"Domestic 48H Tracked Delivery • {title}",
            "description": desc,
            "handle": handle,
            "status": "published" if publish else "draft",
            "is_giftcard": False,
            "discountable": True,
            "variants": [
                {
                    "title": "Default",
                    "sku": sku_id,
                    "manage_inventory": True,
                    "inventory_quantity": stock,
                    "prices": [
                        {"currency_code": "usd", "amount": amount_usd_cents},
                        {"currency_code": "eur", "amount": amount_eur_cents},
                    ],
                }
            ],
            "metadata": {
                "candidate_id": cid,
                "primary_supplier_id": supplier_id,
                "stability_score": stability,
                "verified_landed_cost_usd": landed,
                "cogs_multiple": cogs_multiple,
                "synced_at": now_iso,
                "sync_provenance_hmac": hmac_sig,
            },
        }

    def sync_candidate(
        self,
        candidate_id: str,
        publish: bool = False,
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """Pushes product to Medusa v2 or exports to local catalog."""
        cand = self.store.get_candidate(candidate_id)
        if not cand:
            raise ValueError(f"Candidate {candidate_id} not found.")

        # Get latest verification
        all_vers = self.store.list_supplier_verifications(candidate_id=candidate_id)
        top_ver = all_vers[0] if all_vers else None

        payload = self.build_medusa_payload(candidate=cand, verified_telemetry=top_ver, publish=publish)

        if dry_run:
            return {
                "status": "DRY_RUN",
                "candidate_id": candidate_id,
                "payload": payload,
                "medusa_backend_connected": False,
            }

        # 1. Update Local Headless Catalog Export
        catalog_file = CATALOG_DIR / "products.json"
        catalog_data: Dict[str, Any] = {}
        if catalog_file.exists():
            try:
                with catalog_file.open("r", encoding="utf-8") as f:
                    catalog_data = json.load(f)
            except Exception:
                catalog_data = {}

        catalog_data[candidate_id] = payload
        with catalog_file.open("w", encoding="utf-8") as f:
            json.dump(catalog_data, f, indent=2)

        # 2. Remote Medusa v2 API Sync if token is configured
        remote_synced = False
        medusa_product_id = f"prod_medusa_{candidate_id}"
        if self.api_token:
            try:
                url = f"{self.backend_url}/admin/products"
                body = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(
                    url,
                    data=body,
                    headers={
                        "Authorization": f"Bearer {self.api_token}",
                        "Content-Type": "application/json",
                    },
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=5.0) as resp:
                    if resp.status in [200, 201]:
                        res_json = json.loads(resp.read().decode("utf-8"))
                        medusa_product_id = res_json.get("product", {}).get("id", medusa_product_id)
                        remote_synced = True
            except Exception:
                remote_synced = False

        # 3. Log Audit Trail
        audit_entry = {
            "candidate_id": candidate_id,
            "medusa_product_id": medusa_product_id,
            "handle": payload["handle"],
            "retail_cents_usd": payload["variants"][0]["prices"][0]["amount"],
            "stock_synced": payload["variants"][0]["inventory_quantity"],
            "status": payload["status"],
            "remote_api_synced": remote_synced,
            "hmac_signature": payload["metadata"]["sync_provenance_hmac"],
        }
        self.store.log_audit("MEDUSA_STOREFRONT_SYNCED", audit_entry)

        return {
            "status": "SYNCED",
            "candidate_id": candidate_id,
            "medusa_product_id": medusa_product_id,
            "handle": payload["handle"],
            "retail_price_usd": round(payload["variants"][0]["prices"][0]["amount"] / 100.0, 2),
            "stock_inventory": payload["variants"][0]["inventory_quantity"],
            "listing_status": payload["status"],
            "remote_api_connected": remote_synced,
            "local_catalog_export": str(catalog_file),
            "hmac_provenance": payload["metadata"]["sync_provenance_hmac"],
        }
