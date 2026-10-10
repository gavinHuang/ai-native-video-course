---
title: GPU fundamentals for generative video
hours: 12
outcomes:
  - Explain VRAM capacity, memory bandwidth, compute at low precision, and the software stack, and which one limits a workload.
  - Explain why video diffusion is compute-bound and LLM decoding is bandwidth-bound, with the arithmetic.
  - Predict whether a workflow fits on a GPU (weights, encoder offload, two-expert models, activation headroom).
  - Compare CUDA, Apple Metal/MLX, and ROCm for this work, and choose a platform per workload.
keywords: [VRAM, memory bandwidth, tensor cores, compute-bound, bandwidth-bound]
summary: >
  Three hardware numbers decide most questions: VRAM capacity (does it fit), memory bandwidth (how fast weights can
  be read), and compute at low precision (how fast the matrix work runs). Video diffusion processes thousands of
  tokens per step with the same weights, so it is limited by compute. LLM decoding produces one token at a time and
  reads all weights for each token, so it is limited by bandwidth. Whether a workflow fits depends on what must be
  in VRAM during sampling; the text encoder can be offloaded, and two-expert models need one expert at a time.
diagram:
  type: compare
  title: What limits the workload
  left:
    title: "Video diffusion: compute-bound"
    items: ["Thousands of tokens per step", "Same weights reused for all tokens", "Low-precision tensor cores help most", "Faster GPU = faster steps"]
  right:
    title: "LLM decoding: bandwidth-bound"
    items: ["One token per step", "All weights read for every token", "Memory bandwidth sets tokens/s", "Large unified memory works well"]
watch:
  - title: "NVIDIA — Blackwell architecture overview"
    url: https://www.nvidia.com/en-us/data-center/technologies/blackwell-architecture/
    note: "Note FP4/FP8 support and the memory numbers."
  - title: "RTX 5090 vs 128 GB unified memory: Strix Halo, DGX Spark, Mac Studio M5 (analysis)"
    url: https://medium.com/@rosgluk/rtx-5090-vs-128gb-unified-memory-strix-halo-dgx-spark-and-mac-studio-m5-566c12d6e374
    note: "Read the trade-off: fast 32 GB against larger, slower memory."
quiz:
  - q: "An LLM has 18 GB of weights. A GPU has 1,792 GB/s of memory bandwidth. What is the upper bound of its decode speed?"
    options: ["About 1,792 tokens/s", "About 100 tokens/s (1,792 / 18), because every token reads all weights once", "About 18 tokens/s", "It depends only on TFLOPS"]
    answer: 1
    explain: "Decode speed ≤ bandwidth / bytes per token. Real speed is lower (other reads, overheads)."
  - q: "Why is video diffusion compute-bound?"
    options: ["It uses little memory", "Each step processes thousands of tokens with the same weights, so the matrix multiplications dominate and the weights are read once per step, not once per token", "It runs on the CPU", "It is random"]
    answer: 1
    explain: "Many tokens per weight read = high arithmetic intensity. That is where low-precision tensor cores give large gains."
  - q: "A workflow has a 10 GB model, a 7 GB text encoder, and a 1.4 GB VAE. On a 24 GB GPU with 6 GB of activation headroom, does it fit?"
    options: ["No", "Not all at once (24.4 GB), but yes if the text encoder is offloaded after it encodes the prompt (17.4 GB)", "Yes, easily", "Only on CPU"]
    answer: 1
    explain: "The text encoder runs once at the start. Moving it to system RAM before sampling frees its VRAM."
  - q: "A two-expert 14B video model has two 14.3 GB files. Why does it fit on a 32 GB GPU?"
    options: ["It does not", "Only one expert samples at a time (high-noise steps, then low-noise steps), so only about 14 GB of expert weights must be in VRAM at once", "The files are compressed in VRAM", "The GPU uses the disk"]
    answer: 1
    explain: "Mixture-of-experts models with sequential experts can swap them between the two sampling phases (C11·M02)."
  - q: "A Mac with 128 GB of unified memory and a PC with a 32 GB GPU: which is better for a 22B video model that fits in both?"
    options: ["The Mac, because it has more memory", "Usually the PC for speed: diffusion is compute-bound and the CUDA GPU has much more low-precision compute and mature kernels; the Mac is good for editing and large LLMs", "They are the same", "Neither can run it"]
    answer: 1
    explain: "Capacity decides whether it runs. Compute and software decide how fast."
  - q: "A new FP4 kernel speeds up sampling 2×, but only on the newest GPU generation. What is the lesson for planning?"
    options: ["Ignore it", "Precision support and kernels differ by GPU generation and platform; check which precisions your GPU accelerates before you plan with a speed-up", "FP4 is always slower", "Buy any GPU"]
    answer: 1
    explain: "Low-precision formats help only when the hardware and the software path support them."
  - q: "Why does the speed of the disk matter for a generation service?"
    options: ["It does not", "Weights must be read into memory at every cold start: 45 GB takes about 7 s from a fast NVMe drive and more than 2 minutes from a typical network volume", "For the output files only", "For the logs"]
    answer: 1
    explain: "Load time = bytes / read speed. It adds to every cold start (M04)."
deeper:
  - title: "Horace He — Making Deep Learning Go Brrrr From First Principles"
    url: https://horace.io/brrr_intro.html
  - title: "Apple MLX — GitHub"
    url: https://github.com/ml-explore/mlx
  - title: "Wikipedia — Roofline model (the compute versus bandwidth idea, after Williams et al.)"
    url: https://en.wikipedia.org/wiki/Roofline_model
---
## Learn

### Three numbers
1. **VRAM capacity (GB):** the weights in use, the activations, and the working buffers must fit. If they do not, the run fails, or it becomes much slower because parts move between system RAM and the GPU.
2. **Memory bandwidth (GB/s):** how fast data moves from VRAM to the compute units.
3. **Compute at low precision (TFLOPS):** how fast the tensor cores do matrix work in BF16, FP8, or FP4. Lower precision is faster when the hardware supports it.
A fourth factor is the **software stack**: drivers, kernels, and framework support. A fast GPU with weak kernels for your model is slow.

### Compute-bound and bandwidth-bound
A useful mental model: for each byte of weights that the GPU reads, how much arithmetic does it do?
- **Video and image diffusion:** each step processes the whole latent, thousands of tokens (C11·M02 computed 27,280 tokens for a 5 s clip). The same weights are used for all of them. So each weight read feeds a lot of arithmetic: the work is **compute-bound**. More low-precision compute gives faster steps.
- **LLM decoding:** each step makes one new token, and must read all weights for it. Little arithmetic per byte: the work is **bandwidth-bound**. An upper bound: tokens per second ≤ bandwidth / weight bytes. An 18 GB model on a 1,792 GB/s GPU: at most about 100 tokens/s.
- **Training** (LoRAs, C14) needs both, plus memory for gradients and optimizer states.

### Will it fit?
Add up what must be in VRAM during sampling:
- **The diffusion model:** all of it, while it samples. A two-expert model (high-noise and low-noise experts) needs only one expert at a time.
- **The VAE** and small extras (upscalers, LoRAs).
- **Activation headroom:** grows with resolution and frame count. Start with about 6 GB and measure (C11·M02).
- **The text encoder:** it runs once, at the start. It can be offloaded to system RAM before sampling. A large encoder (a 12B language model) is often bigger than you expect.
If it still does not fit: lower-precision weights (FP8, 4-bit), offloading of parts of the model (much slower), or a bigger GPU.

### Load time
Weights must be read from storage at every cold start: load time = weight bytes / read speed. 45 GB loads in about 7 s from a fast PCIe 4.0 NVMe drive (about 6 GB/s), about 40 s from a 10 GbE NAS, and more than 2 minutes from a typical network volume. This matters for serving (M04).

### Platforms
- **NVIDIA with CUDA:** the default for generative video. New kernels and low-precision paths (FP8, FP4) appear here first. Consumer cards have 24–32 GB; professional cards up to 96 GB; data-center GPUs 80–141 GB or more, mostly rented.
- **Apple silicon (Metal, MLX, PyTorch MPS):** large unified memory, quiet, and very good for editing, grading, and LLMs. Diffusion runs, but usually much more slowly, and video tools often arrive later.
- **AMD (ROCm):** many PyTorch models run; check each model and kernel.
- **Unified-memory boxes** (128 GB in a small computer): large capacity, lower bandwidth. Good for big models that would not fit elsewhere; slower per step.

### Media engines
Hardware video encoders and decoders matter for editing and delivery, not for generation: H.264, H.265, and AV1 on most GPUs; ProRes on Apple silicon.

## Tool walkthrough

### Plan the fit and the load time

```bash
python starter/tools/gpu_plan.py 03_i2v_wan22_5b 04_flf2v_wan22_14b 06_i2v_ltx25
python starter/tools/gpu_plan.py --weights-gb 29.2 --encoder-gb 9.5 --headroom 8
python starter/tools/gpu_plan.py --llm-gb 18
python starter/tools/gpu_plan.py 06_i2v_ltx25 --gpu "My GPU:48:960"
```

The tool reads the file sizes from the starter `models.lock.json`. It uses vendor spec-sheet numbers for VRAM and bandwidth. Add your own GPU with `--gpu name:vram_gb:bandwidth_gbs`.

### Measure on the real GPU
- `nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu --format=csv -lms 500` in a second terminal during a run.
- ComfyUI's `/system_stats` endpoint for VRAM (C11·M04).
- PyTorch: `torch.cuda.max_memory_allocated()` after a run.

### Platforms and numbers (as of 2026-10)
RTX 5090: 32 GB, 1,792 GB/s. RTX PRO 6000 Blackwell: 96 GB, 1,792 GB/s. H100 SXM: 80 GB, 3,350 GB/s. H200: 141 GB, 4,800 GB/s. DGX Spark: 128 GB unified, about 273 GB/s. Apple M5 Max and M5 Ultra: up to 128 and 512 GB unified memory (see the landscape page and the vendor's spec sheet for bandwidth).

## Worked example

**Fit plan for three starter workflows** (`gpu_plan.py`, 6 GB headroom; 2026-10-04):

| Workflow | Weights | In VRAM while sampling | 24 GB (RTX 4090) | 32 GB (RTX 5090) | 96 GB |
|---|---|---|---|---|---|
| 03 Wan 2.2 5B I2V | 18.1 GB | 11.4 GB | fits with encoder offload | fits | fits |
| 04 Wan 2.2 14B FLF2V | 35.6 GB | 14.5 GB (one expert) | fits with encoder offload | fits | fits |
| 06 LTX-2.5 I2V | 44.9 GB | 24.3 GB | does not fit (needs about 30 GB) | fits with encoder offload | fits |

Load times of all weights for workflow 06: about 7 s from PCIe 4.0 NVMe, 41 s from a 10 GbE NAS, 150 s from a typical network volume.

**LLM decode bound** for an 18 GB model: RTX 5090 at most about 100 tokens/s; H100 about 186; DGX Spark about 15. The unified-memory box can hold much larger LLMs, but it reads them slowly.

**Question: LTX-2.5 (22B) on a Mac Studio with 128 GB, or a PC with an RTX 5090?**
- Capacity: 44.9 GB of weights. The Mac holds it all; the 5090 needs the text encoder offloaded.
- Speed: diffusion is compute-bound, and the CUDA GPU has much more low-precision compute and the most mature kernels. Expect several times faster steps on the 5090.
- Software: day-one workflow support targets CUDA.
- Decision: the 5090 for generation; the Mac for editing, grading, and local LLMs.

## Lab

**Deliverable:** `C13/M01/` with a fit plan for your workflows, one measured run, and a platform decision.

1. Run `gpu_plan.py` for the workflows that you use. Add the GPU that you have or rent.
2. Run one workflow on a real GPU. Measure peak VRAM and the time per step. Compare with the plan. Explain the difference.
3. Run a local LLM (any size that fits) and measure tokens per second. Compare with the bandwidth bound.
4. Write a platform decision for your studio: which machine for generation, editing, grading, LLMs, and training, with the numbers.

**Result checklist**
- [ ] Fit plan for your workflows.
- [ ] One measured run: peak VRAM and time, against the plan.
- [ ] LLM tokens/s against the bound.
- [ ] A platform decision with reasons.

## Model answer

**Plan versus measurement (shape of a strong answer):**

| Run | Plan | Measured | Why the difference |
|---|---|---|---|
| 03 Wan 5B, 1280 × 704, 121 frames, RTX 5090 | fits; 11.4 GB weights + about 6 GB headroom | peak 23.6 GB | the activations at this size need about 12 GB, not 6 |
| 03 Wan 5B, 640 × 352 | same | peak 15.1 GB | a quarter of the tokens: about 4 GB of activations |
| LLM 18 GB (Q8), RTX 5090 | ≤ 100 tokens/s | 71 tokens/s | the KV cache and other reads add traffic |

"Decision: an RTX 5090 workstation for exploration with the Wan 5B and 14B workflows. LTX-2.5 batches and LoRA training on a rented 80 GB GPU. Editing and grading on the existing Mac. I set the headroom for my sizes to 12 GB in all future plans."
