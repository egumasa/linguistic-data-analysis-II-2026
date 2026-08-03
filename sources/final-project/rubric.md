---
title: "Rubric"
subtitle: "What is graded — and what is not"
toc: true
---
::: {.callout-important}

## The accuracy is not graded

A careful study reporting **F1 = 0.31** with a clear account of *why* scores higher than a sloppy one reporting **0.82**.

What is graded is whether your numbers are **defensible**: reproducible (frozen predictions, pinned model, `temperature=0`), honestly reported, and interpreted. A low κ is likewise not a penalty — it is a finding about your scheme.
:::

This matters for your track choice. `cars50` is the hardest track precisely because its own annotators only reached κ ≈ 0.43 — which makes it the *best* track for showing you can tell "the model is wrong" apart from "the scheme is fuzzy". Picking the easy track to protect your F1 buys you nothing here.

## Presentation + Q&A

Four criteria. The weighting is on the syllabus.

1. **The pipeline is narrated as an I/O chain** — what each step consumes and produces — not
   read off the slides. This is the [`PLAN.md`](plan.md) table, out loud.
2. **The mandatory error item is answered with a reasoned attribution.** Evidence from the
   item itself, not "the model is bad at C1".
3. **The QC pass is described concretely**: how many labels changed, which label pair caused
   the most disagreement, and what your scheme now says about it.
4. **Every member speaks** and can answer a question about their own slide.

## Two-page report

**Written individually**, so this part of your mark is your own. Six sections, each scored
on **specificity** — named items and actual numbers, not high numbers.

| Section                | What earns the marks                                                                          |
| ---------------------- | --------------------------------------------------------------------------------------------- |
| 1 · Intro             | what the topic is and why it matters, in your own framing                                    |
| 2 · Methodology       | the corpus and sampling; the label set, sample size, per-label counts, your κ and**what adjudication changed**; and your split, with a reason |
| 3 · Prompt iterations | ≥2 rounds, each with a**stated reason** for the change — not "added examples"         |
| 4 · Evaluation        | per-class P/R/F1 + confusion matrix + which class did worst, and what it was confused with    |
| 5 · Error analysis    | ≥3 misses attributed to model or scheme,**with a reason each**                         |
| 6 · Limitations       | ≥2 that apply to**your** run — not the three generic ones anyone could write         |

Sections 5 and 6 are where two members of the same group should visibly diverge. You ran
one study together; what you make of its errors, and which of its limits you think matter
most, is yours to argue.

## Two mechanical integrity checks

Neither is about suspicion; both are about the numbers meaning what they say.

- **`PLAN.md` signed before the first model call.** A final run made before sign-off is not
  accepted as the final run. (See [the gate](plan.md).)
- **`scripts/` is unmodified.** The plumbing is documented as not-to-be-edited, so your
  submitted copy is diffed against the template. A changed `metrics.py` or `pipeline.py` needs
  explaining before the numbers can be taken at face value.

If you *did* need to change something in `scripts/` — a bug, a track the helpers do not
handle — say so in your limitations section and explain what and why. That is a perfectly good
outcome. Silently changing it is not.

## Completed notebook

Graded under hands-on. What is checked: it runs top to bottom on a fresh runtime, your frozen
predictions file exists, and the numbers in your report are the ones the notebook actually
produces.
