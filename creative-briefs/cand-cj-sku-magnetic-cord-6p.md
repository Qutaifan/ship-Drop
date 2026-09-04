# Creative Brief — Magnetic Cable Organizer 6-Pack Desk Clips

## Product

> **Market note (2026-09-03):** `scripts/generate_brief.py` defaults to EU shipping carriers, EU delivery windows, and the EU AI Act disclosure regardless of the candidate's actual market. This is a US-pilot candidate (`config/markets/us-pilot.json`) -- the fields below were corrected by hand after generation. The generator itself is not market-aware and should be fixed before it's relied on for future US candidates; see the corresponding engineering debt task.

- Name: Magnetic Cable Organizer 6-Pack Desk Clips
- Linked validation file: products/cand-cj-sku-magnetic-cord-6p.md

## The "3+1" Creative Brief

### Ad Hook 1 — Problem-Oriented (9:16 Vertical Video)
- **0–3s (The Stop)**: Tight close-up on user struggling with traditional friction point. Bold kinetic text: *"Tired of digging through cable spaghetti every time you sit down?"*
- **3–10s (The Solution)**: Instant, seamless operation of Magnetic Cable Organizer 6-Pack Desk Clips in one smooth motion.
- **10–15s (Feature Proof)**: 2–3 macro cuts showing build quality, ease of cleaning, and durability.
- **15–20s (Call-to-Action)**: Clean packshot with discount overlay: *"Limited Launch Stock — Free US Delivery (3–8 Days)"*.

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
- **Trust Badges**: Fast US Domestic Shipping (USPS/UPS) · 30-Day Money-Back Guarantee · 2-Year Warranty.
- **Direct Express Checkout**: Integrated Stripe ExpressCheckout button (1-tap Apple Pay / Google Pay).

### Mid-Page Social Proof & Visual Evidence
- **Review Module**: Real customer photo grid with $\ge 4.7$ aggregate star rating.
- **Interactive FAQ Accordion**: Clear answers on shipping times, returns, and material specs.

### No-Account Checkout
- Direct 1-page checkout without account creation barriers.

---

## Remotion Programmatic Video Scaffold (JSON Props)

```json
{
  "composition": "ShortFormAd9x16",
  "fps": 30,
  "durationInFrames": 450,
  "resolution": {
    "width": 1080,
    "height": 1920
  },
  "audio": {
    "track": "dynamic-beat-120bpm.mp3",
    "volume": 0.8
  },
  "colorPalette": {
    "primary": "#1A1A1A",
    "accent": "#FF4D4D",
    "background": "#F7F7F7",
    "text": "#111111"
  },
  "hooks": [
    {
      "id": "hook-1-problem",
      "headline": "Tired of cable spaghetti on your desk?",
      "subheadline": "Snap it in place in 2 seconds.",
      "durationFrames": 90
    },
    {
      "id": "hook-2-transform",
      "headline": "Before vs. After",
      "subheadline": "Instant desk upgrade.",
      "durationFrames": 90
    },
    {
      "id": "hook-3-lifestyle",
      "headline": "Elevate your workspace.",
      "subheadline": "Minimalist design & premium feel.",
      "durationFrames": 90
    }
  ],
  "cta": {
    "text": "Get 40% Off Today \u2014 Free US Shipping",
    "badge": "30-Day Money-Back Guarantee",
    "durationFrames": 90
  }
}
```

---

## Compliance & Regulatory Disclosures
- **FTC AI Disclosure**: PDP & video footer carries disclosure per FTC guidance: *"Product imagery and creative brief assisted by generative AI"*. (EU AI Act disclosure is not applicable to the US pilot; reinstate if this candidate is ever sold into the EU.)
- **FTC Pricing Safeguards**: All pricing discounts are transparent and non-demographically profiled.
