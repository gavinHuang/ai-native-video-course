#!/usr/bin/env python3
"""Check a delivery file against a spec (C09·M04, C10·M02, C15·M03, C18). Needs ffmpeg and ffprobe.

  python spec_check.py film.mp4 --spec specs/web_1080p.json
  python spec_check.py *.mp4 --spec specs/reels_9x16.json --json report.json

A spec is a JSON file. Every key is optional; only the keys in the spec are checked:
  {"container": "mp4", "video_codec": ["h264", "hevc"], "width": 1920, "height": 1080,
   "fps": [23.976, 24, 25, 30], "pix_fmt": ["yuv420p"], "color": {"primaries": "bt709", "transfer": "bt709",
   "matrix": "bt709", "range": "tv"}, "max_duration_s": 180, "min_duration_s": 1,
   "max_video_mbps": 20, "audio_codec": ["aac"], "audio_rate": 48000, "audio_channels": 2,
   "loudness_lufs": -14, "loudness_tol": 1.0, "true_peak_max": -1.0, "max_black_s": 0.5, "max_freeze_s": 1.0}
Exit code 0 = all checks pass. The report says what to fix for each failure.
The specs in starter/specs/ are examples. Use the real spec of your client or platform.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", path],
                         capture_output=True, text=True)
    if out.returncode:
        sys.exit(f"ffprobe cannot read {path}")
    return json.loads(out.stdout)


def loudness(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-map", "0:a:0", "-af", "ebur128=peak=true",
                        "-f", "null", "-"], capture_output=True, text=True)
    txt = r.stderr
    i = re.findall(r"I:\s+(-?[\d.]+) LUFS", txt)
    tp = re.findall(r"Peak:\s+(-?[\d.]+|-inf) dBFS", txt)
    lra = re.findall(r"LRA:\s+(-?[\d.]+) LU", txt)
    return (float(i[-1]) if i else None, float(tp[-1]) if tp and tp[-1] != "-inf" else None,
            float(lra[-1]) if lra else None)


def black_and_freeze(path, black_d, freeze_d):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-an", "-vf",
                        f"blackdetect=d={black_d}:pix_th=0.10,freezedetect=n=0.003:d={freeze_d}", "-f", "null", "-"],
                       capture_output=True, text=True)
    blacks = [(float(a), float(b)) for a, b in re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", r.stderr)]
    fstarts = [float(x) for x in re.findall(r"freeze_start: ([\d.]+)", r.stderr)]
    fdurs = [float(x) for x in re.findall(r"freeze_duration: ([\d.]+)", r.stderr)]
    # A freeze that lasts to the end of the file has a start but no duration: compute it from the file length.
    if len(fstarts) > len(fdurs):
        total = float(probe(path)["format"].get("duration", 0))
        fdurs += [round(total - x, 3) for x in fstarts[len(fdurs):]]
    return blacks, [(st, d) for st, d in zip(fstarts, fdurs) if d >= freeze_d]


def fps_of(s):
    num, den = map(int, s.get("avg_frame_rate", "0/1").split("/"))
    return num / den if den else 0


def check(path, spec):
    info = probe(path)
    fmt = info["format"]
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    res = []

    def add(name, ok, found, want, fix=""):
        res.append({"check": name, "ok": bool(ok), "found": found, "want": want, "fix": "" if ok else fix})

    if "container" in spec:
        names = fmt.get("format_name", "")
        add("container", spec["container"] in names.split(",") or Path(path).suffix[1:] == spec["container"],
            names, spec["container"], "export to the right container (for example .mp4)")
    if v is None:
        add("video stream", False, "none", "present", "the file has no video")
        return res
    if "video_codec" in spec:
        add("video codec", v["codec_name"] in spec["video_codec"], v["codec_name"], spec["video_codec"], "re-encode with an allowed codec")
    for k in ("width", "height"):
        if k in spec:
            add(k, v[k] == spec[k], v[k], spec[k], "render at the delivery size (do not let the platform scale)")
    if "fps" in spec:
        f = fps_of(v)
        add("frame rate", any(abs(f - x) < 0.01 for x in spec["fps"]), round(f, 3), spec["fps"],
            "conform to an allowed frame rate (C09·M04)")
    if "pix_fmt" in spec:
        add("pixel format", v.get("pix_fmt") in spec["pix_fmt"], v.get("pix_fmt"), spec["pix_fmt"],
            "use -pix_fmt yuv420p for web delivery")
    col = spec.get("color", {})
    for key, field in (("primaries", "color_primaries"), ("transfer", "color_transfer"), ("matrix", "color_space"),
                       ("range", "color_range")):
        if key in col:
            got = v.get(field, "unknown")
            add(f"color {key}", got == col[key], got, col[key],
                "tag the file correctly at export (C09·M01); untagged files are shown with a guess")
    dur = float(fmt.get("duration", 0))
    if "max_duration_s" in spec:
        add("max duration", dur <= spec["max_duration_s"], round(dur, 2), spec["max_duration_s"], "cut it shorter")
    if "min_duration_s" in spec:
        add("min duration", dur >= spec["min_duration_s"], round(dur, 2), spec["min_duration_s"], "file too short")
    if "max_video_mbps" in spec and v.get("bit_rate"):
        mbps = int(v["bit_rate"]) / 1e6
        add("video bitrate", mbps <= spec["max_video_mbps"], round(mbps, 2), f"<= {spec['max_video_mbps']}",
            "lower the bitrate or raise CRF")
    if "max_black_s" in spec or "max_freeze_s" in spec:
        bd = max(0.04, spec.get("max_black_s", 0.5))
        fd = max(0.2, spec.get("max_freeze_s", 1.0))
        blacks, freezes = black_and_freeze(path, bd, fd)
        if "max_black_s" in spec:
            add("black frames", not blacks, [f"{x:.2f}-{y:.2f} s" for x, y in blacks] or "none", f"no black >= {bd} s",
                "trim or replace the black frames (a generated clip often ends on black)")
        if "max_freeze_s" in spec:
            add("frozen picture", not freezes, [f"{x:.2f} s for {d:.2f} s" for x, d in freezes] or "none", f"no freeze >= {fd} s",
                "a frozen frame: check the end of generated clips and failed renders")
    audio_keys = {"audio_codec", "audio_rate", "audio_channels", "loudness_lufs", "true_peak_max"}
    if audio_keys & spec.keys():
        if a is None:
            add("audio stream", False, "none", "present", "add the mix")
            return res
        if "audio_codec" in spec:
            add("audio codec", a["codec_name"] in spec["audio_codec"], a["codec_name"], spec["audio_codec"], "encode audio as AAC")
        if "audio_rate" in spec:
            add("audio sample rate", int(a["sample_rate"]) == spec["audio_rate"], int(a["sample_rate"]), spec["audio_rate"],
                "resample to 48 kHz")
        if "audio_channels" in spec:
            add("audio channels", a["channels"] == spec["audio_channels"], a["channels"], spec["audio_channels"], "export the right channel layout")
        if "loudness_lufs" in spec or "true_peak_max" in spec:
            I, TP, LRA = loudness(path)
            if "loudness_lufs" in spec:
                tol = spec.get("loudness_tol", 1.0)
                add("integrated loudness", I is not None and abs(I - spec["loudness_lufs"]) <= tol, I,
                    f"{spec['loudness_lufs']} ± {tol} LUFS", f"adjust the mix by {spec['loudness_lufs'] - (I or 0):+.1f} LU (C10·M02)")
            if "true_peak_max" in spec:
                add("true peak", TP is not None and TP <= spec["true_peak_max"], TP, f"<= {spec['true_peak_max']} dBTP",
                    "use a true-peak limiter at the end of the mix (C10·M02)")
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--spec", required=True)
    ap.add_argument("--json")
    a = ap.parse_args()
    spec = json.loads(Path(a.spec).read_text())
    report, fails = {}, 0
    for f in a.files:
        res = check(f, spec)
        report[f] = res
        bad = [r for r in res if not r["ok"]]
        fails += bool(bad)
        print(f"{'PASS' if not bad else 'FAIL'}  {f}  ({len(res) - len(bad)}/{len(res)} checks)")
        for r in bad:
            print(f"   - {r['check']}: found {r['found']}, want {r['want']}. Fix: {r['fix']}")
    if a.json:
        Path(a.json).write_text(json.dumps(report, indent=2))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
