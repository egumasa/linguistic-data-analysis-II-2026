# Replication datasets — data preparation

This directory holds the **open, expert-annotated datasets** used in the LLM annotation/evaluation
strand of the course (Days 2–5), reshaped into one schema so a single notebook works for all of
them. This README documents what was prepared, why, and how to rebuild it.

> Student-facing catalog & tutorials: [`../replication-datasets.md`](../replication-datasets.md).
> Licenses & citations: [`SOURCES.md`](./SOURCES.md).

## Why this exists

The course teaches students to use an LLM to **annotate** linguistic data and **evaluate** it
against a human gold standard (precision / recall / F1 / confusion matrix). That needs real,
openly licensed, expert-annotated data. The motivating study — **Kim & Lu (2024)**, on using
ChatGPT for rhetorical move-step annotation — has **no open replication data**, so we assembled a
menu of open datasets that cover the same kinds of tasks (including an open stand-in for Kim & Lu).

## Canonical schema

Every gold file is a flat list in the course's single schema — students only ever change the
*prompt*, *label set*, and *gold file*:

```json
[
  {"id": 1, "text": "However, little is known about ...", "label": "Gap"},
  {"id": 2, "text": "We therefore investigated ...",      "label": "Purpose"}
]
```

## Directory layout

```
data/
├── README.md                     ← this file
├── SOURCES.md                    ← per-dataset licenses, citations, download steps
├── prep_datasets.py              ← instructor builder: rebuild ALL gold files (stdlib only)
├── prep_datasets.ipynb           ← instructor notebook wrapper (build + validate)
├── _generate_student_notebooks.py← regenerates the student notebooks below
├── notebooks/                    ← STUDENT notebooks: one download+preprocess walkthrough per dataset
│   ├── download_cefr_sp.ipynb
│   ├── download_raamove.ipynb
│   ├── download_cars50.ipynb
│   ├── download_autoerroranalyzer.ipynb
│   └── download_icnale_gra.ipynb
├── .gitignore                    ← ignores raw/, gold/, __pycache__
├── raw/                          ← original downloads (git-ignored; regenerate, don't commit)
└── gold/                         ← derived gold files in canonical schema (git-ignored; rebuild locally)
```

### Two audiences

- **Students** run `notebooks/download_<dataset>.ipynb` — Colab-ready, stdlib only, heavily narrated.
  Each walks through *download → inspect the raw format → reshape to `{id,text,label}` → check label
  balance → save*. They are meant to be **run and read**, not authored from scratch (the course's
  "read visible Python" floor). The recurring lesson: every dataset's raw format differs, and tidying
  it is half of gold-standard construction.
- **Instructors** run `prep_datasets.py` to rebuild every gold file at once (same logic, batched).

- **`*_<task>.json`** (e.g. `raamove_moves.json`) = balanced **~60–72 item gold sets** for the
  worked tutorials.
- **`*_pool.json`** = the **full dataset**, for building larger / differently-balanced gold sets in
  mini-projects.

## What was prepared

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
  contains each sentence's **human gold** *and* the **published tool's predictions**, so students can
  benchmark their LLM against both. The 23 error codes are collapsed to 4 broader classes
  (Grammatical / Lexical / Mechanical / No error) via `L2_COARSE` in the builder; sentences spanning
  >1 broader category are dropped for a clean single-label task. A binary detection set is also made.
- **ICNALE GRA** — password-gated. Once registered and downloaded, export a `text,score` CSV to
  `raw/icnale_gra/essays_scores.csv` and re-run the builder; scores are banded into Low/Mid/High.

## How to rebuild

```bash
cd sources/resources/code-examples/data
uv run --no-project python prep_datasets.py            # build all available datasets
uv run --no-project python prep_datasets.py raamove    # build just one
```

`raamove`, `cars50`, and `cefr` auto-download (RAAMove via `git clone`, CaRS-50 via the Mendeley
public API, CEFR via `git clone`). `l2_errors` and `icnale_gra` need their raw files placed under
`raw/` first — see [`SOURCES.md`](./SOURCES.md) for exact steps.

## Design choices

- **Reproducible & auditable.** All shaping lives in `prep_datasets.py` (stdlib only — the repo
  declares no dependencies). **No datasets are committed** — both `raw/` downloads and the derived
  `gold/*.json` are git-ignored; rebuild them locally with the prep script or the download notebooks,
  with sources cited in `SOURCES.md`.
- **Fixed-seed sampling.** Gold sets are sampled with `SEED = 42` so rebuilds are deterministic.
- **Balanced gold sets.** Tutorial gold files hold an equal number of items per label, so confusion
  matrices and per-class F1 are meaningful from the start.
- **Two difficulty axes.** Datasets are chosen to separate *easy-to-judge* tasks (CEFR) from
  *hard-to-judge* research tasks (moves, errors), so students learn the pipeline before facing
  genuine annotation ambiguity.

## Validation

`prep_datasets.ipynb` (and the build output) checks every gold file against the canonical schema:
unique `id`s, non-empty `text`, non-empty `label`, and (where applicable) labels drawn from the
declared set. Current build: all 10 gold files valid.
