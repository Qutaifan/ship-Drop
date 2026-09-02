# Founder Signal Shortlist — 2026-09-01

**Source state:** `python agency/cli.py status` after signal deduplication  
**Corrected 2026-09-02:** the two Priority-1 BUY signals originally listed here
(`…magnet-b84a3f`, `…foldab-923f7a`) were quarantined at 2026-09-01T15:06:46 with
reason `superseded_by_phase2_economics_refresh`. They have been replaced below by
the live signals `…magnet-500f28` and `…foldab-460ef9`, which are the pair
`docs/phase2-approval.md` references. **Their unit economics do not currently pass
the CAC gate — see `reports/2026-09-02-founder-decision-matrix.md` before
approving.**  
**Pending founder-review signals:** 17  
**Goal:** reduce founder attention to the few decisions that change the roadmap.

---

## Recommended Decision Set

| Priority | Signal ID | Type | Market | Product | Recommended founder action | Why |
|---|---|---|---|---|---|---|
| 1 | `sig-buy-candidate-us-2026-09-01-magnet-500f28` | BUY | US | Magnetic Cable Organizer — 6-Pack Silicone Cord Clips | **Hold — correct economics, then approve staging** | Staging pack is ready, but the record carries a $69.99 placeholder retail against a researched $24.99, and net margin $15.44 fails the 2×CPA gate. |
| 1 | `sig-buy-candidate-us-2026-09-01-foldab-460ef9` | BUY | US | Foldable Silicone Bowl Set — 4-Pack Collapsible Kitchen Bowls | **Hold — correct economics, then approve staging** | Same placeholder retail defect; net margin $17.54 against a $24.00 gate, and margin/COGS 1.91× is under the 2.00× floor. |
| 2 | `sig-sell-kill-cand-cj-sku-magnetic-wristband-556c05` | SELL_KILL | US | Magnetic Tool Wristband with 15 Strong Magnets | **Reject / archive candidate** | Predicted net margin only $10.38; below acceptable paid-acquisition buffer. |
| 3 | `sig-supplier-switch-candidate-us-2026-09-01-portab-360078` | SUPPLIER_SWITCH | US | Portable Neck Fan — Hands-Free Wearable Cooling Device | **Hold** | Demand may exist, but supplier and battery-risk issues make it a distraction from the top-2 shortlist. |
| 3 | `sig-supplier-switch-candidate-us-2026-09-01-magnet-29656b` | SUPPLIER_SWITCH | US | Magnetic Wristband Tool Holder — Hands-Free Screw/Nail/Drill Bit Organizer | **Hold** | Needs verified domestic sourcing before it can re-enter the pilot. |
| 4 | remaining EU BUY / SWITCH / TREND signals | mixed | EU | EU backlog | **Defer** | Current operating contract is US-first. EU items should not compete for founder attention until the US pilot is decided. |

---

## Full Pending List by Bucket

### US Buy Now (staging-prep only) — blocked on economics correction
- `sig-buy-candidate-us-2026-09-01-magnet-500f28`
- `sig-buy-candidate-us-2026-09-01-foldab-460ef9`

### US Hold / Re-source
- `sig-supplier-switch-candidate-us-2026-09-01-magnet-29656b`
- `sig-supplier-switch-candidate-us-2026-09-01-portab-360078`
- `sig-buy-cand-cj-sku-magnetic-cord-6p-1a5ea6` *(parallel US cable-organizer path; merge/recompute before live use)*

### US Kill
- `sig-sell-kill-cand-cj-sku-magnetic-wristband-556c05`

### EU Defer
- `sig-supplier-switch-candidate-electric-jar-vacuum-d9a82d`
- `sig-buy-candidate-mini-thermal-sticker-37c990`
- `sig-buy-candidate-ultrasonic-jewelry-c-7d51b3`
- `sig-supplier-switch-bamboo-drawer-organizers-8b58a4`
- `sig-supplier-switch-cable-management-box-f85219`
- `sig-buy-cloud-key-holder-6e6308`
- `sig-supplier-switch-electric-pepper-grinder-d23b46`
- `sig-supplier-switch-folding-laundry-basket-9e83b9`
- `sig-trend-alert-led-sunset-lamp-d2cbc2`
- `sig-trend-alert-portable-neck-fan-50ca49`
- `sig-sell-kill-electric-pepper-grinder-6c7f6d`

---

## Operating Recommendation

Founder time should be spent on exactly three decisions next:

1. correct the **top 2 US candidates**' unit economics and re-run the gate before
   approving Phase 2 staging,
2. kill the **magnetic wristband** path,
3. defer the **EU backlog** until the US pilot decision is complete.
