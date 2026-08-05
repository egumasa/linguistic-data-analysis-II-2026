#!/usr/bin/env python3
"""Build day3_prompt_design_answers.ipynb from day3_prompt_design.ipynb.

    python sources/notebooks/_build_answers.py

The answers notebook is the same notebook with every fill-in completed: the five
`evaluate` lines written out, and each fill-in string carrying one worked example.
It is DERIVED — never edit it directly. Edit day3_prompt_design.ipynb, then re-run
this script; the two files cannot drift because every difference between them is a
row in REPLACEMENTS below.

Each row is (mode, marker, text):
  * mode "replace" — the cell whose source contains `marker` gets `text` as its
    whole new source;
  * mode "append"  — `text` is added to the end of that cell's source.
A marker must match exactly one cell, or this script stops with an error.

To turn another pre-filled cell into a student fill-in later: blank it in
day3_prompt_design.ipynb, then add one "replace" row here carrying the completed
version. (Example row, currently unused:
    ("replace", "calls_per_round   = None", COMPLETED_RUNTIME_CELL),
)
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "day3_prompt_design.ipynb"
TARGET = HERE / "day3_prompt_design_answers.ipynb"

TITLE_NOTE = """

***
**This file is the completed version** of `day3_prompt_design.ipynb`: the five
`evaluate` lines are filled in, and every fill-in string carries one worked example.
Work through the fill-in notebook first; open this one to check your work — your
prompts, predictions and numbers do not have to match these."""

EVALUATE_DONE = '''# the five numbered lines are filled in — this is the completed version.
def evaluate(gold: list[dict[str, str]],
             predictions: list[str],
             ordered: bool = False) -> float:
    """Score predictions against gold: print the full report, return macro-F1.

    ordered=True adds quadratic weighted kappa, for labels that sit on a scale.

    Example:
        >>> f1_by_round["1 zero-shot"] = evaluate(valid, predictions, ordered=True)
    """
    ### Step 1: line the two label lists up, gold first ###
    y_true = []                          # the correct labels, from the gold set
    for item in gold:
        y_true.append(item["label"])
    y_pred = predictions                 # the model's labels, in the same order

    ### Step 2: per-class precision / recall / F1, as a text table ###
    print(classification_report(y_true, y_pred, labels=LEVELS, zero_division=0))  # (1)
    ### Step 3: one overall number — agreement corrected for chance ###
    kappa = cohen_kappa_score(y_true, y_pred)                                     # (2)
    print(f"Cohen's kappa            {kappa:.3f}")
    if ordered:                          # only when the labels sit on a scale
        weighted = cohen_kappa_score(y_true, y_pred, labels=LEVELS,
                                     weights="quadratic")                         # (3)
        print(f"Cohen's kappa (weighted) {weighted:.3f}   <- labels are ordered")
    ### Step 4: draw the same information as a picture ###
    cm = confusion_matrix(y_true, y_pred, labels=LEVELS)                          # (4)
    plt.figure(figsize=(5.5, 4.5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=LEVELS, yticklabels=LEVELS)
    plt.xlabel("Predicted"); plt.ylabel("Gold"); plt.title("Confusion matrix")
    plt.tight_layout(); plt.show()

    ### Step 5: one number to keep — handed back to whoever called ###
    macro_f1 = f1_score(y_true, y_pred, labels=LEVELS, average="macro",
                        zero_division=0)                                          # (5)
    print(f"F1 (macro)               {macro_f1:.3f}")
    return macro_f1'''

DECLARE_DONE = '''# a worked example of the declare cell — one possible round 4.
PROMPT_ID   = "4 describe C1 explicitly"
WORST_CLASS = "C1"
MY_CHANGE   = "add one line describing what makes a sentence C1"
I_PREDICT   = "C1 recall goes up, because the prompt now says what to look for; B2 and C2 may lose a little to it"

print(f"Round {PROMPT_ID} — targeting {WORST_CLASS}. Change: {MY_CHANGE}.")
print(f"Prediction: {I_PREDICT}")'''

PROMPT_MINE_DONE = '''# the worked round-4 prompt: the zero-shot prompt plus the ONE declared change.
PROMPT_MINE = """You are an expert rater of English sentence difficulty using the CEFR scale.
Classify the sentence into exactly one of: A1, A2, B1, B2, C1, C2.
C1 sentences use precise, lower-frequency vocabulary and complex noun phrases,
but still read as ordinary prose rather than technical writing.
Reply as JSON, like: {{"label": "B1"}}

Sentence: {text}"""

print(PROMPT_MINE.format(text="(each sentence lands here)"))'''

ROUND5_DONE = '''# the ready-made round, with the prediction written out as an example.
PROMPT_ID = "5 tie-break rule"
I_PREDICT = "fewer far misses upward: when the model hesitates between two adjacent levels it now takes the lower one, so weighted kappa should improve even if macro-F1 barely moves"

PROMPT_R5 = PROMPT_MINE + """
If you are unsure between two adjacent levels, choose the lower one."""

print(f"Round {PROMPT_ID}. Prediction: {I_PREDICT}")'''

REPORT_DONE = """### Your report — a completed example

The numbers below are from one example run; yours will differ. What should match is the *shape*: every claim names a set, a number, and a reason.

- The best prompt on `valid` was round `3` (`chain-of-thought`), with macro-F1 = `0.42`.
- The change that helped most was asking for reasoning before the label; we expected it to help because the errors after round 2 were concentrated in adjacent-level confusions, where a direct answer has nothing to weigh.
- On the held-out `test` set the same prompt scored macro-F1 = `0.36`.
- The gap between the two scores is `0.06`, which we read as the cost of tuning: the prompt was chosen because it suited the 24 validation items, and new sentences pay that back."""

REPLACEMENTS = [
    ("append", "# Day 3 · Prompt design & iteration", TITLE_NOTE),
    ("replace", "# ✏️ we fill the five numbered lines together in class", EVALUATE_DONE),
    ("replace", 'PROMPT_ID   = "4 …"', DECLARE_DONE),
    ("replace", "# ✏️ everything between the triple quotes is yours", PROMPT_MINE_DONE),
    ("replace", 'PROMPT_ID = "5 tie-break rule"', ROUND5_DONE),
    ("replace", "### Your report   ✏️ YOU EDIT", REPORT_DONE),
]


def as_source(text):
    lines = text.split("\n")
    return [l + "\n" for l in lines[:-1]] + [lines[-1]]


def main():
    nb = json.loads(SOURCE.read_text(encoding="utf-8"))
    for mode, marker, text in REPLACEMENTS:
        hits = [c for c in nb["cells"] if marker in "".join(c["source"])]
        if len(hits) != 1:
            print(f"ERROR: marker {marker!r} matches {len(hits)} cells (need exactly 1)")
            return 1
        cell = hits[0]
        new = ("".join(cell["source"]) + text) if mode == "append" else text
        cell["source"] = as_source(new)

    out = json.dumps(nb, indent=1, ensure_ascii=False) + "\n"
    if TARGET.exists() and TARGET.read_text(encoding="utf-8") == out:
        print(f"{TARGET.name} already up to date.")
        return 0
    TARGET.write_text(out, encoding="utf-8")
    print(f"Wrote {TARGET.name} ({len(nb['cells'])} cells, "
          f"{len(REPLACEMENTS)} cells completed).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
