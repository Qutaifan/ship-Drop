# Approval Policy — Dropship Phase 0+

**Owner:** Ahmad  
**Default mode:** deny live-risk actions unless explicitly approved.

---

## Always Requires Ahmad Approval

| Action | Earliest Phase | Reason |
|---|---:|---|
| Publish first campaign | 4 | starts live spend |
| Increase daily or lifetime budget | 4+ | spend risk |
| Change campaign targeting | 4+ | market/legal/performance risk |
| Change product price | 4+ | margin, tax, offer consistency |
| Publish storefront to production | 3+ | public legal/commercial exposure |
| Submit supplier order | 5+ | duplicate/order/refund risk |
| Send customer email/SMS | 5+ | consent/deliverability/legal risk |
| Launch a new country/region | 7+ | tax, returns, compliance, payment risk |
| Make product-safety/legal/tax claims | any | compliance risk |
| Store or rotate live credentials | any | security risk |

---

## Allowed Without Approval in Phase 0/1

| Action | Constraints |
|---|---|
| Read public web data | no login-cookie scraping for ad-account platforms |
| Use curated knowledge skills | guidance only; do not treat as API integrations |
| Generate candidate reports | must cite source/evidence files |
| Run deterministic calculators | tests must pass |
| Write local schemas/docs/fixtures | no secrets |
| Create draft recommendations | clearly marked draft |
| Create Kanban tasks | no live external side effects |

---

## Emergency Automation Allowed Later

A worker may automatically pause a campaign only when all conditions are true:

1. campaign is already live and approved,
2. hard global spend cap is exceeded or API-reported spend is inconsistent,
3. pause action is logged immediately,
4. Ahmad is notified with the exact campaign ID and reason.

No automatic scaling is allowed during the pilot.

---

## Approval Record Format

Every approval must be recorded with:

```yaml
approval_id: string
action: string
object_id: string
requested_by: dropship-orchestrator|dropship-research|dropship-launch|dropship-operations
approved_by: Ahmad
approved_at: ISO-8601 timestamp
scope:
  market_config_id: string
  candidate_id: string|null
  max_budget: number|null
  currency: string|null
constraints:
  - string
expires_at: ISO-8601 timestamp|null
```

---

## Deny-by-Default Rule

If the scope, market, budget, platform, supplier, or expiration is unclear, the action is denied and routed to `HUMAN_REVIEW`.
