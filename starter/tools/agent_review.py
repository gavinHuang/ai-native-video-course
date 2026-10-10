#!/usr/bin/env python3
"""Check an agent's editing session: what it said it did against what changed (C08·M03).

  python otio_diff.py before.otio after.otio --json diff.json
  python agent_review.py --log agent_log.json --diff diff.json

agent_log.json is the list of actions that the agent reported (ask it to log every change in this form):
  [{"type": "renamed", "clip": "S04_t01", "to": "S04_hero"},
   {"type": "trimmed", "clip": "S02_t01"},
   {"type": "markers", "clip": "S01_t01"}]
Types: added, removed, reordered, renamed, trimmed, relinked, markers (the same as otio_diff.py).

Result: MATCH when every change in the diff was reported and every reported action is in the diff.
UNREPORTED changes are the dangerous ones: the agent changed something and did not say so.
"""
import argparse
import json
import sys


def key(c):
    return (c["type"], c.get("clip") or "")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--log", required=True)
    ap.add_argument("--diff", required=True)
    a = ap.parse_args()
    log = json.load(open(a.log))
    diff = json.load(open(a.diff))
    reported = {key(c) for c in log}
    found = {key(c) for c in diff}
    unreported = sorted(found - reported)
    missing = sorted(reported - found)
    for t, c in unreported:
        print(f"UNREPORTED change: {t} {c}  <- the agent did this without saying so; check it")
    for t, c in missing:
        print(f"NOT DONE: {t} {c}  <- the agent reported it, but the timeline does not show it")
    ok = not unreported and not missing
    print("MATCH" if ok else f"{len(unreported)} unreported, {len(missing)} not done")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
