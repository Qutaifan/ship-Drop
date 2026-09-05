#!/usr/bin/env python3
"""
Flow credit guard for the veo-flow-ads skill.

Reads a local credit ledger at infra/flow_credits.json (manually updated
after each Flow session, since Flow has no public credit-balance API).
Asserts the winner-phase budget: remaining credits >= 200, Quality
generations this calendar month <= 10. Exits 1 on violation.

Usage:
  python scripts/flow_credit_check.py            # pre-flight guard
  python scripts/flow_credit_check.py --after    # post-session log

Stdlib only.
"""
import argparse
import datetime as dt
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
LEDGER = REPO / "infra" / "flow_credits.json"
QUALITY_CEILING_PER_MONTH = 10
REMAINING_FLOOR = 200


def load_ledger():
    if not LEDGER.exists():
        LEDGER.parent.mkdir(parents=True, exist_ok=True)
        LEDGER.write_text(json.dumps({
            "plan": "Google AI Pro",
            "monthly_allowance": 1000,
            "refresh_date": (dt.date.today() + dt.timedelta(days=30)).isoformat(),
            "quality_used_this_month": 0,
            "fast_used_this_month": 0,
            "lite_used_this_month": 0,
            "history": [],
        }, indent=2))
    return json.loads(LEDGER.read_text())


def remaining(ledger):
    used = (ledger.get("quality_used_this_month", 0) * 100
            + ledger.get("fast_used_this_month", 0) * 20
            + ledger.get("lite_used_this_month", 0) * 10)
    return ledger["monthly_allowance"] - used


def guard(ledger):
    rem = remaining(ledger)
    q = ledger.get("quality_used_this_month", 0)
    failures = []
    if rem < REMAINING_FLOOR:
        failures.append(f"remaining {rem} < floor {REMAINING_FLOOR}")
    if q > QUALITY_CEILING_PER_MONTH:
        failures.append(f"quality used {q} > ceiling {QUALITY_CEILING_PER_MONTH}")
    if failures:
        print("FAIL:", "; ".join(failures), file=sys.stderr)
        return 1
    print(f"OK  remaining={rem}  quality_used={q}/{QUALITY_CEILING_PER_MONTH}  "
          f"refresh={ledger.get('refresh_date')}")
    return 0


def log_session(model, generations, ledger):
    if model not in ("quality", "fast", "lite"):
        print(f"unknown model {model!r}", file=sys.stderr)
        return 1
    key = f"{model}_used_this_month"
    ledger[key] = ledger.get(key, 0) + generations
    ledger.setdefault("history", []).append({
        "ts": dt.datetime.now().isoformat(timespec="seconds"),
        "model": model,
        "generations": generations,
        "credits_spent": generations * {"quality": 100, "fast": 20, "lite": 10}[model],
    })
    LEDGER.write_text(json.dumps(ledger, indent=2))
    rem = remaining(ledger)
    print(f"logged: {model} x{generations} ({generations * {'quality':100,'fast':20,'lite':10}[model]} cr). "
          f"remaining={rem}")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--after", nargs=3, metavar=("MODEL", "COUNT", "NOTE"),
                    help="log a session: model quality|fast|lite, count, free note")
    args = ap.parse_args()
    ledger = load_ledger()
    if args.after:
        model, count, note = args.after
        rc = log_session(model, int(count), ledger)
    else:
        rc = guard(ledger)
    sys.exit(rc)


if __name__ == "__main__":
    main()