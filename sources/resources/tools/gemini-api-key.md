---
title: "Get a free Gemini API key (for Corpus Lab & the final project)"
subtitle: "Reproducible LLM results, still 100% inside Colab — no install"
toc: true
---

## When you need this

**You need a key starting on Day 3.** Days 1 and 2 are keyless:

- **Day 1** uses Colab's built-in Gemini (`colab.ai`) for your first live call — zero setup. That free
  backend gives you **no control over randomness** (run the same prompt twice and the answer can
  change); that's fine here, and we use it to *show* you why LLM output varies.
- **Day 2** doesn't call the model at all — it evaluates a **frozen** set of predictions committed to
  the repo, so everyone's precision/recall/F1 come out identical while you're learning the metrics.

**From Day 3 on — the Corpus Lab and the final project — you run the model yourself, and your results
have to be stable and reproducible:** your reported precision/recall/F1 shouldn't change every time
you re-run, and (because the Corpus Labs are **autograded**) a grader must be able to re-run your
notebook and get the same numbers. For that you switch to the **Gemini API**, where you *can* pin the
randomness (`temperature=0`, a fixed `seed`, a pinned model).

::: {.callout-important}
You do **not** install anything or leave Colab. You get a free key, paste it into Colab's built-in
**Secrets** manager once, and the notebook picks it up automatically.
:::

## Step 1 — Create a free API key (AI Studio)

1. Go to **<https://aistudio.google.com/apikey>** and sign in with your **Tohoku Google account**.
2. Click **Create API key**.
3. Copy the key (a long string starting with `AIza…`). Treat it like a password.

This is the **free tier** — no billing, no credit card. It has rate limits (a cap on requests per
minute / per day), which are plenty for one student's coursework.

::: {.callout-warning}
## Never paste your key into a notebook cell
Anyone who sees your notebook (or the committed `.ipynb`) would get your key. Always use Colab
**Secrets** (Step 2) so the key stays out of the code and out of what you submit.
:::

## Step 2 — Add the key to Colab Secrets

1. Open your Corpus-Lab / project notebook in Colab.
2. In the **left sidebar**, click the **🔑 key icon** (“Secrets”).
3. Click **+ Add new secret**.
4. Name it exactly `GEMINI_API_KEY`.
5. Paste your key into the **Value** box.
6. Turn on the **Notebook access** toggle for this secret.

You only do this once per Google account — the secret is remembered across your notebooks.

## Step 3 — The notebook uses it automatically

When `GEMINI_API_KEY` is set, the notebook's setup cell reads it from Secrets and routes calls
through the Gemini API instead of `colab.ai`. You don't change any code. Under the hood it does this:

```python
import os
from google.colab import userdata
from google import genai
from google.genai import types

# Pull the key from Colab Secrets (never hard-code it).
os.environ["GEMINI_API_KEY"] = userdata.get("GEMINI_API_KEY")

client = genai.Client()   # reads GEMINI_API_KEY from the environment

def generate_text(p):
    return client.models.generate_content(
        model="gemini-3.1-flash-lite",               # pinned model
        contents=p,
        config=types.GenerateContentConfig(
            temperature=0,   # greedy decoding — removes sampling randomness
            seed=42,         # fixed random state
        ),
    ).text
```

The setup cell prints which backend it chose, e.g.
`LLM backend: Gemini API (gemini-3.1-flash-lite)`. If it still says `Colab Gemini`, your secret isn't set
or its notebook-access toggle is off — recheck Step 2.

::: {.callout-tip}
## If Colab's built-in Gemini (`colab.ai`) is ever unavailable
The Days 1–3 demos use the keyless `colab.ai` backend. If it's down or unreachable in class, the fix
is the same steps above: create a free key (Step 1) and add it as the `GEMINI_API_KEY` secret
(Step 2). The notebook then routes **every** call through the Gemini API automatically — so the API
key doubles as the fallback whenever the built-in backend isn't working.
:::

## About reproducibility (important, and a little humbling)

`temperature=0` + `seed` makes the model **as reproducible as a hosted LLM gets** — but **not
perfectly**. Requests are batched with other users' on Google's servers, and the resulting
floating-point math can differ slightly run to run, which occasionally flips the label on a
genuinely borderline item. So expect:

- **Clear-cut items** → identical every run.
- **Ambiguous items** → the same *most of the time*, with the odd flip.

Because of this, your final deliverable **freezes your predictions**: you run the model once, save
its raw output to a JSON file, and commit that alongside your analysis. Your evaluation (P/R/F1,
confusion matrix, error table) then runs off the **frozen file**, so your submitted numbers are
100% reproducible — and anyone can audit exactly what the model said. (The Corpus-Lab notebook shows
you how.)

## Rate limits & good manners

The free tier limits **requests per minute** and **per day**. If you hit a limit you'll get a
rate-limit error — wait a bit and re-run, or reduce your sample size. Practical tips:

- Develop your prompt on a **small** slice (10–20 items) first; only run the full set once you're
  happy.
- Once you've frozen your predictions, you don't need to call the API again — re-run analysis off
  the JSON.

## Want to keep working after the course? (optional, advanced)

Everything above stays in Colab. If you'd rather run locally in your own environment (e.g. Positron
+ `uv`), clone the course repo and set the same `GEMINI_API_KEY` as an environment variable — the
notebooks detect they're *not* in Colab and use the API automatically. See
[Python setup (local)](./python-setup.md). This is **optional** — not required for the course.
