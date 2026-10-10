---
title: Conditioning, guidance, and control
hours: 9
outcomes:
  - Explain the main types of conditioning (text, image, reference, structure, audio).
  - Explain classifier-free guidance (CFG) and its effect on output.
  - Use seed, steps, CFG, and denoise strength on purpose.
  - Choose a control method for a given production problem.
keywords: [conditioning, CFG, seed, denoise strength, ControlNet, reference]
summary: >
  Conditioning is all the information that guides the denoising: text, images, reference videos, structure maps,
  and audio. Classifier-free guidance, or CFG, makes the model follow the conditioning more strongly. Too low gives
  weak prompt adherence. Too high gives burnt, over-saturated output. The seed fixes the start noise, so you can
  reproduce a result. Denoise strength decides how much of an input image or video the model keeps. Structure
  controls, like depth or pose, fix the layout while the prompt changes the look.
diagram:
  type: layers2d
  title: Control methods and what they fix
  rows: ["Text prompt", "First/last frame", "Reference images", "Structure (depth, pose, edges)", "Input video + denoise"]
  cols: ["Fixes", "Leaves free"]
  cells:
    - ["Subject, action, style (loosely)", "Exact look, layout"]
    - ["Exact start / end composition", "Motion between frames"]
    - ["Identity of character, product, place", "Pose, camera, lighting"]
    - ["Layout, pose, camera geometry", "Materials, style, light"]
    - ["Motion and timing of the source", "Look (at high denoise)"]
watch:
  - title: "Sander Dieleman — Guidance: a cheat code for diffusion models (blog)"
    url: https://sander.ai/2022/05/26/guidance.html
    note: "Read the first half. The clearest explanation of CFG."
  - title: "ComfyUI docs — ControlNet tutorial"
    url: https://docs.comfy.org/tutorials/controlnet/controlnet
    note: "Look at the example images for depth, pose, and canny control."
quiz:
  - q: "CFG is set very high (for example 15 on a model that expects 4). Typical result?"
    options: ["Softer, more natural image", "Over-saturated, high-contrast, 'burnt' output with artifacts", "Lower resolution", "Different aspect ratio"]
    answer: 1
    explain: "High guidance pushes the output too far toward the condition. Distilled and flow models often need low CFG (1–5)."
  - q: "You want the motion of a real dance video but a new character and style. Best control?"
    options: ["Text prompt only", "Pose (skeleton) control from the source video, plus a character reference", "Higher CFG", "A new seed"]
    answer: 1
    explain: "Pose control fixes the motion; the reference fixes identity; the prompt sets style."
  - q: "Video-to-video with denoise strength 0.3. What happens?"
    options: ["Almost a new video", "The source is mostly kept; small style changes", "The video becomes black", "The audio changes only"]
    answer: 1
    explain: "Low denoise keeps most of the input. High denoise (0.7–1.0) keeps little more than the rough motion."
  - q: "Why does a producer log the seed for every chosen shot?"
    options: ["To bill the client", "To reproduce or vary the shot later", "It is required by law", "To set the frame rate"]
    answer: 1
    explain: "Same seed + same settings = same start noise. You can re-render at higher steps, or make small variations."
  - q: "A depth control makes the room geometry right, but the walls get a noisy, bumpy surface. What do you change first?"
    options: ["More CFG", "End the depth control earlier (for example at 50–60 % of the steps) or lower its strength, so that late steps can make clean detail", "A new seed only", "A longer prompt"]
    answer: 1
    explain: "Early steps fix the layout; late steps make detail. Controls active to the end force their errors into the detail."
  - q: "The reference image shows a red jacket; the prompt says 'blue jacket'. The result mixes both. What is the rule?"
    options: ["Add both colors", "Choose one master for each property (here, the reference for wardrobe) and remove the conflicting words from the prompt", "Raise CFG", "Use more steps"]
    answer: 1
    explain: "Conflicting conditions give mixed results or artifacts. Decide which input controls which property."
deeper:
  - title: "Ho & Salimans (2022) — Classifier-Free Diffusion Guidance"
    url: https://arxiv.org/abs/2207.12598
  - title: "Zhang et al. (2023) — Adding Conditional Control to Text-to-Image Diffusion Models (ControlNet)"
    url: https://arxiv.org/abs/2302.05543
  - title: "Ye et al. (2023) — IP-Adapter: Text Compatible Image Prompt Adapter"
    url: https://arxiv.org/abs/2308.06721
---
## Learn

### Conditioning
**Conditioning** is all the information that guides the denoising. In 2026, a video model can take many types at the same time:
- **Text:** the prompt.
- **Frames:** a first frame, a last frame, or key frames in the middle.
- **References:** images or short videos of a character, product, place, or style. Some current models accept dozens of references.
- **Structure:** depth maps, pose skeletons, edge maps, camera paths, or a 3D "white box" scene.
- **Audio:** speech or music that the video must follow.
- **Input video:** for video-to-video edits.

Each type fixes some things and leaves others free (see the diagram). Good direction is the right combination: the fewest conditions that fix what the shot needs, and nothing more.

### Classifier-free guidance (CFG)
During training, the model sometimes sees no prompt. So it learns two predictions: with the condition, and without it. At generation time, **CFG** takes the difference between them and multiplies it:

`output = unconditional + CFG × (conditional − unconditional)`

- CFG near 1: weak adherence, natural but may ignore the prompt.
- CFG in the model's normal range: good balance.
- CFG too high: over-saturated, high contrast, artifacts.

CFG doubles the compute per step (two predictions). Distilled models often bake guidance in and use CFG = 1. The **negative prompt** is the "unconditional" side. It works only when CFG > 1.

### Seed and steps
- The **seed** fixes the start noise. Log it for every shot you keep, with all other settings and the model version.
- More **steps**: more detail, more time (M03).

### Denoise strength
For image-to-image and video-to-video, you do not start from pure noise. You add noise to your input up to a level, and then denoise. That level is the **denoise strength**.
- 0.2–0.4: keep structure and most detail; change grade or style a little.
- 0.5–0.7: keep layout and motion; change materials and look.
- 0.8–1.0: keep only rough motion; new content.

### Strength and timing of a control
Structure controls (depth, pose, edges) usually have two settings:
- **strength:** how much the control pushes the result (for example 0.4–1.0);
- **start and end:** the part of the steps where it is active (for example from 0 % to 60 % of the steps).
Because early steps set the composition (M03), a control that is active only in the first half fixes the layout and leaves the detail free. A control that is active to the end can force its own errors into the detail: a noisy depth map makes noisy surfaces.

### When conditions conflict
Conditions can disagree: the prompt says "a woman with short hair", the reference shows long hair; the first frame is daylight, the prompt says "night". The model then follows one, mixes them, or makes artifacts. Rules:
- Decide which condition is the master for each property (identity → reference; layout → structure or first frame; light and mood → prompt).
- Remove words from the prompt that disagree with the master conditions.
- Add one condition at a time, and test after each.

### Choose a control method
| Problem | Control |
|---|---|
| Same character in every shot | Reference images or a character LoRA (C14) |
| Exact start and end of a shot | First/last frame |
| Exact camera move | Camera-path control, or 3D layout (C07) |
| Copy motion from a performance | Pose or video reference |
| Restyle real footage | Video-to-video + depth/edge control |
| Product must not change shape | Product references + structure control + low denoise |

## Worked example

**Task:** A sneaker ad. The shoe must stay exactly the same. The background and light change in each shot.

1. Make a product sheet: 6 clean photos of the shoe (front, back, sides, top, 3/4).
2. Shot 1 (hero): image-to-video. Start frame = a composite of the real shoe photo on a generated background. Prompt only the camera move and light: "slow orbit left, soft rim light, dust in the air".
3. Shot 2 (on foot): reference-to-video with all 6 product references + one model reference. Prompt the action.
4. Check every frame for logo and stitching changes. If they drift, reduce motion, shorten the clip, or use first/last frame both from real photos.
5. Log seed, model, CFG, references, and cost for each kept shot.

Lesson: for products, give the model as little freedom as possible on the product, and full freedom on the rest.

## Lab

**Deliverable:** `C01/M05/` with 4 short clips or 4 images per test, plus a report.

Use one model that exposes CFG, seed, and an image input (hosted on fal/Replicate, or ComfyUI).
1. **CFG sweep:** one prompt and seed; CFG at 1, 3, 5, 8, 12. Note the effect.
2. **Denoise sweep:** one input image; denoise 0.2, 0.4, 0.6, 0.8.
3. **Control test:** make a depth map of a photo (any depth estimator, for example Depth Anything). Generate 3 different styles with the same depth control.
4. Write a table: method → what it fixed → what it left free → when you will use it.

**Result checklist**
- [ ] Three labeled contact sheets.
- [ ] The table has at least 5 rows.
- [ ] All runs in the prompt log.

## Model answer

- CFG 1: soft, low saturation, the "neon" in the prompt is weak. CFG 3–5: best. CFG 8: higher contrast. CFG 12: burnt highlights, color banding, and repeated patterns.
- Denoise 0.2: almost the input. 0.4: new grade and texture, same layout. 0.6: new materials, same layout. 0.8: same rough composition only.
- Depth control kept the room geometry and camera in all 3 styles; materials and light changed freely.
- Use: depth for restyling a real location; pose for performances; references for identity; first/last frame for exact transitions.
- Depth control active only for the first 60 % of steps gave the same geometry with cleaner surfaces than control to the end.

A strong report states the settings next to each observation, so that another person can repeat the test and see the same effect.
