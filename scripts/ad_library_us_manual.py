#!/usr/bin/env python3
"""
US Ad Library Manual Competitor Check

The Meta Ad Library API does NOT return commercial US ads (DSA ad-repository
rules only compel EU/UK disclosure). This script is the local record of a
manual web-UI count. It does NOT call Meta.

Usage:
  python3 ad_library_us_manual.py --product "Bamboo Drawer Organizer" --check
  python3 ad_library_us_manual.py --product "Bamboo Drawer Organizer" --advertiser "Brand X" --first-seen 2026-07-01 --active --ads 12 --likes 50000
  python3 ad_library_us_manual.py --product "Bamboo Drawer Organizer" --report
"""
import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports"


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def today_slug():
    return date.today().isoformat()


def report_path(product):
    return REPORTS / f"{today_slug()}-us-ad-library-manual-{slugify(product)}.md"


def load_competitors(product):
    """Load existing competitor list, or return empty list."""
    p = report_path(product)
    if not p.exists():
        return []
    text = p.read_text(encoding="utf-8")
    # Parse naive block format
    blocks = re.findall(
        r"### (.+?)\n(.+?)(?=\n### |\Z)",
        text,
        re.DOTALL,
    )
    out = []
    for name, body in blocks:
        if name.strip().lower() == "summary":
            continue
        first = re.search(r"first_seen:\s*(\S+)", body)
        last = re.search(r"last_seen:\s*(\S+)", body)
        ads = re.search(r"ad_count:\s*(\d+)", body)
        likes = re.search(r"page_likes:\s*(\d+)", body)
        active = "active: true" in body
        out.append({
            "name": name.strip(),
            "first_seen": first.group(1) if first else "?",
            "last_seen": last.group(1) if last else "?",
            "ad_count": int(ads.group(1)) if ads else 0,
            "page_likes": int(likes.group(1)) if likes else 0,
            "active": active,
        })
    return out


def save_competitors(product, competitors):
    p = report_path(product)
    p.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# US Meta Ad Library Manual Check — {product}",
        "",
        f"**Date**: {today_slug()}",
        f"**Source**: facebook.com/ads/library (manual web UI count)",
        f"**Note**: Meta Ad Library API does not return commercial US ads. Counts are manual.",
        "",
        "## Manual Procedure",
        "1. facebook.com/ads/library/?active_status=active&ad_type=all&country=US",
        "2. Search: exact product name + 2-3 feature keywords",
        "3. Count distinct page names",
        "4. For each: first-seen, last-seen, ad count, page likes",
        "5. Cross-check on TikTok Creative Center (US filter) and Google Shopping",
        "",
        "## Advertisers",
        "",
    ]
    for c in competitors:
        lines.append(f"### {c['name']}")
        lines.append(f"- first_seen: {c['first_seen']}")
        lines.append(f"- last_seen: {c['last_seen']}")
        lines.append(f"- ad_count: {c['ad_count']}")
        lines.append(f"- page_likes: {c['page_likes']}")
        lines.append(f"- active: {str(c['active']).lower()}")
        lines.append("")
    lines.append("### Summary")
    lines.append("")
    return p, "\n".join(lines)


def render_report(product, competitors, tikTok_hashtags=None, google_shopping=None):
    p, header = save_competitors(product, competitors)
    n = len(competitors)
    sustained = [c for c in competitors if c["active"] and _days_active(c) >= 30]
    summary = [
        f"- Total distinct advertisers (US Meta): **{n}**",
        f"- Active 30+ days: **{len(sustained)}**",
        f"- Saturated (>15 advertisers): **{'YES' if n > 15 else 'NO'}**",
    ]
    if tikTok_hashtags:
        summary.append(f"- TikTok Creative Center hashtags: {', '.join(tikTok_hashtags)}")
    if google_shopping:
        summary.append(f"- Google Shopping: {google_shopping}")

    summary_block = "\n".join(summary)
    verdict_lines = ["", "## Verdict", ""]

    # Gate logic
    if n < 5:
        verdict_lines.append("- FAIL: <5 distinct advertisers (need 5-10)")
    elif n > 15:
        verdict_lines.append("- WARN: >15 advertisers — saturated, cheap entry unlikely")
    else:
        verdict_lines.append(f"- OK: {n} advertisers in target range [5, 15]")

    if len(sustained) < 3:
        verdict_lines.append(f"- FAIL: only {len(sustained)} ads active 30+ days (need 3+)")
    else:
        verdict_lines.append(f"- OK: {len(sustained)} ads active 30+ days (sustained profitability evidence)")

    if n >= 5 and 5 <= n <= 15 and len(sustained) >= 3:
        verdict_lines.append("")
        verdict_lines.append("**US Competitor Check: PASS**")
    else:
        verdict_lines.append("")
        verdict_lines.append("**US Competitor Check: FAIL**")

    final = header + summary_block + "\n".join(verdict_lines) + "\n"
    p.write_text(final, encoding="utf-8")
    print(f"Wrote {p}")
    return p


def _days_active(c):
    try:
        d = datetime.fromisoformat(c["last_seen"]) - datetime.fromisoformat(c["first_seen"])
        return d.days
    except (ValueError, TypeError):
        return 0


def main():
    p = argparse.ArgumentParser(description="US Meta Ad Library manual check (record + score)")
    p.add_argument("--product", required=True, help="Product name")
    p.add_argument("--advertiser", help="Add a single advertiser")
    p.add_argument("--first-seen", help="YYYY-MM-DD")
    p.add_argument("--last-seen", help="YYYY-MM-DD")
    p.add_argument("--ads", type=int, default=1, help="ad count")
    p.add_argument("--likes", type=int, default=0, help="page likes")
    p.add_argument("--inactive", action="store_true", help="Mark as inactive")
    p.add_argument("--check", action="store_true", help="Check current record and print gate result")
    p.add_argument("--report", action="store_true", help="Re-render the report from saved data")
    p.add_argument("--tiktok", help="Comma-separated TikTok Creative Center hashtags")
    p.add_argument("--google", help="Free-form Google Shopping observation")
    args = p.parse_args()

    if args.advertiser:
        competitors = load_competitors(args.product)
        competitors.append({
            "name": args.advertiser,
            "first_seen": args.first_seen or "?",  # type: ignore[arg-type]
            "last_seen": args.last_seen or "?",
            "ad_count": args.ads,
            "page_likes": args.likes,
            "active": not args.inactive,
        })
        tt = args.tiktok.split(",") if args.tiktok else None
        render_report(args.product, competitors, tt, args.google)
        return 0

    if args.check or args.report:
        competitors = load_competitors(args.product)
        if not competitors:
            print(f"No record yet for '{args.product}'. Add advertisers first.")
            return 1
        # Re-render the verdict
        # Re-read existing file to preserve any free-form text, but rewrite the Summary + Verdict blocks.
        existing = report_path(args.product)
        text = existing.read_text(encoding="utf-8")
        # Strip from "### Summary" onward
        text = re.split(r"\n### Summary\n", text)[0]
        # Parse tiktok + google from existing summary if present
        tt = None
        gg = None
        m = re.search(r"TikTok Creative Center hashtags: ([^\n]+)", text)
        if m:
            tt = [h.strip() for h in m.group(1).split(",")]
        m = re.search(r"Google Shopping: ([^\n]+)", text)
        if m:
            gg = m.group(1).strip()
        # Build a fresh report
        p_new, header = save_competitors(args.product, competitors)
        n = len(competitors)
        sustained = [c for c in competitors if c["active"] and _days_active(c) >= 30]
        summary = [
            f"- Total distinct advertisers (US Meta): **{n}**",
            f"- Active 30+ days: **{len(sustained)}**",
            f"- Saturated (>15 advertisers): **{'YES' if n > 15 else 'NO'}**",
        ]
        if tt:
            summary.append(f"- TikTok Creative Center hashtags: {', '.join(tt)}")
        if gg:
            summary.append(f"- Google Shopping: {gg}")
        summary_block = "\n".join(summary)
        verdict = ["", "## Verdict", ""]
        if n < 5:
            verdict.append("- FAIL: <5 distinct advertisers (need 5-10)")
        elif n > 15:
            verdict.append("- WARN: >15 advertisers — saturated, cheap entry unlikely")
        else:
            verdict.append(f"- OK: {n} advertisers in target range [5, 15]")
        if len(sustained) < 3:
            verdict.append(f"- FAIL: only {len(sustained)} ads active 30+ days (need 3+)")
        else:
            verdict.append(f"- OK: {len(sustained)} ads active 30+ days (sustained profitability evidence)")
        if n >= 5 and 5 <= n <= 15 and len(sustained) >= 3:
            verdict.append("")
            verdict.append("**US Competitor Check: PASS**")
        else:
            verdict.append("")
            verdict.append("**US Competitor Check: FAIL**")
        final = header + summary_block + "\n".join(verdict) + "\n"
        existing.write_text(final, encoding="utf-8")
        print(f"Updated {existing}")
        return 0

    p.error("provide --advertiser (add), --check (evaluate), or --report (re-render)")


if __name__ == "__main__":
    sys.exit(main() or 0)
