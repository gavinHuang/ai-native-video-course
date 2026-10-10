#!/usr/bin/env python3
"""Will a workflow fit on a GPU, and how long do its weights take to load? (C13·M01, C13·M04)

  python gpu_plan.py 03_i2v_wan22_5b 06_i2v_ltx25            # starter workflows (sizes from models.lock.json)
  python gpu_plan.py --weights-gb 29.2 --encoder-gb 9.5      # any model
  python gpu_plan.py --llm-gb 18                              # upper bound of LLM decode speed per GPU

Rules used (state them in your plan; they are estimates, not benchmarks):
  - The text encoder runs once at the start; it can be offloaded to system RAM before sampling.
  - The diffusion model must be in VRAM while it samples (or the run becomes much slower with offloading).
  - Two-expert models (high-noise and low-noise) need only one expert in VRAM at a time.
  - Activations need extra VRAM that grows with resolution and frames: --headroom GB (default 6).
  - Load time = weight bytes / storage read speed.
  - LLM decoding reads all weights for every token: tokens/s <= memory bandwidth / model bytes.
GPU numbers are from vendor spec sheets (memory size and bandwidth only). Add your own GPU with --gpu name:vram_gb:bandwidth_gbs.
"""
import argparse
import json
from pathlib import Path

STARTER = Path(__file__).resolve().parent.parent
GPUS = {  # name: (VRAM GB, memory bandwidth GB/s) from vendor spec sheets
    "RTX 4090": (24, 1008),
    "RTX 5090": (32, 1792),
    "L40S": (48, 864),
    "RTX PRO 6000 Blackwell": (96, 1792),
    "A100 80GB SXM": (80, 2039),
    "H100 SXM": (80, 3350),
    "H200": (141, 4800),
    "DGX Spark (unified)": (128, 273),
}
STORAGE = {  # typical sequential read, GB/s
    "PCIe 4.0 NVMe": 6.0,
    "PCIe 3.0 NVMe": 3.0,
    "SATA SSD": 0.5,
    "10 GbE NAS": 1.1,
    "1 GbE NAS": 0.11,
    "cloud network volume (typical)": 0.3,
}


def workflow_sizes(name):
    idx = {i["workflow"]: i for i in json.loads((STARTER / "comfyui" / "workflows" / "index.json").read_text())}
    lock = json.loads((STARTER / "comfyui" / "models.lock.json").read_text())
    if name not in idx:
        raise SystemExit(f"unknown workflow {name}; known: {', '.join(idx)}")
    files = {m: lock[m] for m in idx[name]["models"]}
    enc = sum(v["bytes"] for k, v in files.items() if v["directory"] == "text_encoders") / 1e9
    dif = [v["bytes"] / 1e9 for k, v in files.items() if v["directory"] in ("diffusion_models", "checkpoints")]
    other = sum(v["bytes"] for k, v in files.items() if v["directory"] not in ("text_encoders", "diffusion_models", "checkpoints")) / 1e9
    two_expert = sum(1 for k in files if "high_noise" in k or "low_noise" in k) == 2
    resident = (max(dif) if two_expert else sum(dif)) + other
    return {"workflow": name, "total_gb": round(sum(v["bytes"] for v in files.values()) / 1e9, 1), "encoder_gb": round(enc, 1),
            "sampling_resident_gb": round(resident, 1), "two_expert": two_expert}


def verdict(vram, w, headroom):
    need_all = w["sampling_resident_gb"] + w["encoder_gb"] + headroom
    need_offload = w["sampling_resident_gb"] + headroom
    if need_all <= vram:
        return "fits, all in VRAM"
    if need_offload <= vram:
        return "fits if the text encoder is offloaded after encoding"
    return f"does not fit: offload of the model itself (slow), FP8/4-bit weights, or a bigger GPU (needs about {need_offload:.0f} GB)"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("workflows", nargs="*")
    ap.add_argument("--weights-gb", type=float)
    ap.add_argument("--encoder-gb", type=float, default=0.0)
    ap.add_argument("--headroom", type=float, default=6.0, help="GB for activations, VAE decode, and the CUDA context")
    ap.add_argument("--llm-gb", type=float, help="LLM weight size in GB: prints a decode-speed upper bound per GPU")
    ap.add_argument("--gpu", action="append", default=[], help="extra GPU as name:vram_gb:bandwidth_gbs")
    a = ap.parse_args()
    for g in a.gpu:
        n, v, b = g.rsplit(":", 2)
        GPUS[n] = (float(v), float(b))
    items = [workflow_sizes(w) for w in a.workflows]
    if a.weights_gb:
        items.append({"workflow": "custom", "total_gb": a.weights_gb + a.encoder_gb, "encoder_gb": a.encoder_gb,
                      "sampling_resident_gb": a.weights_gb, "two_expert": False})
    for w in items:
        print(f"\n{w['workflow']}: {w['total_gb']} GB of weights; text encoder {w['encoder_gb']} GB; "
              f"in VRAM while sampling {w['sampling_resident_gb']} GB{' (one of two experts at a time)' if w['two_expert'] else ''}; "
              f"headroom {a.headroom} GB")
        for name, (vram, _) in GPUS.items():
            print(f"  {name:28} {vram:5.0f} GB  {verdict(vram, w, a.headroom)}")
        print("  load time of all weights:")
        for s, gbs in STORAGE.items():
            print(f"    {s:32} {w['total_gb'] / gbs:7.0f} s")
    if a.llm_gb:
        print(f"\nLLM decode upper bound for {a.llm_gb} GB of weights (bandwidth / bytes per token; real speed is lower):")
        for name, (vram, bw) in GPUS.items():
            fit = "" if a.llm_gb + 2 <= vram else "  (does not fit)"
            print(f"  {name:28} {bw / a.llm_gb:6.0f} tokens/s{fit}")


if __name__ == "__main__":
    main()
