---
title: "Day 2 Tutorial — Annotation, Gold Standards & Evaluation"
subtitle: "Learn the pipeline on an easy-to-judge task (CEFR-SP)"
toc: true
---

> **Goal.** By the end of this tutorial you can take an annotated dataset, evaluate a set of model
> predictions against it, and read the precision / recall / F1 / confusion-matrix output. We use an
> *easy-to-judge* task first — CEFR sentence levels — so the mechanics, not the labeling, are the
> challenge. The hard, research-style task comes in the [Day 3 tutorial](./tutorial-day3-move-replication.md).

**Companion notebook:** `day2_gold_standards_and_evaluation.ipynb` — open it directly in Colab (Tohoku Google account, no setup):

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/egumasa/linguistic-data-analysis-II-2026/blob/main/sources/notebooks/day2_gold_standards_and_evaluation.ipynb)

::: {.callout-note}
## Today runs on *frozen* predictions — no API key needed
Day 2 is about learning to **measure** annotation quality, so it doesn't call the model live (that
wobble would just be noise). Instead the model's predictions were computed once and committed to the
repo; the notebook **loads that frozen file**, so everyone's numbers match exactly. You start calling
the model yourself — with a free key — from [Day 3](./tutorial-day3-move-replication.md). See
[Get a free Gemini API key](../resources/tools/gemini-api-key.md).
:::

::: {.callout-note collapse="true"}
## Prefer to run outside Colab? (optional)
This box is only for running the *same* notebook on your own machine. Install the libraries and
launch Jupyter — no key is needed for Day 2 (it reads the frozen predictions file):

```bash
pip install jupyterlab scikit-learn pandas seaborn matplotlib google-genai
jupyter lab                              # then open day2_gold_standards_and_evaluation.ipynb and Run All
```

For the Day 3+ notebooks (which *do* call the model) set `GEMINI_API_KEY`. Full step-by-step (install
`uv`, virtual environment, getting a key): [Python Setup — Run Locally](../resources/tools/python-setup.md).
:::

## The task

Each item is one English sentence; the label is its **CEFR level** (A1–C2). The gold labels were
assigned by language-education professionals, and we kept only sentences where **two annotators
agreed** — so there is a defensible "right answer" for every item.

Dataset: `gold/cefr_sentences.json` (72 items, 12 per level) — build it with the
[CEFR-SP download notebook](../resources/datasets/notebooks/download_cefr_sp.ipynb).
See the [dataset catalog](../resources/datasets/index.md#cefr-sp-the-on-ramp-to-judge) for provenance.

## Step 1 — Look at the gold standard

Open the gold file. Notice the canonical schema — this is the *only* data shape you will see all
week:

```json
[{"id": 1, "text": "He died on 6 October 1837 in Paris.", "label": "A1"}, ...]
```

::: {.callout-tip}
## Annotate a few yourself first
Before running the model, label ~10 sentences by hand (cover the `label` column). Compare with a
partner and compute simple agreement. For CEFR you will mostly agree — hold on to that feeling, then
notice how different it is for the Day 3 discourse task.
:::

## Step 2 — Load the frozen predictions (the pipeline)

In the `day2_gold_standards_and_evaluation` notebook the pipeline is a few named cells. You do **not**
edit them — you just run them:

| Cell | What it does |
|------|--------------|
| `load_gold(path)` | reads the JSON gold file → `gold` |
| `load_predictions(url)` | reads the **frozen** predictions we pre-computed → `predictions` |
| `evaluate(gold, predictions)` | prints precision / recall / F1 + a confusion matrix |
| `show_errors(gold, predictions)` | lists the items the model got wrong |

The predictions were produced once with the prompt below (shown so you know what generated them —
you don't run it today; that's what makes the numbers reproducible):

```text
You are an expert rater of English sentence difficulty using the CEFR scale.
Classify the sentence into exactly one of: A1, A2, B1, B2, C1, C2.
Answer with the level only.

Sentence: {text}
```

## Step 3 — Read the evaluation

- **Precision / recall / F1** per level, plus a macro average.
- The **confusion matrix** shows *which* levels get mixed up. For CEFR you will usually see
  confusions between *adjacent* levels (B1 ↔ B2), rarely between far-apart ones (A1 ↔ C2) — a sign
  the model has the right idea but imprecise thresholds.

## Step 4 — Error analysis

Run `show_errors`. For each miss, ask: is the *gold* defensible, or is this a genuinely borderline
sentence? This question — "is the disagreement the model's fault or the scheme's?" — is the heart of
annotation work, and it returns with force in the Day 3 task.

## What to take to Day 3

You now know the full loop: **load gold → format prompt → call model → evaluate → inspect errors.**
Today you evaluated *frozen* predictions so the numbers held still while you learned the metrics; on
Day 3 you run the **call model** step yourself (with a free API key), and only the *task* gets harder.

➡️ [Day 3 Tutorial — Replicating Kim & Lu with open data](./tutorial-day3-move-replication.md)
