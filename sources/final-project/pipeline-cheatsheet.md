---
title: "What you have to work with"
subtitle: "Every call the project notebooks offer, and where you first ran it"
toc: true
---

The project notebooks hand you the *mechanics* — paths, file names, the Google Sheets
round-trip, the pacing between API calls, what each notebook passes to the next. What they
do not hand you is the **method**: which agreement statistic your design owes, what counts
as a disagreement, which prompt move to try next, which number your report leads with.
Those you choose, and defend.

This page is the inventory you choose from. Every row says what the call gives you and
**where you first ran it**, so nothing on a project inventory is new.

::: {.callout-note}
## If a call does not work the way you remember it

That is a bug in the template, not in your memory. Say so — there is an automated check
(`scripts/_check_call_forms.py`) whose entire job is to keep every Day 1–3 call form
working unchanged.
:::

## The pipeline, as an I/O chain

```
01 build pool ──▶ pool.json
                    │
02 sample ──────────┴──▶ sample.json  +  the annotation Sheet
                                              │
03 annotate ──────────────────────────────────┴──▶ gold.json ──▶ dev.json
                                                              └─▶ test.json
                                                                    ·
04 develop ── dev.json ──▶ prompts/*.txt  +  rounds.json           ·  untouched
                                    │                              ·
05 test ────────────────────────────┴── test.json ──▶ predictions.json + test_log.jsonl
                                                              │
06 report ────────────────────────────────────────────────────┴──▶ report.md
```

**04 and 05 are two files rather than two halves of one** so that "you may not look at the
test set while you iterate" is a file boundary rather than a scroll position.
`04_develop.ipynb` has no path to your test items at all.

Everything from `05_test` onward reads the **frozen predictions file**, not the model. That
is what makes the numbers in your report hold still.

## 03 · Annotate — how far apart were your coders

You assemble these. Which of them you owe follows from two facts you already have: how many
coders, and whether your labels sit on a scale.

| Call | What it gives you | Where you first ran it |
|---|---|---|
| `load_coder_sheets(id, CODERS)` | one tab per coder, joined by item id | Day 2 S5 step D |
| `column(rows, "CoderA")` | one coder's labels as a plain list | new here — two lines |
| `percent_agreement(a, b)` | how often two coders matched | Day 2 S6 step 9 — you computed it by hand, as `p_o` |
| `cohen_kappa_score(a, b)` | agreement corrected for chance | Day 2 S6 — you wrote it, then checked it against this |
| `cohen_kappa_score(a, b, weights="quadratic")` | the same, a near miss counting less | Day 2 S6 Part B |
| `fleiss_kappa([a, b, c])` | one number for three or more coders | new — three-coder groups only |
| `confusion_matrix(a, b, labels=LABELS)` | *which* label pairs you disagree about | Day 2 S5 step D · S6 Part B |
| `plot_confusion_matrix(m, LABELS, title)` | that matrix, drawn | Day 2 S5 step D |
| `to_canonical(rows, LABELS)` | the adjudicated sheet as gold items | Day 2 S5 step F |
| `compare_to_published(gold, sampled)` | where you differ from the corpus's own labels | Day 2 S5 step F |
| `split_dev_test(gold, DEV, seed=SEED)` | the two halves, every label kept on both sides | Day 4 Part B — you wrote the loop |
| `triage_counts(t, disagreed, categories=CODER_CATEGORIES, what="disagreements")` | your reading of the disagreements, counted | new here — the same four words as Day 2 S6 Part B, one changed |

The `triage_counts` row is optional — notebook 03 says when it is worth the ten minutes, and
everything downstream works without it.

**`disagreements` is not on this list, because you write it.** The rule inside it — what
counts as a disagreement — is a decision about your scheme, and there is no way to hand it
over without answering it for you. You saw the six lines in Day 2 S5, step E.

## 04 · Develop — the prompt rounds, on dev only

| Call | What it gives you | Where you first ran it |
|---|---|---|
| `setup(temperature=TEMPERATURE, seed=SEED, model=MODEL)` | the connection, with the two settings that decide whether a run repeats | Day 3, iteration 0 |
| `load_prompt(path)` | a prompt file, as text | new — your prompt is a *file* now |
| `run_prompt(prompt, dev)` | one predicted label per item | Day 3, every iteration |
| `build_fewshot(prompt, pool, gold)` | the prompt with worked examples in front of it | Day 3 iteration 1 — you typed the examples by hand |
| `extract_label(reply, labels)` | one label out of one reply | Day 3, as the parser behind `run_prompt` |
| `evaluate(dev, pred, ordered=False)` | per-class table, κ, matrix, and macro-F1 back | Day 2 S6 Part B · Day 3 |
| `show_errors(dev, pred)` | just the rows it got wrong | Day 2 S6 Part B · Day 3 |

**And the prompt itself is the other half.** S7's menu — instruction · context · input data ·
output indicator · persona · few-shot · chain-of-thought · structured output — is the space
you are choosing from. Few-shot is one row of that table, not the default.

The number `evaluate` hands back is macro-F1, and here it is only something to compare round
2 against round 1 with. The number you report comes out of `06_report`, where you write the
scoring call yourself.

## 05 · Test — the held-out run

| Call | What it gives you | Where you first ran it |
|---|---|---|
| `freeze_test_run(...)` | runs, saves before scoring, re-reads the file, scores it, logs it | Day 3's "once, and only once" cell, made explicit |
| `read_test_log(path)` | every held-out scoring you have done, with a fingerprint of each prompt | new |

Nothing here stops you running it twice — stopping you would be the wrong design, because a
real mistake on the last afternoon needs a way forward. Instead nothing is overwritten and
every scoring appends a line to a log that travels in your submission.

## 06 · Report — the scoring call *is* the choice

There is no course helper wrapping these. You met them in Day 2 S6: you built precision,
recall, F1 and κ from scratch, then checked your numbers against these very functions.

| Call | What it gives you | Where you first ran it |
|---|---|---|
| `labels_of(test)` | the gold labels as a plain list, ready to score | new here — you wrote the same loop in Day 2 S6 |
| `classification_report(y, p, labels=LABELS)` | precision, recall and F1 for **every** class | Day 2 S6 Part B |
| `f1_score(y, p, average="macro")` | one number: every **class** counts the same | Day 2 S6 Part B |
| `f1_score(y, p, average="micro")` | one number: every **item** counts the same | Day 2 S6 Part B |
| `f1_score(y, p, average="weighted")` | between the two: classes weighted by how common | Day 2 S6 Part B |
| `cohen_kappa_score(y, p)` | agreement with your gold, corrected for chance | Day 2 S6 |
| `cohen_kappa_score(y, p, weights="quadratic")` | the same, a near miss counting less | Day 2 S6 Part B |
| `confusion_matrix(y, p, labels=LABELS)` | which classes it mixes up with which | Day 2 S6 Part B |
| `plot_confusion_matrix(m, LABELS, title)` | that matrix, drawn | Day 2 S5 step D |
| `show_errors(test, pred)` | just the rows it got wrong | Day 2 S6 Part B · Day 3 |
| `errors_on_disagreed(errors, disagreed)` | the errors landing where **your** coders also disagreed | Day 2 S6 Part B, written out as a loop |
| `triage_category(line, CODER_CATEGORIES)` | reads back the triage you wrote in 03, so you can ask whether the model missed the items *you* called `scheme` | 03, if you did its optional section |
| `triage_counts(TRIAGE, errors)` | your judgments, counted by category | new here — the four words are Day 2 S6 Part B, where you sorted errors aloud rather than writing them down |
| `export_results(...)` | the report scaffold, the predictions CSV, your test set | new |

## Things that are easy to get wrong

**`compare_to_published(gold, sampled)` — not `pool`.** Sampling renumbers the ids from 1, so
comparing against the whole pool would pair *your* item 7 with *pool* item 7: two unrelated
sentences.

**Weighted κ needs the order.** If your labels are ordered but not alphabetical —
`Low`/`Mid`/`High` — set `labels_order` in `config.yaml`. Otherwise the weighting is computed
over `High < Low < Mid`, and the number reported to three decimal places means nothing.

**dev is the fast set.** One round on a dozen dev items is about a minute of enforced pacing,
so your sample stays at full size throughout — you do not shrink it to iterate.

**The κ in 03 and the κ in 06 are different claims.** One compares two annotators, the other
compares your gold against a model. Same statistic, and swapping them in the report is a
mistake a reader cannot catch.

## Reading the code

Everything imported lives in `scripts/`. `help(split_dev_test)` prints what to pass in;
`split_dev_test??` prints the source of any function, imported or not; and the Files panel on
the left of Colab lists every function in a file, so you can click straight to one.

Some of what you call is not imported at all — it is written out in the notebook cell in
front of you, because reading it is part of knowing what you did. Those you can edit in
place, and your edited version is in the notebook you hand in, which is where a change of
method should be visible.
