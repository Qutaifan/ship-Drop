#!/usr/bin/env python3
"""
Hermes-Ecom workspace validator.

Checks that the PROTOCOL-01 -> 02 -> 03 pipeline in this workspace is internally
consistent: templates intact, margin arithmetic correct, gates respected, and no
orphaned or unclosed artifacts.

Stdlib only. Run:  python3 scripts/validate_workspace.py [workspace_root]
Exit code 0 = clean, 1 = at least one ERROR.
"""
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

DIRS = ["products", "creative-briefs", "suppliers", "campaigns", "reports", "learnings"]
PLACEHOLDERS = {"", "__", "-", "tbd", "pass / fail", "kill / scale / iterate",
                "n/a", "na", "empty"}

errors, warnings, notes = [], [], []


def err(m):
    errors.append(m)


def warn(m):
    warnings.append(m)


def note(m):
    notes.append(m)


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def field(text, label):
    """Value of a '- Label: value' line, '' if absent or placeholder."""
    # tolerate a qualifier before the colon, e.g. "- Competitors running ads (need 5-10): 7"
    m = re.search(rf"^[-*]\s*{re.escape(label)}[^:\n]*:\s*(.*)$", text,
                  re.MULTILINE | re.IGNORECASE)
    if not m:
        return ""
    v = m.group(1).strip()
    if v.lower() in PLACEHOLDERS or v.startswith("("):
        return ""
    return v


def money(v):
    """First numeric value in a string like '€24.90' or '24,90 EUR'. None if absent."""
    if not v:
        return None
    m = re.search(r"(\d+(?:[.,]\d+)?)", v.replace(",", "."))
    return float(m.group(1)) if m else None


def stems(d):
    if not os.path.isdir(d):
        return set()
    return {f[:-3] for f in os.listdir(d)
            if f.endswith(".md") and not f.startswith("_")
            and f.upper() != "HEURISTICS.MD"}


def check_structure(root):
    for d in DIRS:
        p = os.path.join(root, d)
        if not os.path.isdir(p):
            err(f"missing directory: {d}/")
            continue
        if not os.path.isfile(os.path.join(p, "_TEMPLATE.md")):
            err(f"{d}/ has no _TEMPLATE.md")
    for f in ["AGENTS.md", "README.md"]:
        if not os.path.isfile(os.path.join(root, f)):
            err(f"missing {f}")
    h = os.path.join(root, "learnings", "HEURISTICS.md")
    if not os.path.isfile(h):
        err("learnings/HEURISTICS.md missing — PROTOCOL-03 has nowhere to write")


REQUIRED_PRODUCT_SECTIONS = ["## Product", "## 6-Criteria Screen", "## Competitor Check",
                             "## True Margin Matrix", "## Regulatory Check", "## Verdict"]


def check_products(root):
    """Returns {stem: verdict} for every product file."""
    verdicts = {}
    d = os.path.join(root, "products")
    for s in sorted(stems(d)):
        t = read(os.path.join(d, f"{s}.md"))
        for sec in REQUIRED_PRODUCT_SECTIONS:
            if sec not in t:
                err(f"products/{s}.md missing section '{sec}'")

        vm = re.search(r"^##\s*Verdict\s*$\n+(.*)$", t, re.MULTILINE)
        verdict = ""
        if vm:
            line = vm.group(1).upper()
            if "PASS" in line and "FAIL" not in line:
                verdict = "PASS"
            elif "FAIL" in line and "PASS" not in line:
                verdict = "FAIL"
        verdicts[s] = verdict
        if not verdict:
            warn(f"products/{s}.md has no resolved verdict (still PASS / FAIL)")

        retail = money(field(t, "Retail price target"))
        cost = money(field(t, "Product cost"))
        ship = money(field(t, "Shipping cost"))
        if None in (retail, cost, ship):
            note(f"products/{s}.md — margin math skipped, unit economics incomplete")
            continue

        # VAT is remitted to the state, so margin runs on the ex-VAT amount.
        # Omitting it overstates EU margin by roughly the VAT rate.
        vat = money(field(t, "VAT rate"))
        if vat is None:
            err(f"products/{s}.md has no VAT rate — margin cannot be computed for an "
                f"EU sale, and omitting it overstates net margin by ~{0.19/1.19:.0%}")
            continue
        if vat > 1:                      # tolerate "19" as well as "0.19"
            vat = vat / 100.0
        duty = money(field(t, "Import duty per unit")) or 0.0

        cogs = cost + ship + duty
        fee = round(retail * 0.03, 2)
        net = round(retail / (1 + vat) - cogs - fee, 2)

        stated = money(field(t, "Net Margin"))
        if stated is not None and abs(stated - net) > 0.02:
            err(f"products/{s}.md True Margin Matrix wrong: states {stated:.2f}, "
                f"recomputes to {net:.2f} (ex-VAT revenue {retail/(1+vat):.2f} "
                f"- cogs {cogs:.2f} - 3% fee {fee:.2f})")

        gate_3x = net >= 3 * cogs
        gate_15 = net > 15
        should = "PASS" if (gate_3x and gate_15) else "FAIL"
        if verdict and verdict != should:
            reasons = []
            if not gate_3x:
                reasons.append(f"net {net:.2f} < 3x COGS ({3*cogs:.2f})")
            if not gate_15:
                reasons.append(f"net {net:.2f} not > 15")
            err(f"products/{s}.md verdict {verdict} contradicts margin rules "
                f"(should be {should}: {'; '.join(reasons) or 'both gates met'})")

        if retail < 20:
            err(f"products/{s}.md retail {retail:.2f} is under the €20 floor "
                f"(AGENTS.md §4A.4 — cannot sustain paid ads)")

        comps = money(field(t, "Competitors running ads (need 5–10)")) \
            or money(field(t, "Competitors running ads"))
        aged = money(field(t, "Ads active 30+ days (need ≥3, proves sustained profitability)")) \
            or money(field(t, "Ads active 30+ days"))
        if verdict == "PASS":
            if comps is None or comps < 5:
                err(f"products/{s}.md PASSed with {comps if comps is not None else 'no'} "
                    f"competitors — PROTOCOL-01 requires 5–10")
            if aged is None or aged < 3:
                err(f"products/{s}.md PASSed with {aged if aged is not None else 'no'} "
                    f"ads aged 30+ days — PROTOCOL-01 requires ≥3")
    return verdicts


def check_pipeline(root, verdicts):
    briefs = stems(os.path.join(root, "creative-briefs"))
    camps = stems(os.path.join(root, "campaigns"))
    prods = set(verdicts)

    for b in sorted(briefs):
        if b not in prods:
            err(f"creative-briefs/{b}.md has no products/{b}.md (orphan brief)")
        elif verdicts[b] != "PASS":
            err(f"creative-briefs/{b}.md exists but product verdict is "
                f"'{verdicts[b] or 'unresolved'}' — PROTOCOL-02 requires PASS")

    for c in sorted(camps):
        if c not in prods:
            err(f"campaigns/{c}.md has no products/{c}.md")
        if c not in briefs:
            err(f"campaigns/{c}.md has no creative-briefs/{c}.md — launched without a brief")

    for p in sorted(prods):
        if verdicts[p] == "PASS" and p not in briefs:
            warn(f"products/{p}.md PASSed but has no creative brief — pipeline stalled")
    return camps


def check_campaigns_and_learning(root, camps):
    cd = os.path.join(root, "campaigns")
    ld = os.path.join(root, "learnings")
    retros = " ".join(os.listdir(ld)) if os.path.isdir(ld) else ""

    for c in sorted(camps):
        t = read(os.path.join(cd, f"{c}.md"))
        hyp = ""
        hm = re.search(r"^##\s*Hypothesis\s*$\n+(.*?)(?=\n##|\Z)", t,
                       re.MULTILINE | re.DOTALL)
        if hm:
            hyp = "\n".join(l for l in hm.group(1).splitlines()
                            if not l.strip().startswith("("))
        if not hyp.strip():
            err(f"campaigns/{c}.md has no hypothesis")
        elif not re.search(r"\d", hyp):
            err(f"campaigns/{c}.md hypothesis carries no numeric prediction "
                f"(AGENTS.md §3 DECIDE) — it cannot be scored by PROTOCOL-03")

        status = field(t, "Kill / Scale / Iterate")
        if status:
            if c not in retros:
                err(f"campaigns/{c}.md is closed ('{status}') but has no "
                    f"learnings/*-{c}.md retrospective — PROTOCOL-03 not run")
            if not field(t, "Reasoning"):
                warn(f"campaigns/{c}.md closed with no reasoning recorded")


VALID_STATUS = {"PROVISIONAL", "SUPPORTED", "CONTESTED", "RETIRED"}


def check_heuristics(root):
    p = os.path.join(root, "learnings", "HEURISTICS.md")
    if not os.path.isfile(p):
        return
    rows = re.findall(r"^\|\s*(H-\d+)\s*\|([^|]*)\|([^|]*)\|([^|]*)\|",
                      read(p), re.MULTILINE)
    if not rows:
        note("learnings/HEURISTICS.md has no heuristics yet (expected before the "
             "first closed campaign)")
        return
    for hid, text, status, n in rows:
        status = status.strip().upper()
        if status not in VALID_STATUS:
            err(f"HEURISTICS.md {hid}: invalid status '{status}' "
                f"(must be one of {', '.join(sorted(VALID_STATUS))})")
        cnt = money(n)
        if status == "SUPPORTED" and (cnt is None or cnt < 3):
            err(f"HEURISTICS.md {hid}: SUPPORTED requires n>=3, has n={n.strip() or '0'}")
        if not text.strip():
            err(f"HEURISTICS.md {hid}: empty heuristic text")


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))
    print(f"Hermes-Ecom workspace validation — {root}\n")

    check_structure(root)
    verdicts = check_products(root)
    camps = check_pipeline(root, verdicts)
    check_campaigns_and_learning(root, camps)
    check_heuristics(root)

    for label, items in (("ERROR", errors), ("WARN", warnings), ("NOTE", notes)):
        for m in items:
            print(f"  [{label}] {m}")
    if not (errors or warnings or notes):
        print("  (nothing to report)")

    print(f"\n{len(errors)} error(s), {len(warnings)} warning(s), {len(notes)} note(s)")
    print("RESULT: " + ("FAIL" if errors else "PASS"))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
