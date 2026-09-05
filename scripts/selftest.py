#!/usr/bin/env python3
"""
Hermes-Ecom self-test — proves the validators actually fail when they should.

Builds a synthetic-but-complete workspace in a temp dir, asserts both validators
pass on it, then applies one deliberate defect at a time and asserts the matching
validator catches it. A validator that reports "clean" is only trustworthy if it
is known to fail on bad input; that is what this file establishes.

Run:  python3 scripts/selftest.py
Exit 0 = every case behaved as expected.
"""
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = "selftest-cable-dock"
# retail 59.90 @19% VAT -> ex-VAT 50.34 | cogs 10.00 | fee 1.80 | net 38.54 ; 3x cogs 30.00
PRODUCT = """# Product Validation — Selftest Cable Dock

## Product
- Name: Selftest Cable Dock
- Source/supplier candidate(s): placeholder EU warehouse
- Retail price target: EUR 59.90
- VAT rate (destination market): 0.19
- Product cost: EUR 7.50
- Shipping cost: EUR 2.50
- Import duty per unit: 0

## 6-Criteria Screen
1. Wow Factor: yes
2. Problem Solving: cables fall behind the desk
3. Visual Appeal: silent 9:16 demo
4. Healthy Margins: EUR 38.54 net
5. Low Return Potential: no electronics
6. Low Local Retail Availability: yes

## Competitor Check
- Competitors running ads (need 5-10): 7
- Ads active 30+ days (need >=3): 4

## True Margin Matrix
- Net Margin: 38.54
- Must be >=3x COGS and >$15: PASS

## Regulatory Check
- De Minimis / sourcing region: EU warehouse
- EU AI Act disclosure needed: yes, on PDP
- FTC dynamic pricing rule-based: yes

## Verdict
PASS - proceed to PROTOCOL-02
"""
BRIEF = f"""# Creative Brief — Selftest Cable Dock

## Product
- Name: Selftest Cable Dock
- Linked validation file: products/{P}.md

## The "3+1" Brief

### Ad Hook 1 - Problem-Oriented
- Hook: cable slips behind the desk again
### Ad Hook 2 - Transformation
- Before/after: tangle to aligned
### Ad Hook 3 - Aspirational Lifestyle
- Environment: warm minimal desk

### Landing Page Framework
- Above-the-Fold hero statement: Your cables stop falling.
- Social proof section: 4.7 stars
- Checkout: one-click, no-account confirmed? Yes

## Compliance Notes
- AI imagery disclosure: "Product imagery assisted by generative AI"
"""
CAMPAIGN = f"""# Campaign — Selftest Cable Dock

## Product
- Linked files: products/{P}.md, creative-briefs/{P}.md

## Hypothesis
Hook 1 delivers 1.8% CTR and 2.2% CVR at EUR 14 CPA; predicted net margin EUR 38.54.

## Actuals
| Date | Spend | Impressions | CTR | CVR | Orders | Net Margin | Notes |
|---|---|---|---|---|---|---|---|
| 2026-08-27 | 90 | 63000 | 1.2% | 1.5% | 11 | 408.10 | Hook 1 only |

## Status
- Kill / Scale / Iterate: Iterate
- Reasoning: CTR below prediction, CPA held
"""
RETRO = f"""# Retrospective — {P} — 2026-08-28

## Linked files
- products/{P}.md
- campaigns/{P}.md

## 1. Prediction Ledger
| Metric | Predicted | Actual | Error % | Direction |
|---|---|---|---|---|
| CTR | 1.8% | 1.2% | -33% | over |

## 3. Root cause
- [x] Creative

## 4. Candidate heuristics
| # | Heuristic | Evidence |
|---|---|---|
| 1 | Problem hooks beat aspirational for desk items | Hook 1 1.2% vs Hook 3 0.3% |
"""


def w(root, rel, text):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with io.open(p, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def rw(root, rel, fn):
    """Read-modify-write. The read MUST complete before the file is opened for
    writing — opening "w" truncates, so a one-liner that nests the read inside
    the write call silently wipes the file and every mutation becomes a no-op."""
    p = os.path.join(root, rel)
    with io.open(p, encoding="utf-8") as f:
        before = f.read()
    after = fn(before)
    if after == before:
        raise AssertionError(f"mutation on {rel} changed nothing — the case would "
                             f"pass vacuously")
    with io.open(p, "w", encoding="utf-8", newline="") as f:
        f.write(after)


def build_baseline(dst):
    """Real workspace + a complete synthetic pipeline run."""
    shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns(
        ".git", "__pycache__", ".env", "eCommerce-Skills", ".agents"))
    w(dst, f"products/{P}.md", PRODUCT)
    w(dst, f"creative-briefs/{P}.md", BRIEF)
    w(dst, f"campaigns/{P}.md", CAMPAIGN)
    w(dst, f"learnings/2026-08-28-{P}.md", RETRO)
    def update_heuristics(s):
        target = "| *(empty — populated by the first PROTOCOL-03 retrospective; IDs run H-001, H-002, …)* | | | | | | |"
        replacement = f"| H-001 | Problem hooks beat aspirational for desk items | PROVISIONAL | 1 | {P} | — | 2026-08-28 |"
        if target in s:
            return s.replace(target, replacement)
        return re.sub(r"\|\s*H-001\s*\|[^\n]*", replacement, s, count=1)
    rw(dst, "learnings/HEURISTICS.md", update_heuristics)


def run(script, root):
    r = subprocess.run([sys.executable, os.path.join(root, "scripts", script), root],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, r.stdout


# (name, validator, expected substring, mutation)
CASES = [
    # --- pipeline: PROTOCOL-01 to 03 ---
    ("P1  margin arithmetic wrong", "validate_workspace.py", "True Margin Matrix wrong",
     lambda r: rw(r, f"products/{P}.md", lambda s: s.replace("Net Margin: 38.54", "Net Margin: 44.00"))),
    ("P2  PASS below 3x COGS", "validate_workspace.py", "contradicts margin rules",
     lambda r: rw(r, f"products/{P}.md", lambda s: s.replace("Product cost: EUR 7.50", "Product cost: EUR 14.00"))),
    ("P3  retail under EUR 20", "validate_workspace.py", "under the €20 floor",
     lambda r: rw(r, f"products/{P}.md", lambda s: s.replace("Retail price target: EUR 59.90", "Retail price target: EUR 18.00"))),
    ("P4  PASS with 3 competitors", "validate_workspace.py", "requires 5–10",
     lambda r: rw(r, f"products/{P}.md", lambda s: s.replace("(need 5-10): 7", "(need 5-10): 3"))),
    ("P5  PASS with 1 aged ad", "validate_workspace.py", "requires ≥3",
     lambda r: rw(r, f"products/{P}.md", lambda s: s.replace("(need >=3): 4", "(need >=3): 1"))),
    ("P6  orphan creative brief", "validate_workspace.py", "orphan brief",
     lambda r: shutil.copy(os.path.join(r, f"creative-briefs/{P}.md"),
                           os.path.join(r, "creative-briefs/ghost.md"))),
    ("P7  campaign without brief", "validate_workspace.py", "launched without a brief",
     lambda r: os.remove(os.path.join(r, f"creative-briefs/{P}.md"))),
    ("P8  hypothesis has no number", "validate_workspace.py", "no numeric prediction",
     lambda r: rw(r, f"campaigns/{P}.md", lambda s: re.sub(
         r"## Hypothesis\n.*?\n\n", "## Hypothesis\nHook one should do well.\n\n", s, flags=re.S))),
    ("P9  closed, no retrospective", "validate_workspace.py", "PROTOCOL-03 not run",
     lambda r: os.remove(os.path.join(r, f"learnings/2026-08-28-{P}.md"))),
    ("P11 VAT rate omitted", "validate_workspace.py", "no VAT rate",
     lambda r: rw(r, f"products/{P}.md", lambda s: s.replace("- VAT rate (destination market): 0.19\n", ""))),
    ("P10 SUPPORTED at n=1", "validate_workspace.py", "SUPPORTED requires n>=3",
     lambda r: rw(r, "learnings/HEURISTICS.md", lambda s: s.replace("| PROVISIONAL | 1 |", "| SUPPORTED | 1 |"))),

    # --- infrastructure ---
    ("I1  no Medusa worker process", "validate_infra.py", "MEDUSA_WORKER_MODE=worker",
     lambda r: rw(r, "infra/docker-compose.yml", lambda s: s.replace("MEDUSA_WORKER_MODE: worker", "MEDUSA_WORKER_MODE: server"))),
    ("I2  port on all interfaces", "validate_infra.py", "all interfaces",
     lambda r: rw(r, "infra/docker-compose.yml", lambda s: s.replace('"127.0.0.1:9000:9000"', '"9000:9000"'))),
    ("I3  undeclared env var", "validate_infra.py", "never declares it",
     lambda r: rw(r, "infra/docker-compose.yml", lambda s: s.replace("${JWT_SECRET}", "${TOTALLY_UNDECLARED}"))),
    ("I4  postgres healthcheck gone", "validate_infra.py", "no healthcheck",
     lambda r: rw(r, "infra/docker-compose.yml", lambda s: re.sub(
         r"    healthcheck:\n      test: \[\"CMD-SHELL\", \"pg_isready.*?\n(      \w.*\n)*", "", s))),
    ("I5  valkey volume gone", "validate_infra.py", "no volume",
     lambda r: rw(r, "infra/docker-compose.yml", lambda s: s.replace("    volumes:\n      - valkeydata:/data\n", ""))),
    ("I6  tunnel catch-all missing", "validate_infra.py", "catch-all",
     lambda r: rw(r, "infra/cloudflared/config.example.yml", lambda s: s.replace("  - service: http_status:404\n", ""))),
    ("I7  Firecrawl exposed publicly", "validate_infra.py", "tailnet",
     lambda r: rw(r, "infra/cloudflared/config.example.yml", lambda s: s.replace(
         "  - service: http_status:404", "  - hostname: crawl.example.com\n    service: http://localhost:3002\n  - service: http_status:404"))),
    ("I8  README names missing target", "validate_infra.py", "no such target",
     lambda r: rw(r, "infra/README.md", lambda s: s + "\nThen run `make deploy`.\n")),
    ("I9  compose YAML broken", "validate_infra.py", "not valid YAML",
     lambda r: rw(r, "infra/docker-compose.yml", lambda s: s + "\n  bad:\n   - [unclosed\n")),
    ("I10 secrets committed", "validate_infra.py", "source-of-record",
     lambda r: w(r, "infra/.env", "JWT_SECRET=leaked\n")),

    # --- documentation parity ---
    ("D1  prompt missing PROTOCOL-03", "validate_infra.py", "out of sync",
     lambda r: rw(r, "HERMES-PROMPT.md", lambda s: s.replace("PROTOCOL-03", "PROTOCOL-XX"))),
    ("D2  prompt drops Vercel rule", "validate_infra.py", "Vercel Hobby prohibition",
     lambda r: rw(r, "HERMES-PROMPT.md", lambda s: re.sub(r"^.*Vercel.*$", "", s, flags=re.M))),
    ("D3  copy markers removed", "validate_infra.py", "copy block is unusable",
     lambda r: rw(r, "HERMES-PROMPT.md", lambda s: s.replace("## COPY FROM HERE", "## start"))),
]


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    tmp = tempfile.mkdtemp(prefix="hermes-selftest-")
    base = os.path.join(tmp, "baseline")
    try:
        build_baseline(base)

        print("=== baseline: a complete PROTOCOL-01->03 run must validate clean ===")
        ok = True
        for script in ("validate_workspace.py", "validate_infra.py"):
            code, out = run(script, base)
            status = "PASS" if code == 0 else "FAIL"
            print(f"  {script:24} {status}")
            if code != 0:
                ok = False
                print("\n".join("      " + l for l in out.splitlines() if "[ERROR]" in l))

        print("\n=== negative cases: each defect must be caught ===")
        results = []
        for name, script, expect, mutate in CASES:
            work = os.path.join(tmp, "case")
            shutil.rmtree(work, ignore_errors=True)
            shutil.copytree(base, work)
            mutate(work)
            code, out = run(script, work)
            caught = code == 1 and expect in out
            results.append((name, caught))
            print(f"  {name:34} {'CAUGHT' if caught else 'MISSED'}")

        missed = [n for n, c in results if not c]
        print(f"\nbaseline: {'clean' if ok else 'DIRTY'} - "
              f"negatives caught: {len(results)-len(missed)}/{len(results)}")
        if missed:
            print("MISSED: " + ", ".join(missed))
        verdict = ok and not missed
        print("SELFTEST: " + ("PASS" if verdict else "FAIL"))
        return 0 if verdict else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
