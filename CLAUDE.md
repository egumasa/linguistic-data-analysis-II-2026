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

Quarto's jupyter engine is wired to use `uv` (see `execute` block in `_quarto.yml`: `python: uv run python`). The repo targets Python >=3.13 ([pyproject.toml](pyproject.toml), [.python-version](.python-version)) but currently declares **no dependencies** — `pyproject.toml` is a near-empty `uv` scaffold.

Important: the example notebooks under [sources/resources/code-examples/python/](sources/resources/code-examples/python/) are written to run in **Google Colab** by students (the course assumes no local Python install — see [python-setup.md](sources/resources/tools/python-setup.md)). They import heavy NLP libraries (`spacy`, `taaled`, `pylats`, `lexical-diversity`, `pandas`, `seaborn`). These are not installed locally via `uv` and are not needed to build the site — only to execute notebooks. Do not assume they are available in this environment.

## Coding approach

- use basic functional oriented programming ()
- 

## Layout & content authoring

All site content lives under `sources/`:

- `sources/syllabus/`, `sources/sessions/`, `sources/resources/` — the published pages (syllabus, per-day session notes, tool/corpus guides, code examples).
- `sources/resources/tools/` and `sources/resources/corpora/` — how-to guides (AntConc, BYU corpora, JASP, Python/Colab setup; corpus inventories).
- `assets/css/` — `style.scss` (site theme, extends the `litera` Bootswatch theme) and `slides.scss`. `.scss` files are the sources; `.css` files are generated.

### No student/instructor audience labels

**Assume students will see every file in the repo.** Never describe a file as "instructor-facing", "instructor-only", "student-facing", or "for students" — not in prose, headings, table columns, directory-tree comments, docstrings, or notebook cells. A reader who opens a file labeled "instructor-only" learns nothing useful about it and may assume they weren't meant to be there.

Describe files by **what they do and when you'd open them** instead:

- ❌ "Instructor-facing build script" → ✅ "Batch build of every gold file at once"
- ❌ "How to rebuild (instructors)" → ✅ "Rebuilding every dataset at once"
- ❌ a "Who it's for" column → ✅ a "When you'd open it" column

If something genuinely must not reach students, **`.gitignore` it** — that is the only real hiding mechanism. A label is not access control.

Writing *to* or *about* the instructor as a person is still fine ("report the result to the instructor", the syllabus's "Instructor Information", "group presentations with instructor Q&A"). The rule targets audience labels applied to files.

### Course structure (drives navigation and page organization)

5-day intensive course, 3 sessions per day (intro → tutorial → hands-on), plus 4 "Corpus Lab" hands-on assignments and a final group mini-project. The day/session/assignment hierarchy in `_quarto.yml`'s navbar and sidebars mirrors this. When adding session or assignment pages, keep them consistent with that hierarchy.

### Known state: navigation references a not-yet-built tree

`_quarto.yml` navbar and sidebar `contents` point at paths like `2025/sessions/dayN/...`, `2025/syllabus/...`, and a `metadata-files: _metadata.yml` — **most of these files do not exist yet.** Actual content currently sits under `sources/sessions/`, `sources/syllabus/`, etc. (no `2025/` prefix). The site is mid-build-out; expect to either create the referenced `2025/...` files or update the config paths to match. Verify with `quarto render` before assuming navigation links resolve.

## Planning docs (gitignored)

`planning/` is excluded via [.gitignore](.gitignore) and holds course-design notes (mostly in Japanese) — e.g. `planning/course_planning/course-design.md` (the authoritative internal design doc — rationale, delivery plan, status, and tasks), `LDA2_syllabus.md`. These are working/reference material and are not published; treat them as the source of intent behind the course design, not as deliverables.


## Commiting

- DO not include any Claude co-author tag such as ``Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>``
