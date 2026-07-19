---
title: "Housing Your Data in Google Drive"
subtitle: "Mount Drive from Colab, save a gold set, load it back"
toc: true
---

## Why this guide

In the worked tutorials, the course hands you data over a URL — e.g. Day 2's
[`day2_gold_standards_and_evaluation.ipynb`](../../notebooks/day2_gold_standards_and_evaluation.ipynb) loads a committed CEFR gold set
straight from GitHub, so it *just runs*. That is the **instructor's** distribution channel.

For the **mini-project** you flip roles: you *build your own* gold set (download → reshape →
sample a subset) and you need somewhere to keep it. That place is **your Google Drive** — not
GitHub.

::: {.callout-note}
## GitHub is ours, Drive is yours
GitHub is how *we* ship read-only course data to everyone. Your own rebuilt/sampled data lives in
*your* Drive because it:

- **persists across Colab sessions** — a Colab VM wipes `/content/` when it disconnects, but your
  Drive files survive;
- **needs no `git push`** — save and it's there;
- **stays private and license-clean** — some source datasets can't be redistributed, so committing
  them to a repo would be a licensing problem. Keeping *your* copy in *your* Drive avoids that.
:::

We'll learn the pattern on the **CEFR** data you already know from Day 2, then reuse the *exact
same four steps* for your mini-project dataset.

## The pattern, in four steps

### 1. Mount your Drive

Run this in a Colab cell. It pops up a Google auth window the first time — approve it, and your
Drive appears under `/content/drive/MyDrive/`.

```python
from google.colab import drive
drive.mount('/content/drive')
```

### 2. Make a project folder

Keep everything for this course in one place so paths stay predictable.

```python
import os

DATA_DIR = "/content/drive/MyDrive/lda2/gold"
os.makedirs(DATA_DIR, exist_ok=True)
print("Your data folder:", DATA_DIR)
```

### 3. Save your gold set into Drive

After you've built a gold set — e.g. by running the CEFR download notebook
[`download_cefr_sp.ipynb`](../datasets/notebooks/download_cefr_sp.ipynb), which produces a
list of `{"id", "text", "label"}` items — write it to Drive:

```python
import json

# `gold` is the list your download/build notebook produced
out_path = f"{DATA_DIR}/cefr_sentences.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(gold, f, ensure_ascii=False, indent=2)

print(f"Saved {len(gold)} items to {out_path}")
```

### 4. Load it back — from any future session

This is the payoff: once it's in Drive, any notebook can read it with a **local path** instead of a
URL. The tutorials' `load_gold()` already accepts either:

```python
GOLD_PATH = "/content/drive/MyDrive/lda2/gold/cefr_sentences.json"
gold = load_gold(GOLD_PATH)      # same function, path instead of URL
print(len(gold), "items loaded from Drive")
```

That's the whole round-trip: **mount → folder → save → load**. Nothing is lost when Colab
disconnects, and you never touch GitHub.

## Reusing this for your mini-project

The four steps don't change — you only swap *which* dataset you build and *what* you name the file.
Pick your track in [`mini-project-tracks.md`](../datasets/mini-project-tracks.md), run that track's
download notebook, then:

1. **Mount** your Drive (step 1).
2. **Save** your track's gold set — e.g. `f"{DATA_DIR}/raamove_moves.json"` (step 3).
3. **Load** it by path in your evaluation notebook (step 4).

One dataset, one mechanic, learned once on familiar CEFR data — now applied to your own.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `drive.mount` does nothing / asks again | You disconnected the runtime. Re-run the mount cell and re-approve. |
| `FileNotFoundError` on load | Check the path spelling — it's `MyDrive` (no space), and the folder must exist (re-run step 2). |
| Saved file isn't in Drive | Confirm the cell printed a `/content/drive/MyDrive/...` path, then look under **My Drive → lda2 → gold** in the Drive web UI. |
| "Mountpoint must not already contain files" | Run `drive.flush_and_unmount()` once, then mount again. |

## See also

- [Google Colab Setup Guide](./google-colab-setup.md) — get Colab working in the first place.
- [Replication Datasets](../datasets/index.md) — the download notebooks that *build* the gold sets you house here.
