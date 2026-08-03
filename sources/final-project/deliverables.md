---
title: "Deliverables & submission"
subtitle: "What to hand in, and how"
toc: true
---
Three deliverables, all produced in class:

- **Presentation + Q&A** — the main one. One per group.
- **Two-page report** — six sections, written and handed in **individually**.
- **Completed notebook**, run top to bottom. One per group.

The report is the one thing you do not share. Your group runs one study together, and
then each member writes their own account of it. Two people who ran the same pipeline
should still hand in two different reports, because section 5 asks what *you* make of
the errors and section 6 asks which limitations *you* think matter.

## Submit with zipped folder

- You work on the repository. Once you are done, you will submit a zip file that contains all the information.
- You will also share the actual google drive folder with me.

The zip is the group's work — the plan, the notebooks, the gold set, the predictions and
the slides. **Your report is not in it.** You upload that separately, as your own file.



### Why the folders are kept

Two reasons, and neither is tidiness.

That `scripts/ · prompts/ · data/ · outputs/` split **is** the reproducibility checklist from [Session 10](../sessions/day4/session-10.md), made physical — code, prompts, data and outputs,
each separately pointable-at. And practically: the notebook reads `../scripts` and
`../data/…`, so a flattened folder no longer runs.

### What it deliberately leaves out

`.git/`, `.venv/`, **your `.env`** (it holds your API key), the full pools in `data/pools/`,
and anything ICNALE-derived — the last because ICNALE's licence does not permit
redistribution. The script excludes all of it by name, which is why you should use the script
rather than dragging files by hand.

It also **tells you what is missing** — no frozen predictions, no `PLAN.md`, no per-item
predictions CSV.

## Handing it in

**The group's bundle**, once per group:

1. Run `make_submission.py`.
2. Find `lda2_project_<group>/` in Drive → right-click → **Download** (Drive zips it).
3. Google Classroom → *Final mini-project* → **Add or create → File** → upload → **Turn in**.

Every member's name goes in `PLAN.md`.

**Your report**, once per person: upload your own file to the same assignment, named
`report_<yourname>.pdf`. PDF, so the formatting is the formatting I see.

::: {.callout-warning}

## Check it runs on a fresh runtime first

Before you submit, restart the runtime and **Run all**. If your notebook only works in the
session where you built it up cell by cell, it does not reproduce — and reproducing is the
claim you are making.

The bundle is self-contained for the claim that matters: given your gold set and your frozen
predictions, anyone can recompute your reported numbers with no API key and no network.
:::

## The two-page report

**Written individually.** Six sections, about 900–1050 words of prose, plus your table
and confusion matrix.

1. **Brief intro** (150 words) — brief description of the topic and why it is important.
2. **Methodology** (300 words)
   1. **Data sampling strategy** — what corpus, what sources, how many examples.
   2. **Scheme & gold** — your labels; how you built the gold set (size, balance); your
      percent agreement and κ; and **what your adjudication changed**.
   3. **(Train) / Dev / Test split** — which split you chose and why.
3. **Prompt iterations** (100–200 words) — the table of F1 per round, and for each round
   *what you changed and why you expected it to help*.
4. **Evaluation** (200 words) — per-class precision/recall/F1, the confusion matrix, and
   which class did worst.
5. **Error analysis** (100 words) — at least three concrete misses, each attributed: the
   **model's** fault or the **scheme's**, with a reason.
6. **Limitations** (50–100 words) — at least two that apply to *your* run, not the three
   generic ones everyone can write without having run anything.

### Length and format

Two pages, A4 or US Letter, 11–12pt, single-spaced, 1-inch margins. At that setting a page
holds roughly 500–550 words of prose, so the word budgets above fill about one and a half
pages and the table and confusion matrix take the rest.

The budgets are targets, not limits. If you are well over two pages, the section to cut is
usually the intro — not the error analysis, which is what the Q&A goes to.

Hand it in as **PDF**. Write it in Word, or anything else you like; nothing in the
notebooks drafts it for you. Every number you need is printed on screen in `06_report.ipynb`.

See the [rubric](rubric.md).

## The presentation

**8 minutes + 4 minutes of Q&A.** Five slides: methodology, prompt iterations, evaluation,
error analysis, limitations. The report's intro section is a sentence of framing at the
start, not a slide of its own. **Every member speaks** — one slide each; a three-person
group doubles up.

The presentation is the group's shared account of the study. The report is your own.

Have your `show_errors` table on screen and ready before you start, because every group gets
these two questions:

1. **"Show us an item the model got wrong, and tell us whose fault it was — the model's or
   your scheme's."**
2. **"What did your QC pass change?"**

Neither is a trick. They are the two things that show you did the work rather than ran the
cells.
