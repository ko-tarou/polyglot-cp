"""Polyglot CP problem generator.

Produces ~500 self-contained problems from the parametric families in
families.py. For each concrete problem it emits:

  problems/<id>/statement.md   problem statement (JA) + constraints + I/O + samples
  problems/<id>/meta.json      id/title/topic/difficulty/tags/samples(inline)/...
  problems/<id>/solution.py    reference solution (the single source of truth)
  problems/<id>/tests/         sampleNN.in/.out (shown) + testNN.in/.out (hidden)

The reference solution is THE source of truth: every expected output is produced
by actually running solution.py (in-process, isolated namespace) on each input.
A separate verifier (verify_problems.py) re-runs solution.py as a real subprocess
on a sample of problems and diffs against the stored .out to prove they pass.

Usage:
  python3 tools/generate_problems.py [--out problems] [--seed 42]
"""

import argparse
import io
import json
import os
import random
import shutil
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from families import FAMILIES  # noqa: E402

SAMPLES = 2      # visible sample cases per problem
HIDDEN = 5       # hidden test cases per problem


def run_solution(src, inp):
    """Run a reference solution source in an isolated namespace with redirected IO."""
    ns = {"__name__": "__main__"}
    old_in, old_out = sys.stdin, sys.stdout
    sys.stdin = io.StringIO(inp)
    buf = io.StringIO()
    sys.stdout = buf
    try:
        exec(compile(src, "<solution>", "exec"), ns)
    finally:
        sys.stdin, sys.stdout = old_in, old_out
    out = buf.getvalue()
    # normalize: strip trailing newlines, re-add exactly one (conventional .out)
    return out.rstrip("\n") + "\n" if out.strip() != "" else out.rstrip("\n") + "\n"


def gen_inputs(fam, diff, rng, count):
    """Generate `count` distinct-ish inputs, seeding the first ones with edge cases."""
    inputs = []
    seen = set()
    edges = fam.get("edges", lambda d: [])(diff)
    for e in edges:
        if e not in seen:
            inputs.append(e)
            seen.add(e)
        if len(inputs) >= count:
            return inputs[:count]
    attempts = 0
    while len(inputs) < count and attempts < count * 40:
        attempts += 1
        try:
            s = fam["gen"](diff, rng)
        except Exception:
            continue
        if s and s not in seen:
            inputs.append(s)
            seen.add(s)
    # if we still came up short (tiny input spaces), pad by repeating
    while len(inputs) < count and inputs:
        inputs.append(inputs[len(inputs) % len(edges) if edges else 0])
    return inputs[:count]


def md_io_block(inp, out):
    return (
        "入力:\n\n```\n" + inp.rstrip("\n") + "\n```\n\n"
        "出力:\n\n```\n" + out.rstrip("\n") + "\n```\n"
    )


def build_statement(fam, diff, title, samples):
    parts = [f"# {title}\n", f"難易度: {diff} / 4 ・ トピック: {fam['topic']}\n", fam["statement"](diff)]
    parts.append("\n## 入出力例\n")
    for i, (inp, out) in enumerate(samples, 1):
        parts.append(f"\n### 例 {i}\n\n" + md_io_block(inp, out))
    return "\n".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "problems"))
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    out_root = args.out
    if os.path.exists(out_root):
        shutil.rmtree(out_root)
    os.makedirs(out_root)

    index = []
    topic_diff = Counter()
    topic_count = Counter()
    diff_count = Counter()
    serial = 0
    errors = []

    for fam in FAMILIES:
        for diff in fam["difficulties"]:
            for _ in range(fam["per_diff"]):
                serial += 1
                pid = f"{fam['key']}-d{diff}-{serial:04d}"
                rng = random.Random(f"{args.seed}:{pid}")
                title = fam["title"](diff)

                inputs = gen_inputs(fam, diff, rng, SAMPLES + HIDDEN)
                cases = []
                try:
                    for inp in inputs:
                        out = run_solution(fam["solution"], inp)
                        cases.append((inp, out))
                except Exception as e:  # solution crashed on a generated input
                    errors.append((pid, str(e)))
                    serial -= 1
                    continue

                pdir = os.path.join(out_root, pid)
                tdir = os.path.join(pdir, "tests")
                os.makedirs(tdir)

                with open(os.path.join(pdir, "solution.py"), "w") as f:
                    f.write(fam["solution"])

                sample_pairs = cases[:SAMPLES]
                for i, (inp, out) in enumerate(cases, 1):
                    name = f"sample{i:02d}" if i <= SAMPLES else f"test{i-SAMPLES:02d}"
                    with open(os.path.join(tdir, name + ".in"), "w") as f:
                        f.write(inp)
                    with open(os.path.join(tdir, name + ".out"), "w") as f:
                        f.write(out)

                statement = build_statement(fam, diff, title, sample_pairs)
                with open(os.path.join(pdir, "statement.md"), "w") as f:
                    f.write(statement)

                meta = {
                    "id": pid,
                    "title": title,
                    "topic": fam["topic"],
                    "difficulty": diff,
                    "tags": fam.get("tags", []),
                    "samples": [{"input": inp, "output": out.rstrip("\n")} for inp, out in sample_pairs],
                    "num_samples": len(sample_pairs),
                    "num_hidden_tests": len(cases) - len(sample_pairs),
                    "reference_language": "python",
                    "reference_solution": "solution.py",
                }
                with open(os.path.join(pdir, "meta.json"), "w") as f:
                    json.dump(meta, f, ensure_ascii=False, indent=2)

                index.append({
                    "id": pid, "title": title, "topic": fam["topic"],
                    "difficulty": diff, "tags": fam.get("tags", []), "dir": pid,
                })
                topic_diff[(fam["topic"], diff)] += 1
                topic_count[fam["topic"]] += 1
                diff_count[diff] += 1

    with open(os.path.join(out_root, "index.json"), "w") as f:
        json.dump({"count": len(index), "problems": index}, f, ensure_ascii=False, indent=2)

    print(f"generated {len(index)} problems into {out_root}")
    print("\nby difficulty:")
    for d in sorted(diff_count):
        print(f"  d{d}: {diff_count[d]}")
    print("\nby topic:")
    for t in sorted(topic_count):
        print(f"  {t:12s}: {topic_count[t]}")
    print("\nby topic x difficulty:")
    for (t, d) in sorted(topic_diff):
        print(f"  {t:12s} d{d}: {topic_diff[(t,d)]}")
    if errors:
        print(f"\nWARNING: {len(errors)} family/diff combos errored (skipped):")
        for pid, e in errors[:20]:
            print(f"  {pid}: {e}")


if __name__ == "__main__":
    main()
