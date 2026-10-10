#!/usr/bin/env python3
"""Prompt log and rights log for the whole program (one JSON object per line).

Every generated asset gets a line in prompts/log.jsonl. Every asset that you did not make
gets a line in rights/log.jsonl. C16 and the capstone use both logs.

Usage:
  python promptlog.py add --id KF-S07-v3 --model gemini-3-pro-image --prompt-file p.txt \
      --refs CHAR-MARA-01,LOC-LOCKER-02 --seed 1234 --cost 0.13 --file out/KF-S07-v3.png
  python promptlog.py check                      # validate both logs, check that files exist
  python promptlog.py cost --since 2026-10-01    # spend by model
  python promptlog.py find KF-S07                # all lines whose id starts with KF-S07

As a library:
  from promptlog import add_entry
  add_entry(id="S07_a", model="flux-2-klein-4b", prompt="...", seed=7, refs=["CHAR-MARA-01"], cost_usd=0.0)
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(os.environ.get("AI_VIDEO_LAB", "."))
PROMPT_LOG = ROOT / "prompts" / "log.jsonl"
RIGHTS_LOG = ROOT / "rights" / "log.jsonl"

PROMPT_REQUIRED = {"id", "date", "model", "prompt"}
PROMPT_OPTIONAL = {"seed", "settings", "refs", "cost_usd", "file", "sha256", "parent", "status", "note", "workflow"}
RIGHTS_REQUIRED = {"id", "date", "source", "license", "use"}
RIGHTS_OPTIONAL = {"consent_file", "expires", "url", "file", "sha256", "note", "people"}
STATUS = {"kept", "rejected", "final", None}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def append(path, entry):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def add_entry(**kw):
    """Add one prompt-log line. Returns the entry."""
    e = {k: v for k, v in kw.items() if v is not None}
    e.setdefault("date", dt.date.today().isoformat())
    if e.get("file") and Path(e["file"]).is_file():
        e["sha256"] = sha256(e["file"])
    missing = PROMPT_REQUIRED - e.keys()
    if missing:
        raise ValueError(f"missing fields: {sorted(missing)}")
    append(PROMPT_LOG, e)
    return e


def read(path):
    if not path.exists():
        return []
    rows = []
    for n, line in enumerate(path.read_text().splitlines(), 1):
        if line.strip():
            try:
                rows.append((n, json.loads(line)))
            except json.JSONDecodeError as err:
                rows.append((n, {"_error": str(err)}))
    return rows


# IDs of assets that you made yourself (sheets, key frames, shots). Other references need a rights line.
OWN_ID = re.compile(r"^(CHAR|LOC|PROD|KF)-|^S\d+")


def check():
    problems = []
    ids = set()
    rights_ids = {e.get("id") for _, e in read(RIGHTS_LOG)}
    for path, req, opt in ((PROMPT_LOG, PROMPT_REQUIRED, PROMPT_OPTIONAL), (RIGHTS_LOG, RIGHTS_REQUIRED, RIGHTS_OPTIONAL)):
        for n, e in read(path):
            where = f"{path}:{n}"
            if "_error" in e:
                problems.append(f"{where}: not valid JSON ({e['_error']})")
                continue
            for k in sorted(req - e.keys()):
                problems.append(f"{where}: missing '{k}'")
            for k in sorted(e.keys() - req - opt):
                problems.append(f"{where}: unknown field '{k}' (typo?)")
            if path == PROMPT_LOG and e.get("status") not in STATUS:
                problems.append(f"{where}: status must be kept, rejected, or final")
            if e.get("file"):
                p = Path(e["file"])
                if not p.is_file():
                    problems.append(f"{where}: file {p} does not exist")
                elif e.get("sha256") and sha256(p) != e["sha256"]:
                    problems.append(f"{where}: file {p} changed after it was logged (hash differs)")
            if path == PROMPT_LOG:
                if e.get("id") in ids:
                    problems.append(f"{where}: duplicate id {e['id']}")
                ids.add(e.get("id"))
                for r in e.get("refs", []) or []:
                    if not OWN_ID.match(r) and r not in rights_ids:
                        problems.append(f"{where}: reference {r} has no rights-log line")
    return problems


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add")
    a.add_argument("--id", required=True)
    a.add_argument("--model", required=True)
    g = a.add_mutually_exclusive_group(required=True)
    g.add_argument("--prompt")
    g.add_argument("--prompt-file")
    a.add_argument("--seed", type=int)
    a.add_argument("--refs", help="comma-separated reference IDs")
    a.add_argument("--settings", help='JSON, for example {"steps": 4}')
    a.add_argument("--cost", type=float)
    a.add_argument("--file")
    a.add_argument("--parent", help="id of the asset that this one edits")
    a.add_argument("--status", choices=["kept", "rejected", "final"])
    a.add_argument("--note")
    r = sub.add_parser("rights")
    r.add_argument("--id", required=True)
    r.add_argument("--source", required=True, help="who made it or where it came from")
    r.add_argument("--license", required=True)
    r.add_argument("--use", required=True, help="what you may use it for")
    r.add_argument("--url")
    r.add_argument("--file")
    r.add_argument("--consent-file")
    sub.add_parser("check")
    c = sub.add_parser("cost")
    c.add_argument("--since")
    f = sub.add_parser("find")
    f.add_argument("prefix")
    args = ap.parse_args()

    if args.cmd == "add":
        prompt = args.prompt if args.prompt is not None else Path(args.prompt_file).read_text().strip()
        e = add_entry(id=args.id, model=args.model, prompt=prompt, seed=args.seed,
                      refs=args.refs.split(",") if args.refs else None,
                      settings=json.loads(args.settings) if args.settings else None,
                      cost_usd=args.cost, file=args.file, parent=args.parent, status=args.status, note=args.note)
        print(json.dumps(e, ensure_ascii=False))
    elif args.cmd == "rights":
        e = {"id": args.id, "date": dt.date.today().isoformat(), "source": args.source, "license": args.license,
             "use": args.use, "url": args.url, "file": args.file, "consent_file": args.consent_file}
        e = {k: v for k, v in e.items() if v is not None}
        if e.get("file") and Path(e["file"]).is_file():
            e["sha256"] = sha256(e["file"])
        append(RIGHTS_LOG, e)
        print(json.dumps(e, ensure_ascii=False))
    elif args.cmd == "check":
        problems = check()
        for p in problems:
            print("PROBLEM", p)
        print(f"{len(read(PROMPT_LOG))} prompt lines, {len(read(RIGHTS_LOG))} rights lines, {len(problems)} problems")
        sys.exit(1 if problems else 0)
    elif args.cmd == "cost":
        tot = defaultdict(float)
        for _, e in read(PROMPT_LOG):
            if args.since and e.get("date", "") < args.since:
                continue
            tot[e.get("model", "?")] += float(e.get("cost_usd") or 0)
        for m, v in sorted(tot.items(), key=lambda x: -x[1]):
            print(f"{m:40} US${v:8.2f}")
        print(f"{'total':40} US${sum(tot.values()):8.2f}")
    elif args.cmd == "find":
        for _, e in read(PROMPT_LOG):
            if str(e.get("id", "")).startswith(args.prefix):
                print(json.dumps(e, ensure_ascii=False))


if __name__ == "__main__":
    main()
