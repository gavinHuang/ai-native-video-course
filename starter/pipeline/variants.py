#!/usr/bin/env python3
"""Render data-driven video variants from one template (C15·M01). Needs ffmpeg, Pillow.

  python variants.py template.json variants.csv --out variants/ [--dry-run]

template.json: the fixed structure; {placeholders} refer to CSV columns.
  {"size": [1080, 1920], "fps": 24,
   "segments": [
     {"clip": "shots/hook_{hook_type}_{product_id}.mp4", "dur": 2.0},
     {"clip": "shots/product_{product_id}.mp4", "dur": 3.0, "text": "{offer_text}"},
     {"clip": "shots/endcard.mp4", "dur": 2.0, "text": "{cta}"}],
   "audio": {"voice": "vo/{language}_{variant_id}.wav", "music": "music/bed.wav", "music_db": -18},
   "text_limits": {"offer_text": 32, "cta": 20}}
variants.csv: variant_id,product_id,hook_type,language,offer_text,cta,...

For every row: check the row (required columns, text limits, input files), render the segments at the
template size and rate, burn the text inside the safe zone, mix voice over music, and write a manifest line.
Outputs are cached by a hash of all inputs: a re-run renders only changed rows (no paying or waiting twice).
The A/B rule: a test set must change ONE column; the script reports which columns vary.
"""
import argparse
import csv
import hashlib
import json
import string
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tools"))


def fields(s):
    return [f for _, f, _, _ in string.Formatter().parse(s) if f]


def fill(s, row):
    return s.format(**row) if s else s


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr[-500:])


def text_png(text, w, h, path):
    from captions import font
    from PIL import Image, ImageDraw
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    size = int(h * 0.045)
    f = font(size)
    while d.textlength(text, font=f) > w * 0.8 and size > 14:
        size = int(size * 0.9)
        f = font(size)
    tw = d.textlength(text, font=f)
    y = int(h * 0.62)  # inside the default safe zone (top 14 %, bottom 22 %)
    d.text(((w - tw) / 2, y), text, font=f, fill="white", stroke_width=max(2, size // 12), stroke_fill="black")
    im.save(path)


def check_row(row, tpl, base):
    problems = []
    needed = set()
    for seg in tpl["segments"]:
        needed |= set(fields(seg["clip"])) | set(fields(seg.get("text", "")))
    for v in tpl.get("audio", {}).values():
        if isinstance(v, str):
            needed |= set(fields(v))
    for col in sorted(needed - row.keys()):
        problems.append(f"missing column {col}")
    for col, lim in tpl.get("text_limits", {}).items():
        if len(row.get(col, "")) > lim:
            problems.append(f"{col} is {len(row[col])} characters (limit {lim}): '{row[col]}'")
    if problems:
        return problems
    for seg in tpl["segments"]:
        p = base / fill(seg["clip"], row)
        if not p.exists():
            problems.append(f"missing clip {p}")
    for k in ("voice", "music"):
        v = tpl.get("audio", {}).get(k)
        if v and not (base / fill(v, row)).exists():
            problems.append(f"missing {k} {fill(v, row)}")
    return problems


def render(row, tpl, base, out):
    W, H = tpl["size"]
    fps = tpl.get("fps", 24)
    tmp = Path(tempfile.mkdtemp(prefix="var_"))
    parts = []
    for i, seg in enumerate(tpl["segments"]):
        src = base / fill(seg["clip"], row)
        part = tmp / f"p{i}.mp4"
        vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={fps},setsar=1"
        cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(src)]
        if seg.get("text"):
            png = tmp / f"t{i}.png"
            text_png(fill(seg["text"], row), W, H, png)
            cmd += ["-i", str(png), "-filter_complex", f"[0:v]{vf}[v];[v][1:v]overlay=0:0[o]", "-map", "[o]"]
        else:
            cmd += ["-vf", vf]
        run(cmd + ["-t", str(seg["dur"]), "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", str(part)])
        parts.append(part)
    lst = tmp / "l.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    pic = tmp / "pic.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(pic)])
    total = sum(s["dur"] for s in tpl["segments"])
    au = tpl.get("audio", {})
    ins, fc = [], []
    if au.get("music"):
        ins += ["-i", str(base / fill(au["music"], row))]
        fc.append(f"[{len(ins)//2}:a]volume={au.get('music_db', -18)}dB,aformat=channel_layouts=stereo[m]")
    if au.get("voice"):
        ins += ["-i", str(base / fill(au["voice"], row))]
        fc.append(f"[{len(ins)//2}:a]aformat=channel_layouts=stereo,adelay={int(au.get('voice_at', 0.3)*1000)}|{int(au.get('voice_at', 0.3)*1000)}[vo]")
    labels = "".join(x for x, k in (("[m]", "music"), ("[vo]", "voice")) if au.get(k))
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(pic), *ins]
    if labels:
        fc.append(f"{labels}amix=inputs={labels.count('[')}:normalize=0,apad,atrim=0:{total}[a]")
        cmd += ["-filter_complex", ";".join(fc), "-map", "0:v", "-map", "[a]", "-c:a", "aac", "-ar", "48000"]
    run(cmd + ["-c:v", "copy", "-t", str(total), str(out)])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("template")
    ap.add_argument("csv")
    ap.add_argument("--out", default="variants")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    tpl = json.loads(Path(a.template).read_text())
    base = Path(a.template).resolve().parent
    rows = list(csv.DictReader(open(a.csv)))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    cols = [c for c in rows[0] if c != "variant_id"] if rows else []
    varying = [c for c in cols if len({r[c] for r in rows}) > 1]
    print(f"{len(rows)} variants; columns that vary: {', '.join(varying) or 'none'}")
    if len(varying) > 1:
        print("note: for an A/B test, change one column per test set; this set is a matrix, not a clean A/B test")
    manifest, bad, rendered, cached = [], 0, 0, 0
    for row in rows:
        probs = check_row(row, tpl, base)
        if probs:
            bad += 1
            for p in probs:
                print(f"PROBLEM {row.get('variant_id')}: {p}")
            continue
        h = hashlib.sha256(json.dumps([tpl, row], sort_keys=True).encode())
        for seg in tpl["segments"]:
            h.update((base / fill(seg["clip"], row)).read_bytes()[:1 << 20])
        key = h.hexdigest()[:12]
        f = out / f"{row['variant_id']}_{key}.mp4"
        if f.exists():
            cached += 1
        elif not a.dry_run:
            render(row, tpl, base, f)
            rendered += 1
        manifest.append({"variant_id": row["variant_id"], "file": str(f), "hash": key, **row})
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    print(f"rendered {rendered}, from cache {cached}, rejected {bad}; manifest: {out / 'manifest.json'}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
