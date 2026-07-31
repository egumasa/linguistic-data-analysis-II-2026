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
def generate_text(prompt):
    """Send a prompt to Colab's built-in Gemini; wait between calls so we don't go
    too fast. Returns the reply as text. (Non-reproducible: no temperature/seed.)"""
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
def _resolve_gemini_key():
    """Find a Gemini API key: Colab Secrets first (not auto-exported to env), then env."""
    try:
        from google.colab import userdata      # only exists in Colab
        key = userdata.get("GEMINI_API_KEY")   # what you saved in the Secrets panel
        if key:
            return key                         # found one — use it
    except Exception:
        pass                                    # not in Colab, or secret not set
    return os.environ.get("GEMINI_API_KEY")     # last resort: an environment variable

### Step 2: build the reproducible backend around that key ###
def _make_api_backend(key):
    """Reproducible backend: Gemini API with temperature=0 + a fixed seed."""
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
def _looks_like_rate_limit(error):
    """Does this error mean "you are going too fast", rather than a real bug?"""
    text = str(error).lower()                   # the error, as lowercase text
    return any(s in text for s in               # true if ANY of these phrases appear
               ["429", "resource_exhausted", "rate limit", "quota", "too many requests"])

def _looks_like_daily_quota(error):
    """Is this the PER-DAY cap? Those don't clear by waiting a few seconds."""
    text = str(error).lower()
    return "per day" in text or "perday" in text.replace(" ", "")

def _suggested_delay(error, fallback):
    """The server often says "please retry in 7.2s" — obey it if it did."""
    m = re.search(r"retry in ([0-9]+(?:\\.[0-9]+)?)s", str(error).lower())
    return float(m.group(1)) + 1.0 if m else fallback   # +1s cushion, else our guess

### Step 4: the one function you call all week — pace, ask, and retry if told to ###
_last_call_time = 0.0   # generate_text remembers & updates this with `global`

def generate_text(prompt, max_retries=5):
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
    # `sheets` draws a confusion matrix too (annotator-vs-annotator), so it needs the
    # same plotting stack as `evaluate` — but not classification_report.
    want_report = "evaluate" in lib_names
    want_matrix = bool(lib_names & {"evaluate", "sheets"})
    want_viz = bool(lib_names & {"evaluate", "show_errors", "sheets"})   # pandas/seaborn/plt

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
    'def load_gold(url_or_path):',
    '    """Read the canonical gold JSON: [{\'id\',\'text\',\'label\'}, ...]."""',
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
    'def _extract_level(text):',
    '    """Pull the first A1/A2/B1/B2/C1/C2 out of the model\'s reply."""',
    '    # The model may answer "B2" or "I would say B2." — search rather than assume.',
    '    m = re.search(r"\\b([ABC][12])\\b", str(text).upper())',
    '    return m.group(1) if m else "??"      # "??" = no level found in the reply',
    '',
    'def run_prompt(prompt, gold):',
    '    """Send each item\'s `text` to the LLM via {text}, collect predicted labels."""',
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
    'def evaluate(gold, predictions, ordered=False):',
    '    """Score predictions against gold: per-class P/R/F1 + macro, Cohen\'s κ, and a',
    '    confusion-matrix heatmap.',
    '',
    '    ordered=True adds QUADRATIC WEIGHTED κ — use it only when the labels sit on a',
    '    scale (A1 < A2 < ... < C2), so that a near miss counts as a smaller error than',
    '    a far one. For unordered categories, plain κ is the one to report."""',
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
    'def show_errors(gold, predictions):',
    '    """The items the model got wrong, as a table you can read and argue about."""',
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
    'def load_predictions(url_or_path):',
    '    """Read a frozen predictions list — a committed URL or a local path."""',
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
LIB_SHEETS = code(
    '#@title 🔧 Library cell: Google Sheets annotation round-trip { display-mode: "form" }',
    "# Helper — you don't need to read this. Run it and move on.",
    '# Sheet column headers (the annotation template uses these exact names):',
    'COL_ID, COL_TEXT = "ID", "Text"',
    'COL_A, COL_B = "CoderA", "CoderB"',
    'COL_FINAL, COL_NOTES = "Final", "Note"',
    'ANNOTATION_HEADER = [COL_ID, COL_TEXT, COL_A, COL_B, COL_FINAL, COL_NOTES]',
    '',
    'def _sheets_client():',
    '    """Authorise gspread with your Google account (a pop-up asks for permission)."""',
    '    from google.colab import auth',
    '    import google.auth, gspread',
    '    auth.authenticate_user()           # the pop-up: "let Colab use your Sheets"',
    '    creds, _ = google.auth.default()   # the permission slip that pop-up produced',
    '    return gspread.authorize(creds)    # a logged-in connection to Google Sheets',
    '',
    'def create_annotation_sheet(title, items, labels):',
    '    """Create a Sheet in YOUR Drive: one row per item, blank columns to label.',
    '    `items` are {"id","text",...} dicts — any existing label is deliberately NOT',
    '    copied across, so you annotate blind. Returns the sheet URL."""',
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
    '    return sheet.url',
    '',
    'def load_annotation_sheet(sheet_id, worksheet="round1"):',
    '    """Read one TAB of your annotation sheet back as a list of row dicts.',
    '    `sheet_id` is the long id in the sheet\'s URL:',
    '        docs.google.com/spreadsheets/d/<THIS PART>/edit',
    '    Pasting the whole URL works too — either way opens the exact sheet, so two',
    '    copies that share a name (\\"Copy of ...\\") are never confused.',
    '    `worksheet` is the TAB name (a \\"round\\"): each round lives in its own tab, so',
    '    re-annotating in round2 never overwrites round1 — the analysis stays reproducible."""',
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
    '    return rows',
    '',
    'def to_canonical(rows, labels, column=COL_FINAL):',
    '    """Turn annotation rows into canonical gold: [{"id","text","label"}, ...].',
    '    Blank rows are skipped; labels outside `labels` are reported, not silently kept."""',
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
    '    return gold',
    '',
    'def annotator_agreement(rows, a=COL_A, b=COL_B):',
    '    """Percent agreement + Cohen\'s κ between the two annotator columns, PLUS an',
    '    annotator-vs-annotator confusion matrix (the diagonal is where you agreed;',
    '    off-diagonal cells show which label pairs the two of you confuse)."""',
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
    '    return {"n": len(pairs), "percent_agreement": percent, "kappa": kappa}',
    '',
    'def disagreements(rows, a=COL_A, b=COL_B):',
    '    """The rows your two annotators labelled differently — your adjudication list."""',
    '    # keep a row only if both annotators labelled it AND they chose differently:',
    '    out = [r for r in rows',
    '           if str(r.get(a, "")).strip() and str(r.get(b, "")).strip()',
    '           and str(r[a]).strip() != str(r[b]).strip()]',
    '    print(f"{len(out)} rows to adjudicate. Agree on a `Final` label for each in the sheet.")',
    '    return pd.DataFrame(out)',
    '',
    'def compare_to_published(gold, published):',
    '    """How often does YOUR final label match the published gold, item by item?"""',
    '    ### Step 1: look up the published label for every id ###',
    '    lookup = {item["id"]: item["label"] for item in published}   # id -> their label',
    '    shared = [(g["label"], lookup[g["id"]]) for g in gold if g["id"] in lookup]',
    '    if not shared:',
    '        print("No overlapping ids — did you keep the ids the sheet gave you?")',
    '        return None',
    '',
    '    ### Step 2: count the matches, then show only the rows where you differ ###',
    '    agree = sum(mine == theirs for mine, theirs in shared)',
    '    print(f"{agree}/{len(shared)} match the published label ({agree / len(shared):.1%})")',
    '    return pd.DataFrame([{"id": g["id"], "yours": g["label"], "published": lookup[g["id"]],',
    '                          "text": g["text"]}',
    '                         for g in gold if g["id"] in lookup',
    '                         and g["label"] != lookup[g["id"]]])')


# S6 pass 1 builds the metrics by hand on a BINARY question ("is this sentence
# advanced?"), so it needs the two lists paired into one list of dicts — the same
# shape students have looped over since Day 1 — and a way to see the four counts as
# a square. Both are display/plumbing, never the lesson, so both are helpers.
LIB_PAIR_UP = code(
    '#@title 🔧 Library cell: pair_up(gold, predictions, positive) → items { display-mode: "form" }',
    _HELPER_NOTE,
    'def pair_up(gold, predictions, positive):',
    '    """Pair each gold item with the model\'s prediction, both collapsed to yes/no.',
    '',
    '    `positive` lists the labels that count as "yes" (e.g. ["C1", "C2"]).',
    '    Returns [{"id", "text", "gold", "pred"}, ...] — one dict per item."""',
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
    'def show_2x2(tally):',
    '    """Print a tally of TP/FP/FN/TN as a confusion matrix — rows are the gold',
    '    label, columns are the prediction. No arithmetic: the same four numbers,',
    '    arranged so you can see where the errors went."""',
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
    "sheets": LIB_SHEETS,
    "pair_up": LIB_PAIR_UP,
    "show_2x2": LIB_SHOW_2X2,
}


def libs(*names):
    """The 🔧 pipeline cells for a day, in the given order. Keep the names here in
    sync with the lib_names passed to setup_cell (they drive the day's imports)."""
    return [LIB[n] for n in names]


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
        "You only edit the cells marked **✏️ YOU EDIT**. Cells marked **🔧 Library cell** "
        "are pre-written — run them, don't change them.",
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

    # ---- Part B: segmentation → control flow → practice → project ----
    cells += [md(
        "## Part B · Corpus Lab — from text to sentences, then practice",
        "",
        "In Part A you called the model once. Here you'll turn a paragraph into individual "
        "**sentences** (the unit you'll annotate on Day 2), run the model over all of them, "
        "and then practice the basics on your own. Cells marked **✏️ YOU EDIT** are yours to "
        "change; run the **self-check** at the end until every line prints ✅.")]

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

    # B3. Control flow: for / if / function
    cells += [md(
        "### 3. Run the model over every sentence — `for`, `if`, and a function",
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
        "### 4. Your turn — Python practice",
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
_DAY2_NOTE = ("**Day 2 has two notebooks, one per hands-on session** — S5 builds a gold "
              "standard by hand ({this}), S6 measures a model against one ({other}). "
              "Submit both at the end of the day.")
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
        "So far the gold labels have been handed to you. Now you make some. This session's work "
        "is split across **three surfaces that share one spine**, the six steps **A–F**:",
        "",
        "- **Slides** teach the *concepts* — how to sample (A), why annotate blind (C), how to "
        "read a confusion matrix (D–E).",
        "- **A Google Sheet** holds the *human judgment* — you and your partner annotate there "
        "(C), and re-annotate there (E).",
        "- **This notebook** does the *numbers* — it reads the sheet and measures, adjudicates, "
        "and exports (**D–F**).",
        "",
        "So **steps A–C need no code**; this notebook first runs at **step D**. Each header "
        "below prints the same `A–F` label as the slides — find your place by the *letter*.",
        "",
        "::: {.callout-note}",
        "## Why a spreadsheet?",
        "Annotation is a *judgement* task, not a coding task — a sheet is the fastest honest "
        "way to do it, and it is what most annotation projects actually use. The point is not "
        "the tool; it is that you feel how often two careful people disagree, and what it "
        "takes to resolve that into a single defensible label.",
        ":::")]

    # A–C: code-free (slides + Sheet). The notebook just tells students where to go.
    cells += [md(
        "### A · Sample → copy your track's sheet   *(E&K Step 3 · ①)*",
        "",
        "The sample is **already drawn for you** — one template Sheet per track, whose first "
        "tab is **`round1`** with the columns **`ID · Text · CoderA · CoderB · Final · Note`** "
        "and only `ID` and `Text` filled in (never the labels, so your annotation is genuinely "
        "independent). *How* it was sampled — represent the domain, fix the unit, a seed for "
        "reproducibility — is the slide concept; the exact draw is in the reference appendix at "
        "the end of this notebook.",
        "",
        "**Open your track's template Sheet → `File → Make a copy`** into your own Drive. Then "
        "grab your copy's **id** from its URL — the long string between `/d/` and `/edit` in "
        "`docs.google.com/spreadsheets/d/`**`<id>`**`/edit`. You'll paste it into step D. (Opening "
        "by id, not name, means two copies that share the name \"Copy of …\" are never confused.)")]
    cells += [md(
        "### B · Apply the operationalized scheme   *(E&K Steps 4–5; Fuoli · ②)*",
        "",
        "Before you label, restate the **decidable rule** you're annotating against (the scheme "
        "your team drafted in the earlier sessions) and skim the guidelines and per-level "
        "examples. One label per unit; know your label set cold. → interpret this on **step B** "
        "(slides).")]
    cells += [md(
        "### C · Annotate blind, in pairs   *(E&K Step 6 · ③)*",
        "",
        "This step happens **entirely in the Sheet — no code**, in the **`round1`** tab. One of "
        "you fills **`CoderA`** and the other fills **`CoderB`**, *without looking at each "
        "other's column*. Leave "
        "`Final` blank for now. Use `Note` for anything you found hard to decide; those notes "
        "are your evidence in step E.",
        "",
        "::: {.callout-important}",
        "## Stop here and go annotate",
        "Label all ~20 rows in **both** annotator columns before running the next cell. Come "
        "back to Colab when the sheet is filled in — the notebook picks up at **step D**.",
        ":::")]

    # D–F: the executable round-trip. Setup lives HERE, not at the top, because Colab
    # first runs at step D — steps A–C are done in the slides and the Sheet.
    cells += [md(
        "### D · Measure agreement   *(E&K Step 6 · ③)*   ✏️ YOU EDIT",
        "",
        "Colab opens here — run the two helper cells below first. Then read your copied sheet "
        "back in and measure how much the two of you "
        "agreed: **percent agreement**, **Cohen's κ** (agreement corrected for chance), and an "
        "**annotator-vs-annotator confusion matrix** — the diagonal is where you agreed, the "
        "off-diagonal cells show *which label pairs* you confuse.",
        "",
        "::: {.callout-note collapse=\"true\"}",
        "## How to read what this prints — the interpretation (step D, slides)",
        "Percent agreement flatters two coders who both lean on the same label — they agree a "
        "lot *by luck*. **Cohen's κ** strips that luck out, so trust the κ, not the percentage "
        "(recall S4: 80% raw agreement was only κ ≈ 0.52). Then read the matrix for the *one "
        "off-diagonal cell* dragging κ down — that specific label pair is your to-do list for "
        "step E. You will code κ yourself from scratch in the S6 notebook.",
        ":::")]
    s5_libs = ["sheets", "load_gold"]
    cells += [setup_cell(
        backend=None,          # S5 never calls a model — the judgment is yours
        lib_names=s5_libs,
        gold_url=CEFR_GOLD_URL,
        gold_comment="CEFR-SP gold set — the published labels you compare against in step F.")]
    cells += libs("sheets")
    cells += [code(
        'SHEET_ID = "1AbCdEf...paste_yours"   # ✏️ the id in YOUR copied sheet\'s URL',
        '                                     #    (…/spreadsheets/d/THIS/edit) — the whole URL works too',
        'ROUND    = "round1"                  # ✏️ which round\'s tab to analyze',
        '',
        'rows = load_annotation_sheet(SHEET_ID, ROUND)   # read that tab back into Python',
        'annotator_agreement(rows)            # % agreement, κ, and the confusion matrix')]
    cells += [md(
        "### E · Read the matrix → refine → re-annotate   *(E&K Step 6; Fuoli princ. 2 · ③)*",
        "",
        "A low κ is a diagnosis of your **scheme**, not your annotating. `disagreements(rows)` "
        "lists every row the two of you saw differently — the items behind those off-diagonal "
        "cells.",
        "",
        "::: {.callout-note collapse=\"true\"}",
        "## What to do with this list — the judgment (step E, slides)",
        "For the label pair the matrix flagged, **refine the scheme / guidelines** so that "
        "ambiguity becomes decidable (add a rule, a boundary case, an example). Then re-annotate "
        "in a **fresh round tab** (below) and re-run **step D** to see κ move. Iterate until "
        "agreement is acceptable — that is Fuoli's principle 2 in action.",
        ":::")]
    cells += [code(
        'disagreements(rows)   # the rows you two labelled differently — your worklist')]
    cells += [md(
        "::: {.callout-important}",
        "## Re-annotate in a fresh round tab, then re-run step D",
        "Don't overwrite `round1`. In the Sheet, **right-click the `round1` tab → Duplicate**, "
        "rename the copy **`round2`**, and re-label the confused items *there*. Then set "
        "**`ROUND = \"round2\"`** in step D and re-run it. `round1` stays intact — so every run "
        "is reproducible, and you can watch κ climb round over round. Repeat (round3, …) until κ "
        "is acceptable before moving to step F.",
        ":::")]
    cells += [md(
        "### F · Adjudicate → gold   *(E&K Step 6 → feeds ④⑤)*   ✏️ YOU EDIT",
        "",
        "The last disagreements don't refine away — you **decide** them. In your **latest round "
        "tab**, fill a single `Final` "
        "label for every row (for rows you already agreed on, `Final` is just that "
        "agreed label), then read it back and convert it to canonical form. `to_canonical` "
        "refuses anything that isn't one of your allowed labels, so typos surface here rather "
        "than silently corrupting your gold set.")]
    cells += [code(
        'rows = load_annotation_sheet(SHEET_ID, ROUND)   # re-read your latest round, `Final` filled in',
        'my_gold = to_canonical(rows, LEVELS)            # reads the `Final` column',
        'my_gold[:3]                                     # peek at the first three items')]
    cells += [md(
        "**How does your gold compare with the published gold?** The CEFR-SP labels came from "
        "language-education professionals, and we kept only sentences where two of them agreed. "
        "Differing from them is **not** simply *wrong* — Arase's own experts agreed exactly "
        "only 37.6% of the time — but each difference is worth a look and a defensible reason. "
        "→ interpret this on **step F** (slides).")]
    cells += libs("load_gold")
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
    # "Runtime → Run all" never re-creates sheets. The create_annotation_sheet helper lives
    # in LIB_SHEETS above; this shows the seeded draw that fed it, one sheet per track.
    cells += [md(
        "::: {.callout-note collapse=\"true\"}",
        "## Reference — how the template sheets were built (you don't run this)",
        "",
        "The template Sheet you copied in step A was generated once, ahead of the session, so "
        "the sample is fixed and reproducible. It uses the `create_annotation_sheet` helper "
        "(loaded above) fed by a **seeded** random draw — one sheet per track (`cefr`, "
        "`cars50`, `raamove`, `l2_errors`). Shown here so the sampling is transparent; you do "
        "**not** run it.",
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
    #            metrics built from scratch in ten numbered steps: 12 hand-countable
    #            items first, then all 72, then checked against scikit-learn.
    #   Part B = pass 2 — the real six-class task, with scikit-learn.
    # SURFACE DIVISION (differs from S5 on purpose): the deck carries BOTH the concept
    # and the implementation — every line of pass-1 code is on a slide next to what it
    # prints — and students type it here. So these cells must PRINT EXACTLY what the
    # slides show; every number is derived from the committed gold + frozen predictions.
    # Cells build UP: loose code that runs and prints first, `def` only once re-use
    # motivates it. Cross-reference BY STEP NUMBER, never by cell/slide number.
    cells = [how_to_use(
        2, "Day 2 · S6 — Evaluation metrics",
        ("Corpus Lab", "build the metrics yourself — TP/FP/FN/TN → confusion matrix → "
                       "precision, recall, F1 → Cohen's κ — on a single yes/no question, "
                       "then check your code against scikit-learn."),
        ("Tutorial", "the same job with **scikit-learn** on the real six-level task: "
                     "`classification_report`, the confusion matrix, plain vs. weighted "
                     "κ, and error analysis."),
        note=_DAY2_NOTE.format(
            this="`day2-s5_gold_standard_construction.ipynb`", other="this one"))]

    # ---- Setup + the data both passes run on ----
    cells += [md(
        "## Setup — run this first",
        "",
        "Both parts run on the same data: the **CEFR-SP** gold set (72 sentences, 12 per "
        "level — the pool your S5 sample was drawn from) and one model's answer for every "
        "one of them.",
        "",
        "::: {.callout-note}",
        "## Today runs on *frozen* predictions — no API key, no live model",
        "You met the live model on Day 1 and saw its answers change from run to run. When "
        "you're learning to *measure* quality, that wobble is just noise fighting the lesson — "
        "so today the model's predictions are **pre-computed and committed** to a file. You "
        "load them, and everyone's precision / recall / F1 / κ come out **identical every "
        "run**: if your number differs from the slide, you have a bug, not a different model. "
        "You'll run the model yourself (with the key) from Day 3 on.",
        ":::")]
    s6_libs = ["load_gold", "predictions", "pair_up", "show_2x2", "evaluate", "show_errors"]
    cells += [setup_cell(
        backend=None,          # frozen predictions — Day 2 never calls a model
        lib_names=s6_libs,
        gold_url=CEFR_GOLD_URL,
        gold_comment="CEFR-SP gold set (72 sentences, 12 per level), fetched from the course repo.",
        predictions_url=CEFR_PREDICTIONS_DAY2_URL)]
    cells += libs(*s6_libs)
    cells += [md(
        "### What a *gold file* actually is",
        "",
        "Before we load one, look at the shape up close. A gold standard is stored as "
        "**JSON** text — the same `{\"id\", \"text\", \"label\"}` records you met on Day 1, "
        "written to a file. `json.loads(...)` turns that text into a Python **list of dicts** "
        "you can index into.")]
    cells += [code(
        'raw = \'[{"id": 1, "text": "Hello.", "label": "A1"}, {"id": 2, "text": "Nevertheless, the findings were inconclusive.", "label": "C1"}]\'',
        'items = json.loads(raw)               # JSON text → list of dicts',
        'print("number of items:", len(items))    # two records in that text',
        'print("first record:", items[0])         # the whole first dict',
        'print("its label:", items[0]["label"])   # index: list by position, dict by key')]
    cells += [md(
        "Files are read and written with **`with open(...) as f:`** — it opens the file, "
        "gives it to you as `f`, and closes it automatically when the block ends. You won't "
        "write this yourself (the 🔧 Library cells handle it), but you'll see it, so here it "
        "is once, in the open:")]
    cells += [code(
        'with open("example_gold.json", "w", encoding="utf-8") as f:   # write',
        '    json.dump(items, f)              # the list of dicts becomes JSON text on disk',
        '',
        'with open("example_gold.json", encoding="utf-8") as f:        # read back',
        '    reloaded = json.loads(f.read())  # ...and JSON text becomes a list again',
        'print("read back", len(reloaded), "records — same shape:", reloaded[0])')]
    cells += [md(
        "### Load the gold standard and the frozen predictions",
        "",
        "`load_gold(...)` does exactly the read you just saw, but from a URL. Notice the shape: "
        "every dataset this week is `{\"id\", \"text\", \"label\"}`. That is the *only* data "
        "shape you have to learn.",
        "",
        "Below the gold is the prompt we sent the model — `{text}` is where each sentence gets "
        "slotted in. We ran it **once** over the gold set and committed the answers, so today "
        "you load that frozen file rather than call the model. (From Day 3 you'll run prompts "
        "like this yourself.)")]
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
        "In S5 `annotator_agreement()` printed Cohen's κ *for* you. In a moment `evaluate()` "
        "will print precision, recall and F1 *for* you too. **First you build them.** Once "
        "you have written these formulas, no number in your final project is a black box.",
        "",
        "Work in **ten small steps**. Each one is on a slide with the code and what it prints; "
        "type it here, run it, and check your output matches before moving on. Nothing here "
        "needs an import — just `for`, `if`, and dictionaries.",
        "",
        "::: {.callout-tip}",
        "## If you fall behind, copy the slide",
        "Every cell below is short and self-contained. Copy the code from the slide, run it, "
        "and you're back with the class — then read it and make sure you can say what each "
        "line does.",
        ":::")]

    cells += [md(
        "### Step 1 · Collapse to one yes/no question",
        "",
        "CEFR has six levels. Six levels means **36** confusion-matrix cells — too many to "
        "learn on. So for Part A we ask **one** thing:",
        "",
        "> **Is this sentence *advanced* — C1 or C2?**",
        "",
        "`\"yes\"` (C1 or C2) is our **positive class**; everything else is `\"no\"`. Precision "
        "and recall are *always about the positive class*, so choosing it is a decision you "
        "state out loud, not a technicality.",
        "",
        "Here are 12 of the 72 sentences, already collapsed:")]
    cells += [code(
        'ADVANCED = ["C1", "C2"]      # the levels that count as "yes"',
        '',
        '# Twelve of the 72 sentences with the gold level and the model\'s answer, both',
        '# collapsed to yes/no. (`text` is shortened here for display — the full sentences',
        '# are in `gold`, which you loaded above.)',
        'items = [',
        '    {"id": 17, "text": "Newspaper \'s revenue from classifieds advertisements…",',
        '     "gold": "no", "pred": "no"},',
        '    {"id": 18, "text": "Saffron \'s aroma is often described by connoisseurs…",',
        '     "gold": "yes", "pred": "yes"},',
        '    {"id": 19, "text": "He died on 26 September 2017 in Paris at the age of…",',
        '     "gold": "no", "pred": "no"},',
        '    {"id": 20, "text": "Bat : The bat used by the offense can be made out of…",',
        '     "gold": "no", "pred": "no"},',
        '    {"id": 21, "text": "Because oxygen is more electronegative than carbon ,…",',
        '     "gold": "yes", "pred": "yes"},',
        '    {"id": 22, "text": "Racing bicycles used for Criteriums often have subtl…",',
        '     "gold": "yes", "pred": "no"},',
        '    {"id": 23, "text": "Harris died on 9 May 2019 , at the age of 93 .",',
        '     "gold": "no", "pred": "no"},',
        '    {"id": 24, "text": "The first derivative test is used in calculus optimi…",',
        '     "gold": "yes", "pred": "no"},',
        '    {"id": 25, "text": "She died on June 9 , 2014 , at the age of 103 .",',
        '     "gold": "no", "pred": "no"},',
        '    {"id": 26, "text": "The forest contains at least 900 plant species .",',
        '     "gold": "no", "pred": "no"},',
        '    {"id": 27, "text": "Cryptobranchids are large , fat salamanders , with f…",',
        '     "gold": "yes", "pred": "yes"},',
        '    {"id": 28, "text": "The seven pitches of any diatonic scale can also be…",',
        '     "gold": "no", "pred": "yes"},',
        ']',
        'print(len(items), "items")',
        'print(items[0])')]
    cells += [md(
        "**Before you write any code, count the four outcomes by hand** — with your partner, "
        "off the list above. How many **TP** (gold yes, model yes), **FP** (gold no, model "
        "yes), **FN** (gold yes, model no), **TN** (gold no, model no)?",
        "",
        "::: {.callout-note collapse=\"true\"}",
        "## Check your count (open after you've counted)",
        "|              | model **yes** | model **no** |",
        "|--------------|:-------------:|:------------:|",
        "| gold **yes** | **TP = 3**    | **FN = 2**   |",
        "| gold **no**  | **FP = 1**    | **TN = 6**   |",
        "",
        "TP: rows 18, 21, 27 · FN: rows 22, 24 (real C1s the model missed) · FP: row 28 (it "
        "cried wolf on a B2) · TN: the other six.",
        "",
        "**Everything else in Part A is arithmetic on these four numbers** — and your code has "
        "to reproduce them.",
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
        "**exactly one** runs — every item lands in exactly one cell. The final `else` needs "
        "no condition: if it isn't TP, FP or FN, it can only be TN.",
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
        "You are about to ask that same question of all 12 rows. Copying the ladder twelve "
        "times would be absurd — so **name it once**. Two changes from step 3, and only two: "
        "it is wrapped in `def`, and every `print` became a **`return`**.",
        "",
        "`print` puts a value on the screen and then it is gone; `return` hands the value "
        "back to whoever called the function, so you can **keep it, store it, count it** — "
        "which is exactly what step 5 needs.")]
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
        "is `'FN'` — that's row 22, the racing-bicycle sentence the model missed.",
        "",
        "We *could* have counted as we went. We keep the list because **the list is the "
        "evidence**: a metric is a summary, and `decisions` is the thing being summarised. "
        "Every `'FN'` and `'FP'` in it points at a specific sentence you can read and argue "
        "about — that is error analysis, and it's where the research questions live.")]

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
        "in a square, so you can *see* where the errors went.")]
    cells += [code('show_2x2(tally)')]
    cells += [md(
        "- The **diagonal** (3 and 6) is everything the model got right — 9 of 12.",
        "- The **off-diagonal** (2 and 1) is everything it got wrong, **split by direction**: "
        "two *misses* and one *false alarm*. A single accuracy figure would hide that "
        "difference completely.",
        "",
        "Now the margins — you need them for κ in step 9:",
        "",
        "|              | model **yes** | model **no** | **total** |",
        "|--------------|:-------------:|:------------:|:---------:|",
        "| gold **yes** | 3 | 2 | **5** |",
        "| gold **no**  | 1 | 6 | **7** |",
        "| **total**    | **4** | **8** | **12** |",
        "",
        "The gold set calls 5 sentences advanced; the model calls only **4**. It is slightly "
        "**stingy** with the positive label — watch that habit, it comes back in Part B.")]

    cells += [md(
        "### Step 8 · Precision, recall, F1",
        "",
        "**Precision** — *of everything the model CALLED advanced, how much really was?*",
        "",
        "$$P = \\frac{TP}{TP + FP}$$",
        "",
        "Numbers first, so you can check it on paper — then the same thing read off the "
        "tally, so it survives a change of data:")]
    cells += [code(
        'print(3 / (3 + 1))                                  # TP / (TP + FP), by hand',
        'print(tally["TP"] / (tally["TP"] + tally["FP"]))    # the same, from the tally')]
    cells += [md(
        "Of the 4 sentences the model called advanced, 3 really were. **Precision = 0.75.**",
        "",
        "Now as a function — and note the guard: if a model never predicts the positive "
        "class, `TP + FP` is 0 and Python raises `ZeroDivisionError`. Returning `0.0` says "
        "*\"it earned no credit\"*, which is the honest reading. **Every metric you write "
        "today gets this guard.**")]
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
        "while precision collapses. **F1** is the harmonic mean, so a high score can't cover "
        "for a low one:",
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
        "**Precision 0.75 > recall 0.60** → this model is **conservative** about calling "
        "something advanced: when it commits it's usually right, but it lets real C1s slip "
        "past as B2. Both sentences it missed were **C1 → B2** — near misses, not wild errors.",
        "",
        "*Which error can you live with?* is a **research design** question, not a statistics "
        "one. Screening texts for a C1 reading list? A miss is expensive — favour recall. "
        "Making a claim about which sentences are advanced? A false alarm is expensive — "
        "favour precision. Decide **before** you report a score.",
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
        "Gold and model agree on 9 of 12. Sounds decent — but **so would a lazy model that "
        "answered \"no\" to everything**: it would score 7/12 while knowing nothing at all. "
        "Raw agreement flatters whoever plays the odds.",
        "",
        "So subtract the agreement you'd get **by luck**. $p_e$ multiplies the two raters' "
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
        "**More than half** the agreement we observed (0.75) was available for free. κ asks "
        "how much of what luck *couldn't* explain the two of them actually achieved:",
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
        "### Step 10 · Scale up, then check yourself",
        "",
        "Nothing changes but the input. `pair_up` pairs each gold item with the model's "
        "answer and collapses both to yes/no — giving all 72 items in exactly the shape your "
        "loop already expects.")]
    cells += [code(
        '### Step 1: all 72 items, in the same yes/no shape as the 12 ###',
        'all_items = pair_up(gold, predictions, ADVANCED)',
        '',
        '### Step 2: the SAME loop as step 5 — only the input changed ###',
        'decisions = []',
        'for item in all_items:',
        '    decisions.append(outcome(item["gold"], item["pred"]))',
        '',
        '### Step 3: the SAME tally as step 6 ###',
        'tally = {}',
        'for d in decisions:',
        '    tally[d] = tally.get(d, 0) + 1',
        'print(tally)')]
    cells += [code(
        'show_2x2(tally)                              # the four counts, as a square',
        'print("precision", round(precision(tally), 3),   # your functions, unchanged',
        '      "  recall", round(recall(tally), 3),',
        '      "  F1", round(f1(tally), 3),',
        '      "  kappa", round(kappa(tally), 3))')]
    cells += [md(
        "**The 12-item slice was not the whole story** — precision rose, recall stayed low. "
        "The pattern held: *stingy, but usually right when it commits.* Twelve items is "
        "enough to learn the mechanics, never enough to judge a model.",
        "",
        "Now let scikit-learn mark your work:")]
    cells += [code(
        '#@title 🔎 Self-check against scikit-learn — run me { display-mode: "form" }',
        "# Helper — you don't need to read this. Run it and move on.",
        'from sklearn.metrics import precision_score, recall_score, f1_score',
        '',
        '### Step 1: the same 72 items as two plain lists — the shape sklearn wants ###',
        'y_gold = []',
        'y_pred = []',
        'for item in all_items:',
        '    y_gold.append(item["gold"])',
        '    y_pred.append(item["pred"])',
        '',
        '### Step 2: a small checker — is your number the same as sklearn\'s? ###',
        'TOL, results = 1e-9, []      # TOL: how close counts as "the same"',
        'def _chk(name, got, exp):',
        '    ok = abs(got - exp) < TOL   # compare sizes, not exact bits: floats wobble',
        '    results.append(ok)',
        '    print(("✅" if ok else "❌"), f"{name:<14} yours={got:.6f}  sklearn={exp:.6f}")',
        '',
        '### Step 3: run it on all four metrics you wrote ###',
        '_chk("precision", precision(tally),',
        '     precision_score(y_gold, y_pred, pos_label="yes", zero_division=0))',
        '_chk("recall", recall(tally),',
        '     recall_score(y_gold, y_pred, pos_label="yes", zero_division=0))',
        '_chk("f1", f1(tally),',
        '     f1_score(y_gold, y_pred, pos_label="yes", zero_division=0))',
        '_chk("cohen_kappa", kappa(tally), cohen_kappa_score(y_gold, y_pred))',
        '',
        '### Step 4: one overall verdict ###',
        'print("-" * 47)              # a divider line, 47 dashes long',
        'print(f"All {len(results)} checks passed ✅  — your metrics match scikit-learn."',
        '      if all(results) else',
        '      f"{results.count(False)} of {len(results)} checks FAILED — fix and re-run.")')]
    cells += [md(
        "::: {.callout-important}",
        "## This is the point of Part A",
        "`sklearn` is not doing anything you cannot do. It is doing **exactly what you just "
        "wrote** — faster, and for every class at once. From here on, when a report prints "
        "`0.36`, you know precisely which counts produced it.",
        ":::")]

    # ---- Part B · pass 2: the real six-class task, with scikit-learn ----
    cells += [md(
        "## Part B · Tutorial — the same job, six classes, with scikit-learn",
        "",
        "Drop the yes/no simplification. The real task is **A1 · A2 · B1 · B2 · C1 · C2**.",
        "",
        "- **4 cells → 36.** Counting by hand stops being reasonable.",
        "- Precision and recall are always *about one positive class*, so six classes give "
        "you **six** precisions, **six** recalls, **six** F1s.",
        "- The trick is small: to score `C1`, treat **`C1` as \"yes\" and the other five as "
        "\"no\"** — Part A, run six times. That is **one-vs-rest**, and it is all "
        "`classification_report` does.",
        "",
        "`ordered=True` tells `evaluate` that these labels sit on a **scale**, so it also "
        "reports **quadratic weighted κ** (see below).")]
    cells += [code(
        '# ordered=True: the six levels sit on a scale, so also report weighted κ',
        'evaluate(gold, predictions, ordered=True)')]
    cells += [md(
        "### Reading the report",
        "",
        "- Every **row** is one Part-A run: for `C1`, TP/FP/FN/TN with C1 as the positive class.",
        "- **`support`** is how many gold items that class has — 12 each, by design.",
        "- **`macro avg`** is the plain average of the six F1s: every class counts equally, "
        "**however rare it is**. That's the honest headline for an imbalanced set.",
        "",
        "**Brace yourself: overall accuracy is about 39%.** Before you conclude the model is "
        "useless, look at *how* it is wrong. Roughly **97% of its answers are within one "
        "level** of the gold label — only two sentences in the whole set miss by two, and "
        "nothing misses by more. A model guessing at random would scatter A1s against C2s. "
        "This one doesn't: it has the right idea and imprecise thresholds, which is a very "
        "different failure from not understanding the task — and no single accuracy number "
        "can tell the two apart.",
        "",
        "### Read the matrix *down the columns*",
        "",
        "Rows are gold, so *rows* tell you what happened to each true level. But read **down "
        "the columns** — how often the model *says* each level. The gold set is balanced, 12 "
        "per level, so an unbiased rater would use each label about 12 times.",
        "",
        "This one says **A2 twenty times** and **A1 four times**; it says **C2 exactly once** "
        "in 72 chances. Everything is squeezed toward the **middle of the scale**. Ask "
        "yourself why a rater — human or machine — under pressure to judge something as fuzzy "
        "as \"difficulty\" might drift to the middle and avoid committing to the extremes. "
        "That is your Part-A finding again: precision 0.89 but recall 0.67, because it "
        "under-uses the top of the scale. **You will meet this tendency in your own "
        "annotation work.**",
        "",
        "### Two κ values, same predictions",
        "",
        "Plain **κ = 0.27** (\"fair\" / \"minimal\") — because plain κ treats **A1 → A2 as "
        "exactly as wrong as A1 → C2**. Quadratic **weighted κ = 0.85** — because CEFR levels "
        "are **ordinal**, and a near miss *should* hurt less.",
        "",
        "::: {.callout-important}",
        "## Report the one that matches your labels",
        "Same predictions: 0.27 or 0.85, depending on a single argument. **Ordered labels → "
        "weighted κ. Unordered categories → plain κ.** State which you used and why — a κ "
        "without that sentence is unreadable. *(Arase et al. reported weighted κ = .628 on "
        "this task.)*",
        ":::")]
    cells += [md(
        "### Error analysis — the model's fault, or the scheme's?",
        "",
        "There are 44 misses — too many to read one by one, and you don't need to. Skim a "
        "dozen, then look specifically at the rows where the gold label is **C2** or **A1**: "
        "the ends of the scale are where this model disagrees with the gold most often, so "
        "that is where the interesting arguments are.",
        "",
        "For each miss you read, ask: is the **gold** defensible, or is this a genuinely "
        "borderline sentence? Would **you and your partner** have agreed on it? Would a "
        "**better-written scheme** have prevented the error? *\"Is the disagreement the "
        "model's fault or the scheme's?\"* is the heart of annotation work — and it's the "
        "question your mini-project has to answer honestly.")]
    cells += [code(
        'errors = show_errors(gold, predictions)   # a table of every item it got wrong',
        'errors.head(15)     # ...or errors[errors["gold"] == "C2"] to see the hard end')]
    cells += [md(
        "::: {.callout-note}",
        "## The question you ask decides the error you can see",
        "Look back at rows 19, 23 and 25 in step 1 — the three obituary sentences. In Part "
        "A's yes/no world the model got all three **right** (correctly \"not advanced\"). In "
        "six classes it called every one of them A2 instead of A1. Same predictions, same "
        "gold; a different question made a different error visible.",
        ":::")]

    cells += [submission(note=_DAY2_UPLOAD)]
    save("day2-s6_evaluation_metrics.ipynb", cells)


# ============================================================ DAY 3
def day3():
    cells = [how_to_use(
        3, "Day 3 · Prompt design & iteration",
        ("Tutorial", "improve a prompt through zero-shot → few-shot → chain-of-thought on "
                     "the SAME CEFR-SP task, comparing macro-F1 at each step."),
        ("Corpus Lab", "run your own prompt-iteration study and error analysis "
                       "(to be written)."))]

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
        "[Get a free Gemini API key](../resources/tools/gemini-api-key.md). "
        "When the setup cell prints `LLM backend: Gemini API (...)` you're set; if it still says "
        "`Colab Gemini`, your secret isn't set or its notebook-access toggle is off. Don't worry "
        "about rate limits crashing your loop — that's already handled, and explained right after "
        "Setup, below.",
        ":::")]
    cells += [md("### Setup — run this first")]
    day3_libs = ["load_gold", "run_prompt", "evaluate", "show_errors"]
    cells += [setup_cell(
        backend="api",         # Day 3 on: reproducible Gemini API (key), colab.ai fallback
        lib_names=day3_libs,
        gold_url=CEFR_GOLD_URL,
        gold_comment="CEFR-SP gold set (72 sentences, 12 per level), fetched from the course repo.",
        val_url=CEFR_VAL_URL)]

    # ---- staged walkthrough: the rate-limit guard quietly running in Setup ----
    cells += [md(
        "### Why your calls don't crash the lab — two different clocks",
        "",
        "The free tier limits you in **two independent ways**, on two different clocks:",
        "",
        "- **RPM** — requests per *minute*. A speed limit: how fast you're allowed to call.",
        "- **RPD** — requests per *day*. A fuel tank: how much you're allowed to use, total, "
        "today.",
        "",
        "A plain `for` loop over 72 sentences can blow through the RPM speed limit in the "
        "first few seconds — long before it's used any meaningful share of the day's fuel "
        "tank. This isn't hypothetical: while building this course, a loop tripped a 15-per-"
        "minute cap after only 16 calls in one minute, while just 126 of that day's 500-call "
        "budget had been used. The fix isn't \"use less\" — it's \"go slower, and know which "
        "kind of limit you hit.\"",
        "",
        "Your Setup cell above already has a guard built in that does exactly this. The rest "
        "of this section walks through it, piece by piece — you don't need it to keep "
        "working, but it's worth understanding what's protecting your Corpus Lab.")]

    cells += [md(
        "### Piece 1 — always leave a gap between calls (pacing)",
        "",
        "The simplest fix: never call the model faster than the speed limit allows. If the "
        "limit is 15 calls per minute, that's one call every `60 / 15 = 4` seconds — so before "
        "each call, check how long it's been since the *last* one, and wait out the "
        "difference.",
        "",
        "That means the function has to **remember** when the last call happened, across "
        "calls. Normally a function forgets everything the moment it returns — its local "
        "variables disappear. The `global` keyword is how you tell Python \"no, remember "
        "this one, and share it across every call.\" That's the only new keyword in this "
        "whole guard.",
        "",
        "Try it below — no model, no internet, just pacing:")]
    cells += [code(
        'import time',
        '',
        '### Step 1: two things to remember — when we last called, and how long to wait ###',
        '_demo_last_call = 0.0        # remembered BETWEEN calls, thanks to `global`',
        'DEMO_INTERVAL = 2            # seconds (the real guard uses 4.4s or 13.2s)',
        '',
        '### Step 2: before each call, wait out whatever time is still owed ###',
        'def wait_your_turn():',
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

    cells += [md(
        "### Piece 2 — if you still get told to slow down, wait and try again",
        "",
        "Pacing alone isn't quite enough — the server can still say \"too fast, try again "
        "later,\" and a network hiccup can raise an error for reasons that have nothing to "
        "do with rate limits at all. `try`/`except` is Python's way of saying: *try this, "
        "and if it breaks, do something else instead of crashing.*",
        "",
        "The something-else here depends on **what kind of failure it is**, which we can "
        "tell from the error message:",
        "",
        "- **Not rate-limit shaped at all** (a typo in your prompt, a dropped connection) — "
        "a real bug. Don't retry it; let it raise so you notice.",
        "- **Per-minute limit** — wait a bit and try again; the limit refills every minute, "
        "so this is temporary.",
        "- **Per-day limit** — retrying is pointless. It won't refill until tomorrow no "
        "matter how long you wait, so the guard gives up immediately with a clear message "
        "instead of silently hanging.",
        "",
        "A small demo — no model, just the `try`/`except` shape, retrying until it works:")]
    cells += [code(
        '### Step 1: a stand-in for the real model — it fails twice, then works ###',
        'attempt_count = 0            # how many times we have called it so far',
        '',
        'def flaky_call():',
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

    cells += [md(
        "### Putting the two pieces together",
        "",
        "\"Always wait a bit\" (piece 1) plus \"if told to slow down, wait longer and try "
        "again, but give up right away on a *daily* limit\" (piece 2) is **exactly** what's "
        "inside `generate_text` in the Setup cell above. You've been calling it since your "
        "very first prompt on Day 1, and it's been quietly protecting every call — it'll "
        "protect every Corpus Lab loop you write from here on, too.",
        "",
        "If you're curious to see the fancier version — one that also **remembers past "
        "answers so you never pay for the same prompt twice** — see "
        "[`resources/extra/handling-rate-limits.ipynb`](../resources/extra/handling-rate-limits.ipynb). "
        "It uses one more advanced idea we haven't covered yet (a function that builds and "
        "returns another function), but the underlying logic is identical to what you just "
        "read.")]

    cells += libs(*day3_libs)

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
        "Why bother? If you try five prompts on the 72 sentences and keep the one that scored "
        "highest, that score is no longer an estimate of how the prompt does on *new* "
        "sentences — you picked it *because* it suited those 72. The number is inflated and "
        "you have no way to say by how much. Tuning somewhere else and reporting once keeps "
        "the final figure honest. This is the split S7 introduced.")]
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
        "### Iteration 1 — few-shot   ✏️ YOU EDIT",
        "",
        "Add a few **labeled examples** so the model can pattern-match. The examples below "
        "are hand-written. If you want more, write your own — but never lift one from `val` "
        "or `gold`, or you are showing the model the answers to its own test.")]
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
        "`run_prompt` grabs the *first* CEFR level it sees in the reply. With chain-of-thought "
        "the model may mention a level mid-reasoning, so the parser can pick the wrong one — "
        "which is exactly why the prompt says *don't mention other levels*. If CoT scores "
        "*worse* than few-shot, check `show_errors` to see whether it's the model or the parser.",
        ":::")]
    cells += [md(
        "### Where is your best prompt still wrong?",
        "",
        "`show_errors` lists the sentences your chain-of-thought prompt got wrong — the raw "
        "material for the Corpus Lab below. Skim them and note which level is hardest, and "
        "whether any miss is really the *parser* grabbing the wrong level rather than the "
        "model being wrong.")]
    cells += [code(
        'errors = show_errors(val, pred_cot)   # every validation sentence the CoT prompt got wrong',
        'errors.head(15)                        # the first 15 of them')]
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
        "Pick your best prompt from the table above, and score it on the 72 sentences you "
        "have not touched all session. **This is the number you report.**",
        "",
        "Expect it to be *lower* than your validation score. That gap is not a mistake — it "
        "is the honest cost of having chosen a prompt by looking at results, and it is why "
        "the held-out set was kept back. A rule you can carry into the mini-project: if you "
        "run this cell, look at the answer, then go back and edit a prompt, the 72 items "
        "have stopped being held out. Tune on `val`, come back, run once.")]
    cells += [code(
        '# ✏️ swap in whichever of PROMPT_ZERO / PROMPT_FEWSHOT / PROMPT_COT scored best.',
        'BEST_PROMPT = PROMPT_COT',
        '',
        'pred_test = run_prompt(BEST_PROMPT, gold)   # the 72 held-out sentences',
        'evaluate(gold, pred_test, ordered=True)     # ← report THIS macro-F1')]

    # ---- Part B: Corpus Lab ----
    cells += [md(
        "## Part B · Corpus Lab — your own prompt-iteration study",
        "",
        "Part A handed you three prompts. Now you write the fourth, and — more importantly — "
        "you say **in advance** what you expect it to do.",
        "",
        "That is the whole discipline of this lab. Anyone can try ten prompts and keep the "
        "best. What makes it a *study* is that each change comes with a reason and a "
        "prediction, so that when the number moves you can say **why**. A change that helps "
        "for a reason you named is a finding. One that helps for no reason you can give is a "
        "lucky guess, and you cannot defend it in the Q&A.",
        "",
        "Everything here runs on `val`. The 72 held-out items stay closed.")]

    cells += [md(
        "### Step 1 · Find the model's worst class",
        "",
        "You do not need new code for this — `evaluate` already printed it. Scroll back to "
        "your best prompt's report and read **down the F1 column**: one or two levels will "
        "be far below the rest. That is where the macro-F1 is being lost, because macro-F1 "
        "averages the classes equally.",
        "",
        "Then run the cell below and **read three of the actual sentences** for that level. "
        "The counts tell you where the misses are; only the sentences tell you why. A level "
        "missed because its sentences are genuinely borderline needs a different fix from "
        "one missed because your prompt never described it.")]
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
        "thing, score it, keep or discard, then change the next.",
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
        "row in Step 1's report. Macro-F1 can rise while the level you aimed at gets *worse* "
        "— another level quietly improved and carried the average. So check the row you "
        "predicted, not the headline number.",
        "",
        "The table below lists what your prompt still gets wrong. If the same sentences are "
        "still there, your change missed them; if new ones appeared, you traded one error "
        "for another.")]
    cells += [code(
        'errors_mine = show_errors(val, pred_mine)',
        'errors_mine.head(15)')]

    cells += [md(
        "### Step 5 · Log it   ✏️ YOU EDIT",
        "",
        "Fill in the table. The last column is the one that matters: **was your prediction "
        "right?** \"No\" is a perfectly good answer and costs you nothing — an honest wrong "
        "prediction you can explain beats a right one you cannot.",
        "",
        "| # | Prompt change | Why I expected it to help | macro-F1 (val) | F1 for my target level | Prediction right? |",
        "|---|---|---|:--:|:--:|:--:|",
        "| 0 | *(Part A best — no change)* | — | … | … | — |",
        "| 1 | … | … | … | … | … |",
        "| 2 | … | … | … | … | … |",
        "",
        "If you have time, go round again: Steps 2–4 with one more change. Two logged "
        "iterations with reasons beat five undocumented ones.",
        "",
        "::: {.callout-important}",
        "## Do not re-run the held-out cell",
        "You scored the 72 items once, at the end of Part A. Running that cell again now — "
        "after choosing a prompt by looking at validation results — would report a number "
        "you tuned toward. Your mini-project repeats this whole loop on your own track's "
        "data, where the same rule applies.",
        ":::")]

    cells += [submission()]
    save("day3_prompt_design.ipynb", cells)


# ============================================================ DAY 4
def day4():
    cells = [how_to_use(
        4, "Day 4 · Pipeline assembly & sampling your gold set",
        ("Tutorial", "sample a balanced gold subset from a dataset pool, ready for QC."),
        ("Corpus Lab", "quality-control and adjudicate your sampled gold set "
                       "(to be written)."))]

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
        "## Part B · Corpus Lab — carry on in the project template",
        "",
        "You have just sampled a balanced subset. The next step — **QC and adjudication** — "
        "is the mini-project itself, and it happens in the project template rather than "
        "here, because it needs your group's own track and your own Drive:",
        "",
        "**[github.com/egumasa/lda2-final-template](https://github.com/egumasa/lda2-final-template)**"
        " → `notebooks/mini_project.ipynb`",
        "",
        "There, **step 2** does properly what you did by hand on Day 2 (S5): it builds a "
        "blind annotation sheet from your sample, two of you label it independently, you "
        "measure agreement and κ, and you adjudicate the rows you disagreed on. What comes "
        "out is *your* gold set — and it is what the model gets scored against, so the "
        "disagreements you resolve are doing real work, not bookkeeping.",
        "",
        "`sample_pool` in the template does the whole cell you just wrote, in one call. "
        "That is the point of today: you have seen what it does, so you can say what it "
        "does.",
        "",
        "Before you run anything there, your group needs a signed **`PLAN.md`** — see the "
        "[Final Project](../final-project/index.md) pages.")]

    cells += [submission()]
    save("day4_pipeline_and_sampling.ipynb", cells)


# ============================================================ DAY 5
# There is no Day-5 notebook. Day 5 is project work: groups run their own study in
# notebooks/mini_project.ipynb of the lda2-final-template repo, on their own track and
# their own gold set. The old day5_project_finalization.ipynb was a shell of todo()
# scaffolds pointing at that repo, and principles §3 forbids shipping dead scaffolding.
# What it needed to say now lives on the Final Project pages of the site.


if __name__ == "__main__":
    day1()
    day2_s5()          # Day 2 ships two notebooks — one per hands-on session
    day2_s6()
    day3()
    day4()
    print("ALL DONE ->", OUT)
