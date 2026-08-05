---
title: "Session 8: Hands-on — LLM Classification & Prompt Iteration"
subtitle: "Day 3 · Prompt Design & Iteration (3-2)"
toc: true
---
<!-- BEING-PREPARED-BANNER -->

::: {.callout-warning appearance="simple"}

## 🚧 Being prepared

This page is being finalized ahead of the course (**Aug 3–7, 2026**) and may be incomplete or change before your session. The [syllabus](/syllabus/index.md) and [readings](/syllabus/readings.md) are ready now.
:::

## Learning objectives

By the end of this session, you will be able to:

- Get and store a **Gemini API key** (Colab Secrets) and make **reproducible** calls (`temperature=0`, `seed`).
- **Map the prompt components onto a classification prompt** — recasting Huang & Mizumoto's *Task / Criteria / "My paragraph"* structure as the CEFR prompt (directive = classify; additional information = level descriptors; input = the sentence; output formatting = return only the label).
- Run the **zero-shot → few-shot → chain-of-thought** progression on CEFR, re-evaluating each on a validation set, and score the final prompt **once** on the held-out test set.
- Prompt for **structured output** and recognise **JSON** as the `{id, text, label}` data format.

## Agenda

1. **From feedback to classification** — the same prompt components from [Session 7](session-07.md), now on a new task: directive = classify, additional information = the level descriptors, input = the sentence, output formatting = return only the label.
2. **Your Gemini API key** — get one and store it in Colab Secrets, in four steps. Why a key is needed at all, and the two separate rate limits that govern how fast you can call.
3. **Run classification in Colab** — two files with two purposes: tune every prompt on the 24-item validation set, and keep the 72-item test set for one final run. Then three rounds: **zero-shot**, **few-shot**, **chain-of-thought**, recording macro-F1 on validation after each.
4. **Evaluate the outputs** — read the per-class report rather than the average alone, since one level with F1 near zero drags macro-F1 down and the report shows you which. Then the held-out run, once, on the 72 items.
5. **Structured output** — ask the model to return JSON rather than a bare label, which is the same `{id, text, label}` shape from Day 1 in a format code can read.

Expect the held-out score to come out **lower** than your validation score. That gap is the expected effect of having chosen the prompt by looking at validation results, not a mistake.

## Reading

No new reading for this session — see the Day 3 reading (Huang & Mizumoto, 2025; Kim & Lu, 2024) in [Session 7](session-07.md) and on the [Readings](../../syllabus/readings.md) page.

## Slides & Colab

<!-- Notebook not yet finalized:
- Notebook (tutorial + Corpus Lab): [`day3_prompt_design.ipynb`](../../notebooks/day3_prompt_design.ipynb) — zero-shot → few-shot → chain-of-thought on the CEFR task —
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/egumasa/linguistic-data-analysis-II-2026/blob/main/sources/notebooks/day3_prompt_design.ipynb)
-->

Notebook (Session 8): [`day3_prompt_design.ipynb`](../../notebooks/day3_prompt_design.ipynb) —
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/egumasa/linguistic-data-analysis-II-2026/blob/main/sources/notebooks/day3_prompt_design.ipynb)

<!-- Slides: [Session 8 slides](../../slides/slides-session-08.html){target="_blank"} -->
