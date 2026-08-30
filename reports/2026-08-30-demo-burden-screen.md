# Demo-Burden Screen — 2026-08-30

**Method built with Agent-Reach (YouTube channel, no login, no API fee).**
Purpose: test criterion 3 — *can the value proposition be communicated silently in
9:16 video?* — with evidence instead of judgement, **before** any ad spend.

## Method

For each candidate, pull the top 25 YouTube results and measure three things:

1. **Median video duration** — how long the market takes to explain the product.
2. **Short-form share (≤60s)** — whether the product survives in short form at all.
3. **Skeptic-framing ratio** — share of titles containing *are / does / really /
   worth / test / review*. This is a proxy for **proof burden**: how much evidence a
   buyer demands before believing the product works.

A control product with known short-form virality is included to calibrate the scale.

## Results

| Candidate | Median duration | Short-form ≤60s | Skeptic framing |
|---|---|---|---|
| A — Hard water shower filter | **281s** (4m41) | **2/25 (8%)** | **19/25 (76%)** |
| B — Electric pepper grinder | **76s** | **11/25 (44%)** | 5/25 (20%) |
| C — Cable organizer *(control, known viral)* | 116s | 5/25 (20%) | 5/25 (20%) |

Representative titles for A: *"Are Shower Filters Worth It For Your Skin?"*,
*"Unbiased, Data-Driven Review"*, *"I Lab Tested the Weddell Duo…"*,
*"Does It Actually Filter Water? Chemical Test!"*, *"Don't Buy … Before Watching!"*

## What the data reveals

**The hard water shower filter fails criterion 3, and the market has already proved
it.** Three quarters of the top content is framed as skeptical interrogation, the
median explainer runs nearly five minutes, and short form barely exists in the
category at 8%. Buyers do not accept this product on sight — they demand lab tests
and chemical strips. A benefit that requires a chemical test to demonstrate cannot
be carried by a 3-second silent hook, which is the entire premise of PROTOCOL-02.

The control confirms the scale is measuring something real: a product with known
short-form virality sits at 20% skeptic framing, right beside the pepper grinder,
and far from the filter's 76%.

**The pepper grinder is the inverse.** Median 76 seconds, 44% short form, 20%
skeptic. It is demonstrable — one hand, grinding, done — and carries almost no proof
burden.

## Reranking

| Rank | Was | Now | Reason |
|---|---|---|---|
| 1 | Shower filter | **Electric pepper grinder** | Demonstrable in short form; its cost is WEEE/battery compliance — a **priceable** overhead |
| 2 | Pepper grinder | **Shower filter** | Fails criterion 3 on evidence; also a named-brand, review-driven category (Weddell, AquaBliss, AquaTru, WaterScience, IonDrops, Filterbaby) — weak on criterion 6 |
| 3 | Tech organizer pouch | unchanged | Still undifferentiated |

**A priceable compliance cost beats an unsolvable creative problem.** WEEE and battery
registration are known numbers that go into the margin sheet. "Make an invisible
benefit obvious in three silent seconds" is not a number, and no budget fixes it.

## Status of this method

This screen is **unvalidated**. It correctly ranked one known-viral control, which is
n=1 and proves nothing on its own. It is a pre-screen that reorders candidates and
costs nothing to run — it is **not** a gate, and it must not be written into
`learnings/HEURISTICS.md` until a real campaign has tested it. PROTOCOL-03 admits
heuristics from closed campaigns only; promoting a research hunch into the ledger is
exactly the contamination the lifecycle exists to prevent.

## Reproduce

```
yt-dlp "ytsearch25:<product> demo" --flat-playlist --dump-json --no-warnings
```
