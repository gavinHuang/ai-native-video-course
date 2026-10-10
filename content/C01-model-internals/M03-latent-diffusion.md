---
title: Latent space, diffusion, and flow matching
hours: 10
outcomes:
  - Explain why generation happens in a compressed latent space.
  - Explain the forward (noise) and reverse (denoise) process of diffusion.
  - Explain flow matching as a straight path from noise to data.
  - Connect steps, sampler, and scheduler to quality and speed.
keywords: [latent, VAE, diffusion, flow matching, sampler, step]
summary: >
  Pixels are too many to work with directly. A VAE compresses each image or video into a smaller latent, and decodes
  it back at the end. Diffusion training adds noise to latents and teaches the model to predict that noise. At
  generation time, the model starts from pure noise and removes noise step by step. Flow matching learns a direct
  velocity from noise to data, so fewer steps are necessary. The sampler and scheduler decide how big each step is.
  More steps usually give more detail, but cost more time.
diagram:
  type: flow
  title: Latent diffusion at generation time
  nodes: ["Random noise latent (seed)", "Model predicts noise / velocity", "Sampler takes one step", "Repeat for N steps", "Clean latent", "VAE decoder → pixels"]
  highlight: [1, 5]
  loop: "steps 2–4 repeat, typically 4 to 50 times"
watch:
  - title: "Welch Labs / 3Blue1Brown — But how do AI images and videos actually work?"
    url: https://www.youtube.com/watch?v=iv-5mZ_9CPY
    note: "Watch all (about 40 min). The best visual explanation of diffusion and guidance."
  - title: "Computerphile — How AI image generators work (Stable Diffusion)"
    url: https://www.youtube.com/watch?v=1CIpzeNxIhU
    note: "Watch all (17 min). Simple first view of denoising."
quiz:
  - q: "Why do models generate in a latent space instead of pixels?"
    options: ["Latents look better", "Latents are much smaller, so attention and memory cost less", "Pixels cannot be decoded", "It is a legal requirement"]
    answer: 1
    explain: "A video VAE compresses about 8×8 in space and 4× in time. The transformer then works on far fewer tokens."
  - q: "What does a diffusion model learn in training?"
    options: ["To add noise", "To predict the noise (or velocity) in a noisy latent", "To compress video", "To write prompts"]
    answer: 1
    explain: "Training adds known noise. The model learns to predict it. At generation, it uses this skill to remove noise step by step."
  - q: "Main practical benefit of flow matching / rectified flow?"
    options: ["Straighter paths from noise to data, so good results with fewer steps", "No need for a VAE", "No need for training data", "It removes the seed"]
    answer: 0
    explain: "A straighter path can be followed with larger steps. This, plus distillation, makes 4–8 step generation possible."
  - q: "Same prompt, same model, same seed, same settings, same hardware. The result is:"
    options: ["Always different", "Usually the same (deterministic)", "Always black", "Random resolution"]
    answer: 1
    explain: "The seed fixes the start noise. With the same settings, the result is usually reproducible. Some GPU kernels add small non-determinism."
  - q: "You run image-to-image with a denoise strength of 0.3. What do you expect?"
    options: ["A new composition", "The same composition and layout, with changed texture and detail: the process starts from your image with only 30 % noise, so only the late steps run", "A black image", "A video"]
    answer: 1
    explain: "Strength (denoise) chooses where on the noise path you start. Low strength keeps layout; high strength (0.7–1.0) re-invents it."
  - q: "A 1080p video decode fails with an out-of-memory error after all steps finished. What is the usual fix?"
    options: ["More steps", "Tiled VAE decoding: decode the latent in overlapping tiles (in space and time) to cut peak memory", "A new seed", "A shorter prompt"]
    answer: 1
    explain: "The decoder needs a lot of memory at full resolution. Tiling trades a little time for much less memory; check the tile seams."
  - q: "Small text on a sign is unreadable in every take, even at high step counts. Where is the likely limit?"
    options: ["The seed", "The VAE: at 8× spatial compression, fine detail such as small letters is hard to reconstruct; make text larger, add it in compositing, or upscale", "The sampler name", "The prompt language"]
    answer: 1
    explain: "Detail that the VAE cannot represent cannot appear, whatever the transformer does."
deeper:
  - title: "Ho et al. (2020) — Denoising Diffusion Probabilistic Models"
    url: https://arxiv.org/abs/2006.11239
  - title: "Rombach et al. (2021) — High-Resolution Image Synthesis with Latent Diffusion Models"
    url: https://arxiv.org/abs/2112.10752
  - title: "Lipman et al. (2022) — Flow Matching for Generative Modeling"
    url: https://arxiv.org/abs/2210.02747
  - title: "Liu et al. (2022) — Flow Straight and Fast (Rectified Flow)"
    url: https://arxiv.org/abs/2209.03003
---
## Learn

### The latent space
A 5 s, 720p video has about 75 million pixel values. Attention over all of them is impossible. So the system first compresses the video with a **VAE** (variational autoencoder).
- The **encoder** makes a small **latent**. A typical video VAE compresses 8× in width, 8× in height, and 4× in time. It keeps 16 to 48 channels per position.
- The **decoder** turns the latent back into pixels.

All generation happens in the latent. The decoder runs once at the end. VAE quality sets an upper limit on detail. Small text and fine textures often fail in the VAE, not in the transformer.

### Diffusion: the idea
**Training:**
1. Take a clean latent from the training data.
2. Add random noise at a random strength.
3. Ask the model to predict the noise (or the clean latent).
4. Use the error as the loss.

**Generation:**
1. Start from pure random noise. The **seed** decides this noise.
2. The model predicts the noise in it.
3. Remove a part of the predicted noise. This is one **step**.
4. Repeat until the latent is clean.

Early steps decide the composition and layout. Late steps add detail and texture. This is useful in practice. If you like the composition but not the detail, keep the seed and change late-step settings. If the composition is wrong, change the seed or the prompt. Do not spend late-step settings on a layout problem.

![Denoising: the composition appears early, detail appears late](fig:denoise.svg)

### Start from an image: denoise strength
You do not have to start from pure noise. In **image-to-image** (and video-to-video), the system encodes your input to a latent, adds noise to a chosen level, and runs only the remaining steps. The **denoise strength** (0–1) sets that level:
- 0.2–0.4: same composition and shapes; new texture, light, or style details;
- 0.5–0.7: same rough layout; new forms and details;
- 0.8–1.0: little of the input remains.
This follows directly from "early steps decide composition". It is the basis of restyling, upscaling with detail (C09), and many editing workflows.

### The VAE in practice
- **Decode memory:** decoding a long, high-resolution latent needs a lot of GPU memory. **Tiled decoding** decodes overlapping tiles in space and time; it uses less memory but can show seams.
- **Each model family has its own VAE.** A latent from one family cannot be decoded with another family's VAE.
- **Round trips lose detail.** Encode and decode a frame several times, and it gets softer. Keep your masters in pixels, not in latents. Encode once, edit, and decode once.

### Flow matching
Classic diffusion follows a curved path from noise to data. Curved paths need many small steps (25–50). **Flow matching** (and rectified flow) trains the model to predict a velocity along a straight line from noise to data. A straight path tolerates large steps. Most 2025–2026 image and video models use flow matching. With **distillation** (C01·M06), some models make good output in 4–8 steps.

### Sampler and scheduler
- The **sampler** is the method that takes a step (for example Euler, DPM++, UniPC).
- The **scheduler** decides the noise level at each step (for example linear, Karras, "shift" for flow models).

Rules of thumb:
- Use the sampler and step count from the model card first. Change one setting at a time, and log it.
- Too few steps: soft, unfinished detail.
- Too many steps: more time, small gain, sometimes over-sharpening.
- Flow models often have a "shift" value. A higher shift spends more steps at high noise. This helps the global structure at high resolution.

## Worked example

**Task:** Understand the step budget of an open video model in ComfyUI.

Model card default for a distilled LTX-type model: 8 steps, Euler sampler. Full model: 30–40 steps.

The times below are illustrative orders of size, not measurements; measure your own in the lab.

1. Run 1: distilled model, 8 steps, seed 1234 → 720p, 5 s. Time: about 40 s on an RTX 5090 class GPU.
2. Run 2: full model, 30 steps, same seed → about 4× the time. Better fine texture on fabric; same composition.
3. Run 3: full model, 12 steps → texture between run 1 and run 2; time about 1.6× run 1.
4. Decision: use the distilled model for exploration (many seeds, fast). Use the full model only for selected shots.

This "explore fast, finish slow" pattern appears in every pipeline in Level 4.

## Lab

**Deliverable:** `C01/M03/` with images and a short report.

Use any hosted image model that exposes steps and seed (for example a FLUX model on fal.ai or Replicate), or ComfyUI if you have a GPU.

1. Fix one prompt and seed 42.
2. Generate at steps 1, 2, 4, 8, 16, 32 (or the model's allowed values).
3. Put the results in one contact sheet (use `ffmpeg` tile filter or Python PIL).
4. Change only the seed (3 values) at the best step count.
5. Report: at which step does the composition stop changing? At which step does detail stop improving? What does the seed change?

**Result checklist**
- [ ] One contact sheet for steps, one for seeds.
- [ ] The report names the step where composition is fixed and the step where detail saturates.
- [ ] Every image has a line in your prompt log (model, seed, steps, cost).

## Model answer

Typical result with a flow-matching image model:
- Steps 1–2: blurry color fields; the main layout is already visible.
- Step 4: the composition is fixed. Further steps do not move objects.
- Steps 8–16: edges, skin, and fabric detail improve.
- Step 32: very small gain over 16; time doubles.
- Seed change: composition changes (pose, camera, layout); style and palette stay similar because the prompt is the same.

Conclusion: the seed and the early steps control composition. Late steps control detail. For exploration, vary seeds at low steps. For final output, fix the seed and use more steps. Write the measured times next to each step count: in the report, "step 16 took 2.1× the time of step 8 for a gain that 2 of 3 viewers saw" is a decision that others can check.
