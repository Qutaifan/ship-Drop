#!/usr/bin/env python3
"""
Hermes-Ecom PROTOCOL-02 Creative Brief & Veo 3.1 Prompt Scaffolder (GCC & Global).

Scaffolds a complete "3+1" creative brief for a validated candidate product:
- Hook 1: Problem-Oriented (Snapchat Spotlight & TikTok GCC)
- Hook 2: Transformation (ASMR / Visual Demonstration)
- Hook 3: Aspirational Lifestyle (Modern Gulf & Global lifestyle integration)
- Landing Page Framework (Arabic RTL 1-Page Fast Funnel with Apple Pay / Mada / COD & WhatsApp confirmation)
- Veo 3.1 prompt templates (subject→setting→motion→camera→audio, ≤80 words)
  per `.agents/skills/veo-flow-ads/references/prompt-template.md`
- GCC & Global regulatory compliance headers

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


def build_veo_prompts(clean_name):
    """Three Veo 3.1 prompt templates following subject→setting→motion→camera→audio order.

    Each prompt is ≤80 words per veo-flow-ads skill rules.
    """
    return [
        {
            "id": "hook-1-problem",
            "use": "Problem-Oriented (Snapchat / TikTok)",
            "model": "Veo 3.1 Lite (test) / Quality (winner)",
            "prompt": (
                f"Close-up of a hand struggling with the everyday friction "
                f"that {clean_name} solves — pressing, twisting, lifting, "
                f"or fiddling. Warm lighting, shallow DOF. Hand puts the "
                f"old tool down, picks up {clean_name}, one smooth motion "
                f"resolves the friction. Eye-level, slow dolly-in. "
                f"Audio: frustrated breath, then satisfying mechanical click. "
                f"\n\nPhotorealistic 9:16 vertical video for paid social ad. "
                f"EU AI Act / GCC disclosure overlay added in post."
            ),
        },
        {
            "id": "hook-2-transform",
            "use": "Transformation",
            "model": "Veo 3.1 Lite (test) / Quality (winner)",
            "prompt": (
                f"Split-screen then quick match-cut to {clean_name} in use: "
                f"cluttered or inefficient setup dissolves into a clean, "
                f"effortless result. Bright natural daylight, neutral "
                f"surfaces. The product moves once; the camera holds steady; "
                f"the result is unmistakable. 35mm lens, locked tripod. "
                f"Audio: ASMR material sound — soft click, glide, settle. "
                f"\n\nPhotorealistic 9:16 vertical video for paid social ad. "
                f"EU AI Act / GCC disclosure overlay added in post."
            ),
        },
        {
            "id": "hook-3-lifestyle",
            "use": "Aspirational Lifestyle (GCC / Modern Home)",
            "model": "Veo 3.1 Lite (test) / Quality (winner)",
            "prompt": (
                f"{clean_name} integrated naturally into a calm, modern, "
                f"well-lit home interior — warm ambient light, neutral "
                f"palette, tasteful styling. A person uses it without "
                f"commentary, lives the moment, the camera lingers on the "
                f"product. 50mm prime, slow orbit. Audio: ambient room tone, "
                f"soft footstep, gentle ceramic clink. "
                f"\n\nPhotorealistic 9:16 vertical video for paid social ad. "
                f"EU AI Act / GCC disclosure overlay added in post."
            ),
        },
    ]


def build_brief_content(product_slug, product_name=None):
    clean_name = product_name or product_slug.replace("-", " ").title()

    veo_prompts = build_veo_prompts(clean_name)
    veo_json = json.dumps(veo_prompts, indent=2)

    return rf"""# Creative Brief — {clean_name}

## Product
- Name: {clean_name}
- Linked validation file: products/{product_slug}.md

## The "3+1" Creative Brief (GCC & Multi-Platform)

### Ad Hook 1 — Problem-Oriented (Snapchat Spotlight & TikTok 9:16 Vertical)
- **0–3s (The Stop)**: Tight close-up on user struggling with traditional friction. Kinetic Arabic / English hook: *"هل تعاني من هذه المشكلة يومياً؟"* / *"Tired of dealing with this every day?"*
- **3–10s (The Solution)**: Instant, seamless operation of {clean_name} in one smooth motion.
- **10–15s (Feature Proof)**: 2–3 macro cuts showing premium build quality, durability, and convenience.
- **15–20s (Call-to-Action)**: Clean packshot with Gulf launch offer: *"عرض خاص لفترة محدودة — شحن سريع لدول الخليج والدفع عند الاستلام متاح"*.

### Ad Hook 2 — Transformation (9:16 Vertical Video)
- **0–3s (The Shift)**: Split-screen / instant before-and-after match cut. Cluttered/inefficient state vs. clean, effortless result.
- **3–10s (Mechanism Demonstration)**: Sound-synced ASMR action sequence showing friction resolved in 2 seconds.
- **10–15s (Benefit Reenforcement)**: High-speed montage of everyday use-cases.
- **15–20s (Call-to-Action)**: Urgency badge + 14-day money-back guarantee seal.

### Ad Hook 3 — Aspirational Lifestyle (9:16 Vertical Video)
- **0–3s (The Aesthetic)**: High-end modern living framing (warm lighting, clean aesthetic counter/desk, contemporary interior).
- **3–10s (Organic Integration)**: Natural usage seamlessly fitting into an elevated daily routine.
- **10–15s (Social Proof Overlay)**: Customer endorsement quote: *"صراحة غيّر يومي بالكامل.. مستحيل استغني عنه"* with 5-star rating animation.
- **15–20s (Call-to-Action)**: Minimalist end-card with 1-tap purchase button.

---

## Landing Page Framework (Arabic RTL 1-Page Fast Funnel)

### Above-the-Fold (Mobile LCP < 1.2s, RTL Layout)
- **Hero Statement**: Ultra-clear benefit headline in Arabic (resolves core pain point in $\le 6$ words).
- **Primary Visual**: High-resolution 1:1 styled product asset staged with IC-Light.
- **Trust Badges**: Fast GCC Delivery (Aramex / SMSA / AJEX / iMile) · 14-Day Free Returns · Official Warranty.
- **Direct Express Checkout**: 
  - **Prepaid 1-Tap**: Apple Pay / Mada / Tabby / Tamara button.
  - **Cash on Delivery (COD)**: Simple 3-field form (الاسم الكامل، رقم الجوال، المدينة/الحي).

### Mid-Page Social Proof & Visual Evidence
- **Customer Reviews**: Verified GCC buyer photo reviews with $\ge 4.8$ aggregate star rating.
- **WhatsApp Support Trigger**: Floating WhatsApp button for instant pre-sale reassurance.
- **Interactive FAQ Accordion**: Clear answers on shipping times (2–5 days), payment methods, and return policy.

### Automated Post-Order Verification (For COD Orders)
- Instant automated WhatsApp message confirming delivery address and phone number to reduce RTO (Return to Origin) below 12%.

---

## Veo 3.1 Programmatic Video Brief (Prompt Templates)

Use Veo 3.1 Lite for the test phase (10 credits/clip, ~$0.20, ~100 clips/month on Pro). Promote a proven hook to Veo 3.1 Quality (100 credits/clip, ~$2.00) for the winner phase. Skill: `.agents/skills/veo-flow-ads/`. Reference: `.agents/skills/veo-flow-ads/references/prompt-template.md`.

Each prompt follows the subject→setting→motion→camera→audio order. Keep ≤80 words. Append the regulatory disclosure footer to every prompt.

```json
{veo_json}
```

---

## Compliance & Regulatory Disclosures
- **EU AI Act & Global AI Transparency**: PDP & Video footer carries disclosure: *"Product imagery and creative brief assisted by generative AI"*. SynthID watermark embedded invisibly in all Veo outputs.
- **GCC Consumer Protection & FTC Guidelines**: Transparent non-deceptive pricing, clear return/refund policies, rule-based non-personalized promotional pricing.
"""


def selftest():
    print("Running generate_brief selftest...")
    content = build_brief_content("selftest-gadget", "Selftest Gadget")
    assert "# Creative Brief — Selftest Gadget" in content
    assert "### Ad Hook 1 — Problem-Oriented" in content
    assert "### Ad Hook 2 — Transformation" in content
    assert "### Ad Hook 3 — Aspirational Lifestyle" in content
    assert "Veo 3.1 Programmatic Video Brief" in content
    assert "EU AI Act" in content
    assert "Remotion" not in content, "Remotion reference must be removed"
    prompts = build_veo_prompts("Selftest Gadget")
    assert len(prompts) == 3, "must produce exactly 3 hooks"
    for p in prompts:
        body = p["prompt"].split("\n\n")[0]
        wc = len(body.split())
        assert wc <= 80, f"{p['id']} prompt body {wc} words exceeds 80-word Veo limit"
    print("SELFTEST: PASS")
    return 0


def main():
    ap = argparse.ArgumentParser(description="PROTOCOL-02 Creative Brief Scaffolder (GCC & Global)")
    ap.add_argument("slug", nargs="?", help="Product filename slug (e.g. electric-pepper-grinder)")
    ap.add_argument("--name", help="Display name for the product")
    ap.add_argument("--dry-run", action="store_true", help="Print brief to stdout without writing")
    ap.add_argument("--force", action="store_true", help="Generate brief even if product is not PASS")
    ap.add_argument("--selftest", action="store_true", help="Run offline unit tests")
    a = ap.parse_args()

    if a.selftest:
        return selftest()

    if not a.slug:
        ap.error("product slug required (or pass --selftest)")

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if not a.force:
        ok, msg = check_product_passed(repo_root, a.slug)
        if not ok:
            print(f"FAIL: {msg} (use --force to override)", file=sys.stderr)
            return 1

    content = build_brief_content(a.slug, a.name)
    out_path = os.path.join(repo_root, "creative-briefs", f"{a.slug}.md")
    if a.dry_run:
        print(content)
    else:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"WROTE: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())