#!/usr/bin/env python3
"""Make an animatic from key frames and a shot list (C04·M04). Needs ffmpeg.

  python animatic.py shots.json --frames storyboard/ --out animatic.mp4 [--audio temp_mix.wav] [--size 1080x1920]

shots.json (the C03·M02 shot list; only these fields are used):
  [{"id": "S01", "dur": 3.0, "move": "push", "frame": "S01_b.png", "label": "Hook: ECU photo"}, ...]

  move:  push (slow zoom in) | pull (slow zoom out) | pan_left | pan_right | hold
  frame: optional; default <frames>/<id>_chosen.png, then the first <frames>/<id>_*.png
  label: optional; burned in at the bottom with the shot ID and duration, so reviewers can name shots

Each shot becomes a clip with a slow move. Clips are joined with hard cuts. The audio (temp voice,
music, effects) is mixed under the picture and cut to the picture length.
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

FPS = 24


def find_frame(shot, frames_dir):
    if shot.get("frame"):
        p = Path(frames_dir) / shot["frame"]
        return p if p.exists() else None
    for pat in (f"{shot['id']}_chosen.*", f"{shot['id']}_*.*", f"{shot['id']}.*"):
        hits = sorted(Path(frames_dir).glob(pat))
        if hits:
            return hits[0]
    return None


def move_filter(move, w, h, frames):
    # Render at 2x and use zoompan for smooth sub-pixel moves.
    W, H = w * 2, h * 2
    z_end = 1.12
    if move == "push":
        z = f"1+{(z_end - 1) / frames:.6f}*on"
        x, y = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    elif move == "pull":
        z = f"{z_end}-{(z_end - 1) / frames:.6f}*on"
        x, y = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    elif move in ("pan_left", "pan_right"):
        z = f"{z_end}"
        span = f"(iw-iw/zoom)"
        x = f"{span}*on/{frames}" if move == "pan_right" else f"{span}*(1-on/{frames})"
        y = "ih/2-(ih/zoom/2)"
    else:
        z, x, y = "1", "0", "0"
    return (f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
            f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={w}x{h}:fps={FPS}")


def label_png(text, w, h, path):
    """Draw the shot label as a transparent PNG (works with every ffmpeg build; drawtext is often missing)."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return None
    size = max(18, h // 45)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", size)
    except OSError:
        try:
            font = ImageFont.load_default(size=size)
        except TypeError:
            font = ImageFont.load_default()
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = d.textbbox((0, 0), text, font=font)
    pad = 10
    top = h - (y1 - y0) - 3 * pad
    d.rectangle([24 - pad, top - pad, 24 + (x1 - x0) + pad, top + (y1 - y0) + pad], fill=(0, 0, 0, 140))
    d.text((24, top - y0), text, font=font, fill=(255, 255, 255, 255))
    im.save(path)
    return path


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"ffmpeg failed:\n{' '.join(cmd)}\n{r.stderr[-2000:]}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("shots")
    ap.add_argument("--frames", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--audio")
    ap.add_argument("--size", default="1080x1920")
    ap.add_argument("--no-labels", action="store_true")
    a = ap.parse_args()
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg is not installed")
    w, h = map(int, a.size.split("x"))
    shots = json.loads(Path(a.shots).read_text())
    if isinstance(shots, dict):
        shots = shots.get("shots", [])
    tmp = Path(tempfile.mkdtemp(prefix="animatic_"))
    clips, total, missing = [], 0.0, []
    for i, s in enumerate(shots):
        dur = float(s.get("dur", 2.0))
        frames = max(1, round(dur * FPS))
        src = find_frame(s, a.frames)
        clip = tmp / f"{i:03d}.mp4"
        if src is None:
            missing.append(s["id"])
            inp = ["-f", "lavfi", "-i", f"color=c=0x202020:s={w}x{h}:r={FPS}:d={frames / FPS}"]
            vf = "null"
        else:
            inp = ["-loop", "1", "-i", str(src)]
            vf = move_filter(s.get("move", "hold"), w, h, frames)
        cmd = ["ffmpeg", "-loglevel", "error", "-y", *inp]
        lab = None
        if not a.no_labels:
            text = f"{s['id']}  {dur:.1f}s  {s.get('label', '')}" + ("  [NO FRAME]" if src is None else "")
            lab = label_png(text, w, h, tmp / f"{i:03d}_label.png")
            if lab is None:
                print("warning: install Pillow for shot labels", file=sys.stderr)
        if lab:
            cmd += ["-i", str(lab), "-filter_complex", f"[0:v]{vf}[v];[v][1:v]overlay=0:0[o]", "-map", "[o]"]
        else:
            cmd += ["-vf", vf]
        run(cmd + ["-frames:v", str(frames), "-r", str(FPS), "-pix_fmt", "yuv420p", "-c:v", "libx264",
                   "-crf", "20", str(clip)])
        clips.append(clip)
        total += frames / FPS
    lst = tmp / "list.txt"
    lst.write_text("".join(f"file '{c}'\n" for c in clips))
    picture = tmp / "picture.mp4"
    run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(picture)])
    if a.audio:
        run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(picture), "-i", a.audio, "-map", "0:v", "-map", "1:a",
             "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-af", f"apad,atrim=0:{total:.3f}", "-t", f"{total:.3f}", a.out])
    else:
        shutil.copy(picture, a.out)
    shutil.rmtree(tmp)
    print(json.dumps({"out": a.out, "shots": len(shots), "seconds": round(total, 2), "missing_frames": missing}))


if __name__ == "__main__":
    main()
