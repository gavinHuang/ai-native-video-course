#!/usr/bin/env python3
"""Read an A/B test of two variants honestly (C15·M01, C15·M03).

  python ab_report.py --a 120,4000 --b 152,4000                 # clicks,impressions for A and B
  python ab_report.py --a 120,4000 --b 152,4000 --min-effect 0.2  # also: impressions needed per variant
  python ab_report.py --plan --rate 0.03 --min-effect 0.2        # before the test: how many impressions?

Metric: a rate (click-through rate, 30-second retention, completion). Test: two-proportion z-test.
The report gives both rates, the relative difference with a 95 % confidence interval, and the p-value.
Rules: decide the metric and the minimum effect BEFORE the test; do not stop the test when it first looks
good; with p >= 0.05 the honest result is "no difference found", not "B is a little better".
"""
import argparse
import math


def norm_cdf(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def n_needed(p, rel, alpha=0.05, power=0.8):
    """Impressions per variant to detect a relative change rel of a base rate p (two-sided)."""
    p2 = p * (1 + rel)
    za, zb = 1.959964, 0.841621  # alpha 0.05 two-sided, power 0.8
    pbar = (p + p2) / 2
    num = (za * math.sqrt(2 * pbar * (1 - pbar)) + zb * math.sqrt(p * (1 - p) + p2 * (1 - p2))) ** 2
    return math.ceil(num / (p2 - p) ** 2)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--a")
    ap.add_argument("--b")
    ap.add_argument("--min-effect", type=float, default=0.2, help="smallest relative change worth acting on (0.2 = +20 %)")
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--rate", type=float, help="base rate for --plan")
    a = ap.parse_args()
    if a.plan:
        n = n_needed(a.rate, a.min_effect)
        print(f"base rate {a.rate:.2%}, detect {a.min_effect:+.0%}: about {n:,} impressions per variant (alpha 0.05, power 0.8)")
        return
    xa, na = map(int, a.a.split(","))
    xb, nb = map(int, a.b.split(","))
    pa, pb = xa / na, xb / nb
    p = (xa + xb) / (na + nb)
    se0 = math.sqrt(p * (1 - p) * (1 / na + 1 / nb))
    z = (pb - pa) / se0 if se0 else 0
    pval = 2 * (1 - norm_cdf(abs(z)))
    se = math.sqrt(pa * (1 - pa) / na + pb * (1 - pb) / nb)
    lo, hi = (pb - pa) - 1.96 * se, (pb - pa) + 1.96 * se
    print(f"A: {pa:.2%} ({xa}/{na})   B: {pb:.2%} ({xb}/{nb})")
    print(f"difference B-A: {pb - pa:+.2%} points ({(pb - pa) / pa:+.0%} relative); 95 % CI {lo:+.2%} to {hi:+.2%} points")
    print(f"z = {z:.2f}, p = {pval:.3f}")
    need = n_needed(pa, a.min_effect)
    if pval < 0.05:
        print("result: a real difference (at the 5 % level)" + ("" if abs(pb - pa) / pa >= a.min_effect else
              f", but smaller than the minimum effect of {a.min_effect:+.0%} that you set"))
    else:
        print(f"result: no difference found. To detect {a.min_effect:+.0%} you need about {need:,} impressions per variant "
              f"(you have {min(na, nb):,}).")


if __name__ == "__main__":
    main()
