#!/usr/bin/env python3
"""
Meta Ad Library client — runs the PROTOCOL-01 competitor gate.

WHY THIS IS EU/UK-ONLY
----------------------
The Ad Library API returns *commercial* (non-political) ads only when
`ad_type=ALL` is paired with `ad_reached_countries` inside the EU or UK. That
coverage exists because the DSA ad-repository rules force it, not by Meta's
choice. Outside the EU/UK the API returns political and social-issue ads only,
so competitor research for a normal product is impossible programmatically.

This is not a limitation to work around — it decides the market. An EU-first
launch is the only one where this gate can be automated.

Known constraints, all upstream:
  * access token expires ~60 days; identity verification is required first
  * ~200 Graph API calls/hour including pagination
  * commercial EU ads are retained ~12 months
  * reach only; no impressions, spend, CTR or engagement

Usage:
  export META_ACCESS_TOKEN=...
  python3 scripts/ad_library.py "hard water shower filter" --countries DE,FR,NL
  python3 scripts/ad_library.py --selftest        # offline; proves the gate logic
  python3 scripts/ad_library.py "term" --fixture sample.json   # offline replay

Stdlib only.
"""
import argparse
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

GRAPH_VERSION = os.environ.get("META_GRAPH_VERSION", "v21.0")
ENDPOINT = f"https://graph.facebook.com/{GRAPH_VERSION}/ads_archive"
EU_UK = {"AT","BE","BG","HR","CY","CZ","DK","EE","FI","FR","DE","GR","HU","IE",
         "IT","LV","LT","LU","MT","NL","PL","PT","RO","SK","SI","ES","SE","GB"}
FIELDS = ("id,page_id,page_name,ad_delivery_start_time,ad_delivery_stop_time,"
          "ad_snapshot_url,eu_total_reach,publisher_platforms")

MIN_COMPETITORS = 5      # PROTOCOL-01
MIN_AGED_ADS = 3         # PROTOCOL-01: >=3 ads running 30+ days
AGE_DAYS = 30
SATURATION = 15          # reports/2026-08-30-trend-scan.md: past this, CPMs are bid out


def parse_day(s):
    if not s:
        return None
    try:
        return dt.datetime.strptime(s[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def evaluate(ads, today=None):
    """Pure gate logic — no network, so it is testable offline."""
    today = today or dt.date.today()
    advertisers, aged = {}, 0
    for ad in ads:
        pid = str(ad.get("page_id") or ad.get("page_name") or "?")
        advertisers.setdefault(pid, {"name": ad.get("page_name") or pid, "ads": 0,
                                     "aged": 0, "reach": 0})
        advertisers[pid]["ads"] += 1
        try:
            advertisers[pid]["reach"] += int(ad.get("eu_total_reach") or 0)
        except (TypeError, ValueError):
            pass
        start = parse_day(ad.get("ad_delivery_start_time"))
        stop = parse_day(ad.get("ad_delivery_stop_time"))
        running = stop is None or stop >= today
        if start and running and (today - start).days >= AGE_DAYS:
            aged += 1
            advertisers[pid]["aged"] += 1

    n = len(advertisers)
    gates = {
        "competitors": (n >= MIN_COMPETITORS, f"{n} distinct advertisers "
                        f"(PROTOCOL-01 needs >={MIN_COMPETITORS})"),
        "sustained": (aged >= MIN_AGED_ADS, f"{aged} ads running {AGE_DAYS}+ days "
                      f"(needs >={MIN_AGED_ADS})"),
    }
    verdict = "PASS" if all(ok for ok, _ in gates.values()) else "FAIL"
    return {"advertisers": advertisers, "n_advertisers": n, "n_ads": len(ads),
            "aged": aged, "gates": gates, "verdict": verdict,
            "saturated": n > SATURATION}


def fetch(term, countries, token, limit_pages=5):
    ads, after, pages = [], None, 0
    while pages < limit_pages:
        q = {"access_token": token, "search_terms": term, "ad_type": "ALL",
             "ad_reached_countries": json.dumps(sorted(countries)),
             "ad_active_status": "ALL", "fields": FIELDS, "limit": "100"}
        if after:
            q["after"] = after
        try:
            with urllib.request.urlopen(f"{ENDPOINT}?{urllib.parse.urlencode(q)}",
                                        timeout=30) as r:
                doc = json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")[:400]
            msg = f"Graph API HTTP {e.code}: {body}"
            if e.code == 400 and "ad_type" in body:
                msg += ("\nHINT: ad_type=ALL only returns commercial ads for EU/UK "
                        "countries. Check --countries.")
            if e.code == 190:
                msg += "\nHINT: token expired (~60 day lifetime) — regenerate it."
            raise SystemExit(msg)
        except urllib.error.URLError as e:
            raise SystemExit(f"network error reaching Graph API: {e.reason}")
        ads.extend(doc.get("data") or [])
        after = ((doc.get("paging") or {}).get("cursors") or {}).get("after")
        if not after or not doc.get("data"):
            break
        pages += 1
    return ads


def report(term, countries, res):
    print(f"\nPROTOCOL-01 competitor gate — \"{term}\"  [{','.join(sorted(countries))}]")
    print(f"  ads sampled        {res['n_ads']}")
    print(f"  distinct advertisers {res['n_advertisers']}")
    print(f"  ads aged {AGE_DAYS}+ days   {res['aged']}\n")
    for ok, desc in res["gates"].values():
        print(f"  [{'PASS' if ok else 'FAIL'}] {desc}")
    if res["saturated"]:
        print(f"\n  [WARN] {res['n_advertisers']} advertisers is past the saturation "
              f"line of {SATURATION}. Sustained profitability is proven; cheap entry "
              f"is not. Expect bid-up CPMs.")
    top = sorted(res["advertisers"].values(), key=lambda a: -a["ads"])[:8]
    if top:
        print("\n  advertiser                        ads  aged  reach")
        for a in top:
            print(f"  {a['name'][:32]:32}  {a['ads']:>3}  {a['aged']:>4}  {a['reach']:>8,}")
    print(f"\n  VERDICT: {res['verdict']}")
    print("\n--- paste into products/<name>.md ---")
    print("## Competitor Check")
    print(f"- Competitors running ads (need 5-10): {res['n_advertisers']}")
    print(f"- Ads active 30+ days (need >=3, proves sustained profitability): {res['aged']}")


def selftest():
    """The gate logic must fail on bad input, not just pass on good."""
    today = dt.date(2026, 8, 30)
    old = "2026-06-01"    # 90 days
    recent = "2026-08-25"  # 5 days

    def ad(pid, start, stop=None):
        return {"page_id": pid, "page_name": f"page{pid}",
                "ad_delivery_start_time": start, "ad_delivery_stop_time": stop}

    cases = [
        ("5 advertisers, 3 aged ads -> PASS",
         [ad(i, old) for i in range(1, 4)] + [ad(4, recent), ad(5, recent)], "PASS", False),
        ("4 advertisers -> FAIL (below competitor floor)",
         [ad(i, old) for i in range(1, 5)], "FAIL", False),
        ("6 advertisers but only 2 aged -> FAIL",
         [ad(i, old) for i in range(1, 3)] + [ad(i, recent) for i in range(3, 7)],
         "FAIL", False),
        ("aged ad already stopped does not count -> FAIL",
         [ad(i, old, "2026-07-01") for i in range(1, 7)], "FAIL", False),
        ("20 advertisers -> PASS but flagged saturated",
         [ad(i, old) for i in range(1, 21)], "PASS", True),
        ("empty result -> FAIL", [], "FAIL", False),
    ]
    ok = True
    print("ad_library gate self-test\n")
    for name, ads, want_verdict, want_sat in cases:
        r = evaluate(ads, today=today)
        good = r["verdict"] == want_verdict and r["saturated"] == want_sat
        ok = ok and good
        print(f"  {'OK  ' if good else 'FAIL'} {name}"
              + ("" if good else f"  -> got {r['verdict']}, saturated={r['saturated']}"))
    print("\nSELFTEST: " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description="PROTOCOL-01 competitor gate via Meta Ad Library")
    ap.add_argument("term", nargs="?", help="product search term")
    ap.add_argument("--countries", default="DE,FR,NL,IT,ES",
                    help="comma-separated EU/UK ISO codes (default DE,FR,NL,IT,ES)")
    ap.add_argument("--fixture", help="replay a saved JSON payload instead of calling the API")
    ap.add_argument("--selftest", action="store_true", help="run offline gate tests")
    a = ap.parse_args()

    if a.selftest:
        return selftest()
    if not a.term:
        ap.error("a search term is required (or use --selftest)")

    countries = {c.strip().upper() for c in a.countries.split(",") if c.strip()}
    bad = countries - EU_UK
    if bad:
        raise SystemExit(
            f"{', '.join(sorted(bad))} is outside the EU/UK. The API returns only "
            f"political ads there — commercial competitor data does not exist for "
            f"those markets. This is why the project validates EU-first.")

    if a.fixture:
        with open(a.fixture, encoding="utf-8") as f:
            doc = json.load(f)
        ads = doc.get("data", doc) if isinstance(doc, dict) else doc
    else:
        token = os.environ.get("META_ACCESS_TOKEN")
        if not token:
            raise SystemExit(
                "META_ACCESS_TOKEN is not set.\nCreate a Meta developer app, complete "
                "identity verification, then generate a token. Verification routinely "
                "takes days — start it before you need the data.")
        ads = fetch(a.term, countries, token)

    report(a.term, countries, evaluate(ads))
    return 0


if __name__ == "__main__":
    sys.exit(main())
