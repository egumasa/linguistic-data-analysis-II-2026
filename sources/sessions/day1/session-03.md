---
title: "Session 3: Python Practice & Mini-Project Setup"
subtitle: "Day 1 · Introduction & First Experience (1-3)"
toc: true
---
<!-- BEING-PREPARED-BANNER -->

::: {.callout-warning appearance="simple"}

## 🚧 Being prepared

This page is being finalized ahead of the course (**Aug 3–7, 2026**) and may be incomplete or change before your session. The [syllabus](/syllabus/index.md) and [readings](/syllabus/readings.md) are ready now.
:::

## Learning objectives

By the end of this session you will be able to:

- Split a paragraph into sentences two ways — a naive `.split(".")` and a spaCy sentencizer — and explain why the naive rule fails on abbreviations and decimals.
- Look up a word's vector, compare two words by similarity, and show that a static model gives one word form only one vector no matter what surrounds it.
- Use a `for` loop, an `if`, and a function (`def`) to run the model over a list of sentences and tidy each reply.

## Agenda

This session picks up **Part B** of the Day 1 notebook, then forms project groups.

1. **From a document to sentences** — segment a paragraph *without* a model (`.split(".")`, dot-methods) and *with* a model (spaCy sentencizer); see why sentence boundaries matter for annotation.
2. **What else the model knows about words** — the embeddings from [Session 1](session-01.md), as code you run: a word's 300 numbers, `.similarity(...)`, a word's nearest neighbours, and the two places static vectors stop working (one form gets one vector; averaging loses word order).
3. **Run the model over every sentence** — a `for` loop + an `if`, wrapped into a reusable `ask(...)` function (the seed of the pipeline you'll assemble later in the week).
4. **Your turn** — the guided Python practice exercises with a self-check.
5. **Mini-project setup** — form groups and choose a track (see below).

## Reading

No new reading for this session — the Day 1 reading (Abdurahman et al., 2025, *skim*) is listed in [Session 1](session-01.md) and on the [Readings](../../syllabus/readings.md) page.

## Slides & Colab

<!--
- Notebook — **Part B** (practice): [`day1_python_and_first_llm.ipynb`](../../notebooks/day1_python_and_first_llm.ipynb) —
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/egumasa/linguistic-data-analysis-II-2026/blob/main/sources/notebooks/day1_python_and_first_llm.ipynb)
- Slides: [Session 3 slides](../../slides/slides-session-03.html){target="_blank"}
-->

## Mini-project

This session closes with mini-project **track selection and group formation** — each group needs at least one *Linguistic Data Analysis I* alumnus. Choose your track now so you can start annotating it on Day 2. See the [Final Project](../../final-project/index.md) page.
