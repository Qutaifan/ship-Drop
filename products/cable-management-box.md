# Product Validation — Cable Management Box

**Status: PENDING — competitor gate not run.** Everything runnable without a Meta access token is complete. The verdict stays open until the Ad Library gate executes.

## Product
- Name: Cable Management Box (enclosed, ventilated, hides power strips & cables)
- Source/supplier candidate(s): CJdropshipping — EU warehouse (DE/PL) required, see suppliers/cjdropshipping.md
- Retail price target (VAT-inclusive, as the customer pays): UNVERIFIED — see Buying Constraint below
- VAT rate (destination market, e.g. 0.19 for DE): 0.19
- Product cost: UNVERIFIED — requires CJ account
- Shipping cost: UNVERIFIED — requires CJ account
- Import duty per unit: 0 if fulfilled from CJ's EU warehouse; €3 per customs item if shipped direct from China

## 6-Criteria Screen (PROTOCOL-01 / AGENTS.md §4A)
1. Wow Factor (sub-3s emotional hook?): **PASS** — instant "mess to clean" transformation, satisfying visual relief.
2. Problem Solving (what friction does it resolve?): **PASS** — tangled cable nests behind desks/TVs, dust traps, trip hazards — daily eyesore resolved in one box.
3. Visual Appeal (communicable in silent 9:16 video?): **PASS — evidenced, not assumed.** Demo-burden screen: median video 110s, 28% of top results are ≤60s short-form, only 4% skeptic-framed — well within the proven-viral band (control/pepper-grinder at 20%). See reports/2026-08-30-candidate-sweep.md.
4. Healthy Margins: **CONDITIONAL** — depends entirely on landed cost. See Buying Constraint.
5. Low Return Potential (simple/durable mechanics?): **PASS** — solid plastic/wood enclosure, no moving parts, no electronics; ventilated slots prevent overheating.
6. Low Local Retail Availability: **PARTIAL** — basic cable ties/clips are everywhere; *enclosed ventilated boxes for full power strips* are not yet supermarket stock. Erodes over time.

## Competitor Check (Metapi.io — live data 2026-08-30)
- Competitors running ads (need 5–10): **14 ads found** across 5 distinct pages (Imenlength, Gloryboom.LB11, Rigid.PRO, Festivalment.Pro, Esslinger) — **PASS**
- Ads active 30+ days (need ≥3): **1 ad >30 days** (Rigid.PRO running since 2026-07-14) — **MARGINAL** (only 1 of 14 meets 30-day threshold)
- Metapi task: `CgmBMHWcAhg3Z5xN` (DE, active, all ad types, eu_data=true)

**Key findings**:
- Most ads are for **hook-and-loop strips / cable ties** (Imenlength, Gloryboom.LB11, Festivalment.Pro) — accessories, not enclosed cable management boxes
- **Rigid.PRO** runs a camera rig ad since July 14 (47+ days) — not a cable box
- **Esslinger** runs a German-language desk setup ad ("VexelLine") — peripheral organizer
- **No true enclosed ventilated cable management box ads** found. Competitors are selling cable *accessories*, not the box product.

Run with: `python3 scripts/ad_library.py "cable management box" --countries DE,FR,NL`

## True Margin Matrix
`Net Margin = (Retail / (1 + VAT)) − (Product Cost + Shipping + Import Duty) − (0.03 × Retail)`
- Net Margin: __ (cannot compute — landed cost unknown)
- Must be ≥3x COGS and >€15: PENDING

### Buying Constraint — the number to negotiate against

Solving both gates for the maximum landed cost (product + shipping + duty) at DE VAT 19%:

| Gross retail | Max landed cost | Net margin at that cost |
|---|---|---|
| €24.90 | €5.04 | €15.13 |
| €29.90 | €6.06 | €18.16 |
| €34.90 | €7.07 | €21.20 |
| €39.90 | €8.08 | €24.24 |
| €44.90 | €9.10 | €27.28 |

**Rule: landed cost must be ≤ 20.3% of the VAT-inclusive retail price.** The 3x-COGS gate binds at every price point — the >€15 floor never becomes the constraint above €24.90. Below **€18.51 gross retail the >€15 net gate is unreachable at any cost**, even a free product, which is the real floor criterion 4 should state rather than €20.

**Consequence for sourcing**: at a €34.90 target, total landed cost must not exceed €7.07. If CJ quotes €6 product + €3 EU shipping, the product **fails** — and it fails by a margin no ad creative can recover. This number is the buying constraint, not an aspiration.

## Regulatory Check
- De Minimis / sourcing region: **EU warehouse mandatory.** Direct-from-China adds €3 duty per customs item plus import VAT and ~€2 handling on every order, which alone consumes ~70% of the €7.07 cost budget at a €34.90 retail.
- EU AI Act disclosure needed (AI imagery/support)?: Yes if AI product imagery is used — disclosure on the PDP.
- FTC dynamic pricing rule-based (not user-tracked)?: N/A for EU-first; rule-based only if applied.
- **WEEE + battery obligations**: **NONE** — non-electrical, no battery.
- **REACH / RoHS**: Plastic enclosure — verify SVHC-free, RoHS compliant for EU.

## Verdict
**FAIL** — rejected 2026-08-30 on independent lines of evidence. Not blocked; decided.

1. **Competitor gate: FAIL on sustained profitability.** 9 distinct advertisers clears the >=5 requirement, but **0 ads have run 30+ days** - all 14 started 2026-08-19, an 11-day window. PROTOCOL-01 wants aged ads precisely because they prove someone is still paying to run them. Nine advertisers appearing at once on short bursts under throwaway page names (Denseheavy N, Foildash Global, Gloryboom.LB11) is a product being mass-tested, not one proven profitable. Caveat: every record shares an identical stop date of 2026-08-29, more likely the dataset's snapshot boundary than a real stop - the gate still fails on start dates alone.

2. **Supplier cost: FAIL.** CJ organizer bag landed $11.63 to Germany against a EUR 9.10 ceiling. The one variant that clears it ($5.49) is a 13.5x9x5cm box that cannot carry a EUR 30-45 price.

3. **Criterion 6 (low local retail availability): FAIL.** Stocked by IKEA, Action, Lidl and Kaufland. Local availability caps the achievable price, which drags Criterion 4 down with it — the margin model needs EUR 30-45 gross retail and the shelf price is a fraction of that. No creative recovers a product whose market price is a third of what the unit economics require.

**Provenance note**: this candidate entered the pipeline through the 2026-08-30 candidate sweep, whose skeptic-ratio figures did not reproduce against its own stored data (9 of 10 wrong, every error optimistic). See `reports/2026-08-30-sweep-audit.md`. The ranking that selected it was not evidence.
