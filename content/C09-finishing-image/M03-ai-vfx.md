---
title: AI masks, relighting, cleanup, and compositing
hours: 15
outcomes:
  - Make AI masks and roto for people and objects, and refine edges (hair, motion blur).
  - Remove objects and defects from shots, and check edges, shadows, and flicker.
  - Relight shots with AI, and integrate generated elements into plates (levels, color, light, blur, grain).
  - Restore exact brand elements - track an area, composite the source pixels back, and grade the patch to the shot.
  - Measure a fix (sharpness, difference to the source) instead of judging it only by eye.
keywords: [roto, matte, compositing, relight, planar tracking]
summary: >
  AI masks follow a person or an object through a shot from one click, and give a matte for grading, cleanup, or
  compositing. Video inpainting removes objects and repairs short defects. AI relight changes the light on faces and
  simple scenes. Compositing joins layers; integration makes them belong together: matching black levels, color,
  light direction, blur, grain, and shadows. When generation or an AI edit changes an exact element such as a logo,
  track the area and composite the exact source pixels back, then grade the patch to the shot.
diagram:
  type: flow
  title: Restore an exact element
  nodes: ["AI edit is good, logo is soft", "Track the logo area in the source", "Composite source pixels onto the edit", "Feather the edge", "Grade the patch to the shot", "Measure: sharpness + difference"]
  highlight: [4]
watch:
  - title: "Meta — SAM 2: Segment Anything in Images and Videos (GitHub, with demo links)"
    url: https://github.com/facebookresearch/sam2
    note: "Look at the video demos of masks that follow objects."
  - title: "Foundry — Nuke learning (free tutorials)"
    url: https://learn.foundry.com/nuke
    note: "Do one introduction to compositing tutorial."
quiz:
  - q: "An AI mask of a person looks clean on one frame, but the hair edge flickers in playback. What do you do?"
    options: ["Accept it", "Refine the edge (soften or use a hair-detail mode), check at 100 % in playback, and if it still flickers, use the mask only where the edge does not show (or blur the correction at the edge)", "Use a larger mask", "Lower the resolution"]
    answer: 1
    explain: "Masks are judged in motion. Edges that change from frame to frame show as flicker."
  - q: "After an object removal, the object's shadow is still on the floor. What is the rule?"
    options: ["Shadows do not matter", "Remove everything the object caused: its shadow, reflection, and any light it blocked; check the area in playback", "Darken the whole frame", "Add a new object"]
    answer: 1
    explain: "Viewers notice a shadow without a cause. Removal includes the object's effects on the scene."
  - q: "You composite a generated bird into a real sky plate. It looks pasted on. What do you check, in order?"
    options: ["Only the size", "Black level and contrast, color temperature, light direction, edge sharpness and motion blur, grain, and atmosphere (haze with distance)", "The file format", "Only the color"]
    answer: 1
    explain: "Integration means matching every property that the camera gave the plate."
  - q: "An AI relight made the shot golden-hour and softened the bottle logo. What is the exact fix?"
    options: ["Relight again", "Track the logo area in the source, composite the source pixels onto the relit shot with a feathered edge, and grade the patch to the new light", "Sharpen the whole shot", "Regenerate"]
    answer: 1
    explain: "The relight is good; only the logo needs the exact pixels. In the module test, sharpness in the logo area went from 11.9 to 1,642.7 (Laplacian variance)."
  - q: "The restored, ungraded patch shows a visible cool square on a warm relit shot. Why, and what is the fix?"
    options: ["The tracker failed", "The patch keeps the source color, and the shot was warmed; match the patch's color to the area around it (grade the patch), then check the edge", "The feather is too large", "The codec"]
    answer: 1
    explain: "A patch must look like the shot around it, not like the source. Grade it."
  - q: "When do you use a planar tracker instead of a point tracker?"
    options: ["Never", "When the element is on a flat surface that moves in perspective (a bus side, a sign, a screen): the planar tracker follows position, scale, rotation, and perspective", "For faces", "For audio"]
    answer: 1
    explain: "A corner pin on a planar track keeps a logo glued to a surface in perspective."
  - q: "How do you prove that a restored logo is exact?"
    options: ["Ask the client", "Measure the difference between the patch area and the source (it should be near the encode noise), and check sharpness in the area against the source", "Look once", "Check the file size"]
    answer: 1
    explain: "A number is evidence for a client: the patch matches the source within encode noise."
deeper:
  - title: "Ravi et al. (2024) — SAM 2: Segment Anything in Images and Videos"
    url: https://arxiv.org/abs/2408.00714
  - title: "Brinkmann — The Art and Science of Digital Compositing (book)"
    url: https://www.elsevier.com/books/the-art-and-science-of-digital-compositing/brinkmann/978-0-12-370638-6
  - title: "OpenCV — template matching tutorial"
    url: https://docs.opencv.org/4.x/d4/dc6/tutorial_py_template_matching.html
---
## Learn

### Mattes and masks
A **matte** (or alpha) says, for each pixel, how much of a layer is visible: 1 = fully, 0 = not, values between for soft edges (hair, motion blur, smoke). A **mask** in grading limits a correction to an area. Making a matte frame by frame by hand is called **roto** (rotoscoping), and it is slow.

AI masks changed this. You click or draw a box on the subject in one frame. A segmentation model finds the object and follows it through the shot. Then you refine:
1. Check the edges at 100 % in playback, not on a still.
2. Hair and motion blur: use the tool's edge or detail mode, or soften the edge.
3. Fix the frames where the mask jumps (occlusions, fast turns) with an extra click on that frame.

### Cleanup
Video inpainting removes objects and repairs short defects: a wrong hand for 8 frames, a boom microphone, a sign. The model fills the area from the frames around it and from what it learned. Check:
- **edges** of the filled area at 100 %;
- **effects** of the removed object: its shadow, its reflection, light it blocked;
- **flicker:** the filled area must be stable over time;
- **the measurement:** outside the area, nothing may change (`clip_diff.py`, C05·M05).

### Relighting
AI relight tools change the light on faces and simple scenes: add a key from the left, make it warmer, add a rim. Use them to match a shot to its scene or to the look bible. They redraw the frame, so small exact details (text, logos) can soften. Check those areas after each relight.

### Compositing and integration
Compositing joins layers: a **plate** (the background), elements, and mattes. **Integration** makes the layers belong together. Match, in this order:
1. **Black level and contrast:** the darkest areas of the element must not be blacker than the plate's.
2. **Color:** the white balance and the color of the light.
3. **Light direction:** the bright side of the element faces the plate's light.
4. **Sharpness and motion blur:** the same focus and the same blur for the same motion.
5. **Grain:** the same grain on all layers.
6. **Atmosphere:** haze increases with distance.
7. **Contact:** a shadow where the element touches a surface.

### Exact brand elements
Generation and AI edits draw plausible shapes, not exact ones. When a logo, a product label, or text must be exact:
1. **Track** the area. A point or area tracker follows position. A planar tracker follows position, scale, rotation, and perspective on a flat surface.
2. **Composite** the exact pixels: the real logo file (corner-pinned to the track), or the area from the source clip if the source had it right.
3. **Feather** the edge of the patch.
4. **Grade** the patch to the shot: after a relight, the source pixels have the old light, so match their color to the area around them.
5. **Add** the same blur and grain as the shot.
6. **Measure:** the difference between the patch area and the source should be near the encode noise (before grading), and the sharpness in the area should match the source.

## Tool walkthrough

### Restore a soft logo from the source (scripted)

```bash
python starter/tools/patch_restore.py --src source.mp4 --edit relit.mp4 --box 226,336,274,384 \
  --out relit_fixed.mp4 --feather 6 --grade
```

`--box` is the logo area in the first frame (find it on a still with a grid). The tool tracks the area through the source by template matching, composites the source pixels onto the edit with a feathered edge, and with `--grade` shifts the patch color to match the edit around it. Both clips must have the same size and length. For perspective moves, use a planar tracker in your compositing tool.

### Tools (as of 2026-10)
- **AI masks:** DaVinci Resolve Magic Mask, After Effects Roto Brush, Nuke and Fusion AI roto, SAM 2-based tools.
- **Cleanup:** Resolve object removal, After Effects content-aware fill, Runway Aleph and other edit models (C05·M05).
- **Relight:** Resolve Relight, Aleph relight.
- **Planar tracking and corner pins:** Mocha, the Resolve planar tracker, Nuke.

### Measure sharpness

```python
import cv2
g = cv2.cvtColor(cv2.imread("frame.png"), cv2.COLOR_BGR2GRAY)[y0:y1, x0:x1]
print(cv2.Laplacian(g, cv2.CV_64F).var())   # higher = sharper; compare the same area in source and fix
```

## Worked example

**Logo restore test** (2026-10-04). Source: a 4 s clip in which a portrait moves 200 px/s across the frame. "AI edit": the same clip warmed (red ×1.08, blue ×0.9) and softened (blur σ 6), standing in for a relight that softened detail. The task: restore the NASA logo on the suit.

| Measurement | Result |
|---|---|
| Track | from (226, 336) to (1016, 336) in 96 frames; largest step 10 px per frame; matches the 200 px/s motion |
| Sharpness in the logo area at 3.5 s, edit | 11.9 (Laplacian variance) |
| Sharpness in the logo area, after restore | 1,642.7 |
| Patch vs source, ungraded | mean difference 4.5 (encode noise and the feathered edge) |

By eye, the ungraded patch was a visibly cooler square on the warm edit. With `--grade`, the patch took the warmth of the area around it and the square disappeared (its difference to the source rose to 15.9, as expected, because it is now warmer).

**Street shot, 5 s:** (1) a wrong logo on a bus; (2) a deformed hand in the foreground for 8 frames; (3) the scene must be warmer.
1. Planar-track the bus side; corner-pin the correct logo file; add motion blur and grain.
2. AI-mask the hand; inpaint the 8 frames; check 3 times at 100 % in playback.
3. Relight warmer from the left to match the scene; check the logo again after the relight.
Time: about 35 minutes. Regeneration had failed 4 times on the logo.

## Lab

**Deliverable:** `C09/M03/` with 3 fixed shots, before/after files, and a fix log with measurements.

1. **Mask and grade:** AI-mask a person in one shot. Grade the background separately (darker, cooler). Check the edge in playback.
2. **Cleanup:** remove one object or defect from a shot (with its shadow or reflection). Measure the outside area with `clip_diff.py`.
3. **Integrate:** composite one generated element (a bird, a sign, a vehicle) into a plate. Match the 7 integration points. Show the layers before and after integration.
4. **Restore:** make an AI relight or restyle of a shot with a logo or text. Restore the exact element (`patch_restore.py` or a planar track and corner pin). Grade the patch. Measure sharpness and difference.
5. Write a fix log: shot, problem, method, measurement, time.

**Result checklist**
- [ ] 3 fixed shots with before/after.
- [ ] Integration shown step by step.
- [ ] Restore measured: track, sharpness, difference.
- [ ] Fix log with times.

## Model answer

**Fix log (shape of a strong answer):**

| Shot | Problem | Method | Measurement | Time |
|---|---|---|---|---|
| S04 | Background too bright for the night look | AI mask on Mara; −0.8 stop and cooler on the background | Edge flicker at the hair on 5 frames → edge softened 2 px | 12 min |
| S09 | Cyclist in the background | Video inpainting + shadow removal | `clip_diff` outside the box: PASS, worst outside mean 1.6 | 9 min |
| S12 | Generated drone over a real street plate | 7-point integration; contact shadow not needed (in the air); haze +8 % | — | 25 min |
| S14 | Relight softened the camera brand name | `patch_restore.py --grade`, feather 6 | Sharpness 14 → 1,380; ungraded square removed by --grade | 6 min |

"The most useful habit was to measure the area outside every fix. The inpaint in S09 was clean by eye but changed 2 % of the frame on the first try; the second try with a smaller mask passed."
