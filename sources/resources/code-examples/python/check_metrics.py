"""check_metrics.py — did I get the formulas right?

Run this after you fill in metrics_exercise.py. It builds a small labeled example,
runs YOUR functions, runs scikit-learn's trusted versions on the same data, and prints
a ✅ (match) or ❌ (mismatch) for each metric. When every line is ✅, your formulas are
correct.

    python check_metrics.py                 # checks metrics_exercise.py (your work)
    python check_metrics.py metrics_solution # checks the reference solution

In Colab, run the cell that downloads metrics_exercise.py + check_metrics.py first, then:
    !python check_metrics.py
"""
import importlib
import sys

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    cohen_kappa_score,
)

# Which module to test: the student exercise by default, or one named on the command line.
module_name = sys.argv[1] if len(sys.argv) > 1 else "metrics_exercise"
m = importlib.import_module(module_name)

# ----------------------------------------------------------------------------------
# A small fixture with imbalance and a couple of mistakes — enough to catch bugs.
# ----------------------------------------------------------------------------------
LABELS = ["A1", "A2", "B1", "B2"]
gold = ["A1", "A1", "A2", "A2", "B1", "B1", "B1", "B2", "B2", "B2"]
pred = ["A1", "A2", "A2", "A2", "B1", "B1", "B2", "B2", "B2", "A2"]

# Two annotators for the agreement metrics (percent agreement + kappa).
annot_a = ["A1", "A2", "B1", "B1", "B2", "A1", "A2", "B2", "B1", "A1"]
annot_b = ["A1", "A2", "B1", "B2", "B2", "A2", "A2", "B2", "B1", "A1"]

TOL = 1e-9
results = []


def check(name, got, expected):
    ok = abs(got - expected) < TOL
    results.append(ok)
    mark = "✅" if ok else "❌"
    print(f"{mark} {name:<28} yours={got:.6f}   sklearn={expected:.6f}")


print(f"Checking module: {module_name}\n" + "-" * 60)

# Per-label precision / recall / F1 against sklearn (which uses zero_division=0).
for label in LABELS:
    check(f"precision('{label}')", m.precision(gold, pred, label),
          precision_score(gold, pred, labels=[label], average="micro", zero_division=0))
    check(f"recall('{label}')", m.recall(gold, pred, label),
          recall_score(gold, pred, labels=[label], average="micro", zero_division=0))
    check(f"f1('{label}')", m.f1(gold, pred, label),
          f1_score(gold, pred, labels=[label], average="micro", zero_division=0))

# Macro-F1 over all labels.
check("macro_f1", m.macro_f1(gold, pred, LABELS),
      f1_score(gold, pred, labels=LABELS, average="macro", zero_division=0))

# Agreement metrics.
expected_pa = sum(1 for x, y in zip(annot_a, annot_b) if x == y) / len(annot_a)
check("percent_agreement", m.percent_agreement(annot_a, annot_b), expected_pa)
check("cohen_kappa", m.cohen_kappa(annot_a, annot_b),
      cohen_kappa_score(annot_a, annot_b))

print("-" * 60)
if all(results):
    print(f"All {len(results)} checks passed ✅  — your metrics match scikit-learn.")
else:
    n_fail = results.count(False)
    print(f"{n_fail} of {len(results)} checks FAILED ❌  — fix those functions and re-run.")
    sys.exit(1)
