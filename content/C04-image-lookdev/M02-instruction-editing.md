---
title: Instruction editing, inpainting, outpainting, upscaling
hours: 9
outcomes:
  - Edit images with one-change instructions that name what must not change.
  - Use masks for local fixes, and extend the canvas for a second aspect ratio.
  - Measure what an edit changed outside the target area, and reject edits that drift.
  - Choose between non-generative and generative upscaling, and protect text, logos, and faces.
keywords: [instruction editing, inpainting, outpainting, upscaling, mask]
summary: >
  Modern image models edit by instruction: remove the cup, make it night, change the jacket to red. Good models keep
  everything else the same, but not always, so measure. Inpainting changes only a masked area. Outpainting extends the
  canvas, for example to make a vertical version. Upscalers add resolution; generative upscalers also invent detail,
  so protect faces, text, and logos. An edit is often cheaper and more exact than a new generation, because it keeps
  what was already approved.
diagram:
  type: flow
  title: Fix, do not regenerate
  nodes: ["Key frame, 80 % right", "Instruction edit: one change, name what stays", "Mask + inpaint: local fix", "Measure: change outside the target", "Outpaint: second aspect ratio", "Upscale; protect text, logos, faces"]
  highlight: [3]
watch:
  - title: "Google — Gemini image editing (multi-turn) examples"
    url: https://ai.google.dev/gemini-api/docs/image-generation
    note: "Look at the editing and multi-turn examples. Note how each instruction names one change."
  - title: "Brooks et al. — InstructPix2Pix (project code and examples)"
    url: https://github.com/timothybrooks/instruct-pix2pix
    note: "The research origin of instruction editing. Look at the example pairs."
quiz:
  - q: "You must change three things in an approved frame: the jacket color, the time on the wall clock, and a cup on the table. How do you edit?"
    options: ["One instruction with all three changes", "Three edits, one change each, and a measurement after each edit", "Regenerate from text with the new details", "Upscale first"]
    answer: 1
    explain: "One change per call is followed more exactly and is easy to review. If edit 2 drifts, you go back one step, not three."
  - q: "After an edit, the target object is correct, and the measurement shows saturation +4.3 outside the target area. What happened, and what do you do?"
    options: ["Nothing; 4 is small", "The model shifted the color of the whole frame; redo the edit with a mask, or composite only the target area back onto the original", "Raise the tolerance", "Upscale the image"]
    answer: 1
    explain: "A global shift breaks continuity with neighboring shots. A mask limits the change. A composite keeps the original pixels outside the target exactly."
  - q: "You need a 9:16 version of a perfect 16:9 frame of a person at the table. What is the best method?"
    options: ["Crop the center", "Extend the canvas at the top and bottom, then check the subject size; if she is too small, recompose with a new generation from the same references", "Stretch it", "Generate 9:16 from text only"]
    answer: 1
    explain: "Outpainting keeps the subject. But vertical framing often needs the subject larger, so check composition (C02·M01)."
  - q: "A generative upscaler changed '27' on a locker door to '21'. Why, and what is the fix?"
    options: ["File error", "Generative upscalers invent detail that looks plausible; mask the number and restore it from the original, or use a non-generative upscaler for that area", "Wrong color space", "Too few steps"]
    answer: 1
    explain: "A generative upscaler draws new detail. For text, logos, and real faces, protect the area or use a method that does not invent."
  - q: "After 6 multi-turn edits, the image is soft and the colors are flat. What is the cause and the fix?"
    options: ["The model is broken", "Each edit re-encodes and re-generates the image, and small losses add up; go back to the best version and apply the remaining edits from there, or use masks", "Use more turns", "Lower the resolution"]
    answer: 1
    explain: "Edit chains drift. Keep a version history (log parent IDs) and restart from a strong version."
  - q: "When is a mask better than an instruction edit?"
    options: ["Never", "When the change must stay inside a known area and the rest must stay exact, for example a hand fix or a sign", "When you want a new style", "When the image is small"]
    answer: 1
    explain: "A mask is a hard limit. An instruction is a request that a model can over-apply."
  - q: "A JPEG re-save at quality 90 gives a mean difference of 0.8 and no color shift. A real edit gives mean 0.8 and saturation +4. Why does the checker fail only the edit?"
    options: ["It checks the file name", "It also checks signed shifts (per channel, saturation, brightness); compression noise averages out to about 0, a real color drift does not", "It is random", "It checks file size"]
    answer: 1
    explain: "Mean absolute difference cannot separate noise from drift. Signed mean shifts can."
deeper:
  - title: "Brooks et al. (2022) — InstructPix2Pix: Learning to Follow Image Editing Instructions"
    url: https://arxiv.org/abs/2211.09800
  - title: "Real-ESRGAN (non-diffusion upscaler, open source)"
    url: https://github.com/xinntao/Real-ESRGAN
  - title: "Wang et al. — Real-ESRGAN paper"
    url: https://arxiv.org/abs/2107.10833
---
## Learn

### Why edit
A generated key frame is often 80 % right. A new generation can fix the last 20 % and break the 80 %. An edit keeps the approved parts and changes one thing. It is usually faster, cheaper, and easier to review. Treat edits like code changes: one change at a time, with a check after each change.

### Instruction editing
An instruction edit takes an image and a text instruction and returns a new image. The model was trained on pairs of images that differ by one described change. So it works best when you describe one change.

Write instructions like a retoucher's notes:
- **One change per instruction.** "Change the jacket to deep red wool."
- **Name what must stay.** "Keep her face, pose, hair, and the background unchanged."
- **Be concrete.** "Deep red wool, same cut" works better than "make it pop".
- **Name the place in the frame** when there are several similar objects. "The cup on the left side of the table."

### Edit chains drift
Multi-turn editing is convenient. But each turn decodes and re-generates the image. Small losses add up: detail gets softer, color shifts, and faces change a little. After 3–5 turns, compare with the original. If quality fell, go back to the best version and continue from there. Log each edit with a `parent` ID, so the history is clear.

### Inpainting
A **mask** marks the area that may change. Only the masked area is generated again. The model sees the rest of the image, so the new area matches the light and perspective. Use masks for:
- removing an object;
- fixing hands, eyes, or teeth;
- fixing or adding text;
- replacing a generated product with the real product photo.

Make the mask a little larger than the object, and soften (feather) its edge by a few pixels. A hard edge can show a seam.

### Measure what changed
Do not trust your eyes alone. A color shift of a few values is hard to see in one frame, and easy to see when two shots cut together. Measure each edit:
1. Mark the area that should change (a box or a mask).
2. Compare before and after outside that area.
3. Look at three numbers: the share of pixels that changed, the mean absolute difference, and the signed shift of each color channel, of saturation, and of brightness.

The signed shift is important. Compression noise moves pixels up and down, so its signed mean is near 0. A real drift moves the whole frame in one direction, for example warmer or more saturated. `starter/tools/frame_diff.py` reports all of these and fails the edit if the outside area drifted.

If an edit drifts outside the target, you have two fixes:
- redo it with a mask;
- composite: take only the target area from the edit and paste it onto the original.

### Outpainting and reframing
**Outpainting** extends the canvas and generates the new area. Use it to make a 9:16 version from 16:9, or to add headroom. After the extension, check the composition again (C02·M01). A vertical frame usually needs the subject larger. If the subject becomes too small, generate the vertical frame again from the same references instead.

Outpainting has typical faults: repeated patterns at the edges, a second copy of an object, and lines that do not continue correctly (walls, tables). Check the joins.

### Upscaling
Two kinds of upscalers exist:
- **Non-generative upscalers** sharpen and enlarge what is there. They cannot invent a wrong letter. They look softer.
- **Generative upscalers** use a diffusion model to add detail. They look sharper, with skin texture and fabric. They also invent: pores, threads, and sometimes wrong letters, numbers, or facial features.

Rules:
1. Upscale only approved frames.
2. For text, logos, and real people, protect the area with a mask, or restore it from a non-generative upscale.
3. Check at 200 % zoom.
For video, you usually upscale the video, not the key frame (C09·M04). Upscale key frames for posters, thumbnails, and print.

## Tool walkthrough

### Instruction edit with an image API
Use the same call as in M01, with the approved frame as the input image and the instruction as the text. Example instruction for shot S07:

```text
Make the fluorescent top light colder (more blue). Keep the woman's face, hair, raincoat,
pose, the photo in her hand, and the room exactly as they are.
```

### Mask edit in ComfyUI (open path)
In the ComfyUI editor, right-click a Load Image node and open the mask editor. Paint the area, save, and connect the MASK output to an inpaint-capable graph. The official templates include image-edit and inpaint graphs for current open models. For a hand fix, make the mask about 20 % larger than the hand.

### Measure the edit

```bash
python starter/tools/frame_diff.py KF-S07-v2.png KF-S07-v3.png --box 410,620,690,980 --heatmap diff_S07.png
```

Open `diff_S07.png`: bright areas changed. If the heatmap shows changes far from the box, read the shift numbers.

### Non-generative upscale with ffmpeg
For a safe ×2 reference version: `ffmpeg -i in.png -vf scale=iw*2:ih*2:flags=lanczos out_x2.png`. Compare it with a generative upscale at 200 % zoom.

## Worked example

**Calibrate the checker.** We tested `frame_diff.py` on a 960 × 1200 portrait (2026-10-04). The "allowed area" was a 220 × 220 box:

| After image | Mean abs. diff outside | Saturation shift | Result |
|---|---|---|---|
| JPEG re-save, quality 90 | 0.81 | −1.21 | PASS |
| Local edit inside the box only | 0.00 | 0.00 | PASS |
| Local edit + saturation +15 % everywhere | 0.79 | +4.26 | FAIL |
| Warm shift (red +6, blue −6) | 3.52 | +60.98 | FAIL |
| JPEG re-save, quality 75 | 2.73 | −0.86 | FAIL (3.8 % of pixels changed) |

The mean difference is almost the same for the quality-90 save and the saturation drift (0.81 and 0.79). Only the signed shifts separate them. Also, heavy compression fails the check. So save edit results as PNG.

**Fix plan for `KF-S07-v3`:**
1. The photo in her hand must show a wet locker. Mask the photo area; instruction "a small printed photo of a wet metal locker, slightly blurred". Outside change: 0.2 % of pixels. ✓
2. A 16:9 version for the trailer: extend left and right. A second locker door appears in the wrong color. Instruction edit "make the new locker door the same grey as the others". ✓
3. A 4K poster version: generative ×2 upscale. The locker number "27" became "21". Mask the number and restore it from the lanczos upscale. ✓

## Lab

**Deliverable:** `C04/M02/` with before/after pairs, diff reports, and a fix decision table.

1. Choose 3 key frames from M01 that each have a real problem.
2. For each frame, do one instruction edit, one mask edit, and one canvas extension to a second aspect ratio.
3. Measure every edit with `frame_diff.py`. Save the JSON report and the heatmap. Redo any edit that fails.
4. Upscale one frame twice: non-generative and generative. Compare text, faces, and fabric at 200 % zoom. Write what the generative upscaler invented.
5. Log every kept edit with its `parent` ID.
6. Write a fix decision table: problem → method → measured result → cost.

**Result checklist**
- [ ] 9 before/after pairs, each with a diff report.
- [ ] At least one failed edit that you found by measurement, and how you fixed it.
- [ ] Upscale comparison with a list of invented details.
- [ ] Fix decision table with costs.

## Model answer

**Fix decision table (shape of a strong answer):**

| Frame | Problem | Method | Outside change | Result | Cost |
|---|---|---|---|---|---|
| S03 | extra finger | mask + inpaint, mask 20 % larger than the hand | 0.1 %, no shift | ✓ | US$0.04 |
| S03 | cup in wrong hand | instruction edit | 0.3 %, saturation +3.1 | ✗ → redo with mask | US$0.08 |
| S05 | 16:9 needed | canvas extension | n/a (new area) | ✓ after one fix: a doubled lamp at the right edge | US$0.05 |
| S07 | sign text wrong | mask + inpaint with the exact text in quotes | 0.0 % | ✓ on try 2 | US$0.08 |
| S07 | poster 4K | generative ×2 | n/a | number "27" → "21"; restored from lanczos | US$0.02 |

The written summary gives three lessons with evidence:
1. "Instruction edits drifted color in 2 of 6 cases. Masks never did. For approved frames, I now use masks by default."
2. "Canvas extension made repeated objects at the edges in 2 of 3 cases. I check the edges first."
3. "The generative upscaler invented 3 details: a number, a button, and an eyelash pattern. Faces looked better, text looked worse."

The log shows each edit with its parent, so anybody can follow `KF-S07-v1 → v2 → v3`.
