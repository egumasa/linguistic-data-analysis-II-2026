---
title: "Final Project"
subtitle: "Group Mini-Project — LLM-Based Linguistic Analysis"
toc: true
---
You run a small, end-to-end LLM-annotation study on a real annotated dataset, and report what you find. It is introduced in [Session 3](../sessions/day1/session-03.md) (track selection and
group formation), planned in [Session 11](../sessions/day4/session-11.md), and carried out
across Sessions [12](../sessions/day4/session-12.md)–[15](../sessions/day5/session-15.md).

Everything is produced **during the course**. There is no post-course write-up.

## Where the work happens

All of it in one repository, which you clone into your group's Google Drive:

**[github.com/egumasa/lda2-final-template](https://github.com/egumasa/lda2-final-template)**

`notebooks/` holds six numbered notebooks, run in order. They carry the **mechanics** — the
paths, the file names, the Google Sheets round-trip, the pacing between API calls, and what
each one hands to the next — so that a real study fits in two days.

What they do not carry is the **method**. Which agreement statistic your design owes, what
counts as a disagreement, which prompt move to try next, which number your report leads with:
those you choose, and they are what the Q&A and the rubric ask about.

Each decision point gives you an inventory of what is available, what each call gives you, and
where you first ran it — every one of them has an ancestor in Days 1–4. The
[inventory page](pipeline-cheatsheet.md) has the full list.

::: {.callout-tip}

## One clone, shared by the group

**One member** clones the repo into their Google Drive and shares the folder with the team.
**Nobody pushes** — git is just how you get the code onto the machine.

Colab syncs notebook edits live, like a Google Doc, so you can all work in it at once. But
**runtimes are per-person**, and ordinary files in the folder are last-write-wins — so let one
person be the **driver** for any cell that runs the model or writes a file. Your final run has
to be one run by one person anyway.

The annotation Sheet `02_sample` makes is the exception: that is a real Google Sheet, so annotate it
together.
:::

## The six notebooks

|                           |                                                                        |                       |
| ------------------------- | ---------------------------------------------------------------------- | --------------------- |
| `01_build_pool_<track>` | your track's raw corpus → a pool                                      | no model              |
| `02_sample`             | the pool → your sample, and the blind annotation sheet                | no model              |
| `03_annotate`           | the filled-in sheet →**your** gold set, split into dev and test | no model              |
| `04_develop`            | prompt rounds, on**dev** only                                    | the model, many times |
| `05_test`               | the held-out run, once, frozen to a file                               | the model, once       |
| `06_report`             | the frozen run → error analysis and the report scaffold               | no model              |

**04 and 05 are separate files on purpose.** "You may not look at the test set while you are
still changing the prompt" is a rule that only holds if it is a file boundary rather than a
scroll position, so `04_develop.ipynb` has no path to your test items at all.

Notebooks 01–03 need no model, so there is plenty to get on with while your `PLAN.md` is being
signed off.

::: {.callout-important}

## Your adjudicated gold is the gold

The model is scored against **what your group decided in `03_annotate`**, not against the published
labels. That is what makes the QC pass matter: the boundaries you argued over in `03_annotate` are
exactly the ones you will be pointing at in `06_report` when you explain a miss.

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

| Track         | Task                                 | Difficulty                                           |
| ------------- | ------------------------------------ | ---------------------------------------------------- |
| `raamove`   | Rhetorical moves in RA abstracts (8) | ★★☆                                               |
| `cars50`    | CARS moves in RA introductions       | ★★★ the annotators themselves got κ ≈ 0.43      |
| `l2_errors` | L2 error type, or error detection    | ★★★ also benchmarkable against the published tool |
| `icnale`    | Holistic essay score band            | ★★☆ needs a registered download                   |

## What to read next

- **[The `PLAN.md` gate](plan.md)** — the one page you write *before* you call the model.
- **[Deliverables &amp; submission](deliverables.md)** — exactly what to hand in, and how.
- **[Rubric](rubric.md)** — what is graded. (Not your F1.)
- **[What you have to work with](pipeline-cheatsheet.md)** — every call the notebooks offer, and where you first ran it.
