"""Verify generated problems: re-run each reference solution.py as a REAL
subprocess against every stored test input and diff the produced stdout against
the stored .out. This proves the bundled reference solution actually runs and
yields the recorded expected outputs (the same contract the judge uses).

Usage:
  python3 tools/verify_problems.py            # verify a random sample (default 40)
  python3 tools/verify_problems.py --all      # verify every problem
  python3 tools/verify_problems.py --sample 100 --seed 7
"""

import argparse
import glob
import os
import random
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def cases(pdir):
    tdir = os.path.join(pdir, "tests")
    for inf in sorted(glob.glob(os.path.join(tdir, "*.in"))):
        outf = inf[:-3] + ".out"
        yield inf, outf


def verify_problem(pdir):
    sol = os.path.join(pdir, "solution.py")
    n = 0
    for inf, outf in cases(pdir):
        with open(inf) as f:
            inp = f.read()
        with open(outf) as f:
            expected = f.read().rstrip("\n")
        try:
            r = subprocess.run([sys.executable, sol], input=inp, capture_output=True,
                               text=True, timeout=20)
        except subprocess.TimeoutExpired:
            return False, f"TIMEOUT on {os.path.basename(inf)}"
        if r.returncode != 0:
            return False, f"RE on {os.path.basename(inf)}: {r.stderr.strip()[:120]}"
        got = r.stdout.rstrip("\n")
        if got != expected:
            return False, f"WA on {os.path.basename(inf)}: got {got[:60]!r} want {expected[:60]!r}"
        n += 1
    return True, f"{n} cases OK"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--problems", default=os.path.join(ROOT, "problems"))
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--sample", type=int, default=40)
    ap.add_argument("--seed", type=int, default=1)
    args = ap.parse_args()

    pdirs = sorted(d for d in glob.glob(os.path.join(args.problems, "*")) if os.path.isdir(d))
    if not args.all:
        rng = random.Random(args.seed)
        pdirs = rng.sample(pdirs, min(args.sample, len(pdirs)))

    passed = 0
    failed = []
    for pdir in pdirs:
        ok, msg = verify_problem(pdir)
        if ok:
            passed += 1
        else:
            failed.append((os.path.basename(pdir), msg))

    print(f"verified {len(pdirs)} problems: {passed} PASS, {len(failed)} FAIL")
    for pid, msg in failed[:40]:
        print(f"  FAIL {pid}: {msg}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
