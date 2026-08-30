#!/usr/bin/env python3
"""
Verify a demo-burden sweep's stated metrics against its own raw data.

Written after the 2026-08-30 sweep reported skeptic ratios that did not match the
titles it had itself stored — 9 of 10 wrong, every error in the optimistic
direction. An agent's arithmetic on its own data is not self-evidently correct, so
it is now checked.

Expects a JSON object: {candidate: {titles[], durations[], median_duration,
short_form_share, skeptic_ratio, n_videos}}.

Run:  python3 scripts/verify_sweep.py reports/yt_results_raw.json
Exit 0 = every stated figure reproduces, 1 = at least one does not.
"""
import io
import json
import statistics
import sys

KEYWORDS = ["are ", "does ", "really", "worth", "test", "review"]
TOL = 0.021          # 2 percentage points, i.e. half a video out of 25
DUR_TOL = 2          # seconds


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "reports/yt_results_raw.json"
    data = json.load(io.open(path, encoding="utf-8"))
    if not isinstance(data, dict):
        print("raw file must be an object keyed by candidate")
        return 1

    errors = []
    print(f"Sweep verification — {path}\n")
    print(f"{'candidate':30} {'skeptic':>17} {'short-form':>17} {'median dur':>15}")
    print(f"{'':30} {'said':>8}{'real':>9} {'said':>8}{'real':>9} {'said':>7}{'real':>8}")

    for name, v in data.items():
        titles = v.get("titles") or []
        durs = [d for d in (v.get("durations") or []) if d]
        if not titles:
            errors.append(f"{name}: no titles stored — the figures cannot be checked "
                          f"at all, which is itself a failure")
            continue

        real_sk = sum(1 for t in titles
                      if any(w in t.lower() for w in KEYWORDS)) / len(titles)
        real_sf = sum(1 for d in (v.get("durations") or []) if 0 < d <= 60) / len(titles)
        real_md = int(statistics.median(durs)) if durs else 0

        said_sk = v.get("skeptic_ratio")
        said_sf = v.get("short_form_share")
        said_md = v.get("median_duration")
        n = v.get("n_videos")

        flag = ""
        if said_sk is not None and abs(said_sk - real_sk) > TOL:
            direction = "optimistic" if said_sk < real_sk else "pessimistic"
            errors.append(f"{name}: skeptic ratio stated {said_sk:.0%}, its own titles "
                          f"give {real_sk:.0%} ({direction})")
            flag = "  <-"
        if said_sf is not None and abs(said_sf - real_sf) > TOL:
            errors.append(f"{name}: short-form share stated {said_sf:.0%}, data gives "
                          f"{real_sf:.0%}")
            flag = "  <-"
        if said_md is not None and durs and abs(said_md - real_md) > DUR_TOL:
            errors.append(f"{name}: median duration stated {said_md}s, data gives {real_md}s")
            flag = "  <-"
        if n is not None and n != len(titles):
            errors.append(f"{name}: n_videos stated {n}, {len(titles)} titles stored")

        print(f"{name[:30]:30} {said_sk or 0:>8.0%}{real_sk:>9.0%} "
              f"{said_sf or 0:>8.0%}{real_sf:>9.0%} {said_md or 0:>7}{real_md:>8}{flag}")

    print()
    for e in errors:
        print(f"  [ERROR] {e}")
    optimistic = sum(1 for e in errors if "optimistic" in e)
    if optimistic > 1:
        print(f"\n  [ERROR] {optimistic} errors all run in the optimistic direction. "
              f"Random arithmetic slips do not share a sign — treat the whole sweep as "
              f"unreliable, not as a set of individual typos.")
    print(f"\n{len(errors)} discrepanc{'y' if len(errors)==1 else 'ies'}")
    print("RESULT: " + ("FAIL" if errors else "PASS"))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
