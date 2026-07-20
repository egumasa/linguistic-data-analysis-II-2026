---
title: "Python Setup — Run Locally"
subtitle: "Running the course notebooks on your own computer"
toc: true
---

::: {.callout-note}
**Colab is the course default and needs zero setup** — if you just want to follow along in class,
use the [Google Colab setup](google-colab-setup.md) instead. This guide is the *local* alternative:
a step up in involvement, but worth it if you want to keep working after the course ends or use a
paid LLM API instead of Colab's built-in Gemini. It assumes you're comfortable with a terminal.
:::

The LLM notebooks are written to work **both** in Colab and locally. In Colab, Day 1 uses the free
built-in Gemini and Day 2 reads frozen predictions (no key); from Day 3 the notebooks call the
**Gemini API**. Run locally, they use the Gemini API whenever `GEMINI_API_KEY` is set (with
`temperature=0` + a fixed seed, so results are reproducible). Here is how to go from nothing to a
running notebook.

## 1. Install `uv`

[`uv`](https://docs.astral.sh/uv/) is a single tool that installs Python *and* manages packages —
it replaces `pip`, `venv`, and `pyenv`, so it's the only thing you need to install.

- **macOS / Linux:**
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **Windows (PowerShell):**
  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

Close and reopen your terminal, then check it works: `uv --version`.

## 2. Get the course project

Download the course repository (you need [git](https://git-scm.com/), or use the green **Code →
Download ZIP** button on GitHub and unzip it):

```bash
git clone https://github.com/egumasa/linguistic-data-analysis-II-2026.git
cd linguistic-data-analysis-II-2026
```

## 3. Create the virtual environment

A **virtual environment** is a private, per-project copy of Python and its packages, so what you
install for this course can't collide with anything else on your computer. `uv` builds one (a
`.venv` folder) and installs everything the notebooks need in a single command:

```bash
uv sync --group dev
```

## 4. Get an API key

From Day 3 the notebooks call the model, so you need a **Gemini API** key (the course standardizes on
Gemini). Get a free one from [Google AI Studio](https://aistudio.google.com/apikey) — see
[Get a free Gemini API key](gemini-api-key.md) for details.

Then set it as an environment variable in the same terminal:

```bash
# macOS / Linux
export GEMINI_API_KEY=your-key-here
```
```powershell
# Windows (PowerShell) — setx persists it for new terminals
setx GEMINI_API_KEY "your-key-here"
```

::: {.callout-warning}
An API key is a **secret** — it's tied to billing. Never paste it into a notebook cell, never commit
it to git, never share it. (This project's `.gitignore` already ignores a `.env` file if you prefer
to keep keys there.)
:::

## 5. Open and run the notebook

```bash
uv run jupyter lab
```

In the browser tab that opens, navigate to a notebook that calls the model — e.g.
`sources/notebooks/day3_prompt_design.ipynb` — and choose **Run → Run All Cells**. The
first cell prints which backend it chose, e.g.
`LLM backend: Gemini API (gemini-3.1-flash-lite, temperature=0, seed=42)`. Everything else — loading the
gold set, the confusion matrix, the error table — works exactly as in Colab. (The Day-2 notebook
needs no key; it reads frozen predictions.)

## Troubleshooting

- **`No LLM backend found ...`** — you're running locally but no key is set. Set `GEMINI_API_KEY`
  (step 4) and restart the notebook kernel (**Kernel → Restart**) so it picks up the new environment
  variable.
- **Wrong model** — the pinned model lives in one place (the `MODEL_ID` constant in the setup cell);
  edit it there if you need a different Gemini model.
- **`ModuleNotFoundError`** — you launched Jupyter outside the project env. Always start it with
  `uv run jupyter lab` from the project folder so it uses the `.venv` from step 3.
