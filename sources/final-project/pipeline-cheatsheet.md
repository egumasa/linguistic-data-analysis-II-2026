---
title: "Pipeline cheat-sheet"
subtitle: "Every helper, and where you already used it"
toc: true
---

The project notebook's step cells give you the goal and the available helpers, but not the
calls. This page is the reference for writing them.

**Eight of the fourteen helpers are byte-identical to a call you already made this week.**
That is the whole reason a blank spine is reasonable rather than cruel.

## The pipeline, end to end

```
pool ──sample──▶ sampled ──annotate──▶ sheet ──adjudicate──▶ gold
                                                              │
                            prompt ─────────────┐             │
                                                ▼             ▼
                                          run_prompt ──▶ predictions
                                                              │
                                                    save_predictions
                                                              │
                                                              ▼
                                                       FROZEN FILE
                                                              │
                                         ┌────────────────────┤
                                         ▼                    ▼
                                    evaluate              show_errors
                                         │                    │
                                         └──────▶ export ◀─────┘
```

Everything after the frozen file reads from **that file**, not from the model. That is what
makes your reported numbers hold still.

## The mapping

| Step | Helper | Where you ran it before | Same call? |
|---|---|---|---|
| 1 | `load_gold(path)` | Day 2 S5 step F · Day 3 setup | ✅ identical |
| 1 | `sample_pool(pool, n_per_class, seed)` | Day 4 Part A — as four inline steps | one call instead of four |
| 1 | `label_set(gold)` | new (one line) | — |
| 2 | `create_annotation_sheet(title, items, labels)` | Day 2 S5 step A | ✅ identical |
| 2 | `load_annotation_sheet(sheet_id, worksheet)` | Day 2 S5 step D | ✅ identical |
| 2 | `annotator_agreement(rows)` | Day 2 S5 step D | ✅ identical |
| 2 | `disagreements(rows)` | Day 2 S5 step E | ✅ identical |
| 2 | `to_canonical(rows, labels)` | Day 2 S5 step F | ✅ identical |
| 2 | `compare_to_published(gold, sampled)` | Day 2 S5 step F | ✅ identical |
| 3 | `load_prompt(path)` | new — your prompt is a *file* now | — |
| 3–4 | `run_prompt(PROMPT, gold)` | Day 3, every iteration | ✅ identical |
| 3–4 | `evaluate(gold, pred, ordered=True)` | Day 2 S6 Part B · Day 3 | ✅ identical |
| 4 | `build_fewshot(PROMPT, pool, gold)` | Day 3 iteration 1 — you typed the examples by hand | one call instead of typing |
| 4 | `save_predictions(pred, path)` · `load_predictions(path)` | Day 2 S6 loaded a frozen file; now you make one | — |
| 5 | `show_errors(gold, pred)` | Day 3 | ✅ identical |
| 6 | `export_results(track, gold, pred, f1_by_round, out_dir, group=…)` | new | — |

If a call you learned in the tutorials does **not** work in the template, that is a bug in the
template, not in your memory of it. Say so — there is an automated test (
`scripts/_check_call_forms.py`) whose entire job is to stop that happening.

## Three things that are easy to get wrong

**`compare_to_published(gold, sampled)` — not `pool`.** Sampling renumbers the ids from 1, so
comparing against the whole pool would pair *your item 7* with *pool item 7*: two unrelated
sentences. (The helper matches on text, so it copes — but pass `sampled` and mean it.)

**`ordered=True` only when the labels sit on a scale.** `A1 < A2 < … < C2` and `Move 1 < 2 <
3` do; error categories do not. And if your labels are ordered but *not alphabetical* —
`Low`/`Mid`/`High` — you must pass the order yourself:

```python
evaluate(gold, pred, ordered=True, labels=LABELS_ORDER)
```

Otherwise the weighted κ is computed over `High < Low < Mid`, which means nothing. `evaluate`
prints the order it used, so check that line.

**Iterate small, then freeze once.** At `N_PER_CLASS = 7`, one round is ~40 model calls and
several minutes of enforced pacing; the free tier gives you about 500 calls a day. So keep
`N_PER_CLASS = 2` while you are still changing the prompt, then raise it for the single final
run you freeze.

## Reading the helpers

They are all in `scripts/`, written the long way on purpose. `help(sample_pool)` prints any
signature. `metrics.py` is the one worth reading: it is the library version of the
precision/recall/F1/κ functions you wrote by hand in
[Session 6](../sessions/day2/session-06.md).
