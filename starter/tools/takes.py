#!/usr/bin/env python3
"""Take log, selects, and budget for generation sessions (C05·M01, C05·M06, C15).

Every generated clip is a take. A take has a cost and a length. After review, a take has a decision
and, if selected, the usable part (in and out points). From this the tool computes the number that
matters for planning: cost per usable second, per model and per shot.

  python takes.py add S07 --model kling-3.0 --mode i2v --dur 6 --cost 0.60 --file takes/S07_t01.mp4
  python takes.py review S07_t01 select --in 0.4 --out 4.1 --note "hand flicker after 4.1 s"
  python takes.py review S07_t02 reject --note "face drift"
  python takes.py budget S07 --target 4 --cap 3.00       # usable seconds needed, money cap for the shot
  python takes.py report                                 # by model and by shot; flags shots over cap
  python takes.py selects                                # selects bin for the editor (CSV with trims)

Data: takes/takes.csv and takes/budget.csv in the current folder (plain CSV, open them in a spreadsheet).
"""
import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

DIR = Path("takes")
TAKES = DIR / "takes.csv"
BUDGET = DIR / "budget.csv"
T_FIELDS = ["take", "shot", "model", "mode", "dur", "cost", "file", "decision", "in", "out", "note"]
B_FIELDS = ["shot", "target_s", "cap_usd"]


def load(path, fields):
    if not path.exists():
        return []
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def save(path, fields, rows):
    DIR.mkdir(exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def usable(t):
    if t.get("decision") != "select":
        return 0.0
    a = float(t["in"] or 0)
    b = float(t["out"] or t["dur"])
    return max(0.0, b - a)


def cmd_add(a):
    rows = load(TAKES, T_FIELDS)
    n = 1 + sum(1 for r in rows if r["shot"] == a.shot)
    take = f"{a.shot}_t{n:02d}"
    rows.append({"take": take, "shot": a.shot, "model": a.model, "mode": a.mode or "", "dur": a.dur,
                 "cost": a.cost, "file": a.file or "", "decision": "", "in": "", "out": "", "note": ""})
    save(TAKES, T_FIELDS, rows)
    print(take)


def cmd_review(a):
    rows = load(TAKES, T_FIELDS)
    for r in rows:
        if r["take"] == a.take:
            if a.decision == "select":
                dur = float(r["dur"])
                i = a.in_ if a.in_ is not None else 0.0
                o = a.out if a.out is not None else dur
                if not 0 <= i < o <= dur:
                    sys.exit(f"in/out must satisfy 0 <= in < out <= {dur}")
                r["in"], r["out"] = f"{i:.2f}", f"{o:.2f}"
            r["decision"] = a.decision
            r["note"] = a.note or r["note"]
            save(TAKES, T_FIELDS, rows)
            print(f"{a.take}: {a.decision}" + (f" {r['in']}–{r['out']} s" if a.decision == "select" else ""))
            return
    sys.exit(f"no take {a.take}")


def cmd_budget(a):
    rows = [r for r in load(BUDGET, B_FIELDS) if r["shot"] != a.shot]
    rows.append({"shot": a.shot, "target_s": a.target, "cap_usd": a.cap})
    save(BUDGET, B_FIELDS, rows)
    print(f"{a.shot}: target {a.target} usable s, cap US${a.cap:.2f}")


def cmd_report(a):
    takes = load(TAKES, T_FIELDS)
    budget = {r["shot"]: r for r in load(BUDGET, B_FIELDS)}
    by_model = defaultdict(lambda: {"takes": 0, "reviewed": 0, "selects": 0, "gen_s": 0.0, "use_s": 0.0, "cost": 0.0})
    by_shot = defaultdict(lambda: {"takes": 0, "use_s": 0.0, "cost": 0.0})
    for t in takes:
        m, s = by_model[t["model"]], by_shot[t["shot"]]
        m["takes"] += 1
        m["reviewed"] += 1 if t["decision"] else 0
        m["selects"] += 1 if t["decision"] == "select" else 0
        m["gen_s"] += float(t["dur"])
        m["use_s"] += usable(t)
        m["cost"] += float(t["cost"])
        s["takes"] += 1
        s["use_s"] += usable(t)
        s["cost"] += float(t["cost"])
    print(f"{'model':24} {'takes':>5} {'select rate':>11} {'usable %':>8} {'US$':>8} {'US$/usable s':>12}")
    for name, m in sorted(by_model.items()):
        rate = m["selects"] / m["reviewed"] if m["reviewed"] else 0
        pct = 100 * m["use_s"] / m["gen_s"] if m["gen_s"] else 0
        cpus = m["cost"] / m["use_s"] if m["use_s"] else float("inf")
        print(f"{name:24} {m['takes']:5d} {rate:11.0%} {pct:7.0f}% {m['cost']:8.2f} {cpus:12.2f}")
    print()
    print(f"{'shot':8} {'takes':>5} {'usable s':>8} {'target':>6} {'US$':>7} {'cap':>7}  status")
    over = 0
    for shot, s in sorted(by_shot.items()):
        b = budget.get(shot, {})
        target = float(b["target_s"]) if b else None
        cap = float(b["cap_usd"]) if b else None
        status = []
        if target is not None:
            status.append("covered" if s["use_s"] >= target else f"GAP {target - s['use_s']:.1f} s")
        if cap is not None and s["cost"] > cap:
            status.append("OVER CAP: change the approach")
            over += 1
        print(f"{shot:8} {s['takes']:5d} {s['use_s']:8.1f} {target if target is not None else '-':>6} "
              f"{s['cost']:7.2f} {cap if cap is not None else '-':>7}  {', '.join(status)}")
    total = sum(s["cost"] for s in by_shot.values())
    caps = sum(float(b["cap_usd"]) for b in budget.values())
    print(f"\ntotal US${total:.2f} of US${caps:.2f} capped; {over} shot(s) over cap")


def cmd_selects(a):
    w = csv.writer(sys.stdout)
    w.writerow(["shot", "take", "file", "in", "out", "usable_s", "note"])
    for t in load(TAKES, T_FIELDS):
        if t["decision"] == "select":
            w.writerow([t["shot"], t["take"], t["file"], t["in"], t["out"], f"{usable(t):.2f}", t["note"]])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("add")
    p.add_argument("shot")
    p.add_argument("--model", required=True)
    p.add_argument("--mode")
    p.add_argument("--dur", type=float, required=True)
    p.add_argument("--cost", type=float, required=True)
    p.add_argument("--file")
    p = sub.add_parser("review")
    p.add_argument("take")
    p.add_argument("decision", choices=["select", "reject", "maybe"])
    p.add_argument("--in", dest="in_", type=float)
    p.add_argument("--out", type=float)
    p.add_argument("--note")
    p = sub.add_parser("budget")
    p.add_argument("shot")
    p.add_argument("--target", type=float, required=True)
    p.add_argument("--cap", type=float, required=True)
    sub.add_parser("report")
    sub.add_parser("selects")
    a = ap.parse_args()
    {"add": cmd_add, "review": cmd_review, "budget": cmd_budget, "report": cmd_report, "selects": cmd_selects}[a.cmd](a)


if __name__ == "__main__":
    main()
