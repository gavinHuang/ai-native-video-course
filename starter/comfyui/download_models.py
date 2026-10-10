#!/usr/bin/env python3
"""Download the model files that a starter workflow needs, and check each SHA-256 hash.

Usage:
  python download_models.py --comfy /opt/ComfyUI 03_i2v_wan22_5b          # one workflow
  python download_models.py --comfy /opt/ComfyUI 01_t2i_flux2_klein_4b 03_i2v_wan22_5b
  python download_models.py --list                                        # sizes and licenses only

The file list, URLs, hashes, and licenses come from models.lock.json (checked 2026-10-04).
Read the license column before you use an output in client work (C16·M01).
Some repositories need a Hugging Face login: set HF_TOKEN in the environment.
"""
import argparse
import hashlib
import json
import os
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha256(path, chunk=16 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                return h.hexdigest()
            h.update(b)


def download(url, dest, expected_bytes):
    tmp = dest.with_suffix(dest.suffix + ".part")
    headers = {}
    if os.environ.get("HF_TOKEN"):
        headers["Authorization"] = f"Bearer {os.environ['HF_TOKEN']}"
    have = tmp.stat().st_size if tmp.exists() else 0
    if have:
        headers["Range"] = f"bytes={have}-"  # resume a broken download
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as r, open(tmp, "ab" if have else "wb") as f:
        if have and r.status != 206:
            f.truncate(0)
            have = 0
        done = have
        while True:
            b = r.read(8 << 20)
            if not b:
                break
            f.write(b)
            done += len(b)
            print(f"\r  {done / 1e9:6.2f} / {expected_bytes / 1e9:.2f} GB", end="", file=sys.stderr)
    print(file=sys.stderr)
    tmp.rename(dest)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("workflows", nargs="*")
    ap.add_argument("--comfy", help="ComfyUI folder (models are saved under <comfy>/models/<directory>)")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    lock = json.loads((HERE / "models.lock.json").read_text())
    index = json.loads((HERE / "workflows" / "index.json").read_text())
    by_wf = {i["workflow"]: i for i in index}
    if a.list or not a.workflows:
        for i in index:
            print(f"{i['workflow']:28} {i['download_gb']:6.1f} GB  {i['note']}")
            for m in i["models"]:
                print(f"    {m:60} {lock[m]['bytes'] / 1e9:6.2f} GB  {lock[m]['license']}")
        return
    if not a.comfy:
        sys.exit("--comfy is required")
    names = []
    for w in a.workflows:
        if w not in by_wf:
            sys.exit(f"unknown workflow {w}. Use --list.")
        names += [m for m in by_wf[w]["models"] if m not in names]
    for m in names:
        info = lock[m]
        dest = Path(a.comfy) / "models" / info["directory"] / m
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and dest.stat().st_size == info["bytes"]:
            print(f"have {m} (checking hash)", file=sys.stderr)
        else:
            if info.get("gated") and not os.environ.get("HF_TOKEN"):
                sys.exit(f"{m} is in a gated repository. Accept the license on Hugging Face, then set HF_TOKEN.")
            print(f"get  {m}  [{info['license']}]", file=sys.stderr)
            download(info["url"], dest, info["bytes"])
        if dest.stat().st_size != info["bytes"]:
            sys.exit(f"SIZE MISMATCH for {m}: got {dest.stat().st_size} bytes, expected {info['bytes']}.")
        digest = sha256(dest)
        if not info.get("sha256"):
            print(f"ok   {m}  (no published hash; record yours in models.lock.json: {digest})", file=sys.stderr)
        elif digest != info["sha256"]:
            sys.exit(f"HASH MISMATCH for {m}: got {digest}, expected {info['sha256']}. Delete the file and retry.")
        else:
            print(f"ok   {m}", file=sys.stderr)


if __name__ == "__main__":
    main()
