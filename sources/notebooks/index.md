---
title: "Daily Notebooks"
subtitle: "One notebook per day (two on Day 2) — tutorial + Corpus Lab in a single file"
toc: true
---

Each day has **one Colab notebook** that you work through top to bottom and submit at the end of the
day. Every notebook has two parts:

- **Part A · Tutorial** — the guided, run-along section you do together in class.
- **Part B · Corpus Lab** — the independent hands-on practice for that day.

**Day 2 is the exception**: its two hands-on sessions get a notebook each — S5 builds a gold
standard by hand, S6 measures a model against one — and you submit **both**. The S5 notebook has
no Part A/B; it runs on its own six-step spine, **A–F**.

You open each notebook directly in Colab (Tohoku Google account, no setup), **Run all**, then
**File → Download → Download `.ipynb`** and submit that file.

::: {.callout-note}
## The pipeline is the same all week
**load gold → format prompt → call model → evaluate → inspect errors.** Only the *task* and the
*prompt* change. The datasets behind these notebooks are catalogued under
[Datasets](../resources/datasets/index.md).
:::

::: {.callout-important}
## The Corpus Labs are autograded — so they must be reproducible
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

| Day | Notebook | Part A | Part B |
|---|---|---|---|
| 1 | [`day1_python_and_first_llm.ipynb`](./day1_python_and_first_llm.ipynb) | *Tutorial* — Python basics + your first LLM call | *Corpus Lab* — Python practice exercises (self-checked) |
| 2 · S5 | [`day2-s5_gold_standard_construction.ipynb`](./day2-s5_gold_standard_construction.ipynb) | *(no parts — one lab, steps A–F)* — annotate a gold set by hand in a Google Sheet: agreement → κ → refine & re-annotate → adjudication → canonical JSON ||
| 2 · S6 | [`day2-s6_evaluation_metrics.ipynb`](./day2-s6_evaluation_metrics.ipynb) | *Corpus Lab* — build the metrics yourself on one yes/no question: TP/FP/FN/TN → confusion matrix → precision, recall, F1, κ → checked against scikit-learn | *Tutorial* — the same job with scikit-learn on all six CEFR levels: `classification_report`, confusion matrix, plain vs. weighted κ, error analysis |
| 3 | [`day3_prompt_design.ipynb`](./day3_prompt_design.ipynb) | *Tutorial* — zero-shot → few-shot → chain-of-thought on CEFR | *Corpus Lab* — your own prompt-iteration study *(coming soon)* |
| 4 | [`day4_pipeline_and_sampling.ipynb`](./day4_pipeline_and_sampling.ipynb) | *Tutorial* — sample a balanced gold subset from a pool | draw the dev/test line, then hand off to the project template |

**There is no Day-5 notebook.** From the end of Day 4 the work moves to your own study, in
the six numbered notebooks of the
[project template](https://github.com/egumasa/lda2-final-template) — your track, your gold
set, your prompt. Start at the [Final Project](../final-project/index.md) pages.

## Editing these notebooks

The `.ipynb` files are edited directly — open one, change a cell, run it, save. Two kinds
of cell are the exception: the 📦 **Setup** cell and each 🔧 **Library** cell are built from
`_notebook_lib.py`, so that a helper used on several days has one definition and a day
imports only what it uses. Those cells say so in their own second line, and editing them
by hand does not last. To change a helper's code, edit `_notebook_lib.py`; to change which
helpers a cell ships, edit that cell's `lda2` metadata. Then run the sync below.

The helpers sit at the end of `_notebook_lib.py` as ordinary Python, one
`# === name :: caption ===` section each. Edit one the way you would edit any function —
nothing there is quoted text, and nothing runs it locally.

Two scripts sit next to the notebooks:

```bash
python sources/notebooks/_sync_notebooks.py    # rebuild those cells, clear outputs
python sources/notebooks/_check_notebooks.py   # every cell compiles, fits a screen, is introduced
```

Run both before committing. `_sync_notebooks.py --check` reports what would change without
writing anything, and `--notebook day3` limits it to one file.

Notebooks are committed **without outputs**, so their diffs stay readable. A git filter
takes the outputs out on the way into a commit and leaves your working copy untouched.
Filters are per-clone configuration, so turn it on once in a fresh clone:

```bash
git config filter.nbstrip.clean "uv run python sources/notebooks/_sync_notebooks.py --stdin-strip"
```

To search the prose across all five notebooks, read the cell sources rather than the JSON:

```bash
jq -r '.cells[].source | add' sources/notebooks/*.ipynb | grep -i "confusion matrix"
```
