#!/usr/bin/env python3
"""Refresh the generated cells of the day notebooks, and clear their outputs.

The notebooks are the source of truth: you edit them directly, in Jupyter, VSCode or
Colab. Two kinds of cell are the exception — the 📦 Setup cell and each 🔧 Library
cell — because they carry rules about what a day is allowed to ship. Those cells
record their builder and its arguments in their own `lda2` cell metadata, and this
script rewrites their source from that record. Everything else is left untouched.

    python sources/notebooks/_sync_notebooks.py                 # refresh all five
    python sources/notebooks/_sync_notebooks.py --notebook day3 # just one
    python sources/notebooks/_sync_notebooks.py --check         # report, change nothing
    python sources/notebooks/_sync_notebooks.py --stdin-strip   # git clean filter

To change which helpers a step ships, edit that cell's `names` metadata and re-run.
See planning/course_planning/notebook-coding-principles.md.
"""
import argparse
import difflib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _notebook_lib as L

HERE = Path(__file__).resolve().parent


def notebooks(pattern=None):
    """The day notebooks, or the ones whose filename contains `pattern`."""
    found = sorted(p for p in HERE.glob("*.ipynb"))
    if pattern:
        found = [p for p in found if pattern in p.name]
    return found


def strip_outputs(nb):
    """Clear every code cell's outputs and the metadata a run leaves behind.

    Notebooks are committed without outputs so their diffs stay readable, but you
    still want to run cells while writing them. This undoes the run, not the edit.

    Returns:
        True if anything was cleared.
    """
    changed = False
    for cell in nb["cells"]:
        if cell["cell_type"] != "code":
            continue
        if cell.get("outputs") or cell.get("execution_count") is not None:
            cell["outputs"] = []
            cell["execution_count"] = None
            changed = True
        for key in ("execution", "ExecuteTime"):
            if key in cell.get("metadata", {}):
                del cell["metadata"][key]
                changed = True
        colab = cell.get("metadata", {}).get("colab")
        if isinstance(colab, dict) and "executeInfo" in colab:
            del colab["executeInfo"]
            changed = True
    return changed


def rebuild_generated(nb, name, report):
    """Rewrite each generated cell's source from its own `lda2` metadata.

    Args:
        nb: the loaded notebook.
        name: its filename, for the report.
        report: lines describing what changed, appended to in place.

    Returns:
        True if any cell's source changed.
    """
    changed = False
    for index, cell in enumerate(nb["cells"]):
        spec = cell.get("metadata", {}).get(L.LDA2)
        if not spec:
            continue
        try:
            fresh = L.build(spec)
        except (KeyError, TypeError) as error:
            report.append(f"{name} cell {index}: cannot rebuild — {error}")
            continue
        before, after = "".join(cell["source"]), "".join(fresh["source"])
        if before == after:
            continue
        changed = True
        report.append(f"{name} cell {index}: rebuilt from its {spec['generated']} metadata")
        report += ["    " + line for line in difflib.unified_diff(
            before.split("\n"), after.split("\n"),
            "in the notebook", "rebuilt", lineterm="", n=1)]
        cell["source"] = fresh["source"]
    return changed


def sync(path, check=False):
    """Refresh one notebook. Returns (changed, report lines)."""
    nb = json.loads(path.read_text(encoding="utf-8"))
    report = []
    changed = rebuild_generated(nb, path.name, report)
    if strip_outputs(nb):
        changed = True
        report.append(f"{path.name}: cleared cell outputs")
    if changed and not check:
        path.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    return changed, report


def stdin_strip():
    """Clear outputs on a notebook piped through stdin (the git clean filter).

    Only outputs are cleared here — never the generated cells. A filter runs on every
    commit, and silently rewriting cell *source* underneath a commit would stage
    something the author never saw.
    """
    nb = json.loads(sys.stdin.read())
    strip_outputs(nb)
    sys.stdout.write(json.dumps(nb, indent=1, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true",
                        help="report what would change and exit 1 if anything would")
    parser.add_argument("--notebook", metavar="NAME",
                        help="only notebooks whose filename contains NAME, e.g. day3")
    parser.add_argument("--stdin-strip", action="store_true",
                        help="clear outputs on a notebook read from stdin (git filter)")
    args = parser.parse_args()

    if args.stdin_strip:
        stdin_strip()
        return 0

    targets = notebooks(args.notebook)
    if not targets:
        print(f"No notebook matches {args.notebook!r}", file=sys.stderr)
        return 2

    dirty = []
    for path in targets:
        changed, report = sync(path, check=args.check)
        for line in report:
            print(line)
        if changed:
            dirty.append(path.name)

    if not dirty:
        print(f"{len(targets)} notebook(s) already in sync.")
        return 0
    if args.check:
        print(f"\n{len(dirty)} notebook(s) out of sync: {', '.join(dirty)}")
        print("Run: python sources/notebooks/_sync_notebooks.py")
        return 1
    print(f"\nUpdated {len(dirty)} notebook(s): {', '.join(dirty)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
