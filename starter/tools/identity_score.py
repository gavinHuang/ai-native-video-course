#!/usr/bin/env python3
"""Score how well a generated video (or image) keeps the identity of a reference face.

Used in C05·M03 (drift) and C11·M03 (character pipeline). It uses two small open models from the OpenCV model zoo:
  - YuNet: face detection (MIT license)
  - SFace: face embedding, 128 numbers per face (Apache-2.0); compare two faces with cosine similarity

Usage:
  pip install opencv-python numpy
  python identity_score.py --ref CHAR-MARA_front.png --ref CHAR-MARA_34.png shot_S07_take3.mp4
  python identity_score.py --ref refs/*.png renders/*.mp4 --threshold 0.45 --json report.json

For each clip, the script samples frames, finds the largest face, and compares it with the mean
reference embedding. It reports median, minimum, and the share of frames with no face.
Decision rule (tune it on your own data): PASS if median >= threshold and face found in >= 80 % of frames.

SFace guidance from OpenCV: cosine >= 0.363 means "same person" on real photos. Generated faces
need your own threshold: score 20 clips that you judged by eye, then choose the value that separates them.
"""
import argparse
import json
import statistics
import sys
import urllib.request
from pathlib import Path

import cv2
import numpy as np

MODELS = {
    "face_detection_yunet_2023mar.onnx":
        "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx",
    "face_recognition_sface_2021dec.onnx":
        "https://github.com/opencv/opencv_zoo/raw/main/models/face_recognition_sface/face_recognition_sface_2021dec.onnx",
}
CACHE = Path.home() / ".cache" / "identity_score"
VIDEO_EXT = {".mp4", ".mov", ".webm", ".mkv", ".avi"}


def model_path(name):
    CACHE.mkdir(parents=True, exist_ok=True)
    p = CACHE / name
    if not p.exists():
        print(f"downloading {name}", file=sys.stderr)
        urllib.request.urlretrieve(MODELS[name], p)
    return str(p)


class FaceScorer:
    def __init__(self):
        self.det = cv2.FaceDetectorYN.create(model_path("face_detection_yunet_2023mar.onnx"), "", (320, 320), 0.8)
        self.rec = cv2.FaceRecognizerSF.create(model_path("face_recognition_sface_2021dec.onnx"), "")

    def embed(self, img):
        """Return the embedding of the largest face in a BGR image, or None."""
        h, w = img.shape[:2]
        self.det.setInputSize((w, h))
        _, faces = self.det.detect(img)
        if faces is None or len(faces) == 0:
            return None
        face = max(faces, key=lambda f: f[2] * f[3])  # largest box
        aligned = self.rec.alignCrop(img, face)
        feat = self.rec.feature(aligned)
        return feat / np.linalg.norm(feat)


def frames(path, samples):
    """Yield (frame index, BGR image) for evenly spaced frames."""
    if Path(path).suffix.lower() not in VIDEO_EXT:
        img = cv2.imread(str(path))
        if img is not None:
            yield 0, img
        return
    cap = cv2.VideoCapture(str(path))
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
    for i in sorted({int(k * (n - 1) / max(samples - 1, 1)) for k in range(samples)}):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ok, img = cap.read()
        if ok:
            yield i, img
    cap.release()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("clips", nargs="+")
    ap.add_argument("--ref", action="append", required=True, help="reference image of the character (repeat)")
    ap.add_argument("--samples", type=int, default=16, help="frames to sample per clip")
    ap.add_argument("--threshold", type=float, default=0.45)
    ap.add_argument("--min-face-rate", type=float, default=0.8)
    ap.add_argument("--json", help="write the report to this file")
    a = ap.parse_args()

    fs = FaceScorer()
    refs = []
    for r in a.ref:
        e = fs.embed(cv2.imread(r))
        if e is None:
            sys.exit(f"no face found in reference {r}")
        refs.append(e)
    ref = np.mean(refs, axis=0)
    ref /= np.linalg.norm(ref)

    report = []
    for clip in a.clips:
        scores, missing, worst = [], 0, None
        for idx, img in frames(clip, a.samples):
            e = fs.embed(img)
            if e is None:
                missing += 1
                continue
            s = float(np.dot(e.ravel(), ref.ravel()))
            scores.append(s)
            if worst is None or s < worst[1]:
                worst = (idx, s)
        total = len(scores) + missing
        face_rate = len(scores) / total if total else 0.0
        median = statistics.median(scores) if scores else 0.0
        ok = bool(scores) and median >= a.threshold and face_rate >= a.min_face_rate
        row = {"clip": clip, "median": round(median, 3), "min": round(min(scores), 3) if scores else None,
               "worst_frame": worst[0] if worst else None, "face_rate": round(face_rate, 2),
               "frames": total, "result": "PASS" if ok else "REJECT"}
        report.append(row)
        print(f"{row['result']:6} median {row['median']:.3f}  min {row['min']}  (frame {row['worst_frame']})  "
              f"faces {row['face_rate']:.0%}  {clip}")
    if a.json:
        Path(a.json).write_text(json.dumps({"threshold": a.threshold, "refs": a.ref, "clips": report}, indent=2))
    sys.exit(0 if all(r["result"] == "PASS" for r in report) else 1)


if __name__ == "__main__":
    main()
