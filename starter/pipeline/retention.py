#!/usr/bin/env python3
"""Find the moments where viewers leave (or rewatch) in a retention curve (C15·M03).

  python retention.py retention.csv [--edl cut.edl | --shots shots.json] [--top 3]

retention.csv: two columns exported from the platform's analytics: time_s,pct  (share of viewers still watching)
The tool compares each second's drop with the typical drop of the video, and lists:
  - steep drops: viewers leave faster than usual (a weak moment: slow start, confusing cut, broken promise)
  - bumps: the curve rises (people rewatch or skip back to a moment)
With --shots (the shot list with durations, C03·M02) each moment is mapped to its shot ID, so the finding goes
back into the shot list, the hook library, and the routing table.
"""
import argparse
import csv
import json
import statistics
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv")
    ap.add_argument("--shots", help="shot list JSON with id and dur, in order")
    ap.add_argument("--top", type=int, default=3)
    a = ap.parse_args()
    pts = [(float(r["time_s"]), float(r["pct"])) for r in csv.DictReader(open(a.csv))]
    pts.sort()
    drops = [(pts[i][0], pts[i - 1][1] - pts[i][1]) for i in range(1, len(pts))]
    typical = statistics.median(d for _, d in drops[3:]) if len(drops) > 4 else statistics.median(d for _, d in drops)
    shots = []
    if a.shots:
        t = 0.0
        for s in json.loads(Path(a.shots).read_text()):
            shots.append((t, t + float(s["dur"]), s["id"]))
            t += float(s["dur"])

    def shot_at(t):
        return next((sid for s, e, sid in shots if s <= t < e), "-")

    print(f"start {pts[0][1]:.0f} %, end {pts[-1][1]:.0f} % at {pts[-1][0]:.0f} s; typical drop {typical:.2f} points/s")
    for t, p in pts:
        if t in (3, 30):
            print(f"  held at {t:.0f} s: {p:.0f} %")
    steep = sorted(drops, key=lambda x: -x[1])[: a.top]
    print("steep drops (time, points lost in that second, shot):")
    for t, d in sorted(steep):
        print(f"  {t:5.0f} s  -{d:.1f}  ({d / typical if typical else 0:.1f}x typical)  {shot_at(t - 0.5)}")
    bumps = [(t, -d) for t, d in drops if d < 0]
    if bumps:
        print("bumps (rewatching):")
        for t, d in sorted(bumps, key=lambda x: -x[1])[: a.top]:
            print(f"  {t:5.0f} s  +{d:.1f}  {shot_at(t - 0.5)}")


if __name__ == "__main__":
    main()
