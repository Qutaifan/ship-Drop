---
name: veo-flow-ads
description: Re-shoot winning ad hooks via Google Flow Veo 3.1.
version: 0.1.0
author: Ahmad, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [video-ads, veo, google-flow, winner-phase, dropshipping]
    related_skills: [ecommerce-ppc-strategy-planner, ecommerce-validator]
---

# Veo Flow Ads (Winner-Phase Re-Shoot) Skill

Generate cinematic 9:16 ad clips on Google Flow's Veo 3.1 to **re-shoot hooks that already proved themselves in the Veo Lite/Fast test phase**. Native audio in-clip, ~$2.00 per Quality winner at Pro tier, commercial-use cleared for paid ads.

**Use only after** the Veo Lite/Fast test phase has shipped ≥40 creatives and at least one has crossed the 40% 3-sec view rate threshold. Do NOT use for the test phase.

---

## When to Use

- A campaign's hook scored ≥40% 3-sec view rate in Veo Lite/Fast test data and needs cinematic re-shoot.
- A/B testing Veo Lite/Fast against Veo Quality to determine whether Quality earns its $2.00/clip premium.
- Native synced audio is needed (e.g. sizzle, voiceover, environment sound) — Veo generates audio in-clip.

**Don't use for**: the 40+/month test phase (use Veo Lite on the existing Pro sub — $0.20/clip, ~100/month capacity). Don't use for: text-heavy explainer videos (Remotion/Motion Canvas is cheaper and faster).

---

## Prerequisites

- **Google AI Pro subscription** active (1,000 Flow credits/month). Verify with `scripts/flow_credit_check.py`.
- **Google account** signed into Flow (`https://flow.google`).
- A winning hook reference: `campaigns/<product>.md` with `3s_view_rate ≥ 0.40` recorded.
- A staged product image from `comfyui-product-staging` (transparent PNG with EU AI Act disclosure burned in).
- **ffmpeg** + **ffprobe** installed locally for spec verification and EU AI Act overlay post-process.

---

## How to Run

This skill has two operating modes: **manual** (recommended for the pilot) and **API** (later, via the Veo 3.1 endpoint once it leaves Flow and lands in a stable API path).

### Manual mode (recommended, 2026-08-30)

1. `terminal(command="python scripts/flow_credit_check.py", workdir="C:/Users/Ahmad/Desktop/Dropshipping")` — confirm ≥200 credits remaining before any clip.
2. In Flow: upload the staged product PNG as the first frame reference. Pick **Veo 3.1 Quality** model, **9:16**, **8s**.
3. Paste a structured prompt (template below). Generate.
4. Download the resulting MP4 to `creative-briefs/<product>/veo/<n>.mp4`.
5. Post-process with `ffmpeg` to bake EU AI Act disclosure (see §4).
6. Verify with `scripts/flow_credit_check.py --after` and record in `campaigns/<product>.md`.

### API mode (deferred)

Veo 3.1 on Vertex AI is `$0.40–$4.80 per 8s clip` metered. Same Pro allowance in dollars buys the same Quality output as Flow credits (~$0.40/clip on Fast, $2.00/clip on Quality) but with no ceiling. Useful only when campaign volume exceeds 10 Quality winners/month. Not used in this project's current phase.

---

## Quick Reference

| Veo model | 8s credits (Pro) | $/clip at Pro | Use for |
|---|---|---|---|
| Veo 3.1 Lite | 10 | ~$0.20 | Within-winner iteration; never for final |
| Veo 3.1 Fast | 20 | ~$0.40 | Iteration / pacing test |
| Veo 3.1 Quality | 100 | ~$2.00 | Final winner-phase re-shoot |
| 1080p upscale | 0 | $0 | Apply to all of the above on Pro |

```
scripts/flow_credit_check.py                    # assert ≥200 credits remaining
scripts/flow_credit_check.py --after            # log spend, refresh date
scripts/stitch_veo_clips.py in/*.mp4 out.mp4    # 4×8s → 30s ad with 200ms crossfades
scripts/run_veo_pilot.py --product <slug>       # Wan-vs-Veo A/B harness
ffmpeg -i in.mp4 -vf "drawtext=text='AI-assisted creative':..." -c:a copy out.mp4
```

---

## Procedure

### Step 1 — Confirm the hook is worth a Veo re-shoot

- Open `campaigns/<product>.md`.
- Read the most recent Veo Lite/Fast test result. Required: 3-sec view rate ≥40% AND sample size ≥1,000 impressions.
- If the hook hasn't crossed that bar, return to the test phase and ship more Veo Lite variants. Do not burn Flow Quality credits.

**Completion criterion**: `campaigns/<product>.md` contains a row with `3s_view_rate ≥ 0.40` and `impressions ≥ 1000` against the Veo Lite/Fast variant.

### Step 2 — Run the credit guard

```
terminal(command="python scripts/flow_credit_check.py", workdir="C:/Users/Ahmad/Desktop/Dropshipping")
```

Hard ceiling: ≤10 Quality clips per calendar month. Reserve ≥200 credits for within-winner Fast/Lite iteration. If exceeded, abort and wait until next refresh.

**Completion criterion**: exit code 0; stdout reports `remaining ≥ 200` and `quality_used_this_month ≤ 10`.

### Step 3 — Compose the prompt

Use the template in `references/prompt-template.md`. Required order: subject → setting → motion → camera → audio. Always include the EU AI Act label string in the prompt's "safety" footer so Flow can bake SynthID + the visible label consistently.

**Completion criterion**: prompt saved to `creative-briefs/<product>/veo/<n>.prompt.json` with subject, setting, motion, camera, audio, sfx, label fields.

### Step 4 — Generate and download

In Flow:
- Upload staged product PNG as first-frame reference (from `comfyui-product-staging` output).
- Model: **Veo 3.1 Quality**, 9:16, 8s.
- Paste the prompt from Step 3.
- Generate. If the result misses the brief, **use Fast (20 cr) for the next iteration**, not Quality.

Download the MP4 to `creative-briefs/<product>/veo/<n>.mp4`.

**Completion criterion**: file present at `creative-briefs/<product>/veo/<n>.mp4`; `ffprobe` confirms 1080×1920 H.264 + AAC.

### Step 5 — Bake EU AI Act disclosure

```
terminal(command="ffmpeg -i creative-briefs/<product>/veo/<n>.mp4 -vf \"drawtext=text='AI-assisted creative':x=20:y=H-th-40:fontsize=28:fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=8\" -c:a copy creative-briefs/<product>/veo/<n>-labeled.mp4")
```

Veo already embeds invisible SynthID. The visible label is the EU AI Act Article 50 disclosure we owe anyway — same widget, no extra work.

**Completion criterion**: `creative-briefs/<product>/veo/<n>-labeled.mp4` exists; frame-0 string match on `AI-assisted creative` returns True.

### Step 6 — Stitch into a 30s ad (optional)

For ≥30s placements (long-form Meta, YouTube Shorts top-of-feed):

```
terminal(command="python scripts/stitch_veo_clips.py creative-briefs/<product>/veo/labeled-*.mp4 creative-briefs/<product>/veo/final-30s.mp4")
```

Default: 4×8s clips with 200ms crossfades = 30.8s. Cost: 4 × 100 Quality credits = 400 credits per stitched ad.

**Completion criterion**: `final-30s.mp4` is H.264+AAC at 1080×1920, duration 28–32s.

### Step 7 — Log to the campaign record

Append to `campaigns/<product>.md`:

```
## Veo 3.1 re-shoots
- <YYYY-MM-DD>: clip <n>, model Quality, 8s, prompt <hash>
  - 3-sec view rate (planned A/B): ___
  - ROAS at €79.90 (planned): ___
```

**Completion criterion**: row present with all fields filled or `n/a` justified.

---

## Pitfalls

- **8s native cap** — Veo generates at most 8s per clip. A 30s ad is 4 stitched clips (400 credits on Quality). Plan credit spend before generation, not after.
- **Retries bill like production** — Pro subscribers do not get "lower priority" rate. Every Fast generation is 20 credits whether it lands or not. Use Fast for iteration, Quality only for the final.
- **Do NOT strip SynthID** — invisible watermark is mandatory under Veo's ToS and aligned with EU AI Act Article 50 disclosure. Stripping it breaches ToS and forfeits a disclosure we already owe.
- **Native audio is a feature, not a bug** — Veo generates synced audio in-clip. Don't try to mix your own. Spec: H.264 + AAC; FFmpeg copy is safe.
- **Flow credits do NOT roll over** — Pro's 1,000 credits reset monthly. Don't stockpile.
- **Subject drift on long prompts** — keep prompts under 80 words. Subject → setting → motion → camera → audio. Anything past 80 words degrades coherence.
- **Commercial rights confirmation** — record the license URL (`https://support.google.com/gemini/thread/438424897`) in `campaigns/<product>.md` before any Veo clip is paid-trafficked. Google Product Expert confirmation is the authoritative answer, but cite it.
- **Cost-control**: Quality = $2.00/clip × 10 = $20/mo ceiling for winner-phase. If a campaign needs more than 10 winners/month, escalate to Vertex AI API ($0.40/clip on Fast, metered) — not to higher Flow tier.

---

## Verification

Each Veo clip run is complete only when **all** of the following hold:

- [ ] `scripts/flow_credit_check.py` exits 0; remaining credits ≥200; quality-used-this-month ≤10.
- [ ] Output MP4 is 1080×1920 H.264+AAC (verified via `ffprobe`).
- [ ] EU AI Act overlay text present in frame 0 (verified via `ffmpeg` frame extract + string match).
- [ ] SynthID left intact (no ffmpeg re-encode that strips metadata; use `-c copy` for audio pass-through, `-c:v libx264 -crf 18` for the drawtext pass but keep the original's metadata).
- [ ] Row appended to `campaigns/<product>.md` with model, date, credit cost, prompt hash.
- [ ] For stitched clips: total duration 28–32s; crossfades present at clip boundaries.

---

## License confirmation (cite before paid traffic)

Google Product Expert, June 2026: *Yes, videos made with Veo 3 using Google Flow can be used for commercial purposes with a Google AI Ultra subscription. Or other levels also. Google permits the commercial use of Veo 3 outputs, allowing you to legally integrate them into advertising, marketing materials, and other projects.*

URL: `https://support.google.com/gemini/thread/438424897`

**Action**: copy this URL into `campaigns/<product>.md` "License reference" section before any Veo clip is paid-trafficked. Without it, the campaign record is incomplete.