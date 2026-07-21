---
title: "Session 6: Gold Standards & Evaluation Metrics"
subtitle: "Day 2 · Annotation, Gold Standards & Metrics (2-3)"
toc: true
---

<!-- BEING-PREPARED-BANNER -->
::: {.callout-warning appearance="simple"}
## 🚧 Being prepared
This page is being finalized ahead of the course (**Aug 3–7, 2026**) and may be incomplete or change before your session. The [syllabus](/syllabus/index.md) and [readings](/syllabus/readings.md) are ready now.
:::


## Learning objectives

By the end of this session you will be able to:

- Read a gold file as a `{id, text, label}` list of dicts, and recognise `with open(...)` for reading/writing data files.
- Define precision, recall, and F1, and read them off a `classification_report`.
- Read a confusion matrix and say which classes a model confuses.
- Interpret the metrics critically — what a high or low score does and doesn't tell you.

## Agenda

Works through **Part A** of the Day 2 notebook, which runs on **frozen predictions** — no API key, no live model, so everyone's numbers come out identical every run.

1. **Warm-up: what a gold file is** — parse a `{id, text, label}` record, index into it, and meet `with open(...)` for files.
2. **Load the gold standard and the frozen predictions** the fixed prompt produced.
3. **Read the evaluation** — precision / recall / F1 from a `classification_report`, then the **confusion matrix**.
4. **Error analysis** — which classes get confused, and what that implies.

You'll run the model live yourself from Day 3 onward; today the focus is *measuring* quality, not producing it.

## Reading

- Abdurahman, S., Salkhordeh Ziabari, A., Moore, A. K., Bartels, D. M., & Dehghani, M. (2025). A primer for evaluating large language models in social-science research. *Advances in Methods and Practices in Psychological Science, 8*(2). <https://doi.org/10.1177/25152459251325174>

## Slides & Colab

- Notebook (tutorial + Corpus Lab): [`day2_gold_standards_and_evaluation.ipynb`](../../notebooks/day2_gold_standards_and_evaluation.ipynb) —
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/egumasa/linguistic-data-analysis-II-2026/blob/main/sources/notebooks/day2_gold_standards_and_evaluation.ipynb)
<!-- Slides: [Session 6 slides](../../slides/slides-session-06.html){target="_blank"} -->
