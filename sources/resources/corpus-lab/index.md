---
title: "Corpus Lab"
subtitle: "Hands-on assignments"
toc: true
---

**Corpus Lab** is the hands-on practice you complete each day. It now lives **inside the day's
notebook** as *Part B* — so the tutorial and its lab are one file you submit together. See the
[Daily Notebooks](../tutorials/index.md) index for all five.

::: {.callout-important}
## These are autograded — so they must be reproducible
Corpus Labs are checked automatically, so your results have to come out the same every run. The
**Day 1–2 labs are keyless** (Python practice; metrics on *frozen* predictions). From **Day 3** the
labs call the model, so you use the **Gemini API** with `temperature=0` + a fixed seed and
[a free key](../tools/gemini-api-key.md) — and you **freeze your predictions to JSON** so the grader
re-runs your analysis on exactly the outputs you saw.
:::

## Available now

- **Day 1 · [`day1_python_and_first_llm.ipynb`](../tutorials/day1_python_and_first_llm.ipynb)** —
  Python practice exercises with a self-check.
- **Day 2 · [`day2_gold_standards_and_evaluation.ipynb`](../tutorials/day2_gold_standards_and_evaluation.ipynb)** —
  **[Coding the metrics from scratch](../code-examples/python/index.md)**: implement precision,
  recall, F1, and Cohen's κ by hand, then check your work against scikit-learn. The evaluation
  formulas you rely on in the final project, built from the ground up.

::: {.callout-note}
## Coming soon
The Day 3–5 Corpus Lab sections (your own prompt-iteration study, gold-set QC & adjudication, and
the report scaffold) are still being prepared. Each is marked as a **🚧 TODO** section inside its
day notebook and draws on [Datasets](../datasets/index.md) and the
[mini-project tracks](../datasets/mini-project-tracks.md).
:::
