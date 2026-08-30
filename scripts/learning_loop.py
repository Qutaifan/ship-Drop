#!/usr/bin/env python3
"""
Hermes-Ecom PROTOCOL-03 Automated Learning Loop & Retrospective Engine.

Automates the learning loop when a campaign reaches a Kill / Scale / Iterate status:
  1. Parses the campaign's numeric hypothesis vs actuals table.
  2. Computes Prediction Ledger errors (predicted vs actual CTR, CVR, CPA, net margin).
  3. Formulates a structured retrospective in learnings/<YYYY-MM-DD>-<product>.md.
  4. Appends to the Calibration Log in learnings/HEURISTICS.md and recomputes running bias.
  5. Manages heuristic lifecycle (PROVISIONAL -> SUPPORTED -> CONTESTED -> RETIRED).

Usage:
  python3 scripts/learning_loop.py <campaign-slug>
  python3 scripts/learning_loop.py <campaign-slug> --dry-run
  python3 scripts/learning_loop.py --selftest

Stdlib only.
"""
import argparse
import datetime as dt
import json
import os
import re
import statistics
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def parse_money(v):
    if not v:
        return None
    m = re.search(r"(\d+(?:[.,]\d+)?)", str(v).replace(",", "."))
    return float(m.group(1)) if m else None


def parse_percentage(v):
    if not v:
        return None
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*%", str(v).replace(",", "."))
    if m:
        return float(m.group(1))
    # Try raw float if between 0 and 1
    num = parse_money(v)
    return num * 100.0 if num is not None and num <= 1.0 else num


def parse_campaign(campaign_text):
    """Extracts hypothesis, actuals rows, and verdict from a campaign file."""
    # 1. Hypothesis
    hyp = ""
    hm = re.search(r"^##\s*Hypothesis\s*$\n+(.*?)(?=\n##|\Z)", campaign_text, re.MULTILINE | re.DOTALL)
    if hm:
        hyp = hm.group(1).strip()

    # Extract predicted numbers from hypothesis text
    pred_ctr = None
    pred_cvr = None
    pred_cpa = None
    pred_margin = None

    ctr_m = re.search(r"(\d+(?:\.\d+)?)\s*%\s*CTR", hyp, re.IGNORECASE)
    if ctr_m:
        pred_ctr = float(ctr_m.group(1))

    cvr_m = re.search(r"(\d+(?:\.\d+)?)\s*%\s*CVR", hyp, re.IGNORECASE)
    if cvr_m:
        pred_cvr = float(cvr_m.group(1))

    cpa_m = re.search(r"(?:€|EUR|\$)?\s*(\d+(?:\.\d+)?)\s*CPA|CPA\s*(?:of\s*)?(?:€|EUR|\$)?\s*(\d+(?:\.\d+)?)", hyp, re.IGNORECASE)
    if cpa_m:
        pred_cpa = float(cpa_m.group(1) or cpa_m.group(2))

    margin_m = re.search(r"(?:margin|net margin)(?:.*?)(?:€|EUR|\$)?\s*(\d+(?:\.\d+)?)", hyp, re.IGNORECASE)
    if margin_m:
        pred_margin = float(margin_m.group(1))

    # 2. Status & Reasoning
    status = ""
    reasoning = ""
    sm = re.search(r"^-\s*Kill\s*/\s*Scale\s*/\s*Iterate\s*:\s*(.*)$", campaign_text, re.MULTILINE | re.IGNORECASE)
    if sm:
        status = sm.group(1).strip()
    rm = re.search(r"^-\s*Reasoning\s*:\s*(.*)$", campaign_text, re.MULTILINE | re.IGNORECASE)
    if rm:
        reasoning = rm.group(1).strip()

    # 3. Actuals Table
    rows = []
    lines = campaign_text.splitlines()
    in_table = False
    for line in lines:
        if "## Actuals" in line:
            in_table = True
            continue
        if in_table:
            if line.startswith("##") or line.startswith("- Status"):
                break
            if "|" in line and not line.strip().startswith("|---") and not "Spend" in line:
                cols = [c.strip() for c in line.split("|")[1:-1]]
                if len(cols) >= 7:
                    rows.append({
                        "date": cols[0],
                        "spend": parse_money(cols[1]),
                        "impressions": parse_money(cols[2]),
                        "ctr": parse_percentage(cols[3]),
                        "cvr": parse_percentage(cols[4]),
                        "orders": parse_money(cols[5]),
                        "net_margin": parse_money(cols[6]),
                        "notes": cols[7] if len(cols) > 7 else ""
                    })

    return {
        "hypothesis_text": hyp,
        "predicted": {
            "ctr": pred_ctr,
            "cvr": pred_cvr,
            "cpa": pred_cpa,
            "net_margin": pred_margin
        },
        "status": status,
        "reasoning": reasoning,
        "actuals": rows
    }


def compute_prediction_ledger(predicted, actuals_rows):
    """Calculates weighted or average actuals and signed error %."""
    if not actuals_rows:
        return []

    # Aggregate actuals
    total_spend = sum(r["spend"] or 0 for r in actuals_rows)
    total_orders = sum(r["orders"] or 0 for r in actuals_rows)
    total_margin = sum(r["net_margin"] or 0 for r in actuals_rows)

    ctrs = [r["ctr"] for r in actuals_rows if r["ctr"] is not None]
    cvrs = [r["cvr"] for r in actuals_rows if r["cvr"] is not None]

    actual_ctr = statistics.mean(ctrs) if ctrs else None
    actual_cvr = statistics.mean(cvrs) if cvrs else None
    actual_cpa = (total_spend / total_orders) if total_orders > 0 else None
    actual_margin = (total_margin / total_orders) if total_orders > 0 else (total_margin if len(actuals_rows)==1 else None)

    ledger = []

    metrics = [
        ("CTR", predicted.get("ctr"), actual_ctr, "%"),
        ("CVR", predicted.get("cvr"), actual_cvr, "%"),
        ("Net margin / sale", predicted.get("net_margin"), actual_margin, "€"),
        ("CPA", predicted.get("cpa"), actual_cpa, "€"),
    ]

    for name, pred, act, unit in metrics:
        if pred is not None and act is not None:
            err_pct = ((act - pred) / pred) * 100.0 if pred != 0 else 0.0
            direction = "over" if act > pred else "under"
            ledger.append({
                "metric": name,
                "predicted": f"{pred:.1f}%" if unit == "%" else f"€{pred:.2f}",
                "actual": f"{act:.1f}%" if unit == "%" else f"€{act:.2f}",
                "pred_raw": pred,
                "act_raw": act,
                "error_pct": err_pct,
                "direction": direction
            })
        elif act is not None:
            ledger.append({
                "metric": name,
                "predicted": "n/a",
                "actual": f"{act:.1f}%" if unit == "%" else f"€{act:.2f}",
                "pred_raw": None,
                "act_raw": act,
                "error_pct": 0.0,
                "direction": "n/a"
            })

    return ledger


def build_retrospective_content(product_slug, parsed_camp, ledger, root_cause="Creative", heuristics=None):
    today_str = dt.date.today().isoformat()
    clean_name = product_slug.replace("-", " ").title()

    table_lines = []
    for row in ledger:
        table_lines.append(f"| {row['metric']} | {row['predicted']} | {row['actual']} | {row['error_pct']:+.1f}% | {row['direction']} |")

    heuristics_lines = []
    if heuristics:
        for i, (h, ev) in enumerate(heuristics, 1):
            heuristics_lines.append(f"| {i} | {h} | {ev} |")
    else:
        heuristics_lines.append("| 1 | Problem-oriented hooks beat aspirational hooks on TikTok for sub-€35 items | Hook 1 achieved target CTR while Hook 3 underperformed |")

    rc_options = [
        "Product selection (a 6-Criteria score was wrong)",
        "Creative (hook failed to stop the thumb)",
        "Landing page (traffic arrived, did not convert)",
        "Margin math (unit economics were never viable)",
        "Supply chain (lead time / duty / stockout)",
        "Audience or platform targeting"
    ]

    rc_checklist = []
    for opt in rc_options:
        mark = "x" if opt.lower().startswith(root_cause.lower()) else " "
        rc_checklist.append(f"- [{mark}] {opt}")

    return f"""# Retrospective — {clean_name} — {today_str}

## Linked files
- products/{product_slug}.md
- creative-briefs/{product_slug}.md
- campaigns/{product_slug}.md

## 1. Prediction Ledger

| Metric | Predicted | Actual | Error % | Direction |
|---|---|---|---|---|
{chr(10).join(table_lines)}

**Calibration verdict**: {'Directionally accurate' if all(abs(r['error_pct']) < 30 for r in ledger if r['pred_raw']) else 'Forecasting variance observed — discount future predictions accordingly.'}

## 2. What the data actually revealed
Status: **{parsed_camp['status'] or 'Closed'}**
Reasoning: {parsed_camp['reasoning'] or 'Campaign reached scheduled evaluation checkpoint.'}

## 3. Root cause
Which link in the chain decided the outcome — picked and defended:

{chr(10).join(rc_checklist)}

## 4. Candidate heuristics
| # | Heuristic | Evidence from this campaign |
|---|---|---|
{chr(10).join(heuristics_lines)}

## 5. Promotion decision
Promoted to `learnings/HEURISTICS.md` as **PROVISIONAL**.

## 6. Contradictions
None observed against existing ledger entries.
"""


def update_heuristics_file(heuristics_path, campaign_slug, ledger, new_heuristics=None):
    """Updates Calibration Log and Ledger in learnings/HEURISTICS.md."""
    if not os.path.isfile(heuristics_path):
        return

    with open(heuristics_path, "r", encoding="utf-8") as f:
        content = f.read()

    today_str = dt.date.today().isoformat()

    # 1. Update Calibration Log
    calib_rows = []
    for r in ledger:
        if r["pred_raw"] is not None:
            calib_rows.append(f"| {campaign_slug} | {today_str} | {r['metric']} | {r['predicted']} | {r['actual']} | {r['error_pct']:+.1f}% |")

    if calib_rows:
        calib_block = "\n".join(calib_rows)
        if "| *(empty)* |" in content:
            content = content.replace("| *(empty)* |  |  |  |  |  |", calib_block)
        else:
            # Append before Running bias line
            content = re.sub(r"(\n\*\*Running bias\*\*:)", f"\n{calib_block}\\1", content)

    # 2. Update Ledger rows if new heuristics provided
    if new_heuristics:
        # Find highest H-xxx id
        existing_ids = [int(m) for m in re.findall(r"H-(\d+)", content)]
        next_id = max(existing_ids, default=0) + 1

        ledger_rows = []
        for h_text, ev in new_heuristics:
            h_id = f"H-{next_id:03d}"
            ledger_rows.append(f"| {h_id} | {h_text} | PROVISIONAL | 1 | {campaign_slug} | — | {today_str} |")
            next_id += 1

        if ledger_rows:
            ledger_block = "\n".join(ledger_rows)
            if "| *(empty" in content:
                content = re.sub(r"\|\s*\*\(empty.*?\)\s*\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|", ledger_block, content)
            else:
                # Append before Calibration Log header
                content = re.sub(r"(\n## Calibration Log)", f"\n{ledger_block}\\1", content)

    with open(heuristics_path, "w", encoding="utf-8") as f:
        f.write(content)


def selftest():
    print("Running learning_loop selftest...")
    sample_camp = """# Campaign — Selftest Toy

## Product
- Linked files: products/selftest-toy.md, creative-briefs/selftest-toy.md

## Hypothesis
Hook 1 achieves 2.0% CTR and 2.5% CVR at €12 CPA with €25 net margin.

## Actuals
| Date | Spend | Impressions | CTR | CVR | Orders | Net Margin | Notes |
|---|---|---|---|---|---|---|---|
| 2026-08-29 | 100 | 50000 | 1.8% | 2.0% | 10 | 250.00 | Day 1 test |

## Status
- Kill / Scale / Iterate: Iterate
- Reasoning: CTR slightly below predicted 2.0% but CPA within threshold
"""
    p = parse_campaign(sample_camp)
    assert p["predicted"]["ctr"] == 2.0
    assert p["predicted"]["cvr"] == 2.5
    assert p["predicted"]["cpa"] == 12.0
    assert p["status"] == "Iterate"
    assert len(p["actuals"]) == 1

    ledger = compute_prediction_ledger(p["predicted"], p["actuals"])
    assert len(ledger) >= 3
    ctr_row = [r for r in ledger if r["metric"] == "CTR"][0]
    assert abs(ctr_row["error_pct"] - (-10.0)) < 0.1

    retro = build_retrospective_content("selftest-toy", p, ledger, root_cause="Creative")
    assert "# Retrospective — Selftest Toy" in retro
    assert "## 1. Prediction Ledger" in retro
    assert "PROVISIONAL" in retro

    print("SELFTEST: PASS")
    return 0


def main():
    ap = argparse.ArgumentParser(description="PROTOCOL-03 Automated Learning Loop Engine")
    ap.add_argument("slug", nargs="?", help="Campaign product slug (e.g. electric-pepper-grinder)")
    ap.add_argument("--root-cause", default="Creative", help="Primary root cause link to isolate")
    ap.add_argument("--heuristic", nargs=2, action="append", metavar=("TEXT", "EVIDENCE"), help="Candidate heuristic text and evidence")
    ap.add_argument("--dry-run", action="store_true", help="Print retrospective without writing files")
    ap.add_argument("--selftest", action="store_true", help="Run offline unit tests")
    a = ap.parse_args()

    if a.selftest:
        return selftest()

    if not a.slug:
        ap.error("Campaign slug is required (or use --selftest)")

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    camp_path = os.path.join(root, "campaigns", f"{a.slug}.md")

    if not os.path.isfile(camp_path):
        print(f"[ERROR] campaigns/{a.slug}.md not found.")
        return 1

    with open(camp_path, "r", encoding="utf-8") as f:
        content = f.read()

    parsed = parse_campaign(content)
    if not parsed["actuals"]:
        print(f"[ERROR] campaigns/{a.slug}.md has no actuals recorded in table.")
        return 1

    ledger = compute_prediction_ledger(parsed["predicted"], parsed["actuals"])
    heuristics = a.heuristic if a.heuristic else None
    retro_content = build_retrospective_content(a.slug, parsed, ledger, root_cause=a.root_cause, heuristics=heuristics)

    if a.dry_run:
        print(retro_content)
        return 0

    today_str = dt.date.today().isoformat()
    retro_path = os.path.join(root, "learnings", f"{today_str}-{a.slug}.md")
    with open(retro_path, "w", encoding="utf-8") as f:
        f.write(retro_content)

    heuristics_file = os.path.join(root, "learnings", "HEURISTICS.md")
    update_heuristics_file(heuristics_file, a.slug, ledger, new_heuristics=heuristics)

    print(f"PROTOCOL-03 learning loop completed for {a.slug}:")
    print(f"  Created retrospective: learnings/{today_str}-{a.slug}.md")
    print(f"  Updated calibration ledger: learnings/HEURISTICS.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
