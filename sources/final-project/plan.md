---
title: "The PLAN.md gate"
subtitle: "作戦シート — one page, written before you call the model"
toc: true
---

Before your group runs the model even once, you write a one-page `PLAN.md` and have it
signed off. It is **not graded**. It is a gate.

## Why bother

You have been building this plan all week without writing it down — the 作戦シート from the
[S3](../sessions/day1/session-03.md), [S6](../sessions/day2/session-06.md) and
[S9](../sessions/day3/session-09.md) huddles. This is that sheet, finally given a file.

Two minutes of writing catches the failures that otherwise cost an hour *after* you have
already spent quota on them:

- Your label set says `Move 1/2/3`, your gold file says `1a/1b/2a`, and your prompt says
  "move one". Nothing errors — you just get a confusing F1.
- Your labels are ordered but not alphabetical (`Low`/`Mid`/`High`), so the weighted κ is
  silently computed over `High < Low < Mid` and reported to three decimal places.
- Nobody agreed who annotates which column, so you have one annotator and no κ at all.

Question 3 exists entirely to catch the second one.

## The template

Copy this into `PLAN.md` at the root of your cloned template repo and fill it in.

```markdown
# PLAN — <group>, track <track>
Members: …

1. Unit of analysis: (sentence / whole text) — and why
2. Label set: … (exactly the strings that appear in your gold file)
3. Are the labels ORDERED? If yes, in what order?
   (this decides LABELS_ORDER in the notebook's CONFIG cell)
4. Gold: pool file · N_PER_CLASS · SEED · expected total items
5. QC: who codes CoderA, who codes CoderB, who adjudicates
6. Prompt plan: your baseline idea, then the ONE change you predict
   will help — and why you think so

| # | Step | Consumes | Produces |
|---|------|----------|----------|
| 1 | sample           | POOL_PATH, N_PER_CLASS, SEED | pool, sampled, LABELS |
| 2 | QC / adjudicate  | sampled, LABELS, the sheet   | gold |
| 3 | baseline         | PROMPT, gold                 | pred0, f1_by_round["0…"] |
| 4 | iterate + freeze | PROMPT, pool, gold           | pred_final (a JSON file) |
| 5 | error analysis   | gold, pred_final             | the errors table |
| 6 | export           | all of the above             | outputs/…_report.md |
```

The table is the point of the exercise. If your group can say aloud *"step 2 consumes
`sampled` and the sheet, and produces `gold`"*, you understand the pipeline — and that is
what the end of [Session 11](../sessions/day4/session-11.md) checks.

## The rule

**No group calls the model until the instructor has read your `PLAN.md`.** Steps 1 and 2
(sampling and annotation) need no model, so there is plenty to get on with while you wait.

`PLAN.md` travels in your submission bundle as evidence the gate was passed. A final run
made before sign-off is not accepted as the final run.

## Predicting, not just planning

Question 6 asks what you think will happen. Write it down before you find out.

This is the cheap version of the habit the whole course is about: an LLM is a judge you have
to check, and checking means having an expectation to compare against. A prompt change that
helps for a reason you predicted is a finding. One that helps for no reason you can name is
a lucky guess — and you will struggle to defend it in the Q&A.

Being wrong here costs nothing. Reporting round 2 with "we added examples and it went up" —
when you cannot say why — costs marks under
[error analysis](rubric.md).
