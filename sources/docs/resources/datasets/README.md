# Replication datasets

This folder holds the **open, expert-annotated datasets** used in the LLM annotation/evaluation
strand of the course (Days 2–5), all reshaped into one schema so a single notebook works for
every one of them.

**Start here:**

- **Building a gold set** → open a notebook in [`notebooks/`](./notebooks/) and run it in Colab.
  See [How to use the download notebooks](#how-to-use-the-download-notebooks) below.
- **Browsing the datasets** → the published catalog page is [`index.md`](./index.md).
- **Licenses & citations** → [`SOURCES.md`](./SOURCES.md). **Always cite the original dataset.**

## What each file is for

| File | What it does | When you'd open it |
|------|--------------|--------------------|
| [`index.md`](./index.md) | The published catalog page — all 5 datasets, difficulty ratings, links to the tutorials | Choosing a dataset |
| [`mini-project-tracks.md`](./mini-project-tracks.md) | Three starter tracks for the final mini-project | Planning your mini-project |
| [`notebooks/download_*.ipynb`](./notebooks/) (5) | One Colab walkthrough per dataset: download → inspect → reshape → save | Building a gold set — **start here** |
| `README.md` | This file — what lives here and how to run it | Getting oriented |
| [`SOURCES.md`](./SOURCES.md) | Licenses, citations, and manual-download steps for each dataset | Citing a dataset, or fetching a gated one |
| `gold/*_<task>.json` | Balanced 60–72-item **gold sets** for the worked tutorials | Following a Day 2–5 tutorial |
| `gold/*_pool.json` | The **full datasets**, for building a larger or differently-balanced gold set | Mini-project work |
| [`prep_datasets.py`](./prep_datasets.py) | Builds every `gold/*.json` in one pass (Python standard library only) | You want all datasets at once instead of one notebook at a time |
| [`prep_datasets.ipynb`](./prep_datasets.ipynb) | Notebook wrapper around the builder: build + schema validator | Checking that every gold file matches the schema |
| `_generate_student_notebooks.py` | Regenerates the 5 download notebooks from shared templates | Changing what the notebooks say — never edit a notebook by hand |
| `raw/` | The original downloads, exactly as published — git-ignored | Comparing a gold file against its source |
| `.gitignore` | Ignores `raw/` and `gold/*`, except `gold/cefr_sentences.json` | Rarely |

```
datasets/
├── index.md                      ← dataset catalog (published page)
├── mini-project-tracks.md        ← mini-project starter tracks (published page)
├── README.md                     ← this file
├── SOURCES.md                    ← per-dataset licenses, citations, download steps
├── notebooks/                    ← download notebooks: one walkthrough per dataset
│   ├── download_cefr_sp.ipynb
│   ├── download_raamove.ipynb
│   ├── download_cars50.ipynb
│   ├── download_autoerroranalyzer.ipynb
│   └── download_icnale_gra.ipynb
├── prep_datasets.py              ← batch builder: rebuild ALL gold files at once
├── prep_datasets.ipynb           ← notebook wrapper (build + validate)
├── _generate_student_notebooks.py← regenerates the download notebooks above
├── .gitignore
├── raw/                          ← original downloads (git-ignored)
└── gold/                         ← derived gold files (git-ignored; rebuild locally)
```

## The canonical schema

Every gold file is a flat list in the same shape. This is the one idea that ties the whole
folder together — you only ever change the *prompt*, the *label set*, and the *gold file*:

```json
[
  {"id": 1, "text": "However, little is known about ...", "label": "Gap"},
  {"id": 2, "text": "We therefore investigated ...",      "label": "Purpose"}
]
```

## How to use the download notebooks

**Getting raw data and shaping it into a gold standard is itself a core skill in this course** —
not a chore done for you. So each dataset has its own notebook that walks through the same six
steps:

1. **Download** the raw data
2. **Look at the raw format** — every dataset ships differently (TSV, JSON, XML, CSV)
3. **Reshape** it into the canonical `{id, text, label}` schema
4. **Inspect** the label counts
5. **Sample a balanced gold set** (with `random.seed(42)`, so your result is reproducible)
6. **Save** it as JSON

All five notebooks use only the Python standard library — **no `pip install`, no setup**.

### Opening a notebook in Colab

Click a **Open in Colab** link, then choose **Runtime ▸ Run all**. It takes about 1–2 minutes.

| Dataset | Open in Colab | Produces |
|---------|---------------|----------|
| CEFR-SP | [download_cefr_sp.ipynb](https://colab.research.google.com/github/egumasa/linguistic-data-analysis-II-2026/blob/main/sources/resources/datasets/notebooks/download_cefr_sp.ipynb) | `cefr_sentences.json` (72 items) |
| RAAMove | [download_raamove.ipynb](https://colab.research.google.com/github/egumasa/linguistic-data-analysis-II-2026/blob/main/sources/resources/datasets/notebooks/download_raamove.ipynb) | `raamove_moves.json` (64 items) |
| CaRS-50 | [download_cars50.ipynb](https://colab.research.google.com/github/egumasa/linguistic-data-analysis-II-2026/blob/main/sources/resources/datasets/notebooks/download_cars50.ipynb) | `cars50_moves.json` (60 items) |
| AutoErrorAnalyzer | [download_autoerroranalyzer.ipynb](https://colab.research.google.com/github/egumasa/linguistic-data-analysis-II-2026/blob/main/sources/resources/datasets/notebooks/download_autoerroranalyzer.ipynb) | `l2_errors.json` (60 items) |
| ICNALE GRA | [download_icnale_gra.ipynb](https://colab.research.google.com/github/egumasa/linguistic-data-analysis-II-2026/blob/main/sources/resources/datasets/notebooks/download_icnale_gra.ipynb) | `icnale_gra_scores.json` |

*(Prefer the raw files? They are in [`notebooks/`](./notebooks/).)*

### Seeing the data

You don't need any extra step to look at the data — the notebook shows it to you three times:

- **Step 2** prints the first few *raw* lines, exactly as the original researchers published them
- **Step 4** prints the label counts and the first three reshaped items
- **Step 6** previews the finished gold set

Reading those three outputs *is* the point of the walkthrough. The lesson you should feel:
every dataset's raw format is different, and getting it into one clean shape is half the work
of building a gold standard.

**One exception:** `download_icnale_gra.ipynb` has no download step. ICNALE is password-gated,
so that notebook starts by asking you to upload your own copy, and it only runs in Colab.

### Getting your file out of Colab

⚠️ **Your notebook saves the JSON into the Colab session, which is deleted the moment the
runtime disconnects.** If you close the tab without doing one of the following, your file is
gone and you'll have to run the notebook again.

**Option A — download it to your computer.** In the Colab sidebar on the left, click the
📁 **Files** icon, find your `.json` file, then right-click it → **Download**. (The file only
appears after Step 6 has run; click the ⟳ refresh button if you don't see it.)

**Option B — save it to Google Drive (recommended for this course).** Do this if you'll reuse
the file in the Day 2–5 tutorials, which is the normal case. See
[Housing Your Data in Google Drive](../tools/google-drive-data.md) for how.

### If you have Python on your own machine

Optional, and *not* the main path — but if you already have Python installed and want all the
datasets at once, [`prep_datasets.py`](./prep_datasets.py) builds every gold file in one
command. It uses only the standard library, so there is **nothing to install — no `uv`, no
`pip install`**:

```bash
cd sources/resources/datasets
python3 prep_datasets.py            # build all available datasets
python3 prep_datasets.py raamove    # or just one
```

You need Python 3, `git` (RAAMove and CEFR-SP are fetched with `git clone`), and a clone of
this repository — that last one, not Python, is the real hurdle. Output lands in `gold/` next
to the script. Two datasets need their raw files placed by hand first (`l2_errors` and
`icnale_gra`) — see [`SOURCES.md`](./SOURCES.md).

Why this is a footnote rather than the main route: the script does all the reshaping
invisibly. You get the files, but you skip the skill the notebooks are there to teach.

## The datasets at a glance

| Source dataset | Phenomenon | Gold files (items) | License | Status |
|----------------|-----------|--------------------|---------|--------|
| **CEFR-SP** (Wiki-Auto) | Sentence CEFR level A1–C2 | `cefr_sentences.json` (72), `cefr_pool.json` (3,183) | CC BY-SA 3.0 | ✅ built |
| **RAAMove** | 8 moves in RA abstracts | `raamove_moves.json` (64), `raamove_pool.json` (3,069) | CC BY 4.0 | ✅ built |
| **CaRS-50** | CARS Move/Step in RA intros | `cars50_moves.json` (60), `cars50_pool.json` (1,297), `cars50_step_pool.json` (1,297) | CC BY 4.0 | ✅ built |
| **AutoErrorAnalyzer** | L2 error type / detection | `l2_errors.json` (60), `l2_error_detection.json` (60), `l2_errors_pool.json` (1,038) | OSF | ✅ built |
| **ICNALE GRA** | Holistic essay score band | `icnale_gra_scores.json` | research use (password) | ⛔ manual download |

### Per-dataset preparation notes

- **CEFR-SP** — the on-ramp (easy to judge). Built from the openly-shipped **Wiki-Auto** portion;
  we keep only sentences where **both annotators agreed**, giving unambiguous labels. (The Newsela
  portion is access-gated and not used.)
- **RAAMove** — cleanest *discourse* dataset (tidy JSON). 8-move scheme; κ = 0.785. Best first
  move-analysis task.
- **CaRS-50** — the **Kim & Lu replication** (same Swales CARS scheme, in RA introductions). Default
  is the 3-class **Move** task; the 11-class **Move+Step** pool is a stretch. The dataset's own
  expert κ ≈ 0.43 — a built-in lesson that the task is genuinely hard.
- **AutoErrorAnalyzer** (Mizumoto, 2025) — built from the OSF `Analysis/data_category.csv`, which
  contains each sentence's **human gold** *and* the **published tool's predictions**, so you can
  benchmark your LLM against both. The 23 error codes are collapsed to 4 broader classes
  (Grammatical / Lexical / Mechanical / No error) via `L2_COARSE` in the builder; sentences spanning
  >1 broader category are dropped for a clean single-label task. A binary detection set is also made.
- **ICNALE GRA** — password-gated. Once registered and downloaded, export a `text,score` CSV to
  `raw/icnale_gra/essays_scores.csv` and re-run the builder; scores are banded into Low/Mid/High.

## Rebuilding every dataset at once

```bash
cd sources/resources/datasets
uv run --no-project python prep_datasets.py            # build all available datasets
uv run --no-project python prep_datasets.py raamove    # build just one
```

`raamove`, `cars50`, and `cefr` auto-download (RAAMove via `git clone`, CaRS-50 via the Mendeley
public API, CEFR via `git clone`). `l2_errors` and `icnale_gra` need their raw files placed under
`raw/` first — see [`SOURCES.md`](./SOURCES.md) for exact steps.

`_generate_student_notebooks.py` regenerates all five download notebooks from templates —
**any hand-edit to a notebook is overwritten when it runs**, so change the generator, not the
notebook.

Note that each download notebook carries its *own* copy of the reshaping logic (e.g. `COARSE` in
the AutoErrorAnalyzer notebook mirrors `L2_COARSE` in `prep_datasets.py`). Editing one does not
change the other — keep them in sync by hand.

## Design choices

- **Reproducible & auditable.** All shaping lives in `prep_datasets.py` (stdlib only — the repo
  declares no dependencies). **No datasets are committed** — both `raw/` downloads and the derived
  `gold/*.json` are git-ignored; rebuild them locally with the prep script or the download notebooks,
  with sources cited in `SOURCES.md`.
- **Fixed-seed sampling.** Gold sets are sampled with `SEED = 42` so rebuilds are deterministic.
- **Balanced gold sets.** Tutorial gold files hold an equal number of items per label, so confusion
  matrices and per-class F1 are meaningful from the start.
- **Two difficulty axes.** Datasets are chosen to separate *easy-to-judge* tasks (CEFR) from
  *hard-to-judge* research tasks (moves, errors), so you learn the pipeline before facing
  genuine annotation ambiguity.

## Validation

`prep_datasets.ipynb` (and the build output) checks every gold file against the canonical schema:
unique `id`s, non-empty `text`, non-empty `label`, and (where applicable) labels drawn from the
declared set. Current build: all 10 gold files valid.
