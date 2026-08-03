---
title: "Session 3: Python Practice & Mini-Project Setup"
subtitle: "Day 1 · Introduction & First Experience (1-3)"
toc: true
---
<!-- BEING-PREPARED-BANNER -->


## Learning objectives

By the end of this session you will be able to:

- Split a paragraph into sentences two ways — a naive `.split(".")` and a spaCy sentencizer — and explain why the naive rule fails on abbreviations and decimals.
- Loop over a list of records, build a list with `.append`, and count with a dict.
- Use `if` / `elif` / `else` and `and` to sort items into categories, and divide two counts while guarding against division by zero.
- Wrap the steps into a reusable function with `def` and `return`, and confirm four short exercises with the self-check.

## Agenda

This session picks up **Part B** of the Day 1 notebook, then forms project groups.

1. **From a document to sentences** (steps 1–2) — segment a paragraph *without* a model (`.split(".")`, dot-methods) and *with* a model (spaCy sentencizer); see why sentence boundaries matter for annotation.
2. **The Python you'll reuse all week** (steps 3–9) — the seven patterns Days 2–5 ask you to write: a `for` loop with `if`/`else`, looping over records, `.append`, counting with a dict, `elif` and `and`, dividing with a zero guard, and wrapping it in `ask(...)`.
3. **Your turn** (steps 10–13) — four exercises, each rehearsing one of those patterns, each with its own self-check. The last one, `accuracy`, is the shape of every metric you build on Day 2.
4. **Mini-project setup** — form groups and choose a track (see below).

**Optional, if time allows:** *What a model stores about a word* — the embeddings from [Session 1](session-01.md), as code you run: a word's 300 numbers, `.similarity(...)`, a word's nearest neighbours, and the two places static vectors stop working (one form gets one vector; averaging loses word order). This section sits at the end of the notebook and nothing later in the week depends on it.

## Reading

No new reading for this session — the Day 1 reading (Abdurahman et al., 2025, *skim*) is listed in [Session 1](session-01.md) and on the [Readings](../../syllabus/readings.md) page.

## Slides & Colab

- Notebook — **Part B** (practice): [`day1_python_and_first_llm.ipynb`](../../notebooks/day1_python_and_first_llm.ipynb) —
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/egumasa/linguistic-data-analysis-II-2026/blob/main/sources/notebooks/day1_python_and_first_llm.ipynb)

<!--
- Slides: [Session 3 slides](../../slides/slides-session-03.html){target="_blank"}
-->

## Mini-project

This session closes with mini-project **track selection and group formation** — each group needs at least one *Linguistic Data Analysis I* alumnus. Choose your track now so you can start annotating it on Day 2. See the [Final Project](../../final-project/index.md) page.
