#!/usr/bin/env python3
"""Reframe a horizontal clip to vertical (or square) by following the main face (C08·M04).

  python reframe.py in_16x9.mp4 --out out_9x16.mp4 --aspect 9:16 [--smooth 0.85] [--report reframe.json]

How it works: for each frame, find faces (OpenCV YuNet, as in identity_score.py), take the largest
face, and move a crop window of the target aspect ratio toward it. The movement is smoothed, so the crop
does not jump; the window stays inside the frame. Frames with no face keep the last position.

The report lists what an editor must check by hand:
  - two_faces_cut: frames with 2 or more faces where not all faces fit in the crop (two-shots);
  - face_outside: frames where the main face is partly outside the crop (fast moves);
  - max_speed_px_s: the fastest crop movement (a fast crop looks like a nervous camera operator).
For AI shots it is often better to generate the vertical version natively (C08·M04 Learn).
Needs ffmpeg, numpy, opencv-python.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,r_frame_rate", "-of", "json", path], capture_output=True, text=True, check=True).stdout
    s = json.loads(out)["streams"][0]
    num, den = map(int, s["r_frame_rate"].split("/"))
    return int(s["width"]), int(s["height"]), num / den


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("clip")
    ap.add_argument("--out", required=True)
    ap.add_argument("--aspect", default="9:16")
    ap.add_argument("--smooth", type=float, default=0.85, help="0 = follow at once, 0.95 = very slow")
    ap.add_argument("--report")
    a = ap.parse_args()
    import cv2
    from identity_score import model_path

    W, H, fps = probe(a.clip)
    aw, ah = map(int, a.aspect.split(":"))
    cw = int(round(H * aw / ah / 2) * 2) if aw / ah < W / H else W
    ch = H if aw / ah < W / H else int(round(W * ah / aw / 2) * 2)
    det = cv2.FaceDetectorYN.create(model_path("face_detection_yunet_2023mar.onnx"), "", (W, H), 0.7)
    reader = subprocess.Popen(["ffmpeg", "-v", "error", "-i", a.clip, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                              stdout=subprocess.PIPE)
    writer = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{cw}x{ch}",
                               "-r", str(fps), "-i", "-", "-i", a.clip, "-map", "0:v", "-map", "1:a?", "-c:v", "libx264",
                               "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "copy", "-shortest", a.out], stdin=subprocess.PIPE)
    cx, cy = W / 2, H / 2
    started = False  # the crop starts on the first face found, not at the center
    x0_prev = None
    n, two_cut, outside, speeds = 0, [], [], []
    while True:
        buf = reader.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            break
        img = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        _, faces = det.detect(img)
        if faces is not None and len(faces):
            faces = sorted(faces, key=lambda f: -f[2] * f[3])
            fx, fy, fw, fh = faces[0][:4]
            tx, ty = fx + fw / 2, fy + fh / 2
            if not started:
                cx, cy, started = tx, ty, True
            cx = a.smooth * cx + (1 - a.smooth) * tx
            cy = a.smooth * cy + (1 - a.smooth) * ty
        x0 = int(np.clip(cx - cw / 2, 0, W - cw))
        y0 = int(np.clip(cy - ch / 2, 0, H - ch))
        if faces is not None and len(faces):
            if len(faces) >= 2:
                xs = [f[0] for f in faces] + [f[0] + f[2] for f in faces]
                if min(xs) < x0 or max(xs) > x0 + cw:
                    two_cut.append(n)
            fx, fy, fw, fh = faces[0][:4]
            if fx < x0 or fx + fw > x0 + cw or fy < y0 or fy + fh > y0 + ch:
                outside.append(n)
        if x0_prev is not None:
            speeds.append(abs(x0 - x0_prev) * fps)
        x0_prev = x0
        writer.stdin.write(np.ascontiguousarray(img[y0:y0 + ch, x0:x0 + cw]).tobytes())
        n += 1
    writer.stdin.close()
    writer.wait()
    reader.wait()

    def spans(frames):
        out, start = [], None
        for i, f in enumerate(frames):
            if start is None:
                start = f
            if i + 1 == len(frames) or frames[i + 1] != f + 1:
                out.append([round(start / fps, 2), round(f / fps, 2)])
                start = None
        return out

    rep = {"in": a.clip, "out": a.out, "crop": [cw, ch], "frames": n,
           "two_faces_cut_s": spans(two_cut), "face_outside_s": spans(outside),
           "max_speed_px_s": round(max(speeds), 1) if speeds else 0.0}
    print(json.dumps(rep, indent=2))
    if a.report:
        Path(a.report).write_text(json.dumps(rep, indent=2))


if __name__ == "__main__":
    main()
