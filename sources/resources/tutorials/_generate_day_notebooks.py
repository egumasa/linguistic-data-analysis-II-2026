#!/usr/bin/env python3
"""Generate the five combined day notebooks (tutorial + Corpus Lab in one file).

Students submit ONE .ipynb per day; each contains that day's guided **tutorial**
(Part A) and its **Corpus Lab** (Part B). Notebooks run in Google Colab (free built-in
Gemini, no key) and fall back to a local LLM API off-Colab.

The shared LLM backend + pipeline "library cells" are lifted verbatim from the original
`02_gold_and_eval.ipynb`; only the task-specific bits (GOLD_URL / LEVELS) are
parameterized. Days whose tutorial or lab is not written yet ship honest TODO scaffolds.

Run:  python sources/resources/tutorials/_generate_day_notebooks.py
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent


# ------------------------------------------------------------------ cell helpers
def md(*lines):
    return {"cell_type": "markdown", "metadata": {}, "source": _src(lines)}


def code(*lines):
    return {"cell_type": "code", "metadata": {}, "execution_count": None,
            "outputs": [], "source": _src(lines)}


def _src(lines):
    text = "\n".join(lines)
    return [l + "\n" for l in text.split("\n")][:-1] + [text.split("\n")[-1]]


def save(name, cells):
    nb = {"cells": cells,
          "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python",
                                      "name": "python3"},
                       "language_info": {"name": "python"},
                       "colab": {"provenance": []}},
          "nbformat": 4, "nbformat_minor": 5}
    (OUT / name).write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")
    print("wrote", name)


REPO_RAW = ("https://raw.githubusercontent.com/egumasa/"
            "linguistic-data-analysis-II-2026/main/sources/resources/datasets/gold")
CEFR_GOLD_URL = f"{REPO_RAW}/cefr_sentences.json"
CEFR_POOL_URL = f"{REPO_RAW}/cefr_pool.json"
# Frozen CEFR predictions for the Day-2 metrics lesson (instructor generates this
# once from the fixed Day-2 prompt; committed so Day 2 is keyless & deterministic).
CEFR_PREDICTIONS_DAY2_URL = f"{REPO_RAW}/predictions_day2.json"


# ------------------------------------------------- shared cells (verbatim library)
# The LLM backend block. Two backends, chosen by whether a Gemini API key is set:
#   * DEMO (no key)  → Colab's built-in Gemini (colab.ai). Zero setup, but NON-
#     reproducible: colab.ai exposes no temperature/seed, so output varies run to run.
#   * REAL (key set) → the Gemini API with temperature=0 + seed, for reproducible,
#     autograded work (Corpus Lab from Day 3, and the final project).
# The key is PREFERRED when present — including inside Colab (via Colab Secrets).
# See resources/tools/gemini-api-key.md.
MODEL_ID = "gemini-2.5-flash"   # pinned; confirm against the API pre-flight (see prep-plan)

BACKEND = '''#@title 📦 Setup — run me first { display-mode: "form" }
# Imports + the LLM backend. No pip install needed in Colab.
import json, re, urllib.request, os
from sklearn.metrics import classification_report, confusion_matrix
import pandas as pd, seaborn as sns, matplotlib.pyplot as plt

MODEL_ID = "gemini-2.5-flash"   # pinned model for the reproducible (API) backend

def _resolve_gemini_key():
    """Find a Gemini API key: Colab Secrets first (not auto-exported to env), then env."""
    try:
        from google.colab import userdata      # only exists in Colab
        key = userdata.get("GEMINI_API_KEY")
        if key:
            return key
    except Exception:
        pass                                    # not in Colab, or secret not set
    return os.environ.get("GEMINI_API_KEY")

def _make_api_backend(key):
    """Reproducible backend: Gemini API with temperature=0 + a fixed seed."""
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=key)
    cfg = types.GenerateContentConfig(temperature=0, seed=42)
    return (lambda p: client.models.generate_content(
                model=MODEL_ID, contents=p, config=cfg).text,
            f"Gemini API ({MODEL_ID}, temperature=0, seed=42)")

# Prefer the API key when set (reproducible); else fall back to colab.ai (demo).
_key = _resolve_gemini_key()
if _key:
    generate_text, _backend = _make_api_backend(_key)
else:
    try:
        from google.colab import ai            # Colab's built-in Gemini — no key
        generate_text, _backend = (lambda p: ai.generate_text(p)), "Colab Gemini (demo, non-reproducible)"
    except ImportError:
        raise RuntimeError(
            "No LLM backend found. Run this notebook in Google Colab (free built-in "
            "Gemini, no key needed), or set GEMINI_API_KEY — in Colab via the Secrets "
            "panel, or as an environment variable when running locally. "
            "See resources/tools/gemini-api-key.md.")'''


def setup_cell(gold_url=None, gold_comment=None, predictions_url=None):
    """Build the setup cell. With a gold_url, also define GOLD_URL + LEVELS (CEFR).
    With a predictions_url, also define PREDICTIONS_URL (frozen Day-2 predictions)."""
    src = BACKEND
    if gold_url:
        src += (f'\n\n# {gold_comment}\n'
                f'GOLD_URL = "{gold_url}"\n'
                'LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]')
    if predictions_url:
        src += f'\nPREDICTIONS_URL = "{predictions_url}"   # frozen model predictions'
    src += '\nprint(f"Setup done. LLM backend: {_backend}. scikit-learn ready.")'
    return code(src)


LIB_LOAD_GOLD = code(
    '#@title 🔧 Library cell: load_gold(url_or_path) → gold { display-mode: "form" }',
    'def load_gold(url_or_path):',
    '    """Read the canonical gold JSON: [{\'id\',\'text\',\'label\'}, ...]."""',
    '    if str(url_or_path).startswith("http"):',
    '        raw = urllib.request.urlopen(url_or_path).read().decode("utf-8")',
    '        gold = json.loads(raw)',
    '    else:',
    '        gold = json.loads(open(url_or_path, encoding="utf-8").read())',
    '    print(f"Loaded {len(gold)} items. First one:", gold[0])',
    '    return gold')

LIB_RUN_PROMPT = code(
    '#@title 🔧 Library cell: run_prompt(prompt, gold) → predictions { display-mode: "form" }',
    'def _extract_level(text):',
    '    """Pull the first A1/A2/B1/B2/C1/C2 out of the model\'s reply."""',
    '    m = re.search(r"\\b([ABC][12])\\b", str(text).upper())',
    '    return m.group(1) if m else "??"',
    '',
    'def run_prompt(prompt, gold):',
    '    """Send each item\'s `text` to the LLM via {text}, collect predicted labels."""',
    '    predictions = []',
    '    for i, item in enumerate(gold, 1):',
    '        reply = generate_text(prompt.format(text=item["text"]))',
    '        predictions.append(_extract_level(reply))',
    '        if i % 12 == 0:',
    '            print(f"  ...{i}/{len(gold)} done")',
    '    print(f"Got {len(predictions)} predictions.")',
    '    return predictions')

LIB_EVALUATE = code(
    '#@title 🔧 Library cell: evaluate(gold, predictions) → P/R/F1 + confusion matrix { display-mode: "form" }',
    'def evaluate(gold, predictions):',
    '    y_true = [item["label"] for item in gold]',
    '    y_pred = predictions',
    '    print(classification_report(y_true, y_pred, labels=LEVELS, zero_division=0))',
    '    cm = confusion_matrix(y_true, y_pred, labels=LEVELS)',
    '    plt.figure(figsize=(5.5, 4.5))',
    '    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",',
    '                xticklabels=LEVELS, yticklabels=LEVELS)',
    '    plt.xlabel("Predicted"); plt.ylabel("Gold"); plt.title("Confusion matrix")',
    '    plt.tight_layout(); plt.show()')

LIB_SHOW_ERRORS = code(
    '#@title 🔧 Library cell: show_errors(gold, predictions) → misclassified table { display-mode: "form" }',
    'def show_errors(gold, predictions):',
    '    rows = [{"id": g["id"], "gold": g["label"], "pred": p, "text": g["text"]}',
    '            for g, p in zip(gold, predictions) if g["label"] != p]',
    '    print(f"{len(rows)} of {len(gold)} wrong.")',
    '    return pd.DataFrame(rows)')

# Freeze predictions to JSON so evaluation is reproducible: run the model ONCE,
# save its predictions, then evaluate the saved file (identical numbers every run,
# no LLM in the loop). Used keyless on Day 2 (metrics lesson) and by the final
# project (auditable, autogradable deliverable).
LIB_PREDICTIONS = code(
    '#@title 🔧 Library cell: save_predictions / load_predictions { display-mode: "form" }',
    'def save_predictions(predictions, path):',
    '    """Freeze a list of predicted labels to JSON."""',
    '    with open(path, "w", encoding="utf-8") as f:',
    '        json.dump(predictions, f)',
    '    print(f"Saved {len(predictions)} predictions to {path}")',
    '',
    'def load_predictions(url_or_path):',
    '    """Read a frozen predictions list — a committed URL or a local path."""',
    '    if str(url_or_path).startswith("http"):',
    '        raw = urllib.request.urlopen(url_or_path).read().decode("utf-8")',
    '        predictions = json.loads(raw)',
    '    else:',
    '        predictions = json.loads(open(url_or_path, encoding="utf-8").read())',
    '    print(f"Loaded {len(predictions)} frozen predictions.")',
    '    return predictions')

PIPELINE_LIB = [LIB_LOAD_GOLD, LIB_RUN_PROMPT, LIB_EVALUATE, LIB_SHOW_ERRORS, LIB_PREDICTIONS]


def how_to_use(day, title, part_a, part_b):
    return md(
        f"# {title}",
        "",
        f"*Day {day} — Linguistic Data Analysis II*",
        "",
        "### How to use this notebook",
        "",
        "This is your **single submission for the day**. It has two parts:",
        "",
        f"- **Part A · Tutorial** — {part_a}",
        f"- **Part B · Corpus Lab** — {part_b}",
        "",
        "You only edit the cells marked **✏️ YOU EDIT**. Cells marked **🔧 Library cell** "
        "are pre-written — run them, don't change them.",
        "",
        "➡️ Work top to bottom. When you're done, **Runtime → Run all**, then "
        "**File → Download → Download `.ipynb`** and submit that file.")


SUBMISSION = md(
    "---",
    "## ✅ Before you submit",
    "",
    "1. **Runtime → Run all** and check every cell ran without error.",
    "2. Part A outputs are visible (tables / charts / the model's answers).",
    "3. Part B self-check prints ✅ (or your TODO answers are filled in).",
    "4. **File → Download → Download `.ipynb`** and upload that one file.")


def todo(*lines):
    """A clearly-marked TODO scaffold block (content not written yet)."""
    return md(
        "::: {.callout-warning}",
        "## 🚧 TODO — to be written",
        *("" if l == "" else l for l in lines),
        ":::")


# ============================================================ DAY 1
def day1():
    cells = [how_to_use(
        1, "Day 1 · Python basics & your first LLM call",
        "a hands-on Python primer, then your first call to a language model.",
        "short Python exercises you complete and self-check.")]

    # ---- Part A: Python primer ----
    cells += [md(
        "## Part A · Tutorial — a 15-minute Python primer",
        "",
        "No prior Python needed. Run each cell, read the output, then change a value and "
        "re-run to see what happens. Everything this week is built from these few ideas.")]

    cells += [md(
        "### 1. Variables & data types",
        "",
        "A **variable** is a name for a value. Python's core types you'll use all week: "
        "**string** (`str`, text), **integer** (`int`) and **float** (decimal number), "
        "**list** (an ordered sequence), and **dictionary** (`dict`, key → value pairs).")]
    cells += [code(
        'sentence = "The cat sat on the mat."   # str  — text, in quotes',
        'word_count = 6                          # int  — whole number',
        'score = 4.5                             # float — decimal number',
        'levels = ["A1", "A2", "B1"]            # list — ordered, square brackets',
        'item = {"id": 1, "text": sentence, "label": "A1"}  # dict — key: value',
        '',
        'print(type(sentence), type(word_count), type(score))',
        'print("levels[0] =", levels[0])         # lists are indexed from 0',
        'print("item[\'label\'] =", item["label"])  # look up a dict value by its key')]

    cells += [md(
        "### 2. `if` statements — make a decision",
        "",
        "Run one branch or another depending on a condition. Indentation (4 spaces) is how "
        "Python groups the lines that belong to each branch.")]
    cells += [code(
        'score = 4.5',
        'if score < 4:',
        '    band = "Low"',
        'elif score < 7:',
        '    band = "Mid"',
        'else:',
        '    band = "High"',
        'print("score", score, "→ band", band)')]

    cells += [md(
        "### 3. `for` loops — do something to every item",
        "",
        "Loop over a list, or over a dictionary's items. This is exactly how we'll process "
        "every sentence in a dataset.")]
    cells += [code(
        'for level in levels:',
        '    print("level:", level)',
        '',
        'print("---")',
        'for key, value in item.items():',
        '    print(key, "→", value)')]

    cells += [md(
        "### 4. Functions — name a reusable piece of code",
        "",
        "A **function** takes inputs (arguments) and `return`s a result. Define once, call "
        "as often as you like.")]
    cells += [code(
        'def band_of(score):',
        '    """Turn a numeric score into a Low/Mid/High band."""',
        '    if score < 4:',
        '        return "Low"',
        '    elif score < 7:',
        '        return "Mid"',
        '    return "High"',
        '',
        'print(band_of(2), band_of(5), band_of(9))')]

    cells += [md(
        "### 5. Basic input / output",
        "",
        "`print(...)` shows a value. To read data, we mostly parse **JSON** — the "
        "`{id, text, label}` shape you'll see all week. (`input()` also reads from the "
        "keyboard, but it pauses *Run all*, so we avoid it here.)")]
    cells += [code(
        'raw = \'[{"id": 1, "text": "Hello.", "label": "A1"}, {"id": 2, "text": "Nevertheless, the findings were inconclusive.", "label": "C1"}]\'',
        'data = json.loads(raw)          # JSON text → Python list of dicts',
        'print("number of items:", len(data))',
        'for row in data:',
        '    print(row["id"], row["label"], "|", row["text"])',
        '',
        '# (Reading from the keyboard — left commented so Run all does not pause:)',
        '# name = input("Your name: ")',
        '# print("Hello,", name)')]

    # ---- setup + first LLM call ----
    cells += [md(
        "### 6. Meet the model — your first LLM call",
        "",
        "Run the setup cell (loads the LLM backend — in Colab that's the free built-in "
        "Gemini, no key needed), then send the model a prompt with `generate_text(...)`.")]
    cells += [setup_cell()]
    cells += [md("**✏️ YOU EDIT** — change the prompt and re-run.")]
    cells += [code(
        'reply = generate_text("In one sentence, what is applied linguistics?")',
        'print(reply)')]

    # ---- Part B: lab ----
    cells += [md(
        "## Part B · Corpus Lab — Python practice",
        "",
        "Fill in each function so it does what its docstring says (replace the "
        "`raise NotImplementedError(...)` line). Then run the **self-check** cell at the "
        "bottom until every line prints ✅. No grader needed — the checks *are* your grader.")]
    cells += [code(
        '# ✏️ YOU EDIT — replace each NotImplementedError with your code.',
        '',
        'def label_of(item):',
        '    """Return the value stored under the key "label" in the dict `item`.',
        '    Example: label_of({"id": 1, "text": "Hi", "label": "A1"}) -> "A1".',
        '    """',
        '    raise NotImplementedError("Return item[\'label\'].")',
        '',
        '',
        'def long_words(words, n):',
        '    """Return a LIST of the words whose length is greater than n.',
        '    Example: long_words(["a", "cat", "elephant"], 3) -> ["elephant"].',
        '    """',
        '    # HINT: build a result list; loop with `for w in words:`; keep w if len(w) > n.',
        '    raise NotImplementedError("Return the words longer than n characters.")',
        '',
        '',
        'def count_labels(items):',
        '    """Given a list of {id, text, label} dicts, return a dict mapping each',
        '    label to how many times it appears.',
        '    Example: count_labels([{"label":"A1"}, {"label":"A1"}, {"label":"B1"}])',
        '             -> {"A1": 2, "B1": 1}.',
        '    """',
        '    # HINT: start with counts = {}; for each item, add 1 to counts[label]',
        '    #       (use counts.get(label, 0) + 1 so the first time starts at 0).',
        '    raise NotImplementedError("Count how many items carry each label.")')]
    cells += [code(
        '#@title 🔎 Self-check — run me { display-mode: "form" }',
        'sample = [{"id": 1, "text": "Hi.", "label": "A1"},',
        '          {"id": 2, "text": "Hello there.", "label": "A1"},',
        '          {"id": 3, "text": "Nevertheless...", "label": "C1"}]',
        'checks = [',
        '    ("label_of", label_of(sample[0]) == "A1"),',
        '    ("long_words", long_words(["a", "cat", "elephant"], 3) == ["elephant"]),',
        '    ("count_labels", count_labels(sample) == {"A1": 2, "C1": 1}),',
        ']',
        'for name, ok in checks:',
        '    print(("✅" if ok else "❌"), name)',
        'print("All passed ✅" if all(ok for _, ok in checks)',
        '      else "Some checks failed — fix them and re-run.")')]

    cells += [SUBMISSION]
    save("day1_python_and_first_llm.ipynb", cells)


# ============================================================ DAY 2
def day2():
    cells = [how_to_use(
        2, "Day 2 · Gold standards & evaluation",
        "load a gold standard → evaluate a **frozen** set of model predictions → read "
        "precision / recall / F1 + a confusion matrix → inspect the errors, on an "
        "easy-to-judge task (CEFR sentence level).",
        "code the evaluation metrics (precision, recall, F1, Cohen's κ) by hand, then "
        "check them against scikit-learn.")]

    # ---- Part A: the CEFR pipeline tutorial (ported from 02_gold_and_eval) ----
    cells += [md(
        "## Part A · Tutorial — the pipeline on CEFR-SP",
        "",
        "The task (CEFR sentence level, A1–C2) is easy to judge on purpose — today the "
        "*mechanics* are the lesson, not the labeling.",
        "",
        "::: {.callout-note}",
        "## Today runs on *frozen* predictions — no API key, no live model",
        "You met the live model on Day 1 and saw its answers change from run to run. When "
        "you're learning to *measure* quality, that wobble is just noise fighting the lesson — "
        "so today the model's predictions are **pre-computed and committed** to a file. You "
        "load them and everyone's precision / recall / F1 come out **identical every run**. "
        "You'll run the model yourself (with the key) from Day 3 on.",
        ":::")]
    cells += [md("### Setup — run this first")]
    cells += [setup_cell(
        CEFR_GOLD_URL,
        "CEFR-SP gold set (72 sentences, 12 per level), fetched from the course repo.",
        predictions_url=CEFR_PREDICTIONS_DAY2_URL)]
    cells += PIPELINE_LIB
    cells += [md(
        "### Step 1 — Load the gold standard",
        "",
        "Notice the shape: every dataset this week is `{\"id\", \"text\", \"label\"}`. That is "
        "the *only* data shape you have to learn.")]
    cells += [code('gold = load_gold(GOLD_URL)')]
    cells += [md(
        "### Step 2 — The prompt, and the frozen predictions it produced",
        "",
        "Here is the prompt we sent the model — `{text}` is where each sentence gets slotted "
        "in. We ran it **once** over the gold set and committed the predictions, so today you "
        "load that frozen file rather than call the model. (From Day 3 you'll run prompts like "
        "this yourself.)")]
    cells += [code(
        '# The prompt used to produce the frozen predictions (shown for reference — not run today):',
        'PROMPT = """You are an expert rater of English sentence difficulty using the CEFR scale.',
        'Classify the sentence into exactly one of: A1, A2, B1, B2, C1, C2.',
        'Answer with the level only.',
        '',
        'Sentence: {text}"""',
        '',
        '# Load the pre-computed predictions (same order as `gold`):',
        'predictions = load_predictions(PREDICTIONS_URL)')]
    cells += [md(
        "### Step 3 — Read the evaluation",
        "",
        "Per-level precision / recall / F1 (plus a macro average), then the confusion "
        "matrix. For CEFR you'll usually see confusions between *adjacent* levels "
        "(B1 ↔ B2), rarely far-apart ones (A1 ↔ C2) — the model has the right idea, "
        "imprecise thresholds. Because the predictions are frozen, these numbers are the "
        "same every time you run — that's the point.")]
    cells += [code('evaluate(gold, predictions)')]
    cells += [md(
        "### Step 4 — Error analysis",
        "",
        "For each miss, ask: is the **gold** defensible, or is this a genuinely borderline "
        "sentence? *\"Is the disagreement the model's fault or the scheme's?\"* is the heart "
        "of annotation work — and it returns with force in the Day 3 discourse task.")]
    cells += [code('show_errors(gold, predictions)')]

    # ---- Part B: metrics-from-scratch lab ----
    cells += [md(
        "## Part B · Corpus Lab — code the metrics from scratch",
        "",
        "`evaluate()` above printed precision, recall, F1 and a confusion matrix *for* you. "
        "Now you write those formulas yourself, from plain lists of labels — no imports, no "
        "numpy. Once you have coded them, the numbers scikit-learn reports in your final "
        "project will never be a black box.",
        "",
        "Fill in each function (replace its `raise NotImplementedError(...)`), then run the "
        "**self-check** cell — it compares your functions against scikit-learn on a small "
        "example and prints ✅ / ❌ for each.")]
    cells += [code(
        '# ✏️ YOU EDIT — implement each function. All take plain Python lists of labels.',
        '',
        'def confusion_counts(gold, pred, label):',
        '    """Return {"tp","fp","fn","tn"} for ONE label, treating it as the positive class.',
        '        tp: gold IS label AND pred IS label',
        '        fp: gold is NOT label BUT pred IS label',
        '        fn: gold IS label BUT pred is NOT label',
        '        tn: gold is NOT label AND pred is NOT label',
        '    Example (label="B2", gold=["A1","B2","B2"], pred=["A1","B2","C1"]):',
        '        {"tp": 1, "fp": 0, "fn": 1, "tn": 1}',
        '    """',
        '    # HINT: start tp=fp=fn=tn=0; loop `for g, p in zip(gold, pred):`;',
        '    #       if/elif on whether g == label / p == label.',
        '    raise NotImplementedError("Count tp, fp, fn, tn and return them in a dict.")',
        '',
        '',
        'def precision(gold, pred, label):',
        '    """tp / (tp + fp). Of all items CALLED `label`, what fraction really were?',
        '    Return 0.0 if tp + fp == 0 (never divide by zero)."""',
        '    raise NotImplementedError("Return tp / (tp + fp), or 0.0 if tp + fp == 0.")',
        '',
        '',
        'def recall(gold, pred, label):',
        '    """tp / (tp + fn). Of all items that TRULY were `label`, what fraction found?',
        '    Return 0.0 if tp + fn == 0."""',
        '    raise NotImplementedError("Return tp / (tp + fn), or 0.0 if tp + fn == 0.")',
        '',
        '',
        'def f1(gold, pred, label):',
        '    """Harmonic mean of precision and recall:',
        '        2 * p * r / (p + r).   Return 0.0 if p + r == 0."""',
        '    # HINT: reuse precision(...) and recall(...) above.',
        '    raise NotImplementedError("Return the harmonic mean of precision and recall.")',
        '',
        '',
        'def macro_f1(gold, pred, labels):',
        '    """Plain average of f1(gold, pred, label) over every label in `labels`',
        '    (every class counts equally, no matter how many items it has)."""',
        '    raise NotImplementedError("Average f1 over every label in `labels`.")',
        '',
        '',
        'def percent_agreement(a, b):',
        '    """Fraction of positions where two annotators agree: a[i] == b[i]. 0.0–1.0."""',
        '    raise NotImplementedError("Return the fraction of positions where a[i] == b[i].")',
        '',
        '',
        'def cohen_kappa(a, b):',
        '    """Agreement corrected for chance:  (p_o - p_e) / (1 - p_e).',
        '        p_o = observed agreement = percent_agreement(a, b)',
        '        p_e = chance agreement = sum over labels of prop_a(label) * prop_b(label),',
        '              where prop_x(label) = (# times x used label) / N.',
        '    Return 0.0 if 1 - p_e == 0."""',
        '    # HINT: labels = set(a) | set(b); N = len(a); a.count(label) counts uses.',
        '    raise NotImplementedError("Return (p_o - p_e) / (1 - p_e), or 0.0 if 1 - p_e == 0.")')]
    cells += [code(
        '#@title 🔎 Self-check against scikit-learn — run me { display-mode: "form" }',
        'from sklearn.metrics import (precision_score, recall_score, f1_score,',
        '                             cohen_kappa_score)',
        '',
        '# A small fixture with imbalance and a few mistakes — enough to catch bugs.',
        'LAB = ["A1", "A2", "B1", "B2"]',
        'g = ["A1", "A1", "A2", "A2", "B1", "B1", "B1", "B2", "B2", "B2"]',
        'p = ["A1", "A2", "A2", "A2", "B1", "B1", "B2", "B2", "B2", "A2"]',
        'ann_a = ["A1", "A2", "B1", "B1", "B2", "A1", "A2", "B2", "B1", "A1"]',
        'ann_b = ["A1", "A2", "B1", "B2", "B2", "A2", "A2", "B2", "B1", "A1"]',
        '',
        'TOL, results = 1e-9, []',
        'def _chk(name, got, exp):',
        '    ok = abs(got - exp) < TOL',
        '    results.append(ok)',
        '    print(("✅" if ok else "❌"), f"{name:<22} yours={got:.6f}  sklearn={exp:.6f}")',
        '',
        'for label in LAB:',
        '    _chk(f"precision({label})", precision(g, p, label),',
        '         precision_score(g, p, labels=[label], average="micro", zero_division=0))',
        '    _chk(f"recall({label})", recall(g, p, label),',
        '         recall_score(g, p, labels=[label], average="micro", zero_division=0))',
        '    _chk(f"f1({label})", f1(g, p, label),',
        '         f1_score(g, p, labels=[label], average="micro", zero_division=0))',
        '_chk("macro_f1", macro_f1(g, p, LAB),',
        '     f1_score(g, p, labels=LAB, average="macro", zero_division=0))',
        '_chk("percent_agreement", percent_agreement(ann_a, ann_b),',
        '     sum(1 for x, y in zip(ann_a, ann_b) if x == y) / len(ann_a))',
        '_chk("cohen_kappa", cohen_kappa(ann_a, ann_b), cohen_kappa_score(ann_a, ann_b))',
        '',
        'print("-" * 55)',
        'print(f"All {len(results)} checks passed ✅  — your metrics match scikit-learn."',
        '      if all(results) else',
        '      f"{results.count(False)} of {len(results)} checks FAILED — fix and re-run.")')]

    cells += [SUBMISSION]
    save("day2_gold_standards_and_evaluation.ipynb", cells)


# ============================================================ DAY 3
def day3():
    cells = [how_to_use(
        3, "Day 3 · Prompt design & iteration",
        "improve a prompt through zero-shot → few-shot → chain-of-thought on the SAME "
        "CEFR-SP task, comparing macro-F1 at each step.",
        "run your own prompt-iteration study and error analysis (to be written).")]

    cells += [md(
        "## Part A · Tutorial — three ways to prompt",
        "",
        "Same pipeline as Day 2, same CEFR-SP data — only the **prompt** changes. We compare "
        "three techniques and watch macro-F1 move:",
        "",
        "| Iteration | Technique | Idea |",
        "|---|---|---|",
        "| 0 | **zero-shot** | just describe the task |",
        "| 1 | **few-shot** | add a few labeled examples |",
        "| 2 | **chain-of-thought** | ask the model to reason before answering |",
        "",
        "Record the macro-F1 (the `macro avg` row of `evaluate`) after each run so you can "
        "tell a story about what helped.")]
    cells += [md(
        "::: {.callout-important}",
        "## From today you run the model yourself — you need a free API key",
        "Days 1–2 used Colab's built-in Gemini (or a frozen file). From Day 3 on you call the "
        "model live and need your prompt runs to be **reproducible** (`temperature=0` + a fixed "
        "seed), so the notebook switches to the **Gemini API**. Get a free key and add it to "
        "Colab **Secrets** as `GEMINI_API_KEY` — one-time, ~2 minutes, no install. Full steps: "
        "[Get a free Gemini API key](../tools/gemini-api-key.md). "
        "When the setup cell prints `LLM backend: Gemini API (...)` you're set; if it still says "
        "`Colab Gemini`, your secret isn't set or its notebook-access toggle is off.",
        ":::")]
    cells += [md("### Setup — run this first")]
    cells += [setup_cell(
        CEFR_GOLD_URL,
        "CEFR-SP gold set (72 sentences, 12 per level), fetched from the course repo.")]
    cells += PIPELINE_LIB
    cells += [code('gold = load_gold(GOLD_URL)')]

    cells += [md(
        "### Iteration 0 — zero-shot   ✏️ YOU EDIT",
        "",
        "Just describe the task. This is your baseline; note its macro-F1.")]
    cells += [code(
        'PROMPT_ZERO = """You are an expert rater of English sentence difficulty using the CEFR scale.',
        'Classify the sentence into exactly one of: A1, A2, B1, B2, C1, C2.',
        'Answer with the level only.',
        '',
        'Sentence: {text}"""',
        '',
        'pred_zero = run_prompt(PROMPT_ZERO, gold)',
        'evaluate(gold, pred_zero)')]

    cells += [md(
        "### Iteration 1 — few-shot   ✏️ YOU EDIT",
        "",
        "Add a few **labeled examples** so the model can pattern-match. The examples are "
        "hand-written here (feel free to draw more from `cefr_pool.json` — never from the "
        "gold set you're scoring on, or you'd be testing on training data).")]
    cells += [code(
        'PROMPT_FEWSHOT = """You are an expert rater of English sentence difficulty using the CEFR scale.',
        'Classify the sentence into exactly one of: A1, A2, B1, B2, C1, C2. Answer with the level only.',
        '',
        'Examples:',
        'Sentence: "I have a cat." -> A1',
        'Sentence: "She went to the shops because she needed some milk." -> A2',
        'Sentence: "The results suggest a modest but consistent improvement." -> B2',
        'Sentence: "Notwithstanding these caveats, the framework generalises well." -> C2',
        '',
        'Sentence: {text}"""',
        '',
        'pred_few = run_prompt(PROMPT_FEWSHOT, gold)',
        'evaluate(gold, pred_few)')]

    cells += [md(
        "### Iteration 2 — chain-of-thought (CoT)   ✏️ YOU EDIT",
        "",
        "Ask the model to **reason first, then answer**. Giving it room to think often helps "
        "on borderline items.")]
    cells += [code(
        'PROMPT_COT = """You are an expert rater of English sentence difficulty using the CEFR scale.',
        'Think step by step about the vocabulary and grammar, then decide the level.',
        'Do NOT mention any other CEFR level while reasoning.',
        'End your answer with the final level on its own, exactly one of: A1, A2, B1, B2, C1, C2.',
        '',
        'Sentence: {text}"""',
        '',
        'pred_cot = run_prompt(PROMPT_COT, gold)',
        'evaluate(gold, pred_cot)')]
    cells += [md(
        "::: {.callout-note}",
        "## A real limitation to notice",
        "`run_prompt` grabs the *first* CEFR level it sees in the reply. With chain-of-thought "
        "the model may mention a level mid-reasoning, so the parser can pick the wrong one — "
        "which is exactly why the prompt says *don't mention other levels*. If CoT scores "
        "*worse* than few-shot, check `show_errors` to see whether it's the model or the parser.",
        ":::")]
    cells += [md(
        "### Compare the three",
        "",
        "Fill in the macro-F1 you saw at each step. This little table *is* your result.",
        "",
        "| Iteration | macro-F1 |",
        "|---|:--:|",
        "| 0 · zero-shot | … |",
        "| 1 · few-shot | … |",
        "| 2 · chain-of-thought | … |")]

    # ---- Part B: TODO scaffold ----
    cells += [md("## Part B · Corpus Lab — your own prompt-iteration study")]
    cells += [todo(
        "This lab is still being written. When it is, you will:",
        "",
        "1. Pick one class the model handles worst (use `show_errors`).",
        "2. Write **one concrete prompt change** you predict will help, and test it.",
        "3. Log each iteration's macro-F1 in the table below and explain the change.",
        "",
        "| Iteration | Prompt change | macro-F1 |",
        "|---|---|:--:|",
        "| … | … | … |")]

    cells += [SUBMISSION]
    save("day3_prompt_design.ipynb", cells)


# ============================================================ DAY 4
def day4():
    cells = [how_to_use(
        4, "Day 4 · Pipeline assembly & sampling your gold set",
        "sample a balanced gold subset from a dataset pool, ready for QC.",
        "quality-control and adjudicate your sampled gold set (to be written).")]

    cells += [md(
        "## Part A · Tutorial — sample a balanced gold subset",
        "",
        "For your mini-project you build your **own** gold set by sampling from a *pool*. "
        "A balanced sample (equal items per label) keeps precision/recall/F1 and the "
        "confusion matrix meaningful. Here we demo it on the familiar CEFR pool; swap "
        "`POOL_URL` for your track's pool. See the "
        "[mini-project tracks](../datasets/mini-project-tracks.md) for the full list.")]
    cells += [md("### Setup — run this first")]
    cells += [setup_cell(
        CEFR_GOLD_URL,
        "Default gold + LEVELS for CEFR; change LEVELS to match your own track's labels.")]
    cells += PIPELINE_LIB
    cells += [code(
        f'POOL_URL = "{CEFR_POOL_URL}"   # ✏️ swap for your track\'s pool',
        'pool = load_gold(POOL_URL)')]
    cells += [md(
        "### Draw a balanced sample   ✏️ YOU EDIT",
        "",
        "`PER_LABEL` items per label, with a fixed random seed so the sample is reproducible "
        "(same every run). Rare classes simply yield fewer — that's a property of the data.")]
    cells += [code(
        'import random',
        'from collections import defaultdict, Counter',
        '',
        'PER_LABEL = 8            # how many items per label',
        'random.seed(42)         # fixed seed = same sample every run',
        '',
        'by_label = defaultdict(list)',
        'for item in pool:',
        '    by_label[item["label"]].append(item)',
        '',
        'gold = []',
        'for label in sorted(by_label):',
        '    bucket = by_label[label]',
        '    random.shuffle(bucket)',
        '    gold.extend(bucket[:PER_LABEL])',
        'random.shuffle(gold)',
        'gold = [{"id": i + 1, "text": x["text"], "label": x["label"]}',
        '        for i, x in enumerate(gold)]',
        '',
        'print("sampled:", len(gold), "| per label:",',
        '      dict(Counter(x["label"] for x in gold)))')]
    cells += [md(
        "### Save your gold set to Google Drive",
        "",
        "Keep your own gold set in **your** Drive (not the course repo). See "
        "[Housing your data in Google Drive](../tools/google-drive-data.md) for the "
        "mount → save → load round-trip.")]
    cells += [code(
        '# ✏️ Uncomment in Colab to save to your Drive:',
        '# from google.colab import drive; drive.mount("/content/drive")',
        '# import json',
        '# with open("/content/drive/MyDrive/my_gold.json", "w", encoding="utf-8") as f:',
        '#     json.dump(gold, f, ensure_ascii=False, indent=2)',
        '# print("saved", len(gold), "items")')]

    cells += [md("## Part B · Corpus Lab — QC & adjudicate your gold set")]
    cells += [todo(
        "This lab is still being written. When it is, you will:",
        "",
        "1. Each group member independently re-checks part of the sampled set against the "
        "scheme.",
        "2. Flag disagreements with the published label.",
        "3. Discuss and resolve them — and record *what changed* (this feeds your report's "
        "\"Scheme & gold\" section).")]

    cells += [SUBMISSION]
    save("day4_pipeline_and_sampling.ipynb", cells)


# ============================================================ DAY 5
def day5():
    cells = [how_to_use(
        5, "Day 5 · Project finalization",
        "assemble your full pipeline end-to-end and produce your final evaluation.",
        "finalize your one-page report and notebook (to be written).")]

    cells += [md(
        "## Part A · Tutorial — assemble & finalize",
        "",
        "By today you have all the pieces: a **gold set** (Day 4), a **prompt** you iterated "
        "(Day 3), and the **evaluation** pipeline (Day 2). Today you run them together, "
        "end-to-end, on your held-out gold set and capture the final numbers.",
        "",
        "The four ready-made track notebooks in the "
        "**[`lda2-final-template`](https://github.com/egumasa/lda2-final-template)** repo "
        "(`notebooks/cefr.ipynb`, `raamove.ipynb`, `cars50.ipynb`, `l2_errors.ipynb`) are "
        "the fully-worked versions of this pipeline — use the one matching your track as your "
        "starting point.")]
    cells += [todo(
        "The step-by-step finalization walkthrough is still being written. It will cover:",
        "",
        "- loading your own gold set from Drive,",
        "- running your best prompt end-to-end,",
        "- producing the final per-class P/R/F1 + confusion matrix,",
        "- and exporting the figures for your slides.")]

    cells += [md(
        "## Part B · Corpus Lab — the one-page report",
        "",
        "Your notebook is submitted alongside a one-page report. Draft its five sections "
        "here as you finish each analysis (full guidance: "
        "[mini-project tracks](../datasets/mini-project-tracks.md)).")]
    cells += [todo(
        "Report scaffold (to be expanded):",
        "",
        "1. **Scheme & gold** — label set; how you built the gold set; what QC changed.",
        "2. **Prompt iterations** — table of changes and F1 at each step.",
        "3. **Evaluation** — per-class precision/recall/F1 + confusion matrix.",
        "4. **Error analysis** — concrete misses; model's fault or the scheme's?",
        "5. **Limitations** — stochasticity, contamination risk, what the numbers don't show.")]

    cells += [SUBMISSION]
    save("day5_project_finalization.ipynb", cells)


if __name__ == "__main__":
    day1()
    day2()
    day3()
    day4()
    day5()
    print("ALL DONE ->", OUT)
