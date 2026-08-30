#!/usr/bin/env python3
"""
Hermes-Ecom Multi-Pass Demand & Demo-Burden Screen — PROTOCOL-01 Pre-Screen.

Automates the corrected YouTube demo-burden screening protocol (reports/2026-08-30-sweep-audit.md):
  1. Pulls top 25 YouTube videos via yt-dlp.
  2. Tests two query variants (<term> and <term> demo) to measure ranking stability.
  3. Measures:
     - Median duration (how long the market takes to explain it)
     - Short-form share (share of videos <= 60s)
     - Skeptic ratio (proof burden: share of titles with are/does/really/worth/test/review)
     - Median view count (demand floor: separates real interest from zero-demand commodities)
  4. Rejection Rule: Skeptic ratio >= 50% fails Criterion 3. Median views < 1,000 fails demand floor.

Usage:
  python3 scripts/demand_screen.py "electric pepper grinder"
  python3 scripts/demand_screen.py --fixture reports/yt_results_raw.json
  python3 scripts/demand_screen.py --selftest

Stdlib only (yt-dlp optional for live fetching).
"""
import argparse
import datetime as dt
import json
import os
import shutil
import statistics
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SKEPTIC_KEYWORDS = ["are ", "does ", "really", "worth", "test", "review"]
DEMAND_FLOOR_MEDIAN_VIEWS = 2500
SKEPTIC_REJECT_THRESHOLD = 0.50


def parse_video_item(item):
    """Extracts duration, title, and view count from a yt-dlp entry."""
    title = str(item.get("title") or "")
    duration = item.get("duration")
    views = item.get("view_count")
    try:
        duration = float(duration) if duration is not None else None
    except (ValueError, TypeError):
        duration = None
    try:
        views = int(views) if views is not None else None
    except (ValueError, TypeError):
        views = None
    return {"title": title, "duration": duration, "view_count": views}


def analyze_dataset(entries):
    """Calculates demo-burden metrics on a list of video items."""
    if not entries:
        return None

    titles = [e["title"] for e in entries if e.get("title")]
    durations = [e["duration"] for e in entries if e.get("duration") is not None and e["duration"] > 0]
    views = [e["view_count"] for e in entries if e.get("view_count") is not None and e["view_count"] >= 0]

    n_total = len(titles)
    if n_total == 0:
        return None

    skeptic_count = sum(1 for t in titles if any(w in t.lower() for w in SKEPTIC_KEYWORDS))
    skeptic_ratio = round(skeptic_count / n_total, 2)

    short_form_count = sum(1 for d in durations if 0 < d <= 60)
    short_form_share = round(short_form_count / n_total, 2)

    median_duration = int(statistics.median(durations)) if durations else 0
    median_views = int(statistics.median(views)) if views else 0
    max_views = max(views) if views else 0

    # Gate logic
    criterion_3_pass = skeptic_ratio < SKEPTIC_REJECT_THRESHOLD
    demand_floor_pass = median_views >= DEMAND_FLOOR_MEDIAN_VIEWS if views else True

    return {
        "n_videos": n_total,
        "titles": titles,
        "durations": durations,
        "views": views,
        "skeptic_ratio": skeptic_ratio,
        "short_form_share": short_form_share,
        "median_duration": median_duration,
        "median_views": median_views,
        "max_views": max_views,
        "criterion_3_pass": criterion_3_pass,
        "demand_floor_pass": demand_floor_pass,
    }


def fetch_youtube_results(query, max_results=25):
    """Runs yt-dlp via CLI to fetch video metadata."""
    if not shutil.which("yt-dlp"):
        raise SystemExit(
            "yt-dlp is not installed or not in PATH.\n"
            "Install it via: pip install yt-dlp (or test with --fixture / --selftest)."
        )

    cmd = [
        "yt-dlp",
        f"ytsearch{max_results}:{query}",
        "--flat-playlist",
        "--dump-json",
        "--no-warnings",
        "--quiet",
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60, check=True)
    except subprocess.TimeoutExpired:
        raise SystemExit("yt-dlp query timed out.")
    except subprocess.CalledProcessError as e:
        raise SystemExit(f"yt-dlp error (code {e.returncode}): {e.stderr[:300]}")

    entries = []
    for line in proc.stdout.strip().splitlines():
        if line.strip():
            try:
                doc = json.loads(line)
                entries.append(parse_video_item(doc))
            except json.JSONDecodeError:
                continue
    return entries


def evaluate_candidate(candidate_name, entries_pass1, entries_pass2=None):
    r1 = analyze_dataset(entries_pass1)
    r2 = analyze_dataset(entries_pass2) if entries_pass2 else None

    # Check stability if 2 passes were run
    is_stable = True
    drift = 0.0
    if r1 and r2:
        drift = abs(r1["skeptic_ratio"] - r2["skeptic_ratio"])
        if drift > 0.15:
            is_stable = False

    return {
        "candidate": candidate_name,
        "pass1": r1,
        "pass2": r2,
        "is_stable": is_stable,
        "drift": drift,
    }


def format_report(eval_res):
    p1 = eval_res["pass1"]
    if not p1:
        return "No data found."

    lines = []
    lines.append(f"\nDemand & Demo-Burden Screen — \"{eval_res['candidate']}\"")
    lines.append(f"  Sampled Videos:       {p1['n_videos']}")
    lines.append(f"  Median Duration:      {p1['median_duration']}s")
    lines.append(f"  Short-Form Share:     {p1['short_form_share']:.0%}")
    lines.append(f"  Skeptic Ratio:        {p1['skeptic_ratio']:.0%} (Reject if ≥{SKEPTIC_REJECT_THRESHOLD:.0%})")
    if p1.get("median_views"):
        lines.append(f"  Median Views:         {p1['median_views']:,}")
        lines.append(f"  Max Views:            {p1['max_views']:,}")

    if eval_res["pass2"]:
        p2 = eval_res["pass2"]
        lines.append(f"  Stability Check:      {'STABLE' if eval_res['is_stable'] else 'NOISY DRIFT'} (Pass 2 Skeptic: {p2['skeptic_ratio']:.0%}, Drift: {eval_res['drift']:.0%})")

    lines.append("\n--- Gates Assessment ---")
    lines.append(f"  [Criterion 3] Proof Burden: {'PASS' if p1['criterion_3_pass'] else 'FAIL (High proof burden)'}")
    lines.append(f"  [Demand Floor] View Count:   {'PASS' if p1['demand_floor_pass'] else 'FAIL (Near-zero content demand)'}")

    # A verdict may not be issued from a metric the run itself flagged as unstable.
    # YouTube search ranking drifts between calls; when two passes disagree by more
    # than the drift threshold, the number is noise and cannot support a decision.
    if p1["criterion_3_pass"] and p1["demand_floor_pass"]:
        c3_verdict = "PASS" if eval_res["is_stable"] else "INCONCLUSIVE"
    else:
        c3_verdict = "FAIL"
    lines.append(f"\n  PRE-SCREEN VERDICT: {c3_verdict}")
    if c3_verdict == "INCONCLUSIVE":
        lines.append(f"  Gates passed on pass 1, but the two passes disagree by "
                     f"{eval_res['drift']:.0%} — larger than the differences between "
                     f"candidates this screen is meant to detect. Re-run before relying "
                     f"on it; report the range, not a point value.")
    return "\n".join(lines)


def selftest():
    print("Running demand_screen selftest...")
    # Synthetic dataset 1: Viral, low proof burden (pepper grinder style)
    viral_items = [
        {"title": "One handed electric pepper grinder in action", "duration": 45, "view_count": 15000},
        {"title": "Best kitchen gadget ever #shorts", "duration": 30, "view_count": 80000},
        {"title": "Satisfying pepper grind compilation", "duration": 55, "view_count": 35000},
        {"title": "Is this pepper grinder worth it? Review", "duration": 120, "view_count": 12000},
        {"title": "Kitchen transformation gadget", "duration": 65, "view_count": 22000},
    ]
    r_viral = analyze_dataset(viral_items)
    assert r_viral["skeptic_ratio"] == 0.20
    assert r_viral["short_form_share"] == 0.60
    assert r_viral["criterion_3_pass"] is True
    assert r_viral["demand_floor_pass"] is True

    # Synthetic dataset 2: High proof burden (shower filter style)
    skeptic_items = [
        {"title": "Does this water filter really work? Lab test!", "duration": 300, "view_count": 50000},
        {"title": "Chemical test: shower filter review", "duration": 420, "view_count": 30000},
        {"title": "Are shower filters a scam? Test results", "duration": 280, "view_count": 40000},
        {"title": "Don't buy before watching this review", "duration": 350, "view_count": 25000},
        {"title": "Quick filter install", "duration": 50, "view_count": 10000},
    ]
    r_skep = analyze_dataset(skeptic_items)
    assert r_skep["skeptic_ratio"] == 0.80
    assert r_skep["criterion_3_pass"] is False

    # Synthetic dataset 3: Low demand commodity (100 views)
    dead_items = [
        {"title": "Wooden drawer divider clean", "duration": 50, "view_count": 120},
        {"title": "Drawer layout 1", "duration": 40, "view_count": 80},
    ]
    r_dead = analyze_dataset(dead_items)
    assert r_dead["demand_floor_pass"] is False

    print("SELFTEST: PASS")
    return 0


def main():
    ap = argparse.ArgumentParser(description="PROTOCOL-01 multi-pass demand & demo-burden screen")
    ap.add_argument("term", nargs="?", help="Product keyword to query")
    ap.add_argument("--fixture", help="Replay a saved raw JSON file")
    ap.add_argument("--selftest", action="store_true", help="Run offline unit tests")
    a = ap.parse_args()

    if a.selftest:
        return selftest()

    if a.fixture:
        with open(a.fixture, encoding="utf-8") as f:
            data = json.load(f)
        for cand, v in data.items():
            titles = v.get("titles") or []
            durations = v.get("durations") or []
            entries = [{"title": t, "duration": d if i < len(durations) else None, "view_count": None}
                       for i, (t, d) in enumerate(zip(titles, durations))]
            res = evaluate_candidate(cand, entries)
            print(format_report(res))
        return 0

    if not a.term:
        ap.error("A search term is required (or use --fixture / --selftest)")

    print(f"Executing YouTube demand screen for: \"{a.term}\"...")
    entries_pass1 = fetch_youtube_results(a.term, max_results=25)
    entries_pass2 = fetch_youtube_results(f"{a.term} demo", max_results=25)

    res = evaluate_candidate(a.term, entries_pass1, entries_pass2)
    print(format_report(res))
    return 0


if __name__ == "__main__":
    sys.exit(main())
