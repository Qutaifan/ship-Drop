"""Google Flow / Veo 3.1 Credit Guard and Generation Cost Estimator."""
from __future__ import annotations

import argparse
import json
import sys

MODEL_RATES = {
    "lite": {"credits": 10, "cost_usd": 0.20, "label": "Veo 3.1 Lite (Rapid Iteration)"},
    "fast": {"credits": 20, "cost_usd": 0.40, "label": "Veo 3.1 Fast (Pacing & Split Testing)"},
    "quality": {"credits": 100, "cost_usd": 2.00, "label": "Veo 3.1 Quality (Winner-Phase Re-shoot)"},
}

MONTHLY_PRO_CREDITS = 1000


def evaluate_veo_budget(model: str, clips: int, remaining_credits: int = 1000) -> dict:
    rate = MODEL_RATES.get(model.lower(), MODEL_RATES["quality"])
    total_credits = rate["credits"] * clips
    total_cost_usd = rate["cost_usd"] * clips
    can_afford = remaining_credits >= total_credits

    return {
        "model": rate["label"],
        "clips_requested": clips,
        "credits_per_clip": rate["credits"],
        "total_credits_required": total_credits,
        "estimated_total_cost_usd": round(total_cost_usd, 2),
        "account_credits_remaining": remaining_credits,
        "credits_after_run": remaining_credits - total_credits if can_afford else remaining_credits,
        "approved": can_afford,
        "max_clips_possible": remaining_credits // rate["credits"],
    }


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Google Flow / Veo 3.1 Credit Guard")
    parser.add_argument("--model", choices=["lite", "fast", "quality"], default="quality", help="Veo model tier")
    parser.add_argument("--clips", type=int, default=1, help="Number of 8s video clips to generate")
    parser.add_argument("--remaining", type=int, default=1000, help="Current remaining credits in account")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    args = parser.parse_args()

    res = evaluate_veo_budget(model=args.model, clips=args.clips, remaining_credits=args.remaining)

    if args.json:
        print(json.dumps(res, indent=2))
        return

    print("\n" + "═" * 70)
    print("  🎬 GOOGLE FLOW / VEO 3.1 GENERATION CREDIT GUARD")
    print("═" * 70)
    print(f"  Model Selected          : {res['model']}")
    print(f"  Clips Requested         : {res['clips_requested']} × 8-second 9:16 vertical")
    print(f"  Credits Required        : {res['total_credits_required']} credits (~${res['estimated_total_cost_usd']:.2f} USD)")
    print(f"  Account Balance         : {res['account_credits_remaining']} credits remaining")
    print(f"  Status                  : {'✅ APPROVED (Budget Safe)' if res['approved'] else '❌ REJECTED (Insufficient Credits)'}")
    if not res["approved"]:
        print(f"  Maximum Possible Clips  : {res['max_clips_possible']} clips with current balance")
    print("═" * 70 + "\n")


if __name__ == "__main__":
    main()
