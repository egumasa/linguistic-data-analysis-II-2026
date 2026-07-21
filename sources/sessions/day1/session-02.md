---
title: "Session 2: Colab Onboarding & Your First LLM Call"
subtitle: "Day 1 · Introduction & First Experience (1-2)"
toc: true
---

<!-- BEING-PREPARED-BANNER -->
::: {.callout-warning appearance="simple"}
## 🚧 Being prepared
This page is being finalized ahead of the course (**Aug 3–7, 2026**) and may be incomplete or change before your session. The [syllabus](/syllabus/index.md) and [readings](/syllabus/readings.md) are ready now.
:::


## Learning objectives

By the end of this session you will be able to:

- Sign in to Google Colab, run a cell (Shift+Enter), and read a Python error message well enough to fix a typo.
- Send a prompt to a language model with `generate_text(...)`, then edit the prompt and re-run.
- Recognise Python's core data types — `str`, `list`, `dict` — in what the model hands back, and index into a list or dict.
- Build a prompt from a variable with an f-string.

## Agenda

This is a **guided, run-along session** using Part A of the Day 1 notebook. The LLM call is the spine — everything else is just enough Python to read and reshape what the model gives back.

1. **Colab basics — run a cell, read an error** — sign in, cells and the runtime, Shift+Enter, and how to read a red error.
2. **Your first LLM call** — run the setup cell, then `generate_text(...)`; change the prompt and re-run.
3. **What did the model hand back?** — data types (`str` / `list` / `dict`) and `[...]` indexing, motivated by the reply.
4. **f-strings** — drop a sentence into a prompt with `f"...{sentence}"`.

Control flow (`for`, `if`, functions) and text segmentation come next, in [Session 3](session-03.md).

## Reading
<!-- to be added -->

## Slides & Colab

- Notebook — **Part A** (guided): [`day1_python_and_first_llm.ipynb`](../../notebooks/day1_python_and_first_llm.ipynb) —
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/egumasa/linguistic-data-analysis-II-2026/blob/main/sources/notebooks/day1_python_and_first_llm.ipynb)
- Slides: [Session 2 slides](../../slides/slides-session-02.html){target="_blank"}
