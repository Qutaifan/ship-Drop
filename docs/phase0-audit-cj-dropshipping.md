# Phase 0 Audit — CJ Dropshipping MCP

**Project:** dropship  
**Market:** US pilot  
**Audit timestamp:** 2026-09-01T01:10:28+03:00  
**Auditor:** Hermes-Ecom  
**Status:** **CONNECTED IN ISOLATED PROFILE; BLOCKED FOR LIVE USE**

---

## Executive Verdict

The `cj-dropshipping` MCP must **not** be used for live supplier operations in the current profile.

Updated findings:

1. **Default/project profile:** still not approved for CJ authentication or supplier operations.
2. **Isolated profile created:** `dropship-supplier-ops` now exists with manual approvals, manual cron approvals, memory write approval, and secret redaction enabled.
3. **Connection issue fixed in isolated profile:** `CJ_LOG_FILE` is configured as the string `"true"`, and `hermes --profile dropship-supplier-ops mcp test cj-dropshipping` connects successfully.
4. **The server exposes write-capable tools** and its sensitive-operation layer logs confirmation prompts but does not provide a hard, server-side read-only mode discovered in the source audit.

**Decision:** supplier-facing write actions require a separate isolated Hermes profile before any CJ login, order creation, payment, product connection, webhook configuration, or dispute operation is allowed.

---

## Evidence

### Hermes MCP listing

`hermes mcp list` shows:

```text
cj-dropshipping  node Q:/cj-mcp-server/dist/...  all  enabled
craft            https://mcp.craft.do/my/mcp     all  enabled
hugging_face     https://huggingface.co/mcp      all  enabled
```

### CJ MCP connection test

Default/project profile `hermes mcp test cj-dropshipping` returned:

```text
Testing 'cj-dropshipping'...
  Transport: stdio → node
  Auth: none
  ✗ Connection failed: env.CJ_LOG_FILE Input should be a valid string; input_value=True, input_type=bool
```

Isolated supplier profile connection test returned:

```text
hermes --profile dropship-supplier-ops mcp test cj-dropshipping

✓ Connected
✓ Tools discovered: 65
```

Main/default profile was also corrected for research-only future sessions:

```text
hermes mcp list

cj-dropshipping  node Q:/cj-mcp-server/dist/...  25 selected  enabled
```

The proposed `mcp_guards` runtime snippet was not applied because Hermes docs/source inspection did not show active support for that key. The enforced mechanism used here is the supported MCP `tools.include` filter.

### Source inspection

Source path inspected:

```text
Q:/cj-mcp-server
```

Tool registry exposes product, logistics, order, dispute, shop, stock, webhook, auth, and navigation tools.

Sensitive-operation list found in:

```text
Q:/cj-mcp-server/src/utils/sensitive-ops.ts
```

The sensitive-operation code identifies risky tools and generates confirmation text, but the tool dispatcher continues to handler execution after logging the prompt. It relies on MCP client behavior rather than a hard server-side enforcement switch.

---

## Risk Classification

| Risk area | Finding | Severity | Policy |
|---|---|---:|---|
| MCP connectivity | fixed in `dropship-supplier-ops`; default/project profile still not used | Medium | keep CJ access isolated |
| Read/write separation | default profile restricted to 25 selected research/read tools for new sessions; supplier profile keeps all tools behind manual approvals | High | keep write-capable workflows isolated |
| Order creation | `create_order`, cart, payment tools exist | Critical | blocked until Phase 5 approval |
| Supplier account mutation | product connection, shop save, webhook configuration exist | High | blocked until isolated profile exists |
| Dispute mutation | create/cancel/confirm dispute tools exist | High | blocked until operations phase |
| Logs and secrets | debug mode can log full args after sanitization | Medium | keep debug off for supplier profile |

---

## CJ MCP Tool Classification

### Read / research tools allowed after connection fix

These tools are acceptable for Phase 1 research if no customer PII, no supplier account mutation, and no order/payment operation is involved:

- `search_products`
- `get_category_tree`
- `get_warehouses`
- `get_product_detail`
- `query_cj_inventory`
- `get_product_variants`
- `get_product_reviews`
- `query_sourcing`
- `calculate_freight`
- `get_logistics_timeliness`
- `get_tracking_info`
- `calculate_freight_tip`
- `query_private_inventory`
- `query_sku_details`
- `query_sku_detail_page`
- `query_sku_detail_by_sku`
- `get_product_inventory`
- `get_storage_info`

### Write / sensitive tools blocked in this profile

These tools must not execute from the default/project research profile:

- `add_to_cart`
- `create_order`
- `submit_order_to_cart`
- `confirm_cart_and_pay`
- `generate_payment_link`
- `merge_orders`
- `pay_by_balance`
- `pay_by_balance_v2`
- `confirm_order`
- `delete_order`
- `create_dispute`
- `cancel_dispute`
- `confirm_dispute`
- `save_product_to_shop`
- `create_product_connection`
- `disconnect_product`
- `configure_webhook`
- `logout`

### Requires manual classification before use

- `create_sourcing` — creates a supplier-facing sourcing request. Treat as write-sensitive until Ahmad approves a sourcing workflow.
- `list_shops`, `get_authorize_url`, `get_account_settings` — account-revealing read tools; allowed only after credential policy is confirmed.
- navigation UI tools — read/UI only, but can expose account surfaces; use manually only.

---

## Required Permission Model

### Current profile: `default` / project research context

Allowed:

- public research
- schema validation
- candidate report generation
- local file writes
- CJ catalog/inventory/logistics reads only after connection fix

Blocked:

- CJ login with live supplier account
- supplier order creation
- cart/payment generation
- balance payment
- product-to-store connection
- webhook configuration
- dispute mutation

### Created isolated profile: `dropship-supplier-ops`

Purpose:

- isolated supplier operations only after Phase 5 approval
- separate memory/session/tool history
- approval mode set to smart/manual
- no autonomous cron jobs that can call supplier writes
- no live order action without an approval artifact and idempotency key

Recommended settings:

```yaml
profile: dropship-supplier-ops
approval_owner: Ahmad
approvals_mode: manual
cron_approval_mode: manual
memory_write_approval: true
secret_redaction: true
live_order_submission_allowed: phase5_only
supplier_write_tools: manual_approval_required
cron_supplier_writes: disabled
cj_debug_logging: disabled
idempotency_key_format: cj:{store_order_id}:{fulfillment_version}
```

---

## Remediation Tasks

1. Keep `CJ_LOG_FILE` as a string value in the isolated supplier profile.
2. Do **not** authenticate CJ in the default/project profile.
3. Do **not** use the pasted CJ MCP token in repo files or reports; rotate it before live use because it appeared in chat context.
3. **Decision 2026-09-01:** Token rotation deferred per Ahmad until development phases complete. Token remains in chat context only; not stored in repo, config, or project files. Rotation will be performed before Phase 4+ live supplier workflows.
4. Keep isolated profile `dropship-supplier-ops` as the only approved location for later CJ supplier operations.
5. Add a tool allowlist/denylist to the operating contract and enforce it in review.
6. Require Phase 5 approval artifact before any order/payment/dispute/store mutation.

---

## Phase 0 Decision

**Phase 0 governance audit result:** completed.  
**Phase 0 exit status:** approved for Phase 1 research-only candidate sourcing by `docs/phase0-approval.md`.  
**Remaining restriction:** CJ MCP is write-capable and has no verified hard read-only mode, so live supplier operations remain blocked.  
**Next approval candidate:** begin Phase 1 candidate sourcing only; do not approve live supplier actions.
