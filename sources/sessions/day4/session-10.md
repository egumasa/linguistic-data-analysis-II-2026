---
title: "Session 10: Methodology — Reproducibility, LLM Limits & Ethics"
subtitle: "Day 4 · Methodology & Pipeline Assembly (4-1)"
toc: true
---

<!-- BEING-PREPARED-BANNER -->
::: {.callout-warning appearance="simple"}
## 🚧 Being prepared
This page is being finalized ahead of the course (**Aug 3–7, 2026**) and may be incomplete or change before your session. The [syllabus](/syllabus/index.md) and [readings](/syllabus/readings.md) are ready now.
:::


## Learning objectives

By the end of this session you will be able to:

- Name the practices that make an LLM result reproducible — pin the model and version, log the prompt, set `temperature=0` and a seed, and **run once → freeze the predictions → evaluate off the frozen file**.
- Explain why a hosted LLM is only *best-effort* reproducible even at `temperature=0`, and what freezing buys you that a seed alone does not.
- Name the main limits — hallucination, **data contamination**, stochasticity — and say which of them your own study is exposed to.
- Apply a five-section reporting checklist to your own project, and say what your numbers do **not** show.

## Agenda

1. **Recap** — three days of "an LLM is a judge you must check". Today: how to report one honestly.
2. **Reproducibility in practice** — pin · log · `temperature=0` + seed · freeze.
3. **Limits** — hallucination, contamination, stochasticity. Which apply to *your* track?
4. **Ethics** — privacy in learner data, authorship, and what you owe a corpus's licence.
5. **The reporting checklist** — the six sections your report must cover, and why each exists.

This session is the switch from tutorial mode to project mode. Everything after it is your own study.

## Reading

**Read in full** — revisit the Day 1 primer closely, this time as a reproducibility checklist (see all [course readings](../../syllabus/readings.md)):

- Abdurahman, S., Ziabari, A. S., Moore, A. K., Bartels, D. M., & Dehghani, M. (2025). A primer for evaluating large language models in social-science research. *Advances in Methods and Practices in Psychological Science, 8*(2). <https://doi.org/10.1177/25152459251325174>

## Slides & Colab

<!-- Slides: [Session 10 slides](../../slides/slides-session-10.html){target="_blank"} -->

## Mini-project

The checklist you build here **is** the report you hand in — see
[Deliverables](../../final-project/deliverables.md) and the
[Rubric](../../final-project/rubric.md).

Worth knowing now: **your F1 is not graded.** A careful study reporting 0.31 with a clear
account of why scores higher than a sloppy one reporting 0.82.
