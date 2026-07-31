---
title: "Session 13: Project Work — Prompt Iteration & Final Evaluation"
subtitle: "Day 5 · Project Finalization & Presentations (5-1)"
toc: true
---

<!-- BEING-PREPARED-BANNER -->
::: {.callout-warning appearance="simple"}
## 🚧 Being prepared
This page is being finalized ahead of the course (**Aug 3–7, 2026**) and may be incomplete or change before your session. The [syllabus](/syllabus/index.md) and [readings](/syllabus/readings.md) are ready now.
:::


## Learning objectives

By the end of this session you will be able to:

- Change **one thing** per prompt round, predict its effect, and test it against your gold set.
- Read a confusion matrix to decide *what to change next*, rather than guessing.
- Freeze a final run to a file, and explain why a seed alone is not enough.
- Report plain and weighted κ, and say which one your label set justifies.

## Agenda

1. **Round 1 and 2** — few-shot, then a change of your own. For each: what did you change, and *why did you expect it to help?*
2. **Read the errors between rounds** — the confusion matrix tells you which pair to attack.
3. **The final run** — raise `N_PER_CLASS`, run **once**, `save_predictions`.
4. **Everything after that reads the frozen file**, not the model.

Budget your quota: the free tier gives about 500 calls a day per key. Iterate small.

## Reading

No new reading — Day 5 is project work only (see the [Readings](../../syllabus/readings.md) page).

## Slides & Colab

<!-- Slides: [Session 13 slides](../../slides/slides-session-13.html){target="_blank"} -->

## Mini-project

`notebooks/mini_project.ipynb` — **step 4**.

::: {.callout-important}
## The final run is one run, by one person
Runtimes are per-person, and your reported numbers have to come out of a single frozen file.
Decide who the driver is before you start. If their daily quota runs out, hand the role — and
the runtime — to someone else; the files stay put in your shared Drive folder.
:::
