---
title: "The PLAN.md gate"
subtitle: "作戦シート — written before you call the model"
toc: true
---

Before your group runs the model even once, you fill in `PLAN.md` and have it signed off. It is **not graded**. It is a gate.

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

`PLAN.md` is already in the template you cloned, at the repo root, with every question laid
out and a note under each explaining what turns on it. **You fill it in there** — it travels
in your submission bundle as evidence the gate was passed.

Nine questions, in two groups.

**What you are annotating** — settled by the end of Session 11.

1. **Unit of analysis** — sentence or whole text, and why.
2. **Label set** — exactly the strings that appear in your gold file.
3. **Are the labels ordered?** If yes, in what order. This decides `labels_order` in
   `config.yaml`, and it is the one question that exists purely to catch a silent bug: labels
   that are ordered but not alphabetical (`Low`/`Mid`/`High`) otherwise get a weighted κ
   computed over `High < Low < Mid`, reported to three decimal places, and wrong.
4. **The decisions you made building the pool** — the ✏️ cells notebook 01 left blank, what
   you put in them, and what it cost you.
5. **Sampling** — which strategy, the one-sentence defence, `N_PER_CLASS`, `SEED`.
6. **The dev / test split** — the ratio, and why that one.

**What you will report** — the questions this page exists for.

7. **QC** — who codes which column, who adjudicates, **which agreement statistics you will
   report**, and **what counts as a disagreement**.
8. **Prompt plan** — your baseline, the moves you will try and in what order, how many
   prompts you will test on the held-out set, and how you pick the winner.
9. **The one number you lead with** — macro, micro or weighted F1, or a κ.

## Why questions 7–9 are on this page and not in a notebook

Every one of them determines a number you will report, and every one of them has an answer
you could reach for *after* seeing which option flatters you.

Nothing stops you running all three F1 averages and reporting the highest. Nobody reading
your report could tell. The only thing that makes the number mean anything is that the choice
was made from facts you already had — how many coders, whether the labels are a scale, what
your research question is about — before any of the numbers existed.

So the rule is not about how much you look at. **Looking is fine when it changes what you do
next; it is not fine when it changes what you claim.** Reading the coder confusion matrix to
decide which label boundary to argue about is exactly what it is for. Choosing the statistic
after seeing what each one gives you is not.

Questions 7–9 are the ones where that distinction bites, so they are settled here, at a point
where the numbers do not exist yet.

## The pipeline, as an I/O chain

`PLAN.md` ends with a table of the six notebooks — what each one consumes and what it
produces — with a blank column for the file names your group actually used.

That table is the point of the exercise. If your group can say aloud *"03 consumes the
filled-in sheet and our adjudication, and produces the gold set"*, you understand the
pipeline — and that is what the end of [Session 11](../sessions/day4/session-11.md) checks.

Note where the model appears: **not until 04**. Notebooks 01–03 are the study; the LLM is the
thing being measured by it.

## The rule

**No group calls the model until the instructor has read your `PLAN.md`.** Notebooks 01–03
need no model at all, so there is plenty to get on with while you wait.

`PLAN.md` travels in your submission bundle as evidence the gate was passed. A final run made
before sign-off is not accepted as the final run.

## Predicting, not just planning

Question 8 asks what you think will happen. Write it down before you find out.

This is the cheap version of the habit the whole course is about: an LLM is a judge you have
to check, and checking means having an expectation to compare against. A prompt change that
helps for a reason you predicted is a finding. One that helps for no reason you can name is
a lucky guess — and you will struggle to defend it in the Q&A.

Being wrong here costs nothing. Reporting round 2 with "we added examples and it went up" —
when you cannot say why — costs marks under
[error analysis](rubric.md).
