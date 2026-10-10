#!/usr/bin/env python3
"""Make 2–4 key-frame options per shot from a shot list (C04·M04 reference solution).

  python storyboard.py shots.json --refs refs/ --look look.json --out storyboard/ --options 3 [--dry-run]

It builds each prompt from four sources, always in the same order (C04·M01):
  shot fields (size, angle, lens, action, place, light)  +  descriptors from refs/<ID>/sheet.json
  +  the look suffix from look.json  +  the format (aspect ratio)
Then it calls the open backend: the C11 starter workflow 02 (two references) through the ComfyUI API.
Each option is logged with promptlog.py (model, prompt, seed, refs, file).

shots.json:  [{"id": "S07", "size": "MCU", "angle": "eye level", "lens": "85 mm look",
               "subject": ["CHAR-MARA"], "place": "LOC-LOCKER", "action": "She reads a small printed photo.",
               "light": "cold fluorescent top light, warm practical lamp from frame left", "dur": 4}]
look.json:   {"suffix": "muted teal and amber palette, 35 mm film grain, soft halation, deep blacks",
              "aspect": "9:16", "do_not": ["lens flares", "pure white backgrounds"]}

Output: <out>/<shot>_<a|b|c>.png, <shot>.prompt.txt, plan.json, and review.csv (one row per option, with the
look-bible do-not rules as check columns).
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STARTER = HERE.parent.parent
sys.path.insert(0, str(STARTER / "tools"))
import promptlog  # noqa: E402

SIZES = {"ECU": "extreme close-up", "CU": "close-up", "MCU": "medium close-up", "MS": "medium shot",
         "MWS": "medium wide shot", "WS": "wide shot", "EWS": "extreme wide shot"}
WF = STARTER / "comfyui" / "workflows" / "02_ref_edit_flux2_klein_4b"
CLIENT = STARTER / "solutions" / "C11-M04" / "comfy_run.py"


def sheet(refs, rid):
    p = Path(refs) / rid / "sheet.json"
    if not p.exists():
        sys.exit(f"reference {rid} not found: {p}")
    return json.loads(p.read_text())


def first_view(refs, s):
    views = s.get("views", {})
    key = "front" if "front" in views else ("wide" if "wide" in views else next(iter(views)))
    return str(Path(refs) / s["id"] / views[key])


def build_prompt(shot, refs, look):
    subjects = [sheet(refs, r) for r in shot.get("subject", [])]
    place = sheet(refs, shot["place"]) if shot.get("place") else None
    roles = []
    if subjects:
        roles.append("Image 1 is the character; keep the face, hair, and clothes exactly.")
    if place:
        roles.append(f"Image {2 if subjects else 1} is the place; keep its layout. Do not copy people from it.")
    parts = [
        f"{SIZES.get(shot.get('size'), shot.get('size', ''))}, {shot.get('angle', 'eye level')}, {shot.get('lens', '')}".strip(", "),
        " ".join(s["descriptor"] for s in subjects),
        shot.get("action", ""),
        place["descriptor"] if place else "",
        shot.get("light", ""),
        look.get("suffix", ""),
    ]
    # Do-not rules are NOT written into the prompt: "avoid lens flares" often adds lens flares, because the
    # model reads the words "lens flares". They go into the review sheet (review.csv) as checks instead.
    parts = [p.strip().rstrip(".") for p in parts if p and p.strip()]
    text = " ".join(roles) + " " + ". ".join(p[0].upper() + p[1:] for p in parts) + "."
    ref_files = ([first_view(refs, subjects[0])] if subjects else []) + ([first_view(refs, place)] if place else [])
    ref_ids = [s["id"] for s in subjects] + ([place["id"]] if place else [])
    return text.strip(), ref_files, ref_ids


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("shots")
    ap.add_argument("--refs", default="refs")
    ap.add_argument("--look", required=True)
    ap.add_argument("--out", default="storyboard")
    ap.add_argument("--options", type=int, default=3)
    ap.add_argument("--server", default="http://127.0.0.1:8188")
    ap.add_argument("--seed", type=int, default=1000)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    shots = json.loads(Path(a.shots).read_text())
    look = json.loads(Path(a.look).read_text())
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    plan = []
    for shot in shots:
        prompt, ref_files, ref_ids = build_prompt(shot, a.refs, look)
        if len(ref_files) < 2:
            ref_files = ref_files + ref_files[:1]  # the starter graph needs two images
        (out / f"{shot['id']}.prompt.txt").write_text(prompt + "\n")
        for k in range(a.options):
            opt = "abcd"[k]
            seed = a.seed + 10 * int("".join(ch for ch in shot["id"] if ch.isdigit()) or 0) + k
            job = {"id": f"{shot['id']}_{opt}", "seed": seed, "prompt": prompt, "refs": ref_ids, "files": ref_files}
            plan.append(job)
            if a.dry_run:
                continue
            cmd = [sys.executable, str(CLIENT), "--server", a.server, "--workflow", f"{WF}.json",
                   "--map", f"{WF}.map.json", "--set", f"prompt={prompt}", "--set", f"seed={seed}",
                   "--set", f"filename_prefix=storyboard/{job['id']}", "--upload", f"ref_image_1={ref_files[0]}",
                   "--upload", f"ref_image_2={ref_files[1]}", "--out", str(out), "--log", str(out / "runs.jsonl")]
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode != 0:
                print(f"{job['id']}: failed\n{r.stderr[-800:]}", file=sys.stderr)
                continue
            produced = json.loads(r.stdout)["outputs"][0]
            final = out / f"{job['id']}.png"
            Path(produced).rename(final)
            promptlog.add_entry(id=job["id"], model="flux-2-klein-4b-fp8 (C11 workflow 02)", prompt=prompt,
                                seed=seed, refs=ref_ids, file=str(final), cost_usd=0.0)
            print(f"{job['id']}: {final}")
    (out / "plan.json").write_text(json.dumps(plan, indent=2))
    # Review sheet: one row per option; the do-not rules from the look bible become columns to check.
    checks = [f"no {d}" for d in look.get("do_not", [])]
    rows = ["shot,option,file,story,continuity,identity,look_bible," + ",".join(checks) + ",decision,note"]
    rows += [f"{j['id'].rsplit('_', 1)[0]},{j['id'].rsplit('_', 1)[1]},{j['id']}.png,,,,," + "," * len(checks) + ","
             for j in plan]
    (out / "review.csv").write_text("\n".join(rows) + "\n")
    if a.dry_run:
        for j in plan:
            print(f"{j['id']}  seed {j['seed']}  refs {','.join(j['refs'])}")
        print(f"\nPrompt for {plan[0]['id']}:\n{plan[0]['prompt']}" if plan else "no shots")


if __name__ == "__main__":
    main()
