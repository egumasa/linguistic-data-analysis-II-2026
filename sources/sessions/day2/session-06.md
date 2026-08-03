---
title: "Session 6: Gold Standards & Evaluation Metrics"
subtitle: "Day 2 · Annotation, Gold Standards & Metrics (2-3)"
toc: true
---
<!-- BEING-PREPARED-BANNER -->


## Learning objectives

By the end of this session you will be able to:

- Decide, for a single item, which of **TP · FP · FN · TN** it lands in, and write that decision as an `if`/`elif`.
- **Loop** over a labelled set, **store** one verdict per item, and **tally** the four counts.
- Build a **confusion matrix** from those counts and read it — which errors are misses, and which are false alarms.
- Compute **precision, recall, F1** and **Cohen's κ** *from scratch*, and say what question each one answers.
- Reproduce all of it with **scikit-learn** on the real six-level task — `classification_report`, `confusion_matrix`, `cohen_kappa_score` — and choose between **plain and weighted κ** depending on whether your labels are ordered.
- Read a gold file as a `{id, text, label}` list of dicts, and recognise `with open(...)` for reading/writing data files.
- Interpret the metrics critically — what a high or low score does and doesn't tell you.

## Agenda

Yesterday's question was *"do two people agree?"* Today's is **"is the model any good?"** — the same tools, with one column swapped. Works through `day2-s6_evaluation_metrics.ipynb` in **two passes** over the same data.

**Pass 1 — you build the metrics** *(notebook Part A)*. On a single yes/no question — *is this sentence advanced?* — so there are four counts to track instead of thirty-six, and twelve items you can count by hand.

1. Collapse six CEFR levels to one yes/no question, and name the **positive class**.
2. Decide one item with an `if`, then all four outcomes with an `if`/`elif` ladder.
3. Wrap it in a function, **loop** over the items, and **store** every verdict.
4. **Tally** the verdicts → build the **confusion matrix** → read it.
5. Derive **precision, recall, F1** and **Cohen's κ** from those same four numbers.
6. Re-run on all 72 items, then **check your code against scikit-learn**.

**Pass 2 — scikit-learn at scale** *(notebook Part B)*. The real six-level task: `classification_report` as one-vs-rest run six times, the confusion matrix read **down the columns**, plain vs. quadratic-weighted κ, and error analysis — *"is the disagreement the model's fault, or the scheme's?"*

The session closes with the **作戦会議** strategy huddle: turn today's mechanics onto your own project track — a draft annotation scheme, your gold source, and the agreement you would accept.

The whole session runs on **frozen predictions** — no API key, no live model — so everyone's numbers come out identical every run. You'll run the model live yourself from Day 3 onward; today the focus is *measuring* quality, not producing it.

::: {.callout-tip}

## Keep the slides and Colab open side by side

The code is on the slides, line by line, next to what it prints — and you type it in Colab as we go. If you fall behind, copy the cell from the slide, run it, and rejoin.
:::

## Reading

No new reading for this session — see the Day 2 reading (Eguchi & Kyle, 2024) in [Session 4](session-04.md) and the optional further reading on the [Readings](../../syllabus/readings.md) page.

## Slides & Colab

- Notebook (session 6): [`day2-s6_evaluation_metrics.ipynb`](../../notebooks/day2-s6_evaluation_metrics.ipynb) —
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/egumasa/linguistic-data-analysis-II-2026/blob/main/sources/notebooks/day2-s6_evaluation_metrics.ipynb)
