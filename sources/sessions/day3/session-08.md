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
- **Map the four prompt elements onto a classification prompt** — recasting Huang & Mizumoto's *Task / Criteria / "My paragraph"* structure as the CEFR prompt (instruction = classify; context = level descriptors; input = the sentence; output indicator = return only the label).
- Run the **zero-shot → few-shot → chain-of-thought** progression on CEFR, re-evaluating each on a validation set, and score the final prompt **once** on the held-out test set.
- Prompt for **structured output** and recognise **JSON** as the `{id, text, label}` data format.

## Reading

No new reading for this session — see the Day 3 reading (Huang & Mizumoto, 2025; Kim & Lu, 2024) in [Session 7](session-07.md) and on the [Readings](../../syllabus/readings.md) page.

## Slides & Colab

<!-- Notebook not yet finalized:
- Notebook (tutorial + Corpus Lab): [`day3_prompt_design.ipynb`](../../notebooks/day3_prompt_design.ipynb) — zero-shot → few-shot → chain-of-thought on the CEFR task —
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/egumasa/linguistic-data-analysis-II-2026/blob/main/sources/notebooks/day3_prompt_design.ipynb)
-->
- Further reading: [Mini-project starter tracks](../../resources/datasets/mini-project-tracks.md) (including the discourse-move / Kim & Lu replication track)
<!-- Slides: [Session 8 slides](../../slides/slides-session-08.html){target="_blank"} -->
