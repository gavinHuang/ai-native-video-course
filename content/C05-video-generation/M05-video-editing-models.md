---
title: Editing video with AI models
hours: 14
outcomes:
  - Use instruction-based video editing to remove, add, replace, relight, and restyle, with one change per run.
  - Use region editing and conversational editing, and control drift across turns.
  - Measure an edit frame by frame against the source, inside and outside the edit region.
  - Decide between an AI edit and classic compositing for each job, with time and quality data.
keywords: [video editing model, region editing, relight, restyle, conversational editing]
summary: >
  Video editing models change an existing clip from an instruction. They can remove an object, add an element,
  change wardrobe, relight a scene, or change the style, and they keep the rest of the clip, mostly. Some models edit
  only a marked region; some edit by conversation. They are strong on generated and real footage, and they still
  fail on small text, exact logos, and long clips. Measure each edit against the source, frame by frame, outside and
  inside the edit region. Use AI edits for organic changes, and compositing for anything that must be exact.
diagram:
  type: flow
  title: AI video edit workflow
  nodes: ["Source clip (generated or real)", "Define change: one instruction, name what stays", "Region / mask if supported", "Edit model run (2–3 tries)", "Measure against the source, frame by frame", "Accept, or fall back to compositing (C09)"]
  highlight: [4]
watch:
  - title: "Adobe Help — generate and edit videos with Runway models in Firefly"
    url: https://helpx.adobe.com/firefly/web/firefly-video-editor/generate-videos/generate-videos-using-runway-video-models.html
    note: "Look at the types of edits and the stated limits."
  - title: "The Next Web — Gemini Omni Flash: conversational video generation and editing"
    url: https://thenextweb.com/news/google-gemini-omni-flash-video-model-io-2026
    note: "Note how each turn keeps characters, and what the article says about watermarks."
quiz:
  - q: "A client wants three changes in one shot: a white helmet, no background cyclist, and golden-hour light. How do you run the edits?"
    options: ["One instruction with all three", "Three runs, one change each, in the order of least global to most global (helmet, removal, then relight), with a check after each", "Regenerate the shot", "Relight first"]
    answer: 1
    explain: "One change per run is followed more exactly. A relight changes the whole frame, so do it last; otherwise later edits must match the new light."
  - q: "After a relight edit, the bottle logo is soft. What is the right fix?"
    options: ["Accept it", "Composite the logo back from the source with a tracked mask, and grade it to the new light", "Relight again with 'sharp logo'", "Upscale the clip"]
    answer: 1
    explain: "Edit models redraw the frame. For brand assets, take the exact pixels from the source (C09·M03)."
  - q: "The frame-by-frame check shows outside-region shifts of +2.8 red and −3.8 blue in every frame, for an edit that should only change a jacket. What happened?"
    options: ["Nothing", "The model also shifted the color of the whole clip; the shot no longer matches its neighbors", "The jacket is too big", "The codec"]
    answer: 1
    explain: "A small global shift is easy to miss on one clip and easy to see at the cut. Use a region edit, or match the grade back to the source (C09·M02)."
  - q: "Which edit type is least reliable with current models?"
    options: ["Color change of a jacket", "Removing a simple object", "Changing small text or an exact logo", "Day to night"]
    answer: 2
    explain: "Text and exact logos need exact pixels. Models draw plausible shapes, not exact ones."
  - q: "In conversational editing, quality drops after 5 turns. Why, and what do you do?"
    options: ["The model gets tired", "Each turn regenerates the clip from the last result, and small losses add up; return to the best version and apply the remaining changes from there", "Use more turns", "Lower the resolution"]
    answer: 1
    explain: "Like image edit chains (C04·M02), video edit chains drift. Keep a version history."
  - q: "You must remove a boom microphone from 40 shots of real footage for a client deadline. Each AI edit takes 3 minutes and works in 70 % of cases. A compositor needs 20 minutes per shot. What is a good plan?"
    options: ["All compositing", "AI edit first for all shots; check each one; send the 30 % failures to compositing", "Only AI edits, accept failures", "Reshoot"]
    answer: 1
    explain: "AI first: 40 × 3 min = 2 h, plus 12 failures × 20 min = 4 h. All compositing: 13 h. Measure each edit before you accept it."
  - q: "Why are long clips (more than 10 s) harder for edit models?"
    options: ["They are bigger files", "The model must keep the change and the rest consistent over more frames, and many models work in windows, so the edit can drift or flicker over time", "Licenses", "Audio"]
    answer: 1
    explain: "Edit the shortest clip that the edit needs. Cut long takes into the parts that the edit uses."
deeper:
  - title: "Runway — Aleph documentation (help center)"
    url: https://help.runwayml.com/hc/en-us
  - title: "Ku et al. — AnyV2V: a tuning-free framework for video editing (research background)"
    url: https://arxiv.org/abs/2403.14468
  - title: "Luma — Ray3 Modify (restyle actor footage)"
    url: https://lumalabs.ai/
---
## Learn

### What an edit model does
A video edit model takes a source clip and an instruction. It makes a new clip that follows the instruction and keeps the rest of the source. Inside, it usually encodes the source into latents and uses them as strong conditioning, while it generates the clip again. So "keep the rest" is a strong preference, not a guarantee. Every pixel of the output is new. That is why measurement matters.

### Types of edits and reliability
| Edit | Reliability (as of 2026-10) | Why |
|---|---|---|
| Color or material change (jacket, car) | High | Shape and motion stay; only appearance changes |
| Remove a simple object | High | The model fills in a plausible background |
| Day to night, relight | Medium–high | The whole frame changes, and shadows must agree |
| Restyle (live action to animation, painting) | Medium–high | Motion is kept; style is global |
| Add a new object with motion | Medium | The object must move and interact correctly |
| Change text, logos, exact product details | Low | Exact pixels are needed; the model draws plausible shapes |
| Long clips (more than 10 s) | Medium–low | Consistency over many frames; windowed processing |

### Method
1. **One change per run.** Name what must stay: "Change the rider's helmet to matte white. Keep the rider, the bike, the bridge, and the light unchanged."
2. **Order the changes** from local to global: object changes and removals first, relight and restyle last. A relight changes every pixel, so later edits would have to match it.
3. **Use a region** (a mask or a box) if the model supports it. It is a hard limit, not a request.
4. **Run 2–3 tries.** Edits vary like generations.
5. **Measure** against the source (below).
6. **Fall back** to compositing after two failures (C09·M03).

### Conversational editing
Some models edit by conversation: each instruction applies to the last result. It is fast for exploration. But each turn regenerates the clip, and small losses add up: detail softens, colors move, faces change a little. Keep a version history, compare each version with the source, and return to the best version when quality drops.

### Measure the edit
Play the source and the edit side by side, at full resolution, on a large screen. Check faces, hands, edges, and the light. Then measure:
- **Inside the region:** did the change happen? The mean difference should be large.
- **Outside the region:** did anything else change? The mean difference should be near the re-encode noise, and the signed color shift should be near 0.
- **Over time:** in which frames? An edit can be clean in the first second and drift later.

`starter/tools/clip_diff.py` samples frames from both clips and reports these numbers per frame, with the worst frame. A small global color shift is easy to miss in one clip and easy to see when the edited shot cuts against its neighbors.

### AI edit or compositing
AI edits are fast, and they handle light, shadows, and reflections well, because the model redraws the scene. Compositing (roto, tracking, paint, keying) is slower, and it is exact and controllable. Rule:
- **AI edit first** for organic changes: wardrobe, removal of simple objects, relight, restyle.
- **Compositing** for brand assets, text, logos, faces of real people, and anything that a client will check pixel by pixel.
- **Hybrid:** an AI relight, plus the exact logo composited back from the source with a tracked mask.

For a batch, calculate both paths: AI edit time × all shots + compositing time × failed shots, against compositing for all shots.

## Tool walkthrough

### Edit models (as of 2026-10)
- **Runway Aleph 2.0** (also inside Adobe Firefly): remove, add, relight, change angle, restyle.
- **Gemini Omni Flash:** conversational edits; each turn keeps characters and physics; SynthID watermark on outputs.
- **Kling 3.0 Omni, Seedance 2.5:** region editing.
- **Wan 2.7 instruction edit** (open weights, Apache 2.0): local editing on your own GPU.
- **Luma Ray3 Modify:** restyles actor footage and keeps the performance.

### Measure an edit

```bash
python starter/tools/clip_diff.py source.mp4 edited.mp4 --box 600,300,900,700 --csv per_frame.csv
```

The box is the area that may change, in source pixels (x0, y0, x1, y1). Find it by opening one frame in an image viewer. The result is PASS or FAIL, the worst frame, and the mean color shift. Open `per_frame.csv` to see when the drift starts.

## Worked example

**Calibrate the clip check** (2026-10-04, a 4 s clip, 480 × 600, 12 sampled frames; the box is the edit area):

| Edited clip | Worst outside mean | Mean shift (R, G, B) | Inside mean | Result |
|---|---|---|---|---|
| Re-encode only (H.264, CRF 23) | 1.48 | (0.1, 0.0, 0.1) | 1.24 | PASS |
| A local change inside the box | 1.48 | (0.1, 0.0, 0.1) | 36.96 | PASS |
| The same local change + a warm shift of 3 % | 3.49 | (+2.8, −0.2, −3.8) | 38.79 | FAIL in all 12 frames |

The warm shift is small: 3 %. The mean difference outside (3.49) stays under the limit of 4.0. Only the signed channel shift catches it.

**Ad shot:** a rider on a bridge, generated, 6 s. Client notes: (1) a white helmet; (2) remove a second cyclist in the background; (3) golden hour.
1. Edit 1: "Change the rider's helmet to matte white; keep everything else." First try. `clip_diff` PASS.
2. Edit 2: "Remove the cyclist in the background on the left." The first try left a shadow; the second try is clean. PASS.
3. Edit 3: "Relight to golden hour, low warm sun from the right." The look is right, but the bottle logo became soft. Fix: composite the logo back from the source with a tracked mask, and grade it warmer (C09·M03). 25 minutes of compositing.

## Lab

**Deliverable:** `C05/M05/` with 6 edits (before and after), `clip_diff` reports, a reliability table, and an AI-versus-compositing comparison.

1. Choose 2 generated clips and 1 real clip that you filmed.
2. Do 6 edits across types: a color change, a removal, a relight, a restyle, an addition, and a text or logo change.
3. Use at least 2 different edit models, one of them open if you have a GPU.
4. Measure every edit with `clip_diff.py`. Save the reports.
5. Record the tries, the result, the defects, and the time for each edit.
6. For the failed text or logo edit, fix it with a classic method (mask, track, composite). Record the time. Compare quality and time with the AI attempts.

**Result checklist**
- [ ] 6 before/after pairs, each with a `clip_diff` report.
- [ ] Reliability table by edit type and model.
- [ ] One AI-versus-compositing comparison with times.
- [ ] A rule for your future projects, based on your data.

## Model answer

**Reliability table (shape of a strong answer):**

| Edit | Model A tries / result | Model B tries / result | Outside drift | Time |
|---|---|---|---|---|
| Jacket color | 1 / ✓ | 1 / ✓ | none | 3 min |
| Remove a cyclist | 2 / ✓ | 1 / shadow left | none | 6 min |
| Relight to night (real footage) | 1 / ✓ | 2 / ✓ | whole frame (expected) | 5 min |
| Restyle to animation (real footage) | 1 / ✓ | 1 / ✓, faces changed | expected | 4 min |
| Add a dog walking past | 3 / legs wrong | 2 / ✓ | +1.9 red in frames 40–72 | 12 min |
| Change the shop sign text | 3 / ✗ | 3 / ✗ | — | 15 min, then compositing 30 min ✓ |

The conclusion is a rule with evidence: "AI edits for organic changes: 5 of 5 succeeded in 1–2 tries. Text: 0 of 6 AI tries. Compositing took 30 minutes and is exact. For client logos and text, I go straight to compositing. I measure every AI edit, because the dog edit shifted the color of 33 frames and I did not see it on my laptop."
