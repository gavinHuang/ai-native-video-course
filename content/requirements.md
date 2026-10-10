# Requirements by level

These are the tools and resources that each level needs. All prices are estimates as of October 2026.

## Entry knowledge (assumed)
- Command line, Git, and a package manager.
- Read and change Python and JSON. Call a REST API with `curl` or Python.
- Basic cloud use (one of AWS, GCP, Azure) and Docker.

## Level 1: C01–C03

| Item | Requirement |
|---|---|
| Computer | Any modern laptop. |
| Software | Python 3.11+, Jupyter (local, or Google Colab). |
| AI access | One frontier LLM with API access (for example Claude, GPT, Gemini). An MCP-capable client (for example Claude Desktop or Claude Code). |
| Budget | About US$20–50 per month. |

## Level 2: C04–C07

| Item | Requirement |
|---|---|
| Computer | Any modern laptop. Local generation is optional at this level. |
| AI access | Credits on 2–3 hosted generators, **or** one aggregator API (fal.ai or Replicate) that serves many image, video, and audio models. A voice/music account (for example ElevenLabs). |
| 3D | A free Unreal Engine install, or a browser-based Gaussian-splat viewer. |
| Budget | About US$100–300 for the level. Video costs about US$0.05–0.15 per generated second. Plan to generate about 5 times more than you use. |

## Level 3: C08–C10

| Item | Requirement |
|---|---|
| Computer | 16 GB RAM or more, SSD with 200 GB free. |
| Editing | DaVinci Resolve (free). For the native MCP labs: Resolve Studio (one-time licence) **or** Adobe Premiere (subscription, has an MCP server). |
| Audio | Fairlight (inside Resolve) or a DAW (Reaper is low cost). |
| Budget | One licence or subscription + LLM access. |

## Level 4: C11–C15

| Item | Requirement |
|---|---|
| GPU | **Local:** NVIDIA GPU with 24 GB VRAM minimum, 32 GB recommended (RTX 5090 class). **Or cloud:** rented GPU (H100 about US$3–5/hour; A100 or L40S cheaper). Apple silicon works for some labs, but most open video models run best on CUDA. |
| Software | Docker, ComfyUI, Python, ffmpeg. |
| Cloud | One cloud account with object storage. One GPU rental or serverless GPU account (for example RunPod, Modal). |
| Budget | Cloud path: about US$150–400 GPU time for the level (LoRA training is the largest part). |

## Level 5: C16–C18

| Item | Requirement |
|---|---|
| Tools | Everything from Level 4. `c2patool` (free, open source) for content credentials. |
| Budget | Capstone: about US$100–300 generation and GPU time. |

## What happens without a local GPU
Every Level 4 lab has a cloud path. The concepts and result checklists are the same. The cloud path also teaches you cost control, which is a core skill.
