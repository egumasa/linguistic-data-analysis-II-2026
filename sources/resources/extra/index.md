---
title: "Extra Topics"
subtitle: "Optional deep-dives, beyond the day notebooks"
---

Material here is **not required** for any Corpus Lab or the mini-project. It
covers practical problems that come up once you start running your own LLM code
at any real volume, and it is here so the day notebooks can stay focused on the
linguistics.

## Contents

- 🚦 [Handling rate limits without crashing](handling-rate-limits.ipynb) — why a
  429 arrives when you have "barely used" your quota, how to read which limit you
  hit, and a `make_resilient()` wrapper that paces, retries, and caches. Runs
  without an API key.

## When you'd open this

| If you hit… | Read |
| --- | --- |
| `429 RESOURCE_EXHAUSTED` mid-run | [Handling rate limits](handling-rate-limits.ipynb) |
| A loop that dies partway and loses every answer so far | [Handling rate limits](handling-rate-limits.ipynb) §6 |
| "Quota exceeded" that a retry never fixes | [Handling rate limits](handling-rate-limits.ipynb) §1 — you are probably at a *daily* cap |
