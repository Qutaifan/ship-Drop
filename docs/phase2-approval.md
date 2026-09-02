# Phase 2 Approval — US Pilot Creative Test

```yaml
approval_id: phase2-us-top2-creative-test-001
action: approve_phase_transition
project: dropship
market: US
from_phase: 1
to_phase: 2
requested_by: dropship-orchestrator
approved_by: Ahmad
approved_at: 2026-09-01T17:57:42+03:00
scope:
  candidate_id: candidate-us-2026-09-01-magnetic-cable-organizer,candidate-us-2026-09-01-foldable-silicone-bowl
  max_budget: 600
  currency: USD
constraints:
  - staging only; no public storefront publish
  - this artifact does not authorize live ad spend; exact live campaign IDs require separate Ahmad approval
  - no CJ authentication from the default profile; supplier ops remain isolated
  - creative assets generated locally via ComfyUI and Remotion only
  - tracking limited to self-hosted analytics; no unapproved external pixels
  - refreshed Phase 2 BUY signals now supersede the earlier economics set; only the refreshed signal IDs below may be used for live-gate review
  - any budget increase, targeting change, or supplier write requires separate Ahmad approval
expires_at: 2026-09-15T23:59:59-04:00
```

## Evidence Reviewed

- [x] Operating contract
- [x] Dependency manifest
- [x] Approval policy
- [x] Relevant candidate/evidence files
- [x] Compliance checklist
- [x] Tool-access policy

## Candidates in Scope

| Candidate | Product | Current staging product file | Pending signal |
|---|---|---|---|
| `candidate-us-2026-09-01-magnetic-cable-organizer` | Magnetic Cable Organizer — 6-Pack Silicone Cord Clips | `products/candidate-us-2026-09-01-magnetic-cable-organizer.md` | `sig-buy-candidate-us-2026-09-01-magnet-500f28` |
| `candidate-us-2026-09-01-foldable-silicone-bowl` | Foldable Silicone Bowl Set — 4-Pack Collapsible Kitchen Bowls | `products/candidate-us-2026-09-01-foldable-silicone-bowl.md` | `sig-buy-candidate-us-2026-09-01-foldab-460ef9` |

## Decision

Approved by Ahmad for **Phase 2 staging only** on `2026-09-01T17:57:42+03:00`.

## Notes

This artifact authorizes only the transition into Phase 2 staging preparation. It does not authorize live campaign publication, supplier orders, public storefront deployment, or customer messaging.
