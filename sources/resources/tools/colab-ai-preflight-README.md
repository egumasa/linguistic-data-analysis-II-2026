# `google.colab.ai` pre-flight — how to run

Instructor-only check to run **once before the course**, on the Tohoku Google
account students will use. It confirms Colab's built-in Gemini
(`from google.colab import ai`) is reachable, finds where it throttles, projects
load to ~15 students, and measures how stable the parsed CEFR labels are.

Notebook: [`colab-ai-preflight.ipynb`](./colab-ai-preflight.ipynb)

> This notebook only runs **inside Google Colab** — `google.colab.ai` does not
> exist on a local machine.

## Option A — open in Colab directly (recommended, no clone)

1. Make sure the notebook is on GitHub first: `git push origin main`.
2. Open this link (or paste it into your browser), signed in with the **Tohoku
   Google account**:

   <https://colab.research.google.com/github/egumasa/linguistic-data-analysis-II-2026/blob/main/sources/resources/tools/colab-ai-preflight.ipynb>

3. **Runtime → Run all.** Each step prints its own report; the last cell gives
   go / no-go.

No GPU/TPU needed — the default CPU runtime is fine.

## Option B — clone the repo and upload

Use this if you'd rather not push first, or want to edit locally.

```bash
git clone https://github.com/egumasa/linguistic-data-analysis-II-2026.git
cd linguistic-data-analysis-II-2026
# the notebook lives here:
#   sources/resources/tools/colab-ai-preflight.ipynb
```

Then in Colab: **File → Upload notebook →** pick
`sources/resources/tools/colab-ai-preflight.ipynb`, sign in with the Tohoku
account, and **Runtime → Run all**.

## What each step tells you

| Step | Reads | Decision |
| --- | --- | --- |
| 2 · Smoke test | Is `colab.ai` reachable at all? | Fails → the whole path is unavailable on Tohoku accounts; use the Gemini-API `.env` fallback (D4). |
| 3 · 100-call probe | successes/100, median & p95 latency, first throttle | Throttles well before 100 → single-user ceiling too low. |
| 4 · Class-of-15 projection | per-student daily model-time; per-account vs shared quota | Frames whether 15 students is safe (can't test true concurrency from one account). |
| 5 · Determinism | modal-label agreement over 10 repeats | Low (<~80%) → warn students about F1 wobble; consider majority-vote. |

## After the run

Record the numbers (reachable? throttle point? mean agreement?) in
`planning/course_planning/prep-plan.md` — this closes the **07-09** milestone and
de-risks the **07-12** end-to-end Colab run.
