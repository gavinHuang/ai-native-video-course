---
title: Small and fast models - quantization, distillation, LoRA
hours: 8
outcomes:
  - Explain quantization and compare FP16, FP8, INT8, NVFP4, and GGUF.
  - Explain step distillation and why distilled models are fast.
  - Explain how a LoRA changes a model with few parameters.
  - Choose a model variant for a given GPU, speed, and quality target.
keywords: [quantization, distillation, LoRA, offload, GGUF]
summary: >
  Three methods make large models practical. Quantization stores each parameter with fewer bits, so the model needs
  less memory and often runs faster, with some quality loss. Distillation trains a student model to do in 4 to 8
  steps what the teacher does in 30 or more. A LoRA adds small trainable matrices to a frozen model, so you can teach
  a character, product, or style with a file of tens or hundreds of megabytes. Offload moves parts of the model
  between GPU and CPU memory when VRAM is too small.
diagram:
  type: compare
  title: Choose a variant
  left:
    title: "Speed / memory methods"
    items: ["FP8 / INT8: half the memory of FP16", "NVFP4 / GGUF Q4: about a quarter", "Distilled: 4–8 steps instead of 30+", "Offload: fits, but slower"]
  right:
    title: "Typical cost"
    items: ["Small quality loss, usually fine", "Visible loss in fine detail", "Less diversity, sometimes less detail", "Large time cost per run"]
watch:
  - title: "Hugging Face blog — Exploring quantization backends in Diffusers"
    url: https://huggingface.co/blog/diffusers-quantization
    note: "Read the comparison tables of memory and quality."
  - title: "Edward Hu — LoRA explained by the author (Microsoft)"
    url: https://www.youtube.com/watch?v=DhRoTONcyZE
    note: "Optional. The idea of low-rank updates."
quiz:
  - q: "A LoRA file for a video model is usually:"
    options: ["As big as the full model", "Tens to hundreds of MB", "Less than 1 KB", "A list of prompts"]
    answer: 1
    explain: "A LoRA stores only small low-rank matrices for some layers, not the full weights."
  - q: "Main benefit of a distilled model?"
    options: ["Better prompt understanding", "Far fewer steps, so much faster generation", "Higher native resolution", "Open license"]
    answer: 1
    explain: "Distillation teaches a student to jump in large steps. It is ideal for exploration and real-time use."
  - q: "Your GPU has 16 GB. The model in FP8 needs 14 GB for weights, plus a 9 GB text encoder. Best option?"
    options: ["Buy a new GPU first", "Run the text encoder, then offload it to CPU before the DiT runs", "Use FP32", "Increase resolution"]
    answer: 1
    explain: "The text encoder runs once per prompt. Offloading it after use frees VRAM for the DiT."
  - q: "Which quantization is most likely to show visible artifacts in fine textures?"
    options: ["BF16", "FP8", "4-bit", "FP32"]
    answer: 2
    explain: "Fewer bits = more rounding error. 4-bit is very useful, but check fine detail."
  - q: "A job takes 3 minutes: 70 s to load the model, 90 s to denoise, 20 s to decode. Which change helps most for 50 similar jobs?"
    options: ["4-bit weights", "Keep the model loaded between jobs (a warm worker), so the 70 s load happens once", "More steps", "A shorter prompt"]
    answer: 1
    explain: "Measure every stage. Loading is often the largest fixed cost per job."
  - q: "A step-caching method saves 45 % of the time. How do you decide to use it?"
    options: ["Always use it", "Test it like a quantization: same prompts and seeds with and without it, compare detail and motion blind, then decide per shot type", "Never use it", "Use it only for audio"]
    answer: 1
    explain: "Every speed-up trades some quality. Measure the trade on your eval set (M07)."
deeper:
  - title: "Hu et al. (2021) — LoRA: Low-Rank Adaptation of Large Language Models"
    url: https://arxiv.org/abs/2106.09685
  - title: "Sauer et al. (2023) — Adversarial Diffusion Distillation"
    url: https://arxiv.org/abs/2311.17042
  - title: "Micikevicius et al. (2022) — FP8 Formats for Deep Learning"
    url: https://arxiv.org/abs/2209.05433
  - title: "llama.cpp GGUF format documentation"
    url: https://github.com/ggml-org/ggml/blob/master/docs/gguf.md
---
## Learn

### Quantization
**Quantization** stores each parameter with fewer bits.

| Format | Bits | Notes |
|---|---|---|
| FP32 | 32 | Training reference. Not used for inference. |
| BF16 / FP16 | 16 | Standard full-quality inference. |
| FP8 (E4M3) | 8 | Hardware support on NVIDIA Ada/Hopper/Blackwell. Small quality loss. |
| INT8 | 8 | Integer; needs a scale per block or channel. |
| NVFP4 | 4 | Blackwell (RTX 50, B200) hardware format. Fast and small. |
| GGUF Q4–Q8 | 4–8 | Block quantization format from llama.cpp, widely used in node-graph tools for low VRAM. |

Rules:
- Start with FP8 on a 24–32 GB GPU.
- Use 4-bit only when necessary, and check faces, text, and fine textures.
- The speed gain needs hardware support. FP8 on an old GPU saves memory but may not run faster.

### Distillation
**Step distillation** trains a student model to match the output of a teacher in far fewer steps. Methods include consistency distillation and adversarial distillation. Results:
- 4–8 steps instead of 30–50.
- Often CFG = 1 (guidance is baked in), so each step is also cheaper.
- Less variety between seeds, and sometimes less fine detail.

Use distilled models to explore. Use the full model to finish (pattern from M03).

### LoRA
A **LoRA** (low-rank adaptation) freezes the base model. It adds two small matrices A and B next to some weight matrices W. The change is `W + B·A`. If W is 3,072 × 3,072 (9.4 M numbers) and the rank is 32, A and B together have only about 197,000 numbers. So:
- training needs much less memory,
- the file is small (tens to hundreds of MB),
- you can load several LoRAs and set a strength for each one.

Uses: a character, a product, a style, a camera move, or a speed-up (some "lightning" LoRAs distill steps).

### Offload and block swap
When VRAM is too small, parts of the model live in CPU RAM and move to the GPU when needed. This makes it run, but slower. Text encoders are good offload candidates because they run once. "Block swap" moves transformer blocks in and out during each step; it is slower, but allows large models on 16–24 GB.

### Caching and reuse
Some work does not need to be done again:
- **Text embeddings:** the text encoder output for a prompt is the same in every run. Cache it, and you can even unload the encoder.
- **Step caching:** consecutive denoising steps often change the result very little. Caching methods reuse part of a step's computation in the next step. They save 30–60 % of the time with a small loss of detail. Test them like a quantization.
- **The same seed and start frame** across variations: you change only what you test.

### Speed is not only the model
Measure the whole job: model loading (tens of seconds for large files from a slow disk), text encoding, denoising, VAE decoding, and the video encode. On a cold start, loading can take longer than generation. Keep models loaded between jobs (a warm worker, C13) and put model files on a fast local disk.

### Decision table
| Situation | Choice |
|---|---|
| 32 GB GPU, final quality | FP8 full model, 25–40 steps |
| 24 GB GPU, exploration | FP8 or GGUF Q8 distilled, 4–8 steps |
| 16 GB GPU | GGUF Q4–Q6 or a small (5B) model, offload the text encoder |
| Same character in 40 shots | Train a LoRA (C14) |
| Cloud API | Variant is chosen by the vendor; you pay per second |

## Worked example

**Task:** Same Wan 2.2 14B I2V shot on three set-ups. Reported orders of size; your numbers will differ.

| Set-up | Variant | Steps | Result |
|---|---|---|---|
| RTX 5090, 32 GB | FP8 full | 30 | Best detail; several minutes per 5 s clip |
| RTX 5090, 32 GB | FP8 + "lightning" step LoRA | 4–8 | Under a minute; slightly less micro-detail |
| 16 GB laptop GPU | GGUF Q5 + text encoder offload | 8 | Runs; slower; soft detail on hair |

Decision: explore with the step LoRA. Re-render the 10 selected shots with the full model at 30 steps, same seed.

## Lab

**Deliverable:** `C01/M06/variants.md`.

1. Choose one open model available in several variants on Hugging Face (for example Wan 2.2, LTX-2.5, or FLUX.2).
2. List all official and popular community variants: precision, size in GB, recommended steps, license.
3. If you have a GPU (or rent one for 1 hour): run the same prompt + seed on 2 variants. Record time per run and peak VRAM (`nvidia-smi --query-gpu=memory.used --format=csv -l 1`).
4. If you have no GPU: use a hosted API that offers "fast" and "pro" versions of one model. Record time and cost.
5. Write your decision table for a 24 GB GPU and for a 32 GB GPU.

**Result checklist**
- [ ] Variant list with sizes and sources.
- [ ] Measured time and memory (or cost) for 2 variants.
- [ ] Decision table with reasons.

## Model answer

A good report has: (1) a list such as "BF16 28 GB / FP8 14 GB / GGUF Q8 15 GB / Q4 8 GB / distilled LoRA 600 MB"; (2) measured numbers, for example "FP8 full 30 steps: 6 min, 29 GB peak; FP8 + 6-step LoRA: 1 min 10 s, 27 GB peak"; (3) a decision: "24 GB: GGUF Q8 or FP8 with text-encoder offload, step LoRA for exploration. 32 GB: FP8 full for finals." It also says what quality loss was visible (for example "Q4 changed small text on a sign").

A strong report also separates the stages: load time, denoise time, and decode time for each variant. Without this split, a reader cannot tell if a faster variant is faster at generation or only faster to load.
