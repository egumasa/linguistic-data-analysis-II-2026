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
[Datasets](../resources/datasets/index.md).
:::

::: {.callout-important}
## Part B is autograded — so it must be reproducible
The Corpus Lab sections are checked automatically, so your results have to come out the same every
run. The **Day 1–2 labs are keyless** (Python practice; metrics on *frozen* predictions). From
**Day 3** the labs call the model, so you use the **Gemini API** with `temperature=0` + a fixed seed
and [a free key](../resources/tools/gemini-api-key.md) — and you **freeze your predictions to JSON**
so the grader re-runs your analysis on exactly the outputs you saw.
:::

::: {.callout-tip}
## Which backend each day uses
- **Day 1** — Colab's built-in Gemini (`colab.ai`), keyless. Your first live call; notice it varies.
- **Day 2** — *no model call.* You evaluate **frozen** predictions so the metrics numbers hold still.
- **Day 3 onward** — you run the model yourself via the **Gemini API** (`temperature=0` + a fixed
  seed, so results are reproducible for the autograded labs). One-time setup:
  [get a free key](../resources/tools/gemini-api-key.md).
:::

## The notebooks

| Day | Notebook | Tutorial (Part A) | Corpus Lab (Part B) |
|---|---|---|---|
| 1 | [`day1_python_and_first_llm.ipynb`](./day1_python_and_first_llm.ipynb) | Python basics + your first LLM call | Python practice exercises (self-checked) |
| 2 | [`day2_gold_standards_and_evaluation.ipynb`](./day2_gold_standards_and_evaluation.ipynb) | The pipeline on CEFR-SP (P/R/F1 + confusion matrix) | Annotate a gold set by hand in a Google Sheet (agreement → adjudication → canonical JSON); then code the metrics from scratch |
| 3 | [`day3_prompt_design.ipynb`](./day3_prompt_design.ipynb) | Zero-shot → few-shot → chain-of-thought on CEFR | Your own prompt-iteration study *(coming soon)* |
| 4 | [`day4_pipeline_and_sampling.ipynb`](./day4_pipeline_and_sampling.ipynb) | Sample a balanced gold subset from a pool | QC & adjudicate your gold set *(coming soon)* |
| 5 | [`day5_project_finalization.ipynb`](./day5_project_finalization.ipynb) | Assemble the pipeline end-to-end *(coming soon)* | Draft the one-page report *(coming soon)* |

When you are ready to run your own study, move on to the
[mini-project starter tracks](../resources/datasets/mini-project-tracks.md).
