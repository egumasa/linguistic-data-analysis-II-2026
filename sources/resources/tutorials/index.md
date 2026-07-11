---
title: "Daily Notebooks"
subtitle: "One notebook per day — tutorial + Corpus Lab in a single file"
toc: true
---

Each day has **one Colab notebook** that you work through top to bottom and submit at the end of the
day. Every notebook has two parts:

- **Part A · Tutorial** — the guided, run-along section you do together in class.
- **Part B · Corpus Lab** — the independent hands-on practice for that day.

You open each notebook directly in Colab (Tohoku Google account, no setup), **Run all**, then
**File → Download → Download `.ipynb`** and submit that one file.

::: {.callout-note}
## The pipeline is the same all week
**load gold → format prompt → call model → evaluate → inspect errors.** Only the *task* and the
*prompt* change. The datasets behind these notebooks are catalogued under
[Datasets](../datasets/index.md).
:::

::: {.callout-tip}
## Which backend each day uses
- **Day 1** — Colab's built-in Gemini (`colab.ai`), keyless. Your first live call; notice it varies.
- **Day 2** — *no model call.* You evaluate **frozen** predictions so the metrics numbers hold still.
- **Day 3 onward** — you run the model yourself via the **Gemini API** (`temperature=0` + a fixed
  seed, so results are reproducible for the autograded labs). One-time setup:
  [get a free key](../tools/gemini-api-key.md).
:::

## The notebooks

| Day | Notebook | Tutorial (Part A) | Corpus Lab (Part B) |
|---|---|---|---|
| 1 | [`day1_python_and_first_llm.ipynb`](./day1_python_and_first_llm.ipynb) | Python basics + your first LLM call | Python practice exercises (self-checked) |
| 2 | [`day2_gold_standards_and_evaluation.ipynb`](./day2_gold_standards_and_evaluation.ipynb) | The pipeline on CEFR-SP (P/R/F1 + confusion matrix) | Code the metrics from scratch, checked vs. scikit-learn |
| 3 | [`day3_prompt_design.ipynb`](./day3_prompt_design.ipynb) | Zero-shot → few-shot → chain-of-thought on CEFR | Your own prompt-iteration study *(coming soon)* |
| 4 | [`day4_pipeline_and_sampling.ipynb`](./day4_pipeline_and_sampling.ipynb) | Sample a balanced gold subset from a pool | QC & adjudicate your gold set *(coming soon)* |
| 5 | [`day5_project_finalization.ipynb`](./day5_project_finalization.ipynb) | Assemble the pipeline end-to-end *(coming soon)* | Draft the one-page report *(coming soon)* |

## Deeper notes

The prose walkthroughs below expand on the in-notebook narration:

- [Day 2 — Annotation, gold standards & evaluation](./tutorial-day2-annotation-eval.md)
- [Day 3 — Replicating Kim & Lu with open data](./tutorial-day3-move-replication.md) — the
  discourse-move mini-project track.

When you are ready to run your own study, move on to the
[mini-project starter tracks](../datasets/mini-project-tracks.md).
