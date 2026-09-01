# Schema Evolution & Backward Compatibility Rules

**Project:** Dropship | **Framework:** Hermes  
**Version:** 1.0.0  
**Effective Date:** 2026-09-01  

---

## 1. Core Principles
Schemas are immutable contracts between autonomous research agents, the scoring engine, and human execution gates. Breaking schema changes break downstream automation, invalidate stored audit trails, and risk execution failure.

## 2. Semantic Versioning for Schemas
All schemas declare a `version` field formatted as `MAJOR.MINOR.PATCH` (e.g. `1.0.0`).

1. **PATCH (1.0.0 -> 1.0.1)**:
   - Non-breaking clarifications in descriptions, titles, examples, or documentation.
   - Loosening regex patterns to tolerate valid alternative IDs.
2. **MINOR (1.0.0 -> 1.1.0)**:
   - Adding **optional** fields with default values.
   - Adding new enum values to non-gated fields (e.g. new signal types or platform names).
   - Old records validate without mutation.
3. **MAJOR (1.0.0 -> 2.0.0)**:
   - Renaming or deleting existing fields.
   - Changing field types or value constraints.
   - Adding new **required** fields.
   - Requires explicit migration scripts in `scripts/migrations/` and Founder sign-off.

---

## 3. Compatibility Matrix

| Schema | File | Current Version | Backward Compatibility Rule |
|---|---|---|---|
| **Market Config** | `market-config.schema.json` | `1.0.0` | `live_risk_limits` must remain strictly enforced; additions to market definitions must default to safe sandbox limits. |
| **Evidence** | `evidence.schema.json` | `1.0.0` | New signal types may be added as optional tags; source URLs and confidence ratings are mandatory. |
| **Candidate** | `candidate.schema.json` | `1.0.0` | `approval_gate.requires_ahmad_approval` can never be removed or made optional. Unit economics keys are locked. |
| **Supplier** | `supplier.schema.json` | `1.0.0` | Warehouse country and lead days format locked. New carrier tiers must be appended to `shipping_tiers`. |
| **Trade Signal** | `trade_signal.schema.json` | `1.0.0` | `hypothesis` must always contain numeric CTR, CVR, CPA, and net margin. `approval_status` transitions cannot bypass `PENDING_FOUNDER_REVIEW`. |
| **Approval** | `approval.schema.json` | `1.0.0` | Verification hash algorithm (`sha256`) and required approver (`Ahmad`) are immutable. |

---

## 4. Ingestion & Fallback Rules
- When reading legacy candidate or supplier records lacking a `version` attribute, the parser must inject `"version": "1.0.0"` during normalization before validation.
- Schema validators must use `Draft202012Validator` and reject unknown properties on gated entities (`additionalProperties: false`).
