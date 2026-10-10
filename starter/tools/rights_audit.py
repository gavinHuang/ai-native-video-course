#!/usr/bin/env python3
"""Audit the rights of a project before delivery (C16·M01, C16·M02).

  python rights_audit.py --project "The Camera" [--registry registry.yaml] [--date 2026-10-04]
  (run in the project folder; it reads prompts/log.jsonl and rights/log.jsonl, like promptlog.py)

Checks:
  - every reference used in the prompt log that you did not make has a rights line (as promptlog.py check)
  - rights lines with a consent file: the file exists; an 'expires' date is not past
  - license fields that need attention: non-commercial, research-only, editorial-only, unknown
  - registry adapters (C14·M03): expired, or not allowed for this project
Output: a table of problems and warnings; exit 1 if a problem is found.
"""
import argparse
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import promptlog  # noqa: E402

RISKY = ("non-commercial", "noncommercial", "nc", "research", "editorial", "unknown", "personal use")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", required=True)
    ap.add_argument("--registry")
    ap.add_argument("--date", default=dt.date.today().isoformat())
    a = ap.parse_args()
    problems = list(promptlog.check())
    warnings = []
    for n, e in promptlog.read(promptlog.RIGHTS_LOG):
        where = f"rights:{n} {e.get('id')}"
        lic = str(e.get("license", "")).lower()
        if any(r == lic or f" {r}" in f" {lic}" or f"{r} " in lic for r in RISKY):
            warnings.append(f"{where}: license '{e.get('license')}' - check that it allows this use ({e.get('use')})")
        if e.get("expires") and e["expires"] < a.date:
            problems.append(f"{where}: expired on {e['expires']} - remove the asset or renew the license/consent")
        if e.get("consent_file") and not Path(e["consent_file"]).exists():
            problems.append(f"{where}: consent file {e['consent_file']} not found")
        if e.get("people") and not e.get("consent_file"):
            problems.append(f"{where}: shows people {e['people']} but has no consent file")
    if a.registry:
        import yaml
        for ad in yaml.safe_load(Path(a.registry).read_text()) or []:
            where = f"registry {ad.get('id')}"
            if ad.get("expires") and str(ad["expires"]) < a.date:
                problems.append(f"{where}: expired on {ad['expires']} - the service must refuse it; delete the files as the consent requires")
            uses = ad.get("allowed_uses") or []
            if uses and a.project not in uses:
                warnings.append(f"{where}: not allowed for '{a.project}' (allowed: {', '.join(uses)}) - do not use it here")
    for w in warnings:
        print("WARN   ", w)
    for p in problems:
        print("PROBLEM", p)
    print(f"{len(problems)} problems, {len(warnings)} warnings (audit date {a.date})")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
