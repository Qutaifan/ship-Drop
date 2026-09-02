#!/usr/bin/env python3
"""Metapi.io and Meta Graph API dual-backend competitor gate for PROTOCOL-01."""

# Why EU/UK only: The Ad Library returns commercial ads only inside EU/UK (DSA rules).
# This is NOT a limitation to work around — it DECIDES the market.

# BACKENDS:
# 1. METAPI_API_KEY (preferred): No Meta dev account needed. Sign up at metapi.io
# 2. META_ACCESS_TOKEN: Requires Meta developer account + identity verification (days)
#
# Usage:
#   export METAPI_API_KEY=sk_...   # metapi.io — RECOMMENDED (no Meta account needed)
#   # OR:
#   export META_ACCESS_TOKEN=...  # Meta Graph API — requires dev account
#
#   python3 scripts/ad_library.py "electric pepper grinder" --countries DE,FR,NL
#   python3 scripts/ad_library.py --selftest

import sys
import json
import os
import argparse
from datetime import datetime, date

# ------------------------------------------------------------------
# Backend configuration
# ------------------------------------------------------------------
METAPI_API_KEY = os.environ.get("METAPI_API_KEY", "")
META_ACCESS_TOKEN = os.environ.get("META_ACCESS_TOKEN", "")
EU_UK = {"AT","BE","BG","HR","CY","CZ","DK","EE","FI","FR","DE","GR","HU","IE",
         "IT","LV","LT","LU","MT","NL","PL","PT","RO","SK","SI","ES","SE","GB"}
METAPI_ENDPOINT = "https://api.metapi.io/v1/tasks"
META_ENDPOINT = "https://graph.facebook.com/v21.0/ads_archive"

# Gate parameters (PROTOCOL-01)
MIN_COMPETITORS = 5
MIN_AGED_ADS = 3
AGE_DAYS = 30
SATURATION = 15


def get_backend():
    """Auto-detect backend: metapi if key present, else meta if token present."""
    if METAPI_API_KEY:
        return "metapi"
    if META_ACCESS_TOKEN:
        return "meta"
    return ""


def parse_day(s):
    if not s:
        return None
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def evaluate(ads, today=None):
    """Pure gate logic — no network, testable offline."""
    today = today or date.today()
    advertisers, aged = {}, 0
    for ad in ads:
        pid = str(ad.get("page_id") or ad.get("page_name") or "?")
        advertisers.setdefault(pid, {"name": ad.get("page_name") or pid,
                                     "ads": 0, "aged": 0, "reach": 0})
        advertisers[pid]["ads"] += 1
        try:
            advertisers[pid]["reach"] += int(ad.get("eu_total_reach") or 0)
        except (TypeError, ValueError):
            pass
        start = parse_day(ad.get("ad_delivery_start_time"))
        stop  = parse_day(ad.get("ad_delivery_stop_time"))
        running = stop is None or stop >= today
        if start and running and (today - start).days >= AGE_DAYS:
            aged += 1
            advertisers[pid]["aged"] += 1
    n = len(advertisers)
    gates = {
        "competitors": (n >= MIN_COMPETITORS,
                        f"{n} distinct advertisers (PROTOCOL-01 needs >={MIN_COMPETITORS})"),
        "sustained": (aged >= MIN_AGED_ADS,
                      f"{aged} ads running {AGE_DAYS}+ days (needs >={MIN_AGED_ADS})"),
    }
    verdict = "PASS" if all(ok for ok, _ in gates.values()) else "FAIL"
    return {"advertisers": advertisers, "n_advertisers": n, "n_ads": len(ads),
            "aged": aged, "gates": gates, "verdict": verdict,
            "saturated": n > SATURATION, "backend": get_backend()}


def fetch_metapi(term, countries, api_key):
    """Fetch from metapi.io — no Meta account required.
    
    metapi.io uses an async task-based API:
    1. POST /v1/tasks to create a search task
    2. Poll GET /v1/tasks/{task_id}/status until completed
    3. GET /v1/tasks/{task_id}/results to retrieve ads
    """
    import urllib.parse, urllib.request
    country_codes = ",".join(sorted(c.upper() for c in countries if c.upper() in EU_UK))
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # Step 1: Create task
    task_body = json.dumps({"q": term, "ad_type": "ALL", "ad_reached_countries": country_codes, "ad_active_status": "ALL", "limit": 100}).encode()
    try:
        req = urllib.request.Request(METAPI_ENDPOINT, data=task_body, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as r:
            doc = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")[:400]
        msg = f"Metapi API HTTP {e.code}: {body}"
        if e.code == 401:
            msg += ("\\nHINT: METAPI_API_KEY is invalid. "
                    "Get a free key at https://metapi.io/ (no Meta account needed).")
        raise SystemExit(msg)
    except urllib.error.URLError as e:
        raise SystemExit(f"network error reaching metapi.io: {e.reason}")
    
    task_id = doc.get("task_id")
    if not task_id:
        # Maybe it returned results directly
        results = doc.get("data") or doc.get("results") or doc.get("items") or doc.get("ads") or []
        return results
    
    # Step 2: Poll for completion
    status_url = f"https://api.metapi.io/v1/tasks/{task_id}/status"
    ads = []
    for _ in range(10):
        try:
            req = urllib.request.Request(status_url, headers=headers, method="GET")
            with urllib.request.urlopen(req, timeout=60) as r2:
                status_doc = json.loads(r2.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")[:400]
            raise SystemExit(f"Metapi status check failed: HTTP {e.code}: {body}")
        
        if status_doc.get("status") == "completed":
            break
        if status_doc.get("status") == "failed":
            msg = f"Metapi task failed: {status_doc.get('error_message', 'unknown')}"
            raise SystemExit(msg)
        import time
        time.sleep(2)
    
    # Step 3: Get results
    results_url = f"https://api.metapi.io/v1/tasks/{task_id}/results?offset=0&limit=100"
    try:
        req = urllib.request.Request(results_url, headers=headers, method="GET")
        with urllib.request.urlopen(req, timeout=30) as r3:
            res_doc = json.loads(r3.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")[:400]
        raise SystemExit(f"Metapi results fetch failed: HTTP {e.code}: {body}")
    
    results = res_doc.get("data") or res_doc.get("results") or res_doc.get("items") or res_doc.get("ads") or []
    ads.extend(results)
    return ads
def fetch_meta(term, countries, token, limit_pages=5):
    """Fetch from official Meta Graph API — requires verified Meta developer account."""
    import urllib.parse, urllib.request
    ads, after, pages = [], None, 0
    fields = ("id,page_id,page_name,ad_delivery_start_time,"
              "ad_delivery_stop_time,ad_snapshot_url,eu_total_reach,publisher_platforms")
    while pages < limit_pages:
        q = {"access_token": token, "search_terms": term, "ad_type": "ALL",
             "ad_reached_countries": json.dumps(sorted(countries)),
             "ad_active_status": "ALL", "fields": fields, "limit": "100"}
        if after:
            q["after"] = after
        try:
            url = f"{META_ENDPOINT}?{urllib.parse.urlencode(q)}"
            with urllib.request.urlopen(url, timeout=30) as r:
                doc = json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")[:400]
            msg = f"Graph API HTTP {e.code}: {body}"
            if e.code == 190:
                msg += ("\nHINT: Meta token expired (~60 days). "
                        "Regenerate in Meta developer portal. Requires identity verification.")
            if e.code in (401, 403):
                msg += ("\nNOTE: If using metapi.io instead, set METAPI_API_KEY "
                        "(https://metapi.io/, no Meta account needed).")
            raise SystemExit(msg)
        except urllib.error.URLError as e:
            raise SystemExit(f"network error reaching Meta Graph API: {e.reason}")
        ads.extend(doc.get("data") or [])
        after = ((doc.get("paging") or {}).get("cursors") or {}).get("after")
        if not after or not doc.get("data"):
            break
        pages += 1
    return ads


def fetch(term, countries, backend=""):
    """Fetch competitor ads using the auto-detected backend."""
    if not backend:
        backend = get_backend()
    if backend == "metapi":
        if not METAPI_API_KEY:
            raise SystemExit("METAPI_API_KEY not set.\nGet free key at https://metapi.io/ — no Meta account needed.")
        return fetch_metapi(term, countries, METAPI_API_KEY)
    if backend == "meta":
        if not META_ACCESS_TOKEN:
            raise SystemExit(
                "META_ACCESS_TOKEN not set.\n"
                "Create a Meta developer app + identity verification (takes days).\n"
                "ALTERNATIVE: Get METAPI_API_KEY at https://metapi.io/ — no account needed.")
        return fetch_meta(term, countries, META_ACCESS_TOKEN)
    raise SystemExit(f"No API key found. Set METAPI_API_KEY (https://metapi.io/) or META_ACCESS_TOKEN.")


def report(term, countries, res):
    print(f"\nPROTOCOL-01 competitor gate — \"{term}\"  [{','.join(sorted(countries))}]")
    print(f"  Backend             {res.get('backend', 'unknown') or 'unknown'}")
    print(f"  ads sampled         {res['n_ads']}")
    print(f"  distinct advertisers {res['n_advertisers']}")
    print(f"  ads aged {AGE_DAYS}+ days   {res['aged']}\n")
    for ok, desc in res.get("gates", {}).values():
        print(f"  [{'PASS' if ok else 'FAIL'}] {desc}")
    if res.get("saturated"):
        print(f"\n  [WARN] {res['n_advertisers']} advertisers — past saturation line of {SATURATION}. "
              "Profitability proven but cheap entry is not.")
    top = sorted(res.get("advertisers", {}).values(), key=lambda a: -a.get("ads", 0))[:8]
    if top:
        print("\n  advertiser                        ads  aged  reach")
        for a in top:
            print(f"  {a.get('name','?')[:32]:32}  {a.get('ads',0):>3}  "
                  f"{a.get('aged',0):>4}  {a.get('reach',0):>8,}")
    print(f"\n  VERDICT: {res.get('verdict', 'UNKNOWN')}")
    print("\n--- paste into products/<name>.md ---")
    print("## Competitor Check")
    print(f"- Competitors running ads (need 5-10): {res.get('n_advertisers', 0)}")
    print(f"- Ads active 30+ days (need >=3): {res.get('aged', 0)}")
    print(f"- Backend: {res.get('backend', 'unknown')}")


def selftest():
    """Offline gate logic test — no API keys required."""
    today = date(2026, 8, 30)
    def ad(pid, start, stop=None):
        return {"page_id": pid, "page_name": f"page{pid}",
                "ad_delivery_start_time": start, "ad_delivery_stop_time": stop}
    old = "2026-06-01"; recent = "2026-08-25"
    cases = [
        ("5 advertisers, 3 aged -> PASS",
         [ad(i, old) for i in range(1,4)] + [ad(4,recent),ad(5,recent)], "PASS", False),
        ("4 advertisers -> FAIL", [ad(i, old) for i in range(1,5)], "FAIL", False),
        ("6 advertisers but only 2 aged -> FAIL",
         [ad(i, old) for i in range(1,3)] + [ad(i, recent) for i in range(3,7)], "FAIL", False),
        ("stopped aged ad doesn't count -> FAIL",
         [ad(i, old, "2026-07-01") for i in range(1,7)], "FAIL", False),
        ("20 advertisers -> PASS saturated",
         [ad(i, old) for i in range(1,21)], "PASS", True),
        ("empty -> FAIL", [], "FAIL", False),
    ]
    ok = True
    print("ad_library gate self-test")
    for name, ads, want_v, want_sat in cases:
        r = evaluate(ads, today=today)
        r["backend"] = "selftest"
        good = r["verdict"] == want_v and r.get("saturated") == want_sat
        ok = ok and good
        if not good:
            print(f"  FAIL {name} -> got verdict={r['verdict']}, sat={r.get('saturated')}")
        else:
            print(f"  OK   {name}")
    print(f"\nSELFTEST: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(
        description="PROTOCOL-01 competitor gate: metapi.io (no Meta account) or Meta Graph API")
    ap.add_argument("term", nargs="?", help="product search term")
    ap.add_argument("--countries", default="DE,FR,NL,IT,ES",
                    help="comma-separated EU/UK ISO codes (default DE,FR,NL,IT,ES)")
    ap.add_argument("--fixture", help="replay a saved JSON payload")
    ap.add_argument("--selftest", action="store_true", help="run offline gate tests")
    ap.add_argument("--backend", default="auto", choices=["auto","metapi","meta"],
                    help="Backend: metapi (no Meta account, recommended), meta (official), auto (default)")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.term:
        ap.error("a search term is required (or use --selftest)")
    countries = {c.strip().upper() for c in a.countries.split(",") if c.strip()}
    bad = countries - EU_UK
    if bad:
        raise SystemExit(f"{', '.join(sorted(bad))} is outside EU/UK. No commercial ads there.")
    backend = a.backend
    if backend == "auto":
        backend = get_backend()
    if a.fixture:
        with open(a.fixture, encoding="utf-8") as f:
            doc = json.load(f)
        ads = doc.get("data", doc) if isinstance(doc, dict) else doc
        res = evaluate(ads)
        res["backend"] = "fixture"
    else:
        ads = fetch(a.term, countries, backend=backend)
        res = evaluate(ads)
        res["backend"] = get_backend()
    report(a.term, countries, res)
    return 0


if __name__ == "__main__":
    sys.exit(main())
