---
title: "Session 11: Plenary Pipeline Assembly"
subtitle: "Day 4 · Methodology & Pipeline Assembly (4-2)"
toc: true
---

<!-- BEING-PREPARED-BANNER -->
::: {.callout-warning appearance="simple"}
## 🚧 Being prepared
This page is being finalized ahead of the course (**Aug 3–7, 2026**) and may be incomplete or change before your session. The [syllabus](/syllabus/index.md) and [readings](/syllabus/readings.md) are ready now.
:::


## Learning objectives

By the end of this session you will be able to:

- Describe the whole pipeline as a chain of inputs and outputs — what each step **consumes** and what it **produces**.
- Point to where in Days 1–4 you already ran each call, and use the same call form again.
- Write your group's `PLAN.md`: track, label set, sampling settings, the dev/test ratio, who annotates what, **which agreement statistics you owe and which one number you will lead with** — and the one prompt change you predict will help.

## Agenda

1. **The pipeline, in one diagram** (~15 min) — pool → sample → sheet → adjudicated gold → **dev / test** → prompt rounds on dev → the held-out run → report, with each arrow's data shape named, and the 04/05 file boundary that keeps the test half closed. Plus the inventory and its ancestor column: every call has one, in Days 1–4.
2. **Write `PLAN.md`** (~45 min) — in your groups. The instructor comes round, reads it, and signs it off.
3. **End-state check** (~25 min) — each group states its I/O contract out loud: *"`03_annotate` consumes the filled-in sheet and our adjudication, and produces the gold set."*

Not a re-teach. You have run every one of these helpers already; today is about being able to **name the structure** — which is exactly what the Q&A will ask you to do.

## Reading

No new reading for this session — see the Day 4 reading (Abdurahman et al., 2025, *read in full*) in [Session 10](session-10.md) and on the [Readings](../../syllabus/readings.md) page.

## Slides & Colab

<!-- Slides: [Session 11 slides](../../slides/slides-session-11.html){target="_blank"} -->

## Mini-project

- The inventory: [what you have to work with](../../final-project/pipeline-cheatsheet.md).
- What you write today: [the `PLAN.md` gate](../../final-project/plan.md).
- Where the work happens: [`lda2-final-template`](https://github.com/egumasa/lda2-final-template).

::: {.callout-important}
## No group calls the model until `PLAN.md` is signed
Steps 1 and 2 — sampling and annotation — need no model at all, so there is plenty to get on
with. The gate exists because a mismatched label set costs an hour to unpick *after* you have
spent quota on it.
:::
