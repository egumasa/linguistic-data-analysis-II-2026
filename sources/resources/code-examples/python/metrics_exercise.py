"""metrics_exercise.py — code the evaluation metrics by hand.

In the tutorial and the Corpus Lab we do NOT use a library for the metrics. You
implement precision, recall, F1, and Cohen's kappa yourself, from the raw lists of
labels. This is the whole point of the exercise: once you have written these formulas,
the numbers scikit-learn prints later will never be a black box.

Every function below has a full docstring and a worked comment, then a line that says

    raise NotImplementedError(...)

Replace that line with your own code so the function returns the right value. When you
think you are done, run `check_metrics.py` — it compares each of your functions against
scikit-learn on a small example and prints a ✅ or ❌ for each one.

Vocabulary (all functions take plain Python lists):
    gold  — the list of TRUE labels,      e.g. ["A1", "B2", "B2", "C1"]
    pred  — the list of PREDICTED labels,  e.g. ["A1", "B2", "C1", "C1"]
    gold[i] is the truth for the same item that pred[i] is a prediction for.
    label — one single class you are scoring, e.g. "B2"
    labels — the full list of classes, e.g. ["A1", "A2", "B1", "B2", "C1", "C2"]

No imports needed. No numpy, no sklearn — just loops and arithmetic.
"""


def confusion_counts(gold, pred, label):
    """Return the four counts that every metric is built from, for ONE label.

    Thinking of `label` as the "positive" class, classify each item as one of:
        tp — true positive : gold IS label AND pred IS label
        fp — false positive: gold is NOT label BUT pred IS label
        fn — false negative: gold IS label BUT pred is NOT label
        tn — true negative : gold is NOT label AND pred is NOT label

    Return them as a dict: {"tp": ..., "fp": ..., "fn": ..., "tn": ...}

    Worked example, label="B2", gold=["A1","B2","B2"], pred=["A1","B2","C1"]:
        item 0: gold A1, pred A1 -> neither is B2                 -> tn
        item 1: gold B2, pred B2 -> both are B2                   -> tp
        item 2: gold B2, pred C1 -> gold is B2, pred is not       -> fn
        result: {"tp": 1, "fp": 0, "fn": 1, "tn": 1}
    """
    # HINT: start tp=fp=fn=tn=0, loop with `for g, p in zip(gold, pred):`,
    # and add 1 to the right counter with if/elif on whether g == label / p == label.
    raise NotImplementedError("Count tp, fp, fn, tn for `label` and return them in a dict.")


def precision(gold, pred, label):
    """Precision for one label = tp / (tp + fp).

    "Of all the items the model CALLED `label`, what fraction really were `label`?"
    If the model never predicted `label` at all (tp + fp == 0), return 0.0 so you
    never divide by zero.
    """
    # HINT: call confusion_counts(gold, pred, label) and use its tp and fp.
    raise NotImplementedError("Return tp / (tp + fp), or 0.0 if tp + fp == 0.")


def recall(gold, pred, label):
    """Recall for one label = tp / (tp + fn).

    "Of all the items that TRULY were `label`, what fraction did the model find?"
    If there are no true `label` items (tp + fn == 0), return 0.0.
    """
    # HINT: call confusion_counts(gold, pred, label) and use its tp and fn.
    raise NotImplementedError("Return tp / (tp + fn), or 0.0 if tp + fn == 0.")


def f1(gold, pred, label):
    """F1 for one label = the harmonic mean of precision and recall.

        F1 = 2 * precision * recall / (precision + recall)

    F1 is high only when BOTH precision and recall are high. If precision + recall
    is 0, return 0.0.
    """
    # HINT: reuse precision(...) and recall(...) above.
    raise NotImplementedError("Return the harmonic mean of precision and recall (or 0.0).")


def macro_f1(gold, pred, labels):
    """Macro-averaged F1 = the plain average of the per-label F1 scores.

    "Macro" means every class counts equally, no matter how many items it has — so a
    rare class matters as much as a common one. Compute f1(gold, pred, label) for each
    label in `labels` and return their mean.
    """
    # HINT: build a list of f1(...) values, then divide their sum by len(labels).
    raise NotImplementedError("Average f1(gold, pred, label) over every label in `labels`.")


def percent_agreement(a, b):
    """Simple agreement between two annotators = fraction of items they labeled the same.

    a and b are two equal-length lists of labels for the SAME items (e.g. two people
    who each annotated the gold set). Return (number of positions where a[i] == b[i])
    divided by the total number of items, as a float between 0 and 1.
    """
    # HINT: count matches with `for x, y in zip(a, b): if x == y: ...`
    raise NotImplementedError("Return the fraction of positions where a[i] == b[i].")


def cohen_kappa(a, b):
    """Cohen's kappa — agreement CORRECTED for chance.

    Percent agreement looks high even when two annotators are just guessing, because
    they will match sometimes by luck. Kappa subtracts out that luck:

        kappa = (p_o - p_e) / (1 - p_e)

    where
        p_o = observed agreement = percent_agreement(a, b)   (you already wrote this)
        p_e = agreement EXPECTED BY CHANCE.

    To get p_e, for each label that appears in either list:
        prop_a = (how often annotator a used that label) / N
        prop_b = (how often annotator b used that label) / N
        the chance they BOTH pick that label at random is prop_a * prop_b
    p_e is the sum of prop_a * prop_b over all labels.

    N is the number of items. If (1 - p_e) is 0, return 0.0.

    Worked intuition: if both annotators use every label equally often and agree 90%
    of the time, p_e is small, so kappa is close to p_o. If one label dominates, p_e
    is large, and the same 90% agreement yields a much lower kappa.
    """
    # HINT: build the set of all labels with set(a) | set(b); count with a.count(label);
    # let N = len(a). Compute p_o from percent_agreement(a, b) and p_e from the sum above.
    raise NotImplementedError("Return (p_o - p_e) / (1 - p_e), or 0.0 if 1 - p_e == 0.")
