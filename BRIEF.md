# Dropshiping — Full Project Brief

**Prepared 2026-08-30 · Status: pre-launch, zero products validated, zero spend committed**

---

## 1. What this project is

An EU-first dropshipping operation run by an autonomous agent persona (**Hermes-Ecom**)
against a file-based workflow. Products are screened, costed, and gated by explicit
rules; nothing advances on judgement alone. The workspace is the source of truth and
validators enforce it.

**Governing constraint set by the owner: free and open-source only.** Every unavoidable
cost is named rather than buried.

## 2. Where it actually stands

| | |
|---|---|
| Products validated (PASS) | **0** |
| Products rejected with evidence | 3 |
| Products pending | 1 (electric pepper grinder) |
| Ad spend committed | **€0** |
| Storefront deployed | No — scaffolded only |
| Blocking items | 2 accounts, both requiring the owner |

**Nothing has been wasted.** Four candidates were killed before any budget was
committed, each on hard evidence. That is the workflow working as designed.

---

## 3. The pipeline

```
products/        PROTOCOL-01  screen, cost, gate      → PASS / FAIL
creative-briefs/ PROTOCOL-02  3+1 brief               (requires PASS)
campaigns/       live tracking vs numeric hypothesis
reports/         rollups and research
learnings/       PROTOCOL-03  retrospective → HEURISTICS.md
```

Each stage gates the next and the gates are enforced, not conventional. A brief cannot
exist without a PASS. A campaign cannot exist without a brief. A closed campaign must
produce a retrospective.

### Validation

| Script | Purpose |
|---|---|
| `validate_workspace.py` | Pipeline integrity, margin arithmetic, gate compliance |
| `validate_infra.py` | Compose structure, env coverage, AGENTS/prompt parity |
| `verify_sweep.py` | Recomputes a research sweep's metrics from its own raw data |
| `selftest.py` | 24 deliberate defects — proves the validators fail correctly |
| `profitability.py` | Business-level CAC gate |
| `ad_library.py`, `demand_screen.py`, `margin_solver.py`, `generate_brief.py`, `learning_loop.py` | Pipeline stages |

All stdlib-only except PyYAML. Full flow runs end-to-end and halts precisely at the
two real blockers.

---

## 4. Decisions and why

### Stack — free/OSS, self-hosted

Medusa v2 (MIT) + Next.js, PostgreSQL, Valkey, Docker Compose on the Ubuntu ThinkBook,
published through Cloudflare Tunnel. Cloudflare free plan for DNS/CDN/WAF, R2 for
object storage, Umami for cookieless analytics, Listmonk for email.

**Vercel Hobby is off-limits** — its free tier forbids commercial use; a live store
there is a terms violation and a takedown risk.

### Market — EU, and not by preference

The Meta Ad Library API returns **commercial ads for EU/UK only** (`ad_type=ALL` works
solely inside the EU/UK because the DSA compels the disclosure). Everywhere else it
returns political ads only. **This decides the market**: EU-first is the only path where
the competitor gate can be automated at all.

### Supplier — CJdropshipping

Free membership, per-fulfilment charges only, EU warehouses in Germany and Poland.
Zendrop rejected (free tier is browse-only; fulfilment needs $49/mo). Spocket and
Droppery rejected as paid subscriptions.

### Research tooling

- **Agent-Reach** (MIT) — YouTube, web, RSS. Zero-config channels only.
- **Firecrawl** self-hosted (AGPL-3.0) for merchant sites and supplier catalogues.
- **WebMCP** deferred — it exposes our storefront to agents, worthless before traffic.

**Hard rule: never point automation at Meta Ad Library or TikTok Creative Center, and
never configure Agent-Reach's Facebook/Instagram login channels.** The account at risk
is the one running the ad spend. An ad-account ban is existential, not inconvenient.

### Creative — local for volume, Veo for winners

Creative hit rate is ~5%. Volume finds winners; quality scales them.
- **Test phase**: local Wan on the RTX 4060. Unlimited, free. Ship 40+/month.
- **Winner phase**: re-shoot the proven hook in Google Flow / Veo.

You pay only for concepts that already earned it.

---

## 5. What went wrong, and what it cost to find out

Every item below was caught before spend. This section exists because the failures are
more instructive than the decisions.

| # | Error | How it surfaced | Consequence if missed |
|---|---|---|---|
| 1 | **True Margin Matrix omitted VAT** | Recomputation during supplier research | Overstated EU margin by 21%; flipped a FAIL to a PASS |
| 2 | **EU €150 duty exemption already gone** (ended 1 Jul 2026, replaced by €3/customs item) | CJ customs research | Unmodelled per-order cost on every China-origin parcel |
| 3 | **Sweep reported 9 of 10 skeptic ratios wrong**, every error optimistic | `verify_sweep.py` recomputation | Three candidates selected on numbers that were not real |
| 4 | **Self-test harness truncated files before reading them** | 9/23 catch rate looked wrong | 14 test cases passing vacuously against blank files |
| 5 | **Demo-burden metric is unstable across runs** (12% / 16% / 24% for one product) | Independent re-runs | Ranking noise as if it were signal |
| 6 | **`demand_screen.py` detected instability then returned PASS anyway** | Full-flow run | Verdicts issued from numbers the script itself flagged as noise |
| 7 | **`temu_api.py` fired live API calls on `--help`** | Full-flow run | Also revealed Temu has **no V3 product permission** — the integration does not work |
| 8 | **PROTOCOL-01 had no CAC gate** | Profitability validation | Products could pass every gate and still lose money on every advertised sale |
| 9 | **My own "not profitable" verdict was overstated** | Wider benchmark reading | Rested on one channel's median; corrected to channel-dependent |

**The pattern worth keeping**: a validator reporting "clean" means nothing until it is
proven to fail on bad input. Item 4 was caught only because the negative suite existed.

---

## 6. The economics

### Unit level

```
Net Margin = (Retail / (1 + VAT)) − (Product Cost + Shipping + Import Duty) − (0.03 × Retail)
```

- Landed cost must be **≤ 20.3% of VAT-inclusive retail** (the 3x-COGS gate binds at
  every price point).
- Below **€18.51** retail, the >€15 net gate is unreachable at *any* cost.

### Business level — the gate that was missing

| | |
|---|---|
| Net margin at €34.90 retail | €21.21 |
| Breakeven ROAS | **1.65x** |
| TikTok median ROAS | 1.51x → loss |
| All-paid ecommerce implied ROAS | 2.64x → profit |

Channel-dependent, not doomed. But at €34.90 it fails either way: median CPA (€21.48)
consumes the entire margin.

### The viable window: €62–93 gross retail

- **Floor €62** — below it, CAC eats the margin.
- **Ceiling €93 (~$100 AOV)** — above it, AI-generated creative underperforms human
  creative (ROAS 3.1x vs 3.7x, conversion −8%), forfeiting the local-GPU advantage this
  project depends on.

Two structural advantages in direct tension. The window is where both hold.

### The capital nobody budgeted

| Win rate | Lean (€150/test) | Realistic (€300/test) |
|---|---|---|
| 5% | €3,000 | €6,000 |
| 10% | €1,500 | €3,000 |
| 20% | €750 | €1,500 |

**The free/OSS stack saves ~€30–50/month in SaaS. It does nothing about the €1,500–6,000
of ad spend needed to find one winner.** That is the real capital requirement.

---

## 7. Rejected candidates

| Candidate | Why |
|---|---|
| Hard water shower filter | Criterion 3 — 76% of top YouTube results are skeptic-framed, median 4m41. Benefit needs a chemical test to demonstrate; no 3-second silent hook carries it |
| Folding laundry basket | CJ freight lands it at $11.27–$31.76 vs a €9.10 ceiling. Also an IKEA staple → Criterion 6 fails, capping price |
| Bamboo drawer organizers | Zero advertisers in the DE ad dataset; 109 median YouTube views. No demonstrated demand |
| Cable management box | 9 advertisers but **0 ads aged 30+ days** — all started within an 11-day window under throwaway page names. Mass-testing, not proven profitability |

**Electric pepper grinder** remains PENDING: strong demo-burden result, but fails the
CAC gate at €34.90 and carries WEEE + battery registration (a fixed cost that sets a
minimum viable volume).

---

## 8. Blockers — both require the owner

1. **Meta developer app + identity verification.** Gates the competitor check. Takes
   days; start before it is needed.
2. **EU-warehouse stock.** CJ's China-origin freight breaks every candidate's landed
   cost. Either CJ EU-warehouse SKUs, or Temu V3 product-API permission (currently
   denied for this app_key).

Neither is a research task. Both are account creation.

### Secondary

- `metapi-competitor-check.json` has **undocumented provenance** — its field names are
  not the official Graph API's. Pin down what it is before a verdict rests on it.
- **Wan 2.2 1.3B is unproven on this Forge Neo fork** (2.2 TI2V-5B already failed on a
  VAE mismatch). Test before building a creative pipeline on it.
- Google Flow **credits-per-generation is unpublished** — check in-account before
  subscribing. If Pro's 1,000 credits buy under ~40 generations, it cannot serve testing.
- Flow **commercial-use terms are contradictory across sources**. Read the ToS for the
  specific tier before running paid ads on Veo output.

---

## 9. What to do next, in order

1. **Create the Meta developer app** — longest lead time, blocks the most.
2. **Find EU-warehouse SKUs on CJ in the €62–93 band.** This replaces all prior
   candidate hunting; the old €30–45 band cannot support paid acquisition.
3. **Test Wan 2.2 1.3B on Forge Neo.** Confirms or kills the creative-volume strategy.
4. **Decide the testing budget deliberately** — €1,500–6,000, as the cost of the
   experiment rather than overhead to minimise.
5. Only then: run PROTOCOL-01 on real candidates with real costs.

---

## 10. Honest assessment

The machinery is sound and well-tested. The economics are **thin but not impossible**,
and they only work in a narrow price band with above-median advertising performance.

The genuine edge is **not** the free software stack — it is a local GPU that breaks the
industry link between creative volume and production cost. Everyone else pays roughly
one new ad per $3,000 of monthly spend. This project pays electricity. At a 5% hit rate,
40 creatives a month gives a 79% chance of a winner; five gives 18%.

**That advantage only pays off if the volume is actually produced.** If creative output
stays at five a month, the free stack is irrelevant and the economics do not work.

The decision in front of the owner is not technical. It is whether to commit
€1,500–6,000 to a search process whose machinery is now built and validated.
