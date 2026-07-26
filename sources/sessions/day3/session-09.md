---
title: "Session 9: Error Analysis & Under-the-Hood Walkthrough"
subtitle: "Day 3 · Prompt Design & Iteration (3-3)"
toc: true
---

<!-- BEING-PREPARED-BANNER -->
::: {.callout-warning appearance="simple"}
## 🚧 Being prepared
This page is being finalized ahead of the course (**Aug 3–7, 2026**) and may be incomplete or change before your session. The [syllabus](/syllabus/index.md) and [readings](/syllabus/readings.md) are ready now.
:::


## Learning objectives

By the end of this session, you will be able to:

- Use `show_errors` to find misclassifications, hypothesize a fix, and re-run — the same **generic → structured refinement** you saw in Huang & Mizumoto's Example Prompt 1 → 2 (Session 7), now driven by error data.
- Compare **macro-F1** across iteration rounds.
- Benchmark the best LLM prompt against a **pre-trained spaCy classifier** on the same held-out CEFR test set.
- Interpret what supervised fine-tuning **buys and costs** versus zero-training prompting — the LLM as an assistant to evaluate and supervise, not a verdict to accept.

## Reading

No new reading for this session — see the Day 3 reading (Huang & Mizumoto, 2025; Kim & Lu, 2024) in [Session 7](session-07.md) and on the [Readings](../../syllabus/readings.md) page.

## Slides & Colab
<!-- Slides: [Session 9 slides](../../slides/slides-session-09.html){target="_blank"} -->
<!-- Colab notebook link: to be added -->
