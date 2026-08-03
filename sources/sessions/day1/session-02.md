---
title: "Session 2: Colab Onboarding & Your First LLM Call"
subtitle: "Day 1 · Introduction & First Experience (1-2)"
toc: true
---
<!-- BEING-PREPARED-BANNER -->


## Learning objectives

By the end of this session you will be able to:

- Sign in to Google Colab, run a cell (Shift+Enter), and read a Python error message well enough to fix a typo.
- Store a value in a variable, and send a prompt to a language model with `ai.generate_text(...)`.
- Build a prompt from a variable with an f-string, and recognise the `.format()` template form you will edit from Session 7 on.
- Recognise Python's core data types — `str`, `list`, `dict` — in what the model hands back.
- Build the `{id, text, label}` record the rest of the course uses, **with a label you decided yourself**, and add the model's answer beside it.
- Index and slice into a list of records to compare the two answers.

## Agenda

This is a **guided, run-along session** using Part A of the Day 1 notebook, in **eight short steps**. The model comes first and stays first: you call it, then learn just enough Python to read and score what it gives back.

1. **Run a cell** — sign in, cells and the runtime, Shift+Enter.
2. **Read an error** — run a cell that fails on purpose, and read the last line.
3. **Variables** — store a value under a name with `=`.
4. **Your first LLM call** — the setup cell (one import), then five prompts: the task itself, asking for a format, the same prompt twice, and one the model gets wrong.
5. **f-strings** — drop a sentence into a prompt with `f"...{sentence}"`, then write a `.format()` template of your own.
6. **What kind of value is the answer?** — `type()`, and the three types you use all week.
7. **Put the answer in a record** — decide a sentence's level yourself, then ask the model the same question and store both in one `{id, text, label}` record.
8. **Indexing and slicing** — `items[2]["label"]`, `items[:2]`, and comparing the two answers with `==`.

Control flow (`for`, `if`, `elif`, functions), counting, and text segmentation come next, in [Session 3](session-03.md).

## Reading

No new reading for this session — the Day 1 reading (Abdurahman et al., 2025, *skim*) is listed in [Session 1](session-01.md) and on the [Readings](../../syllabus/readings.md) page.

## Slides & Colab

- Notebook — **Part A** (guided): [`day1_python_and_first_llm.ipynb`](../../notebooks/day1_python_and_first_llm.ipynb) —
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/egumasa/linguistic-data-analysis-II-2026/blob/main/sources/notebooks/day1_python_and_first_llm.ipynb)

<!--
- Slides: [Session 2 slides](../../slides/slides-session-02.html){target="_blank"}
-->
