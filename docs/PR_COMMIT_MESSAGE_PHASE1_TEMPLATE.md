# PR Commit Message Template — Phase 1 Candidate Artifacts

## Branch naming

```text
feat/phase1-candidates-YYYYMMDD-short-description
```

Example:

```text
feat/phase1-candidates-20260901-neck-fan-cable-organizer
```

---

## Commit message (single commit for the batch)

```text
feat(phase1): add candidate cards for magnetic cable organizer and portable neck fan

- docs/candidates/candidate-us-2026-09-01-magnetic-cable-organizer.md
- docs/candidates/candidate-us-2026-09-01-portable-neck-fan.md
- fixtures/evidence-us-cable-organizer-*.json/md (6 files)
- fixtures/evidence-us-neck-fan-*.json/md (6 files)
- docs/phase1-review.md (updated with both candidates)

Both candidates scored against six-criteria US-fit template.
Magnetic Cable Organizer: 27/30 → approve_for_phase2_test
Portable Neck Fan: 21/30 → hold (CN fulfillment risk, margin/COGS below 3×)

No live supplier actions, ad spend, or secrets in this commit.
```

---

## PR Description

### Summary

Adds two Phase 1 research-only candidate artifacts for the US pilot. Both candidates are fully scored using the six-criteria US-fit template with supporting evidence files. No live supplier orders, ad spend, or public publishing.

### Changes

| File | Purpose |
|---|---|
| `docs/candidates/candidate-us-2026-09-01-magnetic-cable-organizer.md` | Candidate 1: 27/30 score; US warehouse; passes all gates |
| `docs/candidates/candidate-us-2026-09-01-portable-neck-fan.md` | Candidate 2: 21/30 score; CN fulfillment; margin/COGS below 3× |
| `fixtures/evidence-us-cable-organizer-*.json/md` | 6 evidence files for Candidate 1 |
| `fixtures/evidence-us-neck-fan-*.json/md` | 6 evidence files for Candidate 2 |
| `docs/phase1-review.md` | Updated summary with both candidates |

### Verification

- [x] All candidate files use `docs/templates/candidate-template.md`
- [x] Unit economics validated via `scripts/validate_phase0_schemas.py`
- [x] No secrets or credentials in any committed file
- [x] CJ MCP access unchanged: main profile limited to 25 read/research tools; supplier ops isolated in `dropship-supplier-ops`
- [x] Phase 0 approval signed at `docs/phase0-approval.md`
- [x] CJ MCP token rotation deferred per Ahmad (recorded in `docs/security/credential-audit.md`)

### Test

```bash
npm run test
# Phase 0 schema validation PASSED
```

### Next Steps (not in this PR)

1. Collect 1–2 more candidates to reach shortlist of 3
2. Ahmad reviews and signs `docs/phase1-review.md` for Phase 2 ad test authorization
3. Rotate exposed CJ MCP token before any live supplier workflows (Phase 4+)
4. Phase 2 creative production on local GPU (ComfyUI + Remotion)

### Related

- Phase 0 governance commit: `63a9213`
- Operating contract: `docs/operating-contract.md`
- Tool access policy: `docs/tool-access-policy.md`
- Approval policy: `docs/approval-policy.md`