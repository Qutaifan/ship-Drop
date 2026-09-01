# Credential Audit — Phase 0

**Project:** dropship  
**Scope:** repository files under `Q:/world/Projects/Dropshiping`, excluding `.git`, `node_modules`, build outputs, and virtual environments.  
**Method:** Redacted pattern scan for token/API-key/secret shapes. Secret values were not printed.

---

## Result

**Status:** no confirmed live credential found in the inspected sample.

The scan reported **82 pattern hits**, but the reviewed hits are false positives or environment-variable references:

| Location | Classification | Notes |
|---|---|---|
| `.agents/skills/medusa-v2-storefront/SKILL.md:52` | false positive | Stripe `event.clientSecret` variable in example code, not a stored secret |
| `agency/departments/*/configs/config.yaml:4` | env reference | `${OPENROUTER_API_KEY}` placeholder/reference, not a literal key |
| `reports/cj-mcp-search-results.json` | false positive | repeated CJ error text saying “Invalid API key or access token”; no actual token present in reviewed sample |
| `scripts/ebay_api.py:218` | env reference/code | reads client secret from environment |
| `scripts/ebay_api.py:225` | code reference | token helper call/reference, not a literal token |

## Governance Decision

- Do not store CJ, Meta, TikTok, Stripe, OpenRouter, or SMTP secrets in repo files.
- Keep secrets in Hermes/profile secret storage or `.env` outside tracked project files.
- Treat the enabled `cj-dropshipping` MCP as **read-only for Phase 0/1** until its tool-level write permissions are isolated.
- Any pasted supplier/API credential must be revoked and regenerated before live use.

## 2026-09-01 CJ MCP Token Handling Note

A CJ MCP token was provided in chat context. It was treated as a live secret, was **not** copied into project files, and is intentionally not reproduced in this repository. Because chat transcripts can persist, the token should be rotated/regenerated before any live supplier workflow.

**Update 2026-09-01 (Ahmad decision):** Token rotation deferred until development phases complete. Token remains in chat context only; not stored in repo, config, or project files. Rotation will be performed before Phase 4+ live supplier workflows.

## Follow-Up Before Phase 4+

Before live ads, storefront publishing, or fulfillment:

1. Re-run this audit after adding connectors.
2. Add pre-commit secret scanning.
3. Confirm provider token scopes are read-only unless an approval-gated write profile is intentionally created.
4. Rotate any credential that appeared in a chat, report, screenshot, or markdown note.
