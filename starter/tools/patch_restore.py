#!/usr/bin/env python3
"""Put exact pixels from the source back onto an edited clip: a tracked, feathered patch (C09·M03, C05·M05).

Use case: an AI relight or restyle made the logo soft or changed small text. The rest of the edit is good.
Take the logo area from the source, follow it through the shot, and composite it onto the edit.

  python patch_restore.py --src source.mp4 --edit edited.mp4 --box 300,380,420,500 --out fixed.mp4 [--feather 8] [--grade]

--box     x0,y0,x1,y1 of the area in the FIRST frame (source pixels)
--track   follow the area through the shot by template matching (default on; use --no-track for a locked shot)
--grade   match the patch's mean color to the edit around it (so a relit edit and an unrelit patch blend)
The report gives the track path and the remaining difference between the patch area and the source.
Needs ffmpeg, numpy, opencv-python. Both clips must have the same size and frame count.
"""
import argparse
import json
import subprocess
import sys

import numpy as np


def info(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate",
                          "-of", "json", path], capture_output=True, text=True, check=True).stdout
    s = json.loads(out)["streams"][0]
    num, den = map(int, s["r_frame_rate"].split("/"))
    return int(s["width"]), int(s["height"]), num / den


def reader(path, W, H):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
    while True:
        b = p.stdout.read(W * H * 3)
        if len(b) < W * H * 3:
            break
        yield np.frombuffer(b, np.uint8).reshape(H, W, 3)
    p.wait()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", required=True)
    ap.add_argument("--edit", required=True)
    ap.add_argument("--box", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--feather", type=int, default=8)
    ap.add_argument("--no-track", action="store_true")
    ap.add_argument("--grade", action="store_true")
    ap.add_argument("--search", type=int, default=24, help="max movement per frame in pixels for the tracker")
    a = ap.parse_args()
    import cv2
    W, H, fps = info(a.src)
    if info(a.edit)[:2] != (W, H):
        sys.exit("the two clips must have the same size")
    x0, y0, x1, y1 = map(int, a.box.split(","))
    bw, bh = x1 - x0, y1 - y0
    mask = np.zeros((bh, bw), np.float32)
    f = max(1, a.feather)
    mask[f:-f, f:-f] = 1.0
    mask = cv2.GaussianBlur(mask, (0, 0), f / 2)[..., None]
    out = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(fps),
                            "-i", "-", "-i", a.edit, "-map", "0:v", "-map", "1:a?", "-c:v", "libx264", "-crf", "16",
                            "-pix_fmt", "yuv420p", "-c:a", "copy", a.out], stdin=subprocess.PIPE)
    tmpl, path, residual = None, [], []
    x, y = x0, y0
    for s_img, e_img in zip(reader(a.src, W, H), reader(a.edit, W, H)):
        if tmpl is None:
            tmpl = s_img[y0:y1, x0:x1].copy()
        elif not a.no_track:
            sx0, sy0 = max(0, x - a.search), max(0, y - a.search)
            sx1, sy1 = min(W, x + bw + a.search), min(H, y + bh + a.search)
            res = cv2.matchTemplate(s_img[sy0:sy1, sx0:sx1], tmpl, cv2.TM_CCOEFF_NORMED)
            _, score, _, (mx, my) = cv2.minMaxLoc(res)
            x, y = sx0 + mx, sy0 + my
            tmpl = s_img[y:y + bh, x:x + bw].copy()  # update: follows slow changes in scale and light
        path.append([x, y])
        patch = s_img[y:y + bh, x:x + bw].astype(np.float32)
        frame = e_img.copy()
        region = frame[y:y + bh, x:x + bw].astype(np.float32)
        if a.grade:
            ring = mask < 0.5
            ring = ring[..., 0]
            if ring.any():
                patch = patch + (region[ring].mean(0) - patch[ring].mean(0))
        frame[y:y + bh, x:x + bw] = np.clip(patch * mask + region * (1 - mask), 0, 255).astype(np.uint8)
        inner = (slice(y + f, y + bh - f), slice(x + f, x + bw - f))
        residual.append(float(np.abs(frame[inner].astype(np.int16) - s_img[inner].astype(np.int16)).mean()))
        out.stdin.write(frame.tobytes())
    out.stdin.close()
    out.wait()
    moves = [abs(p[0] - q[0]) + abs(p[1] - q[1]) for p, q in zip(path[1:], path[:-1])]
    print(json.dumps({"out": a.out, "frames": len(path), "box_first": path[0] if path else None,
                      "box_last": path[-1] if path else None, "max_step_px": max(moves) if moves else 0,
                      "patch_vs_source_mean_diff": round(float(np.mean(residual)), 2) if residual else None,
                      "graded": a.grade}, indent=2))


if __name__ == "__main__":
    main()
