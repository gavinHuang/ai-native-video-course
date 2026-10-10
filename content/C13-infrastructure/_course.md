---
code: C13
title: Infrastructure for Generative Video
level: 4
hours: 60
prereq: C01·M06, C11
outcomes:
  - Explain GPU architecture limits - VRAM, bandwidth, compute, precision, software stack.
  - Specify a local workstation and storage system for AI video work.
  - Choose between GPU rental, serverless GPU, and per-output APIs for each workload.
  - Serve open models in containers with autoscaling and controlled cold starts.
  - Use cloud services for storage, review, collaboration, and delivery.
  - Model cost and operate the system securely.
---
## About this course

You already know cloud and containers. This course applies that knowledge to generative video, where the GPU, memory, and file sizes change every decision. Prices and products are as of October 2026; see the tool landscape.

**Starter tools for this course** (in `tools/` of the [starter kit](starter.zip)):

| Tool | Use |
|---|---|
| `gpu_plan.py` | Does a workflow fit on a GPU (encoder offload, two-expert models, headroom)? Load time per storage type; LLM decode bound (M01, M04) |
| `cost_model.py` | Monthly cost of a workload on rental, serverless, API, and owned hardware, per usable second; break-even (M03) |
| `../solutions/C11-M01/Dockerfile` | A pinned container for the graph server (M04) |
| `takes.py`, `promptlog.py`, `../pipeline/genqueue.py` | Cost data for the monthly report (M05) |
