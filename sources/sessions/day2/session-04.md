---
title: "Session 4: Annotation Principles & Inter-Annotator Agreement"
subtitle: "Day 2 · Annotation, Gold Standards & Metrics (2-1)"
toc: true
---
<!-- BEING-PREPARED-BANNER -->

::: {.callout-warning appearance="simple"}

## 🚧 Being prepared

This page is being finalized ahead of the course (**Aug 3–7, 2026**) and may be incomplete or change before your session. The [syllabus](/syllabus/index.md) and [readings](/syllabus/readings.md) are ready now.
:::

## Learning objectives

By the end of this session you will be able to:

- Place a linguistic annotation task in the classic NLP taxonomy — *identify · extract · categorize*, organized by **unit of analysis**.
- Describe the NLP **evaluation workflow** (gold → predictions → metrics), and explain how it transfers from a trained model to a prompted **LLM**.
- Operationalize a linguistic category into an **annotation scheme** with coding guidelines.
- Explain **inter-annotator agreement**: percent agreement, why **Cohen's κ** corrects for chance, and when to use **quadratic weighted κ** for *ordered* labels.
- Read a **confusion matrix** and compute **precision, recall, and F1** from its four cells (TP · TN · FP · FN).

The message of the day: labelled data is only trustworthy if the category is **operationalized** and two coders agree **beyond chance**.

## Agenda

**A · What NLP tasks are there** — what annotation is, and the task taxonomy made concrete with linguistic examples: part of speech, word sense disambiguation, syntactic dependency, stance, and discourse moves. Tasks organized by unit and output — token-level sequence labelling, span categorization, and one label per unit. This course focuses on **sentence and text categorization**, where the evaluation code is manageable and the `{id, text, label}` shape from [Session 3](../day1/session-03.md) is enough; span tasks bring boundary and partial-match problems that do not fit five days.

**B · How NLP evaluates a system — and how it transfers to LLMs** — the evaluation workflow, and what changes when you swap a trained model for a prompted LLM. The four outcomes (TP · TN · FP · FN), precision and recall, accuracy between two coders, and **Cohen's κ** as agreement beyond chance — how much κ is enough, and **quadratic weighted κ** when labels are ordered.

**C · The define-first workflow** — you cannot evaluate what you have not defined. The five phases, borrowed from Eguchi & Kyle's (2024) model-agnostic pipeline: ① define the annotation task, ② operationalize it into a scheme and guidelines, ③ build the gold standard, ④ set the target at human agreement, ⑤ evaluate the LLM against gold.

**D · The dataset for the class tutorials** — Arase, Uchida & Kajiwara (2022), the **CEFR-SP** corpus: 17k English sentences, each labelled with a CEFR level. One sentence in, one level out — familiar enough to be worth doing and small enough to finish in five days.

This is the conceptual grounding for the hands-on annotation in [Session 5](session-05.md), which executes phases ①–③, and the evaluation code in [Session 6](session-06.md), which executes phases ④–⑤.

::: {.callout-note}
**Before Session 5, skim §3.1 and §3.2 of Arase et al. (2022)** — about a page and a half. The afternoon session opens by asking you to pull two design decisions out of it.
:::

## Reading

**Read** (see all [course readings](../../syllabus/readings.md), including optional Day 2 items):

- Eguchi, M., & Kyle, K. (2024). Building custom NLP tools to annotate discourse-functional features for second language writing research: A tutorial. *Research Methods in Applied Linguistics, 3*(3), 100153. [https://doi.org/10.1016/j.rmal.2024.100153](https://doi.org/10.1016/j.rmal.2024.100153)

## Slides & Colab

<!-- Slides: [Session 4 slides](../../slides/slides-session-04.html){target="_blank"} -->

<!-- Colab notebook link: to be added -->
