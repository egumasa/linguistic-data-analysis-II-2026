---
title: "Day 3 Tutorial — Replicating Kim & Lu with Open Data"
subtitle: "Prompt design & iteration for discourse-move annotation"
toc: true
---

> **Goal.** Replicate the core idea of **Kim & Lu (2024)** — using an LLM to annotate rhetorical
> **moves** — and see how *prompt refinement* and *few-shot examples* change accuracy. Same pipeline
> as [Day 2](./tutorial-day2-annotation-eval.md); a much harder *judgment*.

::: {.callout-important}
## From Day 3 you run the model yourself — with a free key
Days 1–2 were keyless (Day 1's demo used Colab's built-in Gemini; Day 2 read frozen predictions). Now
you call the model live, and — because you compare prompts and the Corpus Labs are **autograded** —
runs must be **reproducible**. The notebooks use the **Gemini API** with `temperature=0` + a fixed
seed, so re-running gives the same numbers and prompt-to-prompt differences reflect the *prompt*, not
noise. One-time setup (~2 min, no install): [get a free Gemini API key](../tools/gemini-api-key.md)
and add it to Colab Secrets. When you settle on a prompt, **freeze its predictions to JSON** so your
reported F1 is auditable.
:::

## Why this task is hard (and why that's the point)

Deciding a sentence's **move** ("is this *Background* or a *Gap*?") requires reading rhetorical
intent in context. Even trained experts disagree: the CaRS-50 annotators reached only
**κ ≈ 0.43**. So do not expect CEFR-level F1 here. The research question is not "can the model be
perfect?" but "**how much does better prompting help, and where does it still fail?**" — exactly
Kim & Lu's question.

## Step 1 — Start clean: RAAMove (8 moves)

Begin with `gold/raamove_moves.json` (64 sentences from RA abstracts, balanced across 8 moves:
Background, Gap, Method, Purpose, Result, Conclusion, Contribution, Implication) — build it with the
[RAAMove download notebook](../datasets/notebooks/download_raamove.ipynb). It is tidy JSON, so you can
focus on the *prompt*.

### Iteration 0 — zero-shot

```text
Classify the move of this sentence from a research abstract into exactly one of:
Background, Gap, Method, Purpose, Result, Conclusion, Contribution, Implication.
Answer with the move only.

Sentence: {text}
```

Run `evaluate`. Note the macro-F1 and the confusion matrix — which moves collapse into each other?
(Implication ↔ Conclusion and Background ↔ Gap are common.)

### Iteration 1 — prompt refinement

Add **short definitions** of each move (one line each) to the prompt. Re-run. Did F1 rise? Which
confusions shrank?

### Iteration 2 — few-shot

Add **one or two example sentences per move** (drawn from `raamove_pool.json`, *not* from your gold
set). Re-run. This mirrors Kim & Lu's finding that few-shot examples and prompt refinement each give
real but modest gains.

::: {.callout-important}
## Keep examples out of your test set
Few-shot examples must come from the **pool** file, never from the gold file you are scoring on —
otherwise you are testing on training data.
:::

## Step 2 — The real replication: CaRS-50 (CARS moves)

Now switch the gold file to `gold/cars50_moves.json` (build it with the
[CaRS-50 download notebook](../datasets/notebooks/download_cars50.ipynb)) — Swales'
**CARS Move 1/2/3** in article *introductions*, the same scheme Kim & Lu used. Re-use your best
prompt (adapt the label set and definitions to Moves 1–3). Compare:

- How does F1 on CaRS-50 compare to RAAMove? Why might introductions be harder than abstracts?
- Stretch: switch to the 11-class **Move+Step** labels
  (`cars50_step_pool.json`) — build a small balanced gold set
  from the pool and watch F1 drop as the label set gets finer.

## Step 3 — Error analysis → next prompt

Run `show_errors` and sort the misses by gold label. For the worst class, write **one concrete
prompt change** you predict will help, then test it. Log each iteration's macro-F1 so you can show
the improvement curve — this table *is* your mini-result.

| Iteration | Prompt change | Macro-F1 |
|-----------|---------------|:--------:|
| 0 | zero-shot | … |
| 1 | + move definitions | … |
| 2 | + few-shot examples | … |

## Discussion (ties back to Kim & Lu)

- Did prompt refinement or few-shot help more? Kim & Lu found both helped, but **fine-tuning** (which
  we do not do here) gave the biggest jump.
- Where the model fails, is it the *model* or the *scheme* (recall κ ≈ 0.43)? How would you report
  that honestly in your presentation?

➡️ Ready to run your own study? [Mini-project starter tracks](../datasets/mini-project-tracks.md)
