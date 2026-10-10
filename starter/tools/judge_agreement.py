#!/usr/bin/env python3
"""How well does an LLM judge agree with human scores? (C03·M03)

Input CSV, one row per item and criterion:
    item,criterion,human,judge
Scores can be pass/fail, 1-5, or any labels. For numeric scales, --within 1 also counts
scores that differ by at most 1 as agreement.

    python judge_agreement.py scores.csv [--within 1]

Prints per criterion: n, raw agreement, Cohen's kappa (agreement beyond chance), and a verdict.
"""
import argparse, csv, sys
from collections import Counter, defaultdict


def kappa(pairs):
    n = len(pairs)
    po = sum(a == b for a, b in pairs) / n
    ha, ja = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ha[k] * ja.get(k, 0) for k in ha) / (n * n)
    return po, (po - pe) / (1 - pe) if pe < 1 else 1.0


def verdict(po, k, n):
    if n < 30:
        return "too few items (use 30 or more)"
    if k >= 0.8:
        return "use the judge"
    if k >= 0.6:
        return "use as a first filter; humans check the fails"
    return "do not use; rewrite the criterion with examples, or keep it human"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("scores")
    ap.add_argument("--within", type=float, default=None)
    a = ap.parse_args(argv)
    by = defaultdict(list)
    with open(a.scores, newline="") as f:
        for r in csv.DictReader(f):
            by[r["criterion"]].append((r["human"].strip(), r["judge"].strip()))
    print(f"{'criterion':<16} {'n':>4} {'agree':>7} {'kappa':>7}  verdict")
    for c, pairs in sorted(by.items()):
        po, k = kappa(pairs)
        line = f"{c:<16} {len(pairs):>4} {po:>7.0%} {k:>7.2f}  {verdict(po, k, len(pairs))}"
        if a.within is not None:
            try:
                near = sum(abs(float(x) - float(y)) <= a.within for x, y in pairs) / len(pairs)
                line += f"  (within ±{a.within:g}: {near:.0%})"
            except ValueError:
                pass
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
