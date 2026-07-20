# `google.colab.ai` pre-flight — how to run

A capacity check run **once before the course**, on the Tohoku Google account the
class will use. It confirms Colab's built-in Gemini
(`from google.colab import ai`) is reachable, finds where it throttles, projects
load to the 8-student class, and measures how stable the parsed CEFR labels are.

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
| 3 · 100-call probe (unguarded) | successes/100, latency, and the first throttle **classified per-minute vs per-day** | Per-minute → fixable by pacing, go to 3b. Per-day → a hard budget; size the labs to fit it. |
| 3b · Same load, guarded | does pacing + backoff + retry reach 100/100, and at what seconds-per-call | 100/100 → ship the wrapper in the day-notebooks. Still failing → lower `ASSUMED_RPM`, or fall back. |
| 4 · Class-of-8 projection | per-student daily model-time; per-account vs shared quota | Frames whether 8 students is safe (can't test true concurrency from one account). |
| 5 · Determinism (guarded) | modal-label agreement over 10 repeats | Low (<~80%) → warn students about F1 wobble; consider majority-vote. |

Step 3 is deliberately **unguarded** — its job is to find the ceiling, so pacing it
would destroy the measurement. Step 3b then re-runs the same load through the
guards to confirm the workaround holds on this account.

Step 3b's seconds-per-call is the number that matters for timetabling: multiply it
by the per-student call count to get how long a lab really takes. If that exceeds
the class period, shrink the gold set.

The guards are explained, with runnable no-key demos, in
[`resources/extra/handling-rate-limits.ipynb`](../extra/handling-rate-limits.ipynb).

## After the run

Record the numbers (reachable? throttle point? mean agreement?) in
`planning/course_planning/prep-plan.md` — this closes the **07-09** milestone and
de-risks the **07-12** end-to-end Colab run.
