---
title: "Replication Datasets"
subtitle: "Open, annotated datasets for LLM annotation & evaluation"
toc: true
---

## Why these datasets

Across Days 2–5 you will use a large language model (LLM) to **annotate** linguistic data and
then **evaluate** it against a human gold standard (precision / recall / F1 / confusion matrix).
To make that practice real, this course draws on **openly licensed, expert-annotated datasets**
from published applied-linguistics and NLP research.

Every dataset is reshaped into one **canonical schema** so that the same notebook works for all of
them — you only ever change the *prompt*, the *label set*, and the *gold file*:

```json
[
  {"id": 1, "text": "However, little is known about ...", "label": "Gap"},
  {"id": 2, "text": "We therefore investigated ...",      "label": "Purpose"}
]
```

The gold files are **not distributed with this repo** — rebuild them into `gold/`
reproducibly with [`prep_datasets.py`](./prep_datasets.py) (or the per-dataset download
notebooks below) from the original sources. Licenses and citations are in
[`SOURCES.md`](./SOURCES.md). **Always cite the original dataset.**

::: {.callout-note}
## Two kinds of difficulty
A task can be hard to *prepare* (messy source data) or hard to *judge* (the labeling decision
itself is subjective). They are independent. We deliberately **start with an easy-to-judge task**
(CEFR level) to learn the pipeline, then move to **hard-to-judge** research tasks (discourse moves,
L2 errors) where even expert annotators disagree — which is exactly what makes them interesting.
:::

## The motivating study

This strand of the course replicates the *idea* of **Kim & Lu (2024)**, who tested how well
ChatGPT can annotate **rhetorical move-steps** in research-article introductions, and how prompt
refinement, few-shot examples, and fine-tuning change its accuracy.

> Kim, M., & Lu, X. (2024). Exploring the potential of using ChatGPT for rhetorical move-step
> analysis: The impact of prompt refinement, few-shot learning, and fine-tuning.
> *Journal of English for Academic Purposes, 71,* 101422.

Their annotated corpus is **not** publicly available, so we use **CaRS-50** — an open dataset that
annotates the *same* phenomenon (Swales' CARS moves in article introductions) — as the stand-in.

## Dataset catalog

| Dataset | Phenomenon | Labels | Judge difficulty | Gold files |
|---------|-----------|--------|:---:|-----------|
| **CEFR-SP** | Sentence proficiency level | A1–C2 (6) | ★☆☆ | `cefr_sentences.json` (72), `cefr_pool.json` (3,183) |
| **RAAMove** | Moves in RA abstracts | 8 moves | ★★★ | `raamove_moves.json` (64), `raamove_pool.json` (3,069) |
| **CaRS-50** | Move-steps in RA intros | Move (3) / Step (11) | ★★★ | `cars50_moves.json` (60), `cars50_pool.json`, `cars50_step_pool.json` |
| **AutoErrorAnalyzer** | L2 written errors | category (4) / detection (2) | ★★★ | `l2_errors.json` (60), `l2_error_detection.json` (60), `l2_errors_pool.json` |
| **ICNALE GRA** | Holistic essay rating (AWE) | Low/Mid/High | ★★☆ | *(manual download — see below)* |

The `*_moves.json` / `*_sentences.json` files are **balanced ~60–72 item gold sets** for the worked
tutorials. The `*_pool.json` files are the **full datasets** for mini-projects (build your own larger
or differently-balanced gold set from them).

### CEFR-SP — the on-ramp (★☆☆ to judge)

Single sentences labeled with their CEFR difficulty level (A1–C2) by language-education
professionals. We keep only sentences where **both annotators agreed**, so the labels are
unambiguous — perfect for learning the annotate → evaluate pipeline before tackling harder tasks.
Built from the openly-shipped **Wiki-Auto** portion (CC BY-SA 3.0).
Source: Arase, Uchida & Kajiwara (2022), *EMNLP* — [github.com/yukiar/CEFR-SP](https://github.com/yukiar/CEFR-SP).

### RAAMove — discourse moves, clean data (★★★ to judge)

Sentences from research-article **abstracts** labeled with one of **8 rhetorical moves**
(Background, Gap, Method, Purpose, Result, Conclusion, Contribution, Implication). Ships as tidy
JSON, so it is the easiest *discourse* dataset to start with. Inter-annotator κ = 0.785.
CC BY 4.0. Source: Liu et al. (2024), *LREC-COLING* — [github.com/ljk1228/RAAMove](https://github.com/ljk1228/RAAMove).

### CaRS-50 — the Kim & Lu replication (★★★ to judge)

Sentences from 50 BioRxiv article **introductions** labeled with Swales' **CARS Move (1–3)** and
**Step (a–d)** — the same scheme Kim & Lu used. Start with the 3-class **Move** version
(`cars50_moves.json`); the 11-class **Move+Step** version (`cars50_step_pool.json`) is a stretch
goal. Note: the dataset's own expert inter-rater agreement is only **κ ≈ 0.43** — a built-in lesson
that this task is genuinely hard. CC BY 4.0.
Source: Lam & Nnamoko (2025), Mendeley Data — [doi:10.17632/kwr9s5c4nk.1](https://data.mendeley.com/datasets/kwr9s5c4nk/1).

### AutoErrorAnalyzer — L2 error annotation (★★★ to judge)

Sentences from Japanese-EFL essays with **human gold** error labels. We collapse the 23-code
taxonomy into 4 broader classes (Grammatical / Lexical / Mechanical / No error); a binary
**error-detection** version is also provided. Bonus: the source file also contains the **published
tool's own predictions**, so you can compare your LLM both to the human gold *and* to the original
system. Source: Mizumoto (2025), *SSLA* 47(3) — [github.com/mizumot/AutoErrorAnalyzer](https://github.com/mizumot/AutoErrorAnalyzer)
+ [OSF](https://osf.io/jyf3r/).

### ICNALE GRA — automated writing evaluation (★★☆ to judge)

Asian-learner English essays rated holistically by many trained raters — the basis for an
**automated writing evaluation** task (predict a Low/Mid/High score band). The archive is
**password-gated**: register at the
[ICNALE download page](https://language.sakura.ne.jp/icnale/download.html), then follow the
instructions in [`SOURCES.md`](./SOURCES.md) to build the gold file.

## Building the gold files yourself

**Getting raw data and shaping it into a gold standard is itself a core skill in this course** — not
just a chore done for you. So each dataset has a **student notebook** (Colab-ready, no setup) that
walks through *download → inspect the raw format → reshape to the canonical schema → check the label
balance → save*. The point you will feel: **every dataset's raw format is different**, and getting
it into one clean shape is half the work of building a gold standard.

| Dataset | Student notebook |
|---------|------------------|
| CEFR-SP | [`download_cefr_sp.ipynb`](./notebooks/download_cefr_sp.ipynb) |
| RAAMove | [`download_raamove.ipynb`](./notebooks/download_raamove.ipynb) |
| CaRS-50 | [`download_cars50.ipynb`](./notebooks/download_cars50.ipynb) |
| AutoErrorAnalyzer | [`download_autoerroranalyzer.ipynb`](./notebooks/download_autoerroranalyzer.ipynb) |
| ICNALE GRA | [`download_icnale_gra.ipynb`](./notebooks/download_icnale_gra.ipynb) (gated — upload your own download) |

Instructors can rebuild everything at once with the script behind those notebooks:

```bash
cd sources/resources/datasets
uv run --no-project python prep_datasets.py          # build all available datasets
uv run --no-project python prep_datasets.py raamove  # or just one
```

Neither the raw downloads nor the derived `gold/*.json` are distributed with this repo — rebuild
them locally with the notebooks or the script above. See
[`prep_datasets.ipynb`](./prep_datasets.ipynb) for the instructor build + a schema
validator.

## Worked tutorials & mini-project tracks

- [Day 2 tutorial — Annotation, gold standards & evaluation](../tutorials/tutorial-day2-annotation-eval.md)
  (on-ramp with CEFR-SP)
- [Day 3 tutorial — Replicating Kim & Lu with open data](../tutorials/tutorial-day3-move-replication.md)
  (RAAMove → CaRS-50)
- [Mini-project starter tracks](./mini-project-tracks.md)
