---
title: "Day 2 Tutorial — Annotation, Gold Standards & Evaluation"
subtitle: "Learn the pipeline on an easy-to-judge task (CEFR-SP)"
toc: true
---

> **Goal.** By the end of this tutorial you can take an annotated dataset, run an LLM over it with a
> fixed prompt, and read the precision / recall / F1 / confusion-matrix output. We use an
> *easy-to-judge* task first — CEFR sentence levels — so the mechanics, not the labeling, are the
> challenge. The hard, research-style task comes in the [Day 3 tutorial](./tutorial-day3-move-replication.md).

**Companion notebook:** `02_gold_and_eval.ipynb` — open it directly in Colab (Tohoku Google account, no setup):

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/egumasa/linguistic-data-analysis-II-2026/blob/main/sources/resources/tutorials/02_gold_and_eval.ipynb)

::: {.callout-note collapse="true"}
## Prefer to run outside Colab? (optional)

**In class you need nothing but Colab** — the notebook uses Colab's free built-in Gemini, no API
key, no install. This box is only for those who want to run the *same* notebook on their own
machine. The notebook auto-detects it isn't in Colab and calls a real LLM API instead; it picks the
provider from whichever key you set (`GEMINI_API_KEY`, `ANTHROPIC_API_KEY`, or `OPENAI_API_KEY`).

Quick version — install the libraries, set one key, launch Jupyter:

```bash
pip install jupyterlab scikit-learn pandas seaborn matplotlib google-genai anthropic openai
export GEMINI_API_KEY=your-key-here      # or ANTHROPIC_API_KEY / OPENAI_API_KEY
jupyter lab                              # then open 02_gold_and_eval.ipynb and Run All
```

Full step-by-step (install `uv`, virtual environment, getting an API key):
[Python Setup — Run Locally](../tools/python-setup.md).
:::

## The task

Each item is one English sentence; the label is its **CEFR level** (A1–C2). The gold labels were
assigned by language-education professionals, and we kept only sentences where **two annotators
agreed** — so there is a defensible "right answer" for every item.

Dataset: `gold/cefr_sentences.json` (72 items, 12 per level) — build it with the
[CEFR-SP download notebook](../datasets/notebooks/download_cefr_sp.ipynb).
See the [dataset catalog](../datasets/index.md#cefr-sp-the-on-ramp-to-judge) for provenance.

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

## Step 2 — Run a fixed prompt (the pipeline)

In the `02_gold_and_eval` notebook the pipeline is four named cells. You do **not** edit them — you
just run them:

| Cell | What it does |
|------|--------------|
| `load_gold(path)` | reads the JSON gold file → `gold` |
| `run_prompt(prompt, gold)` | sends each `text` to the LLM → `predictions` |
| `evaluate(gold, predictions)` | prints precision / recall / F1 + a confusion matrix |
| `show_errors(gold, predictions)` | lists the items the model got wrong |

A minimal starting prompt:

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
On Day 3 the loop is identical; only the *task* gets harder.

➡️ [Day 3 Tutorial — Replicating Kim & Lu with open data](./tutorial-day3-move-replication.md)
