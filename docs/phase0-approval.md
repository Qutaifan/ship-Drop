# Phase 0 Approval

**Approver:** Ahmad  
**Date:** 2026-09-01

**Decision:** Approve transition to Phase 1 for research-only candidate sourcing under the following conditions:
- CJ MCP typing issue fixed and `hermes mcp test cj-dropshipping` passes in the isolated profile.
- Current Hermes profile remains unauthenticated for CJ and is restricted to research-only workflows.
- Isolated Hermes profile `dropship-supplier-ops` is provisioned and documented for supplier-facing operations.
- The exposed CJ token that appeared in chat is considered compromised and must be rotated before any live supplier workflows.
- Tool access policy and credential audit updates are committed to `docs/tool-access-policy.md` and `docs/security/credential-audit.md`.

**Rationale:** Begin candidate sourcing and evidence collection while preserving a secure separation for supplier write actions.

**Signature:** Ahmad
