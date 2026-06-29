"""Bundle the on-disk problem set into static JSON assets for the SPA.

Reads the authoring tree under problems/<id>/ (statement.md, meta.json, tests/)
and emits self-contained JSON that the fully-static frontend can fetch directly
(no backend):

  public/problems/index.json    light list for the picker (id/title/topic/diff/tags)
  public/problems/<id>.json     full problem: statement + samples + ALL test cases

Every test case (visible sampleNN + hidden testNN) is inlined so the browser can
run a submission against the complete set client-side. NOTE: because the site is
fully static, hidden test I/O is shipped to the client (readable in devtools).
That is acceptable for a self-authored practice site; for a real contest you would
keep hidden tests behind a judge API instead.

Usage: python3 tools/build_static_problems.py [--src problems] [--out public/problems]
Stdlib only (no pip).
"""

import argparse
import json
import os
import sys


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def build_problem(src_dir):
    meta = json.loads(read(os.path.join(src_dir, "meta.json")))
    statement = read(os.path.join(src_dir, "statement.md"))
    tests_dir = os.path.join(src_dir, "tests")
    tests = []
    if os.path.isdir(tests_dir):
        names = sorted(
            n[:-3] for n in os.listdir(tests_dir) if n.endswith(".in")
        )
        for name in names:
            in_path = os.path.join(tests_dir, name + ".in")
            out_path = os.path.join(tests_dir, name + ".out")
            if not os.path.exists(out_path):
                continue
            tests.append({
                "name": name,
                "input": read(in_path),
                "output": read(out_path),
                # sampleNN are visible in the statement; testNN are hidden.
                "hidden": not name.startswith("sample"),
            })
    return {
        "id": meta["id"],
        "title": meta["title"],
        "topic": meta["topic"],
        "difficulty": meta["difficulty"],
        "tags": meta.get("tags", []),
        "statement": statement,
        "samples": meta.get("samples", []),
        "tests": tests,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="problems")
    ap.add_argument("--out", default=os.path.join("public", "problems"))
    args = ap.parse_args()

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src = os.path.join(root, args.src)
    out = os.path.join(root, args.out)
    os.makedirs(out, exist_ok=True)

    index_src = json.loads(read(os.path.join(src, "index.json")))
    index = []
    written = 0
    for entry in index_src["problems"]:
        pid = entry["id"]
        pdir = os.path.join(src, entry.get("dir", pid))
        if not os.path.isdir(pdir):
            print(f"  skip (missing dir): {pid}", file=sys.stderr)
            continue
        prob = build_problem(pdir)
        with open(os.path.join(out, pid + ".json"), "w", encoding="utf-8") as f:
            json.dump(prob, f, ensure_ascii=False, separators=(",", ":"))
        index.append({
            "id": prob["id"],
            "title": prob["title"],
            "topic": prob["topic"],
            "difficulty": prob["difficulty"],
            "tags": prob["tags"],
            "tests": len(prob["tests"]),
        })
        written += 1

    with open(os.path.join(out, "index.json"), "w", encoding="utf-8") as f:
        json.dump({"count": len(index), "problems": index}, f,
                  ensure_ascii=False, separators=(",", ":"))

    print(f"Wrote {written} problem JSONs + index.json to {out}")


if __name__ == "__main__":
    main()
