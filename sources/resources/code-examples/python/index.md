---
title: "Coding the metrics from scratch"
subtitle: "Implement precision, recall, F1, and Cohen's κ by hand — then check them against scikit-learn"
toc: true
---

In the [Day-2 notebook](../../tutorials/day2_gold_standards_and_evaluation.ipynb) and the
[Corpus Lab](../../corpus-lab/index.md) you called `evaluate()` on a set of *frozen* predictions
and read the numbers it printed. Here you write those numbers yourself. Once you have coded precision, recall, F1,
and Cohen's κ from the raw label lists, the scores scikit-learn reports in the final
project will never be a black box — you will know exactly what each one means and when it
can mislead you.

> In the **final mini-project** you go back to using scikit-learn's implementations
> ([`lda2-final-template`](../../datasets/mini-project-tracks.md)). The point of *this*
> exercise is to understand them first.

## The files

| File | What it is |
|---|---|
| [`metrics_exercise.py`](metrics_exercise.py) | The file you edit. Each function has a docstring with the formula and a `raise NotImplementedError(...)` line for you to replace. |
| [`check_metrics.py`](check_metrics.py) | Your answer key. It runs your functions and scikit-learn on the same small dataset and prints ✅ / ❌ for each metric. |

You implement six things, all from plain lists of labels — no imports, no numpy:

- `confusion_counts(gold, pred, label)` → the `tp / fp / fn / tn` every metric is built from
- `precision`, `recall`, `f1` for one label
- `macro_f1` across all labels
- `percent_agreement` and `cohen_kappa` for two annotators

## Run it in Google Colab

```python
# Download the two files into the Colab runtime.
BASE = "https://raw.githubusercontent.com/egumasa/linguistic-data-analysis-II-2026/main/sources/resources/code-examples/python"
!wget -q $BASE/metrics_exercise.py -O metrics_exercise.py
!wget -q $BASE/check_metrics.py    -O check_metrics.py

# Open metrics_exercise.py in Colab's file browser (left sidebar), fill in each function,
# save (Ctrl/Cmd-S), then run the checker:
!python check_metrics.py
```

Every line will say ❌ until you implement that function. Fix them until you see:

```
All 15 checks passed ✅  — your metrics match scikit-learn.
```

## Run it locally

```bash
cd sources/resources/code-examples/python
# edit metrics_exercise.py, then:
uv run --group dev python check_metrics.py
```

## Why the checker uses scikit-learn

`check_metrics.py` is allowed to import `sklearn` — it is your *grader*, not your solution.
Comparing against a trusted library is exactly how you gain confidence that a formula you
wrote by hand is correct. That is the same reason the final project trusts scikit-learn
outright: you have already earned the right to.
