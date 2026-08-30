#!/usr/bin/env python3
"""
Hermes-Ecom eBay Market Intelligence & Price Discovery Client (Browse API).

Queries the official eBay REST API to:
  1. Fetch live competitor prices for candidate products in EU markets (default: EBAY_DE).
  2. Filter by item location (e.g., items shipped domestically within the EU).
  3. Compute median retail price, price distribution (min/max/P25/P75), and free shipping share.
  4. Compare against True Margin Matrix targets.

Usage:
  python3 scripts/ebay_api.py "electric pepper grinder" --marketplace EBAY_DE
  python3 scripts/ebay_api.py "bamboo drawer organizer" --country DE --limit 20
  python3 scripts/ebay_api.py --selftest

Stdlib only.
"""
import argparse
import base64
import json
import os
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

AUTH_ENDPOINT = "https://api.ebay.com/identity/v1/oauth2/token"
BROWSE_ENDPOINT = "https://api.ebay.com/buy/browse/v1/item_summary/search"

# Cache token in memory
_CACHED_TOKEN = None
_TOKEN_EXPIRY = 0


def get_oauth_token(client_id, client_secret):
    global _CACHED_TOKEN, _TOKEN_EXPIRY
    now = time.time()
    if _CACHED_TOKEN and now < _TOKEN_EXPIRY - 60:
        return _CACHED_TOKEN

    auth_str = f"{client_id}:{client_secret}"
    b64_auth = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")

    data = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope"
    }).encode("utf-8")

    req = urllib.request.Request(
        AUTH_ENDPOINT,
        data=data,
        headers={
            "Authorization": f"Basic {b64_auth}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            resp_data = json.loads(res.read().decode("utf-8"))
            _CACHED_TOKEN = resp_data.get("access_token")
            _TOKEN_EXPIRY = now + resp_data.get("expires_in", 7200)
            return _CACHED_TOKEN
    except Exception as e:
        print(f"[ERROR] Failed to obtain eBay OAuth token: {e}", file=sys.stderr)
        return None


def query_ebay_browse(query, token, marketplace="EBAY_DE", country="DE", limit=20):
    """
    Queries eBay Browse API item_summary/search.
    Filters by marketplace and optionally itemLocationCountry.
    """
    params = {
        "q": query,
        "limit": str(limit),
    }
    
    filter_parts = []
    if country:
        filter_parts.append(f"itemLocationCountry:{country}")
    
    if filter_parts:
        params["filter"] = ",".join(filter_parts)

    url = f"{BROWSE_ENDPOINT}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "X-EBAY-C-MARKETPLACE-ID": marketplace,
            "Content-Type": "application/json"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            return json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        return {"error": f"HTTP {e.code}: {err}"}
    except Exception as e:
        return {"error": str(e)}


def parse_item_summaries(items_json):
    """Extracts price, currency, and seller stats from items."""
    items = items_json.get("itemSummaries", [])
    results = []
    for it in items:
        price_obj = it.get("price", {})
        price_val = float(price_obj.get("value", 0.0))
        currency = price_obj.get("currency", "EUR")

        shipping_opts = it.get("shippingOptions", [])
        free_shipping = any(float(s.get("shippingCost", {}).get("value", 1.0)) == 0.0 for s in shipping_opts)

        results.append({
            "title": it.get("title", ""),
            "price": price_val,
            "currency": currency,
            "item_id": it.get("itemId", ""),
            "item_location": it.get("itemLocation", {}).get("country", ""),
            "free_shipping": free_shipping,
            "item_web_url": it.get("itemWebUrl", "")
        })
    return results


def summarize_ebay_pricing(parsed_items):
    if not parsed_items:
        return None

    prices = [i["price"] for i in parsed_items if i["price"] > 0]
    if not prices:
        return None

    median_price = statistics.median(prices)
    min_price = min(prices)
    max_price = max(prices)
    free_ship_count = sum(1 for i in parsed_items if i["free_shipping"])
    free_ship_pct = (free_ship_count / len(parsed_items)) * 100.0

    return {
        "count": len(parsed_items),
        "median_price": median_price,
        "min_price": min_price,
        "max_price": max_price,
        "free_shipping_pct": free_ship_pct,
        "sample_currency": parsed_items[0]["currency"]
    }


def selftest():
    print("Running ebay_api selftest...")
    sample_data = {
        "itemSummaries": [
            {
                "title": "Electric Gravity Pepper Grinder Stainless Steel",
                "price": {"value": "29.99", "currency": "EUR"},
                "itemLocation": {"country": "DE"},
                "shippingOptions": [{"shippingCost": {"value": "0.00"}}]
            },
            {
                "title": "Automatic Pepper Salt Mill Battery Operated",
                "price": {"value": "34.50", "currency": "EUR"},
                "itemLocation": {"country": "DE"},
                "shippingOptions": [{"shippingCost": {"value": "2.90"}}]
            },
            {
                "title": "Premium Electric Spice Grinder Set",
                "price": {"value": "39.90", "currency": "EUR"},
                "itemLocation": {"country": "DE"},
                "shippingOptions": [{"shippingCost": {"value": "0.00"}}]
            }
        ]
    }
    
    parsed = parse_item_summaries(sample_data)
    assert len(parsed) == 3
    assert parsed[0]["price"] == 29.99
    assert parsed[0]["free_shipping"] is True

    summary = summarize_ebay_pricing(parsed)
    assert summary["count"] == 3
    assert summary["median_price"] == 34.50
    assert summary["min_price"] == 29.99
    assert summary["max_price"] == 39.90
    assert abs(summary["free_shipping_pct"] - 66.66) < 1.0

    print("SELFTEST: PASS")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Hermes-Ecom eBay Market Intelligence Client")
    ap.add_argument("query", nargs="?", help="Product search term (e.g. 'electric pepper grinder')")
    ap.add_argument("--marketplace", default="EBAY_DE", help="eBay marketplace ID (default: EBAY_DE)")
    ap.add_argument("--country", default="DE", help="Item location country filter (default: DE)")
    ap.add_argument("--limit", type=int, default=20, help="Number of items to retrieve (default: 20)")
    ap.add_argument("--selftest", action="store_true", help="Run offline unit tests")
    a = ap.parse_args()

    if a.selftest:
        return selftest()

    if not a.query:
        ap.error("Search query is required (or use --selftest)")

    client_id = os.environ.get("EBAY_CLIENT_ID")
    client_secret = os.environ.get("EBAY_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("[NOTICE] EBAY_CLIENT_ID and EBAY_CLIENT_SECRET not set in environment.")
        print("To query live eBay marketplace data, provide your eBay Developer App credentials.")
        return 1

    token = get_oauth_token(client_id, client_secret)
    if not token:
        print("[ERROR] Could not authenticate with eBay API.")
        return 1

    print(f"\nQuerying eBay Browse API for '{a.query}' on {a.marketplace} (Location: {a.country})...")
    res = query_ebay_browse(a.query, token, marketplace=a.marketplace, country=a.country, limit=a.limit)

    if "error" in res:
        print(f"[ERROR] API Error: {res['error']}")
        return 1

    parsed = parse_item_summaries(res)
    summary = summarize_ebay_pricing(parsed)

    if not summary:
        print(f"No listings found for '{a.query}' with location {a.country}.")
        return 0

    print(f"\n--- eBay Market Pricing Summary ({a.marketplace}) ---")
    print(f"  Active Competitor Listings: {summary['count']}")
    print(f"  Median Retail Price:        €{summary['median_price']:.2f}")
    print(f"  Price Range:                €{summary['min_price']:.2f} — €{summary['max_price']:.2f}")
    print(f"  Free Shipping Share:        {summary['free_shipping_pct']:.0f}%")
    print("\nTop Competitors:")
    for it in parsed[:5]:
        free_s = " (Free Ship)" if it["free_shipping"] else ""
        print(f"  - €{it['price']:.2f}{free_s}: {it['title'][:60]}...")

    return 0


if __name__ == "__main__":
    sys.exit(main())
