---
name: veo-flow-ads
description: Re-shoot winning ad hooks via Google Flow Veo 3.1 with programmatic prompt templates, credit guards, and EU/FTC AI disclosure watermarks.
version: 0.1.0
author: Ahmad, Hermes-Ecom
license: MIT
platforms: [linux, macos, windows]
---

# Veo Flow Ads (Winner-Phase Video Re-Shoot) Skill 🎬

Generate cinematic 9:16 vertical video ad clips on Google Flow's **Veo 3.1** to **re-shoot hooks that have already proven themselves in testing**. Delivers native in-clip audio, ~$2.00 per Quality winner at Pro tier, commercial-use cleared for paid advertising.

> [!IMPORTANT]
> **Use Only for Winner Scaling**: Creative hit rate is ~5%, so volume finds winners and quality scales them. Run the initial test phase on local GPU / Wan / Remotion (€0 marginal cost). Ship 40+ testing creatives. Once a creative crosses $\ge 40\%$ 3-second view rate or generates $\ge 2.0\times$ ROAS, graduate it to Veo 3.1 Quality for cinematic scale.

---

## 1. Google Flow Credit Reference & Tiers

| Veo Model | 8s Credits (Pro Tier) | Estimated Cost / Clip | Strategic Role |
|---|:---:|:---:|---|
| **Veo 3.1 Lite** | 10 credits | ~$0.20 | Within-winner rapid motion/angle iteration |
| **Veo 3.1 Fast** | 20 credits | ~$0.40 | Pacing, hook variation, split testing |
| **Veo 3.1 Quality** | 100 credits | ~$2.00 | **Final winner-phase scaling asset** (photorealistic + native audio) |
| **1080p Upscale** | 0 credits | $0.00 | Mandatory application to all final outputs |

*Monthly Pro Tier Allowance*: ~1,000 credits/month $\to$ supports up to 10 Quality Winner Re-Shoots or 50 Fast iterations.

---

## 2. Programmatic Prompt Structure (≤ 80 Words)

Veo 3.1 excels when prompted using the deterministic 5-element sequence:
$$\text{Subject} \longrightarrow \text{Setting} \longrightarrow \text{Motion} \longrightarrow \text{Camera} \longrightarrow \text{Audio}$$

### Formula Template:
```
[Subject: Specific product with materials & distinct features] in [Setting: High-end Scandinavian/DTC minimalist interior], [Motion: Precise physical demonstration of the core problem-solving mechanism], [Camera: Tight macro tracking shot, 9:16 vertical framing, shallow depth of field, 24fps cinema grade], [Audio: Crisp ASMR magnetic snap sound effect with subtle ambient room tone].
```

---

## 3. Regulatory Compliance & AI Watermark Injection

Per **EU AI Act Article 50** and **FTC Synthetic Media Safeguards**, all generative marketing videos must carry clean, indelible transparency disclosures:

### Automated FFmpeg Overlay Command:
```bash
ffmpeg -i input_veo.mp4 -vf "drawtext=text='Product imagery assisted by generative AI':x=24:y=H-th-48:fontsize=26:fontcolor=white:box=1:boxcolor=black@0.6:boxborderw=10" -c:a copy output_labeled.mp4
```

> [!WARNING]
> Do NOT attempt to strip Google's invisible **SynthID** watermark. It ensures platform provenance compliance and prevents account suspension under Google Workspace Commercial Terms.

---

## 4. Multi-Clip Assembly (30-Second High-Converting Flow)

To assemble a complete 30-second TikTok / Reels ad from Veo clips:
1. **Clip 1 (0–3s)**: The Shock/Pain Hook (Veo 3.1 Quality, macro disruption).
2. **Clip 2 (3–11s)**: The Mechanism / Relief Transformation (Veo 3.1 Quality, before-and-after match cut).
3. **Clip 3 (11–22s)**: Lifestyle Integration (Veo 3.1 Fast, DTC modern environment).
4. **Clip 4 (22–30s)**: Value Offer + Guarantee + CTA (Remotion programmatic outro banner with Stripe Express badges).
