---
title: Image and video graphs with control
hours: 16
outcomes:
  - Build a start-frame graph that uses two reference images, and explain how reference latents reach the model.
  - Run image-to-video, first/last-frame, and control-video graphs with open models, and explain each conditioning node.
  - Calculate latent size and token count from width, height, and frame count, and use it to predict cost.
  - Chain clips into a longer sequence and control drift.
  - Log time and peak VRAM for each run and choose exploration and final settings from the data.
keywords: [ControlNet, IP-Adapter, first/last frame, tiled decode, reference latent, MoE, frame count rule]
summary: >
  Control enters the graph in three places. References and start frames enter as latents attached to the
  conditioning or placed into the latent. Control videos (depth, pose, edges) enter as extra conditioning frames.
  LoRAs change the model itself. Video graphs add frame count and frame rate, and each model has a frame count rule,
  for example 4n+1 for Wan. The latent size sets the number of tokens, and the token count sets time and memory.
  Long shots are chains of clips: the last frame of one clip is the first frame of the next. Log time and peak VRAM
  for every run.
diagram:
  type: flow
  title: Image-to-video graph (Wan 2.2 5B)
  nodes: ["Load model + text encoder + VAE", "Encode prompt (positive / negative)", "Load start frame", "Wan22ImageToVideoLatent: encode frame into latent 1, mask it", "KSampler: 20 steps, CFG 5, shift 8", "VAE decode → CreateVideo 24 fps → save"]
  highlight: [3]
watch:
  - title: "ComfyUI docs — Wan 2.2 video workflows (official)"
    url: https://docs.comfy.org/tutorials/video/wan/wan2_2
    note: "Read the 5B and 14B sections. Note which files go in which folder."
  - title: "Wan 2.2 — official repository (model card and efficiency notes)"
    url: https://github.com/Wan-Video/Wan2.2
    note: "Read the TI2V-5B section: 720p at 24 fps, and the stated GPU requirements."
  - title: "Lightricks — LTX-2.5 model card (gated: log in to read the files)"
    url: https://huggingface.co/Lightricks/LTX-2.5
    note: "Read the frame and size rules and the two-stage (upscaler) pipeline."
quiz:
  - q: "You set a Wan 2.2 graph to 120 frames at 24 fps. What happens, and what do you set instead?"
    options: ["It works; Wan accepts any frame count", "The frame count must be 4n+1; use 121 frames (5 s plus the first frame)", "Use 128 frames, a power of two", "Use 24 frames per second only"]
    answer: 1
    explain: "The Wan VAE compresses 4 frames into one latent frame after the first frame. So valid counts are 4n+1: 81, 97, 121. The editor widget steps by 4 for this reason."
  - q: "How does Wan22ImageToVideoLatent make the video start on your exact key frame?"
    options: ["It adds the image to the prompt text", "It encodes the image into the first latent frame and sets a noise mask of 0 there, so the sampler does not change that frame", "It trains a LoRA on the image", "It uses the image as a style reference only"]
    answer: 1
    explain: "The node writes the encoded image into the latent and masks it. The sampler denoises only the masked-in (value 1) frames. This is why the first frame matches your key frame."
  - q: "A shot at 1280 × 704, 121 frames takes 8 minutes. You need a version at 1920 × 1056, same length. About how much longer will sampling take?"
    options: ["1.5 × (pixels grow 2.25 ×, but time is linear)", "About 2.25 × or more: tokens grow 2.25 ×, and attention cost grows faster than linearly with tokens", "The same time", "Exactly 4 ×"]
    answer: 1
    explain: "Width and height each grow 1.5 ×, so tokens grow 2.25 ×. Attention compares every token with every other token, so that part grows about 5 ×. Expect 2.5–4 × in practice, and more VRAM. Test at low size, then upscale (C09·M04)."
  - q: "In the Wan 2.2 14B first/last-frame graph, why are there two models and two samplers?"
    options: ["One is a backup", "Wan 2.2 14B is a mixture of two experts: one for the high-noise steps (layout, motion) and one for the low-noise steps (detail)", "One model is for audio", "One model makes the first frame and one makes the last frame"]
    answer: 1
    explain: "The first KSamplerAdvanced runs steps 0–10 with the high-noise expert and returns the latent with leftover noise. The second runs steps 10–20 with the low-noise expert. Only one expert needs to be in VRAM at a time."
  - q: "Your 15 s sequence is three 5 s clips chained by last frame → first frame. The colors get warmer in each clip. What is the best fix?"
    options: ["Raise CFG", "Re-anchor: start each clip from a frame that you color-match to the approved key frame, and fix the remaining drift in the grade", "Use a new seed for each clip", "Generate the 15 s at once at any size"]
    answer: 1
    explain: "Each VAE encode/decode round trip shifts color a little, and the error adds up. Correct the anchor frame before each clip, and do the last match in grading (C09·M02)."
  - q: "You add a depth control video to an image-to-video shot. The camera path now matches your 3D layout, but the actress's face changes. What do you try first?"
    options: ["Remove the reference image", "Keep the control and add or strengthen identity conditioning (reference image, character LoRA); lower control strength in late steps if the model allows it", "Raise the frame rate", "Switch to text-to-video"]
    answer: 1
    explain: "Control fixes structure, not identity. Identity comes from references and LoRAs. When control is strong in late steps, it can also fight fine detail."
  - q: "The LTX-2.5 image-to-video template samples at half size and then uses a latent upscaler. Why?"
    options: ["To save disk space", "Most structure and motion are decided at low resolution, so the expensive full-size pass needs only a few refinement steps", "The model cannot make full-size frames", "It is required by the license"]
    answer: 1
    explain: "Stage 1 makes motion and layout cheaply. The x2 latent upscaler doubles the size. Stage 2 refines detail with few steps. This multi-stage pattern is common in current video models."
  - q: "You log runs. Exploration at 640 × 352 takes 70 s; final settings at 1280 × 704 take 8 min. You need 40 usable shots and expect 1 in 3 takes to be usable. What is a sensible plan?"
    options: ["Make 120 finals", "Explore 120 takes at low size (about 2.3 h), choose 40, then render 40 finals with the same seeds and prompts (about 5.3 h)", "Make 40 finals and accept failures", "Use only text-to-video"]
    answer: 1
    explain: "Low-size takes predict the final composition and motion well when seed and prompt stay the same. You pay the full price only for chosen takes. Check that this holds for your model with 5 test pairs first."
deeper:
  - title: "ComfyUI docs — ControlNet tutorials"
    url: https://docs.comfy.org/tutorials/controlnet/controlnet
  - title: "Wan — technical report of the Wan video models (arXiv 2503.20314)"
    url: https://arxiv.org/abs/2503.20314
  - title: "Lightricks — LTX-2 repository and docs"
    url: https://github.com/Lightricks/LTX-2
---
## Learn

### Three ways to add control
A video model makes a clip from noise. Everything that you add to steer it enters the graph in one of three ways:

1. **Into the latent.** The VAE encodes a start frame, a last frame, or a reference. The graph writes it into the latent or attaches it. A noise mask tells the sampler which parts to keep. This gives the strongest control. The first frame of an image-to-video clip is your key frame because it is never denoised.
2. **Into the conditioning.** The prompt, reference latents, and control signals (depth, pose, edges) are attached to the CONDITIONING data. The model reads them at every step through attention. Strength and step range set how much they push.
3. **Into the model.** A LoRA changes the model weights. Use it for identity or style that references cannot hold (C14).

Older graphs use separate adapter models for references (IP-Adapter) and structure (ControlNet). Current open models often accept references and control natively. The starter workflows use the native nodes. The ideas are the same.

### Reference images (start frames)
A reference-image graph makes a start frame from two or more images, for example a character and a place. For each reference:
- a scale node brings it to about 1 megapixel;
- the VAE encodes it into a latent;
- a reference node attaches that latent to the conditioning.
The reference nodes are chained, so the conditioning carries all references. The prompt then says what to do with them: "the woman from image 1 in the place from image 2". The output size often comes from the first reference.

### Video settings and the frame count rule
A video VAE compresses time as well as space. This gives each model a frame count rule. If the VAE puts 4 frames into one latent frame, the valid counts are 4n + 1: the first frame is encoded alone, then groups of 4. Examples: 81, 97, 121. If the VAE puts 8 frames into one latent frame, the rule is 8n + 1.

If you enter a wrong count, the node rounds it down or the editor refuses it. Width and height have a step too, for example 16 or 32 pixels, because the VAE and the patch size divide the image into blocks. The Tool walkthrough lists the rules for the starter models.

### From settings to cost
The sampler works on tokens. Each token is a small patch of the latent. You can calculate the token count:

```python
def tokens(width, height, frames, t_comp, s_comp, patch=2):
    lat_t = (frames - 1) // t_comp + 1
    return lat_t * (height // (s_comp * patch)) * (width // (s_comp * patch))

tokens(1280, 704, 121, 4, 16)   # Wan 2.2 5B  -> 31 * 22 * 40 = 27,280 tokens
tokens(640, 640, 81, 4, 8)      # Wan 14B FLF -> 21 * 40 * 40 = 33,600 tokens
```

Attention compares each token with every other token. So time grows faster than the token count. Double the width and the height, and the token count grows 4 ×, but attention work grows about 16 ×. This is why you explore at low size and render finals only for chosen takes.

### Long shots
A model makes one clip of 5–20 s. For longer shots:
- **Chain:** use the last frame of clip N as the first frame of clip N+1. Keep the prompt, LoRAs, and settings. Change only the action text.
- **First and last frame:** when you know where the shot must end, give both frames.
- **Extension nodes:** some models continue a clip from its last latent frames. This keeps motion better than one still frame.

Chained clips drift. Each VAE round trip shifts color and detail a little. Fix this:
1. Every 2–3 clips, color-match the anchor frame to the approved key frame before you use it.
2. Keep identity conditioning (reference, LoRA) in every clip.
3. Hide joins with a cut or a cross-fade when the story allows it (C02·M04).
4. Do the final match in grading.

### Performance log
Record each run in one line: workflow hash, model files, width, height, frames, steps, seed, time, peak VRAM, and result (usable or not). Read peak VRAM with `nvidia-smi --query-gpu=memory.used --format=csv -lms 500` in a second terminal, or from the ComfyUI `/system_stats` endpoint.

Ways to make a run faster, in the order to try them:
1. Lower the size for exploration. Keep the seed and the prompt.
2. Use step-distilled LoRAs or distilled models (4–8 steps) for exploration.
3. Use FP8 weights. Use a faster attention kernel if it is installed.
4. Use tiled VAE decode (`VAEDecodeTiled`) if the decode at the end runs out of memory.
5. Rent a bigger GPU only after steps 1–4.

## Tool walkthrough

### Frame count rules of the starter models

| Model family | VAE compression (time × height × width) | Frame count rule | Example |
|---|---|---|---|
| Wan 2.2 5B | 4 × 16 × 16, 48 channels | 4n + 1 | 121 frames = 5 s at 24 fps |
| Wan 2.1 / 2.2 14B | 4 × 8 × 8, 16 channels | 4n + 1 | 81 frames = 5 s at 16 fps |
| LTX-2.3 / 2.5 | 8 × 32 × 32, 128 channels | 8n + 1 | 121 frames at 24 fps |

### The reference graph (02)
`02_ref_edit_flux2_klein_4b` follows the pattern above with these nodes: `ImageScaleToTotalPixels` (about 1 megapixel), `VAEEncode`, and two chained `ReferenceLatent` nodes. `GetImageSize` takes the output size from the first reference.

### The four video graphs in the starter kit
**03 — Image to video (Wan 2.2 5B).** `Wan22ImageToVideoLatent` encodes the start frame into latent frame 1. It sets the noise mask to 0 there. `ModelSamplingSD3` with shift 8 moves the noise schedule toward high noise, which flow-matching video models need at this size. `KSampler`: 20 steps, CFG 5, `uni_pc`. `CreateVideo` at 24 fps, then `SaveVideo`. The official template ships with the start image bypassed (text to video). The starter version connects it.

**04 — First and last frame (Wan 2.2 14B).** The 14B model is a mixture of two experts (MoE). The high-noise expert decides layout and motion. The low-noise expert adds detail. The graph has two `UNETLoader` nodes and two `KSamplerAdvanced` nodes:
- Sampler 1: high-noise expert, steps 0–10 of 20, adds noise, returns the latent with leftover noise.
- Sampler 2: low-noise expert, steps 10–20, adds no noise, finishes.
`WanFirstLastFrameToVideo` puts both frames into the latent. The model must find a motion that connects them. The template also contains 4-step "lightx2v" LoRAs, bypassed. Turn them on for exploration: 4 steps (2 + 2) and CFG 1, at some cost in motion quality.

**05 — Control video (Wan 2.2 5B Fun Control).** `LoadVideo` → `GetVideoComponents` gives the frames of a control video. `Wan22FunControlToVideo` takes the control frames and a reference image. The control video must already be a control signal: depth, pose, or edges. Make it from your own footage with a preprocessor node (for example the core `Canny` node for edges) or from a 3D layout render (C07·M03).

**06 — Image to video with audio (LTX-2.5).** LTX-2.5 makes video and audio together. The graph loads the parts separately: the distilled transformer (INT8), a video VAE, an audio VAE, and the text encoder. `ResolutionSelector` chooses width and height from an aspect ratio and a megapixel value. The graph runs in two stages:
- Stage 1 samples at half size with a long list of noise levels (`ManualSigmas`).
- `LTXVLatentUpsampler` doubles the latent size.
- Stage 2 refines detail with a short list of noise levels.
`LTXVImgToVideoInplace` places the start image in both stages. `LTXVConcatAVLatent` and `LTXVSeparateAVLatent` join and split the video and audio latents around each sampler. `LTXVDualCFGGuider` has separate guidance values for video and audio.

## Worked example

**Task:** plan VRAM and time for the four video graphs before you rent a GPU.

Step 1: add up the weight files from `models.lock.json`:

| Workflow | Large files | Sum of weights |
|---|---|---|
| 03 Wan 5B I2V | model 10.0 GB (FP16) + text encoder 6.7 GB (FP8) + VAE 1.4 GB | 18.1 GB |
| 04 Wan 14B FLF2V | 2 experts × 14.3 GB (FP8) + text encoder 6.7 GB + VAE 0.25 GB | 35.6 GB on disk; about 21 GB in VRAM at one time |
| 05 Wan 5B control | 10.0 + 6.7 + 1.4 GB | 18.1 GB |
| 06 LTX-2.5 I2V | transformer 21.5 GB (INT8) + text encoder 15.4 GB (INT8) + 2 VAEs 1.8 GB + upscaler 1.0 GB + prompt-enhance LLM 5.2 GB (optional) | 44.9 GB |

Step 2: compare with the GPU. The text encoder runs once, at the start. ComfyUI can move it out of VRAM before sampling. The two Wan 14B experts run one after the other, so only one must be in VRAM. Activations come on top of weights.

Step 3: decide:
- **24 GB GPU:** 03 and 05 run. The Wan team states that the 5B model makes a 5 s 720p clip on a 24 GB GPU in under 9 minutes. The ComfyUI docs state that the 5B model fits in 8 GB with ComfyUI offloading, more slowly. 04 runs with offloading, slowly.
- **32 GB GPU:** 03, 04, 05 run well. 06 runs with offloading of the text encoder.
- **48–80 GB GPU:** all four run without offloading. Rent one for a batch day of 06 renders.

Step 4: the token check for 03: 27,280 tokens. For an exploration pass at 640 × 352, the token count is 31 × 11 × 20 = 6,820. That is 4 × fewer tokens, and attention work falls about 16 ×.

## Lab

**Deliverable:** `pipelines/comfy/graphs/` with 4 workflows, `perf.csv`, and a 15 s chained sequence.

1. **Start frame.** Run `02_ref_edit_flux2_klein_4b` with your character sheet image (C04·M03) and a location image. Make 3 start frames for 3 shots of your storyboard.
2. **Image to video.** Run `03_i2v_wan22_5b` from each start frame. Write the motion prompt from your shot list (C02·M06).
3. **First and last frame.** Run `04_flf2v_wan22_14b` between two of your key frames. Run it once at 20 steps and once with the 4-step LoRAs on.
4. **Control.** Record 5 s of yourself doing the action on a phone. Make an edge control video with the `Canny` node (or a depth video). Run `05_v2v_control_wan22_5b` with a start frame as the reference.
5. **Chain.** Make a 15 s sequence from three 5 s clips. Re-anchor the color before clip 3.
6. **Measure.** Run graphs 03 and 04 at 2 sizes. Write each run in `perf.csv`: workflow, size, frames, steps, seed, seconds, peak VRAM, usable (yes/no).
7. **Decide.** Write 5 lines: your exploration settings and your final settings, with the numbers.

Validate each workflow with `validate_workflow.py` before you commit it.

**Result checklist**
- [ ] 4 workflows in Git, UI and API format, validated.
- [ ] `perf.csv` with at least 8 runs, including peak VRAM.
- [ ] The 15 s sequence, with a note on where you re-anchored and why.
- [ ] A settings decision that uses the numbers.

## Model answer

**`perf.csv`** (example from a 32 GB GPU; the shape matters, not the exact numbers):

```
workflow,width,height,frames,steps,seed,seconds,peak_vram_gb,usable
03_i2v_wan22_5b,640,352,121,20,1001,74,14.8,yes
03_i2v_wan22_5b,640,352,121,20,1002,73,14.8,no (hand warps)
03_i2v_wan22_5b,1280,704,121,20,1001,410,23.9,yes
03_i2v_wan22_5b,1280,704,121,20,1002,412,23.9,no (hand warps)
04_flf2v_wan22_14b,640,640,81,20,7,388,24.6,yes
04_flf2v_wan22_14b,640,640,81,4,7,86,24.6,yes (motion stiffer)
04_flf2v_wan22_14b,640,640,81,20,8,391,24.6,no (morph between frames)
04_flf2v_wan22_14b,640,640,81,4,8,85,24.6,no (morph between frames)
```

**Decision note:**
1. Low-size takes predict the final take: the same 2 seeds were usable and unusable at both sizes.
2. Explore 03 at 640 × 352 (about 74 s). Render finals at 1280 × 704 (about 410 s) only for chosen seeds.
3. For 04, the 4-step LoRAs cut time 4.5 × with stiffer motion. Use them to find seeds. Use 20 steps for finals.
4. Morphs in first/last-frame shots come from frames that are too different. Bring the two key frames closer (same lens, smaller move).
5. Peak VRAM stayed under 25 GB, so a 32 GB GPU is enough for this course. Rent 80 GB only for batch days of LTX renders.

**Chain note:** "Clip 2 ended 150 K warmer than the key frame (measured on a white wall area). I color-matched frame 120 of clip 2 to `KF-S07-v3` before it became the first frame of clip 3. The join is on a head turn, so a cut hides it."
