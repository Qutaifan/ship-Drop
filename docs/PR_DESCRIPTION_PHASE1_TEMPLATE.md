# PR Description Template — Phase 1 Artifacts

## Title

```text
feat(phase1): add candidate sourcing artifacts and Phase 1 review
```

## Body

### Summary

This PR adds the first batch of Phase 1 research-only candidate sourcing artifacts for the US pilot. All work remains in the evidence-collection stage — no live supplier orders, ad spend, or public publishing.

### Changes

- `docs/candidates/candidate-us-2026-09-01-magnetic-cable-organizer.md` — pre-filled candidate card using the standard template with six-criteria scoring (27/30), supplier dossier, competitor evidence, unit economics, and numeric hypothesis
- `docs/phase1-review.md` — Phase 1 review artifact summarizing top candidate(s), evidence links, and Phase 2 test plan request with kill/scale/iterate criteria
- `fixtures/evidence-us-cable-organizer-*.json/md` — supporting evidence files (shipping, supplier, margin, differentiation, demand, ops)

### Verification

- All candidate files use the standard template from `docs/templates/candidate-template.md`
- Unit economics validated via `scripts/validate_phase0_schemas.py` (margin/COGS and CAC gates)
- No secrets or credentials in any committed file
- CJ MCP access remains restricted: main profile limited to 25 read/research tools; supplier writes isolated in `dropship-supplier-ops` profile
- Phase 0 approval signed at `docs/phase0-approval.md`

### Testing

```bash
npm run test
# Phase 0 schema validation PASSED
```

### Next Steps (not in this PR)

1. Rotate the exposed CJ MCP token in CJ dashboard and record in `docs/security/credential-audit.md`
2. Collect 2–3 more candidates to reach shortlist of 3
3. Ahmad signs `docs/phase1-review.md` to authorize Phase 2 ad test (max $500)
4. Phase 2 creative production begins on local GPU (ComfyUI + Remotion)

### Related

- Phase 0 governance commit: `63a9213`
- Operating contract: `docs/operating-contract.md`
- Tool access policy: `docs/tool-access-policy.md`
- Approval policy: `docs/approval-policy.md`