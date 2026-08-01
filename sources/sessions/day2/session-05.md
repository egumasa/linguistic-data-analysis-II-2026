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

- Working in a pair, each annotate the same ~20 sentences by hand against a prepared scheme.
- Read a function's first line and its `help(...)` output to work out what to pass in and what comes back.
- Import the annotation spreadsheet into Colab and compute a simple agreement rate, Cohen's κ, and an annotator-vs-annotator confusion matrix.
- Read the confusion matrix to see *where* you two disagree, then refine the scheme and re-annotate — iterate until agreement is acceptable.
- Adjudicate the remaining disagreements, compare your labels against the published gold standard, and interpret the differences.
- Import your annotations back as a canonical `{id, text, label}` gold set.

::: {.callout-note}
This hands-on is where the **construction** objective is assessed — building a gold standard (operationalizing categories and measuring agreement). Give the annotation itself real care; it's the graded piece.
:::

## Agenda

Works through `day2-s5_gold_standard_construction.ipynb` — a Google Sheets annotation round-trip,
run as six steps **A–F** shared by the slides, the Sheet and Colab.

1. **Draw ~20 sentences** from the provided pool for your track.
2. **Annotate by hand** — each person in the pair annotates the same 20 items in a Google Sheet (two annotator columns, so agreement falls out).
3. **Import the sheet into Colab** and **measure agreement** — percent agreement, Cohen's κ, and an annotator-vs-annotator confusion matrix.
4. **Iterate** — read the confusion matrix to find where the scheme is ambiguous, refine it, and re-annotate the disagreements until agreement is acceptable.
5. **Adjudicate** the remaining disagreements to a `final` label, **compare to the published gold**, and import your set back as canonical JSON.

The Google Sheets round-trip (creating the sheet, annotating, reading it back into Colab) is the time-consuming part — pace yourself and don't skip the iterate/adjudicate steps.

## Reading

No new reading for this session — see the Day 2 reading (Eguchi & Kyle, 2024) in [Session 4](session-04.md) and the optional further reading on the [Readings](../../syllabus/readings.md) page.

## Slides & Colab

<!--
- Notebook (Corpus Lab, steps A–F): [`day2-s5_gold_standard_construction.ipynb`](../../notebooks/day2-s5_gold_standard_construction.ipynb) —
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/egumasa/linguistic-data-analysis-II-2026/blob/main/sources/notebooks/day2-s5_gold_standard_construction.ipynb)
- Slides: [Session 5 slides](../../slides/slides-session-05.html){target="_blank"}
-->
