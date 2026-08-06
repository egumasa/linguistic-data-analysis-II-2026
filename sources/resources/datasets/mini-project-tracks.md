---
title: "Mini-Project Starter Tracks"
subtitle: "Pick a dataset, design a scheme, run an LLM, evaluate it"
toc: true
---

This page is about **choosing a track**. The workflow, the deliverables and the rubric are on
the [Final Project](../../final-project/index.md) pages, and the work itself happens in the
[project template](https://github.com/egumasa/lda2-proj-template).

Whichever track you pick, the shape is the same:

1. **Sample** a balanced ~40-item subset from the track's pool (`sample_pool` draws up to *N*
   items per label; rare classes simply yield fewer — that's a property of the data).
2. **QC / adjudicate** the subset: two of you annotate it independently and blind in a Google
   Sheet, measure agreement and κ, then argue out the rows you disagreed on. This is where you
   feel inter-annotator disagreement, and start asking *"is a wrong label the model's fault or
   the scheme's?"* What comes out is **your** gold set — and it is what the model gets scored
   against.
3. **Iterate** the prompt 2–3 rounds against it, through the **Gemini API** with
   `temperature=0` + a fixed seed ([get a free key](../tools/gemini-api-key.md)) so that
   differences reflect the *prompt*, not noise.
4. **Freeze** your final predictions to a JSON file — run the model once, save the output, and
   evaluate off that file from then on. Your reported F1 is then stable and auditable.
5. **Report** precision / recall / F1 + a confusion matrix, with an honest discussion of
   limitations.

Every track ships a builder notebook for the **pool** you sample from: run
`notebooks/01_build_pool_<track>.ipynb` once in Colab and it downloads the raw corpus and
reshapes it into the shared item format. No pool data is committed — your group builds its own.

Provenance & licences: [`SOURCES.md`](./SOURCES.md) · the helpers you will call:
[pipeline cheat-sheet](../../final-project/pipeline-cheatsheet.md).

::: {.callout-tip}
## Your data lives in your Drive, not in git
One member clones the template **into Google Drive** and shares the folder. Your pool, your
gold set and your outputs then persist across sessions and everyone sees the same files —
without anyone pushing anything. See [Housing Your Data in Google
Drive](../tools/google-drive-data.md) for the mount → save → load round-trip.
:::

## Tracks

### ★★★ Discourse moves (RAAMove / CaRS-50)

Annotate rhetorical **moves**. This track replicates the idea of Kim & Lu (2024), who tested how
well ChatGPT can annotate move-steps in research-article introductions, and how prompt refinement
and few-shot examples change its accuracy. Their corpus is not public, so CaRS-50 stands in.

> Kim, M., & Lu, X. (2024). Exploring the potential of using ChatGPT for rhetorical move-step
> analysis: The impact of prompt refinement, few-shot learning, and fine-tuning.
> *Journal of English for Academic Purposes, 71,* 101422.

Tracks: `raamove` (8 moves, abstracts) or `cars50` (CARS Moves, introductions).
Pools built by `prep_datasets.py`: `raamove_pool.json` (3,069), `cars50_pool.json` (1,297), and
`cars50_step_pool.json` for the 11-class stretch version.
Extensions: compare abstracts vs. introductions; move-only vs. move+step; few-shot vs. definitions.

RAAMove ships as tidy JSON and is the gentler start; CaRS-50 is harder because judging moves in
*introductions* needs more context. Expect lower F1 than the Day 2–3 CEFR tutorials — the CaRS-50 annotators
themselves reached only **κ ≈ 0.43**, so "the model is wrong" and "the scheme is fuzzy" are both live
explanations, and telling them apart is the interesting part of your analysis.

### ★★★ L2 error annotation (AutoErrorAnalyzer)

Annotate the **error families** present in a learner sentence — Grammatical, Lexical,
Mechanical — or do binary **error detection**. The family track is **multi-label**: a
sentence with an article error and a spelling error is `Grammatical, Mechanical`, and a
clean sentence is `No error`, so nothing is dropped for having errors of more than one
kind. Agreement is measured per family (exact-set agreement, mean Jaccard, per-family
κ) and scoring is per-family precision, recall and F1 with **micro F1** as the
headline.
Track: `l2_errors`. Pools: `l2_errors_pool.json` (~1,483, family sets) and
`l2_error_detection_pool.json` (~1,485, yes/no).
Special feature: the source also has the **published tool's predictions**, so you can benchmark your
LLM against both the human gold *and* the original system. (Mizumoto, 2025, *SSLA*.)

**Full analysis: `l2_errors_full`.** For groups who want to annotate **all** the error
types, not the three-family grouping. An item's annotation is the **set** of codes
present in the sentence — the paper's 23 codes plus `COLL` (collocation), which the
published annotations also use — written as one comma-separated string (`ART, SP`), or
`No error`. The pipeline is the same as the family track's; what changes is the size
of the code list. Be clear about the cost before choosing it: each coder checks 24
possibilities per sentence, so annotation is markedly slower. The per-code scoring is
exactly how the AutoErrorAnalyzer paper evaluates itself, so your run and the
published tool's `aea_label` predictions are directly comparable on the same
sentences. This is the heaviest track in the project.
Pool: `l2_errors_full_pool.json` (~1,483 items).

### ★★☆ Automated writing evaluation (ICNALE GRA)

Predict a holistic essay score band (Low / Mid / High). Track: `icnale`. Requires
[registering for the ICNALE GRA](https://language.sakura.ne.jp/icnale/download.html) and exporting a
`text,score` CSV yourself — the builder tells you exactly where to put it. The data is research-use
only, so nothing derived from it may be committed or submitted.

⚠️ These labels are **ordered but not alphabetical**, so set
`LABELS_ORDER = ["Low", "Mid", "High"]` in CONFIG — otherwise the weighted κ is computed over
`High < Low < Mid` and means nothing. (That is what question 3 of your `PLAN.md` is for.)

Extensions: compare holistic vs. a single analytic dimension; check whether the LLM rewards length.

## Deliverables, submission and grading

All on the Final Project pages, so there is one authoritative copy of each:

- [Deliverables & submission](../../final-project/deliverables.md) — the bundle, the report's
  six sections, the presentation format.
- [Rubric](../../final-project/rubric.md) — what is graded. Your F1 is not.
- [The `PLAN.md` gate](../../final-project/plan.md) — write this before you call the model.
