---
code: C11
title: Node Pipelines (ComfyUI)
level: 4
hours: 60
prereq: C01, C04, C05 (C14 is not needed; you add a LoRA to the M03 pipeline later, in C14·M03)
learn_allows: [ComfyUI, Comfy]
outcomes:
  - Install a pinned ComfyUI, manage model files with hashes and licenses, and explain how the server runs a graph.
  - Build start-frame graphs with reference images, and video graphs for image-to-video, first/last frame, and control video.
  - Predict time and memory from latent size and token count, and choose exploration and final settings from measurements.
  - Build an end-to-end character pipeline with lip sync and an automatic identity check.
  - Run ComfyUI headless through its API and through MCP, with tests, run logs, and reproducible versions.
---
## About this course

ComfyUI is the standard node-graph tool for open generative models. It gives you control of every step, it runs on your own hardware or in the cloud, and it has an HTTP API. In this course you use it as an engineer: you read graphs node by node, measure them, and run them from code.

**Requirement:** an NVIDIA GPU with 24 GB VRAM or more (32 GB recommended), or a rented cloud GPU. The LTX workflows (06–08) need about 44 GB of weights; they run best on 48–80 GB, so rent that size for a batch day. LTX-2.5 files are gated: log in to Hugging Face, accept the license, and set `HF_TOKEN`. You can do all client and test work (M04) on a laptop with a CPU-only ComfyUI.

## Starter kit

Download the [starter kit](starter.zip). The `comfyui/` folder has:

| File | What it is |
|---|---|
| `workflows/01_t2i_flux2_klein_4b.json` | Text to image, 4 steps (M01) |
| `workflows/02_ref_edit_flux2_klein_4b.json` | Start frame from a character reference and a place reference (M02, M03) |
| `workflows/03_i2v_wan22_5b.json` | Image to video, 1280 × 704, 121 frames at 24 fps (M02) |
| `workflows/04_flf2v_wan22_14b.json` | First and last frame to video, two-expert 14B model (M02) |
| `workflows/05_v2v_control_wan22_5b.json` | Video to video with a control video and a reference image (M02) |
| `workflows/06_i2v_ltx25.json` | Image to video with native audio, LTX-2.5, two stages (M02) |
| `workflows/07_lipsync_ia2v_ltx23.json` | Image + spoken line to video with lip sync, LTX-2.3 (M03). No LTX-2.5 version of this template exists yet. |
| `workflows/08_flf2v_ltx25.json` | First and last frame with LTX-2.5 (alternative to 04) |
| `workflows/*.map.json` | Named inputs for each workflow |
| `workflows/test/00_smoke_cpu.json` | A workflow that runs on CPU without models, for tests (M04) |
| `models.lock.json` | Every model file: URL, size, SHA-256, license (checked 2026-10-04) |
| `download_models.py` | Downloads the files for a workflow and checks each hash |
| `validate_workflow.py` | Checks a workflow against your server before you queue it |

All 8 workflows use core nodes only. We made them from the official ComfyUI templates (2026-10-04). We then checked them with the ComfyUI 0.38.0 server validation (commit `f1072eb`). We did not run them on a GPU for this release, so your first run is also a test. If a node changed in a newer ComfyUI version, the validator tells you which one.

The identity scorer (`tools/identity_score.py`) is in the starter tools; you first use it in C05·M03. Reference solutions are in `solutions/` (`C11-M01` Dockerfile, `C11-M03` pipeline script, `C11-M04` client and tests). Do each lab first, then compare.

**License note:** the lock file shows the license of each file. FLUX.2 klein 4B is Apache-2.0. The VAE file that the official klein template uses comes from the FLUX.2-dev repository (non-commercial license). LTX-2.3 and LTX-2.5 need a paid license for companies with annual revenue of US$10 million or more. Check before client work (C16·M01).
