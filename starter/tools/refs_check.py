#!/usr/bin/env python3
"""Check a reference library (C04·M03). Pipelines (C11, C12) read references by ID, so the library must be exact.

Layout:
  refs/
    CHAR-MARA/  sheet.json  01_front.png  02_34.png  03_side.png ...
    LOC-LOCKER/ sheet.json  wide.png  reverse.png  pano.png ...
    PROD-BOTTLE/ sheet.json ...

sheet.json:
  {
    "id": "CHAR-MARA",
    "kind": "character",                 # character | product | location
    "descriptor": "Mara, early 30s, short black bob, small scar through the LEFT eyebrow, olive raincoat ...",
    "source": "generated",               # generated | photo | licensed
    "rights": "own",                     # own | licensed | consent
    "consent_file": null,                # required for a real person (C16·M02)
    "views": {"front": "01_front.png", "three_quarter": "02_34.png", "side": "03_side.png", "back": "04_back.png"},
    "extra": {"expr_happy": "10_happy.png"},
    "voice_id": null
  }

Usage:  python refs_check.py refs/
"""
import json
import re
import sys
from pathlib import Path

REQUIRED_VIEWS = {
    "character": ["front", "three_quarter", "side", "back"],
    "product": ["front", "back", "left", "right", "top", "logo"],
    "location": ["wide", "reverse"],
}
ID_RE = re.compile(r"^(CHAR|PROD|LOC)-[A-Z0-9]+(-[A-Z0-9]+)*$")


def check_sheet(folder):
    problems = []
    p = folder / "sheet.json"
    if not p.exists():
        return [f"{folder.name}: no sheet.json"]
    try:
        s = json.loads(p.read_text())
    except json.JSONDecodeError as e:
        return [f"{folder.name}: sheet.json is not valid JSON ({e})"]
    sid = s.get("id")
    if sid != folder.name:
        problems.append(f"{folder.name}: id '{sid}' differs from the folder name")
    if not sid or not ID_RE.match(sid):
        problems.append(f"{folder.name}: id must look like CHAR-NAME, PROD-NAME, or LOC-NAME")
    kind = s.get("kind")
    if kind not in REQUIRED_VIEWS:
        problems.append(f"{folder.name}: kind must be character, product, or location")
        return problems
    prefix = {"character": "CHAR-", "product": "PROD-", "location": "LOC-"}[kind]
    if sid and not sid.startswith(prefix):
        problems.append(f"{folder.name}: a {kind} id must start with {prefix}")
    if len(s.get("descriptor", "").split()) < 8:
        problems.append(f"{folder.name}: descriptor is too short (write the fixed sentence that every prompt uses)")
    if s.get("source") not in ("generated", "photo", "licensed"):
        problems.append(f"{folder.name}: source must be generated, photo, or licensed")
    if s.get("rights") not in ("own", "licensed", "consent"):
        problems.append(f"{folder.name}: rights must be own, licensed, or consent (not '{s.get('rights')}')")
    if s.get("source") == "photo" and kind == "character" and not s.get("consent_file"):
        problems.append(f"{folder.name}: a photo of a real person needs consent_file (C16·M02)")
    if s.get("consent_file") and not (folder / s["consent_file"]).exists():
        problems.append(f"{folder.name}: consent file {s['consent_file']} not found")
    views = s.get("views", {})
    for v in REQUIRED_VIEWS[kind]:
        if v not in views:
            problems.append(f"{folder.name}: missing view '{v}'")
    for name, f in {**views, **s.get("extra", {})}.items():
        if not (folder / f).exists():
            problems.append(f"{folder.name}: file for '{name}' not found: {f}")
    listed = set(views.values()) | set(s.get("extra", {}).values()) | {"sheet.json", s.get("consent_file")}
    for f in folder.iterdir():
        if f.is_file() and f.name not in listed and not f.name.startswith("."):
            problems.append(f"{folder.name}: file {f.name} is not listed in sheet.json")
    return problems


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "refs")
    folders = sorted(d for d in root.iterdir() if d.is_dir())
    problems = [p for d in folders for p in check_sheet(d)]
    for p in problems:
        print("PROBLEM", p)
    print(f"{len(folders)} reference sets, {len(problems)} problems")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
