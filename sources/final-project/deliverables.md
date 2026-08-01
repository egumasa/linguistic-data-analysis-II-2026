---
title: "Deliverables & submission"
subtitle: "What to hand in, and how"
toc: true
---

Three deliverables, all produced in class:

- **Presentation + Q&A** — the main one.
- **One-page report** — five sections. `export_results` writes the scaffold; you write the
  parts that need judgment.
- **Completed notebook**, run top to bottom.

## The bundle

One command collects everything:

```bash
python scripts/make_submission.py --group groupA
```

It builds `../lda2_project_<group>/` next to your cloned repo, keeping the folder structure
intact:

```
lda2_project_groupA/
├── PLAN.md                                  ← signed before the first model call
├── notebooks/
│   ├── 01_build_pool_raamove.ipynb          ← run in order, outputs visible
│   ├── 02_sample.ipynb
│   ├── 03_annotate.ipynb
│   ├── 04_develop.ipynb
│   ├── 05_test.ipynb
│   └── 06_report.ipynb
├── prompts/
│   ├── raamove_v0.txt  raamove_v1.txt       ← the round-by-round trail (04)
│   └── raamove.txt                          ← the one you tested
├── data/gold/
│   └── raamove_groupA_gold.json             ← your adjudicated gold (03)
├── outputs/
│   ├── raamove_groupA_predictions.json      ← the FROZEN held-out run (05)
│   ├── raamove_groupA_test_log.jsonl        ← every held-out scoring, fingerprinted
│   ├── raamove_groupA_predictions.csv
│   └── raamove_groupA_report.md
├── scripts/                                 ← the plumbing, unmodified
└── slides.pdf                               ← your 5 slides
```

### Why the folders are kept

Two reasons, and neither is tidiness.

That `scripts/ · prompts/ · data/ · outputs/` split **is** the reproducibility checklist from
[Session 10](../sessions/day4/session-10.md), made physical — code, prompts, data and outputs,
each separately pointable-at. And practically: the notebook reads `../scripts` and
`../data/…`, so a flattened folder no longer runs.

### What it deliberately leaves out

`.git/`, `.venv/`, **your `.env`** (it holds your API key), the full pools in `data/pools/`,
and anything ICNALE-derived — the last because ICNALE's licence does not permit
redistribution. The script excludes all of it by name, which is why you should use the script
rather than dragging files by hand.

It also **tells you what is missing** — no frozen predictions, no `PLAN.md`, or a report still
carrying the scaffold's italic placeholder text.

## Handing it in

1. Run `make_submission.py`.
2. Find `lda2_project_<group>/` in Drive → right-click → **Download** (Drive zips it).
3. Google Classroom → *Final mini-project* → **Add or create → File** → upload → **Turn in**.

**One submission per group**, with every member's name in `PLAN.md`.

::: {.callout-warning}
## Check it runs on a fresh runtime first
Before you submit, restart the runtime and **Run all**. If your notebook only works in the
session where you built it up cell by cell, it does not reproduce — and reproducing is the
claim you are making.

The bundle is self-contained for the claim that matters: given your gold set and your frozen
predictions, anyone can recompute your reported numbers with no API key and no network.
:::

## The one-page report

`export_results` fills in what it can compute — your label set, per-label counts, the
F1-per-round table. Everything in *italics* is a placeholder for you.

1. **Scheme & gold** — your labels; how you built the gold set (size, balance); your percent
   agreement and κ; and **what your adjudication changed**.
2. **Prompt iterations** — the table of F1 per round, and for each round *what you changed and
   why you expected it to help*.
3. **Evaluation** — per-class precision/recall/F1, the confusion matrix, and which class did
   worst.
4. **Error analysis** — at least three concrete misses, each attributed: the **model's** fault
   or the **scheme's**, with a reason.
5. **Limitations** — at least two that apply to *your* run, not the generic three the scaffold
   ships with.

A section left as the scaffold's own prose scores zero for that section. See the
[rubric](rubric.md).

## The presentation

**8 minutes + 4 minutes of Q&A.** Five slides, one per report section. **Every member speaks**
— one slide each; a three-person group doubles up.

Have your `show_errors` table on screen and ready before you start, because every group gets
these two questions:

1. **"Show us an item the model got wrong, and tell us whose fault it was — the model's or
   your scheme's."**
2. **"What did your QC pass change?"**

Neither is a trick. They are the two things that show you did the work rather than ran the
cells.
