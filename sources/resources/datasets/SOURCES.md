# Replication datasets — sources, licenses & attribution

All gold-standard files under `gold/` are **derived** from the open datasets below and
reshaped into the course's canonical schema:

```json
[{"id": 1, "text": "...", "label": "..."}]
```

**No datasets are committed to this repo.** Raw downloads (`raw/`) and the derived gold files
(`gold/*.json`) are both **git-ignored** — rebuild them locally with `prep_datasets.py` (see that
file's header for per-dataset download steps) or the per-dataset download notebooks. Cite the
original source and note that the data were reshaped.

| Gold file(s) | Task / `label` | Source | License | Status |
|--------------|----------------|--------|---------|--------|
| `cefr_sentences.json`, `cefr_pool.json` | CEFR level A1–C2 (on-ramp) | CEFR-SP, Wiki-Auto portion | CC BY-SA 3.0 | ✅ built |
| `raamove_moves.json`, `raamove_pool.json` | RA-abstract move (8 classes) | RAAMove | CC BY 4.0 | ✅ built |
| `cars50_moves.json`, `cars50_pool.json`, `cars50_step_pool.json` | RA-intro Move (3) / Move+Step (11) | CaRS-50 | CC BY 4.0 | ✅ built |
| `l2_errors.json`, `l2_errors_pool.json`, `l2_error_detection.json` | L2 error category / detection | AutoErrorAnalyzer (OSF) | see OSF project | ✅ built |
| `icnale_gra_scores.json` | Holistic score band (AWE) | ICNALE GRA | research use (password) | ⛔ manual download |

Notes:
- **CEFR-SP** ships text only for the **Wiki-Auto** (CC BY-SA 3.0) and SCoRE (CC BY-NC-SA 4.0)
  portions; the Newsela portion is access-gated. The gold files here are built from **Wiki-Auto
  only**, keeping sentences where **both annotators agree** (clean, unambiguous → ideal on-ramp).
  Derived files inherit **CC BY-SA 3.0** (share-alike).
- **L2 errors** is built from the OSF `Analysis/data_category.csv`, which contains each sentence's
  **human gold** error codes *and* the published tool's predictions (`AEA_ErrorCategories`) — so
  students can compare their LLM not only to the human gold but to the original tool. The 23 error
  codes are collapsed to broader categories (Grammatical/Lexical/Mechanical/No error) via
  `L2_COARSE` in `prep_datasets.py`; sentences spanning >1 broader category are dropped for a clean
  single-label task.
- **ICNALE GRA** requires registration (password-protected zip). Once downloaded, export a
  `text,score` CSV to `raw/icnale_gra/essays_scores.csv` and re-run the builder.

## Citations

- **RAAMove** — Liu, J. et al. *RAAMove: A Corpus for Analyzing Moves in Research Article
  Abstracts.* LREC-COLING 2024. (Public release: 400 abstracts / 3,069 sentences, 8-move
  scheme BAC/GAP/MTD/PUR/RST/CLN/CTN/IMP; κ = 0.785.) CC BY 4.0.
- **CaRS-50** — Lam, C. & Nnamoko, N. (2025). *CaRS-50 Dataset: Annotated corpus of
  rhetorical Moves and Steps in 50 article introductions.* Mendeley Data, V1.
  doi:10.17632/kwr9s5c4nk.1. (50 BioRxiv intros, sentence-level Swales CARS Move+Step;
  inter-rater κ ≈ 0.43.) CC BY 4.0.
- **CEFR-SP** — Arase, Y., Uchida, S., & Kajiwara, T. (2022). *CEFR-based Sentence
  Difficulty Annotation and Assessment.* EMNLP 2022.
- **AutoErrorAnalyzer** — Mizumoto, A. (2025). *Automated analysis of common errors in L2
  learner production: Prototype web application development.* Studies in Second Language
  Acquisition, 47(3), 867–884. (26-category error taxonomy; ~100 Japanese-EFL essays;
  gold annotations, Krippendorff's α ≈ .92.)
- **ICNALE GRA** — Ishikawa, S. *The ICNALE Global Rating Archives.* (Asian-learner L2
  English essays/speeches rated on holistic + analytic scales by many trained raters.)

## Motivating study (not openly available)

- **Kim, M. & Lu, X. (2024).** *Exploring the potential of using ChatGPT for rhetorical
  move-step analysis: The impact of prompt refinement, few-shot learning, and fine-tuning.*
  Journal of English for Academic Purposes, 71, 101422. doi:10.1016/j.jeap.2024.101422.
  No open replication package (corpus is the non-public *Corpus of Social Science RA
  Introductions*, Lu et al. 2021). **CaRS-50** is the open stand-in for the same task.
