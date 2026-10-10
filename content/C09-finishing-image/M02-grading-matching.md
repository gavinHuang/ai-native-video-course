---
title: Grading with scopes and matching shots
hours: 15
outcomes:
  - Read the waveform, the RGB parade, and the vectorscope, and connect each to what you see.
  - Do a primary correction - levels, white balance, exposure - with scopes, in a fixed order.
  - Match shots from different models to a hero shot, with a measured color difference before and after.
  - Build the project look from the look bible as a separate layer, and apply it consistently.
  - Use secondaries for skin, sky, and brand colors, and check brand colors against their reference values.
keywords: [scopes, waveform, vectorscope, shot matching, LUT, delta E]
summary: >
  Grading starts with measurement. The waveform shows brightness across the frame, the parade shows each color
  channel, and the vectorscope shows hue and saturation. Correct each shot first (levels, white balance, exposure),
  then match all shots of a scene to a hero shot, then apply one look to all of them. A statistical color match can
  produce a 3D LUT as a starting point; measure the result on the applied file, and check skin and blacks by eye.
  Generated shots differ by model in contrast, saturation, sharpness, and grain; remove model looks before you add
  the project look.
diagram:
  type: flow
  title: Grading order
  nodes: ["Correct: levels, white balance, exposure", "Match: every shot to the hero shot", "Look: one layer from the look bible", "Secondaries: skin, sky, brand colors", "Texture: one grain, one sharpness", "Check on scopes + Delta E"]
  highlight: [1]
watch:
  - title: "Blackmagic — The Colorist Guide to DaVinci Resolve (free official book)"
    url: https://www.blackmagicdesign.com/products/davinciresolve/training
    note: "Do the chapters on primaries, scopes, and shot matching."
  - title: "Mixing Light — articles on scopes"
    url: https://mixinglight.com/
    note: "Read one article on reading the vectorscope."
quiz:
  - q: "On the RGB parade, a white wall shows red higher than green and blue. What does the shot look like, and what do you adjust?"
    options: ["Too dark; raise exposure", "Too warm (red cast); balance the channels so the wall is equal in R, G, and B (white balance / gain)", "Too saturated; lower saturation", "Nothing"]
    answer: 1
    explain: "A neutral object has equal channels. Balance on something that should be neutral."
  - q: "Why do you correct and match before you add the look?"
    options: ["It is faster", "The look must act on comparable shots; if shots differ, the same look makes them differ more", "Looks need high saturation", "Scopes need it"]
    answer: 1
    explain: "Correct, match, then look. In a layer structure, the look node is shared and comes after the per-shot nodes."
  - q: "A color match moves the mean color difference from ΔE 14.6 to a predicted 0.0. After you apply the LUT and encode, you measure ΔE 0.9. Is something wrong?"
    options: ["Yes, the LUT is broken", "No: the LUT interpolation, clipping, and the encode add small errors; 0.9 is below what viewers see between shots (about 2)", "The reference is wrong", "Measure again until 0"]
    answer: 1
    explain: "Always measure the applied file. A difference below about 2 is hard to see at a cut."
  - q: "The match LUT made the blacks slightly blue. Why can a statistical match do this, and what do you do?"
    options: ["It cannot", "It moves the mean and spread of each channel for the whole frame; the shadows can get a tint. Check the blacks on the parade, and fix them in a node after the LUT (or lower the strength)", "Delete the shot", "Raise the contrast"]
    answer: 1
    explain: "A statistical match is a starting point, not a grade. Finish with scopes."
  - q: "Where does skin sit on the vectorscope?"
    options: ["At the center", "Near the skin-tone line (about the 11 o'clock direction, between red and yellow), for every skin color; saturation differs, hue stays close", "At blue", "Anywhere"]
    answer: 1
    explain: "Skin hue is similar for all people; brightness and saturation differ. A skin trace far off the line shows a color cast."
  - q: "A model added its own 'cinematic' teal-and-orange grade to a shot. What do you do first?"
    options: ["Add the project look on top", "Undo the model look first (neutral correction), then match and apply the project look", "Leave it", "Raise saturation"]
    answer: 1
    explain: "Two looks on top of each other give a third look that you did not design."
  - q: "How do you check that the product orange matches the brand color #E8662A?"
    options: ["By eye", "Sample the product in the graded frame, convert to Lab, and compute ΔE against the brand value; keep it below the client's tolerance (often about 2–3)", "Ask the model", "Check the file name"]
    answer: 1
    explain: "Brand colors are numbers. Measure them."
deeper:
  - title: "Van Hurkman — Color Correction Handbook (book)"
    url: https://www.pearson.com/en-us/subject-catalog/p/Van-Hurkman-Color-Correction-Handbook-Professional-Techniques-for-Video-and-Cinema-2nd-Edition/P200000000661
  - title: "Reinhard et al. (2001) — Color Transfer between Images"
    url: https://doi.org/10.1109/38.946629
  - title: "Wikipedia — Color difference (Delta E formulas)"
    url: https://en.wikipedia.org/wiki/Color_difference
---
## Learn

### Scopes
Your eyes adapt to every picture, so they are bad at judging color and brightness alone. Scopes measure:
- **Waveform:** the brightness of each column of the frame, from left to right. Low = dark, high = bright. In 8-bit video range, black is near 16 and white near 235 (the scale is often shown as 0–100 %).
- **RGB parade:** the waveform for each channel, side by side. A neutral grey or white object has equal levels in R, G, and B. A higher red means a warm cast.
- **Vectorscope:** hue as the angle, saturation as the distance from the center. Grey is in the center. Skin of all people sits near the skin-tone line (about the 11 o'clock direction); a skin trace far from it shows a cast.
- **Histogram:** how many pixels have each brightness. Pixels piled at the ends are clipped.

### Correct each shot
Use a fixed order:
1. **Levels:** set the black level (the darkest real black near 16, without crushing large areas) and the white level (below 235).
2. **White balance:** find something that should be neutral (a wall, a white shirt, grey concrete). Balance the parade there.
3. **Exposure:** set the midtones for the subject. For faces, a common target is skin in the upper middle of the waveform.

### Match shots to a hero
In each scene, choose a hero shot: the most important and best-looking shot. Match every other shot to it:
- the same black level and white level;
- the same position of skin on the vectorscope;
- a similar contrast and saturation;
- the same color of key objects (the raincoat, the product).

A statistical match can give a starting point: it moves the mean and the spread of each channel of the shot (in a perceptual color space, Lab) toward the hero shot. The result can be stored as a 3D LUT (`.cube`) and loaded in any grading tool. It matches overall balance and contrast. It does not know what is skin or sky. Finish by hand with scopes.

### Measure a match
The color difference ΔE (Delta E) is the distance between two colors in Lab. Below about 2, most people do not see a difference between two shots at a cut. Above about 5, a cut shows a jump. Measure on the applied, encoded file, not on the tool's prediction.

### The look
The look comes from the look bible (C04·M04): a contrast curve, palette shifts (for example warm highlights and cool shadows), saturation, and texture. Build it as one shared layer (a node, a group, or an adjustment layer) after the per-shot correction and match. Then every shot gets exactly the same look. A LUT can store a look; keep the per-shot corrections outside the LUT.

### Secondaries
A secondary adjusts one part of the picture: a color range (qualifier) or a mask. Typical uses:
- skin (a little less saturation, hue toward the skin line);
- sky (more blue, less brightness);
- the product: match its color to the brand value. Measure it: sample the product, compute ΔE against the reference, and stay inside the client's tolerance.

### Generated-shot specifics
- **Model looks:** some models add their own "cinematic" grade. Neutralize it first.
- **Contrast and saturation** differ by model. The correction step removes most of it.
- **Sharpness:** match it with a slight blur or sharpening, so shots from different models cut together.
- **Grain:** remove the model's grain (or noise) where it differs, then add one project grain to all shots.

## Tool walkthrough

### Scopes from the command line

```bash
python starter/tools/scopes.py S08.mp4 --at 1.5 --out S08_scopes.png
```

### A match LUT

```bash
python starter/tools/match_color.py --src S08.mp4 --ref S07_hero.mp4 --out S08_to_S07.cube
ffmpeg -i S08.mp4 -vf lut3d=S08_to_S07.cube -c:v prores_ks -profile:v 3 S08_matched.mov
python starter/tools/match_color.py --src S08_matched.mov --ref S07_hero.mp4 --out check.cube   # read "delta_e_mean_before"
```

Load the `.cube` in your grading tool as a starting node, at reduced strength if needed (`--strength 0.7`).

### In DaVinci Resolve (as of 2026-10)
- Scopes: Workspace → Video Scopes; choose waveform, parade, vectorscope.
- Per-shot correction in the first nodes; a shared look with a Group (pre-clip and post-clip nodes) or an adjustment clip.
- Shot match: right-click a clip in the clip strip → Shot Match to This Clip. A LUT: right-click a node → LUT → choose the `.cube`.

## Worked example

**Match test** (2026-10-04). A reference shot (a portrait) and a version made warm and dark on purpose (red ×1.12, blue ×0.82, brightness −0.06, contrast 0.85). `match_color.py` on one frame of each:

```
"delta_e_mean_before": 14.61,   L mean 43.1 → ref 47.9,  b mean 14.4 → ref 0.6
```

After applying the 33-point LUT with ffmpeg and encoding to H.264, a new measurement of the matched clip against the reference gave ΔE **0.92**. The tool's internal prediction was 0.0; the LUT interpolation and the encode added the rest. 0.92 is below what viewers see at a cut.

One defect: the LUT maps pure black to (0, 0, 0.07), a slight blue lift. Fix: a correction node after the LUT that sets the blacks neutral on the parade.

**Scene of 6 shots from 3 models:**
1. Hero: S03 (model A).
2. S01 (model B): lifted blacks → lower the lift; cyan cast → balance on the parade.
3. S05 (model C): skin too saturated → −15 %; hue rotated toward the skin line.
4. Shared look node: warm highlights, cool shadows, 35 mm grain.
5. Product secondary: the camera body orange measured at ΔE 3.4 from #E8662A → adjusted to ΔE 1.6.

## Lab

**Deliverable:** `C09/M02/` with a graded scene of 6–8 shots, before/after scopes, a match table with ΔE values, and the look as a LUT.

1. Choose a scene with shots from at least 2 models. Choose the hero shot.
2. Correct each shot in the fixed order. Save scope images before and after for 2 shots.
3. Match each shot to the hero. Use `match_color.py` for a starting LUT on at least 2 shots. Measure ΔE on the applied files.
4. Build the look from your look bible as one shared layer. Export it as a LUT.
5. Do one skin secondary and one product or key-color secondary. Measure the key color against its reference value.
6. Export the scene. Watch it at full screen. Note any cut where you still see a jump, and fix it.

**Result checklist**
- [ ] Graded scene exported.
- [ ] Before/after scopes for 2 shots.
- [ ] Match table with ΔE before and after (measured on the applied files).
- [ ] Look LUT; key color within tolerance.

## Model answer

**Match table (shape of a strong answer):**

| Shot | Model | ΔE to hero before | After LUT (strength 0.8) | After hand finish | Note |
|---|---|---|---|---|---|
| S01 | B | 9.8 | 2.4 | 1.1 | blacks re-neutralized after the LUT |
| S02 | A | 3.1 | — | 1.3 | correction only |
| S05 | C | 12.6 | 3.0 | 1.7 | skin hue rotated 4° by hand |
| S06 | C | 11.9 | 2.7 | 1.4 | |

"The LUT got each shot most of the way. The hand finish was needed for the blacks (a blue lift at full strength) and for skin. The cut S04 → S05 still showed a jump in sharpness, not in color: model C is softer. I added a slight sharpening to S05 and S06."

Key color: "Raincoat olive in S01–S06: ΔE 1.2–2.1 against the reference value from the character sheet."
