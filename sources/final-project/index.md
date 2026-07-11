---
title: "Final Project"
subtitle: "Group Mini-Project — LLM-Based Linguistic Analysis"
toc: true
---

<!-- BEING-PREPARED-BANNER -->
::: {.callout-warning appearance="simple"}
## 🚧 Being prepared
This page is being finalized ahead of the course (**Aug 3–7, 2026**) and may be incomplete or change before your session. The [syllabus](/syllabus/index.md) and [readings](/syllabus/readings.md) are ready now.
:::


The final project is a **group mini-project** in which you run a small, end-to-end LLM-based analysis on a real annotated dataset and report the results. It is introduced in [Session 3](../sessions/day1/session3.md) (track selection + group formation) and carried out across Sessions [12](../sessions/day4/session12.md)–[15](../sessions/day5/session15.md).

## Choose a track

Pick one of the provided expert-annotated datasets (easy → hard). Details and licensing are on the [Replication Datasets](../resources/datasets/index.md) and [Mini-Project Starter Tracks](../resources/datasets/mini-project-tracks.md) pages.

## Workflow

1. **Sample** a balanced ~40-item gold subset from the provided pool (`sample_pool`).
2. **QC / adjudicate** the sampled gold set.
3. **Iterate** your prompt over 2–3 rounds, re-evaluating each round (P/R/F1, confusion matrix).
4. **Freeze** your final predictions to JSON (see below).
5. **Report** in an in-class one-page report.
6. **Present** to the class with instructor Q&A.

::: {.callout-important}
## Run it reproducibly, then freeze
You run the model through the **Gemini API** with `temperature=0` + a fixed seed
([get a free key](../resources/tools/gemini-api-key.md)). Even so, a hosted LLM is only *best-effort*
reproducible, so once your prompt is final, **run it once and save the predictions to a JSON file**,
committed with your notebook. Your evaluation then runs off that frozen file — so your reported F1 is
stable, and anyone (including the grader) can re-run your analysis on exactly the outputs you saw.
:::

## Deliverables

- **Presentation + Q&A** — the graded core.
- **In-class one-page report** — track/labels · gold + what QC changed · prompt-iteration table (F1 per round) · confusion matrix + error analysis · limitations.
- **Completed notebook** — assembled from the cell library and run end-to-end, with your group's gold subset, prompt, **frozen predictions JSON**, and outputs.

All deliverables are produced and submitted **during the course** — there is no post-course write-up.

## Grading

See the [Course Syllabus](../syllabus/index.md) for the full breakdown (mini-project presentation + Q&A and the in-class report are weighted components; the completed notebook is graded under hands-on).
