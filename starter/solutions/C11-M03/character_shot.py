#!/usr/bin/env python3
"""Make one dialogue shot of a character: start frame -> lip-synced video -> identity check.

Reference solution for C11·M03. It chains three starter workflows through the ComfyUI API:
  1. 02_ref_edit_flux2_klein_4b   character ref + place ref + shot prompt -> start frame (PNG)
  2. 07_lipsync_ia2v_ltx23        start frame + line audio + action prompt -> video with lip sync
  3. identity_score.py            video vs character refs -> PASS / REJECT
On REJECT it tries the next seed, up to --tries times.

Usage:
  python character_shot.py --shot shots/S07.json --char-ref refs/CHAR-MARA_front.png \
      --place-ref refs/LOC-LOCKER.png --line audio/S07_mara.wav --out shots/S07/
  python character_shot.py ... --dry-run      # print the plan, run nothing

shots/S07.json example:
  {"id": "S07", "frame_prompt": "Medium close-up of the woman from image 1 in the place from image 2 ...",
   "action_prompt": "She looks up from the photo, surprised, and says the line quietly.",
   "duration_s": 4, "seed": 1000}
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STARTER = HERE.parent.parent
WF = STARTER / "comfyui" / "workflows"
CLIENT = HERE.parent / "C11-M04" / "comfy_run.py"
SCORER = STARTER / "tools" / "identity_score.py"


def comfy(args, workflow, sets, uploads, out, log, dry):
    cmd = [sys.executable, str(CLIENT), "--server", args.server, "--workflow", str(WF / f"{workflow}.json"),
           "--map", str(WF / f"{workflow}.map.json"), "--out", str(out), "--log", str(log)]
    for k, v in sets.items():
        cmd += ["--set", f"{k}={v}"]
    for k, v in uploads.items():
        cmd += ["--upload", f"{k}={v}"]
    print("$", " ".join(cmd[1:]), file=sys.stderr)
    if dry:
        return [str(out / f"{workflow}_DRYRUN")]
    res = subprocess.run(cmd, capture_output=True, text=True)
    sys.stderr.write(res.stderr)
    if res.returncode != 0:
        sys.exit(f"stage {workflow} failed (exit {res.returncode})")
    return json.loads(res.stdout)["outputs"]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--shot", required=True)
    ap.add_argument("--char-ref", required=True, action="append", help="first one goes to the start-frame graph")
    ap.add_argument("--place-ref", required=True)
    ap.add_argument("--line", required=True, help="audio file of the spoken line (C06·M01)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--server", default="http://127.0.0.1:8188")
    ap.add_argument("--threshold", type=float, default=0.45)
    ap.add_argument("--tries", type=int, default=3)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    shot = json.loads(Path(a.shot).read_text())
    for p in a.char_ref + [a.place_ref, a.line]:
        if not Path(p).is_file():
            sys.exit(f"missing input file: {p}")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    log = out / "runs.jsonl"
    report = {"shot": shot["id"], "tries": []}

    for t in range(a.tries):
        seed = shot.get("seed", 0) + t
        frames = comfy(a, "02_ref_edit_flux2_klein_4b",
                       {"prompt": shot["frame_prompt"], "seed": seed},
                       {"ref_image_1": a.char_ref[0], "ref_image_2": a.place_ref}, out / "frames", log, a.dry_run)
        start = frames[0]
        video = comfy(a, "07_lipsync_ia2v_ltx23",
                      {"prompt": shot["action_prompt"], "seed": seed, "duration_s": shot.get("duration_s", 4)},
                      {"start_image": start, "line_audio": a.line}, out / "video", log, a.dry_run)[0]
        if a.dry_run:
            print(f"$ identity_score.py --ref ... {video}", file=sys.stderr)
            break
        score_file = out / f"identity_try{t + 1}.json"
        res = subprocess.run([sys.executable, str(SCORER), *sum([["--ref", r] for r in a.char_ref], []),
                              "--threshold", str(a.threshold), "--json", str(score_file), video],
                             capture_output=True, text=True)
        print(res.stdout.strip(), file=sys.stderr)
        row = json.loads(score_file.read_text())["clips"][0]
        report["tries"].append({"seed": seed, "start_frame": start, "video": video, **row})
        if row["result"] == "PASS":
            report["chosen"] = video
            break
    (out / "report.json").write_text(json.dumps(report, indent=2))
    if not a.dry_run and "chosen" not in report:
        sys.exit(f"no take passed after {a.tries} tries; see {out / 'report.json'}")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
