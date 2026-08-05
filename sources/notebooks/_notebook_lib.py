#!/usr/bin/env python3
"""The generated cells of the day notebooks, and the code that builds them.

The notebooks themselves are the source of truth — you edit them directly. Two
kinds of cell are the exception, because they carry rules a notebook cannot keep
for itself:

  * the 📦 Setup cell, which imports only what its day uses, and
  * each 🔧 Library cell, which ships only the helpers the next step calls.

Those cells carry an `lda2` block in their cell metadata recording which builder
made them and with which arguments. `_sync_notebooks.py` reads that metadata and
rewrites the cell's source from it, so the two rules above hold whatever was typed
into the cell.

See planning/course_planning/notebook-coding-principles.md for the rules, and
sources/notebooks/index.md for the authoring loop.
"""
# The helpers at the end of this file are ordinary Python, and their annotations name
# pandas and other things not installed here. This keeps annotations unevaluated, so the
# file still loads. Nothing in it is ever called locally — `libs()` reads it as text.
from __future__ import annotations

from pathlib import Path

# ------------------------------------------------------------------ cell helpers
def md(*lines):
    return {"cell_type": "markdown", "metadata": {}, "source": _src(lines)}


def code(*lines):
    return {"cell_type": "code", "metadata": {}, "execution_count": None,
            "outputs": [], "source": _src(lines)}


def _src(lines):
    text = "\n".join(lines)
    return [l + "\n" for l in text.split("\n")][:-1] + [text.split("\n")[-1]]


# The metadata key that marks a cell as built rather than written. `_sync_notebooks.py`
# looks for exactly this, and rebuilds the cell from the arguments stored alongside it —
# so the arguments live in the notebook, not in a call site in some other file.
LDA2 = "lda2"

# Printed as the second line of every cell this module builds. The code in those cells is
# real and readable, which is exactly what makes them look editable — and `load_gold`
# alone appears in four notebooks, so an edit typed into one of them would be replaced by
# the next sync. The line says so where the mistake would be made.
GENERATED_NOTE = ("# Generated from _notebook_lib.py — edit there, not here; "
                  "changes to this cell are replaced.")


def generated(cell, builder, **arguments):
    """Mark a cell as built by `builder` from `arguments`, and record both."""
    cell["metadata"] = dict(cell["metadata"])
    cell["metadata"][LDA2] = {"generated": builder, **arguments}
    return cell


def build(spec):
    """Rebuild one generated cell from its own `lda2` metadata.

    Args:
        spec: the contents of a cell's `lda2` metadata block.

    Returns:
        The rebuilt cell, metadata included.
    """
    arguments = {k: v for k, v in spec.items() if k != "generated"}
    builder = spec["generated"]
    if builder == "setup":
        return generated(setup_cell(**arguments), builder, **arguments)
    if builder == "libs":
        return generated(libs(*arguments["names"])[0], builder, **arguments)
    raise KeyError(f"unknown generated-cell builder: {builder!r}")


REPO_RAW = ("https://raw.githubusercontent.com/egumasa/"
            "linguistic-data-analysis-II-2026/main/sources/resources/datasets/gold")
CEFR_GOLD_URL = f"{REPO_RAW}/cefr_sentences.json"
# The pool Day 3 splits into train/valid/test and Day 4 samples from. NOT
# cefr_pool.json — that one is 3,183 items and
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
#     Colab-only by design — it is a 6-line cell, and a student who opens Day 1
#     outside Colab gets a plain ImportError naming google.colab rather than a
#     branch about API keys they have not been given yet (that arrives on Day 3).
#   * API_BACKEND (Day 3+)   → the Gemini API with temperature=0 + seed, for
#     reproducible, autograded work. Prefers a key (Colab Secrets or env), and
#     falls back to colab.ai if none is set.
# Pinned model: gemini-3.1-flash-lite (15 RPM / 500 RPD). NOT gemini-2.5-flash: its
# free tier is 5 RPM / 20 RPD, so one 72-item lab run needs 3.5 days of quota.
# See planning/course_planning/api-preflight-testing.md Task 1.

# The keyless demo backend (Day 1) is two lines: an import, and the call students
# make themselves. There is no course-written wrapper on Day 1 at all — `ai.generate_text`
# IS the call, so the first thing a student runs is a real library function rather than
# something we defined for them off-screen. `generate_text(...)` as a bare name arrives
# on Day 3, where the API backend defines it and reproducibility earns the indirection.
DEMO_BACKEND = '''# --- LLM backend: Colab's free built-in Gemini (no API key) -------------------
from google.colab import ai      # Colab's built-in Gemini — nothing to set up'''

# The reproducible API backend (Day 3+): key preferred, colab.ai fallback, plus a
# rate-limit guard (pacing + retry) — walked through piece by piece in Day 3.
# Three defs on purpose: _resolve_gemini_key, _raw_generate_text (one per backend
# branch), and generate_text. The error checks are inline, so the whole path from
# "run the cell" to "call the model" reads top to bottom.
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

### Step 2: pick a backend — your API key if you have one, else Colab's demo model ###
_key = _resolve_gemini_key()
if _key:
    from google import genai
    from google.genai import types
    _client = genai.Client(api_key=_key)       # your own connection to the API

    def _raw_generate_text(prompt: str, json_reply: bool = False,
                           schema: dict | None = None) -> str:
        # temperature=0 + a fixed seed = the same prompt gives the same answer every
        # run, which is what makes the autograded Corpus Labs reproducible.
        # json_reply=True turns on JSON mode: the reply is valid JSON, in whatever
        # shape the prompt asks for. A schema goes further and enforces one shape.
        if schema is not None:
            cfg = types.GenerateContentConfig(temperature=0, seed=42,
                                              response_mime_type="application/json",
                                              response_schema=schema)
        elif json_reply:
            cfg = types.GenerateContentConfig(temperature=0, seed=42,
                                              response_mime_type="application/json")
        else:
            cfg = types.GenerateContentConfig(temperature=0, seed=42)
        return _client.models.generate_content(model=MODEL_ID, contents=prompt,
                                               config=cfg).text  # prompt in, text out
    _backend = f"Gemini API ({MODEL_ID}, temperature=0, seed=42)"
    _min_interval = 4.4    # keeps us under gemini-3.1-flash-lite's 15-per-minute cap
else:
    try:
        from google.colab import ai            # Colab's built-in Gemini — no key

        def _raw_generate_text(prompt: str, json_reply: bool = False,
                               schema: dict | None = None) -> str:
            # colab.ai has no JSON mode and no schemas — both requests are ignored
            # here, so replies are not guaranteed JSON and run_prompt logs "??" for
            # ones it cannot read. Another reason Day 3 asks for a key.
            return ai.generate_text(prompt)
        _backend = "Colab Gemini (demo, non-reproducible)"
        _min_interval = 13.2   # colab.ai publishes no rate limit — pace conservatively
    except ImportError:        # no key AND not in Colab — nothing to call
        raise RuntimeError(
            "No LLM backend found. Run this notebook in Google Colab (free built-in "
            "Gemini, no key needed), or set GEMINI_API_KEY — in Colab via the Secrets "
            "panel, or as an environment variable when running locally. "
            "See resources/tools/gemini-api-key.md.")

### Step 3: the one function you call all week — pace, ask, and retry if told to ###
_last_call_time = 0.0   # generate_text remembers & updates this with `global`

def generate_text(prompt: str, max_retries: int = 5, json_reply: bool = False,
                  schema: dict | None = None) -> str:
    """Send a prompt to the model and give back its reply.

    It waits between calls so we stay under the free tier's speed limit, and tries
    again if the server tells us to slow down.

    Args:
        prompt: the text to send to the model.
        max_retries: how many times to try again after a rate-limit message.
        json_reply: True asks for JSON mode — the reply is valid JSON; say the
            shape you want in the prompt itself.
        schema: a reply shape to enforce (the optional last section of Day 3).
            None = nothing enforced.

    Returns:
        The model's reply, as text — JSON text when json_reply is True or a
        schema was given.

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
            return _raw_generate_text(prompt, json_reply, schema)   # success — hand the reply back
        except Exception as error:
            text = str(error).lower()           # the error message, as lowercase text
            if not ("429" in text or "quota" in text or "rate limit" in text):
                raise                           # a real bug — don't hide it
            if "per day" in text:               # the PER-DAY cap — waiting won't help
                raise RuntimeError(
                    "Daily quota used up for today — waiting won't help until it "
                    "resets. Come back tomorrow, or ask your instructor.") from error
            if attempt == max_retries:
                raise                           # we've been patient enough
            print(f"  (rate limited — waiting before trying again, attempt {attempt+1})")
            time.sleep(_min_interval * (attempt + 2))   # wait longer each time round
    raise RuntimeError("Still rate-limited after several tries.")'''


def setup_cell(backend=None, lib_names=(), gold_url=None, gold_comment=None,
               predictions_url=None, val_url=None, pool_url=None, pool_comment=None,
               sampling=False, sklearn_direct=False):
    """Build a day's 📦 Setup cell, importing ONLY what that day uses.

    backend    : "demo" (Day 1), "api" (Day 3+), or None (Days 2 & 4 — no model).
    lib_names  : which 🔧 pipeline cells the day ships (drives which imports load).
    gold_url / predictions_url : optionally append GOLD_URL+LEVELS / PREDICTIONS_URL.
    val_url    : the fixed validation set a day tunes prompts on, so the gold set
                 stays a held-out test set.
    pool_url   : the pool a day draws its own sets from (Day 3 splits it into
                 train/valid/test with `split_pool`). Emitted as POOL_URL + LEVELS.
    sampling   : the day draws its own sample with student-written `random` calls.
                 S5 uses this in step A. Day 3 does NOT — its draw goes through the
                 `split_pool` helper, which pulls `random` in via lib_names instead.
    sklearn_direct : the day calls scikit-learn in its own cells rather than through a
                 helper, so the imports cannot be read off `lib_names`. S6 Part B uses
                 this: it names classification_report, cohen_kappa_score and
                 confusion_matrix itself, having built those metrics by hand in Part A.
                 Day 3 needs no flag for its student-built `evaluate`: the sklearn
                 imports sit in a visible teaching cell there, not in Setup.
    """
    lib_names = set(lib_names)
    simple = []                                   # single-line `import x` modules
    if backend == "api":
        simple += ["os", "time"]   # no `re`: the backend's error checks are substring tests
    if sampling or "split_pool" in lib_names:
        simple += ["random"]
    # backend == "demo" needs no imports at all — the colab.ai import is in DEMO_BACKEND.
    if lib_names & {"load_gold", "predictions"} or gold_url or predictions_url or pool_url:
        simple += ["json", "urllib.request"]
    if "run_prompt" in lib_names:
        simple += ["re"]
    # The sheets helpers draw a confusion matrix too (annotator-vs-annotator), so they
    # need the same plotting stack as `evaluate` — but not classification_report.
    sheets_names = {n for n in lib_names if n.startswith("sheets")}
    want_report = "evaluate" in lib_names or sklearn_direct
    want_matrix = bool(lib_names & {"evaluate"} or sheets_names) or sklearn_direct
    want_viz = bool(lib_names & {"evaluate", "show_errors"} or sheets_names) or sklearn_direct

    lines = ['#@title 📦 Setup — run me first { display-mode: "form" }',
             "# Helper — you don't need to read this. Run it and move on.",
             GENERATED_NOTE]
    if simple:
        lines.append("import " + ", ".join(sorted(set(simple))))
    if want_report:
        lines.append("from sklearn.metrics import (classification_report, confusion_matrix,")
        if "evaluate" in lib_names:   # evaluate returns macro-F1 via f1_score
            lines.append("                             cohen_kappa_score, f1_score)")
        else:
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
    if pool_url:
        src += (f'\n\n# {pool_comment}\n'
                f'POOL_URL = "{pool_url}"')
        if not gold_url:              # LEVELS comes with whichever URL block runs first
            src += '\nLEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]'
    if val_url:
        src += (f'\nVAL_URL  = "{val_url}"   '
                '# 24 items to tune on, so GOLD_URL stays held out')
    if predictions_url:
        src += f'\nPREDICTIONS_URL = "{predictions_url}"   # frozen model predictions'

    status = "Setup done."
    if backend == "demo":
        status += " Colab's built-in Gemini is ready."   # no _backend variable on Day 1
    elif backend:
        status += " LLM backend: {_backend}."
    if want_matrix:
        status += " scikit-learn ready."
    # Day 1's status line has nothing to interpolate, and an `f` on a brace-less string
    # is exactly the confusion step 8 teaches students to spot. Only use it when needed.
    prefix = "f" if "{" in status else ""
    src += f'\n\nprint({prefix}"{status}")'
    return code(src)


# The 🔧 pipeline "library" cells. Each day ships only the ones it calls, selected
# by name through libs(...) — see the LIB registry below. All are collapsed form
# cells flagged "helper — you don't need to read this"; their internals are kept
# readable (explicit loops, minimal regex) for the curious.
_HELPER_NOTE = "# Helper — you don't need to read this. Run it and move on."


# Each 🔧 helper below is ordinary Python, so an editor checks it and you can read it
# without counting quotes. `libs()` slices a named section back out of this file's own
# text and wraps it as a notebook cell. The marker line carries two things: the name a
# day requests, and the caption listed at the top of the built cell.
_MARKER = "# === "


def _sections():
    """name → (caption, code) for every `# === name :: caption ===` block below.

    Read as text rather than by importing, so a helper can refer to pandas, seaborn or
    google.colab — none of which are installed here — without this file failing to load.
    The helpers are only ever printed into a notebook; nothing calls them here.
    """
    found, name, caption, body = {}, None, None, []
    for line in Path(__file__).read_text(encoding="utf-8").split("\n"):
        if not (line.startswith(_MARKER) and line.endswith(" ===")):
            if name:
                body.append(line)
            continue
        if name:
            found[name] = (caption, "\n".join(body).strip("\n"))
        header = line[len(_MARKER):-4].strip()
        name = None if header == "end" else header.partition(" :: ")[0]
        caption = header.partition(" :: ")[2]
        body = []
    return found


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
    sections = _sections()
    signatures = [sections[name][0] for name in names]
    return [code(
        '#@title 🔧 Library cell: %s { display-mode: "form" }'
        % ", ".join(s.split("(")[0].strip() for s in signatures),
        _HELPER_NOTE,
        GENERATED_NOTE,
        *["#   " + s for s in signatures],
        "",
        "\n\n\n".join(sections[name][1] for name in names))]


# --------------------------------------------------------- the 🔧 helpers themselves
# Ordinary module-level Python from here down. Nothing imports or runs it; `libs()`
# reads it as text. Edit a helper here and every day that ships it updates on the next
# `_sync_notebooks.py` run.
#
# One dependency between sections: `sheets_auth` carries _sheets_client and
# `sheets_base` the column constants, so whichever S5 step loads first must request
# both — in S5 that is step D.

# === load_gold :: load_gold(url_or_path) → gold ===
def load_gold(url_or_path: str) -> list[dict[str, str]]:
    """Read the canonical gold JSON: [{'id','text','label'}, ...].

    Args:
        url_or_path: a web address, or the path to a file on this machine.

    Returns:
        The gold items, each a dict with "id", "text" and "label".

    Example:
        >>> gold = load_gold(GOLD_URL)
    """
    if str(url_or_path).startswith("http"):                 # a web address?
        raw = urllib.request.urlopen(url_or_path).read().decode("utf-8")  # download it
        gold = json.loads(raw)                              # JSON text -> list of dicts
    else:                                                   # otherwise a file on disk
        gold = json.loads(open(url_or_path, encoding="utf-8").read())
    print(f"Loaded {len(gold)} items. First one:", gold[0])  # proof it worked
    return gold

# === run_prompt :: run_prompt(prompt, gold) → predictions ===
# Day 3 defines run_prompt in a visible cell, built up on screen; this section is the
# shippable copy and must say the same thing. Edit both or neither.
# The reply shape is asked for in the prompt itself (a line like
# `Reply as JSON, like: {{"label": "B1"}}`); json_reply=True guarantees it parses.
def run_prompt(prompt: str, gold: list[dict[str, str]]) -> list[str]:
    """Send each item's `text` to the LLM via {text}, collect predicted labels.

    Args:
        prompt: your prompt, containing {text} where the sentence should go. It
            should ask for a JSON reply with a "label" field — see Part A, step 1.
        gold: the items to label, each with a "text" key.

    Returns:
        One predicted label per gold item, in the same order. "??" marks a reply
        no label could be read out of.

    Example:
        >>> predictions = run_prompt(PROMPT, valid)
    """
    predictions = []                                  # answers, in gold order
    for i, item in enumerate(gold, 1):                # i counts 1, 2, 3, ...
        reply = generate_text(prompt.format(text=item["text"]), json_reply=True)
        try:
            answer = json.loads(reply)                # JSON text -> a Python dict
        except json.JSONDecodeError:                  # not JSON (keyless backend)
            answer = {}
        label = answer.get("label", "??")             # "??" = no label in the reply
        if label not in LEVELS:                       # not one of the six levels?
            label = "??"
        predictions.append(label)
        if i % 12 == 0:                               # every 12th item...
            print(f"  ...{i}/{len(gold)} done")       # ...show progress
    print(f"Got {len(predictions)} predictions.")
    return predictions

# === evaluate :: evaluate(gold, predictions) → macro-F1 + report + κ + confusion matrix ===
# Day 3 builds evaluate in class from a skeleton; this section is the shippable copy
# and the completed answer. Edit both or neither. Matches the project template's
# helpers/scoring.py, which also returns the macro-F1.
def evaluate(gold: list[dict[str, str]],
             predictions: list[str],
             ordered: bool = False) -> float:
    """Score predictions against gold: per-class P/R/F1 + macro, Cohen's κ, and a
    confusion-matrix heatmap.

    ordered=True adds QUADRATIC WEIGHTED κ — use it only when the labels sit on a
    scale (A1 < A2 < ... < C2), so that a near miss counts as a smaller error than
    a far one. For unordered categories, plain κ is the one to report.

    Args:
        gold: the gold items, each with a "label" key.
        predictions: one predicted label per gold item, in the same order.
        ordered: True when the labels sit on a scale.

    Returns:
        The macro-F1, as a number, so a round's score can be kept. The report, the
        κ values and the matrix are printed either way.

    Example:
        >>> f1_by_round["1 zero-shot"] = evaluate(valid, predictions, ordered=True)
    """
    ### Step 1: line the two label lists up, gold first ###
    y_true = []                          # the correct labels, from the gold set
    for item in gold:
        y_true.append(item["label"])
    y_pred = predictions                 # the model's labels, in the same order

    ### Step 2: per-class precision / recall / F1, as a text table ###
    print(classification_report(y_true, y_pred, labels=LEVELS, zero_division=0))

    ### Step 3: one overall number — agreement corrected for chance ###
    print(f"Cohen's kappa            {cohen_kappa_score(y_true, y_pred):.3f}")
    if ordered:                          # only when the labels sit on a scale
        weighted = cohen_kappa_score(y_true, y_pred, labels=LEVELS,
                                     weights="quadratic")   # near misses hurt less
        print(f"Cohen's kappa (weighted) {weighted:.3f}   <- labels are ordered")

    ### Step 4: draw the same information as a picture ###
    cm = confusion_matrix(y_true, y_pred, labels=LEVELS)   # counts per gold/pred pair
    plt.figure(figsize=(5.5, 4.5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",     # annot=True writes the counts
                xticklabels=LEVELS, yticklabels=LEVELS)
    plt.xlabel("Predicted"); plt.ylabel("Gold"); plt.title("Confusion matrix")
    plt.tight_layout(); plt.show()

    ### Step 5: one number to keep — handed back to whoever called ###
    macro_f1 = f1_score(y_true, y_pred, labels=LEVELS, average="macro",
                        zero_division=0)   # the report's "macro avg" F1, as a number
    print(f"F1 (macro)               {macro_f1:.3f}")
    return macro_f1

# === split_pool :: split_pool(pool, train_per_level, valid_per_level, test_per_level, seed) → train, valid, test ===
def split_pool(pool: list[dict[str, str]], train_per_level: int,
               valid_per_level: int, test_per_level: int,
               seed: int = 42) -> tuple[list[dict[str, str]],
                                        list[dict[str, str]],
                                        list[dict[str, str]]]:
    """Draw three disjoint, level-balanced sets from the pool.

    Each set gets the same number of items per CEFR level, drawn without
    replacement — no item appears in two sets. The seed makes the draw
    repeatable: same pool, same numbers, same seed = same three sets.

    Args:
        pool: the items to draw from, each with a "label" key.
        train_per_level: items per level for the train set (few-shot examples).
        valid_per_level: items per level for the validation set (tune here).
        test_per_level: items per level for the test set (scored once, at the end).
        seed: fixes the randomness so the draw is repeatable.

    Returns:
        Three lists: train, valid, test.

    Raises:
        ValueError: when a level has fewer items than the three sizes add up to.

    Example:
        >>> train, valid, test = split_pool(pool, 2, 4, 6, seed=42)
    """
    rng = random.Random(seed)             # a private, seeded random-number source
    need = train_per_level + valid_per_level + test_per_level
    train, valid, test = [], [], []
    for level in LEVELS:
        stock = []                        # every pool item with this level
        for item in pool:
            if item["label"] == level:
                stock.append(item)
        if len(stock) < need:
            raise ValueError(
                f"Not enough {level} items: the pool has {len(stock)}, but the three "
                f"sizes add up to {need} per level. Make one of the sets smaller.")
        drawn = rng.sample(stock, need)   # `need` distinct items, in random order
        train += drawn[:train_per_level]
        valid += drawn[train_per_level:train_per_level + valid_per_level]
        test  += drawn[train_per_level + valid_per_level:]
    print(f"train {len(train)} · valid {len(valid)} · test {len(test)} items "
          f"({train_per_level}/{valid_per_level}/{test_per_level} per level)")
    return train, valid, test

# === show_errors :: show_errors(gold, predictions) → misclassified table ===
def show_errors(gold: list[dict[str, str]], predictions: list[str]) -> pd.DataFrame:
    """The items the model got wrong, as a table you can read and argue about.

    Args:
        gold: the gold items, each with "id", "text" and "label".
        predictions: one predicted label per gold item, in the same order.

    Returns:
        A table with one row per mistake: id, gold, pred, text.

    Example:
        >>> show_errors(gold, predictions)
    """
    rows = []
    for g, p in zip(gold, predictions):   # walk gold and predictions side by side
        if g["label"] != p:               # keep only the disagreements
            rows.append({"id": g["id"], "gold": g["label"], "pred": p, "text": g["text"]})
    print(f"{len(rows)} of {len(gold)} wrong.")
    # Name the columns even when there are no rows. A table built from an empty list has
    # no columns at all, and then errors["gold"] fails for a student whose prompt got
    # everything right.
    return pd.DataFrame(rows, columns=["id", "gold", "pred", "text"])   # Colab shows a table

# === predictions :: load_predictions(url_or_path) → predictions ===
def load_predictions(url_or_path: str) -> list[str]:
    """Read a frozen predictions list — a committed URL or a local path.

    Args:
        url_or_path: a web address, or the path to a file on this machine.

    Returns:
        One predicted label per gold item, in gold order.

    Example:
        >>> predictions = load_predictions(PREDICTIONS_URL)
    """
    if str(url_or_path).startswith("http"):                 # a web address?
        raw = urllib.request.urlopen(url_or_path).read().decode("utf-8")  # download it
        predictions = json.loads(raw)                       # JSON text -> list
    else:                                                   # otherwise a file on disk
        predictions = json.loads(open(url_or_path, encoding="utf-8").read())
    print(f"Loaded {len(predictions)} frozen predictions.")
    return predictions

# === sheets_auth :: connect to Google Sheets ===
def _sheets_client():
    """Authorise gspread with your Google account (a pop-up asks for permission).

    Returns:
        A logged-in connection to Google Sheets.

    Raises:
        RuntimeError: when signing in from your own computer fails.
    """
    ### Step 1: in Colab, use the Google account you are already signed in with ###
    try:
        from google.colab import auth
        import google.auth, gspread
        auth.authenticate_user()           # the pop-up: "let Colab use your Sheets"
        creds, _ = google.auth.default()   # the permission slip that pop-up produced
        return gspread.authorize(creds)    # a logged-in connection to Google Sheets
    except ImportError:                    # `google.colab` only exists inside Colab
        pass

    ### Step 2: on your own computer, let gspread do its own sign-in ###
    import gspread
    try:
        return gspread.oauth()
    except Exception as error:
        raise RuntimeError(
            "Could not sign in to Google Sheets from this computer.\n"
            "This step is written for Google Colab, where your Google account is "
            "already available — open the notebook there and it will work with no "
            "setup.\n"
            "To run it here instead, gspread needs a credentials file first: "
            "https://docs.gspread.org/en/latest/oauth2.html\n"
            f"The error was: {error}") from error

# === sheets_base :: read one tab of your annotation sheet ===
# Sheet column headers (the annotation template uses these exact names):
COL_ID, COL_TEXT = "ID", "Text"
COL_A, COL_B = "CoderA", "CoderB"
COL_FINAL, COL_NOTES = "Final", "Note"
ANNOTATION_HEADER = [COL_ID, COL_TEXT, COL_A, COL_B, COL_FINAL, COL_NOTES]

def load_annotation_sheet(sheet_id: str,
                          worksheet: str = "round1") -> list[dict[str, str]]:
    """Read one TAB of your annotation sheet back as a list of row dicts.

    Opening by id or URL always opens the exact sheet, so two copies that share a
    name (\"Copy of ...\") are never confused. Each round lives in its own tab, so
    re-annotating in round2 never overwrites round1.

    Args:
        sheet_id: the long id in the sheet's URL
            (docs.google.com/spreadsheets/d/<THIS PART>/edit). The whole URL works too.
        worksheet: the TAB name — one tab per annotation round.

    Returns:
        One dict per row, keyed by the column headings (ID, Text, CoderA, ...).

    Raises:
        ValueError: when the sheet has no tab by that name. The message lists the
            tabs it does have.

    Example:
        >>> rows = load_annotation_sheet(SHEET_ID, worksheet="round1")
    """
    ### Step 1: open the sheet — a pasted URL and a bare id both work ###
    client = _sheets_client()
    if str(sheet_id).startswith("http"):
        sheet = client.open_by_url(sheet_id)
    else:
        sheet = client.open_by_key(sheet_id)

    ### Step 2: find the tab (the "round") — and say which tabs exist if it is missing ###
    try:
        ws = sheet.worksheet(worksheet)
    except Exception:
        tabs = [w.title for w in sheet.worksheets()]   # what IS in this sheet
        raise ValueError(f"No tab named {worksheet!r}. Tabs in this sheet: {tabs}")

    ### Step 3: read every row as a dict keyed by the header names ###
    rows = ws.get_all_records()        # [{"ID": 1, "Text": "...", "CoderA": "B1", ...}, ...]
    print(f"Read {len(rows)} rows from tab '{worksheet}'.")
    return rows

# === sheets_pairs :: labelled_pairs(rows) → the labels you BOTH chose ===
def labelled_pairs(rows: list[dict[str, str]],
                   a: str = COL_A,
                   b: str = COL_B) -> tuple[list[str], list[str]]:
    """The two annotators' labels, keeping only the rows BOTH of them labelled.

    A row one of you has not reached yet is not a disagreement, so it is left out
    rather than counted. The three functions below all start by calling this, which
    is why each of them can be run on its own.

    Args:
        rows: the rows read back by load_annotation_sheet.
        a: the column holding the first annotator's labels.
        b: the column holding the second annotator's labels.

    Returns:
        Two lists of the same length: annotator A's labels, annotator B's labels.

    Example:
        >>> a_labels, b_labels = labelled_pairs(rows)
    """
    a_labels = []
    b_labels = []
    for row in rows:
        label_a = str(row[a]).strip()           # .strip() drops the spaces a sheet adds
        label_b = str(row[b]).strip()
        if label_a != "" and label_b != "":     # skip the rows only one of you reached
            a_labels.append(label_a)
            b_labels.append(label_b)
    return a_labels, b_labels


# === sheets_percent :: calc_percentage_agreement(rows) → how often you matched ===
def calc_percentage_agreement(rows: list[dict[str, str]],
                              a: str = COL_A,
                              b: str = COL_B) -> float | None:
    """How often the two of you chose the same label.

    This counts every match, including the ones two annotators would hit by luck
    alone — which is why it is always higher than the κ below it.

    Args:
        rows: the rows read back by load_annotation_sheet.
        a: the column holding the first annotator's labels.
        b: the column holding the second annotator's labels.

    Returns:
        The proportion of doubly-labelled rows you matched on, or None when no row
        has both annotators filled in.

    Example:
        >>> agreement = calc_percentage_agreement(rows)
    """
    a_labels, b_labels = labelled_pairs(rows, a, b)   # rows you BOTH labelled
    if len(a_labels) == 0:
        print("No rows where BOTH annotators have labelled. Nothing to compare yet.")
        return None
    matches = 0
    for i in range(len(a_labels)):
        if a_labels[i] == b_labels[i]:
            matches = matches + 1
    percent = matches / len(a_labels)
    print(f"{len(a_labels)} doubly-annotated · agreement {percent:.1%}")
    return percent


# === sheets_kappa :: calc_cohen_kappa(rows) → the same, minus the luck ===
def calc_cohen_kappa(rows: list[dict[str, str]],
                     a: str = COL_A,
                     b: str = COL_B) -> float | None:
    """The same comparison, with agreement-by-luck subtracted.

    Two annotators who both lean on the same label agree often without the scheme
    doing any work. Cohen's κ takes that luck out, so it is the number to trust —
    recall S4, where 80% raw agreement was only κ ≈ 0.52.

    Args:
        rows: the rows read back by load_annotation_sheet.
        a: the column holding the first annotator's labels.
        b: the column holding the second annotator's labels.

    Returns:
        Cohen's κ, or None when no row has both annotators filled in.

    Example:
        >>> kappa = calc_cohen_kappa(rows)
    """
    from sklearn.metrics import cohen_kappa_score
    a_labels, b_labels = labelled_pairs(rows, a, b)   # rows you BOTH labelled
    if len(a_labels) == 0:
        print("No rows where BOTH annotators have labelled. Nothing to compare yet.")
        return None
    kappa = cohen_kappa_score(a_labels, b_labels)
    print(f"{len(a_labels)} doubly-annotated · Cohen's κ {kappa:.3f}")
    return kappa


# === sheets_plot_confusion :: plot_confusion(rows) → which labels you confuse ===
def plot_confusion(rows: list[dict[str, str]],
                   a: str = COL_A,
                   b: str = COL_B) -> None:
    """Draw WHICH labels the two of you confuse, not just how often.

    The diagonal is where you agreed; an off-diagonal cell is a label pair whose
    boundary your scheme has not made decidable yet. That cell is your worklist for
    step E. Same kind of picture evaluate() draws for gold against a model.

    Args:
        rows: the rows read back by load_annotation_sheet.
        a: the column holding the first annotator's labels.
        b: the column holding the second annotator's labels.

    Returns:
        Nothing. It shows the matrix.

    Example:
        >>> plot_confusion(rows)
    """
    a_labels, b_labels = labelled_pairs(rows, a, b)   # rows you BOTH labelled
    if len(a_labels) == 0:
        print("No rows where BOTH annotators have labelled. Nothing to compare yet.")
        return None
    labels = sorted(set(a_labels) | set(b_labels))   # every label either of you used
    cm = confusion_matrix(a_labels, b_labels, labels=labels)
    plt.figure(figsize=(5.5, 4.5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=labels, yticklabels=labels)
    plt.xlabel("Annotator B"); plt.ylabel("Annotator A")   # diagonal = you agreed
    plt.title("Annotator-vs-annotator confusion matrix")
    plt.tight_layout(); plt.show()

# === sheets_disagree :: disagreements(rows) → the rows to argue about ===
def disagreements(rows: list[dict[str, str]],
                  a: str = COL_A,
                  b: str = COL_B) -> pd.DataFrame:
    """The rows your two annotators labelled differently — your adjudication list.

    Args:
        rows: the rows read back by load_annotation_sheet.
        a: the column holding the first annotator's labels.
        b: the column holding the second annotator's labels.

    Returns:
        A table of the rows where the two annotators chose different labels.

    Example:
        >>> disagreements(rows)
    """
    # keep a row only if both annotators labelled it AND they chose differently:
    out = [r for r in rows
           if str(r.get(a, "")).strip() and str(r.get(b, "")).strip()
           and str(r[a]).strip() != str(r[b]).strip()]
    print(f"{len(out)} rows to adjudicate. Agree on a `Final` label for each in the sheet.")
    return pd.DataFrame(out)

# === sheets_canonical :: to_canonical(rows, labels) → gold ===
def to_canonical(rows: list[dict[str, str]],
                 labels: list[str],
                 column: str = COL_FINAL) -> list[dict[str, str]]:
    """Turn annotation rows into canonical gold: [{"id","text","label"}, ...].

    Blank rows are skipped; labels outside `labels` are reported, not silently kept.

    Args:
        rows: the rows read back by load_annotation_sheet.
        labels: the labels your scheme allows. Anything else is reported as invalid.
        column: which column holds the agreed label.

    Returns:
        The usable rows as gold items, each {"id", "text", "label"}.

    Example:
        >>> my_gold = to_canonical(rows, LEVELS)
    """
    ### Step 1: sort every row into one of three piles ###
    gold, blank, invalid = [], 0, []     # usable rows · not labelled yet · typos
    for row in rows:
        label = str(row.get(column, "")).strip()   # .strip() drops stray spaces
        if not label:
            blank += 1                    # nobody has filled this row in yet
        elif label not in labels:
            invalid.append((row.get(COL_ID), label))   # e.g. "b1" or "B11"
        else:
            gold.append({"id": int(row[COL_ID]), "text": str(row[COL_TEXT]), "label": label})

    ### Step 2: report all three counts, so nothing is dropped silently ###
    print(f"{len(gold)} usable · {blank} still blank · {len(invalid)} invalid")
    if invalid:
        print("  fix these in the sheet, then re-run:", invalid[:10])   # first 10
    return gold

# === sheets_compare :: compare_to_published(gold, published) → how often you two agree ===
def compare_to_published(gold: list[dict[str, str]],
                         published: list[dict[str, str]]) -> pd.DataFrame | None:
    """How often does YOUR final label match the published gold, item by item?

    Items are matched by their TEXT, not their id, because a sampled set is often
    renumbered from 1 — and matching those ids against the original set would pair
    your item 7 with their item 7: two unrelated sentences, and a percentage that
    means nothing. (Ids are still used as a fallback, in case a text was edited.)

    Args:
        gold: your own gold items, from to_canonical.
        published: the published gold items, from load_gold.

    Returns:
        A table of the items where you and the published gold differ, or None
        when nothing could be matched.

    Example:
        >>> compare_to_published(my_gold, published)
    """
    ### Step 1: index the published labels by text, and by id as a fallback ###
    label_by_text = {}
    label_by_id = {}
    for item in published:
        label_by_text[str(item["text"])] = item["label"]
        label_by_id[item["id"]] = item["label"]

    ### Step 2: pair each of your items with its published label ###
    matched = []
    for item in gold:
        text = str(item["text"])
        if text in label_by_text:
            theirs = label_by_text[text]
        elif item["id"] in label_by_id:
            theirs = label_by_id[item["id"]]
        else:
            continue                       # not in the published set at all
        matched.append({"id": item["id"], "yours": item["label"],
                        "published": theirs, "text": item["text"]})
    if len(matched) == 0:
        print("None of your items could be matched to the published set.")
        return None

    ### Step 3: count the matches, then show only the rows where you differ ###
    agree = 0
    differences = []
    for row in matched:
        if row["yours"] == row["published"]:
            agree = agree + 1
        else:
            differences.append(row)
    print(f"{agree}/{len(matched)} match the published label "
          f"({agree / len(matched):.1%})")
    return pd.DataFrame(differences)

# === sheets_create :: create_annotation_sheet(title, items, labels) → url ===
def create_annotation_sheet(title: str,
                            items: list[dict[str, str]],
                            labels: list[str]) -> str:
    """Create a Sheet in YOUR Drive: one row per item, blank columns to label.

    Any existing label on an item is deliberately NOT copied across, so you
    annotate blind.

    Args:
        title: the name to give the new spreadsheet.
        items: the items to annotate, each with "id" and "text".
        labels: the labels your scheme allows, printed as a reminder.

    Returns:
        The URL of the sheet it created.

    Example:
        >>> url = create_annotation_sheet("Group 1 gold", items, LEVELS)
    """
    ### Step 1: make an empty spreadsheet in your own Drive ###
    sheet = _sheets_client().create(title)
    worksheet = sheet.sheet1
    worksheet.update_title("round1")   # first round lives in the 'round1' tab

    ### Step 2: one row per item — id and text filled in, label columns left blank ###
    rows = []
    for item in items:
        #                id            text          CoderA CoderB Final Note
        rows.append([item["id"], item["text"], "", "", "", ""])

    ### Step 3: write it all in one go, then pin the header row ###
    worksheet.update([ANNOTATION_HEADER] + rows)   # header first, then the data
    worksheet.freeze(rows=1)                       # header stays put as you scroll
    print(f"Created '{title}' with {len(rows)} rows in tab 'round1'.")
    print("Allowed labels:", ", ".join(labels))
    print("Open it:", sheet.url)
    return sheet.url

# === pair_up :: pair_up(gold, predictions, positive) → items ===
def pair_up(gold: list[dict[str, str]],
            predictions: list[str],
            positive: list[str]) -> list[dict[str, str]]:
    """Pair each gold item with the model's prediction, both collapsed to yes/no.

    Args:
        gold: the gold items, each with "id", "text" and "label".
        predictions: one predicted label per gold item, in the same order.
        positive: the labels that count as "yes" (e.g. ["C1", "C2"]).

    Returns:
        One dict per item: {"id", "text", "gold", "pred"}, where "gold" and
        "pred" are each "yes" or "no".

    Example:
        >>> items = pair_up(gold, predictions, ["C1", "C2"])
    """
    items = []
    for g, p in zip(gold, predictions):   # gold item and its prediction, side by side
        items.append({"id": g["id"],
                      "text": g["text"],
                      # six CEFR levels collapse to two answers: "yes" or "no"
                      "gold": "yes" if g["label"] in positive else "no",
                      "pred": "yes" if p in positive else "no"})
    print(f"Paired {len(items)} items. Positive class = {positive}.")
    return items

# === show_2x2 :: show_2x2(tally) → the four counts as a square ===
def show_2x2(tally: dict[str, int]) -> None:
    """Print a tally of TP/FP/FN/TN as a confusion matrix — rows are the gold
    label, columns are the prediction. No arithmetic: the same four numbers,
    arranged so you can see where the errors went.

    Args:
        tally: how many items fell into each outcome, e.g. {"TP": 3, "FP": 1}.
            A missing outcome counts as 0.

    Returns:
        Nothing. It prints the square.

    Example:
        >>> show_2x2(tally)
    """
    # .get(..., 0) so a missing outcome shows as 0 rather than crashing:
    tp = tally.get("TP", 0)
    fp = tally.get("FP", 0)
    fn = tally.get("FN", 0)
    tn = tally.get("TN", 0)
    # :<9 pads a label to 9 characters, :>9 right-aligns a number in 9 — that is all
    # the f-strings below are doing: lining the four counts up into a square.
    print(f"{'':<9}{'pred yes':>9}{'pred no':>9}")     # column headings
    print(f"{'gold yes':<9}{tp:>9}{fn:>9}")              # top row:    TP  FN
    print(f"{'gold no':<9}{fp:>9}{tn:>9}")               # bottom row: FP  TN

# === your_gold :: load_your_gold(path, fallback_url) → your gold, or the published one ===
def load_your_gold(path: str, fallback_url: str) -> list[dict[str, str]]:
    """Load the gold set you saved in S5, and fall back to the published one.

    S5's last step writes your adjudicated labels to your Drive. If that file is
    there, this reads it and you score the model against your own labels. If it is
    not — you did not save it, or Drive is not mounted — you get the published
    CEFR-SP set instead, and the notebook still runs from top to bottom.

    Args:
        path: where S5 saved your gold set, e.g. the Drive path in the cell above.
        fallback_url: the published gold set, used when `path` is not readable.

    Returns:
        The gold items, each {"id", "text", "label"}.

    Example:
        >>> gold = load_your_gold(MY_GOLD_PATH, GOLD_URL)
    """
    try:
        gold = load_gold(path)
        print(f"→ scoring against YOUR gold set ({len(gold)} items).")
        return gold
    except OSError:                      # no such file, or Drive not mounted
        print(f"No file at {path} — falling back to the published gold set.")
        gold = load_gold(fallback_url)
        print(f"→ scoring against the PUBLISHED gold set ({len(gold)} items).")
        return gold

# === predictions_for :: predictions_for(gold, published, predictions) → predictions in YOUR order ===
def predictions_for(gold: list[dict[str, str]],
                    published: list[dict[str, str]],
                    predictions: list[str]) -> tuple[list[dict[str, str]], list[str]]:
    """Line the frozen predictions up with YOUR gold items, matching on text.

    The frozen predictions are one label per *published* item, in published order.
    Your own gold set is a sample of those sentences, renumbered from 1, so
    position 3 of yours and position 3 of theirs are two unrelated sentences.
    Matching on the text pairs each of your items with the answer the model gave
    for that same sentence. Items whose text is not in the published set have no
    frozen prediction and are dropped, with a count.

    Args:
        gold: your gold items, from load_your_gold.
        published: the published gold items, from load_gold(GOLD_URL).
        predictions: the frozen predictions, in published order.

    Returns:
        Two lists of the same length: your matched items, and their predictions.

    Example:
        >>> gold, predictions = predictions_for(gold, published, predictions)
    """
    ### Step 1: which prediction belongs to which sentence? ###
    pred_by_text = {}
    for i, item in enumerate(published):
        if i < len(predictions):                  # published and predictions run together
            pred_by_text[str(item["text"])] = predictions[i]

    ### Step 2: keep the items we have a frozen answer for ###
    matched, matched_predictions = [], []
    for item in gold:
        text = str(item["text"])
        if text in pred_by_text:
            matched.append(item)
            matched_predictions.append(pred_by_text[text])

    dropped = len(gold) - len(matched)
    print(f"{len(matched)} of your {len(gold)} items have a frozen prediction.")
    if dropped:
        print(f"  {dropped} dropped — not in the published set, so no answer was frozen for them.")
    return matched, matched_predictions

# === end ===
