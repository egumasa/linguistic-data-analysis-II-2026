---
title: "Session 5: Hands-on — Gold-Standard Annotation & Agreement"
subtitle: "Day 2 · Annotation, Gold Standards & Metrics (2-2)"
toc: true
---

<!-- BEING-PREPARED-BANNER -->
::: {.callout-warning appearance="simple"}
## 🚧 Being prepared
This page is being finalized ahead of the course (**Aug 3–7, 2026**) and may be incomplete or change before your session. The [syllabus](/syllabus/index.md) and [readings](/syllabus/readings.md) are ready now.
:::


## Learning objectives

By the end of this session you will be able to:

- Draw a sample of sentences and annotate them by hand against a prepared scheme.
- Compute a simple agreement rate (and Cohen's κ) between two annotators, and adjudicate the disagreements.
- Compare your adjudicated labels against the published gold standard and interpret the differences.
- Import your annotations back as a canonical `{id, text, label}` gold set.

::: {.callout-note}
This hands-on is where the **construction** objective is assessed — building a gold standard (operationalizing categories and measuring agreement). Give the annotation itself real care; it's the graded piece.
:::

## Agenda

Works through **Part B** of the Day 2 notebook — a Google Sheets annotation round-trip.

1. **Draw ~20 sentences** from the provided pool for your track.
2. **Annotate by hand** in a Google Sheet (two annotator columns, so agreement falls out).
3. **Measure agreement** — percent agreement + Cohen's κ — then **adjudicate** the disagreements to a `final` label.
4. **Compare to the published gold** and import your set back as canonical JSON.

The Google Sheets round-trip (creating the sheet, annotating, reading it back) is the time-consuming part — pace yourself and don't skip the adjudication step.

## Reading
<!-- to be added -->

## Slides & Colab

- Notebook (tutorial + Corpus Lab): [`day2_gold_standards_and_evaluation.ipynb`](../../notebooks/day2_gold_standards_and_evaluation.ipynb) —
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/egumasa/linguistic-data-analysis-II-2026/blob/main/sources/notebooks/day2_gold_standards_and_evaluation.ipynb)
<!-- Slides: [Session 5 slides](../../slides/slides-session-05.html){target="_blank"} -->
