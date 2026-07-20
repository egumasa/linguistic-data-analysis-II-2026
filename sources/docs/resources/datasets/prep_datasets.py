#!/usr/bin/env python3
"""Prepare open replication datasets into the course's canonical schema.

Canonical schema (every gold file, every task):

    [{"id": 1, "text": "...", "label": "..."}, ...]

Reproducible batch build of every gold file at once (stdlib only — no pip installs).
The per-dataset notebooks in notebooks/ do the same work one dataset at a time, with
the reshaping steps spelled out; this script is the shortcut when you want them all.
Run from this directory:

    python3 prep_datasets.py            # build everything that has raw/ data
    python3 prep_datasets.py raamove    # build a single dataset

Outputs go to gold/. Raw inputs are read from raw/ and are git-ignored.

------------------------------------------------------------------------------------------
DOWNLOAD STEPS (put results under raw/):

  raamove/    git clone https://github.com/ljk1228/RAAMove raw/raamove
              (auto-cloned by this script if missing)
  cars50/     Download the 50 XML files from https://data.mendeley.com/datasets/kwr9s5c4nk/1
              into raw/cars50/  (auto-download attempted by this script)
  cefr/       git clone https://github.com/yukiar/CEFR-SP raw/cefr
              NOTE: the repo ships sentence IDs/levels; the sentence text comes from
              Wikipedia/Newsela per its README — follow repo instructions to materialize.
  l2_errors/  From https://github.com/mizumot/AutoErrorAnalyzer + its OSF project:
              place the essays + gold error annotations + "Error Categories.xlsx" in
              raw/l2_errors/  (OSF component IDs vary — confirm on the OSF project page).
  icnale_gra/ Request via the form at https://language.sakura.ne.jp/icnale/download.html
              place essays + Global Rating Archive score tables in raw/icnale_gra/.
------------------------------------------------------------------------------------------
"""
from __future__ import annotations

import json
import random
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
GOLD = HERE / "gold"
SEED = 42  # fixed for reproducible gold-set sampling

RAAMOVE_LABELS = {
    "BAC": "Background", "GAP": "Gap", "MTD": "Method", "PUR": "Purpose",
    "RST": "Result", "CLN": "Conclusion", "CTN": "Contribution", "IMP": "Implication",
}


# --------------------------------------------------------------------------- helpers
def validate(items: list[dict], allowed: set[str] | None = None) -> None:
    """Assert items match the canonical schema; raise on the first problem."""
    ids = set()
    for i, it in enumerate(items):
        assert set(it) >= {"id", "text", "label"}, f"item {i} missing keys: {it}"
        assert it["id"] not in ids, f"duplicate id {it['id']}"
        ids.add(it["id"])
        assert isinstance(it["text"], str) and it["text"].strip(), f"empty text at id {it['id']}"
        assert isinstance(it["label"], str) and it["label"], f"empty label at id {it['id']}"
        if allowed is not None:
            assert it["label"] in allowed, f"label {it['label']!r} not in {sorted(allowed)}"


def balanced_sample(items: list[dict], per_label: int, label_key: str = "label") -> list[dict]:
    """Return up to `per_label` items per label class, sampled with a fixed seed."""
    rng = random.Random(SEED)
    by_label: dict[str, list[dict]] = {}
    for it in items:
        by_label.setdefault(it[label_key], []).append(it)
    out: list[dict] = []
    for label in sorted(by_label):
        pool = by_label[label]
        rng.shuffle(pool)
        out.extend(pool[:per_label])
    rng.shuffle(out)
    return out


def write_gold(name: str, items: list[dict], allowed: set[str] | None = None) -> None:
    validate(items, allowed)
    GOLD.mkdir(parents=True, exist_ok=True)
    path = GOLD / name
    path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    counts = Counter(it["label"] for it in items)
    print(f"  wrote {path.relative_to(HERE)}  ({len(items)} items)  {dict(counts)}")


def reid(items: list[dict]) -> list[dict]:
    """Renumber ids sequentially from 1, preserving order."""
    return [{**it, "id": n} for n, it in enumerate(items, 1)]


# --------------------------------------------------------------------------- RAAMove
def build_raamove() -> None:
    src = RAW / "raamove"
    if not src.exists():
        print("  cloning RAAMove ...")
        subprocess.run(
            ["git", "clone", "--depth", "1", "https://github.com/ljk1228/RAAMove", str(src)],
            check=True, capture_output=True,
        )
    rows: list[dict] = []
    for fname in ("Intelligence.json", "Engineering.json"):
        data = json.loads((src / fname).read_text(encoding="utf-8"))
        domain = fname.split(".")[0]
        for r in data:
            rows.append({
                "text": r["text"].strip(),
                "label": RAAMOVE_LABELS.get(r["labels"], r["labels"]),
                "_domain": domain,
            })
    # full pool (for mini-projects) and a balanced ~64-item gold set (8 per move) for the tutorial
    pool = reid([{"id": 0, "text": r["text"], "label": r["label"]} for r in rows])
    allowed = set(RAAMOVE_LABELS.values())
    write_gold("raamove_pool.json", pool, allowed)
    gold = reid(balanced_sample(pool, per_label=8))
    write_gold("raamove_moves.json", gold, allowed)


# --------------------------------------------------------------------------- CaRS-50
def build_cars50() -> None:
    import time
    import urllib.request
    src = RAW / "cars50"
    xmls = sorted(src.glob("*.xml")) if src.exists() else []
    if not xmls:
        print("  downloading CaRS-50 from the Mendeley public API ...")
        src.mkdir(parents=True, exist_ok=True)

        def fetch(url):  # Mendeley's CDN requires a browser User-Agent
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            return urllib.request.urlopen(req, timeout=60)

        meta = json.loads(fetch(
            "https://data.mendeley.com/public-api/datasets/kwr9s5c4nk").read())
        for f in meta["files"]:
            dest = src / f["filename"]
            for _ in range(3):  # retry on the occasional dropped connection
                try:
                    dest.write_bytes(fetch(f["content_details"]["download_url"]).read())
                    break
                except Exception:
                    time.sleep(2)
        xmls = sorted(src.glob("*.xml"))
    if not xmls:
        print("  SKIP cars50: download failed — fetch manually from "
              "https://data.mendeley.com/datasets/kwr9s5c4nk/1 into raw/cars50/")
        return
    # XML shape: <biology_intro>...<fulltext><paragraph>
    #   <sentence><sentenceID/><text/><step>1b</step></sentence> ...
    move_rows: list[dict] = []
    step_rows: list[dict] = []
    for xml in xmls:
        tree = ET.parse(xml)
        for sent in tree.iter("sentence"):
            text_el = sent.find("text")
            step_el = sent.find("step")
            text = (text_el.text or "").strip() if text_el is not None else ""
            code = (step_el.text or "").strip() if step_el is not None else ""
            if not text or not code or not code[0].isdigit():
                continue
            move = code[0]  # leading digit = Move (1/2/3)
            move_rows.append({"id": 0, "text": text, "label": f"Move {move}"})
            step_rows.append({"id": 0, "text": text, "label": code})
    if not move_rows:
        print("  SKIP cars50: parsed 0 sentences — inspect the XML tag/attribute names.")
        return
    # Default (tutorial) granularity = Move (3 classes); stretch granularity = Move+Step.
    write_gold("cars50_pool.json", reid(move_rows))
    write_gold("cars50_moves.json", reid(balanced_sample(reid(move_rows), per_label=20)))
    write_gold("cars50_step_pool.json", reid(step_rows))


# --------------------------------------------------- gated / manual-download datasets
CEFR_NUM = {"1": "A1", "2": "A2", "3": "B1", "4": "B2", "5": "C1", "6": "C2"}


def build_cefr() -> None:
    # Use the openly-shipped Wiki-Auto portion (CC BY-SA 3.0). Files are TSV:
    #   sentence \t labelA \t labelB   (labels 1..6 = A1..C2).
    # Keep only items where BOTH annotators agree -> unambiguous gold (the "easy on-ramp").
    src = RAW / "cefr" / "Wiki-Auto"
    files = sorted(src.glob("*.txt")) if src.exists() else []
    if not files:
        print("  SKIP cefr: clone github.com/yukiar/CEFR-SP into raw/cefr/ "
              "(Wiki-Auto portion ships text; Newsela portion is access-gated).")
        return
    rows: list[dict] = []
    for f in files:
        for line in f.read_text(encoding="utf-8").splitlines():
            parts = line.split("\t")
            if len(parts) < 3:
                continue
            text, a, b = parts[0].strip(), parts[1].strip(), parts[2].strip()
            if a == b and a in CEFR_NUM and text:  # annotator agreement only
                rows.append({"id": 0, "text": text, "label": CEFR_NUM[a]})
    items = reid(rows)
    write_gold("cefr_pool.json", items, set(CEFR_NUM.values()))
    write_gold("cefr_sentences.json", reid(balanced_sample(items, per_label=12)),
               set(CEFR_NUM.values()))


# AutoErrorAnalyzer 23-code taxonomy -> 3 broader categories (from Error Categories.xlsx).
L2_COARSE = {
    **{c: "Grammatical" for c in
       ("ART PREP NUM TENSE VFORM WO AGR DET POSS MOD CONJ STRUCT").split()},
    **{c: "Lexical" for c in "N ADJ ADV V REF EXPR".split()},
    **{c: "Mechanical" for c in "SP MIS UNN CWS PUNC".split()},
}


def build_l2_errors() -> None:
    import csv
    src = RAW / "l2_errors" / "data_category.csv"
    if not src.exists():
        print("  SKIP l2_errors: download data_category.csv from the AutoErrorAnalyzer OSF "
              "project (osf.io/jyf3r, Analysis folder) into raw/l2_errors/")
        return

    def coarse(human_field: str) -> str | None:
        codes = [c.strip() for c in human_field.split(",") if c.strip()]
        if not codes:
            return None
        if codes[0] == "NO_ERROR":
            return "No error"
        cats = {L2_COARSE.get(c) for c in codes} - {None}
        return next(iter(cats)) if len(cats) == 1 else None  # skip mixed-category sentences

    pool, detection = [], []
    with src.open(encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh):
            sent = (r.get("Sentence") or "").strip()
            human = (r.get("Human_ErrorCategories") or "").strip()
            if not sent or not human:
                continue
            label = coarse(human)
            if label is not None:
                pool.append({"id": 0, "text": sent, "label": label})
            detection.append({"id": 0, "text": sent,
                              "label": "No error" if human == "NO_ERROR" else "Has error"})
    allowed = {"Grammatical", "Lexical", "Mechanical", "No error"}
    write_gold("l2_errors_pool.json", reid(pool), allowed)
    write_gold("l2_errors.json", reid(balanced_sample(reid(pool), per_label=15)), allowed)
    write_gold("l2_error_detection.json",
               reid(balanced_sample(reid(detection), per_label=30)), {"Has error", "No error"})


def build_icnale_gra() -> None:
    # ICNALE GRA is password-gated: register at the download form to get the password,
    # download ICNALE_GRA_2.x.zip, then export a simple CSV with columns `text` (essay) and
    # `score` (a numeric rating; e.g. a consensus/averaged holistic score) to
    # raw/icnale_gra/essays_scores.csv. We band the numeric score into Low/Mid/High.
    import csv
    src = RAW / "icnale_gra" / "essays_scores.csv"
    if not src.exists():
        print("  SKIP icnale_gra: register at language.sakura.ne.jp/icnale (password-gated "
              "ICNALE_GRA_2.x.zip), then export raw/icnale_gra/essays_scores.csv "
              "with columns text,score")
        return

    def band(score: float) -> str:
        return "Low" if score < 4 else ("Mid" if score < 7 else "High")  # tune to the rubric

    rows = []
    with src.open(encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh):
            text = (r.get("text") or "").strip()
            raw_score = (r.get("score") or "").strip()
            if not text or not raw_score:
                continue
            rows.append({"id": 0, "text": text, "label": band(float(raw_score))})
    allowed = {"Low", "Mid", "High"}
    write_gold("icnale_gra_pool.json", reid(rows), allowed)
    write_gold("icnale_gra_scores.json", reid(balanced_sample(reid(rows), per_label=20)), allowed)


# --------------------------------------------------------------------------- main
BUILDERS = {
    "raamove": build_raamove,
    "cars50": build_cars50,
    "cefr": build_cefr,
    "l2_errors": build_l2_errors,
    "icnale_gra": build_icnale_gra,
}

if __name__ == "__main__":
    targets = sys.argv[1:] or list(BUILDERS)
    for name in targets:
        if name not in BUILDERS:
            print(f"unknown dataset {name!r}; choose from {list(BUILDERS)}")
            continue
        print(f"[{name}]")
        BUILDERS[name]()
