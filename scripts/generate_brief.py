#!/usr/bin/env python3
"""
Hermes-Ecom PROTOCOL-02 Creative Brief & Remotion Scaffold Generator.

Scaffolds a complete "3+1" creative brief for a validated candidate product:
- Hook 1: Problem-Oriented
- Hook 2: Transformation
- Hook 3: Aspirational Lifestyle
- Landing Page Framework with Stripe Express Checkout (Apple/Google Pay)
- Remotion JSON props schema for programmatic vertical video rendering
- EU AI Act & FTC compliance headers

Usage:
  python3 scripts/generate_brief.py <product-slug>
  python3 scripts/generate_brief.py electric-pepper-grinder --dry-run
  python3 scripts/generate_brief.py --selftest

Stdlib only.
"""
import argparse
import json
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def check_product_passed(root, product_slug):
    p_path = os.path.join(root, "products", f"{product_slug}.md")
    if not os.path.isfile(p_path):
        return False, f"products/{product_slug}.md does not exist."
    with open(p_path, encoding="utf-8") as f:
        content = f.read()

    vm = re.search(r"^##\s*Verdict\s*$\n+(.*)$", content, re.MULTILINE)
    if not vm or "PASS" not in vm.group(1).upper() or "FAIL" in vm.group(1).upper():
        return False, f"products/{product_slug}.md verdict is not 'PASS'."
    return True, "PASS"


def build_brief_content(product_slug, product_name=None):
    clean_name = product_name or product_slug.replace("-", " ").title()

    remotion_schema = {
        "composition": "ShortFormAd9x16",
        "fps": 30,
        "durationInFrames": 450,
        "resolution": {"width": 1080, "height": 1920},
        "audio": {"track": "dynamic-beat-120bpm.mp3", "volume": 0.8},
        "colorPalette": {
            "primary": "#1A1A1A",
            "accent": "#FF4D4D",
            "background": "#F7F7F7",
            "text": "#111111"
        },
        "hooks": [
            {
                "id": "hook-1-problem",
                "headline": f"Tired of messy cooking with {clean_name}?",
                "subheadline": "One-handed ease in 2 seconds.",
                "durationFrames": 90
            },
            {
                "id": "hook-2-transform",
                "headline": "Before vs. After",
                "subheadline": "Instant kitchen upgrade.",
                "durationFrames": 90
            },
            {
                "id": "hook-3-lifestyle",
                "headline": "Elevate your dining space.",
                "subheadline": "Minimalist design & premium feel.",
                "durationFrames": 90
            }
        ],
        "cta": {
            "text": "Get 40% Off Today — Free EU Shipping",
            "badge": "30-Day Money-Back Guarantee",
            "durationFrames": 90
        }
    }

    schema_json = json.dumps(remotion_schema, indent=2)

    return rf"""# Creative Brief — {clean_name}

## Product
- Name: {clean_name}
- Linked validation file: products/{product_slug}.md

## The "3+1" Creative Brief

### Ad Hook 1 — Problem-Oriented (9:16 Vertical Video)
- **0–3s (The Stop)**: Tight close-up on user struggling with traditional friction point. Bold kinetic text: *"Tired of doing this every single meal?"*
- **3–10s (The Solution)**: Instant, seamless operation of {clean_name} in one smooth motion.
- **10–15s (Feature Proof)**: 2–3 macro cuts showing build quality, ease of cleaning, and durability.
- **15–20s (Call-to-Action)**: Clean packshot with discount overlay: *"Limited Launch Stock — Free EU Delivery (2–4 Days)"*.

### Ad Hook 2 — Transformation (9:16 Vertical Video)
- **0–3s (The Shift)**: Split-screen / swift before-and-after transition. Cluttered/inefficient state vs. clean, effortless state.
- **3–10s (Mechanism Demonstration)**: Sound-synced ASMR action sequence showing the product resolving friction immediately.
- **10–15s (Benefit Reenforcement)**: High-speed montage of various use-cases.
- **15–20s (Call-to-Action)**: Urgent stock notice + 30-Day satisfaction guarantee badge.

### Ad Hook 3 — Aspirational Lifestyle (9:16 Vertical Video)
- **0–3s (The Aesthetic)**: High-end lifestyle framing (warm lighting, clean aesthetic counter/desk, modern interior).
- **3–10s (Organic Integration)**: Natural usage seamlessly fitting into a calm, organized routine.
- **10–15s (Social Proof Overlay)**: On-screen quote: *"I didn't know I needed this until I got it."* with 5-star animation.
- **15–20s (Call-to-Action)**: Minimalist end-card with one-click purchase URL.

---

## Landing Page Framework (Conversion-Optimized)

### Above-the-Fold (Mobile LCP < 1.2s)
- **Hero Statement**: Ultra-clear benefit headline (resolves the core friction point in $\le 6$ words).
- **Primary Visual**: High-resolution 1:1 styled product asset staged with IC-Light.
- **Trust Badges**: Fast EU Local Warehouse Shipping (DHL/Hermes) · 30-Day Money-Back Guarantee · 2-Year Warranty.
- **Direct Express Checkout**: Integrated Stripe ExpressCheckout button (1-tap Apple Pay / Google Pay).

### Mid-Page Social Proof & Visual Evidence
- **Review Module**: Real customer photo grid with $\ge 4.7$ aggregate star rating.
- **Interactive FAQ Accordion**: Clear answers on shipping times, returns, and material specs.

### No-Account Checkout
- Direct 1-page checkout without account creation barriers.

---

## Remotion Programmatic Video Scaffold (JSON Props)

```json
{schema_json}
```

---

## Compliance & Regulatory Disclosures
- **EU AI Act**: PDP & Video footer carries disclosure: *"Product imagery and creative brief assisted by generative AI"*.
- **FTC Pricing Safeguards**: All pricing discounts are transparent and non-demographically profiled.
"""


def selftest():
    print("Running generate_brief selftest...")
    content = build_brief_content("selftest-gadget", "Selftest Gadget")
    assert "# Creative Brief — Selftest Gadget" in content
    assert "### Ad Hook 1 — Problem-Oriented" in content
    assert "### Ad Hook 2 — Transformation" in content
    assert "### Ad Hook 3 — Aspirational Lifestyle" in content
    assert "Remotion Programmatic Video Scaffold" in content
    assert "EU AI Act" in content
    print("SELFTEST: PASS")
    return 0


def main():
    ap = argparse.ArgumentParser(description="PROTOCOL-02 Creative Brief Scaffolder")
    ap.add_argument("slug", nargs="?", help="Product filename slug (e.g. electric-pepper-grinder)")
    ap.add_argument("--name", help="Display name for the product")
    ap.add_argument("--dry-run", action="store_true", help="Print brief to stdout without writing")
    ap.add_argument("--force", action="store_true", help="Generate brief even if product is not PASS")
    ap.add_argument("--selftest", action="store_true", help="Run offline unit tests")
    a = ap.parse_args()

    if a.selftest:
        return selftest()

    if not a.slug:
        ap.error("A product slug is required (or use --selftest)")

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_file = os.path.join(root, "creative-briefs", f"{a.slug}.md")

    if not a.force:
        passed, msg = check_product_passed(root, a.slug)
        if not passed:
            print(f"[ERROR] Cannot generate brief: {msg}")
            print("PROTOCOL-02 requires a PASS verdict in products/<slug>.md before creating a brief.")
            print("Use --force if you explicitly wish to override.")
            return 1

    content = build_brief_content(a.slug, a.name)

    if a.dry_run:
        print(content)
        return 0

    with open(target_file, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Created creative brief at: creative-briefs/{a.slug}.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
