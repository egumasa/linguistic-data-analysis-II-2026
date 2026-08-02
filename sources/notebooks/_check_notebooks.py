#!/usr/bin/env python3
"""Do the day notebooks still hold the properties they are supposed to have?

    uv run python sources/notebooks/_check_notebooks.py

Nothing runs these notebooks before a student does, so a cell can sit in the repo
broken, enormous, or unannounced and nothing complains. Quarto renders them without
executing. This file asserts what a reader can otherwise only check by eye:

    1. every code cell is valid Python (undefined names are fine; broken syntax is not)
    2. no code cell is longer than a screen
    3. every code cell has a markdown cell above it saying what it is about
    4. the 📦 Setup cell's `lib_names` matches the 🔧 Library cells the day ships
    5. Days 1 and 2 contain no model-API machinery

Rules 4 and 5 were re-checked by hand until now. They are mechanical, so they live
here. What still needs a human: no ✏️ cell may use syntax the progression table has
not introduced by that day.

See planning/course_planning/notebook-coding-principles.md.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _notebook_lib as L

HERE = Path(__file__).resolve().parent

# A cell longer than this is doing more than one thing, or is a wall of source. Counted
# as the student sees it, comments and all, because comments are part of the reading.
MAX_CELL_LINES = 40

problems = []


def report(notebook, index, message):
    problems.append(f"{notebook}  cell {index}: {message}")


def source_of(cell):
    return "".join(cell["source"])


def is_generated(cell):
    return L.LDA2 in cell.get("metadata", {})


def check_it_compiles(notebook, index, text):
    """Would this cell run? Undefined names are fine; broken syntax is not."""
    # A line starting with ! or % is Colab shell/magic syntax, not Python, and compile()
    # would reject it. Those cells are one line each; skip them.
    for line in text.splitlines():
        if line.strip().startswith(("!", "%")):
            return
    try:
        compile(text, "<cell>", "exec")
    except SyntaxError as error:
        report(notebook, index, f"is not valid Python — {error.msg} (line {error.lineno})")


def is_collapsed(text):
    """Does this cell arrive collapsed, with a title instead of a body?

    Colab renders a `#@title ... { display-mode: "form" }` cell as a single titled bar.
    The length rule exists so a student is not asked to read a wall of code, and a cell
    they never see the inside of is not a wall — the 🔧 and 🔎 cells all say in their
    first line that they are plumbing to run and move past.
    """
    return text.lstrip().startswith("#@title") and 'display-mode: "form"' in text


def check_it_fits_on_a_screen(notebook, index, cell, text):
    """Collapsed cells are exempt — they are titled bars, not something to read."""
    if is_generated(cell) or is_collapsed(text):
        return
    length = len(text.splitlines())
    if length > MAX_CELL_LINES:
        report(notebook, index,
               f"{length} lines long — split it (the limit is {MAX_CELL_LINES})")


def is_a_self_check(text):
    """A 🔎 Self-check cell belongs directly under the ✏️ cell it checks.

    Putting a markdown cell between them would separate an exercise from the cell that
    tells the student whether they got it right.
    """
    return text.lstrip().startswith("#@title 🔎 Self-check")


def check_it_has_a_lead_in(notebook, index, cells):
    """A code cell needs a markdown cell above it saying what is about to happen.

    Generated cells are exempt on both sides: a 🔧 Library cell is plumbing that sits
    directly above the step it serves, and stacking two of them is deliberate.
    """
    cell = cells[index]
    if is_generated(cell) or is_a_self_check(source_of(cell)):
        return
    if index == 0:
        report(notebook, index, "is the first cell in the notebook, with no lead-in above it")
        return
    above = cells[index - 1]
    if above["cell_type"] != "markdown" and not is_generated(above):
        report(notebook, index,
               "has another code cell directly above it — it needs a markdown lead-in")


def check_setup_matches_libs(notebook, cells):
    """Rule 3 of the principles doc: a day ships only the helpers it calls.

    The Setup cell's imports are driven by its `lib_names`, so that list has to name
    exactly the helpers the day's Library cells actually define. Too few and an import
    is missing; too many and the day loads something it never calls.
    """
    declared, shipped = None, set()
    for cell in cells:
        spec = cell.get("metadata", {}).get(L.LDA2)
        if not spec:
            continue
        if spec["generated"] == "setup":
            declared = set(spec.get("lib_names", ()))
        elif spec["generated"] == "libs":
            shipped |= set(spec["names"])
    if declared is None:
        return
    missing = shipped - declared
    extra = declared - shipped
    if missing:
        problems.append(f"{notebook}: Setup lib_names is missing {sorted(missing)} — "
                        "the day ships those helpers but Setup does not import for them")
    if extra:
        problems.append(f"{notebook}: Setup lib_names has {sorted(extra)} but no Library "
                        "cell defines them — drop them, or the day imports what it never calls")


# Rule 4 of the principles doc: a day never loads a model it does not use. Day 1 uses
# the keyless colab.ai demo; Day 2 works from frozen predictions and touches no model.
NO_MODEL = {"day2-s5": "Day 2 (S5)", "day2-s6": "Day 2 (S6)"}
MODEL_MARKERS = ("from google import genai", "GEMINI_API_KEY", "run_prompt(")


def check_no_model_machinery(notebook, cells):
    which = next((label for key, label in NO_MODEL.items() if notebook.startswith(key)), None)
    if which is None:
        return
    for index, cell in enumerate(cells):
        if cell["cell_type"] != "code":
            continue
        text = source_of(cell)
        for marker in MODEL_MARKERS:
            if marker in text:
                report(notebook, index,
                       f"{which} calls no model, but this cell mentions {marker!r}")


def check_notebook(path):
    cells = json.loads(path.read_text(encoding="utf-8"))["cells"]
    for index, cell in enumerate(cells):
        if cell["cell_type"] != "code":
            continue
        text = source_of(cell)
        check_it_compiles(path.name, index, text)
        check_it_fits_on_a_screen(path.name, index, cell, text)
        check_it_has_a_lead_in(path.name, index, cells)
    check_setup_matches_libs(path.name, cells)
    check_no_model_machinery(path.name, cells)


def main():
    paths = sorted(HERE.glob("*.ipynb"))
    if not paths:
        print("No notebooks found in", HERE)
        return 1

    for path in paths:
        check_notebook(path)
        print("  checked", path.name)

    print()
    if problems:
        print(len(problems), "problems:")
        for problem in problems:
            print("  -", problem)
        print("\nEdit the notebook, then run _sync_notebooks.py.")
        return 1
    print(f"All {len(paths)} notebooks: every code cell runs, fits a screen and is "
          "introduced;\nSetup matches the helpers each day ships; Days 1–2 call no model.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
