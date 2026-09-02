# Dependency Manifest — Phase 0

**Project:** dropship  
**Phase:** evidence_only  
**Pilot market:** US  
**Generated from local inspection:** yes

---

## Hermes Runtime

| Component | Status | Evidence |
|---|---|---|
| Hermes version | `0.20.6` | `hermes doctor` reported version files consistent |
| Python | `3.11.15` | `hermes doctor` |
| Virtual environment | active | `hermes doctor` |
| Skills CLI | available | `hermes skills --help` |
| Project skills trust | enabled | `hermes skills trust Q:/world/Projects/Dropshiping` |
| Kanban | available, runtime-gated | `hermes doctor` |
| Cronjob | available | `hermes doctor` |

## Enabled Toolsets Relevant to Phase 0/1

| Toolset | Status | Use |
|---|---|---|
| web | enabled | public research and extraction |
| terminal | enabled | git, tests, CLI verification |
| file | enabled | read/write project artifacts |
| code_execution | enabled | schema validation and deterministic scripts |
| skills | enabled | load curated guidance skills |
| todo | enabled | task tracking |
| memory | enabled | durable user/project preferences only |
| delegation | enabled | bounded subtasks only |
| cronjob | enabled | later reconciliation jobs |
| computer_use | enabled | manual UI fallback only |

## Warnings / Non-Blocking Issues

| Item | Status | Action |
|---|---|---|
| browser/browser-cdp | doctor reports system dependency warnings despite browser enabled in tool list | verify before relying on browser workflows |
| discord/discord_admin | missing `DISCORD_BOT_TOKEN` | irrelevant to Phase 0/1 |
| homeassistant/spotify/yuanbao | dependencies not met | irrelevant to Phase 0/1 |

## MCP Servers

| MCP Server | Status | Phase 0/1 Policy |
|---|---|---|
| `cj-dropshipping` | default/project profile restricted to 25 selected research/read tools for new sessions; isolated profile `dropship-supplier-ops` connects successfully with 65 tools discovered | research-only reads until Phase 5; supplier writes require explicit approval |
| `craft` | listed | not in critical path |
| `hugging_face` | listed | not in critical path |

## Nexscope eCommerce-Skills

| Field | Value |
|---|---|
| Local path | `Q:/world/Projects/Dropshiping/eCommerce-Skills` |
| Commit | `ee0fb29433d02ccc22e3e6cea9ab4586d49fd42e` |
| License | MIT |
| Local `SKILL.md` count | 162 |
| README advertised count | 157 |
| Phase 0/1 policy | curated subset only; guidance layer, not production integrations |

## Curated Project-Local Phase 0/1 Skills

Copied to:

```text
Q:/world/Projects/Dropshiping/.hermes/skills/ecommerce
```

Manifest:

```text
Q:/world/Projects/Dropshiping/.hermes/skills/ecommerce-phase1-manifest.json
```

| Skill | Source | Classification |
|---|---|---|
| `dropshipping-product-research` | Nexscope | knowledge skill |
| `market-gap-analysis` | Nexscope | knowledge skill |
| `ecommerce-keyword-research` | Nexscope | knowledge skill |
| `product-review-analysis` | Nexscope | knowledge skill |
| `competitor-price-analysis` | Nexscope | knowledge skill |
| `ecommerce-competitor-analysis` | Nexscope | knowledge skill |
| `profit-margin-calculator-shopify` | Nexscope | knowledge skill + bundled calculator reference |
| `competitive-pricing-strategy` | Nexscope | knowledge skill |
| `price-optimization-tool` | Nexscope | knowledge skill |
| `cross-border-ecommerce` | Nexscope | knowledge skill |

## ecommerce-ops-suite

| Field | Value |
|---|---|
| URL | `https://github.com/jian1929/ecommerce-ops-suite` |
| Status | exists |
| Current policy | experimental reference only |
| Critical path | no |
| Reason | small project, overlapping folders, paid competitive monitor claim, not audited locally |

## Live-Risk Dependencies Not Yet Approved

| Dependency | Phase | Current Status |
|---|---:|---|
| Meta Marketing API writes | 4+ | disabled |
| TikTok Ads API writes | 4+ | disabled |
| Google Ads / Merchant Center writes | 4+ | disabled |
| CJ supplier order submission | 5+ | disabled |
| Stripe live mode | 3+ test only, live later | disabled |
| Listmonk live sends | 7+ | disabled |
| Public storefront deploy | 3+ staging only, live later | disabled |

## Open Phase 0 Items

- Rotate/regenerate the pasted CJ MCP token before live use because it appeared in chat context.

## Completed Phase 0 Items

- Created and validated `schemas/market-config.schema.json`.
- Created and validated `schemas/evidence.schema.json`.
- Created and validated `schemas/candidate.schema.json`.
- Created US pilot config at `config/markets/us-pilot.json`.
- Created schema fixtures at `fixtures/evidence.sample.json` and `fixtures/candidate.sample.json`.
- Added validation command: `npm run test` → `python scripts/validate_phase0_schemas.py`.
- Completed initial credential exposure audit at `docs/security/credential-audit.md`.
- Created standalone approval policy at `docs/approval-policy.md`.
- Completed CJ Dropshipping MCP governance audit at `docs/phase0-audit-cj-dropshipping.md`.
- Created pending Phase 0 approval artifact at `docs/phase0-approval.md`.
- Created tool access policy at `docs/tool-access-policy.md`.
- Created US compliance checklist at `docs/us-compliance-checklist.md`.
- Created candidate template at `docs/templates/candidate-template.md`.
- Created isolated supplier profile `dropship-supplier-ops`.
- Verified `cj-dropshipping` MCP connection in `dropship-supplier-ops`; 65 tools discovered.
- Restricted default/project profile CJ MCP to 25 selected research/read tools for new sessions.
- Ahmad signed Phase 0 approval at `docs/phase0-approval.md` for Phase 1 research-only candidate sourcing.
