# Dropship Operating Contract

**Project:** dropship  
**Phase:** Phase 0 — Evidence and Contract Audit  
**Pilot Market:** US  
**Approval Owner:** Ahmad  
**Status:** live-risk actions disabled

---

## Market Configuration

```yaml
market:
  primary_country: US
  currency: USD
  tax_model: destination_sales_tax
  fulfillment_region: US
  target_delivery_days: 3-8
  returns_region: US
  advertising_region: US
```

## Operating Limits

```yaml
live_spend_allowed: false
live_order_submission_allowed: false
live_storefront_publish_allowed: false
live_customer_messaging_allowed: false
candidate_limit: 5
```

## MVP Profiles

```yaml
profiles:
  - dropship-orchestrator
  - dropship-research
  - dropship-launch
  - dropship-operations
```

## Approval Gates

Ahmad approval is required for:

- first campaign publication
- any budget increase
- supplier order submission
- price change
- new country launch
- public storefront publication
- live customer messaging
- any compliance representation that creates legal/tax/product-safety risk

## Allowed Automation in Phase 0/1

- read public data
- classify skills as guidance vs executable
- generate candidate reports
- calculate deterministic margins
- draft launch assets
- prepare recommendations
- create Kanban tasks
- write audit logs and manifests

## Disallowed Automation in Phase 0/1

- ad spend
- campaign publication
- supplier order submission
- public storefront deployment
- price changes
- customer email/SMS sending
- account-risk scraping using login cookies
- customs/tax manipulation

## Capability Typing Rule

| Type | Definition | Phase 0/1 Rule |
|---|---|---|
| Knowledge skill | Markdown reasoning framework | allowed as guidance |
| API connector | Reads/writes external systems | read-only only unless approved |
| Deterministic service | Formula/schema/state logic | allowed after tests |
| Human gate | Approval-required action | Ahmad decides |

## Current Skill Bundle Policy

The project uses a curated project-local skill bundle under:

```text
Q:\world\Projects\Dropshiping\.hermes\skills\ecommerce\
```

Global installation of all e-commerce skills is rejected for Phase 0/1 because it creates context noise and loads irrelevant marketplace guidance.

## Current Hermes Toolset Status

From `hermes doctor` and `hermes tools list`:

- Hermes health check passed.
- Core required toolsets are enabled: web, terminal, file, code execution, skills, todo, memory, delegation, cronjob, computer_use.
- MCP server `cj-dropshipping` is listed with all tools enabled in the default/project profile but remains unauthenticated and not approved for supplier operations there.
- Default/project profile CJ MCP access is restricted to 25 selected research/read tools for new sessions using `mcp_servers.cj-dropshipping.tools.include`.
- Isolated profile `dropship-supplier-ops` was created and verified to connect to the local CJ MCP server with 65 tools discovered.
- CJ supplier writes require the isolated `dropship-supplier-ops` profile plus explicit Ahmad approval before any authentication or live supplier workflow.
- Live supplier submission remains disabled by this operating contract.
- Browser toolset is enabled in CLI listing; doctor also reports browser/browser-cdp system dependency warnings. Browser-dependent production workflows must be verified before use.

## Tool Access Policy

The canonical tool-access policy is maintained at:

```text
docs/tool-access-policy.md
```

Phase 0/1 research profiles may use local files, public reads, deterministic validators, and draft generation. Account mutation and financial/customer-impact actions remain approval-gated and are blocked in the default/project profile.

## Source Repositories

- Nexscope `eCommerce-Skills`: local folder present and MIT licensed.
- `ecommerce-ops-suite`: real GitHub repository, treated as experimental reference only until cloned, pinned, and audited.

## Phase 0 Exit Criteria

Phase 0 is complete only when:

- dependency manifest is complete
- candidate/evidence/market schemas exist
- selected skills are classified as guidance vs executable
- credential audit is complete
- no live-risk connector is able to execute without Ahmad approval
- `docs/phase0-audit-cj-dropshipping.md` is reviewed
- `docs/phase0-approval.md` is signed by Ahmad
