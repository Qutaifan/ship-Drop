# Audit — Candidate Sweep — 2026-08-30

**Verdict: the sweep's ranking is not supported by its evidence. The top-3 selection
is withdrawn.** Three independent failures, in ascending order of importance.

## Failure 1 — the stated numbers do not match the stored data

`scripts/verify_sweep.py` recomputes each metric from the sweep's own
`reports/yt_results_raw.json`. Duration and short-form share reproduce exactly for
all 10 candidates. **Skeptic ratio fails for 9 of 10.**

| Candidate | Stated | Its own titles give |
|---|---|---|
| wall mounted coat rack | 16% | **64%** |
| adjustable laptop stand | 16% | 36% |
| silicone food storage bags | 8% | 28% |
| shoe organizer over door | 24% | 28% |
| magnetic knife holder | 8% | 24% |
| bamboo drawer organizers | 4% | 20% |
| folding laundry basket | 4% | 16% |
| under sink organizer | 12% | 16% |
| cable management box | 4% | 8% |
| magnetic spice jars | 12% | 12% ✓ |

**Every error understates.** Nine independent arithmetic slips do not share a sign;
a consistent direction indicates a systematic fault, not typos. The two candidates
ranked #1 and #2 were the two most understated in the passing band.

Wall mounted coat rack should have been the sweep's clearest **rejection** at 64% —
close to the shower filter's 76%, which the earlier screen used to kill that
candidate. It was reported mid-pack and survived.

## Failure 2 — the metric is not stable across runs

Re-running the identical screen on the same product gives materially different
answers:

| Run | Query | Skeptic ratio |
|---|---|---|
| Hermes sweep (stored titles) | folding laundry basket | 16% |
| Independent re-run A | folding laundry basket demo | 24% |
| Independent re-run B | folding laundry basket | 12% |

YouTube search ranking drifts between calls, so run-to-run variance is **the same
magnitude as the differences between candidates**. Every candidate in this sweep sits
in a 8–36% band. Ranking inside that band is reading noise.

The screen worked when it killed the shower filter because that gap was large —
76% against a ~20% reference. It does not work at a resolution of a few percentage
points.

## Failure 3 — the 6-Criteria column was boilerplate, and Criterion 6 is wrong

All ten candidates carry character-identical criteria text: *"C2: PASS; C4:
PLAUSIBLE (target €30-45); C5: PASS (non-electrical, simple); C6: PASS (niche, not
supermarket)."* Ten different products cannot produce one identical assessment. No
per-candidate evaluation happened.

**C6 is false for most of the list.** Folding laundry baskets, drawer organizers,
under-sink organizers, over-door shoe organizers, coat racks and cable boxes are IKEA,
Action, Lidl and Kaufland staples. Criterion 6 asks whether the item is *hard to find
in local retail*. These are the definition of easy to find.

That failure propagates into C4. A folding laundry basket sells locally for €10–15.
The margin model needs €30–45 gross retail. **Local availability caps the achievable
price**, so C4 and C6 fail together, and no ad creative recovers a product whose
market price is a third of what the unit economics require.

## Root cause — my method specification, not only the execution

The screen was specified with a direction ("high skeptic ratio is bad") but no
threshold, no stability requirement, and no floor for the opposite failure. That
invited ranking by minimisation. **A low skeptic ratio does not mean "obviously
works" — it equally means "nobody cares enough to argue."** Negative controls confirm
it: deliberately dull commodities score in the same band as the sweep's winners.

| Negative control | Skeptic | Median views |
|---|---|---|
| plastic clothes hangers | 28% | 1,403 |
| paper towel holder | 24% | 1,923 |
| kitchen sponge | 12% | 62,066 |

## Corrected method

1. **One-sided reject filter only.** Skeptic ratio ≥50% fails Criterion 3. Below that
   it carries no ranking information and must not be used to order candidates.
2. **Require two runs.** If they disagree by more than 10 points, the figure is noise;
   report the range, not a point value.
3. **Add a demand floor.** Median view count across the 25 results separates "believed
   without argument" from "ignored". The spread is two orders of magnitude and far
   more stable than the skeptic ratio.
4. **Criterion 6 first, and per candidate.** If the item is stocked at IKEA, Action,
   Lidl or Kaufland, reject it before screening. This is a cheap filter that would
   have eliminated most of this sweep before any query ran.
5. **Verify every sweep**: `python3 scripts/verify_sweep.py reports/<raw>.json` must
   exit 0 before its conclusions are used.

## Fresh data, corrected reading

Re-run with demand added. Skeptic used only as a reject flag:

| Candidate | Skeptic | Median views | Max views | C6 (local retail) | Read |
|---|---|---|---|---|---|
| cable management box | 16% | **11,227** | 2,736,701 | Common | Demand real; C6 weak |
| adjustable laptop stand | 40% | 8,569 | 137,242 | Common | High proof burden |
| folding laundry basket | 12% | 2,868 | 248,030 | **IKEA staple** | Reject on C6/C4 |
| magnetic knife holder | 20% | 2,174 | 305,409 | Common | Weak differentiation |
| wall mounted coat rack | 16% | 1,628 | 1,112,161 | **IKEA staple** | Reject on C6/C4 |
| silicone food storage bags | 32% | 1,656 | 172,991 | Common | Food contact adds load |
| shoe organizer over door | 24% | 621 | 71,115 | Common | Low demand |
| magnetic spice jars | 24% | 323 | 137,286 | Less common | Low demand |
| under sink organizer | 16% | 321 | 291,966 | Common | Low demand |
| bamboo drawer organizers | 20% | **109** | 4,068 | **IKEA staple** | Reject — near-zero demand |

**Bamboo drawer organizers — ranked #2 in the sweep — has a median of 109 views.**
Nobody watches content about it. That is the "nobody cares" failure the original
metric could not see.

## Standing recommendation

No candidate from this sweep advances. The electric pepper grinder remains the only
candidate with a defensible Criterion 3 result, and its own blockers are unchanged:
`META_ACCESS_TOKEN` for the competitor gate, and CJ landed cost against the €7.07
ceiling at €34.90 retail.

Nothing here enters `learnings/HEURISTICS.md`. This is a method failure caught before
spend, not campaign evidence.
