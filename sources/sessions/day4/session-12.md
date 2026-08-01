---
title: "Session 12: Project Work — Sample & QC the Gold Set"
subtitle: "Day 4 · Methodology & Pipeline Assembly (4-3)"
toc: true
---

<!-- BEING-PREPARED-BANNER -->
::: {.callout-warning appearance="simple"}
## 🚧 Being prepared
This page is being finalized ahead of the course (**Aug 3–7, 2026**) and may be incomplete or change before your session. The [syllabus](/syllabus/index.md) and [readings](/syllabus/readings.md) are ready now.
:::


## Learning objectives

By the end of this session you will be able to:

- Draw a **balanced** subset from your track's pool, and explain why balance matters for precision, recall, F1 and the confusion matrix.
- Annotate a sample **independently and blind**, and interpret your percent agreement and Cohen's κ.
- Adjudicate your disagreements into a single agreed gold set, and record *what changed*.
- Run a baseline prompt to get a number to beat.

## Agenda

1. **Sample + create the sheet** (~20 min) — `sample_pool`, then `create_annotation_sheet`.
2. **Annotate blind** (~25 min) — two of you, `CoderA` and `CoderB`, no peeking at the published label.
3. **Agreement → disagreements → adjudicate** (~25 min) — the heart of the session. Where you disagreed with each other tells you which label boundaries are genuinely fuzzy.
4. **Baseline prompt** (~10 min) — at `N_PER_CLASS = 2`, so it finishes inside the slot.

This is the same A–F round-trip you did by hand in [Session 5](../day2/session-05.md), now on your own track and your own data.

## Reading

No new reading for this session — see the Day 4 reading (Abdurahman et al., 2025, *read in full*) in [Session 10](session-10.md) and on the [Readings](../../syllabus/readings.md) page.

## Slides & Colab

- Notebook: [`day4_pipeline_and_sampling.ipynb`](../../notebooks/day4_pipeline_and_sampling.ipynb) — sample a balanced subset, then hand off to the project template —
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/egumasa/linguistic-data-analysis-II-2026/blob/main/sources/notebooks/day4_pipeline_and_sampling.ipynb)
- Project notebooks: [`lda2-final-template/notebooks/`](https://github.com/egumasa/lda2-final-template/tree/main/notebooks) —
  open them from your group's Drive folder, not from GitHub, so you are working on your own copy.

<!-- Slides: [Session 12 slides](../../slides/slides-session-12.html){target="_blank"} -->

## Mini-project

Work in the [project template](https://github.com/egumasa/lda2-final-template) —
**`01_build_pool_<track>`, `02_sample` and `03_annotate`**. None of the three calls the model,
so nothing here waits on the `PLAN.md` gate.

::: {.callout-important}
## Your adjudicated gold is what the model gets scored against
Not the published labels. That is what makes this session load-bearing rather than a warm-up:
the boundaries you argue about here are the ones you will point at on Day 5 when you explain
why the model missed something.
:::

::: {.callout-tip}
## dev is the fast set
One round at full size is ~40 model calls and several minutes of enforced pacing. That is what
the dev/test split at the end of `03_annotate` is for: you iterate against the dev half, a
dozen or so items, and your sample stays at full size throughout.
:::
