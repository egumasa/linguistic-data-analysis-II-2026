---
title: "Session 7: Prompt Design — Zero-shot vs Few-shot"
subtitle: "Day 3 · Prompt Design & Iteration (3-1)"
toc: true
---
<!-- BEING-PREPARED-BANNER -->

::: {.callout-warning appearance="simple"}

## 🚧 Being prepared

This page is being finalized ahead of the course (**Aug 3–7, 2026**) and may be incomplete or change before your session. The [syllabus](/syllabus/index.md) and [readings](/syllabus/readings.md) are ready now.
:::

## Learning objectives

By the end of this session, you will be able to:

- **Name the four prompt elements** — *instruction · context · input data · output indicator* — and locate each in a real prompt.
- Distinguish **zero-shot** from **few-shot** prompting and judge **when examples help**.
- Explain **chain-of-thought** prompting and where it earns its keep.
- Place a technique on the **run-it-this-week vs. know-it-exists** line (zero/few/CoT and structured output vs. self-consistency, RAG, and agentic prompting).
- Explain the **train/test contamination** trap and why you **tune on a validation set** but **report on a held-out test set**.

The message of the day: a prompt has parts you can design, and small changes to those parts change the score.

## Agenda

1. **The anatomy of a prompt** — the four elements (*instruction · context · input data · output indicator*), and how structure and persona sharpen the instruction. Worked on Huang & Mizumoto's (2025) writing-feedback prompt.
2. **Zero-shot, few-shot, chain-of-thought** — what examples actually buy you, read off a real results table from Kim & Lu (2024), including where prompting alone stops improving and fine-tuning takes over. Then chain-of-thought, and the Example Prompt 1 → Example Prompt 2 refinement.
3. **The wider design space** — which techniques to *run* this week and which to simply *know about* (self-consistency, RAG, agentic prompting).
4. **Two errors to avoid before you tune** — train/test contamination, and tuning on validation while reporting on test.

The four elements return in [Session 8](session-08.md), mapped onto the CEFR classification task, and again in [Session 9](session-09.md) as the error-analysis iteration loop.

## Reading

**Read** (see all [course readings](../../syllabus/readings.md)):

- Huang, J., & Mizumoto, A. (2025). Prompt engineering: Enhancing AI-driven language learning and feedback. In L. McCallum & D. Tafazoli (Eds.), *The Palgrave Encyclopedia of Computer-Assisted Language Learning* (pp. 1–8). Springer Nature Switzerland. [https://doi.org/10.1007/978-3-031-51447-0_103-1](https://doi.org/10.1007/978-3-031-51447-0_103-1)
- Kim, M., & Lu, X. (2024). Exploring the potential of using ChatGPT for rhetorical move-step analysis: The impact of prompt refinement, few-shot learning, and fine-tuning. *Journal of English for Academic Purposes, 71*, 101422. [https://doi.org/10.1016/j.jeap.2024.101422](https://doi.org/10.1016/j.jeap.2024.101422)

::: {.callout-note appearance="simple"}

**Running example (Day 3).** We anchor the whole day in Huang & Mizumoto's worked prompts — **Example Prompt 1** (a generic chain-of-thought paragraph-feedback prompt) refined into **Example Prompt 2** (the structured *Task / Criteria / "My paragraph"* prompt). That same structure returns in **Session 8** (mapped onto the CEFR classification prompt) and in **Session 9** (as the error-analysis iteration loop). A self-study map of the wider technique landscape: the [Prompt Engineering Guide](https://www.promptingguide.ai/techniques).
:::


## Slides & Colab

<!-- Slides: [Session 7 slides](../../slides/slides-session-07.html){target="_blank"} -->

<!-- Colab notebook link: to be added -->
