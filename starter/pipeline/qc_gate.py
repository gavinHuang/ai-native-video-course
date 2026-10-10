#!/usr/bin/env python3
"""Automated quality gates for a multi-agent pipeline (C12·M04).

A gate takes one item (a clip, a timeline, a deliverable) and returns PASS, FIX, or REJECT with reasons.
The orchestrator (code, not an LLM) moves the item on, sends it back with the reasons, or queues it for a person.

  python qc_gate.py --stage shot  --item S07_t04.mp4 --refs refs/CHAR-MARA/01_front.png refs/CHAR-MARA/02_34.png
  python qc_gate.py --stage delivery --item film_web.mp4 --spec web_1080p
  python qc_gate.py --stage shot --item S07_t04.mp4 --refs ... --json gate.json      # machine-readable result

Gates by stage (edit GATES below for your project):
  shot     : tech (fps, size, no black/frozen frames), identity (face vs refs), length
  delivery : full delivery spec (format, color tags, loudness, true peak, black/frozen frames)
Each check is FIX (a cheap automatic or small manual fix exists) or REJECT (regenerate) when it fails.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOLS = HERE.parent / "tools"
SPECS = HERE.parent / "specs"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(TOOLS))

GATES = {
    "shot": {"fps": [24], "min_s": 1.0, "max_black_s": 0.3, "max_freeze_s": 0.75, "identity_min": 0.45},
    "delivery": {},
}


def shot_gate(item, refs, cfg):
    import mediakit
    import spec_check
    res = []
    info = mediakit.probe(item)
    ok_fps = any(abs(info.get("fps", 0) - f) < 0.01 for f in cfg["fps"])
    res.append({"check": "frame rate", "ok": ok_fps, "found": info.get("fps"), "on_fail": "FIX",
                "fix": "conform with frame interpolation (C09·M04)"})
    res.append({"check": "length", "ok": info["duration"] >= cfg["min_s"], "found": round(info["duration"], 2), "on_fail": "REJECT",
                "fix": "too short to use; regenerate"})
    blacks, freezes = spec_check.black_and_freeze(item, cfg["max_black_s"], cfg["max_freeze_s"])
    res.append({"check": "black frames", "ok": not blacks, "found": blacks, "on_fail": "FIX", "fix": "trim the black frames"})
    res.append({"check": "frozen picture", "ok": not freezes, "found": freezes, "on_fail": "FIX",
                "fix": "trim the frozen part (often the end of a generated clip)"})
    if refs:
        import tempfile
        tmp = Path(tempfile.mkdtemp(prefix="gate_")) / "id.json"
        subprocess.run([sys.executable, str(TOOLS / "identity_score.py"), *sum([["--ref", x] for x in refs], []),
                        "--threshold", str(cfg["identity_min"]), "--json", str(tmp), item], capture_output=True, text=True)
        try:
            rep = json.loads(tmp.read_text())["clips"][0]
            res.append({"check": "identity", "ok": rep["result"] == "PASS", "found": rep["median"], "on_fail": "REJECT",
                        "fix": f"identity below {cfg['identity_min']} (worst frame {rep['worst_frame']}); regenerate with stronger references"})
        except (ValueError, KeyError, IndexError, FileNotFoundError):
            res.append({"check": "identity", "ok": False, "found": "no score", "on_fail": "REJECT", "fix": "no face found; check the shot"})
    return res


def delivery_gate(item, spec):
    import spec_check
    s = json.loads((SPECS / f"{spec}.json").read_text())
    return [{"check": r["check"], "ok": r["ok"], "found": r["found"], "on_fail": "FIX", "fix": r["fix"]}
            for r in spec_check.check(item, s)]


def decide(results):
    fails = [r for r in results if not r["ok"]]
    if not fails:
        return "PASS"
    return "REJECT" if any(r["on_fail"] == "REJECT" for r in fails) else "FIX"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", choices=sorted(GATES), required=True)
    ap.add_argument("--item", required=True)
    ap.add_argument("--refs", nargs="*")
    ap.add_argument("--spec", default="web_1080p")
    ap.add_argument("--json")
    a = ap.parse_args()
    res = shot_gate(a.item, a.refs, GATES["shot"]) if a.stage == "shot" else delivery_gate(a.item, a.spec)
    verdict = decide(res)
    out = {"item": a.item, "stage": a.stage, "verdict": verdict,
           "reasons": [{"check": r["check"], "found": r["found"], "fix": r["fix"]} for r in res if not r["ok"]]}
    print(json.dumps(out, indent=2, default=str))
    if a.json:
        Path(a.json).write_text(json.dumps(out, indent=2, default=str))
    sys.exit({"PASS": 0, "FIX": 1, "REJECT": 2}[verdict])


if __name__ == "__main__":
    main()
