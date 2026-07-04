#!/usr/bin/env python3
"""Generate student-facing, Colab-runnable download+preprocess notebooks (one per dataset).

Pedagogy: cells are pre-written and heavily narrated; students RUN them and READ the code
(the "read visible Python" floor). Each notebook shows that the raw data format differs every
time, and walks download -> inspect raw -> reshape to {id,text,label} -> inspect labels -> save.
Stdlib only (no pip installs) so they run in a fresh Colab.
"""
import json
from pathlib import Path

OUT = Path("/Users/eguchi/Projects/linguistic-data-analysis-II-2026/"
           "sources/resources/code-examples/data/notebooks")
OUT.mkdir(parents=True, exist_ok=True)


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


SCHEMA_NOTE = (
    "Every dataset in this course is reshaped into the **same canonical schema** so one notebook "
    "works for all of them:\n\n"
    "```json\n"
    "[{\"id\": 1, \"text\": \"...\", \"label\": \"...\"}]\n"
    "```\n\n"
    "The *raw* data, though, looks different every time. **That difference is the lesson** — half "
    "of building a gold standard is getting messy real data into a clean, consistent shape."
)

SAVE_CELL = (
    "import json\n"
    "with open(OUT_FILE, \"w\", encoding=\"utf-8\") as f:\n"
    "    json.dump(gold, f, ensure_ascii=False, indent=2)\n"
    "print(f\"Saved {len(gold)} items to {OUT_FILE}\")\n"
    "gold[:3]  # preview the first three items"
)

BALANCE_CELL = (
    "# Build a small BALANCED gold set: an equal number of items per label.\n"
    "# Balance matters so precision/recall/F1 and the confusion matrix are meaningful.\n"
    "import random\n"
    "from collections import defaultdict\n"
    "\n"
    "PER_LABEL = 12          # how many items per label\n"
    "random.seed(42)         # fixed seed = same sample every run (reproducible)\n"
    "\n"
    "by_label = defaultdict(list)\n"
    "for item in rows:\n"
    "    by_label[item[\"label\"]].append(item)\n"
    "\n"
    "gold = []\n"
    "for label in sorted(by_label):\n"
    "    bucket = by_label[label]\n"
    "    random.shuffle(bucket)\n"
    "    gold.extend(bucket[:PER_LABEL])\n"
    "\n"
    "random.shuffle(gold)\n"
    "gold = [{\"id\": i + 1, \"text\": x[\"text\"], \"label\": x[\"label\"]} for i, x in enumerate(gold)]\n"
    "\n"
    "from collections import Counter\n"
    "print(\"items:\", len(gold), \"| per label:\", dict(Counter(x[\"label\"] for x in gold)))"
)

INSPECT_CELL = (
    "from collections import Counter\n"
    "counts = Counter(item[\"label\"] for item in rows)\n"
    "print(\"total items:\", len(rows))\n"
    "print(\"label counts:\", dict(counts))\n"
    "rows[:3]  # peek at the first three reshaped items"
)


def header(title, subtitle, what, license_line, citation, diff):
    return md(
        f"# {title}",
        "",
        f"*{subtitle}*",
        "",
        f"**What it is.** {what}",
        "",
        f"**Difficulty of the labeling judgment:** {diff}",
        "",
        f"**License:** {license_line}  ",
        f"**Cite:** {citation}",
        "",
        "---",
        "",
        SCHEMA_NOTE,
    )


# ===================================================================== CEFR-SP
save("download_cefr_sp.ipynb", [
    header(
        "CEFR-SP — download & preprocess",
        "The on-ramp dataset: sentence proficiency level (A1–C2)",
        "Single English sentences, each labeled with its CEFR level by language-education "
        "professionals. We use the openly-shipped **Wiki-Auto** portion.",
        "CC BY-SA 3.0 (Wiki-Auto portion)",
        "Arase, Uchida & Kajiwara (2022), *EMNLP*. github.com/yukiar/CEFR-SP",
        "★☆☆ — easy. Levels are concrete and annotators usually agree.",
    ),
    md("## Step 1 — Download the raw data",
       "",
       "The corpus lives in a GitHub repository, so we just clone it. (`!` runs a shell command "
       "from inside the notebook.)"),
    code("!git clone --depth 1 https://github.com/yukiar/CEFR-SP"),
    md("## Step 2 — Look at the raw format",
       "",
       "The Wiki-Auto files are **tab-separated text**, one sentence per line:",
       "",
       "```",
       "sentence <TAB> label_by_annotator_A <TAB> label_by_annotator_B",
       "```",
       "",
       "Labels are numbers: `1`=A1, `2`=A2, … `6`=C2. Let's print the first few raw lines."),
    code("raw_path = \"CEFR-SP/CEFR-SP/Wiki-Auto/CEFR-SP_Wikiauto_dev.txt\"\n"
         "with open(raw_path, encoding=\"utf-8\") as f:\n"
         "    sample = [next(f) for _ in range(5)]\n"
         "for line in sample:\n"
         "    print(repr(line))"),
    md("## Step 3 — Reshape into the canonical schema",
       "",
       "Three decisions, each a real gold-standard-building choice:",
       "",
       "1. **Trust only agreement.** We keep a sentence only when *both* annotators gave the same "
       "level — so every label is unambiguous (ideal for a first task).",
       "2. **Make labels human-readable.** Convert `1`→`A1`, …, `6`→`C2`.",
       "3. **Fit the schema.** Output `{id, text, label}`."),
    code("import glob\n"
         "\n"
         "CEFR = {\"1\": \"A1\", \"2\": \"A2\", \"3\": \"B1\", \"4\": \"B2\", \"5\": \"C1\", \"6\": \"C2\"}\n"
         "\n"
         "rows = []\n"
         "for path in glob.glob(\"CEFR-SP/CEFR-SP/Wiki-Auto/*.txt\"):\n"
         "    with open(path, encoding=\"utf-8\") as f:\n"
         "        for line in f:\n"
         "            parts = line.rstrip(\"\\n\").split(\"\\t\")\n"
         "            if len(parts) < 3:\n"
         "                continue\n"
         "            text, a, b = parts[0].strip(), parts[1].strip(), parts[2].strip()\n"
         "            if text and a == b and a in CEFR:      # keep only agreed labels\n"
         "                rows.append({\"text\": text, \"label\": CEFR[a]})\n"
         "\n"
         "print(\"kept\", len(rows), \"agreed sentences\")"),
    md("## Step 4 — Inspect the labels"),
    code(INSPECT_CELL),
    md("## Step 5 — Build a balanced gold set"),
    code(BALANCE_CELL),
    md("## Step 6 — Save it"),
    code("OUT_FILE = \"cefr_sentences.json\""),
    code(SAVE_CELL),
    md("---",
       "Done! You built `cefr_sentences.json` from raw research data. Next: use it in the "
       "**Day 2 tutorial** (annotation → evaluation)."),
])

# ===================================================================== RAAMove
save("download_raamove.ipynb", [
    header(
        "RAAMove — download & preprocess",
        "Discourse moves in research-article abstracts (8 moves)",
        "Sentences from research-article abstracts, each labeled with one of 8 rhetorical moves "
        "(Background, Gap, Method, Purpose, Result, Conclusion, Contribution, Implication).",
        "CC BY 4.0",
        "Liu et al. (2024), *LREC-COLING*. github.com/ljk1228/RAAMove",
        "★★★ — hard. Telling a *Gap* from *Background* needs rhetorical judgment.",
    ),
    md("## Step 1 — Download the raw data",
       "",
       "Clone the GitHub repository. The data is two JSON files (one per discipline area)."),
    code("!git clone --depth 1 https://github.com/ljk1228/RAAMove"),
    md("## Step 2 — Look at the raw format",
       "",
       "Each file is a list of objects with `idx` (which abstract), `text` (the sentence), and "
       "`labels` (a short move code, e.g. `BAC`)."),
    code("import json\n"
         "with open(\"RAAMove/Intelligence.json\", encoding=\"utf-8\") as f:\n"
         "    raw = json.load(f)\n"
         "print(\"sentences in this file:\", len(raw))\n"
         "raw[:3]"),
    md("## Step 3 — Reshape into the canonical schema",
       "",
       "Two decisions:",
       "",
       "1. **Combine both files** (both disciplines) into one dataset.",
       "2. **Expand the move codes** into readable names (`BAC`→`Background`) and fit `{id, text, "
       "label}`."),
    code("CODES = {\"BAC\": \"Background\", \"GAP\": \"Gap\", \"MTD\": \"Method\",\n"
         "         \"PUR\": \"Purpose\", \"RST\": \"Result\", \"CLN\": \"Conclusion\",\n"
         "         \"CTN\": \"Contribution\", \"IMP\": \"Implication\"}\n"
         "\n"
         "rows = []\n"
         "for fname in [\"RAAMove/Intelligence.json\", \"RAAMove/Engineering.json\"]:\n"
         "    with open(fname, encoding=\"utf-8\") as f:\n"
         "        for r in json.load(f):\n"
         "            rows.append({\"text\": r[\"text\"].strip(),\n"
         "                         \"label\": CODES.get(r[\"labels\"], r[\"labels\"])})\n"
         "\n"
         "print(\"combined sentences:\", len(rows))"),
    md("## Step 4 — Inspect the labels",
       "",
       "Notice the classes are **imbalanced** — there are far more `Method` sentences than "
       "`Implication`. That is why we balance before testing."),
    code(INSPECT_CELL),
    md("## Step 5 — Build a balanced gold set",
       "",
       "We take 8 per move here (8 moves × 8 = 64 items)."),
    code(BALANCE_CELL.replace("PER_LABEL = 12", "PER_LABEL = 8")),
    md("## Step 6 — Save it"),
    code("OUT_FILE = \"raamove_moves.json\""),
    code(SAVE_CELL),
    md("---",
       "You built `raamove_moves.json`. Use it in the **Day 3 tutorial** (replicating Kim & Lu)."),
])

# ===================================================================== CaRS-50
save("download_cars50.ipynb", [
    header(
        "CaRS-50 — download & preprocess",
        "The Kim & Lu replication: CARS move-steps in article introductions",
        "Sentences from 50 BioRxiv article *introductions*, each labeled with a Swales **CARS "
        "Move (1–3)** and **Step (a–d)** — the same scheme Kim & Lu (2024) used.",
        "CC BY 4.0",
        "Lam & Nnamoko (2025), Mendeley Data, doi:10.17632/kwr9s5c4nk.1",
        "★★★ — hard. The dataset's own expert agreement is only κ ≈ 0.43.",
    ),
    md("## Step 1 — Download the raw data",
       "",
       "This dataset is on **Mendeley Data** as 50 separate XML files. There is no single zip, so "
       "we ask Mendeley's public API for the list of files and download each one. (You don't need "
       "to understand every line — read it as: *get the file list, then loop and download*.)"),
    code("import urllib.request, json, os, time\n"
         "\n"
         "# Mendeley needs a normal browser User-Agent, so we add one to each request.\n"
         "def fetch(url):\n"
         "    req = urllib.request.Request(url, headers={\"User-Agent\": \"Mozilla/5.0\"})\n"
         "    return urllib.request.urlopen(req, timeout=60)\n"
         "\n"
         "os.makedirs(\"cars50\", exist_ok=True)\n"
         "meta = json.load(fetch(\"https://data.mendeley.com/public-api/datasets/kwr9s5c4nk\"))\n"
         "\n"
         "for f in meta[\"files\"]:\n"
         "    url = f[\"content_details\"][\"download_url\"]\n"
         "    dest = os.path.join(\"cars50\", f[\"filename\"])\n"
         "    for attempt in range(3):          # retry on the occasional dropped connection\n"
         "        try:\n"
         "            with fetch(url) as resp, open(dest, \"wb\") as out:\n"
         "                out.write(resp.read())\n"
         "            break\n"
         "        except Exception:\n"
         "            time.sleep(2)\n"
         "\n"
         "print(\"downloaded\", len(os.listdir(\"cars50\")), \"XML files\")"),
    md("## Step 2 — Look at the raw format",
       "",
       "Each file is **XML**. Inside, every sentence is a `<sentence>` element holding a `<text>` "
       "and a `<step>` code like `1b` (Move 1, Step b). Let's print the start of one file."),
    code("with open(\"cars50/text001.xml\", encoding=\"utf-8\") as f:\n"
         "    print(f.read()[:900])"),
    md("## Step 3 — Reshape into the canonical schema",
       "",
       "We parse the XML and pull out each sentence's text and code. Decision: for a first pass we "
       "use just the **Move** (the leading digit of the code) as the label — 3 classes instead of "
       "11. (The full Move+Step is a stretch goal.)"),
    code("import glob\n"
         "import xml.etree.ElementTree as ET\n"
         "\n"
         "rows = []\n"
         "for path in glob.glob(\"cars50/*.xml\"):\n"
         "    tree = ET.parse(path)\n"
         "    for sentence in tree.iter(\"sentence\"):\n"
         "        text_el = sentence.find(\"text\")\n"
         "        step_el = sentence.find(\"step\")\n"
         "        if text_el is None or step_el is None:\n"
         "            continue\n"
         "        text = (text_el.text or \"\").strip()\n"
         "        code = (step_el.text or \"\").strip()\n"
         "        if text and code and code[0].isdigit():\n"
         "            rows.append({\"text\": text, \"label\": f\"Move {code[0]}\"})\n"
         "\n"
         "print(\"sentences:\", len(rows))"),
    md("## Step 4 — Inspect the labels"),
    code(INSPECT_CELL),
    md("## Step 5 — Build a balanced gold set",
       "",
       "Three moves × 20 = 60 items."),
    code(BALANCE_CELL.replace("PER_LABEL = 12", "PER_LABEL = 20")),
    md("## Step 6 — Save it"),
    code("OUT_FILE = \"cars50_moves.json\""),
    code(SAVE_CELL),
    md("---",
       "You built `cars50_moves.json` — the open stand-in for Kim & Lu's data. Use it in the "
       "**Day 3 tutorial**.",
       "",
       "**Stretch:** change the label to the full code (`code` instead of `f\"Move {code[0]}\"`) "
       "for the 11-class Move+Step task and watch accuracy drop."),
])

# ============================================================ AutoErrorAnalyzer
save("download_autoerroranalyzer.ipynb", [
    header(
        "AutoErrorAnalyzer — download & preprocess",
        "L2 written-error annotation (and human-vs-tool comparison)",
        "Sentences from Japanese-EFL essays, each with a **human gold** error label. The same file "
        "also stores a published tool's predictions, so you can compare your LLM to both.",
        "see the OSF project (osf.io/jyf3r)",
        "Mizumoto (2025), *Studies in Second Language Acquisition*, 47(3), 867–884.",
        "★★★ — hard. Many error types; some sentences have several.",
    ),
    md("## Step 1 — Download the raw data",
       "",
       "The annotations live on the **OSF** project for the paper. We download one CSV directly "
       "by its OSF link."),
    code("import urllib.request\n"
         "urllib.request.urlretrieve(\"https://osf.io/download/gezat/\", \"data_category.csv\")\n"
         "print(\"downloaded data_category.csv\")"),
    md("## Step 2 — Look at the raw format",
       "",
       "It is a **CSV**. The columns we care about are `Sentence`, `Human_ErrorCategories` (the "
       "gold), and `AEA_ErrorCategories` (the tool's prediction). A sentence can carry several "
       "comma-separated error codes, or `NO_ERROR`."),
    code("import csv\n"
         "with open(\"data_category.csv\", encoding=\"utf-8-sig\", newline=\"\") as f:\n"
         "    reader = csv.DictReader(f)\n"
         "    print(\"columns:\", reader.fieldnames)\n"
         "    for i, row in enumerate(reader):\n"
         "        print(row[\"Sentence\"], \"|GOLD:\", row[\"Human_ErrorCategories\"],\n"
         "              \"|TOOL:\", row[\"AEA_ErrorCategories\"])\n"
         "        if i == 3:\n"
         "            break"),
    md("## Step 3 — Reshape into the canonical schema",
       "",
       "The 23 fine error codes are a lot for one task, so we **collapse** them into 3 broad "
       "families (plus *No error*). Decisions:",
       "",
       "1. Map each code to Grammatical / Lexical / Mechanical (`COARSE` below).",
       "2. Use the sentence's **first** error code as its label; `NO_ERROR` → `No error`.",
       "3. Skip sentences whose errors span more than one family (keeps the task single-label)."),
    code("COARSE = {}\n"
         "for c in \"ART PREP NUM TENSE VFORM WO AGR DET POSS MOD CONJ STRUCT\".split():\n"
         "    COARSE[c] = \"Grammatical\"\n"
         "for c in \"N ADJ ADV V REF EXPR\".split():\n"
         "    COARSE[c] = \"Lexical\"\n"
         "for c in \"SP MIS UNN CWS PUNC\".split():\n"
         "    COARSE[c] = \"Mechanical\"\n"
         "\n"
         "def to_label(human_field):\n"
         "    codes = [c.strip() for c in human_field.split(\",\") if c.strip()]\n"
         "    if not codes:\n"
         "        return None\n"
         "    if codes[0] == \"NO_ERROR\":\n"
         "        return \"No error\"\n"
         "    families = {COARSE.get(c) for c in codes} - {None}\n"
         "    return families.pop() if len(families) == 1 else None  # skip mixed sentences\n"
         "\n"
         "rows = []\n"
         "with open(\"data_category.csv\", encoding=\"utf-8-sig\", newline=\"\") as f:\n"
         "    for row in csv.DictReader(f):\n"
         "        text = (row[\"Sentence\"] or \"\").strip()\n"
         "        label = to_label((row[\"Human_ErrorCategories\"] or \"\").strip())\n"
         "        if text and label:\n"
         "            rows.append({\"text\": text, \"label\": label})\n"
         "\n"
         "print(\"sentences:\", len(rows))"),
    md("## Step 4 — Inspect the labels"),
    code(INSPECT_CELL),
    md("## Step 5 — Build a balanced gold set",
       "",
       "Four classes × 15 = 60 items."),
    code(BALANCE_CELL.replace("PER_LABEL = 12", "PER_LABEL = 15")),
    md("## Step 6 — Save it"),
    code("OUT_FILE = \"l2_errors.json\""),
    code(SAVE_CELL),
    md("---",
       "You built `l2_errors.json`. Because the raw file also has the tool's predictions, a great "
       "mini-project is to compare **your LLM vs. the human gold vs. the original tool**."),
])

# ===================================================================== ICNALE GRA
save("download_icnale_gra.ipynb", [
    header(
        "ICNALE GRA — download & preprocess",
        "Automated writing evaluation: holistic essay score bands",
        "Asian-learner English essays rated holistically by many trained raters. We turn the "
        "average rating into a Low/Mid/High band.",
        "research use — password-gated (registration required)",
        "Ishikawa, S. *The ICNALE Global Rating Archives.*",
        "★★☆ — moderate. Rubric-based, but raters disagree at the margins.",
    ),
    md("## Step 1 — Get access (this one is gated)",
       "",
       "Unlike the other datasets, ICNALE GRA is **not** a direct download. You must:",
       "",
       "1. Register on the [ICNALE download page](https://language.sakura.ne.jp/icnale/download.html) "
       "to receive a password.",
       "2. Download and unzip `ICNALE_GRA_2.x.zip`.",
       "3. From it, make a small spreadsheet with two columns — `text` (the essay) and `score` "
       "(its average holistic rating) — and save it as `essays_scores.csv`.",
       "",
       "Then upload that CSV here:"),
    code("from google.colab import files   # (Colab only)\n"
         "uploaded = files.upload()        # choose your essays_scores.csv"),
    md("## Step 2 — Look at the raw format",
       "",
       "Your CSV should have a `text` column and a numeric `score` column."),
    code("import csv\n"
         "with open(\"essays_scores.csv\", encoding=\"utf-8-sig\", newline=\"\") as f:\n"
         "    reader = csv.DictReader(f)\n"
         "    print(\"columns:\", reader.fieldnames)\n"
         "    for i, row in enumerate(reader):\n"
         "        print(row)\n"
         "        if i == 2:\n"
         "            break"),
    md("## Step 3 — Reshape into the canonical schema",
       "",
       "Decision: turn the continuous score into three **bands**. Adjust the cut-offs to match the "
       "rubric you downloaded."),
    code("def band(score):\n"
         "    s = float(score)\n"
         "    if s < 4:\n"
         "        return \"Low\"\n"
         "    elif s < 7:\n"
         "        return \"Mid\"\n"
         "    return \"High\"\n"
         "\n"
         "rows = []\n"
         "with open(\"essays_scores.csv\", encoding=\"utf-8-sig\", newline=\"\") as f:\n"
         "    for row in csv.DictReader(f):\n"
         "        text = (row.get(\"text\") or \"\").strip()\n"
         "        score = (row.get(\"score\") or \"\").strip()\n"
         "        if text and score:\n"
         "            rows.append({\"text\": text, \"label\": band(score)})\n"
         "\n"
         "print(\"essays:\", len(rows))"),
    md("## Step 4 — Inspect the labels"),
    code(INSPECT_CELL),
    md("## Step 5 — Build a balanced gold set"),
    code(BALANCE_CELL.replace("PER_LABEL = 12", "PER_LABEL = 20")),
    md("## Step 6 — Save it"),
    code("OUT_FILE = \"icnale_gra_scores.json\""),
    code(SAVE_CELL),
    md("---",
       "You built `icnale_gra_scores.json` for an automated-writing-evaluation mini-project."),
])

print("ALL DONE ->", OUT)
