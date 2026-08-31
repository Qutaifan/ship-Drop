# Dropship Full Phased Roadmap

> **For Hermes:** Implement this roadmap phase-by-phase. Do not skip approval gates. Use Hermes Kanban for durable product lifecycle state and use `delegate_task` only for bounded parallel research inside a worker.

**Goal:** Build a safe, profitable, automation-ready dropshipping operating system by proving one evidence-backed product pipeline before enabling live ads, storefront publishing, fulfillment automation, or retention automation.

**Architecture:** Start with four MVP Hermes profiles and deterministic services. Expand to specialized bots only after the product lifecycle has passed real-world gates. Knowledge skills guide reasoning; executable connectors and deterministic services perform real work; Ahmad owns all live-risk approvals.

**Tech Stack:** Hermes profiles, Hermes Kanban, cron reconciliation jobs, local eCommerce-Skills guidance, audited `ecommerce-ops-suite` ideas only, deterministic Python/Node services, Medusa v2 + Next.js later, PostgreSQL/SQLite evidence store, CJdropshipping connector later, Meta/TikTok/Google API connectors later, Listmonk later, ComfyUI/Remotion later.

---

## Non-Negotiable Governance Rules

1. **Phase order is mandatory.** No live commercial action before its acceptance gate passes.
2. **One market per validation run.** US and EU logic must never be mixed in one candidate report.
3. **Skills are not integrations.** Markdown skills are reasoning guidance only.
4. **Every external write is gated.** Campaign publish, supplier order submission, price changes, public deployment, budget increases, and country launches require Ahmad approval.
5. **Deterministic math beats prompt math.** Margin, CPA, shipping, tax/duty, and state transitions must run through scripts/services with fixtures.
6. **Audit trail is mandatory.** Every candidate, decision, approval, quote, campaign draft, order state, and verdict must be recorded.
7. **No account-risk scraping.** Do not configure Agent-Reach login channels for Facebook, Instagram, or other ad-account-adjacent platforms.
8. **No artificial customs optimization.** Classification follows real product, origin, HS code, description, and declaration rules.

---

## MVP Agent Profiles

| Profile | Phase Introduced | Responsibility | Skills / Guidance | Tools / Services | Live-Risk Permissions |
|---|---:|---|---|---|---|
| `dropship-orchestrator` | 0 | Kanban board, product state machine, approval queue, audit log, profile dispatch | `ecommerce-growth-strategy`, `ecommerce-business-plan`, Hermes `background-systems` | Hermes Kanban, cronjob, file/evidence store | None by default |
| `dropship-research` | 1 | Product discovery, source collection, candidate reports, validation prep | `dropshipping-product-research`, `market-gap-analysis`, `ecommerce-keyword-research`, `product-review-analysis`, `competitor-price-analysis`, `ecommerce-competitor-analysis` | Web extract/search, Agent-Reach zero-config, Firecrawl self-hosted if audited, deterministic margin service | Read-only only |
| `dropship-launch` | 2 | Creative brief, product page draft, campaign draft, compliance checklist | `ecommerce-ppc-strategy-planner`, `product-description-generator`, `ecommerce-video-marketing`, `shoppable-video`, `ecommerce-landing-page`, `conversion-rate-optimization` | ComfyUI later, Remotion later, Next.js draft generator later | Draft-only |
| `dropship-operations` | 3 | Sandbox commerce flow, order-state design, ad metrics monitoring, fulfillment safety, learning reports | `supply-chain-optimization-shopify`, `ecommerce-shipping-rates`, `ecommerce-returns-management`, `warehouse-optimization`, `ecommerce-email-marketing-builder`, `ecommerce-customer-retention` | Medusa connector, CJ connector, Stripe test mode, Listmonk later, ad metrics connectors | Read-only/test-mode unless approved |

---

## Future Expanded Agent Fleet

Only split the MVP profiles after Phase 4 produces at least one `KILL | ITERATE | SCALE_CANDIDATE` verdict with clean logs.

| Future Agent | Split From | Trigger to Create | Responsibility |
|---|---|---|---|
| `dropship-scout` | research | Research queue exceeds 20 candidates/week | Always-on discovery and trend scans |
| `dropship-validator` | research | Multiple candidate reports/week need separate QA | Deterministic validation and evidence QA |
| `dropship-creative` | launch | Creative throughput becomes bottleneck | Hook briefs, image/video generation, Remotion renders |
| `dropship-storefront` | launch/operations | Staging deployments happen weekly | Medusa products, Next.js pages, analytics tags |
| `dropship-fulfillment` | operations | More than 5 live fulfilled orders | CJ submission, tracking, exceptions, refund handoff |
| `dropship-ads` | operations | Paid test is running | Metrics pull, recommendations, emergency pause only |
| `dropship-retention` | operations | 100+ subscribers or 20+ customers | Consent-safe Listmonk flows and lifecycle messaging |
| `dropship-learning` | orchestrator/operations | 3+ campaign verdicts exist | Calibration, root-cause tagging, heuristic lifecycle |

---

## Product State Machine

```text
DISCOVERED
→ EVIDENCE_PENDING
→ VALIDATION_READY
→ FOUNDER_REVIEW
→ APPROVED_FOR_CREATIVE
→ CREATIVE_READY
→ APPROVED_FOR_DRAFT_STORE
→ STORE_DRAFT_READY
→ APPROVED_FOR_TEST
→ TESTING
→ KILL | ITERATE | SCALE_CANDIDATE
→ FOUNDER_SCALE_APPROVAL
→ SCALED
```

### State Ownership

| State | Owner | Required Evidence | Exit Gate |
|---|---|---|---|
| `DISCOVERED` | research | product idea + source URL | basic source exists |
| `EVIDENCE_PENDING` | research | competitor, price, supplier, demand evidence in progress | evidence JSON complete |
| `VALIDATION_READY` | research | candidate report generated | orchestrator validates schema |
| `FOUNDER_REVIEW` | orchestrator | complete report + recommendation | Ahmad approval/rejection |
| `APPROVED_FOR_CREATIVE` | launch | approval record | launch pack generation starts |
| `CREATIVE_READY` | launch | 3 hooks + PDP copy + campaign draft | Ahmad creative approval |
| `APPROVED_FOR_DRAFT_STORE` | launch | creative approval | staging store work starts |
| `STORE_DRAFT_READY` | launch/operations | staged page + test checkout | Ahmad test approval |
| `APPROVED_FOR_TEST` | orchestrator | budget cap + platform + campaign draft | Ahmad live launch approval |
| `TESTING` | operations | campaign metrics + spend cap | verdict report |
| `KILL` | operations/learning | losing evidence | learning entry written |
| `ITERATE` | launch/operations | partial signal | revised test approved |
| `SCALE_CANDIDATE` | operations/learning | profitable evidence | founder scale review |
| `FOUNDER_SCALE_APPROVAL` | orchestrator | scale proposal | Ahmad approval |
| `SCALED` | operations | scale authorization | expanded operations controls |

---

# Phase 0 — Evidence and Contract Audit

## Objective
Freeze the operating contract, dependencies, market configuration, and security boundaries before any automation is installed or trusted.

## Agents Active
- `dropship-orchestrator`

## Skills / References
- Hermes `background-systems`
- Hermes `cli-reference`
- Nexscope README and selected `SKILL.md` files as inventory only
- `ecommerce-ops-suite` README as inventory only

## Deliverables

| Deliverable | Path | Owner |
|---|---|---|
| Operating contract | `docs/operating-contract.md` | orchestrator |
| Dependency manifest | `docs/dependency-manifest.md` | orchestrator |
| Market config schema | `schemas/market-config.schema.json` | orchestrator |
| Candidate schema | `schemas/candidate.schema.json` | orchestrator |
| Evidence schema | `schemas/evidence.schema.json` | orchestrator |
| Approval policy | `docs/approval-policy.md` | orchestrator |
| Secret exposure checklist | `docs/security/credential-audit.md` | orchestrator |

## Required Decisions

### Market Selection
Choose exactly one pilot:

```yaml
# Option A: US pilot
market:
  primary_country: US
  currency: USD
  tax_model: destination_sales_tax
  fulfillment_region: US
  target_delivery_days: 3-8
  returns_region: US
  advertising_region: US
```

```yaml
# Option B: EU pilot
market:
  primary_region: EU
  launch_countries: [DE, FR, NL]
  currency: EUR
  vat_model: destination_vat
  ioss_required: conditional
  fulfillment_region: EU
  ai_disclosure_policy: article_50_brand_policy
```

## Dependency Audit Checklist

| Item | Required Action | Pass Criteria |
|---|---|---|
| Nexscope eCommerce-Skills | Pin commit, inspect license, enumerate selected skills | commit hash + license recorded |
| ecommerce-ops-suite | Pin commit, inspect license, identify paid/duplicate components | marked experimental, not critical path |
| Hermes version | Verify `hermes --help`, `hermes kanban --help`, `hermes profile --help`, `hermes cron --help` | commands confirmed against installed version |
| CJdropshipping | Verify account/API availability and docs | no live order capability enabled |
| Meta/TikTok/Google APIs | Verify eligibility only | no write tokens required for Phase 1 |
| Credentials | Search repo/docs for exposed tokens | none found or rotated |

## Exit Criteria
- One market selected.
- Dependencies pinned.
- All selected skills classified as guidance vs executable.
- No exposed credentials remain valid.
- Approval policy blocks all live-risk actions.
- Kanban board strategy documented.

## Stop Conditions
- Any live credential appears in repo or docs.
- Pilot market remains undecided.
- A required repository license is incompatible or unclear.

---

# Phase 1 — Product Research Report Only

## Objective
Produce reproducible, evidence-backed candidate reports without creating stores, launching ads, submitting supplier orders, or sending customer messages.

## Agents Active
- `dropship-orchestrator`
- `dropship-research`

## Skills / Guidance
- `dropshipping-product-research`
- `market-gap-analysis`
- `tiktok-shop-product-research` only if TikTok is relevant to selected market
- `tiktok-shop-trending-products` only as guidance, not guaranteed live data
- `ecommerce-keyword-research`
- `competitor-price-analysis`
- `ecommerce-competitor-analysis`
- `product-review-analysis`
- `profit-margin-calculator-shopify` as guidance only
- `competitive-pricing-strategy`
- `price-optimization-tool`
- `cross-border-ecommerce` only for market-specific compliance framing

## Tools / Services
- Web search/extract
- Agent-Reach zero-config channels only
- Firecrawl self-hosted only after audit; merchant/supplier pages only
- Deterministic margin calculator
- JSON schema validator
- Evidence store

## Candidate Report Schema

Each report must include:

```yaml
candidate_id: string
product_name: string
market_config_id: string
source_summary: string
competitor_evidence:
  - source_url: string
    competitor_name: string
    product_url: string
    observed_price: number
    currency: string
    extraction_method: string
    confidence: low|medium|high
supplier_evidence:
  - supplier_name: string
    product_url: string
    quoted_product_cost: number
    quoted_shipping_cost: number|null
    warehouse_country: string|null
    delivery_days_min: number|null
    delivery_days_max: number|null
    hs_code: string|null
    origin_country: string|null
    landed_cost_confidence: low|medium|high
demand_evidence:
  - source: string
    signal_type: search|video|review|ad|trend
    metric_name: string
    metric_value: string|number
    confidence: low|medium|high
unit_economics:
  gross_selling_price: number
  net_revenue: number
  contribution_before_ads: number
  break_even_cpa: number
  target_cpa: number
  safety_factor: number
  expected_profit_per_order: number
compliance_unknowns:
  - string
recommendation: reject|hold|founder_review
rationale: string
```

## Deterministic Margin Formula

```text
Net Revenue
= Gross Selling Price
- VAT or Sales Tax Liability
- Discounts
- Refund Allowance

Contribution Before Ads
= Net Revenue
- Product Cost
- Shipping
- Duty
- Payment Fees
- Packaging
- Variable Support Cost
- Return Allowance

Break-even CPA
= Contribution Before Ads

Target CPA
= Break-even CPA × Safety Factor

Expected Profit Per Order
= Contribution Before Ads - Expected CPA
```

Default safety factor: configurable `0.60–0.75`.

## Workflow

1. Orchestrator creates up to `candidate_limit: 5` Kanban tasks.
2. Research worker collects public evidence only.
3. Research worker saves raw evidence JSON before writing analysis.
4. Margin calculator runs from evidence JSON.
5. Candidate report is generated from saved evidence, not memory.
6. Orchestrator validates schema.
7. Orchestrator routes only `founder_review` candidates to Ahmad.

## Exit Criteria
- At least one candidate report can be regenerated from raw evidence.
- All estimates are marked.
- Market config is consistent throughout the report.
- No live external write permissions were used.
- No product is marked `founder_review` with low-confidence landed cost if market requires customs/import confidence.

---

# Phase 2 — Draft Launch Pack

## Objective
For one Ahmad-approved candidate, generate a non-public launch pack: creative strategy, product page copy, campaign draft, compliance checklist, and tracking plan.

## Agents Active
- `dropship-orchestrator`
- `dropship-launch`
- `dropship-research` for evidence clarification only

## Skills / Guidance
- `ecommerce-ppc-strategy-planner`
- `tiktok-shop-ads` if TikTok is selected
- `ecommerce-video-marketing`
- `shoppable-video`
- `product-description-generator`
- `ecommerce-landing-page`
- `conversion-rate-optimization`
- `product-differentiation-shopify` as DTC positioning guidance, not Shopify execution

## Deliverables

| Deliverable | Path | Owner |
|---|---|---|
| Launch pack | `launch-packs/<candidate_id>/launch-pack.md` | launch |
| Creative briefs | `launch-packs/<candidate_id>/creative-briefs.md` | launch |
| Product page draft | `launch-packs/<candidate_id>/product-page.md` | launch |
| Campaign draft | `launch-packs/<candidate_id>/campaign-draft.md` | launch |
| Compliance checklist | `launch-packs/<candidate_id>/compliance-checklist.md` | launch |
| Tracking plan | `launch-packs/<candidate_id>/tracking-plan.md` | launch |

## Creative Requirements

Produce exactly three test hooks:

1. **Problem-Oriented:** painful daily friction → product relief.
2. **Transformation:** before/after visible change.
3. **Aspirational Lifestyle:** premium environment, brand desire.

For each hook:
- 9:16 script
- first 3-second hook
- shot list
- voiceover/caption text
- UGC vs polished direction
- proof element needed
- claim risk notes
- AI-disclosure metadata requirement

## Campaign Draft Requirements

No live campaign creation. Draft only:
- platform
- objective
- audience hypothesis
- daily budget cap proposal
- attribution window
- minimum sample floor
- kill/iterate/scale candidate rules
- expected CTR/CVR/CPA/contribution model
- approval checklist

## Exit Criteria
- Ahmad approves or rejects the launch pack.
- Every claim in the product page draft maps to evidence or is marked unverified.
- No generated creative is published.
- No live campaign is created.

---

# Phase 3 — Storefront Staging

## Objective
Build a staged commerce flow for one approved launch pack and verify sandbox checkout, analytics, shipping quote capture, refund path, and event logging.

## Agents Active
- `dropship-orchestrator`
- `dropship-launch`
- `dropship-operations`

## Native Capabilities to Build / Verify

Do not rely on Shopify skills as Medusa tools. Build native capabilities:

| Capability | Purpose |
|---|---|
| `medusa-product-importer` | Create/update draft product in Medusa |
| `medusa-price-manager` | Apply selected market price and currency |
| `medusa-order-reader` | Read sandbox orders |
| `medusa-fulfillment-updater` | Write fulfillment state in sandbox/test mode |
| `nextjs-landing-page-generator` | Generate staged landing page |
| `merchant-center-feed-exporter` | Export feed later; not required for Phase 3 exit |
| `stripe-checkout-handler` | Verify Stripe test-mode checkout events |
| `analytics-event-validator` | Confirm Umami/analytics events |

## Deliverables

| Deliverable | Path / System | Owner |
|---|---|---|
| Draft Medusa product | Medusa staging | launch |
| Staged Next.js page | staging URL/local preview | launch |
| Stripe test checkout proof | `reports/staging/<candidate_id>/stripe-test.md` | operations |
| Analytics event proof | `reports/staging/<candidate_id>/analytics-events.md` | operations |
| Refund path proof | `reports/staging/<candidate_id>/refund-test.md` | operations |
| Staging QA report | `reports/staging/<candidate_id>/qa-report.md` | orchestrator |

## Exit Criteria
- Sandbox order created end-to-end.
- Stripe test payment captured and refunded in test mode.
- Order appears in Medusa staging.
- Analytics events recorded for product view, add to cart, checkout started, purchase.
- No production domain or public campaign points to the page.

---

# Phase 4 — Controlled Micro-Test

## Objective
Launch one product in one market on one paid platform under a fixed budget with founder approval and automated emergency pause only.

## Agents Active
- `dropship-orchestrator`
- `dropship-operations`
- `dropship-launch` for creative iteration only

## Live-Risk Gate

Ahmad must approve:
- product
- market
- platform
- budget cap
- campaign draft
- landing page URL
- tracking plan
- refund/fulfillment readiness
- kill/iterate/scale candidate criteria

## Automation Allowed

| Action | Automation Level |
|---|---|
| Pull campaign metrics | automatic |
| Produce recommendation | automatic |
| Pause on hard global spend cap breach | automatic |
| Create draft campaign | automatic only if API supports draft mode |
| Publish first campaign | Ahmad approval required |
| Increase daily budget | Ahmad approval required |
| Change targeting | Ahmad approval required |
| Change price | Ahmad approval required |
| Launch new country | Ahmad approval required |

## Required Metrics Context

No verdict without:
- attribution window
- minimum spend floor
- minimum click floor
- conversion delay window
- refund-adjusted revenue policy
- contribution margin model
- sample-size caveat

## Exit Criteria
A written verdict exists:
- `KILL`
- `ITERATE`
- `SCALE_CANDIDATE`

The verdict must include:
- spend
- clicks
- orders
- CPA
- contribution before ads
- expected profit per order
- actual/estimated refund allowance
- recommendation
- confidence level

---

# Phase 5 — Limited Fulfillment

## Objective
Process first live orders safely with human approval and duplicate-order protection.

## Agents Active
- `dropship-orchestrator`
- `dropship-operations`

## Order State Machine

```text
PAID
→ FULFILLMENT_REVIEW
→ STOCK_CONFIRMED
→ SUBMISSION_PENDING
→ SUBMITTED
→ SUPPLIER_ACCEPTED
→ SHIPPED
→ DELIVERED
```

## Exception States

```text
OUT_OF_STOCK
PRICE_CHANGED
ADDRESS_INVALID
DUPLICATE_BLOCKED
SUPPLIER_REJECTED
TRACKING_STALE
REFUND_REQUIRED
HUMAN_REVIEW
```

## Idempotency Rule

Every supplier submission uses:

```text
cj:{store_order_id}:{fulfillment_version}
```

The connector must reject duplicate submission attempts with the same idempotency key.

## First-Five-Order Policy

For orders 1–5:
- read order automatically
- quote supplier cost automatically
- check stock automatically
- prepare supplier submission automatically
- Ahmad approves before actual CJ submission
- record quoted vs charged cost
- record estimated vs actual delivery
- record customer communication timestamps

## Exit Criteria
- Five live orders fulfilled without duplicate submission.
- No hidden supplier cost variance over approved tolerance.
- Tracking synchronization works.
- Refund path is verified for at least one test/sandbox order and documented for live orders.

---

# Phase 6 — Learning and Calibration

## Objective
Convert real test outcomes into reusable, falsifiable heuristics that improve the next product cycle.

## Agents Active
- `dropship-orchestrator`
- `dropship-operations`
- future split candidate: `dropship-learning`

## Inputs
- candidate report
- launch pack
- campaign metrics
- order/fulfillment outcomes
- refund/return evidence
- customer/review feedback if available

## Prediction Ledger

Track predicted vs actual:
- CTR
- CVR
- CPA
- contribution before ads
- expected profit per order
- refund rate
- delivery days
- return/refund cause

## Root Cause Taxonomy

Each verdict must isolate exactly one primary root cause:
- product selection
- creative
- landing page
- margin math
- supply chain
- targeting
- compliance/friction
- tracking/instrumentation

## Heuristic Lifecycle

```text
PROVISIONAL → SUPPORTED → CONTESTED → RETIRED
```

Rules:
- New insight starts as `PROVISIONAL`.
- Upgrade to `SUPPORTED` after `n ≥ 3` consistent observations.
- Move to `CONTESTED` when evidence conflicts.
- Move to `RETIRED` when cleanly falsified.
- Never delete rows.

## Exit Criteria
- Campaign verdict scored.
- Signed error % calculated for all tracked predictions.
- One primary root cause assigned.
- At least one heuristic updated or a “no new heuristic” rationale recorded.
- Next Phase 1 research cycle consumes the updated ledger.

---

# Phase 7 — Controlled Scaling

## Objective
Scale only after a product becomes a `SCALE_CANDIDATE` and Ahmad approves the scale proposal.

## Agents Active
- `dropship-orchestrator`
- `dropship-operations`
- split agents if justified: `dropship-ads`, `dropship-fulfillment`, `dropship-retention`

## Scale Preconditions

- contribution-positive after ad spend
- tracking reliable
- supplier capacity verified
- return/refund rate within tolerance
- delivery time within promise
- customer support workload manageable
- no unresolved compliance blocker
- backup/restore tested
- hard spend cap configured

## Scaling Controls

| Control | Requirement |
|---|---|
| Budget increase | Ahmad approval per increase |
| Market expansion | separate market config and approval |
| Creative expansion | approved claims only |
| Supplier expansion | quote + contract check |
| Inventory pre-stock | cash-flow model required |
| Retention flows | consent and deliverability verified |

## Exit Criteria
- Scale decision approved.
- Spend increases logged.
- Supplier capacity monitored.
- Retention/fulfillment/ads can be split into dedicated agents if queue pressure justifies it.

---

# Phase 8 — Full Autonomous Operating Model

## Objective
Promote the MVP profiles into the larger autonomous fleet only after safety, profitability, and operational contracts are proven.

## Expanded Agents

| Agent | Purpose | Activation Condition |
|---|---|---|
| `dropship-scout` | continuous product sourcing | 20+ candidates/week |
| `dropship-validator` | strict validation gate | 5+ candidate reports/week |
| `dropship-creative` | creative production | 10+ creative assets/week |
| `dropship-storefront` | Medusa/Next.js operations | multiple products staged/live |
| `dropship-fulfillment` | supplier/order automation | 5 clean live orders passed |
| `dropship-ads` | campaign monitoring | paid campaigns running daily |
| `dropship-retention` | email/customer lifecycle | consent system + list volume exists |
| `dropship-learning` | calibration ledger | 3+ verdicts logged |
| `dropship-orchestrator` | executive control | always active |

## Autonomous Boundaries

Even in Phase 8, the following remain approval-gated:
- new supplier contracts
- new countries
- budget increases above configured threshold
- campaign publication where spend starts immediately
- product claims that create regulatory risk
- customer refunds above threshold
- legal/tax/compliance representations

## Exit Criteria
- Fleet runs with auditable state transitions.
- Failure recovery works after process restart.
- Daily summaries are accurate and sourced.
- Human approval queue is concise and actionable.
- Profitability reports reconcile campaign, order, and payment data.

---

## Infrastructure Reliability Requirements

Before live orders or scaling:

| Area | Requirement |
|---|---|
| Database | daily encrypted PostgreSQL backup |
| Kanban | daily SQLite/board backup |
| Off-device backup | enabled and restore-tested |
| Host recovery | Docker restart policies and boot recovery |
| Monitoring | Uptime Kuma checks for storefront, Medusa, tunnel, database, worker queues |
| Disk | disk usage alerts |
| Secrets | separate database users, no secrets in repo, rotation procedure |
| GPU worker | optional only; campaign launch must not depend on ComfyUI being online |
| Audit log | append-only or tamper-evident export |

---

## Cost Model Correction

Do not describe the stack as “free.” Use this language:

**Software-first, zero-subscription where possible.**

Known unavoidable costs:
- ad spend
- payment processing
- domain
- email delivery at scale or SMTP limitations
- supplier fulfillment/COGS
- refunds/returns
- compliance/accounting support if needed
- potential API or data access costs
- hardware, power, backup, and operations time

---

## Phase Review Template

Every phase review should answer:

```markdown
# Phase X Review

## Completed
- ...

## Evidence
- path/link: ...

## Acceptance Criteria
| Criterion | Status | Evidence |
|---|---|---|

## Risks Remaining
- ...

## Approval Needed
- approve/reject/hold: ...

## Next Phase Recommendation
- proceed / repeat / stop
```

---

## Immediate Next Step

Start with **Phase 0 only**:

1. Confirm the pilot market: US or EU.
2. Create `docs/operating-contract.md`.
3. Create schemas for market, evidence, and candidate reports.
4. Pin and audit the selected skill/tool dependencies.
5. Confirm no credentials are exposed or active in project files.

Only after Phase 0 passes should Phase 1 research begin.
