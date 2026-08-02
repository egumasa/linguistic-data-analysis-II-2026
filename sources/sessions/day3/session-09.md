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
- Compare **macro-F1** across iteration rounds, and keep the validation/test distinction honest.
- Place your prompted-LLM result next to the **published supervised results for the same corpus** (Arase et al., 2022) — and say what the comparison does and does not license.
- Interpret what supervised training **buys and costs** versus zero-training prompting — the LLM as an assistant to evaluate and supervise, not a verdict to accept.

## Agenda

1. **Error analysis** — the number shows *that* something changed; the errors show *why*. Read down the per-class F1 column first, then separate the two causes: the model is wrong, or the scheme is fuzzy.
2. **Iterating the prompt** — say what you expect before you run it, then check the class you aimed at. One change per round.
3. **Inside `run_prompt`** — a walkthrough of the helper you have called all day: how it fills the `{text}` slot, paces the calls to stay under the rate limit, retries on a `429`, scans the reply for the label, and returns labels in gold order. You do not edit it; the point is being able to describe what it does.
4. **The LLM is one option, not the only one** — put your score next to the published supervised results for the same corpus, and work out what that comparison does and does not license.

## The CEFR wrap-up

You spent Day 3 pushing a prompt as far as it goes on CEFR levels. The closing question is
the honest one: **how good is that, really?**

Arase, Uchida & Kajiwara (2022) — the paper behind the corpus you have been using since
Session 4 — trained models on this exact task and reported them in their Table 6. Their test
split is 3,012 sentences; ours is a balanced 72-item draw, so these are *not* the same
measurement. But both are macro-F1 over the same six labels on the same corpus, which is
enough to see where prompting sits:

| System | macro-F1 | Quadratic weighted κ |
|---|:--:|:--:|
| Bag-of-words + SVM (their naive baseline) | 41.2 | 0.354 |
| *k*-NN over frozen BERT embeddings | 38.8 | 0.373 |
| BERT-Base classifier, loss-weighted | 82.5 | 0.609 |
| Their proposed metric-based model | **84.5** | **0.628** |
| *Our zero-shot prompt, Day 2 frozen run (72 items)* | *≈36* | *0.849* |

Two things to take from this, both uncomfortable in a useful way:

1. **A zero-shot prompt lands near a bag-of-words baseline, not near a trained model.** The
   gap to 84.5 is what a labelled training set buys — and CEFR-SP took trained experts to
   build. That is the cost side of the trade.
2. **Our weighted κ looks *better* than theirs.** It is not, and working out why is the
   exercise: our 72 items are balanced 12-per-level while their test set is not, and κ is
   sensitive to the marginal distribution. A number that flatters you across two different
   test sets is exactly the kind of comparison a reader should refuse — and the kind your
   own report must not make.

The point is not that prompting is bad. It is that "the model got 36" means nothing until
you can say *36 compared to what, on which items*.

## Reading

## Reading

No new reading for this session — see the Day 3 reading (Huang & Mizumoto, 2025; Kim & Lu, 2024) in [Session 7](session-07.md) and on the [Readings](../../syllabus/readings.md) page.

## Slides & Colab
<!-- Slides: [Session 9 slides](../../slides/slides-session-09.html){target="_blank"} -->
<!-- Colab notebook link: to be added -->
