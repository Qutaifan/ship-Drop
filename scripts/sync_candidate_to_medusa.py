#!/usr/bin/env python3
"""Sync approved Hermes candidate dossiers into Medusa v2 draft product listings."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agency.core.store import Store

DRAFTS_DIR = ROOT / "data" / "medusa_drafts"


def slugify(text: str) -> str:
    text = text.lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def candidate_to_medusa_payload(cand: Dict[str, Any], latest_ver: Dict[str, Any] | None = None) -> Dict[str, Any]:
    name = cand.get("product_name", "Untitled Product")
    cid = cand.get("candidate_id", "cand-unknown")
    handle = slugify(name)[:50]
    econ = cand.get("unit_economics", {})

    gross_price = float(econ.get("gross_selling_price", 29.99))
    currency = econ.get("currency", "USD").lower()
    wh = latest_ver.get("warehouse_country", "US") if latest_ver else "US"
    stock = latest_ver.get("stock_level", 100) if latest_ver else 100
    stability = latest_ver.get("stability_score", 0.90) if latest_ver else 0.90

    # Pricing calculations: Medusa expects integer cents (e.g. 2999)
    usd_cents = int(round(gross_price * 100))
    eur_cents = int(round((gross_price * 0.92) * 100))

    description = f"""**{name}**

Engineered for reliability and instant satisfaction.

### Key Highlights
- **Direct Domestic Fulfillment**: Dispatched directly from verified {wh} warehouses ({latest_ver.get('lead_days_min', 3)}-{latest_ver.get('lead_days_max', 5)} day tracked transit via {latest_ver.get('shipping_method', 'USPS') if latest_ver else 'USPS'}).
- **Audited Supplier Reliability**: Sourced through pre-screened supply partners with verified packaging grade ({latest_ver.get('packaging_type', 'custom_box') if latest_ver else 'standard'}).
- **100% Quality Inspected**: Backed by our 30-day domestic satisfaction guarantee.
"""

    return {
        "title": name,
        "subtitle": "Premium Direct-Fulfillment Selection",
        "description": description.strip(),
        "handle": handle,
        "is_giftcard": False,
        "discountable": True,
        "status": "draft",  # Strict draft status — never auto-publish
        "options": [
            {"title": "Standard Selection"}
        ],
        "variants": [
            {
                "title": "Default",
                "sku": f"HERMES-{cid[:16].upper()}",
                "manage_inventory": True,
                "inventory_quantity": stock,
                "prices": [
                    {"currency_code": "usd", "amount": usd_cents},
                    {"currency_code": "eur", "amount": eur_cents},
                ],
                "options": ["Default"],
            }
        ],
        "metadata": {
            "hermes_candidate_id": cid,
            "hermes_stability_score": stability,
            "verified_warehouse_country": wh,
            "verified_warehouse_type": latest_ver.get("warehouse_type", "domestic") if latest_ver else "domestic",
            "sourcing_supplier": latest_ver.get("supplier_id", "primary-supplier") if latest_ver else "primary-supplier",
            "eu_ioss_eligible": True,
        }
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync Hermes Candidates to Medusa v2 Draft Listings")
    parser.add_argument("candidate_id", nargs="?", help="Target candidate ID (syncs all approved if omitted)")
    parser.add_argument("--out", help="Optional output JSON path")
    args = parser.parse_args()

    store = Store()
    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)

    if args.candidate_id:
        cand = store.get_candidate(args.candidate_id)
        if not cand:
            print(f"❌ Candidate '{args.candidate_id}' not found.")
            sys.exit(1)
        candidates = [cand]
    else:
        candidates = store.list_candidates()

    synced = 0
    print("\n" + "═" * 70)
    print("  🛍️ MEDUSA v2 STOREFRONT PRODUCT SYNC (DRAFT MODE)")
    print("═" * 70)

    for c in candidates:
        cid = c.get("candidate_id")
        latest_ver = store.get_latest_verification_for_candidate(cid)
        payload = candidate_to_medusa_payload(c, latest_ver)

        out_file = DRAFTS_DIR / f"{cid}.medusa.json"
        with out_file.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

        store.log_audit("MEDUSA_DRAFT_GENERATED", {
            "candidate_id": cid,
            "handle": payload["handle"],
            "status": "draft",
            "output_path": str(out_file)
        })

        price_str = f"${payload['variants'][0]['prices'][0]['amount'] / 100:.2f}"
        print(f"  ✓ Synced '{payload['title'][:36]}' -> {out_file.name} ({price_str})")
        synced += 1

    print("-" * 70)
    print(f"✨ Successfully generated {synced} Medusa v2 draft product payload(s) in {DRAFTS_DIR}")
    print("═" * 70 + "\n")


if __name__ == "__main__":
    main()
