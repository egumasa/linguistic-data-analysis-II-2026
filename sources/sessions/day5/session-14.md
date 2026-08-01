---
title: "Session 14: Project Work — Finalize Report & Notebook"
subtitle: "Day 5 · Project Finalization & Presentations (5-2)"
toc: true
---

<!-- BEING-PREPARED-BANNER -->
::: {.callout-warning appearance="simple"}
## 🚧 Being prepared
This page is being finalized ahead of the course (**Aug 3–7, 2026**) and may be incomplete or change before your session. The [syllabus](/syllabus/index.md) and [readings](/syllabus/readings.md) are ready now.
:::


## Learning objectives

By the end of this session you will be able to:

- Attribute concrete errors to the **model** or to the **scheme**, with a reason for each.
- Write limitations that apply to *your* run rather than generic ones.
- Assemble the submission bundle and confirm the notebook runs top to bottom on a fresh runtime.
- Build five slides that map onto the five report sections.

## Agenda

1. **Error analysis** — `show_errors`, then cross-reference against the rows you adjudicated in Session 12. Overlap between the two is a finding, not a failure.
2. **Write the report** — `export_results` gives you the scaffold; you write the four things it cannot compute.
3. **Build the bundle** — `python scripts/make_submission.py --group <yours>`, then check what it says is missing.
4. **Restart and Run all** — if your notebook only works in the session you built it in, it does not reproduce.
5. **Five slides**, one per report section.

## Reading

No new reading — Day 5 is project work only (see the [Readings](../../syllabus/readings.md) page).

## Slides & Colab

<!-- Slides: [Session 14 slides](../../slides/slides-session-14.html){target="_blank"} -->

## Mini-project

`06_report.ipynb` — error analysis and export — then submission.

- What goes in the bundle, and how to turn it in: [Deliverables](../../final-project/deliverables.md).
- What earns marks: [Rubric](../../final-project/rubric.md).

::: {.callout-warning}
## The placeholders are not filler
`export_results` writes the report in *italics* where you are meant to write. A section left
as the scaffold's own prose scores zero — and `make_submission.py` will warn you if any are
still there.
:::
