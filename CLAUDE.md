# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A [Quarto](https://quarto.org) website for the graduate course **Linguistic Data Analysis II** (Tohoku University, Graduate School of International Cultural Studies, Summer 2026). The course teaches applied linguistics students to use and evaluate Large Language Models for linguistic analysis — annotation scheme design, gold-standard dataset construction, prompt design, and evaluation (precision/recall/F1, confusion matrices). It is the sequel to [Linguistic Data Analysis I](https://egumasa.github.io/linguistic-data-analysis-I/).

This is a content/teaching-materials repo, not an application. "Code" here means Quarto markdown (`.md`/`.qmd`) pages, the site config, and example Jupyter notebooks distributed to students.

## Literature search (Zotero MCP)

When course materials, planning docs, or syllabi need supporting references — or when the user asks to find, verify, or cite relevant literature — use the **Zotero MCP** tools to search the user's own library first (e.g. `mcp__zotero-mcp__search_library`, `search_fulltext`, `semantic_search`, `search_by_identifier`, `get_item_details`, `get_item_abstract`, `generate_bibliography`). Prefer citing works that already exist in the Zotero library so references stay consistent with the user's collection, and confirm bibliographic details (authors, year, venue) against Zotero rather than from memory before adding a citation.

## Build & preview

Quarto is configured in [sources/_quarto.yml](sources/_quarto.yml) — **the project root for Quarto is `sources/`, not the repo root.** Run Quarto commands from inside `sources/`.

```bash
cd sources
quarto preview          # live-reload local server while editing
quarto render           # build the full site into sources/docs/ (the publish target)
quarto render path/to/page.qmd   # render a single page
```

- Output goes to `sources/docs/` (`output-dir: docs`), which is what gets published to GitHub Pages at https://egumasa.github.io/linguistic-data-analysis-II-2026/.
- `execute.freeze: auto` means computational cells are only re-run when their source changes; cached results live in a `_freeze/` directory.

## Python / notebooks

Quarto's jupyter engine is wired to use `uv` (see `execute` block in `_quarto.yml`: `python: uv run python`). The repo targets Python >=3.13 ([pyproject.toml](pyproject.toml), [.python-version](.python-version)). `[project].dependencies` is deliberately empty so the Quarto render stays light; the packages the notebooks need live in the `dev` dependency group, installed with `uv sync --group dev`.

Important: the day notebooks in [sources/notebooks/](sources/notebooks/) and the dataset download notebooks in [sources/resources/datasets/notebooks/](sources/resources/datasets/notebooks/) are written to run in **Google Colab** by students (the course assumes no local Python install — see [python-setup.md](sources/resources/tools/python-setup.md)). They use `google-genai`, `gspread`, and `scikit-learn`, among others. None of this is needed to build the site — only to execute notebooks. Do not assume these packages are available in this environment.

## Coding approach

- use basic function-oriented programming: plain functions over small data structures, no classes unless a library requires one.

### Notebook coding principles (MUST read before touching `sources/notebooks/`)

Any work on the day notebooks MUST follow
[planning/course_planning/notebook-coding-principles.md](planning/course_planning/notebook-coding-principles.md).
In short: **the `.ipynb` files are the source — edit them directly.** 367 of the 385 cells
are ordinary and stay exactly as you leave them.

The 18 exceptions are the 📦 Setup cell and each 🔧 Library cell. They say so in their own
second line, and `_sync_notebooks.py` rewrites them, so an edit typed into one is
replaced. They exist because `load_gold` appears in four notebooks (`evaluate` /
`show_errors` are Day 3 only), and because the Setup cell's import line is computed from
the helper list — a day imports exactly what it ships. To change one:

- **the helper's code** → edit [sources/notebooks/_notebook_lib.py](sources/notebooks/_notebook_lib.py), then sync. Every day using it updates together. The helpers sit at the end of that file as ordinary Python, one `# === name :: caption ===` section each — edit them as you would any function.
- **which helpers a cell ships, or a day's backend** → edit that cell's `lda2` metadata, then sync.

Editable ✏️ cells stay within the vocabulary the progression table has introduced by that
day.

After editing a notebook:

```bash
python sources/notebooks/_sync_notebooks.py    # rebuild generated cells, clear outputs
python sources/notebooks/_check_notebooks.py   # the invariants
```

## Layout & content authoring

All site content lives under `sources/`:

- `sources/syllabus/`, `sources/sessions/`, `sources/resources/` — the published pages (syllabus, per-day session notes, tool/corpus guides).
- `sources/resources/tools/` and `sources/resources/corpora/` — how-to guides (AntConc, BYU corpora, JASP, Python/Colab setup; corpus inventories).
- `sources/slides/` — the 15 revealjs decks (`slides-session-01.qmd` … `slides-session-15.qmd`) plus shared deck config in `_slides.yml`.
- `sources/notebooks/` — the five day notebooks students run in Colab. See the notebook coding principles above before editing.
- `sources/final-project/` — the group mini-project pages (plan, deliverables, rubric, pipeline cheatsheet).
- `sources/resources/datasets/` — the gold JSON files, `prep_datasets.py`, and the download notebooks.
- `sources/assets/css/` — `style.scss` (site theme, extends the `litera` Bootswatch theme), `slides.scss`, `slides-v2.scss`, and the variable-only flavor files `slide-forest.scss`, `slide-warm.scss`, `slide-pastel.scss`. `.scss` files are the sources; `.css` files are generated.

### Say it plainly — no metaphors

Students here are graduate applied-linguistics students, many of them working in a second language. A figure of speech costs them a translation step and buys nothing.

**Never dress a technical statement up as an image, a wager, or a piece of equipment.** Say what the thing is and what it is for.

- ❌ "get one honest number to beat" → ✅ "a first score, before you change anything"
- ❌ "your steering wheel, not your result" → ✅ "use it to decide what to change next; do not report it"
- ❌ "a re-roll of the dice" → ✅ "the same prompt run a second time"
- ❌ "reading it back is not superstition" → ✅ "reading it back checks that the file you will report from is the file you think it is"
- ❌ "F1 is the scoreboard" · "the model's blind spot" · "the prompt is a contract"

The same rule covers flourishes that carry no information: no "and that is the whole trick", no "here is where it gets interesting", no one-word sentences for emphasis. Emphasis is **bold**, not drama.

This binds **`sources/slides/` as well as `sources/notebooks/`**, and applies to every kind of text — slide bullets, page prose, markdown cells, code comments, and error messages alike.

### No student/instructor audience labels

**Assume students will see every file in the repo.** Never describe a file as "instructor-facing", "instructor-only", "student-facing", or "for students" — not in prose, headings, table columns, directory-tree comments, docstrings, or notebook cells. A reader who opens a file labeled "instructor-only" learns nothing useful about it and may assume they weren't meant to be there.

Describe files by **what they do and when you'd open them** instead:

- ❌ "Instructor-facing build script" → ✅ "Batch build of every gold file at once"
- ❌ "How to rebuild (instructors)" → ✅ "Rebuilding every dataset at once"
- ❌ a "Who it's for" column → ✅ a "When you'd open it" column

If something genuinely must not reach students, **`.gitignore` it** — that is the only real hiding mechanism. A label is not access control.

Writing *to* or *about* the instructor as a person is still fine ("report the result to the instructor", the syllabus's "Instructor Information", "group presentations with instructor Q&A"). The rule targets audience labels applied to files.

### Course structure (drives navigation and page organization)

5-day intensive course, 15 sessions, 3 per day. Days 1–3 run intro → tutorial → hands-on; Days 4–5 are methodology and project work. Assessment is attendance and participation, the hands-on activities across Days 1–3 plus the completed notebook, the Day 5 group presentation with Q&A, and a one-page report. The day/session hierarchy in `_quarto.yml`'s navbar and sidebars mirrors this. When adding session pages, keep them consistent with that hierarchy.

## Planning docs (gitignored)

`planning/` is excluded via [.gitignore](.gitignore) and holds course-design notes — e.g. `planning/course_planning/course-design.md` (the authoritative internal design doc — rationale, delivery plan, status, and tasks) and `notebook-coding-principles.md`. These are working/reference material and are not published; treat them as the source of intent behind the course design, not as deliverables.


## Commiting

- DO not include any Claude co-author tag such as ``Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>``
