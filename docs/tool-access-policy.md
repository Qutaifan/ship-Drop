# Tool Access Policy — Dropship Hermes-Ecom

**Project:** dropship  
**Market:** US pilot  
**Owner:** Ahmad  
**Default:** deny live-risk actions unless explicitly approved

---

## Policy Summary

Hermes-Ecom may automate research, validation, local file generation, schema checks, and draft recommendations. It may not autonomously spend money, submit supplier orders, publish storefront changes, send customer communications, or mutate supplier/account state.

---

## Access Tiers

| Tier | Description | Approval required | Examples |
|---|---|---:|---|
| Tier 0 — local | local docs, schemas, fixtures, tests | No | write candidate files, run `npm run test` |
| Tier 1 — public read | public web/data research | No | product research, competitor pages, demand screens |
| Tier 2 — account read | authenticated read-only account data | Yes for first connection | CJ inventory/account reads, ad account reporting |
| Tier 3 — account mutation | changes external system state | Always | product connection, webhook setup, store sync |
| Tier 4 — financial/customer impact | spend, orders, payment, customer messages | Always + phase gate | ads, supplier orders, refunds, customer email/SMS |

---

## CJ Dropshipping MCP Policy

### Allowed in research profile after connection fix

- catalog search
- product detail reads
- warehouse reads
- inventory reads
- freight/timeliness calculations
- review reads

### Blocked in research profile

- CJ authentication with live supplier account
- add to cart
- create order
- confirm order
- generate payment link
- pay by balance
- merge orders
- delete order
- create/cancel/confirm dispute
- save product to shop
- create or disconnect product connection
- configure webhook
- create sourcing request unless separately approved

---

## Required Profile Separation

| Profile | Purpose | Allowed tiers |
|---|---|---|
| `dropship-orchestrator` | governance, approvals, roadmap | Tier 0–1; Tier 2 by approval |
| `dropship-research` | product and supplier evidence | Tier 0–1; CJ read-only after connection fix |
| `dropship-launch` | draft pages, creatives, staging | Tier 0–1; no production publish |
| `dropship-operations` | post-approval monitoring | Tier 0–2 initially |
| `dropship-supplier-ops` | supplier writes after Phase 5 | Tier 3–4 only with explicit approval |

Current supplier profile status:

```yaml
profile: dropship-supplier-ops
created: true
approvals.mode: manual
approvals.cron_mode: manual
memory.write_approval: true
security.redact_secrets: true
cj_mcp_connection: verified
cj_mcp_tools_discovered: 65
live_supplier_writes: blocked
```

Current main/default profile guard status:

```yaml
profile: default
cj_mcp_connection: verified
cj_mcp_tools_selected: 25
cj_mcp_env.CJ_LOG_FILE: disabled
write_capable_cj_tools_available_in_profile: false_for_new_sessions
guard_mechanism: mcp_servers.cj-dropshipping.tools.include
unsupported_snippet_not_used: mcp_guards
```

Hermes source/docs did not expose a runtime `mcp_guards` enforcement block. The supported control is MCP tool selection via `mcp_servers.<server>.tools.include`, so the main profile uses an include-list of research/read tools rather than the non-enforced `mcp_guards` snippet.

---

## Approval Artifact Requirement

Any Tier 3 or Tier 4 action requires an approval file containing:

```yaml
approval_id: string
action: string
external_system: string
object_id: string
requested_by: string
approved_by: Ahmad
approved_at: ISO-8601 timestamp
max_budget: number|null
currency: string|null
idempotency_key: string|null
expires_at: ISO-8601 timestamp|null
rollback_plan: string
```

---

## Supplier Order Idempotency

Every future CJ order action must use this idempotency format:

```text
cj:{store_order_id}:{fulfillment_version}
```

No duplicate order attempt is allowed without first checking the prior order status and writing a new fulfillment version.

---

## Enforcement Rule

If tool capability is unclear, classify it as write-sensitive and route to `HUMAN_REVIEW`.
