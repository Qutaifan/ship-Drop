# Skills Audit vs AGENTS.md Stack — 2026-08-30

Audited: the five project-local skills under `.agents/skills/`. AGENTS.md §7A is the contract; deviations and OSS alternatives are below.

## Top-line finding

The five project skills are **directionally aligned** with the AGENTS.md stack but each has at least one **blocker-level defect**: a missing hardline frontmatter field, a now-wrong threshold copied from a pre-2026-08-30 report, a prohibited workflow, or a missing dependency on infrastructure the workspace doesn't yet have. They will mislead an agent that loads them verbatim.

Three skills (ecommerce-validator, medusa-v2-storefront, comfyui-product-staging) need ground-up rewrites before they can be trusted. Two (crawlee-scraper, remotion-video-ads) need targeted patches.

**Nexscope review (added 2026-08-30, see `.agents/skills/_reviewed-not-installed.md`).** Reviewed nine Nexscope eCommerce-Skills candidates (MIT, 142-skill repo). Adopted `ecommerce-ppc-strategy-planner` (533 lines, best fit); archived the five custom skills to `.agents/skills/_archive/`. Outcome: one of nine candidates carried substantive methodology applicable to a non-Amazon Medusa stack. The rest are either prompt-only guidance or Amazon-FBA-shaped math. The five archived skills + executable scripts in `scripts/` remain the source of truth for PROTOCOL-01 gating. Rollback: `mv .agents/skills/_archive/* .agents/skills/`.

Internet scan: every layer has a credible OSS alternative. None of the alternatives is materially better than the chosen one for this project's constraints (zero marginal cost, single-GPU, EU customs-aware). **No re-stack warranted.** Only Rewrites and a license question on Remotion.

---

## Cross-cutting issues (all five skills)

1. **Frontmatter is non-conformant** with the in-repo SKILL.md standard (`hermes-agent-skill-authoring` skill):
   - Every file is missing `version`, `author`, `license`, `platforms`, `metadata.hermes.{tags, related_skills}`.
   - `description` exceeds the 60-char hardline in all five:
     - `ecommerce-validator` — 230 chars
     - `medusa-v2-storefront` — 213 chars
     - `crawlee-scraper` — 161 chars
     - `comfyui-product-staging` — 165 chars
     - `remotion-video-ads` — 168 chars
   - Consequence: the system-prompt index truncates each description at 57+`...` and the trigger capability is buried mid-sentence. Agents won't reliably load them.
2. **No `When to Use` triggers** — all five open straight into architecture. The agent has no counter-trigger ("don't use for…").
3. **No `Verification` section** — no completion criterion per skill. PROTOCOL-01 expects falsifiable outputs; the validator skill has no way to prove a PASS verdict.
4. **No `Pitfalls` section** — the scripts know things the skills don't surface (e.g. `profitability.py` exists; the skill doesn't reference it; AGENTS.md calls for CAC gate that margin_solver alone doesn't enforce).

---

## 1. ecommerce-validator

**Verdict: BLOCKER — needs ground-up rewrite.** Contains a now-wrong EU duty figure, a missing CAC gate, and a "buying constraint" formula that contradicts AGENTS.md.

### Critical defects

| # | Issue | Source of truth |
|---|---|---|
| D1 | Says "**€3 flat customs duty**" without flagging that direct-from-China now ALSO incurs **import VAT + ~€2 carrier fee per unit** | AGENTS.md §4B ("€3 duty + import VAT + carrier handling fee (~€2) on every order") |
| D2 | No reference to `profitability.py` / CAC gate | AGENTS.md §4A ("CAC gate added 2026-08-30 … net margin must be ≥ 2× median CPA benchmark ~€21.48") |
| D3 | Lists WEEE & Battery Directives as a Step 4 item, but no script enforces them | `validate_workspace.py` doesn't check this — mismatch between procedure and enforcement |
| D4 | "Buying Constraint: landed cost ≤ 20.3% of VAT-inclusive retail" — this is a derived number (≈ (1−k)/(1+vat) for k=margin share), not an input constraint. Conflates "ceiling" with "ceiling at this specific margin target" | Reverse-engineered against AGENTS.md — the right input is "must clear 3× COGS AND >€15 AND >2× median CPA" |
| D5 | Skeptic-ratio rule (≥50% = fail) is correct but not cross-referenced to `learnings/HEURISTICS.md` per PROTOCOL-03 | AGENTS.md §3 (ORIENT phase mandates reading HEURISTICS.md first) |
| D6 | Step 4 says "EU AI Act: include disclosure" — AGENTS.md §4B now requires **clean, visible disclosure** specifically for AI imagery / virtual models / conversational agents. Skill underspecifies | AGENTS.md §4B |

### OSS alternatives considered

| Alternative | Verdict |
|---|---|
| `ProductLair` research tool (free) | Web SaaS; no scriptable API; doesn't compute CAC gate. **Reject.** |
| `AliShopping Tools` 11-free stack (2026) | Affiliate-tool blog. **Reject.** |
| `Ecomhunt` / `Sell The Trend` free tier | Both gated; no CAC math. **Reject.** |
| Spreadsheet-based workflow | Re-invents `scripts/margin_solver.py`. **Reject.** |
| **None — keep the in-repo script stack** | `margin_solver.py` (corrected 2026-08-30), `profitability.py` (CAC gate), `ad_library.py`, `demand_screen.py`. Already aligned with AGENTS.md. **Adopt — but rewrite the skill to match the scripts.** |

### Required rewrite

- Delete "Buying Constraint" formula entirely.
- Reorder as: **Step 0: read `learnings/HEURISTICS.md`**.
- **Step 1**: `demand_screen.py` (skeptic ratio + median views + short-form share) — keep.
- **Step 2**: `margin_solver.py` with the corrected VAT-corrected formula.
- **Step 2b (NEW)**: `profitability.py --retail R --landed L` — exits 1 on CAC failure.
- **Step 3**: `ad_library.py` (EU/UK only — keep current rule, it's correct).
- **Step 4**: regulatory checklist with explicit EU AI Act disclosure wording + FTC rule-based pricing + WEEE/battery (where electrical).
- **Step 5 (NEW)**: `validate_workspace.py products/<slug>.md` — final gate; PASS only if validator exits 0.
- Add `Verification` section: "Skill completes when validate_workspace.py exits 0 on the populated product file."

---

## 2. medusa-v2-storefront

**Verdict: BLOCKER — needs rewrite.** Stripe Express element wiring is technically correct, but the skill hard-codes the wrong validator host and is missing the AGENTS.md-mandated R2 wiring.

### Critical defects

| # | Issue | Source of truth |
|---|---|---|
| D1 | Says "Medusa v2 Backend (127.0.0.1:9000)" — fine. But shows Cloudflare Tunnel + Cloudflare Pages + self-hosted Umami with **no Cloudflare Tunnel config** and **no R2 driver wiring** | AGENTS.md §7A (Cloudflare R2 free-tier + Tunnel required) |
| D2 | Recommends Stripe Express Checkout element with a `clientSecret` it never provisions | A real `clientSecret` requires `paymentIntents.create()` server-side in Medusa; the skill skips that step |
| D3 | VAT rates table is correct but IOSS/OSS one-stop filing wiring is missing (AGENTS.md says register IOSS/OSS, not per-country) | AGENTS.md §4B |
| D4 | No reference to `infra/docker-compose.yml`, `infra/cloudflared/`, or `infra/README.md` — the skill is detached from the infra scaffold that actually exists in this repo | `infra/` directory listing confirms Docker Compose and Cloudflared scaffold exist |
| D5 | Recommends `fetchpriority="high"` but doesn't mention `next/image` + R2 loader config Medusa's Next.js starter requires | Practical: R2 needs a custom loader in `next.config.js` |
| D6 | No mention of Vercel prohibition (AGENTS.md §7A hard trap) | AGENTS.md §7A |

### OSS alternatives considered

| Alternative | Verdict |
|---|---|
| **Saleor** (BSD-3, Python/Django/GraphQL) | Mature, ~22.7k stars, best-in-class GraphQL. But: requires Python in stack, complicates infra (Python on ThinkBook + Node on Next.js + Postgres already). AGENTS.md picked Medusa for a reason (MIT, JS-stack homogeneity). **Reject — no improvement that offsets stack fragmentation.** |
| **Vendure** (TypeScript/GraphQL/NestJS, GPLv3 core) | Better B2B and multi-channel; mature admin UI. **License is GPLv3** — once modified core is shipped, AGENTS.md's "free/OSS path" starts blurring. Managed cloud not GA until late 2026. **Reject — license risk and the GPLv3 + AGENTS.md "no commercial clauses" tension.** |
| **Spree Commerce** (BSD-3, REST, TS SDK) | Real OSS, no platform fees. Smaller community, fewer 2026 Next.js starters. **Reject — momentum gap vs Medusa.** |
| **Bagisto** (MIT, Laravel/PHP) | All-in-one; doesn't fit headless-only architecture the AGENTS.md spec mandates. **Reject.** |
| **WooCommerce** (GPL, PHP/WordPress) | AGENTS.md already lists as fallback ("if Medusa's two-process proves too heavy"). **Keep as fallback, not primary.** |
| **Shopware** (MIT) | Strong EU presence but Symfony/PHP. **Reject.** |
| **Stay on Medusa v2** | AGENTS.md §7A chose it explicitly. ~35k stars, MIT, first-class Next.js starter. **Keep.** |

### Required rewrite

- Add "When NOT to use: don't use for monoliths, don't deploy the storefront to Vercel Hobby."
- Section 1: full architecture diagram including Cloudflare Tunnel, R2, Umami, Valkey, Postgres 16.
- Section 2: **complete** Stripe Express wiring — server-side `paymentIntents.create` snippet, not just client element.
- Section 3: IOSS/OSS one-stop registration + Medusa region config (destination VAT).
- Section 4: `next.config.js` R2 loader + `next/image` config; explicit Cloudflare Pages build command.
- Add `Pitfalls`: Vercel Hobby trap, IOSS registration timeline, R2 CORS for Stripe webhook, two-process (server + worker) minimum.
- Add `Verification`: `curl http://localhost:9000/health` returns ok, Cloudflare tunnel route resolves, `/api/payment-intent` returns a non-empty `clientSecret`.

---

## 3. crawlee-scraper

**Verdict: PATCH-LEVEL.** Pattern is right; gap is it's a TypeScript snippet in a Python-first workspace, and it has no anti-detection session-pool config for sites that block Cloudflare-fronted stores.

### Critical defects

| # | Issue | Source of truth |
|---|---|---|
| D1 | Uses Crawlee **TypeScript** (`import { PlaywrightCrawler } from 'crawlee'`). The workspace scripts are Python-first (margin_solver, profitability, ad_library, demand_screen). Introducing a TS toolchain just for one skill is asymmetric | Project convention: `scripts/*.py`, no `package.json` yet |
| D2 | No proxy pool config — modern storefronts (Shopify, Cloudflare-fronted) fingerprint Crawlee's default UA | Crawlee docs: `proxyConfiguration` with rotating residential proxies |
| D3 | No reference to `scripts/` for *which* sites the agent scrapes — agent has to re-derive the merchant-site scope from AGENTS.md §7A "Firecrawl remit" paragraph | AGENTS.md §7A |
| D4 | `await crawler.run([...])` is commented out — agent can't run the example as-is | Skill must run verbatim |

### OSS alternatives considered

| Alternative | Verdict |
|---|---|
| **Firecrawl (self-hosted, AGPL-3.0)** | AGENTS.md already ADOPTS this for OBSERVE phase on merchant sites. Crawlee is fine for routes where Firecrawl's LLM-extract step is wrong (e.g. a 1,000-product catalog table Firecrawl would over-chunk). **Complement, not replace.** |
| **Playwright alone** | No request queue, no retries, no dataset storage. Why Crawlee exists. **Reject as a replacement.** |
| **Scrapy** | Pythonic, no JS execution by default; needs scrapy-playwright bridge. Slower for JS-heavy storefronts than Crawlee. **Reject.** |
| **Apify SDK / Apify platform** | SaaS. Violates zero-cost. **Reject.** |
| **Agent-Reach (Jina Reader)** | AGENTS.md ADOPTS for YouTube/web/RSS — different layer (demand-side, not merchant scrape). **Complement, not replace.** |
| **Stay on Crawlee, but Python port** | Crawlee-Python exists (Apify team, MIT/Apache, less mature than TS). For prototype phase this is acceptable. **Adopt — switch snippet to `crawlee` Python.** |

### Required patch

- Convert TypeScript snippet to Python (`from crawlee.playwright_crawler import PlaywrightCrawler`).
- Add `proxy_configuration` example with rotating residential free tier (`apify-proxy` free tier or `webshare.io` free 10 proxies).
- Add explicit scope: "merchant sites and supplier catalogues; **never** Meta Ad Library, TikTok Creative Center, or any platform whose terms forbid scraping."
- Add `Verification`: `python scripts/crawlee_smoke.py https://example.com` exits 0 with a row in `./dataset.json` containing `{url, title, price, reviews}`.

---

## 4. comfyui-product-staging

**Verdict: BLOCKER — needs rewrite.** Pipeline concept is correct (BiRefNet → FLUX.1 Schnell → IC-Light → upscaler). But the chosen **base model (FLUX.1 Schnell) is no longer the right test-phase default** per the AGENTS.md tech-upgrade report.

### Critical defects

| # | Issue | Source of truth |
|---|---|---|
| D1 | Pipeline ends with image. PROTOCOL-02 requires **video scaffolds** too; the skill is image-only. Video generation now lives in `.agents/skills/veo-flow-ads/` (Flow / Veo 3.1) — ComfyUI skill only owns the image leg | AGENTS.md §7A (Creative & Video Generation stack row) |
| D2 | FLUX.1 Schnell is still the right image base for 8GB VRAM. No video leg in this skill — Veo handles video | AGENTS.md §7E |
| D3 | ComfyUI API JSON-payload example shows a placeholder dict `{"prompt": prompt_workflow}` but no actual workflow structure with the four nodes connected | The skill should ship a real workflow JSON in `references/` |
| D4 | BiRefNet has shipped natively in ComfyUI core since May 2026 (per ComfyUI.org 2026-05-15 release post). Skill says "BiRefNet or SegmentAnythingUltra" — current best practice is just BiRefNet native, with `Lucida` fine-tune as fallback for transparent objects | ComfyUI.org release notes 2026-05-15 |
| D5 | IC-Light `bcon` vs `fbc` distinction is correct but the skill doesn't say **when** to choose each (bcon = relight the cutout using a new background; fbc = relight foreground given both new background and existing foreground detail). Missing decision rule | IC-Light repo README |
| D6 | No mention of **VOID** (released by Netflix, 2026-05) for object removal from existing lifestyle images — useful for staging variations | ComfyUI.org 2026-05-15 release post |
| D7 | EU AI Act disclosure shown but not enforced — needs to be embedded in the actual PNG metadata via `exiftool` or ComfyUI's text-node-on-image path | EU AI Act Article 50 transparency obligation |

### OSS alternatives considered

| Alternative | Verdict |
|---|---|
| **RMBG-2.0 / INSPYRENET / BEN2 via ComfyUI-RMBG custom node** | Better background-removal accuracy than BiRefNet for fashion/glass/camouflage. Worth a fallback chain, not a primary replacement. **Adopt as fallback layer.** |
| **Lucida fine-tune (MIT, BiRefNet-based)** | Specialised for transparent / camouflaged / sticker / line-art cases — exactly the edge cases this project will hit. **Adopt as fallback.** |
| **Claid / remove.bg / Photoroom APIs** | Cloud-only, per-image cost. **Reject — breaks free constraint.** |
| **Clipdrop / Bria / Photoroom SaaS** | Same. **Reject.** |
| **FLUX.2 / SDXL / Stable Diffusion 3.5** | Larger, slower on 8GB. **Reject — RTX 4060 has 8GB; FLUX.1 Schnell still the right image base.** |
| **Wan 2.2 (1.3B, Apache-2.0)** | Removed 2026-08-30 — laptop cannot run locally. **Reject.** |
| **Stay on ComfyUI** | Yes. **Adopt.** |

### Required rewrite

- Section 1 (Pipeline): **Image leg only** (BiRefNet → FLUX.1 Schnell → IC-Light → 4×-UltraSharp). Video generation is out of scope — owned by `.agents/skills/veo-flow-ads/` (Google Flow / Veo 3.1).
- Section 2 (Models): pin versions — BiRefNet v2 (`comfyui/models/background_removal/`), FLUX.1-schnell-fp8 GGUF, IC-Light bcon/fbc decision rule.
- Section 3 (Nodes): include a downloadable workflow JSON in `references/bi-refnet-flux-iclight.json`. (Video workflow JSON is out of scope — see veo-flow-ads skill.)
- Section 4 (API): real ComfyUI `/prompt` payload with connected node graph, not a placeholder.
- Section 5 (Compliance): SynthID-aware — every output PNG carries an EU AI Act disclosure; ComfyUI text-overlay node can render it directly. Wire `exiftool` post-process as belt-and-braces.
- Section 6 (Variants): add **VOID** workflow for object-removal edits on lifestyle plates.
- Add `Verification`: run the workflow on `samples/raw-supplier-shoe.jpg`, output exists at `output/staged/`, JSON result includes `node_outputs.background_removal` and `node_outputs.iclight_relit`.

---

## 5. remotion-video-ads → veo-flow-ads (replacement)

**Verdict: REPLACE, not patch.** As of 2026-08-30, Ahmad is on Google AI Pro ($19.99/mo, 1,000 Flow credits/mo). That changes the math:

- Veo 3.1 Quality = 100 credits per 8s clip → **~10 Quality winners/month** at $19.99, or **~$2.00 per winner**.
- Veo 3.1 Fast = 20 credits per 8s clip → **~50 Fast generations/month** for ~$0.40 each.
- Veo 3.1 Lite = 10 credits per 8s clip → **~100 Lite generations/month** for ~$0.20 each.

Per-protocol volume math (AGENTS.md §7E): 40 creatives/month needed, ~5% hit rate → ~2 winners/month. **Pro's 10 Quality credits cover that with headroom.** Test phase runs on Veo 3.1 Lite (100 clips/month at $0.20/clip) and Veo 3.1 Fast (50 clips/month at $0.40/clip) on the same Pro subscription — Wan 2.2 is **not** in the pipeline because Ahmad's laptop cannot run it locally. Veo Quality replaces Remotion for the winner phase — native audio, cinematic quality, cheaper than the API equivalent at this volume.

### Why Veo over Remotion (re-evaluated)

| Axis | Remotion | Veo 3.1 Quality (Flow) |
|---|---|---|
| Marginal cost per clip | Free ≤3 employees, then $0.01/render ($100/mo min) | ~$2.00 per 8s Quality at Pro |
| Native audio (cinematic) | No — you mix in ffmpeg | **Yes** — Veo generates synced audio in-clip |
| Cinematic quality at $0–100 AOV | Loses to human by ~8% conv (per `reports/2026-08-30-leverage-and-tech.md`) | Unknown — closes the gap; **measure** |
| License for ad spend on this stack | Proprietary; 4-employee trigger breaks the budget | **Yes** — commercial use permitted; SynthID watermark carried; user owns output |
| Right tool for search phase (40+/month) | No — render time per clip ≈ minutes | No — same |
| Right tool for winner phase (2–10/month) | Yes | **Yes — and better, because of native audio** |

**Decision rule (codified):**
1. **Test phase** — Veo 3.1 Lite on Google Flow Pro (10 credits/clip, ~$0.20). ~100 clips/month capacity. Switch to Veo 3.1 Fast (20 credits/clip, ~$0.40) once a hook candidate emerges. Goal: find the hook.
2. **Winner phase** — Veo 3.1 Quality on Google Flow Pro (100 credits/clip, ~$2.00). Re-shoot the proven hook where native audio and cinematic quality raise hook rate on a concept already known to work. Budget: ≤10 Quality clips/month at €19.99 — leaves 500+ credits for Fast/Lite iteration within a winner.

### Critical defects in current remotion-video-ads (carry over)

| # | Issue | Source of truth |
|---|---|---|
| D1 | Composition 450 frames @ 30fps = 15s. PROTOCOL-02 wants sub-3s hook + 18s total. Same defect regardless of which tool renders it. | AGENTS.md §5 PROTOCOL-02 |
| D2 | Audio sync: 120–128 BPM backing track — no `scripts/` snippet for beat-marker extraction | Profile skill `media/songsee` exists for audio features |
| D3 | TikTok ad spec check missing (H.264 + AAC, 1080×1920, ≤30s, ≤287 Mbps) | TikTok Ads Creative Specs |
| D4 | EU AI Act disclosure must ride every output. Veo carries an **invisible SynthID watermark** plus optional visible label — align with the existing EU AI Act disclosure obligation, do NOT strip | Google Veo ToS + EU AI Act Article 50 |

### OSS alternatives considered (still no replacement)

| Alternative | Verdict |
|---|---|
| **Motion Canvas** (MIT) | Genuinely OSS. Fallback if Veo credits run out. **Defer.** |
| **VideoFlow** (Apache-2.0) | Newer, smaller ecosystem. **Defer.** |
| **Revideo / Midrender** | BSL 1.1. **Reject.** |
| **Editly / Manim** | Too thin / wrong tool. **Reject.** |
| **Shotstack / Creatomate** | Hosted SaaS. **Reject.** |
| **Veo 3.1 on Vertex AI API** | Per-second billing ($0.40–$4.80 per 8s). At Pro-equivalent volumes, $0.40/clip × 50 = $20/mo — same as Pro subscription but no quality ceiling. **Useful for campaigns past validation; not for the test/winner cycle.** |
| **Seedance** (free tier, commercial OK, no watermark) | Per the commercial-use guide above, "many commercial workflows use both: Seedance for high-volume routine content, Veo for specific high-stakes projects where quality justifies the cost." Worth a pilot alongside Veo Lite for the test phase — **deferred** (not on critical path; Veo Lite already covers volume on the existing Pro sub). |

### Replacement skill structure: `.agents/skills/veo-flow-ads/SKILL.md`

- **When to Use** — only after Veo Lite/Fast test phase has identified a top-decile hook; never for the 40+/month test phase (Veo Lite already covers that on the Pro sub at $0.20/clip).
- **Section 1: Flow credits budget**
  - Track current month, refresh date, remaining credits.
  - Hard ceiling: ≤10 Quality clips/month. Reserve ≥200 credits for Fast/Lite within-winner iteration.
  - Script: `scripts/flow_credit_check.py` reads Pro account, asserts "Quality cap not exceeded."
- **Section 2: Hook-to-Veo workflow**
  - Input: a winning hook from `campaigns/<product>.md` that scored ≥40% 3-sec view rate in Veo Lite/Fast test.
  - Output: 8s Veo 3.1 Quality clip at 1080×1920, H.264+AAC, SynthID-invisible + visible "AI-assisted" label.
  - Reference assets: the staged product image from `comfyui-product-staging` (PNG, transparent BG, EU disclosure burned in).
- **Section 3: Prompt patterns**
  - Subject first, then setting, then motion, then audio.
  - Example: *"Close-up of a hand pressing an electric pepper grinder over a wooden steak plate; steam rises from a medium-rare ribeye; warm restaurant lighting, shallow DOF, cinematic 24fps; sfx: grinder motor and peppercorn crack."*
- **Section 4: Disclosure obligations (dual)**
  - **SynthID** — already embedded by Google, do NOT strip.
  - **EU AI Act** — visible label overlay required; ComfyUI text-node can bake it in post-Flow, or `ffmpeg drawtext` after download.
  - **Platform** — TikTok/IG "AI content" toggle + YouTube "Altered or Synthetic" checkbox.
- **Section 5: License confirmation (required reading)**
  - Google Product Expert confirms commercial use permitted at Pro/Ultra tier (June 2026 thread).
  - **Cite the thread URL** in `campaigns/<product>.md` before any Veo clip runs in paid ads.
- **Pitfalls**
  - 8s native cap — longer videos stitch multiple clips (4 clips = 30s ≈ 400 credits on Quality).
  - Retries bill like production — Veo "lower priority" doesn't apply on Pro, every Fast generation is 20 credits whether it lands or not.
  - **Don't strip SynthID** — breaches ToS and aligns poorly with the disclosure we already owe.
- **Verification**
  - `scripts/flow_credit_check.py` exits 0 with remaining credits > 200.
  - Output file is 1080×1920 H.264+AAC MP4.
  - ffprobe shows audio track present.
  - EU AI Act overlay text present (string match against frame 0 extracted via ffmpeg).

### Open question to resolve

AGENTS.md §7E flagged "Veo-grade output closes the gap [vs human creative above $100 AOV] — unknown." With Pro now in hand, **run a head-to-head pilot** before any commitment: take one winning Veo Lite/Fast hook, re-shoot in Veo Quality, A/B against the Lite/Fast version on the same Meta ad set with $50 each. Decision criterion: ≥10% lift in 3-sec view rate justifies the $2.00/clip Quality spend; parity or worse stays on Fast for the winner phase too. Record results in `learnings/HEURISTICS.md` per PROTOCOL-03.

---

## Recommended action sequence

1. **Today** — rewrite all five SKILL.md frontmatter (version/author/license/platforms/metadata) so they conform to the in-repo skill-authoring standard and their descriptions fit the 60-char ceiling.
2. **Today** — patch `ecommerce-validator` with the CAC gate; replace `remotion-video-ads` with `veo-flow-ads` (this audit, §5).
3. **This week** — port `crawlee-scraper` from TypeScript to Python.
4. **This week** — rewrite `comfyui-product-staging` with BiRefNet-native, FLUX.1 Schnell image leg only, Lucida fallback, VOID object removal, EU AI Act metadata wire. (Video generation is owned by veo-flow-ads, not this skill.)
5. **This week** — rewrite `medusa-v2-storefront` to include Cloudflare Tunnel config, R2 loader, complete Stripe Express server-side, IOSS/OSS registration.
6. **Backlog** — add the missing scripts referenced by the skills: `crawlee_smoke.py`, `flow_credit_check.py` (already shipped), `run_veo_pilot.sh` (Lite/Fast vs Quality A/B harness), `stitch_veo_clips.py` (4×8s → 30s ad with crossfades).
7. **Pilot, before any commitment** — A/B test one winning Veo Lite/Fast hook against its Veo Quality re-shoot on Meta ($50 each). Decision criterion: ≥10% lift in 3-sec view rate justifies the $2.00/clip Quality spend; otherwise stay on Fast for winners too.

## Re-stack verdict

**Stack change in one place: Remotion → Veo 3.1 Quality (Google Flow).** Trigger: Ahmad is on Google AI Pro ($19.99/mo, 1,000 Flow credits). Veo's Quality tier fits the winner-phase volume (~10/month) at ~$2.00/clip with native audio, and Google's June 2026 Product Expert confirmation clears commercial use for paid ads. **Test phase uses Veo Lite + Fast on the same Pro subscription — Wan 2.2 / local GPU was removed 2026-08-30 because Ahmad's laptop cannot run it.** Remotion stays on disk only as a fallback (e.g. Motion Canvas / VideoFlow) if Veo credits prove insufficient at scale. Every other stack layer holds: Medusa v2 (MIT) over Saleor/Vendure/Spree, Crawlee over Scrapy/Apify, ComfyUI + BiRefNet + FLUX.1 Schnell over cloud alternatives for the image leg, self-hosted infra over Vercel/managed.