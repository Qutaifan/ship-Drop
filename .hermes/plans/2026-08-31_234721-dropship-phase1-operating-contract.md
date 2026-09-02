# Dropship Phase 1 Operating Contract Implementation Plan

> **For Hermes:** Use governed-repo-workflow and Hermes Kanban for implementation. Do not execute live spend, supplier submissions, storefront publishing, or customer messaging during Phase 1.

**Goal:** Replace the oversized autonomous fleet proposal with a safe, evidence-only MVP that produces reproducible product candidate reports before any live commercial action.

**Architecture:** Four Hermes profiles coordinate through a durable Kanban board and a deterministic product state machine. Markdown skills provide reasoning guidance only; executable capabilities are isolated as audited connectors/services; live-risk actions require Ahmad approval.

**Tech Stack:** Hermes profiles, Hermes Kanban, cron reconciliation jobs, local Markdown/Nexscope skills, project scripts, SQLite/PostgreSQL evidence store later, CJ connector later, Meta/TikTok APIs later, Medusa/Next.js only after staged launch approval.

---

## Executive Correction

The previous nine-agent plan is a valid target architecture, but it is not safe as Phase 1. Phase 1 must prove one repeatable research-to-validation report loop before automating storefronts, ads, fulfillment, retention, or compliance decisions.

**Phase 1 rule:** agents may research, calculate, draft, and recommend. They may not publish, spend, submit supplier orders, change prices, or launch countries.

---

## Operating Contract v0.1

```yaml
project: dropship
phase: evidence_only
market:
  status: MUST_CHOOSE_ONE_BEFORE_VALIDATION
  allowed_options:
    us:
      primary_country: US
      currency: USD
      tax_model: destination_sales_tax
      fulfillment_region: US
      target_delivery_days: 3-8
      returns_region: US
      advertising_region: US
    eu:
      primary_region: EU
      launch_countries: [DE, FR, NL]
      currency: EUR
      vat_model: destination_vat
      ioss_required: conditional
      fulfillment_region: EU
      ai_disclosure_policy: article_50_brand_policy
supplier: CJdropshipping
storefront: undecided
live_spend_allowed: false
live_order_submission_allowed: false
live_storefront_publish_allowed: false
live_customer_messaging_allowed: false
approval_owner: Ahmad
candidate_limit: 5
profiles:
  - dropship-orchestrator
  - dropship-research
  - dropship-launch
  - dropship-operations
risk_policy:
  founder_approval_required_for:
    - first_campaign_publish
    - any_budget_increase
    - supplier_order_submission
    - price_change
    - new_country_launch
    - public_storefront_publish
  automatic_allowed:
    - read_public_data
    - calculate_margins
    - draft_campaigns
    - draft_product_pages
    - generate_reports
    - emergency_pause_on_hard_spend_cap_only
```

---

## Agent / Bot MVP Fleet

| Profile | Type | Phase 1 Responsibility | Explicitly Not Allowed |
|---|---|---|---|
| `dropship-orchestrator` | Durable coordinator | Product state machine, Kanban routing, approval queue, audit log | Live API writes, ad publication, supplier submission |
| `dropship-research` | Evidence worker | Product discovery, competitor evidence, price snapshots, candidate reports | Treating skills as live data sources, scraping login-only channels |
| `dropship-launch` | Drafting worker | Creative briefs, product page drafts, campaign drafts, compliance checklist | Public storefront deploys, live campaign creation |
| `dropship-operations` | Monitoring/design worker | Define future order, ad, inventory, and retention workflows; test idempotency models | Live fulfillment, customer messaging, budget changes |

**Future split condition:** only split into the previous nine-agent fleet after one product completes `KILL | ITERATE | SCALE_CANDIDATE` with clean audit logs.

---

## Capability Typing Rule

Every capability must be classified before use:

| Type | Definition | Example | Phase 1 Use |
|---|---|---|---|
| Knowledge skill | Markdown instructions/frameworks for reasoning | Nexscope `market-gap-analysis` | Allowed as guidance |
| API connector | Reads/writes external systems | CJ API connector, Meta API connector | Read-only only unless approved |
| Deterministic service | Applies invariant formulas/schema checks | Margin calculator, state validator | Allowed |
| Human gate | Requires Ahmad approval | campaign publish, supplier submission | Mandatory |

**Critical distinction:** a skill is not a production integration. Skills can shape reasoning; tools/connectors execute real operations.

---

## Available Skills to Use as Guidance

### Research Guidance
- `dropshipping-product-research`
- `market-gap-analysis`
- `tiktok-shop-product-research`
- `tiktok-shop-trending-products`
- `ecommerce-keyword-research`
- `competitor-price-analysis`
- `ecommerce-competitor-analysis`
- `product-review-analysis`

### Validation / Unit Economics Guidance
- `profit-margin-calculator-shopify`
- `competitive-pricing-strategy`
- `price-optimization-tool`
- `cross-border-ecommerce`

### Draft Launch Guidance
- `ecommerce-ppc-strategy-planner`
- `product-description-generator`
- `ecommerce-video-marketing`
- `shoppable-video`
- `ecommerce-landing-page`
- `conversion-rate-optimization`

### Operations Guidance
- `supply-chain-optimization-shopify`
- `ecommerce-shipping-rates`
- `ecommerce-returns-management`
- `restock-alert`
- `warehouse-optimization`
- `ecommerce-email-marketing-builder`
- `ecommerce-customer-retention`

### Experimental Only
- `ecommerce-ops-suite` components: use for prompt/process ideas only until pinned, licensed, and audited.
- Do not place its paid competitive monitor on the critical path.

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

**Phase 1 stops at:** `FOUNDER_REVIEW`.

No agent may jump directly from validation to live ads, live supplier orders, or public storefront publishing.

---

## Phase 0: Evidence and Contract Audit

**Objective:** Freeze dependencies and market assumptions before automation.

**Files likely to change/create:**
- Create: `docs/operating-contract.md`
- Create: `docs/dependency-manifest.md`
- Create: `schemas/candidate.schema.json`
- Create: `schemas/evidence.schema.json`
- Create: `schemas/market-config.schema.json`

**Steps:**
1. Verify the Nexscope `eCommerce-Skills` repository commit and license.
2. Verify every skill name selected for Phase 1 exists locally.
3. Verify `ecommerce-ops-suite` commit, license, folder duplication, and paid/free component claims.
4. Choose exactly one pilot market configuration: US or EU.
5. Record all operating costs as costs, not “free”: payment processing, ads, email delivery, domains, APIs, hosting risk, operations time.
6. Verify Hermes CLI commands against the installed version before writing setup instructions.
7. Verify whether any CJ, Meta, TikTok, Stripe, or email credentials were pasted into repo/conversation/docs; if yes, revoke and rotate.
8. Produce a signed dependency manifest.

**Exit condition:** one market selected, dependency manifest written, no exposed credentials, no unaudited tool in critical path.

---

## Phase 1: Product Research Report Only

**Objective:** Produce up to five reproducible candidate reports from real evidence without live commercial actions.

**Files likely to change/create:**
- Create: `reports/candidates/<YYYY-MM-DD>-<candidate>.md`
- Create: `data/evidence/<candidate>.json`
- Create: `data/candidates.json`
- Modify only if needed: existing project scripts for deterministic validation

**Workflow:**
1. `dropship-orchestrator` creates Kanban tasks for `candidate_limit: 5`.
2. `dropship-research` gathers evidence from allowed sources:
   - public web pages
   - YouTube / RSS / Jina Reader via zero-config Agent-Reach
   - official APIs where available
   - no Facebook/Instagram login-cookie scraping
3. `dropship-research` writes raw evidence JSON with source URL, timestamp, extraction method, and confidence.
4. Deterministic margin service calculates contribution before ads:

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

5. Safety factor must be configurable, default `0.60–0.75`; it must not be hidden in a prompt.
6. `dropship-research` generates a candidate report with:
   - product description
   - target market
   - competitor evidence
   - supplier evidence
   - price and contribution model
   - compliance unknowns
   - proof-burden assessment
   - recommendation: `REJECT | HOLD | FOUNDER_REVIEW`
7. Orchestrator routes `FOUNDER_REVIEW` items to Ahmad.

**Exit condition:** at least one candidate report is reproducible from raw evidence and contains no assumed live integrations.

---

## Phase 2: Draft Launch Pack

**Objective:** Generate draft assets for one approved candidate, without publishing.

**Build:**
- Three creative briefs
- Product page draft
- Product copy
- Compliance checklist
- Tracking plan
- Draft campaign structure

**No live spend. No public publishing.**

**Exit condition:** Ahmad approves or rejects the launch pack.

---

## Phase 3: Storefront Staging

**Objective:** Validate technical commerce flow in sandbox only.

**Build/test:**
- Medusa draft product
- Next.js staged landing page
- Stripe test transaction
- Shipping quote validation
- Refund path
- Analytics event validation

**Exit condition:** complete sandbox order passes end-to-end.

---

## Phase 4: Controlled Micro-Test

**Objective:** Launch one product, one market, one platform, fixed budget, founder approved.

**Allowed automation:**
- Pull campaign metrics
- Produce recommendations
- Emergency pause on hard global cap breach

**Founder approval required:**
- first campaign publish
- any budget increase
- targeting change
- price change
- new country launch

**Exit condition:** `KILL | ITERATE | SCALE_CANDIDATE` verdict.

---

## Phase 5: Limited Fulfillment

**Objective:** Validate supplier execution without duplicate orders or hidden cost drift.

**Order states:**
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

**Exception states:**
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

**Idempotency key:**
```text
cj:{store_order_id}:{fulfillment_version}
```

First five orders require Ahmad approval before supplier submission.

**Exit condition:** five error-free fulfilled orders with quoted vs actual cost and delivery variance recorded.

---

## Phase 6: Learning Loop

**Objective:** Convert campaign outcomes into calibrated heuristics.

**Build:**
- prediction scoring
- calibration log
- root-cause tagging
- heuristic versioning
- promotion at `n ≥ 3`
- `PROVISIONAL | SUPPORTED | CONTESTED | RETIRED` lifecycle

**Exit condition:** next validation run consumes updated heuristics.

---

## Security and Compliance Controls

### Market Consistency
- Do not mix US and EU validators.
- One candidate report uses one market config only.
- Currency, tax model, delivery promises, return address, ad geography, and compliance checklist must match that market.

### EU-Specific Controls If EU Is Selected
Each fulfillment quote must include:

```json
{
  "warehouse_country": "DE",
  "destination_country": "FR",
  "stock_available": 26,
  "shipping_cost": 6.40,
  "delivery_days_min": 3,
  "delivery_days_max": 6,
  "hs_code": "REQUIRED",
  "origin_country": "CN",
  "import_status": "CONFIRM_REQUIRED",
  "landed_cost_confidence": "LOW"
}
```

No product passes EU validation while `landed_cost_confidence` is `LOW`.

Do not artificially group tariff lines to reduce duty. Customs classification must follow the real product, origin, declaration, and applicable law.

### AI Creative Controls
Treat “Product imagery assisted by generative AI” as a conservative internal brand policy, not a universal legal guarantee.

Creative metadata must preserve:
- original source asset
- generated asset
- prompt and model metadata
- human reviewer
- approval timestamp
- disclosure decision
- platform disclosure setting
- whether a real person’s likeness is represented

---

## Removed From Phase 1

- Google Shopping execution
- subscription flows
- RFM segmentation
- VIP programs
- automated supplier submission
- automated budget increases
- 40 creatives per hook
- Veo winner reshoots
- full nine-profile fleet
- EU tariff grouping optimization
- every-six-hour scouting
- all 157 skills installed globally
- public storefront creation
- live ad publishing

---

## Verification Plan

Before Phase 1 is considered complete:

1. Run repository searches to confirm all referenced skill folders exist.
2. Read selected `SKILL.md` files and classify each as guidance vs executable.
3. Run deterministic margin calculator tests on at least three fixture products.
4. Validate candidate JSON against `schemas/candidate.schema.json`.
5. Reproduce one candidate report from saved raw evidence without live browsing.
6. Confirm no live API write permissions are required for Phase 1.
7. Confirm all approval-gated actions are blocked by default.

---

## Final Recommendation

Do not execute the old seven immediate actions unchanged.

Execute this instead:

1. Write `docs/operating-contract.md` from the YAML above.
2. Select the pilot market: US or EU.
3. Pin and audit only the small Phase 1 skill bundle.
4. Build the `dropship-research` evidence worker and candidate schema.
5. Generate one reproducible candidate report.
6. Review with Ahmad before any storefront, ad, or supplier automation.
