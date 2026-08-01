#!/usr/bin/env python3
"""Generate the five combined day notebooks (tutorial + Corpus Lab in one file).

Students submit ONE .ipynb per day; each contains that day's guided **tutorial**
(Part A) and its **Corpus Lab** (Part B). Notebooks run in Google Colab (free built-in
Gemini, no key) and fall back to a local LLM API off-Colab.

Each day's Setup cell and 🔧 pipeline cells are selected **per day** so a notebook ships
only what it actually calls: setup_cell(backend=..., lib_names=[...]) picks the LLM
backend (demo / api / none) and the imports, and libs(...) picks the pipeline cells.
See planning/course_planning/notebook-coding-principles.md for the rules this enforces.
Days whose tutorial or lab is not written yet ship honest TODO scaffolds.

Run:  python sources/notebooks/_generate_day_notebooks.py
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
# The pool Day 4 samples from. NOT cefr_pool.json — that one is 3,183 items and
# git-ignored, so fetching it by URL 404s (this is what broke the Day-4 dry run).
# cefr_pool_demo.json is a committed 335-item draw that keeps the natural imbalance
# (A1 12 … B1 123), because "rare levels yield fewer items" is the lesson.
CEFR_POOL_URL = f"{REPO_RAW}/cefr_pool_demo.json"
# The 24-item validation set Day 3 tunes prompts on (4 per level, disjoint from the 72).
# Iterating on the gold set would mean tuning on the items the final score is reported
# over — the contamination S7 teaches against. Built by `prep_datasets.py cefr_val`.
CEFR_VAL_URL = f"{REPO_RAW}/cefr_val.json"
# Frozen CEFR predictions for the Day-2 metrics lesson (generated once from the
# fixed Day-2 prompt; committed so Day 2 is keyless & deterministic).
CEFR_PREDICTIONS_DAY2_URL = f"{REPO_RAW}/predictions_day2.json"


# ------------------------------------------------- shared cells (library)
# Two LLM backends live here; each day's Setup cell pulls in ONLY the one it needs
# (and Days 2 & 4 pull in neither — they touch no model):
#   * DEMO_BACKEND (Day 1)   → Colab's built-in Gemini (colab.ai). Keyless, zero
#     setup, but NON-reproducible: colab.ai exposes no temperature/seed, so output
#     varies run to run. Day 1 only needs to *see* a model answer, so that's fine.
#   * API_BACKEND (Day 3+)   → the Gemini API with temperature=0 + seed, for
#     reproducible, autograded work. Prefers a key (Colab Secrets or env), and
#     falls back to colab.ai if none is set.
# Pinned model: gemini-3.1-flash-lite (15 RPM / 500 RPD). NOT gemini-2.5-flash: its
# free tier is 5 RPM / 20 RPD, so one 72-item lab run needs 3.5 days of quota.
# See planning/course_planning/api-preflight-testing.md Task 1.

# The keyless demo backend (Day 1): pace the calls, then hand off to colab.ai.
DEMO_BACKEND = '''# --- LLM backend: Colab's free built-in Gemini (no API key) -------------------

### Step 1: remember when we last called the model, so we can pace ourselves ###
_last_call_time = 0.0    # updated after every call; 0.0 means "never called yet"
_min_interval = 13.2     # colab.ai publishes no rate limit — pace conservatively

### Step 2: the one function you call all day — it waits its turn, then asks ###
def generate_text(prompt: str) -> str:
    """Send a prompt to Colab's built-in Gemini and give back its reply.

    It waits between calls so we don't go too fast. Non-reproducible: colab.ai
    exposes no temperature or seed, so the same prompt can give a different answer.

    Args:
        prompt: the text to send to the model.

    Returns:
        The model's reply, as text.

    Example:
        >>> reply = generate_text("What CEFR level is this sentence? I like cats.")
    """
    global _last_call_time                                    # share this across calls
    wait = _min_interval - (time.monotonic() - _last_call_time)   # still too soon?
    if wait > 0:
        time.sleep(wait)                                      # pause for the difference
    _last_call_time = time.monotonic()                        # note the time of this call
    return _raw_generate_text(prompt)                         # now actually ask the model

### Step 3: connect to Colab's built-in model (or explain why we can't) ###
try:
    from google.colab import ai            # Colab's built-in Gemini — no key
    _raw_generate_text = lambda p: ai.generate_text(p)   # the raw, unpaced call
    _backend = "Colab Gemini (demo, non-reproducible)"   # shown by the Setup printout
except ImportError:                        # `google.colab` only exists inside Colab
    raise RuntimeError(
        "No LLM backend found. Run this notebook in Google Colab (free built-in "
        "Gemini, no key needed). See resources/tools/gemini-api-key.md.")'''

# The reproducible API backend (Day 3+): key preferred, colab.ai fallback, plus a
# rate-limit guard (pacing + retry) — walked through piece by piece in Day 3.
API_BACKEND = '''# --- LLM backend: Gemini API when a key is set, else colab.ai demo ------------
MODEL_ID = "gemini-3.1-flash-lite"   # pinned model for the reproducible (API) backend

### Step 1: find an API key — Colab's Secrets panel first, then the environment ###
def _resolve_gemini_key() -> str | None:
    """Find a Gemini API key: Colab Secrets first (not auto-exported to env), then env.

    Returns:
        The key, or None when neither place has one.
    """
    try:
        from google.colab import userdata      # only exists in Colab
        key = userdata.get("GEMINI_API_KEY")   # what you saved in the Secrets panel
        if key:
            return key                         # found one — use it
    except Exception:
        pass                                    # not in Colab, or secret not set
    return os.environ.get("GEMINI_API_KEY")     # last resort: an environment variable

### Step 2: build the reproducible backend around that key ###
def _make_api_backend(key: str) -> tuple:
    """Reproducible backend: Gemini API with temperature=0 + a fixed seed.

    Args:
        key: your Gemini API key.

    Returns:
        Two things: the function that calls the model, and a label to print.
    """
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=key)         # your own connection to the API
    # temperature=0 + a fixed seed = the same prompt gives the same answer every run,
    # which is what makes the autograded Corpus Labs reproducible.
    cfg = types.GenerateContentConfig(temperature=0, seed=42)
    return (lambda p: client.models.generate_content(
                model=MODEL_ID, contents=p, config=cfg).text,   # prompt in, text out
            f"Gemini API ({MODEL_ID}, temperature=0, seed=42)")  # a label to print

# ---- keeps us from calling the model faster than the free tier allows ----------
# (explained step by step in Day 3, right after this cell — the short version:
#  wait a bit between calls, and if we still get told to slow down, wait longer
#  and try again, unless the message says we are out of quota for the whole day.)

### Step 3: read the error message to work out WHICH kind of failure this is ###
def _looks_like_rate_limit(error: Exception) -> bool:
    """Does this error mean "you are going too fast", rather than a real bug?

    Args:
        error: the exception the API call raised.

    Returns:
        True when the message looks like a rate limit.
    """
    text = str(error).lower()                   # the error, as lowercase text
    return any(s in text for s in               # true if ANY of these phrases appear
               ["429", "resource_exhausted", "rate limit", "quota", "too many requests"])

def _looks_like_daily_quota(error: Exception) -> bool:
    """Is this the PER-DAY cap? Those don't clear by waiting a few seconds.

    Args:
        error: the exception the API call raised.

    Returns:
        True when the message names a per-day limit.
    """
    text = str(error).lower()
    return "per day" in text or "perday" in text.replace(" ", "")

def _suggested_delay(error: Exception, fallback: float) -> float:
    """The server often says "please retry in 7.2s" — obey it if it did.

    Args:
        error: the exception the API call raised.
        fallback: how long to wait when the server named no delay.

    Returns:
        Seconds to wait before trying again.
    """
    m = re.search(r"retry in ([0-9]+(?:\\.[0-9]+)?)s", str(error).lower())
    return float(m.group(1)) + 1.0 if m else fallback   # +1s cushion, else our guess

### Step 4: the one function you call all week — pace, ask, and retry if told to ###
_last_call_time = 0.0   # generate_text remembers & updates this with `global`

def generate_text(prompt: str, max_retries: int = 5) -> str:
    """Send a prompt to the model and give back its reply.

    It waits between calls so we stay under the free tier's speed limit, and tries
    again if the server tells us to slow down.

    Args:
        prompt: the text to send to the model.
        max_retries: how many times to try again after a rate-limit message.

    Returns:
        The model's reply, as text.

    Raises:
        RuntimeError: when the daily quota is used up, or after the last retry.

    Example:
        >>> reply = generate_text("What CEFR level is this sentence? I like cats.")
    """
    global _last_call_time                      # share the clock across every call
    for attempt in range(max_retries + 1):      # try, then retry up to max_retries times
        wait = _min_interval - (time.monotonic() - _last_call_time)   # still too soon?
        if wait > 0:
            time.sleep(wait)                    # pause so we stay under the speed limit
        try:
            _last_call_time = time.monotonic()  # note the time of this attempt
            return _raw_generate_text(prompt)   # success — hand the reply straight back
        except Exception as error:
            if not _looks_like_rate_limit(error):
                raise                                   # a real bug — don't hide it
            if _looks_like_daily_quota(error):          # out of fuel for today
                raise RuntimeError(
                    "Daily quota used up for today — waiting won't help until it "
                    "resets. Come back tomorrow, or ask your instructor.") from error
            if attempt == max_retries:
                raise                                   # we've been patient enough
            print(f"  (rate limited — waiting before trying again, attempt {attempt+1})")
            # wait longer each time round (attempt+2), unless the server named a delay
            time.sleep(_suggested_delay(error, _min_interval * (attempt + 2)))
    raise RuntimeError("Still rate-limited after several tries.")

### Step 5: pick a backend — your API key if you have one, else Colab's demo model ###
# Prefer the API key when set (reproducible); else fall back to colab.ai (demo).
_key = _resolve_gemini_key()
if _key:
    _raw_generate_text, _backend = _make_api_backend(_key)   # reproducible: key + seed
    _min_interval = 4.4     # keeps us under gemini-3.1-flash-lite's 15-requests/minute cap
else:
    try:
        from google.colab import ai            # Colab's built-in Gemini — no key
        _raw_generate_text, _backend = (lambda p: ai.generate_text(p)), "Colab Gemini (demo, non-reproducible)"
        _min_interval = 13.2   # colab.ai publishes no rate limit — pace conservatively
    except ImportError:        # no key AND not in Colab — nothing to call
        raise RuntimeError(
            "No LLM backend found. Run this notebook in Google Colab (free built-in "
            "Gemini, no key needed), or set GEMINI_API_KEY — in Colab via the Secrets "
            "panel, or as an environment variable when running locally. "
            "See resources/tools/gemini-api-key.md.")'''


def setup_cell(backend=None, lib_names=(), gold_url=None, gold_comment=None,
               predictions_url=None, val_url=None):
    """Build a day's 📦 Setup cell, importing ONLY what that day uses.

    backend    : "demo" (Day 1), "api" (Day 3+), or None (Days 2 & 4 — no model).
    lib_names  : which 🔧 pipeline cells the day ships (drives which imports load).
    gold_url / predictions_url : optionally append GOLD_URL+LEVELS / PREDICTIONS_URL.
    val_url    : Day 3 only — the validation set prompts are tuned on, so the gold
                 set stays a held-out test set.
    """
    lib_names = set(lib_names)
    simple = []                                   # single-line `import x` modules
    if backend == "api":
        simple += ["os", "re", "time"]
    elif backend == "demo":
        simple += ["time"]
    if lib_names & {"load_gold", "predictions"} or gold_url or predictions_url:
        simple += ["json", "urllib.request"]
    if "run_prompt" in lib_names:
        simple += ["re"]
    # The sheets helpers draw a confusion matrix too (annotator-vs-annotator), so they
    # need the same plotting stack as `evaluate` — but not classification_report.
    sheets_names = {n for n in lib_names if n.startswith("sheets")}
    want_report = "evaluate" in lib_names
    want_matrix = bool(lib_names & {"evaluate"} or sheets_names)
    want_viz = bool(lib_names & {"evaluate", "show_errors"} or sheets_names)

    lines = ['#@title 📦 Setup — run me first { display-mode: "form" }',
             "# Helper — you don't need to read this. Run it and move on."]
    if simple:
        lines.append("import " + ", ".join(sorted(set(simple))))
    if want_report:
        lines.append("from sklearn.metrics import (classification_report, confusion_matrix,")
        lines.append("                             cohen_kappa_score)")
    elif want_matrix:
        lines.append("from sklearn.metrics import confusion_matrix")
    if want_viz:
        lines.append("import pandas as pd, seaborn as sns, matplotlib.pyplot as plt")
    src = "\n".join(lines)

    if backend == "demo":
        src += "\n\n" + DEMO_BACKEND
    elif backend == "api":
        src += "\n\n" + API_BACKEND

    if gold_url:
        src += (f'\n\n# {gold_comment}\n'
                f'GOLD_URL = "{gold_url}"\n'
                'LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]')
    if val_url:
        src += (f'\nVAL_URL  = "{val_url}"   '
                '# 24 items to tune on, so GOLD_URL stays held out')
    if predictions_url:
        src += f'\nPREDICTIONS_URL = "{predictions_url}"   # frozen model predictions'

    status = "Setup done."
    if backend:
        status += " LLM backend: {_backend}."
    if want_matrix:
        status += " scikit-learn ready."
    src += f'\nprint(f"{status}")'
    return code(src)


# The 🔧 pipeline "library" cells. Each day ships only the ones it calls, selected
# by name through libs(...) — see the LIB registry below. All are collapsed form
# cells flagged "helper — you don't need to read this"; their internals are kept
# readable (explicit loops, minimal regex) for the curious.
_HELPER_NOTE = "# Helper — you don't need to read this. Run it and move on."

LIB_LOAD_GOLD = code(
    '#@title 🔧 Library cell: load_gold(url_or_path) → gold { display-mode: "form" }',
    _HELPER_NOTE,
    'def load_gold(url_or_path: str) -> list[dict[str, str]]:',
    '    """Read the canonical gold JSON: [{\'id\',\'text\',\'label\'}, ...].',
    '',
    '    Args:',
    '        url_or_path: a web address, or the path to a file on this machine.',
    '',
    '    Returns:',
    '        The gold items, each a dict with "id", "text" and "label".',
    '',
    '    Example:',
    '        >>> gold = load_gold(GOLD_URL)',
    '    """',
    '    if str(url_or_path).startswith("http"):                 # a web address?',
    '        raw = urllib.request.urlopen(url_or_path).read().decode("utf-8")  # download it',
    '        gold = json.loads(raw)                              # JSON text -> list of dicts',
    '    else:                                                   # otherwise a file on disk',
    '        gold = json.loads(open(url_or_path, encoding="utf-8").read())',
    '    print(f"Loaded {len(gold)} items. First one:", gold[0])  # proof it worked',
    '    return gold')

LIB_RUN_PROMPT = code(
    '#@title 🔧 Library cell: run_prompt(prompt, gold) → predictions { display-mode: "form" }',
    _HELPER_NOTE,
    'def _extract_level(text: str) -> str:',
    '    """Pull the first A1/A2/B1/B2/C1/C2 out of the model\'s reply.',
    '',
    '    Args:',
    '        text: whatever the model replied.',
    '',
    '    Returns:',
    '        The level it found, or "??" when the reply contains none.',
    '    """',
    '    # The model may answer "B2" or "I would say B2." — search rather than assume.',
    '    m = re.search(r"\\b([ABC][12])\\b", str(text).upper())',
    '    return m.group(1) if m else "??"      # "??" = no level found in the reply',
    '',
    'def run_prompt(prompt: str, gold: list[dict[str, str]]) -> list[str]:',
    '    """Send each item\'s `text` to the LLM via {text}, collect predicted labels.',
    '',
    '    Args:',
    '        prompt: your prompt, containing {text} where the sentence should go.',
    '        gold: the items to label, each with a "text" key.',
    '',
    '    Returns:',
    '        One predicted label per gold item, in the same order.',
    '',
    '    Example:',
    '        >>> predictions = run_prompt(PROMPT, gold)',
    '    """',
    '    predictions = []                                  # answers, in gold order',
    '    for i, item in enumerate(gold, 1):                # i counts 1, 2, 3, ...',
    '        reply = generate_text(prompt.format(text=item["text"]))  # {text} <- sentence',
    '        predictions.append(_extract_level(reply))     # keep just the level',
    '        if i % 12 == 0:                               # every 12th item...',
    '            print(f"  ...{i}/{len(gold)} done")       # ...show progress',
    '    print(f"Got {len(predictions)} predictions.")',
    '    return predictions')

LIB_EVALUATE = code(
    '#@title 🔧 Library cell: evaluate(gold, predictions) → P/R/F1 + κ + confusion matrix { display-mode: "form" }',
    _HELPER_NOTE,
    'def evaluate(gold: list[dict[str, str]],',
    '             predictions: list[str],',
    '             ordered: bool = False) -> None:',
    '    """Score predictions against gold: per-class P/R/F1 + macro, Cohen\'s κ, and a',
    '    confusion-matrix heatmap.',
    '',
    '    ordered=True adds QUADRATIC WEIGHTED κ — use it only when the labels sit on a',
    '    scale (A1 < A2 < ... < C2), so that a near miss counts as a smaller error than',
    '    a far one. For unordered categories, plain κ is the one to report.',
    '',
    '    Args:',
    '        gold: the gold items, each with a "label" key.',
    '        predictions: one predicted label per gold item, in the same order.',
    '        ordered: True when the labels sit on a scale.',
    '',
    '    Returns:',
    '        Nothing. It prints the table and the κ values, and draws the matrix.',
    '',
    '    Example:',
    '        >>> evaluate(gold, predictions, ordered=True)',
    '    """',
    '    ### Step 1: line the two label lists up, gold first ###',
    '    y_true = []                          # the correct labels, from the gold set',
    '    for item in gold:',
    '        y_true.append(item["label"])',
    '    y_pred = predictions                 # the model\'s labels, in the same order',
    '',
    '    ### Step 2: per-class precision / recall / F1, as a text table ###',
    '    print(classification_report(y_true, y_pred, labels=LEVELS, zero_division=0))',
    '',
    '    ### Step 3: one overall number — agreement corrected for chance ###',
    '    print(f"Cohen\'s kappa            {cohen_kappa_score(y_true, y_pred):.3f}")',
    '    if ordered:                          # only when the labels sit on a scale',
    '        weighted = cohen_kappa_score(y_true, y_pred, labels=LEVELS,',
    '                                     weights="quadratic")   # near misses hurt less',
    '        print(f"Cohen\'s kappa (weighted) {weighted:.3f}   <- labels are ordered")',
    '',
    '    ### Step 4: draw the same information as a picture ###',
    '    cm = confusion_matrix(y_true, y_pred, labels=LEVELS)   # counts per gold/pred pair',
    '    plt.figure(figsize=(5.5, 4.5))',
    '    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",     # annot=True writes the counts',
    '                xticklabels=LEVELS, yticklabels=LEVELS)',
    '    plt.xlabel("Predicted"); plt.ylabel("Gold"); plt.title("Confusion matrix")',
    '    plt.tight_layout(); plt.show()')

LIB_SHOW_ERRORS = code(
    '#@title 🔧 Library cell: show_errors(gold, predictions) → misclassified table { display-mode: "form" }',
    _HELPER_NOTE,
    'def show_errors(gold: list[dict[str, str]], predictions: list[str]) -> pd.DataFrame:',
    '    """The items the model got wrong, as a table you can read and argue about.',
    '',
    '    Args:',
    '        gold: the gold items, each with "id", "text" and "label".',
    '        predictions: one predicted label per gold item, in the same order.',
    '',
    '    Returns:',
    '        A table with one row per mistake: id, gold, pred, text.',
    '',
    '    Example:',
    '        >>> show_errors(gold, predictions)',
    '    """',
    '    rows = []',
    '    for g, p in zip(gold, predictions):   # walk gold and predictions side by side',
    '        if g["label"] != p:               # keep only the disagreements',
    '            rows.append({"id": g["id"], "gold": g["label"], "pred": p, "text": g["text"]})',
    '    print(f"{len(rows)} of {len(gold)} wrong.")',
    '    return pd.DataFrame(rows)             # a table, so Colab displays it nicely')

# Frozen predictions make evaluation reproducible: the model is run ONCE offline,
# its predictions saved to JSON and committed, then loaded here (identical numbers
# every run, no LLM in the loop). Day 2 loads them keyless. The one-off freezing is
# an offline step, so only the loader ships in the notebooks.
LIB_LOAD_PREDICTIONS = code(
    '#@title 🔧 Library cell: load_predictions(url_or_path) → predictions { display-mode: "form" }',
    _HELPER_NOTE,
    'def load_predictions(url_or_path: str) -> list[str]:',
    '    """Read a frozen predictions list — a committed URL or a local path.',
    '',
    '    Args:',
    '        url_or_path: a web address, or the path to a file on this machine.',
    '',
    '    Returns:',
    '        One predicted label per gold item, in gold order.',
    '',
    '    Example:',
    '        >>> predictions = load_predictions(PREDICTIONS_URL)',
    '    """',
    '    if str(url_or_path).startswith("http"):                 # a web address?',
    '        raw = urllib.request.urlopen(url_or_path).read().decode("utf-8")  # download it',
    '        predictions = json.loads(raw)                       # JSON text -> list',
    '    else:                                                   # otherwise a file on disk',
    '        predictions = json.loads(open(url_or_path, encoding="utf-8").read())',
    '    print(f"Loaded {len(predictions)} frozen predictions.")',
    '    return predictions')

# Manual annotation round-trip: Colab writes a Google Sheet into the student's own
# Drive, they label it by hand in the browser (two annotator columns, so agreement
# falls out), then Colab reads it back and canonicalises it to {id,text,label}.
# gspread + google-auth are pre-installed in Colab; no pip install needed.
""">>> The Google Sheets round-trip, split by the STEP that uses each piece.

S5 does not run these together: step D reads the sheet and measures, step E lists the
disagreements, step F adjudicates and compares. Loading all seven functions before step D
put 235 lines between the student and their first number, and shipped
`create_annotation_sheet`, which S5 never runs. So each piece is its own registry entry and
`libs(...)` requests it where it is called.

`sheets_base` carries the column constants and `_sheets_client`, which the others need — it
must be loaded first, and it is, because step D loads it.
"""

LIB_SHEETS_BASE = code(
    '#@title 🔧 Library cell: read one tab of your annotation sheet { display-mode: "form" }',
    "# Helper — you don't need to read this. Run it and move on.",
    '# Sheet column headers (the annotation template uses these exact names):',
    'COL_ID, COL_TEXT = "ID", "Text"',
    'COL_A, COL_B = "CoderA", "CoderB"',
    'COL_FINAL, COL_NOTES = "Final", "Note"',
    'ANNOTATION_HEADER = [COL_ID, COL_TEXT, COL_A, COL_B, COL_FINAL, COL_NOTES]',
    '',
    'def _sheets_client():',
    '    """Authorise gspread with your Google account (a pop-up asks for permission).',
    '',
    '    Returns:',
    '        A logged-in connection to Google Sheets.',
    '    """',
    '    from google.colab import auth',
    '    import google.auth, gspread',
    '    auth.authenticate_user()           # the pop-up: "let Colab use your Sheets"',
    '    creds, _ = google.auth.default()   # the permission slip that pop-up produced',
    '    return gspread.authorize(creds)    # a logged-in connection to Google Sheets',
    '',
    'def load_annotation_sheet(sheet_id: str,',
    '                          worksheet: str = "round1") -> list[dict[str, str]]:',
    '    """Read one TAB of your annotation sheet back as a list of row dicts.',
    '',
    '    Opening by id or URL always opens the exact sheet, so two copies that share a',
    '    name (\\"Copy of ...\\") are never confused. Each round lives in its own tab, so',
    '    re-annotating in round2 never overwrites round1.',
    '',
    '    Args:',
    '        sheet_id: the long id in the sheet\'s URL',
    '            (docs.google.com/spreadsheets/d/<THIS PART>/edit). The whole URL works too.',
    '        worksheet: the TAB name — one tab per annotation round.',
    '',
    '    Returns:',
    '        One dict per row, keyed by the column headings (ID, Text, CoderA, ...).',
    '',
    '    Raises:',
    '        ValueError: when the sheet has no tab by that name. The message lists the',
    '            tabs it does have.',
    '',
    '    Example:',
    '        >>> rows = load_annotation_sheet(SHEET_ID, worksheet="round1")',
    '    """',
    '    ### Step 1: open the sheet — a pasted URL and a bare id both work ###',
    '    client = _sheets_client()',
    '    if str(sheet_id).startswith("http"):',
    '        sheet = client.open_by_url(sheet_id)',
    '    else:',
    '        sheet = client.open_by_key(sheet_id)',
    '',
    '    ### Step 2: find the tab (the "round") — and say which tabs exist if it is missing ###',
    '    try:',
    '        ws = sheet.worksheet(worksheet)',
    '    except Exception:',
    '        tabs = [w.title for w in sheet.worksheets()]   # what IS in this sheet',
    '        raise ValueError(f"No tab named {worksheet!r}. Tabs in this sheet: {tabs}")',
    '',
    '    ### Step 3: read every row as a dict keyed by the header names ###',
    '    rows = ws.get_all_records()        # [{"ID": 1, "Text": "...", "CoderA": "B1", ...}, ...]',
    '    print(f"Read {len(rows)} rows from tab \'{worksheet}\'.")',
    '    return rows')


# Only the reference appendix at the end of S5 runs this — the template Sheets were built
# once, ahead of the session. It is shown so the sampling is transparent, and loaded there
# rather than at step D, where it would be 40 lines a student never calls.
LIB_SHEETS_CREATE = code(
    '#@title 🔧 Library cell: create_annotation_sheet(title, items, labels) → url { display-mode: "form" }',
    "# Helper — you don't need to read this. Run it and move on.",
    '',
    'def create_annotation_sheet(title: str,',
    '                            items: list[dict[str, str]],',
    '                            labels: list[str]) -> str:',
    '    """Create a Sheet in YOUR Drive: one row per item, blank columns to label.',
    '',
    '    Any existing label on an item is deliberately NOT copied across, so you',
    '    annotate blind.',
    '',
    '    Args:',
    '        title: the name to give the new spreadsheet.',
    '        items: the items to annotate, each with "id" and "text".',
    '        labels: the labels your scheme allows, printed as a reminder.',
    '',
    '    Returns:',
    '        The URL of the sheet it created.',
    '',
    '    Example:',
    '        >>> url = create_annotation_sheet("Group 1 gold", items, LEVELS)',
    '    """',
    '    ### Step 1: make an empty spreadsheet in your own Drive ###',
    '    sheet = _sheets_client().create(title)',
    '    worksheet = sheet.sheet1',
    '    worksheet.update_title("round1")   # first round lives in the \'round1\' tab',
    '',
    '    ### Step 2: one row per item — id and text filled in, label columns left blank ###',
    '    rows = []',
    '    for item in items:',
    '        #                id            text          CoderA CoderB Final Note',
    '        rows.append([item["id"], item["text"], "", "", "", ""])',
    '',
    '    ### Step 3: write it all in one go, then pin the header row ###',
    '    worksheet.update([ANNOTATION_HEADER] + rows)   # header first, then the data',
    '    worksheet.freeze(rows=1)                       # header stays put as you scroll',
    '    print(f"Created \'{title}\' with {len(rows)} rows in tab \'round1\'.")',
    '    print("Allowed labels:", ", ".join(labels))',
    '    print("Open it:", sheet.url)',
    '    return sheet.url')


# Step F: turn the adjudicated sheet into canonical gold, then compare it with the
# published labels. Loaded at F, not at D, because that is where they are called.
LIB_SHEETS_CANONICAL = code(
    '#@title 🔧 Library cell: to_canonical(rows, labels) → gold { display-mode: "form" }',
    "# Helper — you don't need to read this. Run it and move on.",
    '',
    'def to_canonical(rows: list[dict[str, str]],',
    '                 labels: list[str],',
    '                 column: str = COL_FINAL) -> list[dict[str, str]]:',
    '    """Turn annotation rows into canonical gold: [{"id","text","label"}, ...].',
    '',
    '    Blank rows are skipped; labels outside `labels` are reported, not silently kept.',
    '',
    '    Args:',
    '        rows: the rows read back by load_annotation_sheet.',
    '        labels: the labels your scheme allows. Anything else is reported as invalid.',
    '        column: which column holds the agreed label.',
    '',
    '    Returns:',
    '        The usable rows as gold items, each {"id", "text", "label"}.',
    '',
    '    Example:',
    '        >>> my_gold = to_canonical(rows, LEVELS)',
    '    """',
    '    ### Step 1: sort every row into one of three piles ###',
    '    gold, blank, invalid = [], 0, []     # usable rows · not labelled yet · typos',
    '    for row in rows:',
    '        label = str(row.get(column, "")).strip()   # .strip() drops stray spaces',
    '        if not label:',
    '            blank += 1                    # nobody has filled this row in yet',
    '        elif label not in labels:',
    '            invalid.append((row.get(COL_ID), label))   # e.g. "b1" or "B11"',
    '        else:',
    '            gold.append({"id": int(row[COL_ID]), "text": str(row[COL_TEXT]), "label": label})',
    '',
    '    ### Step 2: report all three counts, so nothing is dropped silently ###',
    '    print(f"{len(gold)} usable · {blank} still blank · {len(invalid)} invalid")',
    '    if invalid:',
    '        print("  fix these in the sheet, then re-run:", invalid[:10])   # first 10',
    '    return gold')


# Step D: the measuring. Loaded together with the reader above, because "read the sheet"
# and "see how far apart you were" are one action from the student's side.
LIB_SHEETS_AGREEMENT = code(
    '#@title 🔧 Library cell: annotator_agreement(rows) → % agreement, κ, matrix { display-mode: "form" }',
    "# Helper — you don't need to read this. Run it and move on.",
    '',
    'def annotator_agreement(rows: list[dict[str, str]],',
    '                        a: str = COL_A,',
    '                        b: str = COL_B) -> dict[str, float] | None:',
    '    """Percent agreement + Cohen\'s κ between the two annotator columns, PLUS an',
    '    annotator-vs-annotator confusion matrix (the diagonal is where you agreed;',
    '    off-diagonal cells show which label pairs the two of you confuse).',
    '',
    '    Args:',
    '        rows: the rows read back by load_annotation_sheet.',
    '        a: the column holding the first annotator\'s labels.',
    '        b: the column holding the second annotator\'s labels.',
    '',
    '    Returns:',
    '        {"n", "percent_agreement", "kappa"}, or None when no row has both',
    '        annotators filled in.',
    '',
    '    Example:',
    '        >>> annotator_agreement(rows)',
    '    """',
    '    from sklearn.metrics import cohen_kappa_score',
    '    ### Step 1: keep only the rows where BOTH annotators actually chose a label ###',
    '    pairs = [(str(r.get(a, "")).strip(), str(r.get(b, "")).strip()) for r in rows]',
    '    pairs = [(x, y) for x, y in pairs if x and y]    # drop half-finished rows',
    '    if not pairs:',
    '        print("No rows where BOTH annotators have labelled. Nothing to compare yet.")',
    '        return None',
    '',
    '    ### Step 2: two metrics — raw agreement, and agreement corrected for chance ###',
    '    a_labels = [x for x, _ in pairs]                 # annotator A\'s choices',
    '    b_labels = [y for _, y in pairs]                 # annotator B\'s choices',
    '    percent = sum(x == y for x, y in pairs) / len(pairs)   # how often you matched',
    '    kappa = cohen_kappa_score(a_labels, b_labels)    # ...minus the luck',
    '    print(f"{len(pairs)} doubly-annotated · agreement {percent:.1%} · Cohen\'s κ {kappa:.3f}")',
    '',
    '    ### Step 3: draw WHICH labels you two confuse, not just how often ###',
    '    # annotator-vs-annotator confusion matrix (mirrors the gold-vs-model evaluate()):',
    '    labels = sorted(set(a_labels) | set(b_labels))   # every label either of you used',
    '    cm = confusion_matrix(a_labels, b_labels, labels=labels)',
    '    plt.figure(figsize=(5.5, 4.5))',
    '    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",',
    '                xticklabels=labels, yticklabels=labels)',
    '    plt.xlabel("Annotator B"); plt.ylabel("Annotator A")   # diagonal = you agreed',
    '    plt.title("Annotator-vs-annotator confusion matrix")',
    '    plt.tight_layout(); plt.show()',
    '    return {"n": len(pairs), "percent_agreement": percent, "kappa": kappa}')


# Step E: the worklist. Its own cell, loaded at E, because the six lines inside it are the
# subject of the cell that follows — the one decision students re-implement in the open.
LIB_SHEETS_DISAGREE = code(
    '#@title 🔧 Library cell: disagreements(rows) → the rows to argue about { display-mode: "form" }',
    "# Helper — you don't need to read this. Run it and move on.",
    '',
    'def disagreements(rows: list[dict[str, str]],',
    '                  a: str = COL_A,',
    '                  b: str = COL_B) -> pd.DataFrame:',
    '    """The rows your two annotators labelled differently — your adjudication list.',
    '',
    '    Args:',
    '        rows: the rows read back by load_annotation_sheet.',
    '        a: the column holding the first annotator\'s labels.',
    '        b: the column holding the second annotator\'s labels.',
    '',
    '    Returns:',
    '        A table of the rows where the two annotators chose different labels.',
    '',
    '    Example:',
    '        >>> disagreements(rows)',
    '    """',
    '    # keep a row only if both annotators labelled it AND they chose differently:',
    '    out = [r for r in rows',
    '           if str(r.get(a, "")).strip() and str(r.get(b, "")).strip()',
    '           and str(r[a]).strip() != str(r[b]).strip()]',
    '    print(f"{len(out)} rows to adjudicate. Agree on a `Final` label for each in the sheet.")',
    '    return pd.DataFrame(out)')


# Step F, second half. Matching is by TEXT, with id only as a fallback — the same rule the
# project's copy follows, and for the project's reason: sample_pool renumbers ids from 1,
# so an id-based match would pair YOUR item 7 with POOL item 7, two unrelated sentences,
# and report a meaningless percentage without ever failing. S5's own sample keeps the
# original ids, so both rules agree here; they stop agreeing the moment a student carries
# this call into the project, which is exactly when nothing would raise.
LIB_SHEETS_COMPARE = code(
    '#@title 🔧 Library cell: compare_to_published(gold, published) → differences { display-mode: "form" }',
    "# Helper — you don't need to read this. Run it and move on.",
    '',
    'def compare_to_published(gold: list[dict[str, str]],',
    '                         published: list[dict[str, str]]) -> pd.DataFrame | None:',
    '    """How often does YOUR final label match the published gold, item by item?',
    '',
    '    Items are matched by their TEXT, not their id, because a sampled set is often',
    '    renumbered from 1 — and matching those ids against the original set would pair',
    '    your item 7 with their item 7: two unrelated sentences, and a percentage that',
    '    means nothing. (Ids are still used as a fallback, in case a text was edited.)',
    '',
    '    Args:',
    '        gold: your own gold items, from to_canonical.',
    '        published: the published gold items, from load_gold.',
    '',
    '    Returns:',
    '        A table of the items where you and the published gold differ, or None',
    '        when nothing could be matched.',
    '',
    '    Example:',
    '        >>> compare_to_published(my_gold, published)',
    '    """',
    '    ### Step 1: index the published labels by text, and by id as a fallback ###',
    '    label_by_text = {}',
    '    label_by_id = {}',
    '    for item in published:',
    '        label_by_text[str(item["text"])] = item["label"]',
    '        label_by_id[item["id"]] = item["label"]',
    '',
    '    ### Step 2: pair each of your items with its published label ###',
    '    matched = []',
    '    for item in gold:',
    '        text = str(item["text"])',
    '        if text in label_by_text:',
    '            theirs = label_by_text[text]',
    '        elif item["id"] in label_by_id:',
    '            theirs = label_by_id[item["id"]]',
    '        else:',
    '            continue                       # not in the published set at all',
    '        matched.append({"id": item["id"], "yours": item["label"],',
    '                        "published": theirs, "text": item["text"]})',
    '    if len(matched) == 0:',
    '        print("None of your items could be matched to the published set.")',
    '        return None',
    '',
    '    ### Step 3: count the matches, then show only the rows where you differ ###',
    '    agree = 0',
    '    differences = []',
    '    for row in matched:',
    '        if row["yours"] == row["published"]:',
    '            agree = agree + 1',
    '        else:',
    '            differences.append(row)',
    '    print(f"{agree}/{len(matched)} match the published label "',
    '          f"({agree / len(matched):.1%})")',
    '    return pd.DataFrame(differences)')


# S6 pass 1 builds the metrics by hand on a BINARY question ("is this sentence
# advanced?"), so it needs the two lists paired into one list of dicts — the same
# shape students have looped over since Day 1 — and a way to see the four counts as
# a square. Both are display/plumbing, never the lesson, so both are helpers.
LIB_PAIR_UP = code(
    '#@title 🔧 Library cell: pair_up(gold, predictions, positive) → items { display-mode: "form" }',
    _HELPER_NOTE,
    'def pair_up(gold: list[dict[str, str]],',
    '            predictions: list[str],',
    '            positive: list[str]) -> list[dict[str, str]]:',
    '    """Pair each gold item with the model\'s prediction, both collapsed to yes/no.',
    '',
    '    Args:',
    '        gold: the gold items, each with "id", "text" and "label".',
    '        predictions: one predicted label per gold item, in the same order.',
    '        positive: the labels that count as "yes" (e.g. ["C1", "C2"]).',
    '',
    '    Returns:',
    '        One dict per item: {"id", "text", "gold", "pred"}, where "gold" and',
    '        "pred" are each "yes" or "no".',
    '',
    '    Example:',
    '        >>> items = pair_up(gold, predictions, ["C1", "C2"])',
    '    """',
    '    items = []',
    '    for g, p in zip(gold, predictions):   # gold item and its prediction, side by side',
    '        items.append({"id": g["id"],',
    '                      "text": g["text"],',
    '                      # six CEFR levels collapse to two answers: "yes" or "no"',
    '                      "gold": "yes" if g["label"] in positive else "no",',
    '                      "pred": "yes" if p in positive else "no"})',
    '    print(f"Paired {len(items)} items. Positive class = {positive}.")',
    '    return items')

LIB_SHOW_2X2 = code(
    '#@title 🔧 Library cell: show_2x2(tally) → the four counts as a square { display-mode: "form" }',
    _HELPER_NOTE,
    'def show_2x2(tally: dict[str, int]) -> None:',
    '    """Print a tally of TP/FP/FN/TN as a confusion matrix — rows are the gold',
    '    label, columns are the prediction. No arithmetic: the same four numbers,',
    '    arranged so you can see where the errors went.',
    '',
    '    Args:',
    '        tally: how many items fell into each outcome, e.g. {"TP": 3, "FP": 1}.',
    '            A missing outcome counts as 0.',
    '',
    '    Returns:',
    '        Nothing. It prints the square.',
    '',
    '    Example:',
    '        >>> show_2x2(tally)',
    '    """',
    '    # .get(..., 0) so a missing outcome shows as 0 rather than crashing:',
    '    tp = tally.get("TP", 0)',
    '    fp = tally.get("FP", 0)',
    '    fn = tally.get("FN", 0)',
    '    tn = tally.get("TN", 0)',
    '    # :<9 pads a label to 9 characters, :>9 right-aligns a number in 9 — that is all',
    '    # the f-strings below are doing: lining the four counts up into a square.',
    '    print(f"{\'\':<9}{\'pred yes\':>9}{\'pred no\':>9}")     # column headings',
    '    print(f"{\'gold yes\':<9}{tp:>9}{fn:>9}")              # top row:    TP  FN',
    '    print(f"{\'gold no\':<9}{fp:>9}{tn:>9}")               # bottom row: FP  TN')

# name → 🔧 cell. A day requests only what it calls via libs(...).
LIB = {
    "load_gold": LIB_LOAD_GOLD,
    "run_prompt": LIB_RUN_PROMPT,
    "evaluate": LIB_EVALUATE,
    "show_errors": LIB_SHOW_ERRORS,
    "predictions": LIB_LOAD_PREDICTIONS,
    # The Sheets round-trip, one entry per S5 step. See the note above LIB_SHEETS_BASE:
    # "sheets_base" carries the column constants and _sheets_client, so whichever step
    # loads first must request it — in S5 that is step D.
    "sheets_base": LIB_SHEETS_BASE,
    "sheets_agreement": LIB_SHEETS_AGREEMENT,
    "sheets_disagree": LIB_SHEETS_DISAGREE,
    "sheets_canonical": LIB_SHEETS_CANONICAL,
    "sheets_compare": LIB_SHEETS_COMPARE,
    "sheets_create": LIB_SHEETS_CREATE,
    "pair_up": LIB_PAIR_UP,
    "show_2x2": LIB_SHOW_2X2,
}


def libs(*names):
    """The helpers ONE step needs, as one collapsed cell.

    Call this once per step, naming only what that step calls — not once per notebook
    with everything in it. Merging a whole day put hundreds of lines between the student
    and their first result, and shipped functions the day never ran; merging a *step*
    keeps the cell short and next to the call it serves.

    The signatures are listed at the top of the merged cell, so it still says what it
    defines without being opened.

    Keep the names here in sync with the lib_names passed to setup_cell (they drive
    the day's imports)."""
    signatures, short_names, bodies = [], [], []
    for name in names:
        lines = "".join(LIB[name]["source"]).split("\n")
        signature = lines[0].split("Library cell: ", 1)[1].split(" {", 1)[0].strip()
        signatures.append(signature)
        short_names.append(signature.split("(")[0].strip())

        # Drop each cell's own "you don't need to read this" note — one is enough —
        # and the blank lines that framed it.
        body = [l for l in lines[1:] if not l.startswith("# Helper — you don't need")]
        while body and not body[0].strip():
            body.pop(0)
        while body and not body[-1].strip():
            body.pop()
        bodies.append("\n".join(body))

    return [code(
        '#@title 🔧 Library cell: %s { display-mode: "form" }' % ", ".join(short_names),
        _HELPER_NOTE,
        *["#   " + s for s in signatures],
        "",
        "\n\n\n".join(bodies))]


_NUMBER = {1: "one", 2: "two", 3: "three"}


def how_to_use(day, title, *parts, note=None):
    """A notebook's opening cell.

    parts : (kind, description) pairs — ("Tutorial", ...) / ("Corpus Lab", ...) —
            lettered Part A, B, C in the order given. Pass none for a notebook that
            is one continuous lab (Day 2's S5 notebook, whose only letters are A–F).
    note  : an extra line for days that ship more than one notebook.
    """
    lines = [f"# {title}",
             "",
             f"*Day {day} — Linguistic Data Analysis II*",
             ""]
    if note:
        lines += [note, ""]
    lines += ["### How to use this notebook", ""]
    if parts:
        # A day with a `note` ships more than one notebook, so it isn't "the" submission.
        lead = "" if note else "This is your **single submission for the day**. "
        lines += [f"{lead}It has {_NUMBER[len(parts)]} parts:", ""]
        lines += [f"- **Part {letter} · {kind}** — {description}"
                  for letter, (kind, description) in zip("ABC", parts)]
        lines += [""]
    lines += [
        "You only edit the cells marked **✏️ YOU EDIT**. Run the **🔧 Library cell**s and "
        "leave them alone.",
        "",
        "➡️ Work top to bottom. When you're done, **Runtime → Run all**, then "
        "**File → Download → Download `.ipynb`** and submit that file."]
    return md(*lines)


_TUTORIAL_CHECKS = ["Tutorial outputs are visible (tables / charts / the model's answers).",
                    "Every Corpus Lab self-check prints ✅ (or your TODO answers are "
                    "filled in)."]


def submission(note=None, checks=None):
    """The closing checklist.

    checks : the middle "what should be visible" items, for a notebook that isn't the
             usual tutorial + lab pair.
    note   : replaces the final upload step for days spread over more than one notebook.
    """
    items = ["**Runtime → Run all** and check every cell ran without error.",
             *(checks or _TUTORIAL_CHECKS),
             "**File → Download → Download `.ipynb`** and upload "
             + (note or "that one file.")]
    return md(
        "***",
        "## ✅ Before you submit",
        "",
        *(f"{i}. {item}" for i, item in enumerate(items, 1)))


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
        1, "Day 1 · Your first LLM call & reading its data",
        ("Tutorial", "call a language model, then learn to read the data it hands back."),
        ("Corpus Lab", "segment text into sentences, run the model over a list, then "
                       "practice the basics."))]

    # ---- Part A: Colab survival → first LLM call → data types → f-strings ----
    cells += [md(
        "## Part A · Tutorial — your first LLM call, and reading its answer",
        "",
        "No prior Python needed. The star of Part A is a single call to a language model; "
        "everything else — variables, data types, f-strings — is just enough Python to read "
        "and reshape what the model gives you back. Run each cell, read the output, then "
        "change a value and re-run to see what happens.")]

    # 1. Colab survival kit
    cells += [md(
        "### 1. Getting your bearings in Colab",
        "",
        "This page is a **Colab notebook**: a stack of **cells** you run top to bottom. A "
        "code cell runs when you press **Shift+Enter** (or click ▶). The first run wakes up "
        "a **runtime** — a temporary computer in the cloud that remembers your variables "
        "until you close the tab. Run the cell below to prove it works.")]
    cells += [code(
        'print("Hello, Colab! You just ran your first cell.")')]
    cells += [md(
        "**When a cell breaks — read the error.** Sooner or later a cell turns red. Don't "
        "panic: Python tells you what went wrong on the **last line**. For example, running "
        "`print(mesage)` (a typo for `message`) prints:",
        "",
        "```",
        "NameError: name 'mesage' is not defined",
        "```",
        "",
        "Read it back to front: the **error type** (`NameError`), the **message** "
        "(`'mesage' is not defined`), and the **line** it happened on. Nearly every early "
        "error is a typo or a cell you haven't run yet. Fix the typo, re-run, move on.")]

    # 2. First LLM call (the spine)
    cells += [md(
        "### 2. Your first LLM call",
        "",
        "Run the setup cell (it loads the LLM backend — in Colab that's the free built-in "
        "Gemini, no key needed), then send the model a prompt with `generate_text(...)`. The "
        "answer comes back as text, which we store in a **variable** called `reply`.")]
    cells += [setup_cell(backend="demo")]
    cells += [md("**✏️ YOU EDIT** — change the prompt text and re-run. The prompt is just "
                 "text you send; the reply is just text you get back.")]
    cells += [code(
        '# ✏️ change the text in the quotes, then press Shift+Enter to re-run.',
        'reply = generate_text("In one sentence, what is applied linguistics?")  # ask',
        'print(reply)                                    # show what came back')]

    # 3. Data types — motivated by the reply
    cells += [md(
        "### 3. What did the model hand back? — Python data types",
        "",
        "Every value in Python has a **type**. Ask what type `reply` is:")]
    cells += [code(
        'print(type(reply))     # <class \'str\'> — a string, i.e. text')]
    cells += [md(
        "The three types you'll use all week:",
        "",
        "- **`str`** — text, in quotes (like `reply`).",
        "- **`list`** — an ordered sequence, in square brackets. Several sentences, say.",
        "- **`dict`** — a labelled record, in curly braces: `key → value` pairs. This is the "
        "`{id, text, label}` shape every dataset this week uses.",
        "",
        "Build one of each, then reach inside them with **`[...]`** — lists by position "
        "(counting from 0), dicts by key.")]
    cells += [code(
        'sentences = ["The cat sat on the mat.",          # a list of strings',
        '             "Nevertheless, the findings were inconclusive."]',
        'record = {"id": 1, "text": sentences[0], "label": "A1"}   # a dict',
        '',
        'print("how many sentences:", len(sentences))   # len() = how many items',
        'print("first sentence:", sentences[0])       # list — index by position (from 0)',
        'print("its gold label:", record["label"])   # dict — index by key')]

    # 4. f-strings
    cells += [md(
        "### 4. f-strings — put your data *into* a prompt",
        "",
        "An **f-string** (`f\"...\"`) drops a variable straight into a piece of text with "
        "`{curly braces}`. That's how you build a prompt *about* a specific sentence — the "
        "trick we'll use to run one prompt over a whole dataset later.")]
    cells += [md("**✏️ YOU EDIT** — change the sentence and re-run.")]
    cells += [code(
        'sentence = "Nevertheless, the findings were inconclusive."   # ✏️ your sentence',
        'prompt = f"What CEFR level (A1-C2) is this sentence? {sentence}"  # f = fill in {}',
        'print("Prompt sent:", prompt)                # see what {sentence} became',
        '',
        'reply = generate_text(prompt)                # send the finished prompt',
        'print("Model says:", reply)')]

    # ---- Part B: segmentation → word vectors → control flow → practice → project ----
    cells += [md(
        "## Part B · Corpus Lab — from text to sentences, then practice",
        "",
        "In Part A you called the model once. Here you'll turn a paragraph into individual "
        "**sentences** (the unit you'll annotate on Day 2), look at how a model stores the "
        "meaning of a word, run the model over a whole list, and then practice the basics on "
        "your own. Cells marked **✏️ YOU EDIT** are yours to change; run the **self-check** at "
        "the end until every line prints ✅.")]

    # The word-vector block in B3 needs a spaCy model that ships with vectors, and the
    # download is large. Put it FIRST, so it runs while the session opens rather than
    # inside the 10-minute block it belongs to.
    #
    # It MUST be en_core_web_lg, not _md. The md model prunes 684,830 vector keys down to
    # 20,000 rows, so unrelated words end up sharing one vector — cat and dog are literally
    # identical in md, as are perhaps/maybe and banana/apple. That would make every
    # similarity number in this block meaningless, and would wreck the punchline in
    # particular: "the same word form always gets the same vector" is only interesting if
    # DIFFERENT words don't also score 1.0. lg keeps 514,157 distinct vectors.
    cells += [md(
        "### Run this one now",
        "",
        "Section 3 uses an English model that carries a **vector for every word**. It is a "
        "large file and takes a minute or two to arrive, so start it now and carry on "
        "reading — it will be ready by the time you need it.")]
    cells += [code(
        '#@title 📥 Download the word-vector model — run me now { display-mode: "form" }',
        _HELPER_NOTE,
        '!python -m spacy download en_core_web_lg',
        '',
        'import importlib, spacy',
        '# The model was installed after Python started, so refresh the module list',
        '# before loading it — otherwise the load below may not find it yet.',
        'importlib.invalidate_caches()',
        'nlp_vec = spacy.load("en_core_web_lg")',
        'print("✅ word vectors ready —", f"{nlp_vec.vocab.vectors.shape[0]:,}", "words have one")')]

    # B1. Segmentation without a model
    cells += [md(
        "### 1. Splitting text into sentences — *without* a model",
        "",
        "Text arrives as one long string. To analyse it sentence by sentence you first have "
        "to **segment** it. The obvious idea: split on the full stop. To do that we call a "
        "**method** on the string — `some_text.split(\".\")` — using a dot (`.`) to run a "
        "built-in action on a value.")]
    cells += [code(
        'paragraph = ("Dr. Smith reviewed the data. The results were clear, e.g. accuracy '
        'rose. Scores went from 3.14 to 9.")',
        '',
        'naive = paragraph.split(".")     # cut the string at every "."',
        'print("pieces:", len(naive))     # how many pieces did that give us?',
        'for piece in naive:              # look at each piece in turn',
        '    print(repr(piece))           # repr() shows the quotes and spaces exactly')]
    cells += [md(
        "Look at the output: `\"Dr\"` (from *Dr.*), `\"e\"` and `\"g\"` (from *e.g.*), and "
        "`\"3\"`/`\"14\"` (from *3.14*) all got split in the wrong places. **Sentence "
        "boundaries are not just full stops** — abbreviations and decimals break the naive "
        "rule.")]

    # B2. Segmentation with a model
    cells += [md(
        "### 2. Splitting text into sentences — *with* a model",
        "",
        "A proper tool knows more than \"cut at every dot\". We'll use **spaCy**, an NLP "
        "library. `import spacy` loads that toolbox; `spacy.blank(\"en\")` makes a minimal "
        "English pipeline and we add a rule-based **sentencizer** to it (no model download "
        "needed).")]
    cells += [code(
        '### Step 1: build a sentence splitter that knows more than "cut at every dot" ###',
        'import spacy                       # the NLP toolbox',
        'nlp = spacy.blank("en")            # a minimal English pipeline',
        'nlp.add_pipe("sentencizer")        # add the rule-based splitter — no download',
        '',
        '### Step 2: run it on the paragraph and look at what came out ###',
        'doc = nlp(paragraph)               # spaCy reads the text',
        'sentences = list(doc.sents)        # spaCy\'s sentence objects, as a list',
        'print("sentences found:", len(sentences))',
        'print("first sentence:", sentences[0])')]
    cells += [md(
        "spaCy keeps `Dr.` and `e.g.` intact and finds the real boundaries. **Why this "
        "matters:** on Day 2 the unit you annotate and feed the LLM is the *sentence* — bad "
        "boundaries mean bad data downstream.")]

    # B3. Word vectors — the S1 embedding concept, made runnable. Session 1 asserts three
    # things on slides (similar words sit close · one word form has only one vector ·
    # averaging throws word order away); every cell here is a student checking one of them.
    cells += [md(
        "### 3. What else the model knows about words",
        "",
        "In Session 1 you saw that a model turns each word into a long list of numbers, and "
        "that words with similar meanings end up with similar numbers. Those numbers are not "
        "hidden — you can look at them.",
        "",
        "The pipeline you just used, `nlp`, only knows where sentences end. The one you "
        "downloaded at the top of Part B, `nlp_vec`, also carries a **vector** for every word "
        "it knows.")]
    cells += [code(
        'word = nlp_vec("suggest")[0]      # read one word; [0] takes the first token',
        'print("how many numbers:", word.vector.shape)',
        'print("the first eight: ", word.vector[:8].round(3))   # rounded, to fit on one line')]
    cells += [md(
        "Three numbers were enough to place a colour in the Session 1 colour cube. It takes "
        "three hundred to place a word.")]

    # Claim 1: similar words sit close.
    cells += [md(
        "#### Are similar words really close?",
        "",
        "`.similarity(...)` compares two vectors and gives a number between 0 and 1: the "
        "higher it is, the closer the two words sit. Compare a pair that share a meaning "
        "with a pair that do not.")]
    cells += [md("**✏️ YOU EDIT** — swap in two words from your own research area and re-run.")]
    cells += [code(
        'print("suggest / indicate:", round(nlp_vec("suggest").similarity(nlp_vec("indicate")), 3))',
        'print("suggest / banana:  ", round(nlp_vec("suggest").similarity(nlp_vec("banana")), 3))')]

    cells += [md(
        "Instead of guessing pairs, you can ask which words sit closest to a given one. "
        "Run the helper, then try your own word.")]
    cells += [code(
        '#@title 🔧 Helper: nearest(word) → the closest words { display-mode: "form" }',
        _HELPER_NOTE,
        'import numpy',
        '',
        '',
        'def nearest(word: str, n: int = 10) -> list[tuple[str, float]]:',
        '    """The n words whose vectors sit closest to `word`.',
        '',
        '    Args:',
        '        word: the word to look up.',
        '        n: how many neighbours to return.',
        '',
        '    Returns:',
        '        A list of (word, closeness) pairs, closest first. Empty if the model',
        '        has never seen the word.',
        '',
        '    Example:',
        '        >>> nearest("hedge", n=3)',
        '    """',
        '    entry = nlp_vec.vocab[word]',
        '    if not entry.has_vector:                 # nothing to compare against',
        '        print(f"{word!r} is not in this model\'s vocabulary.")',
        '        return []',
        '    # most_similar wants a table of rows, so hand it a table with one row in it.',
        '    one_row = entry.vector.reshape(1, -1)',
        '    # Ask for far more candidates than we need: the table stores several spellings',
        '    # of the same word (suggest, Suggest, SUGGEST), and we keep only one of each.',
        '    keys, _, scores = nlp_vec.vocab.vectors.most_similar(one_row, n=n * 8)',
        '    seen = {word.lower()}                    # never report the word itself',
        '    neighbours = []',
        '    for key, score in zip(keys[0], scores[0]):',
        '        found = nlp_vec.vocab.strings[key].lower()',
        '        if found.isalpha() and found not in seen:',
        '            seen.add(found)',
        '            neighbours.append((found, round(float(score), 3)))',
        '    return neighbours[:n]',
        '',
        '',
        'print("Helper ready. Try nearest(\'perhaps\').")')]
    cells += [md("**✏️ YOU EDIT** — put in a word you care about.")]
    cells += [code(
        'for neighbour in nearest("perhaps"):   # ✏️ your word here',
        '    print(neighbour)')]
    cells += [md(
        "Two things are worth noticing before you move on.",
        "",
        "The neighbours of *perhaps* are mostly other hedges — *possibly*, *probably*, "
        "*certainly*, *might*. Nothing told the model that these words hedge a claim; it "
        "placed them together because they turn up in the same positions in text.",
        "",
        "Now try `nearest(\"corpus\")`. The closest words include *habeas*, *christi* and "
        "*corpora*. One spelling has collected the legal sense, the religious sense and the "
        "linguistic sense into a single vector, because there is only one vector available "
        "for the form. `nearest(\"hedge\")` does the same thing with garden hedges and "
        "financial hedging. Keep that in mind for the next part.")]

    # Claim 2: one word form, one vector — the limit that motivates attention.
    cells += [md(
        "#### Where these vectors stop working",
        "",
        "Session 1 used *free* in two sentences that mean different things — *your account is "
        "free of charge* and *claim your free prize now*. Take the word out of each sentence "
        "and compare the two vectors.")]
    cells += [code(
        'banking = nlp_vec("your account is free of charge")',
        'promo   = nlp_vec("claim your free prize now")',
        '',
        'free_1 = banking[3]      # the 4th word of the first sentence',
        'free_2 = promo[2]        # the 3rd word of the second sentence',
        'print("comparing:", free_1.text, "and", free_2.text)',
        'print("similarity:", round(free_1.similarity(free_2), 3))')]
    cells += [md(
        "The score is exactly **1.0**, because the two vectors are not merely close — they "
        "are the same vector. This model stores one vector per word form and looks it up the "
        "same way every time, so the surrounding words change nothing. That is what *static* "
        "means, and it is the limitation Session 1 said attention was built to remove.",
        "",
        "*(Both sentences use lower-case `free` on purpose: these vectors are looked up by "
        "exact form, so `FREE` and `free` are separate entries.)*",
        "",
        "The same lookup has a second consequence. A sentence's vector is the average of its "
        "words, and an average does not record the order they came in:")]
    cells += [code(
        'print(round(nlp_vec("the dog chased the cat")',
        '            .similarity(nlp_vec("the cat chased the dog")), 3))')]
    cells += [md(
        "Two sentences with opposite meanings, one score of 1.0. Word order is gone. "
        "**Why this matters for the rest of the week:** the categories you will annotate — a "
        "CEFR level, a rhetorical move, whether a claim is hedged — depend on word order and "
        "context. A model built on these vectors alone cannot represent that; the model you "
        "call with `generate_text(...)` can.")]

    # A picture of the space.
    cells += [md(
        "#### A map of the space",
        "",
        "Three hundred numbers per word is too many to look at, but the words can be flattened "
        "onto a page so that words with close vectors land near each other.")]
    cells += [code(
        '#@title 🔧 Helper: map_words(words) → a 2-D picture { display-mode: "form" }',
        _HELPER_NOTE,
        'import matplotlib.pyplot as plt',
        '',
        '',
        'def map_words(words: list[str]) -> None:',
        '    """Plot words on a flat map, keeping words with close vectors close.',
        '',
        '    Args:',
        '        words: the words to place.',
        '',
        '    Returns:',
        '        Nothing. It draws the picture.',
        '',
        '    Example:',
        '        >>> map_words(["cat", "dog", "syntax"])',
        '    """',
        '    known = []',
        '    for w in words:',
        '        if nlp_vec.vocab[w].has_vector:',
        '            known.append(w)',
        '        else:',
        '            print(f"skipping {w!r} — not in the model\'s vocabulary")',
        '    rows = numpy.array([nlp_vec.vocab[w].vector for w in known])',
        '    rows = rows - rows.mean(axis=0)          # centre the cloud on zero',
        '    # 300 directions is too many to draw, so keep the two along which these',
        '    # particular words are most spread out, and plot along those.',
        '    _, _, directions = numpy.linalg.svd(rows, full_matrices=False)',
        '    flat = rows @ directions[:2].T',
        '    plt.figure(figsize=(8, 6))',
        '    plt.scatter(flat[:, 0], flat[:, 1], s=18)',
        '    for w, (x, y) in zip(known, flat):',
        '        plt.annotate(w, (x, y), fontsize=11, xytext=(4, 3),',
        '                     textcoords="offset points")',
        '    plt.title("Words placed by their vectors")',
        '    plt.xticks([])',
        '    plt.yticks([])',
        '    plt.show()',
        '',
        '',
        'print("Helper ready. Try map_words([...]).")')]
    cells += [md("**✏️ YOU EDIT** — change the words and re-run.")]
    cells += [code(
        '# Three groups of words: hedges, research verbs, and animals.',
        'map_words(["perhaps", "possibly", "maybe", "likely", "presumably",',
        '           "suggest", "indicate", "demonstrate", "argue", "conclude",',
        '           "cat", "dog", "horse", "rabbit", "sheep"])   # ✏️ your words')]
    cells += [md(
        "The animals land well away from the other ten words. The hedges and the research "
        "verbs, though, sit mixed together rather than in two groups — they are all words of "
        "academic prose, and they appear in similar places in similar texts, which is the "
        "only thing these vectors record. The map shows you what the model separates, which "
        "is not always what you want it to separate.")]

    # B4. Control flow: for / if / function
    cells += [md(
        "### 4. Run the model over every sentence — `for`, `if`, and a function",
        "",
        "Now that you have a list of sentences, do something to *each* one. A **`for` loop** "
        "repeats the same steps for every item; an **`if`** lets you react to what comes "
        "back. Below, we build a prompt for each sentence (with an f-string) and ask the "
        "model for its CEFR level.")]
    cells += [md("**✏️ YOU EDIT** — try your own sentences.")]
    cells += [code(
        '### Step 1: the sentences to ask about ###',
        'examples = ["The findings were inconclusive.",      # ✏️ try your own sentences',
        '            "Nevertheless, we draw some tentative conclusions.",',
        '            "More research is needed."]',
        '',
        '### Step 2: for each one — build a prompt, ask, and react to the reply ###',
        'for sentence in examples:              # repeat everything below for each sentence',
        '    prompt = f"What CEFR level (A1-C2) is this sentence? Answer with just the level. {sentence}"',
        '    reply = generate_text(prompt).strip()   # .strip() removes stray blank space',
        '    if reply == "":                    # the model sometimes says nothing at all',
        '        print(sentence, "→ (no answer)")',
        '    else:                              # normal case: it answered',
        '        print(sentence, "→", reply)')]
    cells += [md(
        "Finally, wrap those three steps — build prompt, call model, tidy the reply — into a "
        "**function** you can reuse. Defining `ask(...)` once means the rest of the week you "
        "just call `ask(sentence)`. This little function is the seed of the pipeline you'll "
        "assemble later.")]
    cells += [code(
        'def ask(sentence):                     # `def` names a block of steps',
        '    """Ask the model for the CEFR level of one sentence; return its reply."""',
        '    prompt = f"What CEFR level (A1-C2) is this sentence? Answer with just the level. {sentence}"',
        '    return generate_text(prompt).strip()   # `return` hands the answer back',
        '',
        'print(ask("The cat sat on the mat."))  # one line now does all three steps')]

    # B4. Guided practice (existing exercises)
    cells += [md(
        "### 5. Your turn — Python practice",
        "",
        "Fill in each function so it does what its docstring says (replace the "
        "`raise NotImplementedError(...)` line). Then run the **self-check** cell below until "
        "every line prints ✅. No grader needed — the checks *are* your grader.")]
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
        '### Step 1: a tiny dataset with answers we already know ###',
        'sample = [{"id": 1, "text": "Hi.", "label": "A1"},',
        '          {"id": 2, "text": "Hello there.", "label": "A1"},',
        '          {"id": 3, "text": "Nevertheless...", "label": "C1"}]',
        '',
        '### Step 2: run each of your functions and compare with the right answer ###',
        'checks = [                             # each entry: (name, did it match?)',
        '    ("label_of", label_of(sample[0]) == "A1"),',
        '    ("long_words", long_words(["a", "cat", "elephant"], 3) == ["elephant"]),',
        '    ("count_labels", count_labels(sample) == {"A1": 2, "C1": 1}),',
        ']',
        '',
        '### Step 3: report one line per check, then an overall verdict ###',
        'for name, ok in checks:',
        '    print(("✅" if ok else "❌"), name)',
        'print("All passed ✅" if all(ok for _, ok in checks)   # all() = every one of them',
        '      else "Some checks failed — fix them and re-run.")')]

    # Read-only syntax cheat-sheet
    cells += [md(
        "### Python you'll *see* but won't have to write",
        "",
        "The pre-written **🔧 Library cells** later this week occasionally use two shorthands. "
        "You never have to write them — just recognise them:",
        "",
        "- A **list comprehension** builds a list in one line. "
        "`[row[\"label\"] for row in rows]` means \"the `label` of every row\" — the same as a "
        "`for` loop that `.append`s each label.",
        "- **`try` / `except`** (handle an error instead of crashing) and **`global`** (let a "
        "function update a shared variable) show up in the LLM backend and are explained on "
        "**Day 3** — no need to learn them today.")]

    # Mini-project setup
    cells += [md(
        "***",
        "## Mini-project — form your group & pick a track",
        "",
        "Before Day 2 you'll settle into a project group and choose a dataset **track**. Each "
        "group needs **at least one *Linguistic Data Analysis I* alumnus**. Once formed, pick "
        "your track and note it — you'll annotate that dataset tomorrow.",
        "",
        "See the [Final Project](../final-project/index.md) page for the tracks and what the "
        "project involves.")]

    cells += [submission()]
    save("day1_python_and_first_llm.ipynb", cells)


# Day 2 is the only day with two notebooks — one per hands-on session — so its
# "how to use" / "before you submit" cells say so rather than "your single submission".
_DAY2_NOTE = ("**Day 2 has two notebooks** — S5 builds a gold standard by hand ({this}), "
              "S6 measures a model against one ({other}). Submit both at the end of the day.")
_DAY2_UPLOAD = "**both** of today's Day-2 notebooks."


# ==================================================== DAY 2 · S5 (gold standard)
def day2_s5():
    cells = [how_to_use(
        2, "Day 2 · S5 — Build a gold standard",
        note=_DAY2_NOTE.format(this="this one", other="`day2-s6_evaluation_metrics.ipynb`"))]

    # The graded home of the "gold-standard construction" outcome (session 2-2). Work is
    # DIVIDED BY ACTIVITY across three surfaces that share one A–F spine (see the S5 slides):
    #   slides own the concepts · the Google Sheet owns the human judgment (A–C, re-annotate
    #   in E) · this notebook owns the numbers (D–F). Colab first runs at step D — steps
    #   A–C are code-free. Cross-reference BY the A–F label, never by cell/slide number.
    # This whole notebook IS the lab, so A–F are its only letters — no Part A/B/C here.
    cells += [md(
        "## Build a gold standard yourself",
        "",
        "So far the gold labels have been handed to you. Now you make some, in six steps "
        "**A–F** across three places:",
        "",
        "- **Slides** — the concepts.",
        "- **A Google Sheet** — where you and your partner annotate (C) and re-annotate (E).",
        "- **This notebook** — the numbers (**D–F**).",
        "",
        "**Steps A–C need no code.** Colab first runs at step D. Find your place by the "
        "letter.")]

    # A–C: code-free (slides + Sheet). The notebook just tells students where to go.
    cells += [md(
        "### A · Sample → copy your track's sheet   *(E&K Step 3 · ①)*",
        "",
        "The sample is already drawn for you: one template Sheet per track. Its `round1` tab "
        "has the columns **`ID · Text · CoderA · CoderB · Final · Note`**, with only `ID` and "
        "`Text` filled in.",
        "",
        "**Open your track's Sheet → `File → Make a copy`.** Then take your copy's **id** from "
        "its URL — the long string between `/d/` and `/edit`. You paste it into step D.")]
    cells += [md(
        "### B · Apply the operationalized scheme   *(E&K Steps 4–5; Fuoli · ②)*",
        "",
        "Before you label, restate the **decidable rule** you're annotating against — the scheme "
        "your team drafted in the earlier sessions — and skim the guidelines and per-level "
        "examples. One label per unit; know your label set cold. → interpret this on **step B** "
        "(slides).")]
    cells += [md(
        "### C · Annotate blind, in pairs   *(E&K Step 6 · ③)*",
        "",
        "**Entirely in the Sheet — no code**, in the **`round1`** tab. One of you fills "
        "**`CoderA`** and the other **`CoderB`**, *without looking at each other's column*. "
        "Leave `Final` blank. Use `Note` for anything you found hard to decide.",
        "",
        "::: {.callout-important}",
        "## Stop here and go annotate",
        "Label all ~20 rows in **both** annotator columns before running the next cell. The "
        "notebook picks up at **step D**.",
        ":::")]

    # D–F: the executable round-trip. Setup lives HERE, not at the top, because Colab
    # first runs at step D — steps A–C are done in the slides and the Sheet.
    cells += [md(
        "### D · Measure agreement   *(E&K Step 6 · ③)*   ✏️ YOU EDIT",
        "",
        "Colab opens here. Run the two setup cells below, then read your sheet back in and "
        "measure how far apart you were.",
        "",
        "::: {.callout-note collapse=\"true\"}",
        "## How to read what this prints",
        "Percent agreement flatters two coders who both lean on the same label. **Cohen's κ** "
        "strips that luck out, so trust the κ (recall S4: 80% raw agreement was only "
        "κ ≈ 0.52). Then find the one off-diagonal cell dragging κ down — that label pair is "
        "your worklist for step E.",
        ":::")]
    # Every helper this notebook uses, so setup imports the right things — but they are
    # LOADED one step at a time below, next to the call each one serves.
    s5_libs = ["sheets_base", "sheets_agreement", "sheets_disagree",
               "sheets_canonical", "sheets_compare", "load_gold"]
    cells += [setup_cell(
        backend=None,          # S5 never calls a model — the judgment is yours
        lib_names=s5_libs,
        gold_url=CEFR_GOLD_URL,
        gold_comment="CEFR-SP gold set — the published labels you compare against in step F.")]
    # Step D needs exactly two things: read the tab, and measure how far apart you were.
    cells += libs("sheets_base", "sheets_agreement")

    cells += [code(
        'SHEET_ID = "1AbCdEf...paste_yours"   # ✏️ the id in YOUR copied sheet\'s URL',
        '                                     #    (…/spreadsheets/d/THIS/edit) — the whole URL works too',
        'ROUND    = "round1"                  # ✏️ which round\'s tab to analyze',
        '',
        'rows = load_annotation_sheet(SHEET_ID, ROUND)   # read that tab back into Python',
        'annotator_agreement(rows)            # % agreement, κ, and the confusion matrix')]

    # The rule for WHICH statistic to report. It goes after the call, so it is read
    # against numbers already on the screen rather than in the abstract. PLAN.md §7 asks
    # groups to commit to this before they run anything, and until now S5 never said it.
    cells += [md(
        "#### Which of those numbers you report is not a free choice",
        "",
        "Which of those three belong in your report follows from **your design**:",
        "",
        "| Your design | Report |",
        "|---|---|",
        "| two coders, labels with no order | percent agreement **and** Cohen's κ |",
        "| two coders, labels on a scale | those two, **and** the weighted κ |",
        "| three or more coders | percent agreement **and** Fleiss' κ, plus Cohen's κ per pair |",
        "",
        "Both numbers, not one. Percent agreement alone counts lucky agreement as earned; a κ "
        "alone is hard to read without the raw figure beside it.",
        "",
        "**Settle this before you run anything**, so the choice does not depend on which "
        "number comes out higher.",
        "",
        "::: {.callout-note}",
        "## One difference in the project",
        "There **each coder gets their own tab**, so the reading call is "
        "`load_coder_sheets(SHEET_ID, CODERS)`. Same columns underneath, one call name "
        "different.",
        ":::")]

    cells += [md(
        "### E · Read the matrix → refine → re-annotate   *(E&K Step 6; Fuoli princ. 2 · ③)*",
        "",
        "A low κ is a diagnosis of your **scheme**, not your annotating. `disagreements(rows)` "
        "lists every row the two of you saw differently.",
        "",
        "::: {.callout-note collapse=\"true\"}",
        "## What to do with this list",
        "For the label pair the matrix flagged, **refine the scheme** until the ambiguity "
        "becomes decidable: add a rule, a boundary case, an example. Then re-annotate in a "
        "fresh round tab (below) and re-run **step D** to see κ move.",
        ":::")]
    cells += libs("sheets_disagree")
    cells += [code(
        'disagreements(rows)   # the rows you two labelled differently — your worklist')]
    cells += [md(
        "#### What that helper actually did — and the decision inside it",
        "",
        "It is six lines, and **the rule inside is a decision about your scheme** rather than "
        "a fact about your data. In the project you write this function yourself; here is the "
        "version the helper runs:")]
    cells += [code(
        '### The rule: a row is a disagreement when the two of you chose DIFFERENT labels ###',
        'to_argue_about = []',
        'for row in rows:',
        '    a = str(row.get("CoderA", "")).strip()   # .strip() drops the spaces a sheet adds',
        '    b = str(row.get("CoderB", "")).strip()',
        '    if a != "" and b != "":      # skip rows one of you has not reached yet',
        '        if a != b:',
        '            to_argue_about.append(row)',
        '',
        'print(len(to_argue_about), "rows to adjudicate")',
        'pd.DataFrame(to_argue_about)     # the same table the helper printed')]
    cells += [md(
        "Two things in there are choices, not facts.",
        "",
        "**A blank cell is skipped, not counted as a disagreement.** A row one of you has not "
        "reached yet is not two people disagreeing.",
        "",
        "**`a != b` is the obvious rule, not the only defensible one.** If your labels sit on "
        "a scale (A1 < A2 < … < C2), you might count only a gap of two or more as worth an "
        "argument. Whichever you use, your report has to say which.")]
    cells += [md(
        "::: {.callout-important}",
        "## Re-annotate in a fresh round tab, then re-run step D",
        "Don't overwrite `round1`. In the Sheet, **right-click the `round1` tab → Duplicate**, "
        "rename the copy **`round2`**, and re-label the confused items *there*. Then set "
        "**`ROUND = \"round2\"`** in step D and re-run it. Repeat (round3, …) until κ is "
        "acceptable, then move to step F.",
        ":::")]
    cells += [md(
        "### F · Adjudicate → gold   *(E&K Step 6 → feeds ④⑤)*   ✏️ YOU EDIT",
        "",
        "The last disagreements don't refine away — you **decide** them. In your **latest round "
        "tab**, fill a single `Final` label for every row. Where you already agreed, `Final` is "
        "that agreed label. Then read it back and convert it to canonical form.")]

    # Type hints and Google-style docstrings are on every helper from here on. They are
    # recognise-only (see notebook-coding-principles.md §6b) — students read them and are
    # never asked to write one, so this is the only cell in the course that teaches them.
    # It sits HERE, immediately above the to_canonical call it uses as its example, rather
    # than at step D against a function students have not met yet.
    cells += [md(
        "#### First — looking up what a helper expects",
        "",
        "`to_canonical` is the first helper you pass more than one thing to. Two ways to find "
        "out what it wants.",
        "",
        "**1 — The first line of the function.**",
        "",
        "```python",
        "def to_canonical(rows: list[dict[str, str]],",
        "                 labels: list[str],",
        "                 column: str = COL_FINAL) -> list[dict[str, str]]:",
        "```",
        "",
        "- Before each colon: what the argument is **called**.",
        "- After each colon: the **kind of data** it expects.",
        "- `= COL_FINAL` means that one already has a value, so you can leave it out.",
        "- After the `->`: **what you get back**.",
        "",
        "**2 — `help(to_canonical)`**, or **Shift+Tab** after typing `to_canonical(`.",
        "",
        "You read these; you never write them.")]
    cells += libs("sheets_canonical")
    cells += [code(
        'help(to_canonical)   # ✏️ change the name to look up any other helper')]
    cells += [code(
        'rows = load_annotation_sheet(SHEET_ID, ROUND)   # re-read your latest round, `Final` filled in',
        'my_gold = to_canonical(rows, LEVELS)            # reads the `Final` column',
        'my_gold[:3]                                     # peek at the first three items')]
    cells += [md(
        "**How does your gold compare with the published gold?** The CEFR-SP labels came from "
        "language-education professionals, keeping only sentences where two of them agreed. "
        "Arase's own experts agreed exactly only 37.6% of the time, so a difference is not "
        "simply an error — but each one needs a look and a reason. "
        "→ interpret this on **step F** (slides).")]
    cells += libs("load_gold", "sheets_compare")
    cells += [code(
        'published = load_gold(GOLD_URL)      # the CEFR-SP labels, for comparison only',
        'compare_to_published(my_gold, published)   # how often you two agree, item by item')]
    cells += [md(
        "**Save your gold set to your Drive** — it belongs in **your** Drive, not the course "
        "repo, and it becomes S6's yardstick. See "
        "[Housing your data in Google Drive](../resources/tools/google-drive-data.md).")]
    cells += [code(
        '# ✏️ Uncomment in Colab to save:',
        '# from google.colab import drive; drive.mount("/content/drive")',
        '# with open("/content/drive/MyDrive/my_gold_day2.json", "w", encoding="utf-8") as f:',
        '#     json.dump(my_gold, f, ensure_ascii=False, indent=2)',
        '# print("saved", len(my_gold), "items")')]
    # Reference appendix: how the per-track template sheets were produced. Framed by what it
    # does (not who runs it) per CLAUDE.md; kept as a NON-executable fenced block so
    # "Runtime → Run all" never re-creates sheets. Because it never runs, the
    # create_annotation_sheet helper is NOT loaded anywhere in this notebook — shipping 40
    # lines a student never calls is what principles §3 rules out.
    cells += [md(
        "::: {.callout-note collapse=\"true\"}",
        "## Reference — how the template sheets were built (you don't run this)",
        "",
        "The template Sheet you copied in step A was generated once, ahead of the session, so "
        "the sample is fixed and reproducible: a `create_annotation_sheet` helper fed by a "
        "**seeded** random draw, one sheet per track. You do **not** run it.",
        "",
        "```python",
        "import random",
        "",
        "N_ITEMS = 20            # how many sentences to annotate",
        "random.seed(42)         # fixed seed = the same sample every time it is drawn",
        "",
        "to_annotate = random.sample(gold, N_ITEMS)   # `gold` = your track's labelled pool",
        "# The sheet gets ids + text only — never the labels — so annotation stays blind:",
        "create_annotation_sheet(\"lda2_day2_cefr\", to_annotate, LEVELS)",
        "```",
        ":::")]

    cells += [submission(
        note=_DAY2_UPLOAD,
        checks=["Your agreement numbers and the annotator-vs-annotator matrix are visible "
                "(step D), for the **last** round you ran.",
                "`my_gold` printed a list of `{id, text, label}` records, and step F's "
                "comparison against the published gold ran (step F)."])]
    save("day2-s5_gold_standard_construction.ipynb", cells)


# =============================================== DAY 2 · S6 (evaluation metrics)
def day2_s6():
    # TWO PASSES over the same CEFR-SP data, in this order (see the S6 slides):
    #   Part A = pass 1 — a BINARY question ("is this sentence advanced?"), with the
    #            metrics built from scratch in ten numbered steps on 12 hand-countable
    #            items SLICED FROM the loaded gold + predictions (not typed by hand),
    #            then checked against scikit-learn on those same 12.
    #   Part B = pass 2 — the real six-class task on all 72, with scikit-learn.
    # SURFACE DIVISION (differs from S5 on purpose): the deck carries BOTH the concept
    # and the implementation — every line of pass-1 code is on a slide next to what it
    # prints — and students type it here. So these cells must PRINT EXACTLY what the
    # slides show; every number is derived from the committed gold + frozen predictions.
    # Cells build UP: loose code that runs and prints first, `def` only once re-use
    # motivates it. Cross-reference BY STEP NUMBER, never by cell/slide number.
    cells = [how_to_use(
        2, "Day 2 · S6 — Evaluation metrics",
        ("Corpus Lab", "build the metrics yourself on one yes/no question: TP/FP/FN/TN → "
                       "confusion matrix → precision, recall, F1 → Cohen's κ."),
        ("Tutorial", "the same job with **scikit-learn** on the real six-level task, plus "
                     "error analysis."),
        note=_DAY2_NOTE.format(
            this="`day2-s5_gold_standard_construction.ipynb`", other="this one"))]

    # ---- Setup + the data both passes run on ----
    cells += [md(
        "## Setup — run this first",
        "",
        "Both parts run on the same data: the **CEFR-SP** gold set (72 sentences, 12 per "
        "level) and one model's answer for each of them.",
        "",
        "::: {.callout-note}",
        "## Today runs on *frozen* predictions — no API key, no live model",
        "On Day 1 the live model's answers changed from run to run, which would get in the way "
        "while you are learning to *measure* quality. So today's predictions are "
        "**pre-computed and committed** to a file. Everyone's precision, recall, F1 and κ come "
        "out **identical every run**: if your number differs from the slide, you have a bug, "
        "not a different model.",
        ":::")]
    s6_libs = ["load_gold", "predictions", "show_2x2", "evaluate", "show_errors"]
    cells += [setup_cell(
        backend=None,          # frozen predictions — Day 2 never calls a model
        lib_names=s6_libs,
        gold_url=CEFR_GOLD_URL,
        gold_comment="CEFR-SP gold set (72 sentences, 12 per level), fetched from the course repo.",
        predictions_url=CEFR_PREDICTIONS_DAY2_URL)]
    # Setup loads only what the next two cells call. `show_2x2` arrives in Part A where
    # it is used, and `evaluate`/`show_errors` in Part B — which also keeps
    # `evaluate` (and the classification_report and cohen_kappa_score inside it) from
    # sitting above the cells where students build precision, recall and κ themselves.
    cells += libs("load_gold", "predictions")
    cells += [md(
        "## Load the data — the pipeline's first step",
        "",
        "Every evaluation starts by **loading the two things it will compare**: the gold "
        "standard and the model's predictions. This is a step in its own right, not part of "
        "the setup — the confusion matrix you build later is made from exactly what you load "
        "here, nothing typed in by hand.",
        "",
        "First, what these files are and how reading one works; then the two loads.")]
    cells += [md(
        "### What a *gold file* actually is",
        "",
        "A gold standard is stored as **JSON** text — the same `{\"id\", \"text\", \"label\"}` "
        "records you met on Day 1, written to a file. `json.loads(...)` turns that text into a "
        "Python **list of dicts** you can index into.")]
    cells += [code(
        'raw = \'[{"id": 1, "text": "Hello.", "label": "A1"}, {"id": 2, "text": "Nevertheless, the findings were inconclusive.", "label": "C1"}]\'',
        'items = json.loads(raw)               # JSON text → list of dicts',
        'print("number of items:", len(items))    # two records in that text',
        'print("first record:", items[0])         # the whole first dict',
        'print("its label:", items[0]["label"])   # index: list by position, dict by key')]
    cells += [md(
        "Files are read and written with **`with open(...) as f:`** — it opens the file, gives "
        "it to you as `f`, and closes it when the block ends. The 🔧 Library cells do this for "
        "you, but you will see it around, so here it is once:")]
    cells += [code(
        'with open("example_gold.json", "w", encoding="utf-8") as f:   # write',
        '    json.dump(items, f)              # the list of dicts becomes JSON text on disk',
        '',
        'with open("example_gold.json", encoding="utf-8") as f:        # read back',
        '    reloaded = json.loads(f.read())  # ...and JSON text becomes a list again',
        'print("read back", len(reloaded), "records — same shape:", reloaded[0])')]
    cells += [md(
        "### Now load the real gold and predictions",
        "",
        "`load_gold(...)` does the read you just saw, but from a URL. Every dataset this week "
        "has the same shape, `{\"id\", \"text\", \"label\"}`.",
        "",
        "Below the gold is the prompt we sent the model, where `{text}` is the slot each "
        "sentence drops into. We ran it **once** over the gold set and committed the answers, "
        "so today you load that frozen file rather than call the model.")]
    cells += [code(
        'gold = load_gold(GOLD_URL)',
        '',
        '# The prompt used to produce the frozen predictions (shown for reference — not run today):',
        'PROMPT = """You are an expert rater of English sentence difficulty using the CEFR scale.',
        'Classify the sentence into exactly one of: A1, A2, B1, B2, C1, C2.',
        'Answer with the level only.',
        '',
        'Sentence: {text}"""',
        '',
        '# Load the pre-computed predictions (same order as `gold`):',
        'predictions = load_predictions(PREDICTIONS_URL)')]

    # ---- Part A · pass 1: build the metrics from scratch, on a binary question ----
    cells += [md(
        "## Part A · Corpus Lab — build the metrics yourself",
        "",
        "In S5 `annotator_agreement()` printed Cohen's κ for you. **Here you build precision, "
        "recall, F1 and κ yourself**, before Part B's `evaluate()` prints them for you again.",
        "",
        "Work in **ten small steps**. Each is on a slide with the code and what it prints; "
        "type it here, run it, and check your output matches before moving on. No imports — "
        "just `for`, `if`, and dictionaries.",
        "",
        "::: {.callout-tip}",
        "## If you fall behind, copy the slide",
        "Every cell below is short and self-contained. Copy the code from the slide, run it, "
        "then read it.",
        ":::")]

    cells += [md(
        "### Step 1 · Collapse to one yes/no question",
        "",
        "CEFR's six levels mean **36** confusion-matrix cells — too many to learn on. So Part A "
        "asks **one** thing:",
        "",
        "> **Is this sentence *advanced* — C1 or C2?**",
        "",
        "`\"yes\"` (C1 or C2) is our **positive class**; everything else is `\"no\"`. Precision "
        "and recall are *always about the positive class*, so choosing it is a decision you "
        "state out loud.",
        "",
        "The 12 rows below are **built from the `gold` and `predictions` you just loaded** — "
        "positions 17 to 28 — with each six-level label collapsed to yes/no. Nothing is typed "
        "in by hand; this is the pipeline that feeds the confusion matrix:")]
    cells += [code(
        'ADVANCED = ["C1", "C2"]      # the levels that count as "yes"',
        '',
        '# Take twelve of the 72 you loaded (ids 17–28) and their predictions. Slicing keeps',
        '# positions 16–27; predictions[16:28] are the answers for those same sentences.',
        'gold_12 = gold[16:28]',
        'pred_12 = predictions[16:28]',
        '',
        '# Pair each gold sentence with its prediction, collapsing both to the yes/no question:',
        'items = []',
        'i = 0                          # position within the twelve, counted up by hand',
        'for g in gold_12:              # g is one gold record: {"id", "text", "label"}',
        '    p = pred_12[i]             # the model\'s answer for that same sentence',
        '    if g["label"] in ADVANCED:   # collapse the gold level to yes/no',
        '        gold_answer = "yes"',
        '    else:',
        '        gold_answer = "no"',
        '    if p in ADVANCED:            # collapse the model\'s answer the same way',
        '        pred_answer = "yes"',
        '    else:',
        '        pred_answer = "no"',
        '    items.append({"id": g["id"], "text": g["text"],',
        '                  "gold": gold_answer, "pred": pred_answer})',
        '    i = i + 1                  # move to the next of the twelve',
        '',
        'print(len(items), "items — id, gold, pred:")',
        'for it in items:                # the twelve, to count by hand with your partner',
        '    print(it["id"], it["gold"], it["pred"])')]
    cells += [md(
        "**Before you write any code, count the four outcomes by hand** — with your partner, "
        "off the twelve rows you just printed. How many **TP** (gold yes, model yes), **FP** (gold no, model "
        "yes), **FN** (gold yes, model no), **TN** (gold no, model no)?",
        "",
        "::: {.callout-note collapse=\"true\"}",
        "## Check your count (open after you've counted)",
        "|              | model **yes** | model **no** |",
        "|--------------|:-------------:|:------------:|",
        "| gold **yes** | **TP = 3**    | **FN = 2**   |",
        "| gold **no**  | **FP = 1**    | **TN = 6**   |",
        "",
        "TP: rows 18, 21, 27 · FN: rows 22, 24 (real C1s the model missed) · FP: row 28 (a B2 "
        "it called advanced) · TN: the other six.",
        "",
        "**Everything else in Part A is arithmetic on these four numbers.**",
        ":::")]

    cells += [md(
        "### Step 2 · Ask one item",
        "",
        "A metric never looks at more than **one item and two labels** at a time. Start there.")]
    cells += [code(
        'item = items[0]                     # the first of the 12 rows',
        'print(item["gold"], item["pred"])   # its gold answer, then the model\'s')]
    cells += [md(
        "Row 17: the gold says not advanced, and the model agrees.",
        "",
        "Now ask the first of the four questions — *is this a true positive?* That means "
        "**both** labels are `\"yes\"`:")]
    cells += [code(
        '# `and` means BOTH sides have to be true:',
        'if item["gold"] == "yes" and item["pred"] == "yes":',
        '    print("TP")     # only runs when both are "yes"')]
    cells += [md(
        "**Nothing printed.** That isn't a bug — it's the honest answer: row 17 is not a TP, "
        "and an `if` with no `else` stays silent when its condition is false.",
        "",
        "One `if` can only ever answer **one** of the four questions. We need all four.")]

    cells += [md(
        "### Step 3 · The four branches",
        "",
        "Four cells in the table → four branches, **in the same order**. `elif` means *\"only "
        "if none of the above matched\"*, so the branches are checked top to bottom and "
        "**exactly one** runs — every item lands in exactly one cell. The final `else` needs no "
        "condition: if it isn't TP, FP or FN, it can only be TN.",
        "",
        "✏️ **Change the index and re-run** to see each branch fire.")]
    cells += [code(
        'item = items[0]      # ✏️ try 1 (a TP), 5 (an FN), 11 (an FP)',
        'print(item["gold"], item["pred"])',
        '',
        '# checked top to bottom; the FIRST match wins, so exactly one branch runs:',
        'if item["gold"] == "yes" and item["pred"] == "yes":',
        '    print("TP")      # advanced, and the model agreed',
        'elif item["gold"] == "no" and item["pred"] == "yes":',
        '    print("FP")      # a false alarm',
        'elif item["gold"] == "yes" and item["pred"] == "no":',
        '    print("FN")      # a real one, missed',
        'else:',
        '    print("TN")      # not advanced, left alone')]

    cells += [md(
        "### Step 4 · Make it a function",
        "",
        "You are about to ask that same question of all 12 rows, so **name it once**. Two "
        "changes from step 3: it is wrapped in `def`, and every `print` became a **`return`**.",
        "",
        "`print` puts a value on the screen and then it is gone; `return` hands the value back "
        "to whoever called the function, so you can **keep it, store it, count it** — which is "
        "what step 5 needs.")]
    cells += [code(
        'def outcome(gold_label, pred_label):',
        '    """Which of the four cells does this one item land in?"""',
        '    if gold_label == "yes" and pred_label == "yes":',
        '        return "TP"      # `return` hands the answer back, instead of printing it',
        '    elif gold_label == "no" and pred_label == "yes":',
        '        return "FP"',
        '    elif gold_label == "yes" and pred_label == "no":',
        '        return "FN"',
        '    else:',
        '        return "TN"',
        '',
        '',
        'print(outcome("yes", "no"))     # gold said advanced, model said no → a miss')]
    cells += [md(
        "::: {.callout-tip}",
        "## Test it by hand before you trust it",
        "`outcome(\"yes\", \"no\")` → **FN** ✓. Try all four combinations against the table in "
        "step 1. A function you haven't checked is a guess.",
        ":::")]

    cells += [md(
        "### Step 5 · Loop, and store every decision",
        "",
        "Run that function over all 12 rows and **keep** the answers — the same *\"build a "
        "list in a loop\"* pattern you wrote on Day 1.")]
    cells += [code(
        'decisions = []                     # start empty; the loop fills it',
        'for item in items:                 # one pass per row of the table',
        '    decisions.append(outcome(item["gold"], item["pred"]))   # add its verdict',
        '',
        'print(decisions)                   # 12 verdicts, in the table\'s order')]
    cells += [md(
        "Twelve items in, twelve verdicts out, **in the same order as the table**. Position 6 "
        "is `'FN'` — row 22, the racing-bicycle sentence the model missed.",
        "",
        "We could have counted as we went, but a metric is only a summary and `decisions` is "
        "the thing being summarised. Every `'FN'` and `'FP'` in it points at a specific "
        "sentence you can read and argue about.")]

    cells += [md(
        "### Step 6 · Tally the verdicts",
        "",
        "This is Day 1's `count_labels` exercise, run on a new list. `tally.get(d, 0)` means "
        "*\"how many so far — and if you've never seen this one, start from 0\"*; without the "
        "`.get`, the very first `'TN'` would crash, because `tally[\"TN\"]` doesn't exist yet.")]
    cells += [code(
        'tally = {}                         # a dict: verdict -> how many times',
        'for d in decisions:                # d is "TP", "FP", "FN" or "TN"',
        '    tally[d] = tally.get(d, 0) + 1   # count so far (0 if new), plus one',
        '',
        'print(tally)')]
    cells += [md(
        "**Compare with what you counted by hand in step 1: TP = 3, FP = 1, FN = 2, TN = 6.** "
        "They match — your code and your eyes agree.")]

    cells += [md(
        "### Step 7 · The confusion matrix",
        "",
        "A confusion matrix is **not a new calculation**. It is those same four numbers put "
        "in a square, so you can *see* where the errors went.",
        "",
        "`show_2x2` only prints — the arithmetic was all yours.")]
    cells += libs("show_2x2")
    cells += [code('show_2x2(tally)')]
    cells += [md(
        "- The **diagonal** (3 and 6) is everything the model got right — 9 of 12.",
        "- The **off-diagonal** (2 and 1) is everything it got wrong, **split by direction**: "
        "two misses and one false alarm.",
        "",
        "Now the margins — you need them for κ in step 9:",
        "",
        "|              | model **yes** | model **no** | **total** |",
        "|--------------|:-------------:|:------------:|:---------:|",
        "| gold **yes** | 3 | 2 | **5** |",
        "| gold **no**  | 1 | 6 | **7** |",
        "| **total**    | **4** | **8** | **12** |",
        "",
        "The gold set calls 5 sentences advanced; the model calls only **4**. It uses the "
        "positive label slightly less often than it should — that pattern comes back in Part "
        "B.")]

    cells += [md(
        "### Step 8 · Precision, recall, F1",
        "",
        "**Precision** — *of everything the model CALLED advanced, how much really was?*",
        "",
        "$$P = \\frac{TP}{TP + FP}$$",
        "",
        "Numbers first, so you can check it on paper, then the same thing read off the tally, "
        "so it survives a change of data:")]
    cells += [code(
        'print(3 / (3 + 1))                                  # TP / (TP + FP), by hand',
        'print(tally["TP"] / (tally["TP"] + tally["FP"]))    # the same, from the tally')]
    cells += [md(
        "Of the 4 sentences the model called advanced, 3 really were. **Precision = 0.75.**",
        "",
        "Now as a function, with a guard: if a model never predicts the positive class, "
        "`TP + FP` is 0 and Python raises `ZeroDivisionError`. Returning `0.0` says it earned "
        "no credit, which is the honest reading. **Every metric you write today gets this "
        "guard.**")]
    cells += [code(
        'def precision(tally):',
        '    """Of everything CALLED advanced, how much really was?  TP / (TP + FP)"""',
        '    tp = tally.get("TP", 0)      # .get(..., 0) so a missing count reads as 0',
        '    fp = tally.get("FP", 0)',
        '    if tp + fp == 0:             # the model never said "yes" at all',
        '        return 0.0               # no credit earned — and no division by zero',
        '    return tp / (tp + fp)        # everything it got right, over everything it claimed',
        '',
        '',
        'print(round(precision(tally), 3))   # round to 3 decimal places')]
    cells += [md(
        "**Recall** asks the *other* question — *of everything that TRULY was advanced, how "
        "much did we catch?*",
        "",
        "$$R = \\frac{TP}{TP + FN}$$",
        "",
        "✏️ Same shape as `precision`, with **one** real change: `FN` instead of `FP`.")]
    cells += [code(
        'def recall(tally):',
        '    """Of everything that TRULY was advanced, how much did we find?"""',
        '    tp = tally.get("TP", 0)',
        '    fn = tally.get("FN", 0)       # ← the only real change',
        '    if tp + fn == 0:              # nothing was truly advanced — nothing to find',
        '        return 0.0',
        '    return tp / (tp + fn)         # what it found, over everything there was to find',
        '',
        '',
        'print(round(recall(tally), 3))')]
    cells += [md(
        "Three of the five genuinely advanced sentences were found. **Recall = 0.60.**",
        "",
        "Precision and recall pull against each other: flag everything and recall hits 1.0 "
        "while precision collapses. **F1** is their harmonic mean, so a high score cannot "
        "cover for a low one:",
        "",
        "$$F_1 = 2 \\cdot \\frac{P \\cdot R}{P + R}$$")]
    cells += [code(
        'def f1(tally):',
        '    """Harmonic mean of precision and recall."""',
        '    p = precision(tally)         # reuse the function you just wrote',
        '    r = recall(tally)            # ...and the other one',
        '    if p + r == 0:               # both zero — nothing to average',
        '        return 0.0',
        '    return 2 * p * r / (p + r)   # harmonic mean: a low score drags it down',
        '',
        '',
        'print(round(precision(tally), 3), round(recall(tally), 3), round(f1(tally), 3))')]
    cells += [md(
        "::: {.callout-important}",
        "## The gap between P and R describes the model",
        "**Precision 0.75 > recall 0.60** → this model is **conservative**: when it commits "
        "it is usually right, but it labels real C1s as B2.",
        "",
        "*Which error can you live with?* is a **research design** question. Screening for a "
        "C1 reading list, a miss is expensive — favour recall. Claiming which sentences are "
        "advanced, a false alarm is expensive — favour precision.",
        ":::")]

    cells += [md(
        "### Step 9 · Cohen's κ",
        "",
        "Start with the easy number — **observed agreement**, the diagonal over the total:")]
    cells += [code(
        'n = tally["TP"] + tally["FP"] + tally["FN"] + tally["TN"]   # all 12 items',
        'p_o = (tally["TP"] + tally["TN"]) / n   # the diagonal (both agreed), over the total',
        'print(round(p_o, 3))')]
    cells += [md(
        "Gold and model agree on 9 of 12. But **a model that answered \"no\" to everything** "
        "would score 7/12 while knowing nothing — raw agreement flatters a rater who just uses "
        "the commonest label.",
        "",
        "So subtract the agreement you would get **by luck**. $p_e$ multiplies the two raters' "
        "own rates, label by label — the row and column totals from step 7:")]
    cells += [code(
        '# each line: how often GOLD says it × how often the MODEL says it = agreement by luck',
        'p_yes = ((tally["TP"] + tally["FN"]) / n) * ((tally["TP"] + tally["FP"]) / n)',
        'p_no  = ((tally["FP"] + tally["TN"]) / n) * ((tally["FN"] + tally["TN"]) / n)',
        'p_e   = p_yes + p_no          # luck on "yes" plus luck on "no"',
        'print(round(p_yes, 3), round(p_no, 3), round(p_e, 3))')]
    cells += [md(
        "- `p_yes`: gold says yes **5/12** × model says yes **4/12** = 0.139",
        "- `p_no`: gold says no **7/12** × model says no **8/12** = 0.389",
        "",
        "**More than half** the agreement we observed (0.75) was available by luck alone. κ "
        "asks how much of what luck *couldn't* explain the two of them actually achieved:",
        "",
        "$$\\kappa = \\frac{p_o - p_e}{1 - p_e}$$")]
    cells += [code(
        '# what they beat luck by (p_o - p_e), over how much was left to beat (1 - p_e):',
        'print(round((p_o - p_e) / (1 - p_e), 3))')]
    cells += [md(
        "**75% agreement → κ = 0.47** — \"moderate\" (Landis & Koch) or \"weak\" (McHugh). "
        "The same gap S4 showed you (80% → κ ≈ 0.52), now computed by your own code.",
        "",
        "Wrap it up so you can reuse it:")]
    cells += [code(
        'def kappa(tally):',
        '    """Agreement corrected for chance: (p_o - p_e) / (1 - p_e)."""',
        '    n = tally["TP"] + tally["FP"] + tally["FN"] + tally["TN"]   # every item',
        '    p_o = (tally["TP"] + tally["TN"]) / n     # agreement we actually observed',
        '    p_yes = ((tally["TP"] + tally["FN"]) / n) * ((tally["TP"] + tally["FP"]) / n)',
        '    p_no = ((tally["FP"] + tally["TN"]) / n) * ((tally["FN"] + tally["TN"]) / n)',
        '    p_e = p_yes + p_no                        # agreement luck alone would give',
        '    if 1 - p_e == 0:                          # luck already explains everything',
        '        return 0.0',
        '    return (p_o - p_e) / (1 - p_e)            # how much of the rest they achieved',
        '',
        '',
        'print(round(kappa(tally), 3))')]
    cells += [md(
        "::: {.callout-tip}",
        "## This is yesterday's function",
        "Nothing in `kappa()` knows whether the second column came from **your partner** or "
        "from **a model**. That is why S5's agreement number and today's evaluation number "
        "are the same statistic: **κ measures two label columns, whoever produced them.**",
        ":::")]
    cells += [md(
        "::: {.callout-important}",
        "## Report both numbers",
        "Two numbers on the same twelve items: raw agreement **0.75**, κ **0.47**. A κ of "
        "0.47 under 75% agreement says something different from a κ of 0.47 under 95% — so "
        "report both.",
        "",
        "Which κ joins the percentage follows from your design: unordered labels → "
        "`cohen_kappa_score(a, b)`; labels on a scale → the weighted one as well; three or "
        "more coders → Fleiss' κ.",
        ":::")]

    cells += [md(
        "### Step 10 · Check yourself against scikit-learn",
        "",
        "You built a confusion matrix and four metrics by hand. Before trusting them, **check "
        "them against `scikit-learn`** on the same twelve items: the library builds the same "
        "2×2 and computes the same numbers, and if yours differ, you have a bug to find. This "
        "is the only place `scikit-learn` enters Part A — as a marker for work you already "
        "did.")]
    cells += [code(
        '#@title 🔎 Self-check against scikit-learn — run me { display-mode: "form" }',
        "# Helper — you don't need to read this. Run it and move on.",
        'from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix',
        '',
        '### Step 1: the same 12 items as two plain lists — the shape sklearn wants ###',
        'y_gold = []',
        'y_pred = []',
        'for item in items:               # the twelve you built and tallied by hand',
        '    y_gold.append(item["gold"])',
        '    y_pred.append(item["pred"])',
        '',
        '### Step 2: a small checker — is your number the same as sklearn\'s? ###',
        'TOL, results = 1e-9, []      # TOL: how close counts as "the same"',
        'def _chk(name: str, got: float, exp: float) -> None:',
        '    """Print whether your number matches sklearn\'s, and remember the answer."""',
        '    ok = abs(got - exp) < TOL   # compare sizes, not exact bits: floats wobble',
        '    results.append(ok)',
        '    print(("✅" if ok else "❌"), f"{name:<14} yours={got:.6f}  sklearn={exp:.6f}")',
        '',
        '### Step 3: first the confusion matrix — do your four counts match? ###',
        'cm = confusion_matrix(y_gold, y_pred, labels=["yes", "no"])   # rows = gold, cols = pred',
        'sk = {"TP": cm[0][0], "FN": cm[0][1],    # name sklearn\'s four cells the way you did',
        '      "FP": cm[1][0], "TN": cm[1][1]}',
        'counts_ok = all(tally.get(k, 0) == sk[k] for k in ["TP", "FP", "FN", "TN"])',
        'results.append(counts_ok)',
        'yours = f"{tally.get(\'TP\',0)}/{tally.get(\'FP\',0)}/{tally.get(\'FN\',0)}/{tally.get(\'TN\',0)}"',
        'theirs = f"{sk[\'TP\']}/{sk[\'FP\']}/{sk[\'FN\']}/{sk[\'TN\']}"',
        'print(("✅" if counts_ok else "❌"), f"TP/FP/FN/TN     yours={yours}  sklearn={theirs}")',
        '',
        '### Step 4: then the four metrics you wrote ###',
        '_chk("precision", precision(tally),',
        '     precision_score(y_gold, y_pred, pos_label="yes", zero_division=0))',
        '_chk("recall", recall(tally),',
        '     recall_score(y_gold, y_pred, pos_label="yes", zero_division=0))',
        '_chk("f1", f1(tally),',
        '     f1_score(y_gold, y_pred, pos_label="yes", zero_division=0))',
        '_chk("cohen_kappa", kappa(tally), cohen_kappa_score(y_gold, y_pred))',
        '',
        '### Step 5: one overall verdict ###',
        'print("-" * 47)              # a divider line, 47 dashes long',
        'print(f"All {len(results)} checks passed ✅  — your confusion matrix and metrics match scikit-learn."',
        '      if all(results) else',
        '      f"{results.count(False)} of {len(results)} checks FAILED — fix and re-run.")')]
    cells += [md(
        "::: {.callout-important}",
        "## This is the point of Part A",
        "`sklearn` is not doing anything you cannot do. It is doing **exactly what you just "
        "wrote** — faster, and for every class at once. **Twelve items is enough to learn the "
        "mechanics, never enough to judge a model** — so in Part B you load the full ordinal "
        "CEFR labels and let `scikit-learn` score all 72. From here on, when a report prints "
        "`0.36`, you know precisely which counts produced it.",
        ":::")]
    cells += [md(
        "### The names you just checked yourself against",
        "",
        "These are the real scikit-learn names, and you call them directly from here on:",
        "",
        "| The call | What it gives you | Where it comes back |",
        "|---|---|---|",
        "| `precision_score(y, p, pos_label=…)` | precision for one positive class | anywhere you have a yes/no question |",
        "| `recall_score(y, p, pos_label=…)` | recall for that class | as above |",
        "| `f1_score(y, p, average=…)` | one F1 number over all classes | your headline number |",
        "| `classification_report(y, p, labels=…)` | precision, recall and F1 for **every** class | your per-class table |",
        "| `confusion_matrix(y, p, labels=…)` | which classes get mixed up with which | coder vs coder, and gold vs model |",
        "| `cohen_kappa_score(y, p)` | agreement corrected for chance | coder vs coder, and gold vs model |",
        "| `cohen_kappa_score(y, p, weights=\"quadratic\")` | the same, with a near miss counting as a smaller error | only when your labels are a scale |",
        "",
        "`y` is the gold labels as a plain list; `p` is the other column — your partner's "
        "labels, or the model's answers.")]

    # ---- Part B · pass 2: the real six-class task, with scikit-learn ----
    cells += [md(
        "## Part B · Tutorial — the same job, six classes, with scikit-learn",
        "",
        "Drop the yes/no simplification. The real task is the **full ordinal CEFR scale**: "
        "**A1 · A2 · B1 · B2 · C1 · C2**.",
        "",
        "You do not load anything new — the `gold` and `predictions` from the start of the "
        "notebook already carry the full level. Part A only *collapsed* them to yes/no; here "
        "you use them as they are:")]
    cells += [code(
        '# The same items, now with their full CEFR level instead of yes/no:',
        'print("full gold label:", gold[0]["label"], " full prediction:", predictions[0])')]
    cells += [md(
        "- **4 cells → 36.** Counting by hand stops being reasonable.",
        "- Six classes give you **six** precisions, **six** recalls, **six** F1s.",
        "- To score `C1`, treat **`C1` as \"yes\" and the other five as \"no\"** — Part A, run "
        "six times. That is **one-vs-rest**, and it is all `classification_report` does.",
        "",
        "`ordered=True` tells `evaluate` the labels sit on a **scale**, so it also reports "
        "quadratic weighted κ.")]
    cells += libs("evaluate", "show_errors")
    cells += [code(
        '# ordered=True: the six levels sit on a scale, so also report weighted κ',
        'evaluate(gold, predictions, ordered=True)')]
    cells += [md(
        "### Reading the report",
        "",
        "- Every **row** is one Part-A run: for `C1`, TP/FP/FN/TN with C1 as the positive class.",
        "- **`support`** is how many gold items that class has — 12 each, by design.",
        "- **`macro avg`** is the plain average of the six F1s: every class counts equally, "
        "however rare.",
        "",
        "**Overall accuracy is about 39%** — but look at *how* it is wrong. Roughly **97% of "
        "its answers are within one level** of the gold label. It has the right idea and "
        "imprecise thresholds, which no accuracy figure can tell apart from not understanding "
        "the task.",
        "",
        "### One number, three different questions",
        "",
        "The report prints two other averages beside `macro avg`. On an uneven label set they "
        "disagree:")]
    cells += [code(
        'from sklearn.metrics import f1_score',
        '',
        '# The same predictions, scored three ways.',
        'y_gold = []                        # the gold column, as a plain list',
        'for item in gold:',
        '    y_gold.append(item["label"])',
        '',
        'for how in ["macro", "micro", "weighted"]:',
        '    score = f1_score(y_gold, predictions, average=how, zero_division=0)',
        '    print(how, round(score, 3))')]
    cells += [md(
        "- **macro** — every *class* counts the same, however rare.",
        "- **micro** — every *item* counts the same, so common classes dominate.",
        "- **weighted** — per-class F1 averaged by how common each class is: between the two.",
        "",
        "The three land close together here because this gold set is balanced, 12 per level. "
        "**On an unbalanced set they can differ by a lot.**",
        "",
        "::: {.callout-important}",
        "## Pick the question before you see the answers",
        "Which one you report follows from what you are claiming, and you can settle it "
        "before any number exists. A reader cannot detect that you ran all three and reported "
        "the highest.",
        ":::")]
    cells += [md(
        "### Read the matrix *down the columns*",
        "",
        "Rows are gold, so *rows* tell you what happened to each true level. Read **down the "
        "columns** instead — how often the model *says* each level. The gold set is balanced, "
        "12 per level, so an unbiased rater would use each label about 12 times.",
        "",
        "This one says **A2 twenty times**, **A1 four times**, and **C2 exactly once** in 72 "
        "chances: everything is squeezed toward the **middle of the scale**. It is your Part-A "
        "finding again — precision ran ahead of recall (0.75 vs 0.60 on your twelve), because "
        "it under-uses the top of the scale.")]
    cells += [md(
        "### Two κ values, same predictions",
        "",
        "Plain **κ = 0.27**, because plain κ treats **A1 → A2 as exactly as wrong as "
        "A1 → C2**. Quadratic **weighted κ = 0.85**, because CEFR levels are **ordinal** and "
        "a near miss should hurt less.",
        "",
        "::: {.callout-important}",
        "## Report the one that matches your labels",
        "Same predictions: 0.27 or 0.85, depending on a single argument. **Ordered labels → "
        "weighted κ. Unordered categories → plain κ.** State which you used and why. *(Arase "
        "et al. reported weighted κ = .628 on this task.)*",
        ":::")]
    cells += [md(
        "### Error analysis — the model's fault, or the scheme's?",
        "",
        "There are 44 misses — too many to read one by one. Skim a dozen, then look at the "
        "rows where the gold label is **C2** or **A1**, where this model disagrees most often.",
        "",
        "For each miss, ask: is the **gold** defensible, or is this a genuinely borderline "
        "sentence? Would **you and your partner** have agreed on it? *\"Is the disagreement "
        "the model's fault or the scheme's?\"* is the central question of annotation work.")]
    cells += [code(
        'errors = show_errors(gold, predictions)   # a table of every item it got wrong',
        'errors.head(15)     # ...or errors[errors["gold"] == "C2"] to see the hard end')]
    cells += [md(
        "#### Four words for four different findings",
        "",
        "*\"The model got it wrong\"* covers four situations that call for four different "
        "responses. These are the words your final project asks for:",
        "",
        "| Word | What it means | What you would do about it |",
        "|---|---|---|",
        "| **`model`** | the label is clear, two coders would agree at once, and the model still missed it | nothing — this is the model's limit |",
        "| **`scheme`** | the item is genuinely borderline *under your scheme*, and you know which ones those are because you argued about them | rewrite the boundary rule |",
        "| **`wording`** | the label *name* misleads. `Gap` may read to a model as \"missing data\" | one more prompt round could fix this |",
        "| **`ambiguous`** | the item itself is unclear in a way no scheme would settle | say so, and move on |",
        "",
        "`scheme` and `wording` are the pair to be careful about: **a prompt can reach one of "
        "them and not the other.**",
        "",
        "**Now do it, out loud, with your partner.** Pick two or three rows from the table "
        "above, read the actual sentence, and say which of the four words fits and why.",
        "",
        "Give a reason, not a verdict. *\"model — wrong\"* is not worth saying; *\"model — "
        "this is about as plainly C1 as a sentence gets, and it said A2\"* is.")]
    cells += [md(
        "#### The cross-reference: where did *you two* disagree?",
        "",
        "Here is the join that makes `scheme` an evidenced claim rather than an impression. "
        "You already have a list of items your S5 partner and you labelled differently. If "
        "the model's errors land on those same items, what you have measured is a fuzzy "
        "boundary in your scheme — not a stupid model.",
        "",
        "Type in a few ids from your own `disagreements(rows)` table in S5 and see:")]
    cells += [code(
        '# ✏️ ids from YOUR S5 disagreement table — the rows you two argued about.',
        'DISAGREED_IDS = [17, 23, 41]',
        '',
        'both = []',
        'for row_id in errors["id"]:          # every item the model got wrong',
        '    if row_id in DISAGREED_IDS:      # ...that you two also disagreed about',
        '        both.append(row_id)',
        '',
        'print(len(both), "of", len(errors), "model errors are items you argued about too:", both)')]
    cells += [md(
        "A **high** overlap says the scheme is the problem. A **low** one says the model is "
        "missing things two humans found easy — a different finding, and just as reportable. "
        "In the project this is one call, `errors_on_disagreed(errors, disagreed)`.")]
    cells += [md(
        "::: {.callout-note}",
        "## The question you ask decides the error you can see",
        "Look back at rows 19, 23 and 25 in step 1 — the three obituary sentences. Under Part "
        "A's yes/no question the model got all three **right**. In six classes it called every "
        "one of them A2 instead of A1. Same predictions, same gold; a different question made "
        "a different error visible.",
        ":::")]

    cells += [submission(note=_DAY2_UPLOAD)]
    save("day2-s6_evaluation_metrics.ipynb", cells)


# ============================================================ DAY 3
def day3():
    cells = [how_to_use(
        3, "Day 3 · Prompt design & iteration",
        ("Tutorial", "improve a prompt through zero-shot → few-shot → chain-of-thought, "
                     "comparing macro-F1 at each step."),
        ("Corpus Lab", "your own prompt-iteration study: find the model's worst class, "
                       "predict what a change will do, then make it and check."))]

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
        "Record the macro-F1 (the `macro avg` row of `evaluate`) after each run, so you can say "
        "which technique helped.")]
    cells += [md(
        "::: {.callout-important}",
        "## From today you run the model yourself — you need a free API key",
        "From Day 3 on you call the model live, so the notebook switches to the **Gemini "
        "API**. Get a free key and add it to Colab **Secrets** as `GEMINI_API_KEY` — one-time, "
        "~2 minutes, no install. Full steps: "
        "[Get a free Gemini API key](../resources/tools/gemini-api-key.md).",
        "",
        "When the setup cell prints `LLM backend: Gemini API (...)` you're set. If it still "
        "says `Colab Gemini`, your secret isn't set or its notebook-access toggle is off. Rate "
        "limits are handled for you, and explained at the end of Part A.",
        ":::")]
    cells += [md("### Setup — run this first")]
    day3_libs = ["load_gold", "run_prompt", "evaluate", "show_errors"]
    cells += [setup_cell(
        backend="api",         # Day 3 on: reproducible Gemini API (key), colab.ai fallback
        lib_names=day3_libs,
        gold_url=CEFR_GOLD_URL,
        gold_comment="CEFR-SP gold set (72 sentences, 12 per level), fetched from the course repo.",
        val_url=CEFR_VAL_URL)]

    # ---- staged walkthrough of the rate-limit guard already running in Setup.
    # Built here, but appended at the END of Part A: nothing in the tutorial depends
    # on it, and putting it between Setup and the first prompt made it four of the
    # nine cells a student ran before seeing any result. By the end of Part A they
    # have made ~150 calls, which is the point at which the guard is worth reading
    # about — and it is Part B where they start writing loops of their own.
    rate_limit_cells = [md(
        "## Why your calls didn't crash the lab — two different clocks",
        "",
        "The free tier limits you in **two independent ways**, on two different clocks:",
        "",
        "- **RPM** — requests per *minute*: how fast you're allowed to call.",
        "- **RPD** — requests per *day*: how many calls you're allowed in total, today.",
        "",
        "A plain `for` loop over 72 sentences can pass the RPM limit in the first few seconds, "
        "long before it has used much of the day's RPD budget. While building this course, a "
        "loop tripped a 15-per-minute cap after 16 calls, with only 126 of that day's 500 "
        "used. The fix is to go slower, and to know which limit you hit.",
        "",
        "The Setup cell's guard does this, and the rest of this section walks through it.")]

    rate_limit_cells += [md(
        "### Piece 1 — always leave a gap between calls (pacing)",
        "",
        "Never call the model faster than the limit allows. At 15 calls per minute that is one "
        "call every `60 / 15 = 4` seconds, so before each call, check how long it has been "
        "since the last one and wait out the difference.",
        "",
        "That means the function has to **remember** when the last call happened. The `global` "
        "keyword tells Python to keep one variable and share it across every call.",
        "",
        "Try it below — no model, no internet, just pacing:")]
    rate_limit_cells += [code(
        'import time',
        '',
        '### Step 1: two things to remember — when we last called, and how long to wait ###',
        '_demo_last_call = 0.0        # remembered BETWEEN calls, thanks to `global`',
        'DEMO_INTERVAL = 2            # seconds (the real guard uses 4.4s or 13.2s)',
        '',
        '### Step 2: before each call, wait out whatever time is still owed ###',
        'def wait_your_turn() -> None:',
        '    """Wait out whatever time is still owed, then say we are calling."""',
        '    global _demo_last_call   # "remember this one, and share it across calls"',
        '    wait = DEMO_INTERVAL - (time.monotonic() - _demo_last_call)   # time still owed',
        '    if wait > 0:                                     # too soon — sit it out',
        '        print(f"  waiting {wait:.1f}s so we don\'t call too often...")',
        '        time.sleep(wait)',
        '    _demo_last_call = time.monotonic()               # note when this call happened',
        '    print("  → calling now!")',
        '',
        '### Step 3: three calls in a row — watch the gap appear between them ###',
        'for i in range(3):',
        '    wait_your_turn()')]

    rate_limit_cells += [md(
        "### Piece 2 — if you still get told to slow down, wait and try again",
        "",
        "Pacing alone isn't enough: the server can still say \"too fast, try again later\". "
        "What to do depends on the kind of failure, which the error message tells you:",
        "",
        "- **Not rate-limit shaped** (a typo, a dropped connection) — a real bug. Don't retry.",
        "- **Per-minute limit** — wait and try again; it refills every minute.",
        "- **Per-day limit** — retrying is pointless. The guard gives up at once with a clear "
        "message.",
        "",
        "A demo — no model, just the `try`/`except` shape, retrying until it works:")]
    rate_limit_cells += [code(
        '### Step 1: a stand-in for the real model — it fails twice, then works ###',
        'attempt_count = 0            # how many times we have called it so far',
        '',
        'def flaky_call() -> str:',
        '    """Pretends to fail twice, then succeeds — like a real rate-limited call."""',
        '    global attempt_count     # keep the count between calls',
        '    attempt_count += 1',
        '    if attempt_count <= 2:                                   # the first two tries',
        '        raise Exception("429 rate limit — please slow down")  # ...blow up',
        '    return "success!"                                        # the third works',
        '',
        '### Step 2: try it, and if it breaks, go round again instead of crashing ###',
        'for attempt in range(3):     # up to three goes',
        '    try:',
        '        result = flaky_call()',
        '        print("Got:", result)',
        '        break                # it worked — stop looping',
        '    except Exception as error:   # it broke — `error` holds the message',
        '        print(f"  attempt {attempt+1} failed ({error}) — trying again...")')]

    rate_limit_cells += [md(
        "### Putting the two pieces together",
        "",
        "Piece 1 plus piece 2 is what is inside `generate_text` in the Setup cell above, and "
        "it protects every Corpus Lab loop you write from here on.",
        "",
        "A fuller version, which also remembers past answers so you never pay for the same "
        "prompt twice, is in "
        "[`resources/extra/handling-rate-limits.ipynb`](../resources/extra/handling-rate-limits.ipynb).")]

    # Part A calls these three; `show_errors` waits until Part B, where the error analysis
    # starts, so this cell stays about running a prompt and scoring it.
    cells += libs("load_gold", "run_prompt", "evaluate")

    cells += [md(
        "## Two sets, two jobs",
        "",
        "From here you work with **two** files, and mixing them up is the single easiest way "
        "to report a number that isn't real.",
        "",
        "| File | Size | What it is for |",
        "|---|:--:|---|",
        "| `val` | 24 | **Tune on this.** Every prompt you try gets scored here. |",
        "| `gold` | 72 | **Report on this.** Touched once, at the very end. |",
        "",
        "If you try five prompts on the 72 sentences and keep the highest score, that score no "
        "longer estimates how the prompt does on *new* sentences: you picked it *because* it "
        "suited those 72. Tuning somewhere else and reporting once is what keeps the final "
        "figure honest. This is the split S7 introduced.")]
    cells += [code(
        'val  = load_gold(VAL_URL)    # 24 sentences — tune every prompt against these',
        'gold = load_gold(GOLD_URL)   # 72 sentences — held out; scored ONCE at the end',
        'print(len(val), "validation items ·", len(gold), "held-out test items")')]

    cells += [md(
        "### Iteration 0 — zero-shot   ✏️ YOU EDIT",
        "",
        "Just describe the task. This is your baseline; note its macro-F1.")]
    cells += [code(
        '# ✏️ everything between the triple quotes is the prompt — edit it freely.',
        '# `{text}` is the slot each sentence gets dropped into; keep it.',
        'PROMPT_ZERO = """You are an expert rater of English sentence difficulty using the CEFR scale.',
        'Classify the sentence into exactly one of: A1, A2, B1, B2, C1, C2.',
        'Answer with the level only.',
        '',
        'Sentence: {text}"""',
        '',
        'pred_zero = run_prompt(PROMPT_ZERO, val)   # ask the model about the 24 validation items',
        'evaluate(val, pred_zero, ordered=True)     # score it — note the macro-F1')]

    cells += [md(
        "#### Two settings decide whether that number is repeatable",
        "",
        "The Setup cell connected to the model with these two arguments:",
        "",
        "```python",
        "cfg = types.GenerateContentConfig(temperature=0, seed=42)",
        "```",
        "",
        "- **`temperature`** is how much the model is allowed to vary. At `0` it takes its "
        "most likely answer every time. Higher values are useful for writing and unhelpful "
        "when you are measuring something.",
        "- **`seed`** fixes the randomness that is left, so a repeat of the same call starts "
        "from the same place.",
        "",
        "Run the same prompt over the same five items twice and see whether the answers "
        "match:")]
    cells += [code(
        'first  = run_prompt(PROMPT_ZERO, val[:5])   # five items, to keep this cheap',
        'second = run_prompt(PROMPT_ZERO, val[:5])   # the same five, the same prompt',
        '',
        'print("first run: ", first)',
        'print("second run:", second)',
        'print("identical?", first == second)   # two lists are == when every item matches')]
    cells += [md(
        "`True` is what `temperature=0` is for. On the keyless Colab backend you may see "
        "fewer, because `colab.ai` exposes neither setting — that is the Day-1 behaviour, and "
        "why this course asks for a key from today.",
        "",
        "::: {.callout-note}",
        "## Best-effort, not guaranteed",
        "Even at `temperature=0` a hosted model can change its answer: the provider updates "
        "the model, or batches your request differently. So **save the run to a file** and "
        "report from the file, not from what is on screen.",
        ":::")]

    cells += [md(
        "### Iteration 1 — few-shot   ✏️ YOU EDIT",
        "",
        "Add a few **labeled examples** so the model can pattern-match. The ones below are "
        "hand-written; write your own if you want more, but never take one from `val` or "
        "`gold`, or you are showing the model the answers to its own test.")]
    cells += [code(
        '# ✏️ same prompt as before, plus labelled examples. Add, remove or reword them —',
        '# but never use a sentence from `gold`, or you are testing on your own answers.',
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
        'pred_few = run_prompt(PROMPT_FEWSHOT, val)   # same 24 sentences, new prompt',
        'evaluate(val, pred_few, ordered=True)        # did macro-F1 move?')]
    cells += [md(
        "#### *Which* examples? That is the decision, not whether to use any",
        "",
        "The four above are one choice out of many. Two strategies pull in opposite "
        "directions:",
        "",
        "- **The clearest case of each label.** Safe, and it may teach nothing about the "
        "boundary you keep losing items on.",
        "- **The hardest cases, near a boundary.** Riskier: a borderline example read the "
        "wrong way drags its neighbours with it.",
        "",
        "**Predict first, then find out.** Say which you think will help here, swap two "
        "examples for that kind, and re-run.",
        "",
        "Two rules either way: **never take an example from `val` or `gold`**, and **cover "
        "every label** if you can, or the ones you left out get under-predicted.")]

    cells += [md(
        "### Iteration 2 — chain-of-thought (CoT)   ✏️ YOU EDIT",
        "",
        "Ask the model to **reason first, then answer**. Giving it room to think often helps "
        "on borderline items.")]
    cells += [code(
        '# ✏️ this prompt asks for reasoning BEFORE the answer. The "do NOT mention any',
        '# other level" line matters: run_prompt keeps the FIRST level it sees in the reply.',
        'PROMPT_COT = """You are an expert rater of English sentence difficulty using the CEFR scale.',
        'Think step by step about the vocabulary and grammar, then decide the level.',
        'Do NOT mention any other CEFR level while reasoning.',
        'End your answer with the final level on its own, exactly one of: A1, A2, B1, B2, C1, C2.',
        '',
        'Sentence: {text}"""',
        '',
        'pred_cot = run_prompt(PROMPT_COT, val)   # slower: the model writes more each time',
        'evaluate(val, pred_cot, ordered=True)    # best of the three so far?')]
    cells += [md(
        "::: {.callout-note}",
        "## A real limitation to notice",
        "`run_prompt` takes the *first* CEFR level it sees in the reply. With chain-of-thought "
        "the model may mention a level mid-reasoning, so the parser can pick the wrong one. If "
        "CoT scores *worse* than few-shot, check `show_errors` to see whether it is the model "
        "or the parser.",
        ":::")]
    cells += [md(
        "### Compare the three",
        "",
        "Fill in the macro-F1 you saw at each step — all three on the **validation** set. "
        "This little table *is* your result.",
        "",
        "| Iteration | macro-F1 (val, 24 items) |",
        "|---|:--:|",
        "| 0 · zero-shot | … |",
        "| 1 · few-shot | … |",
        "| 2 · chain-of-thought | … |")]

    cells += [md(
        "### The held-out run — once, and only once   ✏️ YOU EDIT",
        "",
        "Pick your best prompt from the table above and score it on the 72 sentences you have "
        "not touched all session. **This is the number you report.**",
        "",
        "Expect it to be lower than your validation score. That gap is the cost of having "
        "chosen a prompt by looking at results.",
        "",
        "**If you run this cell, then go back and edit a prompt, the 72 items have stopped "
        "being held out.** In the project this is a file boundary: `04_develop.ipynb` cannot "
        "reach the test items and `05_test.ipynb` opens them once.")]
    cells += [code(
        '# ✏️ swap in whichever of PROMPT_ZERO / PROMPT_FEWSHOT / PROMPT_COT scored best.',
        'BEST_PROMPT = PROMPT_COT',
        '',
        'pred_test = run_prompt(BEST_PROMPT, gold)   # the 72 held-out sentences',
        'evaluate(gold, pred_test, ordered=True)     # ← report THIS macro-F1')]

    # Part A is done and reported. The rate-limit walkthrough goes here, where the
    # student has just watched ~150 calls go through without crashing, and is about
    # to start writing prompt loops of their own in Part B.
    cells += rate_limit_cells

    # ---- Part B: Corpus Lab ----
    cells += [md(
        "## Part B · Corpus Lab — your own prompt-iteration study",
        "",
        "Part A handed you three prompts. Now you write the fourth, and say **in advance** what "
        "you expect it to do.",
        "",
        "Anyone can try ten prompts and keep the best. What makes it a *study* is that each "
        "change comes with a reason and a prediction, so that when the number moves you can "
        "say **why**.",
        "",
        "Everything here runs on `val`. The 72 held-out items stay closed.")]

    cells += [md(
        "### Step 1 · Find the model's worst class",
        "",
        "No new code needed — `evaluate` already printed it. Scroll back to your best prompt's "
        "report and read **down the F1 column**: one or two levels will be far below the rest.",
        "",
        "Then run the cell below and **read three of the actual sentences** for that level. "
        "The counts tell you where the misses are; only the sentences tell you why. Three "
        "cases to tell apart: the sentences are genuinely borderline · your prompt never "
        "described that level · the parser kept an earlier level the model mentioned while "
        "reasoning.")]
    cells += libs("show_errors")
    cells += [code(
        'errors = show_errors(val, pred_cot)   # swap pred_cot for whichever prompt scored best',
        'errors.head(15)')]

    cells += [md(
        "### Step 2 · Write your prediction down first   ✏️ YOU EDIT",
        "",
        "Fill in all three strings **before** you touch the prompt. This is the cell that "
        "turns the next step from tinkering into an experiment.")]
    cells += [code(
        '# ✏️ fill in the three strings. Nothing else in this cell changes.',
        'WORST_CLASS = "…"        # the level with the lowest F1 in Step 1',
        'MY_CHANGE   = "…"        # the ONE thing you will change, in a short phrase',
        'I_PREDICT   = "…"        # what you expect to happen, and why you expect it',
        '',
        'print(f"Targeting {WORST_CLASS}. Change: {MY_CHANGE}.")',
        'print(f"Prediction: {I_PREDICT}")')]
    cells += [md(
        "::: {.callout-tip}",
        "## One change at a time",
        "If you add examples *and* rewrite the instruction *and* ask for reasoning, and the "
        "score moves, you have learned nothing about which of the three did it. Change one "
        "thing, score it, keep or discard it, then change the next.",
        "",
        "Ideas worth trying, roughly cheapest first: describe the weak level explicitly · "
        "add two examples *of that level* · say what separates it from its neighbour · give "
        "the model an out (\"if unsure between two adjacent levels, choose the lower\").",
        ":::")]

    cells += [md(
        "### Step 3 · Make the change and score it   ✏️ YOU EDIT",
        "",
        "Start from your best Part-A prompt and make the one change you just described.")]
    cells += [code(
        '# ✏️ everything between the triple quotes is yours. Keep the {text} slot.',
        'PROMPT_MINE = """You are an expert rater of English sentence difficulty using the CEFR scale.',
        'Classify the sentence into exactly one of: A1, A2, B1, B2, C1, C2.',
        'Answer with the level only.',
        '',
        'Sentence: {text}"""',
        '',
        'pred_mine = run_prompt(PROMPT_MINE, val)',
        'evaluate(val, pred_mine, ordered=True)')]

    cells += [md(
        "### Step 4 · Check the class you actually targeted",
        "",
        "Compare the **F1 for `WORST_CLASS`** in the report you just printed against the same "
        "row in Step 1's report. Macro-F1 can rise while the level you aimed at gets *worse*, "
        "because another level carried the average — so check the row you predicted, not the "
        "headline number.",
        "",
        "The table below lists what your prompt still gets wrong.")]
    cells += [code(
        'errors_mine = show_errors(val, pred_mine)',
        'errors_mine.head(15)')]

    cells += [md(
        "### Step 5 · Log it   ✏️ YOU EDIT",
        "",
        "Fill in the table. The last column is the one that matters: **was your prediction "
        "right?** \"No\" costs you nothing — a wrong prediction you can explain beats a right "
        "one you cannot.",
        "",
        "| # | Prompt change | Why I expected it to help | macro-F1 (val) | F1 for my target level | Prediction right? |",
        "|---|---|---|:--:|:--:|:--:|",
        "| 0 | *(Part A best — no change)* | — | … | … | — |",
        "| 1 | … | … | … | … | … |",
        "| 2 | … | … | … | … | … |",
        "",
        "If you have time, repeat Steps 2–4 with one more change. Two logged iterations with "
        "reasons beat five undocumented ones.",
        "",
        "::: {.callout-important}",
        "## Do not re-run the held-out cell",
        "You scored the 72 items once, at the end of Part A. Running that cell again now, "
        "after choosing a prompt by looking at validation results, would report a number you "
        "tuned toward.",
        ":::")]

    cells += [submission()]
    save("day3_prompt_design.ipynb", cells)


# ============================================================ DAY 4
def day4():
    cells = [how_to_use(
        4, "Day 4 · Pipeline assembly & sampling your gold set",
        ("Tutorial", "sample a balanced gold subset from a dataset pool, ready for QC."),
        ("Corpus Lab", "draw the line between the items you may look at while you work "
                       "(dev) and the items you open once, at the end (test)."))]

    cells += [md(
        "## Part A · Tutorial — sample a balanced gold subset",
        "",
        "For your mini-project you build your **own** gold set by sampling from a *pool*. "
        "A balanced sample (equal items per label) keeps precision/recall/F1 and the "
        "confusion matrix meaningful. Here we demo it on the familiar CEFR pool; swap "
        "`POOL_URL` for your track's pool. See the "
        "[mini-project tracks](../resources/datasets/mini-project-tracks.md) for the full list.")]
    cells += [md("### Setup — run this first")]
    day4_libs = ["load_gold"]      # Day 4 only loads a pool + samples it — no model, no eval
    # No gold_url here: Day 4 loads a POOL, in the visible ✏️ cell below. Passing one
    # would also emit LEVELS, which Day 4 never uses — and the old comment told students
    # to edit LEVELS inside a cell whose first line says "you don't need to read this".
    cells += [setup_cell(backend=None, lib_names=day4_libs)]
    cells += libs(*day4_libs)
    cells += [code(
        f'POOL_URL = "{CEFR_POOL_URL}"   # ✏️ swap for your track\'s pool',
        'pool = load_gold(POOL_URL)   # the big labelled set you will sample FROM')]
    cells += [md(
        "### Draw a balanced sample   ✏️ YOU EDIT",
        "",
        "`PER_LABEL` items per label, with a fixed random seed so the sample is reproducible "
        "(same every run). Rare classes simply yield fewer — that's a property of the data.")]
    cells += [code(
        'import random',
        'from collections import defaultdict, Counter',
        '',
        '### Step 1: the two settings you control ###',
        'PER_LABEL = 8            # how many items per label',
        'random.seed(42)         # fixed seed = same sample every run',
        '',
        '### Step 2: sort the whole pool into one bucket per label ###',
        'by_label = defaultdict(list)   # a dict that starts each new key at []',
        'for item in pool:',
        '    by_label[item["label"]].append(item)   # drop the item in its label\'s bucket',
        '',
        '### Step 3: shuffle each bucket and take the first PER_LABEL from it ###',
        'gold = []',
        'for label in sorted(by_label):        # sorted() = same label order every run',
        '    bucket = by_label[label]',
        '    random.shuffle(bucket)            # mix, so we are not taking the first 8 found',
        '    gold.extend(bucket[:PER_LABEL])   # a rare label simply gives fewer than 8',
        '',
        '### Step 4: mix the labels together and renumber the ids from 1 ###',
        'random.shuffle(gold)             # so the labels are not grouped in blocks',
        'gold = [{"id": i + 1, "text": x["text"], "label": x["label"]}',
        '        for i, x in enumerate(gold)]   # enumerate gives (position, item) pairs',
        '',
        '### Step 5: report what you actually got, label by label ###',
        'print("sampled:", len(gold), "| per label:",',
        '      dict(Counter(x["label"] for x in gold)))   # Counter tallies the labels')]
    cells += [md(
        "### Save your gold set to Google Drive",
        "",
        "Keep your own gold set in **your** Drive (not the course repo). See "
        "[Housing your data in Google Drive](../resources/tools/google-drive-data.md) for the "
        "mount → save → load round-trip.")]
    cells += [code(
        '# ✏️ Uncomment in Colab to save to your Drive:',
        '# from google.colab import drive; drive.mount("/content/drive")',
        '# import json',
        '# with open("/content/drive/MyDrive/my_gold.json", "w", encoding="utf-8") as f:',
        '#     json.dump(gold, f, ensure_ascii=False, indent=2)',
        '# print("saved", len(gold), "items")')]

    cells += [md(
        "## Part B · Draw the line: which items you may look at",
        "",
        "On Day 3 you worked with two files: `val`, which every prompt was scored against, "
        "and `gold`, opened once at the end. They were handed to you already separated. "
        "**Your own gold set arrives in one piece**, so drawing that line is now a step you "
        "take — and it is the last one before the model gets involved.",
        "",
        "| | what it is for |",
        "|---|---|",
        "| **dev** | the items you may look at. Change the prompt because of what you see here, as often as you like. |",
        "| **test** | opened once, at the end. Whatever it says is what you report. |",
        "",
        "The reason is the one Day 3 gave you: a score measured on the items you kept "
        "adjusting against stops measuring how good your prompt is and starts measuring how "
        "long you kept adjusting. It only ever goes up.",
        "",
        "Both halves come out of the same annotation work, so the split costs you **no extra "
        "annotation**. What it costs is items you are allowed to learn from.")]
    cells += [md(
        "### Split it, keeping every label on both sides   ✏️ YOU EDIT",
        "",
        "Not a straight cut down the middle: split **within each label**, the same "
        "bucket-then-slice shape you wrote ten minutes ago. A straight cut on a shuffled "
        "list can leave a whole label on one side, and a label missing from `test` drops out "
        "of your macro average without announcing itself.")]
    cells += [code(
        '### Step 1: the setting you control ###',
        'DEV_PER_LABEL = 3       # ✏️ how many items per label you may look at',
        '',
        '### Step 2: sort the sample into one bucket per label (as in Part A) ###',
        'buckets = defaultdict(list)',
        'for item in gold:',
        '    buckets[item["label"]].append(item)',
        '',
        '### Step 3: take the first few of each bucket for dev, the rest for test ###',
        'dev = []',
        'test = []',
        'for label in sorted(buckets):',
        '    bucket = buckets[label]',
        '    dev.extend(bucket[:DEV_PER_LABEL])    # the ones you may look at',
        '    test.extend(bucket[DEV_PER_LABEL:])   # everything after them',
        '',
        '### Step 4: read the counts BEFORE you go any further ###',
        'print("dev :", len(dev),  "|", dict(Counter(x["label"] for x in dev)))',
        'print("test:", len(test), "|", dict(Counter(x["label"] for x in test)))')]
    cells += [md(
        "**Read those two lines rather than glancing at them.** A label showing up in `dev` "
        "with nothing left in `test` cannot appear in the score you report, and right now it "
        "costs you one number to fix. Later it costs an afternoon.",
        "",
        "There is no right size for `dev`, only one you can defend. A bigger `dev` gives you "
        "steadier feedback while you iterate and leaves a smaller `test`, so the number you "
        "finally report bounces around more. A smaller `dev` means prompt decisions made on "
        "very few items — which is how you tune to noise and then watch the gain evaporate on "
        "the half you held back.",
        "",
        "In the final project this is `split_dev_test(gold, DEV, seed=SEED)`, and it handles "
        "the two fiddly cases this cell does not: a proportion instead of a fixed count, and "
        "a label with a single surviving item — which it sends to `test`, for the reason "
        "above. The rule it follows is the one you just wrote.")]
    cells += [md(
        "## Where this goes next",
        "",
        "Everything after this — the annotation sheet, agreement, adjudication, the prompt "
        "rounds, the held-out run — happens in your group's own copy of the project "
        "template, because it needs your track, your Drive and your group's decisions:",
        "",
        "**[github.com/egumasa/lda2-final-template](https://github.com/egumasa/lda2-final-template)**",
        "",
        "| Notebook | What it does |",
        "|---|---|",
        "| `01_build_pool_<track>` | turns your track's raw corpus into a pool |",
        "| `02_sample` | the draw you wrote in Part A, plus the blind annotation sheet |",
        "| `02b_add_samples` | optional — time left over, so more items into the same sheet |",
        "| `03_annotate` | agreement, adjudication, and the split you wrote in Part B |",
        "| `04_develop` | prompt rounds, on **dev** only |",
        "| `05_test` | the held-out run, once |",
        "| `06_report` | scoring, error analysis, export |",
        "",
        "`03_annotate` does properly what you did by hand on Day 2 (S5): two of you label the "
        "sheet independently, you measure agreement, and you adjudicate the rows you "
        "disagreed on. What comes out is *your* gold set, and it is what the model gets "
        "scored against — so those disagreements are doing real work, not bookkeeping.",
        "",
        "Today is why you can read those notebooks: `sample_pool` is the Part-A cell in one "
        "call and `split_dev_test` is the Part-B cell in one call. You have seen what they "
        "do, so you can say what they do.",
        "",
        "Before you run anything that calls the model, your group needs a signed "
        "**`PLAN.md`** — see the [Final Project](../final-project/index.md) pages.")]

    cells += [submission()]
    save("day4_pipeline_and_sampling.ipynb", cells)


# ============================================================ DAY 5
# There is no Day-5 notebook. Day 5 is project work: groups run their own study in the
# six numbered notebooks of the lda2-final-template repo, on their own track and their
# own gold set. The old day5_project_finalization.ipynb was a shell of todo()
# scaffolds pointing at that repo, and principles §3 forbids shipping dead scaffolding.
# What it needed to say now lives on the Final Project pages of the site.


if __name__ == "__main__":
    day1()
    day2_s5()          # Day 2 ships two notebooks — one per hands-on session
    day2_s6()
    day3()
    day4()
    print("ALL DONE ->", OUT)
