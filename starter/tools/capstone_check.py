#!/usr/bin/env python3
"""Check a capstone delivery package before you submit it (C18·M02).

    python capstone_check.py capstone/delivery.json [--allow-test-cert] [--json report.json]

delivery.json lists what you deliver; paths are relative to the JSON file:
{
  "plan":      ["plan/treatment.md", "plan/bible.md", "plan/shots.json", "plan/routing.md",
                "plan/pipeline.md", "plan/rights_disclosure.md", "plan/schedule_risks.md"],
  "files":     [{"file": "deliver/film_web.mp4", "spec": "specs/web_1080p.json", "signed": true}],
  "captions":  ["deliver/film.en.srt", "deliver/film.de.srt"],
  "stems":     ["deliver/stems/DX.wav", "deliver/stems/MX.wav", "deliver/stems/FX.wav"],
  "logs":      ["logs/prompts.jsonl", "logs/rights.jsonl"],
  "writeup":   "writeup.md",
  "rubric":    "rubric_scores.json"
}
Each check maps to a rubric row. The tool proves completeness, not quality: you and a peer score quality.
"""
import argparse, json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import spec_check  # noqa: E402

ROWS = ["Story + direction", "Visual quality + consistency", "Sound", "Pipeline + automation",
        "Infrastructure + cost", "Rights + disclosure", "Write-up + evidence"]
WRITEUP_SECTIONS = ["brief", "pipeline", "model choice", "cost", "human time", "problems", "rights", "change"]


def srt_cues(path):
    txt = Path(path).read_text(encoding="utf-8-sig")
    times = re.findall(r"(\d\d:\d\d:\d\d,\d\d\d) --> (\d\d:\d\d:\d\d,\d\d\d)", txt)
    return len(times)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("delivery")
    ap.add_argument("--allow-test-cert", action="store_true", help="accept the c2patool sample certificate (practice only)")
    ap.add_argument("--json")
    a = ap.parse_args(argv)
    root = Path(a.delivery).resolve().parent
    d = json.loads(Path(a.delivery).read_text())
    findings = []  # (rubric row, ok, message)

    def add(row, ok, msg):
        findings.append({"row": row, "ok": bool(ok), "msg": msg})

    for p in d.get("plan", []):
        add("Pipeline + automation", (root / p).exists(), f"plan part {p}")

    for item in d.get("files", []):
        f = root / item["file"]
        if not f.exists():
            add("Visual quality + consistency", False, f"{item['file']}: missing")
            continue
        if item.get("spec"):
            res = spec_check.check(str(f), json.loads((root / item["spec"]).read_text()))
            bad = [r for r in res if not r["ok"]]
            for r in res:
                row = "Sound" if r["check"] in ("integrated loudness", "true peak", "audio sample rate",
                                                "audio channels", "audio codec") else "Visual quality + consistency"
                if not r["ok"]:
                    add(row, False, f"{item['file']}: {r['check']} found {r['found']}, want {r['want']}")
            add("Visual quality + consistency", not bad, f"{item['file']}: {len(res) - len(bad)}/{len(res)} spec checks")
        if item.get("signed"):
            try:
                import provenance
                v = provenance.verify_state(f)
                ok = v["state"] in ("Valid", "Trusted")
                if "signingCredential.untrusted" in v.get("codes", []) and not a.allow_test_cert:
                    ok = False
                    v["state"] += " (test certificate)"
                add("Rights + disclosure", ok, f"{item['file']}: content credentials {v['state']}, source {v.get('ai_source')}")
            except SystemExit as e:  # c2patool not installed
                add("Rights + disclosure", False, f"{item['file']}: cannot verify ({e})")

    for c in d.get("captions", []):
        p = root / c
        n = srt_cues(p) if p.exists() else 0
        add("Sound", n > 0, f"captions {c}: {n} cues" if p.exists() else f"captions {c}: missing")
    for s in d.get("stems", []):
        add("Sound", (root / s).exists(), f"stem {s}")
    for lg in d.get("logs", []):
        p = root / lg
        n = sum(1 for line in p.open() if line.strip()) if p.exists() else 0
        add("Rights + disclosure", n > 0, f"log {lg}: {n} lines" if p.exists() else f"log {lg}: missing")

    w = root / d.get("writeup", "writeup.md")
    if w.exists():
        heads = " ".join(h.lower() for h in re.findall(r"^#+\s*(.+)$", w.read_text(), re.M))
        words = len(w.read_text().split())
        missing = [s for s in WRITEUP_SECTIONS if s not in heads]
        add("Write-up + evidence", not missing, f"write-up: {words} words; missing sections: {missing or 'none'}")
        numbers = len(re.findall(r"(?:US\$|\$|€)\s?\d[\d,.]*|\d+(?:[.,]\d+)?\s*(?:%|s\b|h\b|kWh|LUFS)", w.read_text()))
        add("Write-up + evidence", numbers >= 10, f"write-up: {numbers} measured values (want 10 or more)")
    else:
        add("Write-up + evidence", False, "write-up missing")

    r = root / d.get("rubric", "rubric_scores.json")
    if r.exists():
        sc = json.loads(r.read_text())
        for who in ("self", "peer"):
            got = sc.get(who, {})
            add("Write-up + evidence", all(k in got for k in ROWS), f"rubric scores ({who}): {len(got)}/{len(ROWS)} rows")
        add("Write-up + evidence", len(sc.get("improvements", [])) >= 3, f"improvements: {len(sc.get('improvements', []))} (want 3)")
    else:
        add("Write-up + evidence", False, "rubric scores missing")

    fails = [f for f in findings if not f["ok"]]
    for row in ROWS:
        fr = [f for f in findings if f["row"] == row]
        if not fr:
            continue
        print(f"{row}")
        for f in fr:
            print(f"  {'ok  ' if f['ok'] else 'FAIL'} {f['msg']}")
    print(f"\n{len(findings) - len(fails)}/{len(findings)} checks pass -> {'READY' if not fails else 'NOT READY'}")
    if a.json:
        Path(a.json).write_text(json.dumps(findings, indent=2))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
