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

- **Name the main classes of prompting strategies** — instruction structuring · in-context learning · thought generation · decomposition · ensembling · self-criticism — and say which ones we run this week.
- **Locate the components of a prompt** — *directive · examples · output formatting · style instructions · role · additional information* — in a real prompt.
- Distinguish **zero-shot** from **few-shot** prompting and judge **when examples help**.
- Explain **chain-of-thought** prompting and which tasks it improves.
- Explain the **train/test contamination** trap and why you **tune on a validation set** but **report on a held-out test set**.

The message of the day: a prompt has parts you can design, and small changes to those parts change the score.

## Agenda

1. **A map of prompting strategies** — the many named techniques group into a few **strategy classes**, each answering a different question about the model call: instruction structuring · in-context learning · thought generation · ensembling · self-criticism · decomposition.
2. **Instruction structuring** — the six components of a prompt (*directive · examples · output formatting · style instructions · role · additional information*), read off Huang & Mizumoto's (2025) writing-feedback prompt.
3. **In-context learning and thought generation** — zero-shot vs. few-shot, what examples actually teach, and the results table from Kim & Lu (2024), including where prompting alone stops improving and fine-tuning takes over. Then chain-of-thought, and the Example Prompt 1 → Example Prompt 2 refinement.
4. **Three strategy classes to know about, not run** — ensembling (self-consistency), self-criticism (and why not to use an LLM to check your own labels), decomposition (prompt chaining, RAG).
5. **Two errors to avoid before you tune** — train/test contamination, and tuning on validation while reporting on test.

The prompt components return in [Session 8](session-08.md), mapped onto the CEFR classification task, and again in [Session 9](session-09.md) as the error-analysis iteration loop.

## Reading

**Read** (see all [course readings](../../syllabus/readings.md)):

- Huang, J., & Mizumoto, A. (2025). Prompt engineering: Enhancing AI-driven language learning and feedback. In L. McCallum & D. Tafazoli (Eds.), *The Palgrave Encyclopedia of Computer-Assisted Language Learning* (pp. 1–8). Springer Nature Switzerland. [https://doi.org/10.1007/978-3-031-51447-0_103-1](https://doi.org/10.1007/978-3-031-51447-0_103-1)
- Kim, M., & Lu, X. (2024). Exploring the potential of using ChatGPT for rhetorical move-step analysis: The impact of prompt refinement, few-shot learning, and fine-tuning. *Journal of English for Academic Purposes, 71*, 101422. [https://doi.org/10.1016/j.jeap.2024.101422](https://doi.org/10.1016/j.jeap.2024.101422)

::: {.callout-note appearance="simple"}

**Running example (Day 3).** We anchor the whole day in Huang & Mizumoto's worked prompts — **Example Prompt 1** (a generic chain-of-thought paragraph-feedback prompt) refined into **Example Prompt 2** (the structured *Task / Criteria / "My paragraph"* prompt). That same structure returns in **Session 8** (mapped onto the CEFR classification prompt) and in **Session 9** (as the error-analysis iteration loop). A self-study map of the wider technique landscape: the [Prompt Engineering Guide](https://www.promptingguide.ai/techniques).
:::


## Slides & Colab

- Slides: [Session 7 slides](../../slides/slides-session-07.html){target="_blank"}

<!-- Colab notebook link: to be added -->
