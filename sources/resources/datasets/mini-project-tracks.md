---
title: "Mini-Project Starter Tracks"
subtitle: "Pick a dataset, design a scheme, run an LLM, evaluate it"
toc: true
---

For the final mini-project you run your own small LLM-annotation study. The workflow for every
track is the same:

1. **Sample** a balanced ~40-item gold subset from the track's pool using `sample_pool` (it draws up
   to *N* items per label; rare classes simply yield fewer — that's a property of the data).
2. **QC / adjudicate** the subset: each group member independently re-checks part of it against the
   scheme, flag disagreements with the published label, then discuss and resolve. This is where you
   feel inter-annotator disagreement and start asking *"is a wrong label the model's fault or the
   scheme's?"*
3. **Iterate** the prompt 2–3 rounds against your gold set. Run through the **Gemini API** with
   `temperature=0` + a fixed seed ([get a free key](../tools/gemini-api-key.md)) so each round is
   reproducible and differences reflect the *prompt*, not sampling noise.
4. **Freeze** your final predictions to a JSON file (run the model once, save + commit its output).
   Your evaluation runs off that frozen file, so your reported F1 is stable and auditable.
5. **Report** precision / recall / F1 + a confusion matrix with an honest discussion of limitations.

Each track rebuilds a ready gold file **and** a full pool to sample your own subset from.

Rebuild the gold files: [`README.md`](./README.md) · provenance & licenses: [`SOURCES.md`](./SOURCES.md) ·
the pipeline: [Day 2](../../notebooks/day2_gold_standards_and_evaluation.ipynb) & [Day 3](../../notebooks/day3_prompt_design.ipynb) notebooks.

::: {.callout-tip}
## Keep your data in your own Drive
Unlike the worked tutorials (which load a URL we ship for you), you build your own gold set here —
so **house it in your Google Drive**, not GitHub. See
[Housing Your Data in Google Drive](../tools/google-drive-data.md) for the mount → save → load
round-trip, worked on the familiar CEFR data and reused unchanged for your track.
:::

## Tracks

### ★★★ Discourse moves (RAAMove / CaRS-50)

Annotate rhetorical **moves**. This track replicates the idea of Kim & Lu (2024), who tested how
well ChatGPT can annotate move-steps in research-article introductions, and how prompt refinement
and few-shot examples change its accuracy. Their corpus is not public, so CaRS-50 stands in.

> Kim, M., & Lu, X. (2024). Exploring the potential of using ChatGPT for rhetorical move-step
> analysis: The impact of prompt refinement, few-shot learning, and fine-tuning.
> *Journal of English for Academic Purposes, 71,* 101422.

Gold: `raamove_moves.json` (8 moves, abstracts) or `cars50_moves.json` (CARS Moves, introductions).
Pools: `raamove_pool.json`, `cars50_pool.json`, `cars50_step_pool.json` (11-class stretch).
Extensions: compare abstracts vs. introductions; move-only vs. move+step; few-shot vs. definitions.

RAAMove ships as tidy JSON and is the gentler start; CaRS-50 is harder because judging moves in
*introductions* needs more context. Expect lower F1 than the CEFR tutorials — the CaRS-50 annotators
themselves reached only **κ ≈ 0.43**, so "the model is wrong" and "the scheme is fuzzy" are both live
explanations, and telling them apart is the interesting part of your analysis.

### ★★★ L2 error annotation (AutoErrorAnalyzer)

Classify the error type in a learner sentence (Grammatical / Lexical / Mechanical / No error), or do
binary **error detection**.
Gold: `l2_errors.json`, `l2_error_detection.json` · Pool: `l2_errors_pool.json`.
Special feature: the source also has the **published tool's predictions**, so you can benchmark your
LLM against both the human gold *and* the original system. (Mizumoto, 2025, *SSLA*.)
Extensions: try the finer 23-code taxonomy; analyze which error types the LLM over-/under-predicts.

### ★★☆ Automated writing evaluation (ICNALE GRA)

Predict a holistic essay score band (Low / Mid / High). Requires
[registering for the ICNALE GRA](https://language.sakura.ne.jp/icnale/download.html) and building the
gold file per [`SOURCES.md`](./SOURCES.md).
Extensions: compare holistic vs. a single analytic dimension; check whether the LLM rewards length.

## Deliverables

Everything is produced **in class** — there is no post-course write-up:

- **Presentation + Q&A** — the main deliverable. Be ready to explain *why* the model missed specific
  items and what your QC pass changed; the Q&A is where you show you did the work.
- **One-page report** (the five sections below) — your working doc and the scaffold for the talk.
- **Completed notebook** — assembled and run end-to-end, with your sampled gold subset, prompt, and
  evaluation outputs; submitted as evidence that the in-class work was completed.

### What the one-page report covers

1. **Scheme & gold** — your label set, and how you built the gold set: subset size, balance, and
   **what your QC/adjudication pass changed** (any disagreements with the published label).
2. **Prompt iterations** — a table of changes and the F1 at each step (see the Day 3 tutorial).
3. **Evaluation** — per-class precision/recall/F1 + confusion matrix on a held-out gold set.
4. **Error analysis** — concrete examples, and whether failures are the *model's* or the *scheme's*.
5. **Limitations** — stochasticity, contamination risk, and what your numbers do **not** show.
