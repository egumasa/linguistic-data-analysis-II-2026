---
title: "Final Project"
subtitle: "Group Mini-Project — LLM-Based Linguistic Analysis"
toc: true
---

You run a small, end-to-end LLM-annotation study on a real annotated dataset, and report what
you find. It is introduced in [Session 3](../sessions/day1/session-03.md) (track selection and
group formation), planned in [Session 11](../sessions/day4/session-11.md), and carried out
across Sessions [12](../sessions/day4/session-12.md)–[15](../sessions/day5/session-15.md).

Everything is produced **during the course**. There is no post-course write-up.

## Where the work happens

All of it in one repository, which you clone into your group's Google Drive:

**[github.com/egumasa/lda2-final-template](https://github.com/egumasa/lda2-final-template)**

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/egumasa/lda2-final-template/blob/main/notebooks/mini_project.ipynb)

`notebooks/mini_project.ipynb` is **your** notebook: one skeleton, any track. Each of its six
steps ships with its header, its goal, the helpers available to it, and the variable names the
next step expects — **but not the calls.** You write those.

That is deliberate, and it should not be hard: every call has the same form it had in
Days 1–3, and each step says where you used it before. `run_prompt(PROMPT, gold)` and
`evaluate(gold, pred, ordered=True)` are the same two lines you ran on Day 3. The
[pipeline cheat-sheet](pipeline-cheatsheet.md) has the full mapping.

::: {.callout-tip}
## One clone, shared by the group
**One member** clones the repo into their Google Drive and shares the folder with the team.
**Nobody pushes** — git is just how you get the code onto the machine.

Colab syncs notebook edits live, like a Google Doc, so you can all work in it at once. But
**runtimes are per-person**, and ordinary files in the folder are last-write-wins — so let one
person be the **driver** for any cell that runs the model or writes a file. Your final run has
to be one run by one person anyway.

The annotation Sheet in step 2 is the exception: that is a real Google Sheet, so annotate it
together.
:::

## The six steps

1. **Sample** a balanced subset from your track's pool.
2. **QC / adjudicate** it — two of you annotate blind, measure agreement and κ, then argue out
   the disagreements. What comes out is **your** gold set.
3. **Baseline** prompt — one honest number to beat.
4. **Iterate** 2–3 rounds, then **freeze**: run your best prompt once and save the predictions
   to a file.
5. **Error analysis** — which misses are the *model's* fault, and which are the *scheme's*?
6. **Export** the report scaffold, then write the parts only you can write.

::: {.callout-important}
## Your adjudicated gold is the gold
The model is scored against **what your group decided in step 2**, not against the published
labels. That is what makes the QC pass matter: the boundaries you argued over in step 2 are
exactly the ones you will be pointing at in step 5 when you explain a miss.

`compare_to_published` still shows you where you differ from the source corpus — and that gap
is itself a finding worth a line in your report.
:::

::: {.callout-important}
## Run it once, then freeze it
You run the model through the **Gemini API** with `temperature=0` and a fixed seed
([get a free key](../resources/tools/gemini-api-key.md)). Even then, a hosted LLM is only
*best-effort* reproducible — so once your prompt is final, **run it once and save the
predictions to a JSON file.** Every number you report comes out of that file.

Your F1 is then stable, and anyone can re-run your analysis on exactly the outputs you saw.
:::

## Choose a track

Four, easy to hard. Details, licences and provenance: [Replication
Datasets](../resources/datasets/index.md) and [Mini-Project Starter
Tracks](../resources/datasets/mini-project-tracks.md).

| Track | Task | Difficulty |
|---|---|---|
| `raamove` | Rhetorical moves in RA abstracts (8) | ★★☆ |
| `cars50` | CARS moves in RA introductions | ★★★ the annotators themselves got κ ≈ 0.43 |
| `l2_errors` | L2 error type, or error detection | ★★★ also benchmarkable against the published tool |
| `icnale` | Holistic essay score band | ★★☆ needs a registered download |

## What to read next

- **[The `PLAN.md` gate](plan.md)** — the one page you write *before* you call the model.
- **[Deliverables & submission](deliverables.md)** — exactly what to hand in, and how.
- **[Rubric](rubric.md)** — what is graded. (Not your F1.)
- **[Pipeline cheat-sheet](pipeline-cheatsheet.md)** — every helper, and where you already used it.
