#!/usr/bin/env python3
"""One-day model test: usable rate and cost per usable second per shot type (C17·M02).

Input: a CSV of blind scores, one row per clip:
    model,case,shot_type,seed,usable,seconds,cost_usd
usable is 1 or 0 (your usable rule from C01·M07). seconds = clip length.

    python model_trial.py scores.csv --incumbent current_model --candidate new_model
"""
import argparse, csv, math, sys
from collections import defaultdict


def wilson(k, n, z=1.96):
    """95 % Wilson interval for a rate k/n (good for small n)."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def fisher_greater(k1, n1, k2, n2):
    """One-sided Fisher exact p-value that rate 1 > rate 2."""
    K, N = k1 + k2, n1 + n2
    total = math.comb(N, K)
    return sum(math.comb(n1, i) * math.comb(n2, K - i)
               for i in range(k1, min(n1, K) + 1)) / total


def summarize(rows):
    """{(model, shot_type): dict} with n, usable, rate, interval, cost per usable second."""
    acc = defaultdict(lambda: {"n": 0, "k": 0, "sec": 0.0, "usable_sec": 0.0, "cost": 0.0})
    for r in rows:
        for key in ((r["model"], r["shot_type"]), (r["model"], "ALL")):
            a = acc[key]
            u = int(r["usable"])
            a["n"] += 1
            a["k"] += u
            a["sec"] += float(r["seconds"])
            a["usable_sec"] += float(r["seconds"]) * u
            a["cost"] += float(r["cost_usd"])
    out = {}
    for key, a in acc.items():
        lo, hi = wilson(a["k"], a["n"])
        out[key] = {
            "n": a["n"], "usable": a["k"], "rate": a["k"] / a["n"], "lo": lo, "hi": hi,
            "cost": a["cost"],
            "cost_per_usable_s": a["cost"] / a["usable_sec"] if a["usable_sec"] else float("inf"),
        }
    return out


def decide(inc, cand):
    """Suggest adopt / watch / ignore for one shot type. You make the final decision."""
    if fisher_greater(inc["usable"], inc["n"], cand["usable"], cand["n"]) < 0.05:
        return "ignore for this shot type (worse, p < 0.05)"
    better = fisher_greater(cand["usable"], cand["n"], inc["usable"], inc["n"]) < 0.05
    cheaper = cand["cost_per_usable_s"] < inc["cost_per_usable_s"]
    if better and cheaper:
        return "adopt"
    if better:
        return "adopt if the quality gain is worth the price"
    if cheaper and cand["rate"] >= inc["rate"] - 0.05:
        return "watch: similar quality, cheaper; test more cases"
    return "watch: no clear difference with this sample"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("scores")
    ap.add_argument("--incumbent", required=True)
    ap.add_argument("--candidate", required=True)
    a = ap.parse_args(argv)
    with open(a.scores, newline="") as f:
        rows = list(csv.DictReader(f))
    s = summarize(rows)
    types = sorted({t for (_, t) in s if t != "ALL"}) + ["ALL"]
    print(f"{'shot type':<12} {'model':<16} {'usable':>8} {'rate':>6} {'95% interval':>14} {'$/usable s':>11}")
    for t in types:
        for m in (a.incumbent, a.candidate):
            r = s.get((m, t))
            if not r:
                continue
            print(f"{t:<12} {m:<16} {r['usable']:>3}/{r['n']:<4} {r['rate']:>6.0%} "
                  f"{r['lo']:>6.0%}-{r['hi']:<6.0%} {r['cost_per_usable_s']:>11.3f}")
        inc, cand = s.get((a.incumbent, t)), s.get((a.candidate, t))
        if inc and cand and t != "ALL":
            p = fisher_greater(cand["usable"], cand["n"], inc["usable"], inc["n"])
            print(f"{'':<12} -> {decide(inc, cand)}  (p candidate better = {p:.3f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
