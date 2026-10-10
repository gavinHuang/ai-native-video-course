---
title: Character, product, and environment sheets
hours: 11
outcomes:
  - Make a character sheet with a turnaround, an expression set, wardrobe variants, and a fixed descriptor sentence.
  - Make a product sheet that protects shape, logo, materials, and exact colors.
  - Make an environment sheet with several angles, light states, a panorama anchor, and a top-view plan.
  - Store references in a library that code can read by ID, with source and rights for every file.
  - Test consistency with references only, and find which details drift.
keywords: [character sheet, turnaround, product sheet, environment sheet, panorama anchor]
summary: >
  Consistency starts with reference sheets. A character sheet shows one person from the front, three-quarter, side,
  and back, with expressions and wardrobe variants, on plain light. A product sheet shows the exact object from all
  sides, with its logo and materials. An environment sheet shows a place from several angles and at several times of
  day; a panorama can anchor the whole space. Every set gets an ID and a sheet file with its descriptor, source, and
  rights. Prompts, pipelines, and logs then point to the same IDs.
diagram:
  type: layers2d
  title: Reference sheets
  rows: ["Character", "Product", "Environment"]
  cols: ["Contents", "Used for"]
  cells:
    - ["Front, 3/4, side, back; 6 expressions; wardrobe A/B; details", "References, LoRA training data (C14)"]
    - ["6 views, logo close-up, material swatches, color values", "Reference-to-video, inserts, QC"]
    - ["Wide, reverse, details; 3 light states; panorama; top plan", "Scene continuity, camera planning"]
watch:
  - title: "Bilibili — Seedance 2.0: 360° panorama control for scene consistency (Chinese)"
    url: https://www.bilibili.com/video/BV1C7QoBZEEk/
    note: "Watch the method: one panorama as the anchor for many shots in the same place."
  - title: "RunComfy — Consistent Character Creator workflow (ComfyUI)"
    url: https://www.runcomfy.com/comfyui-workflows/consistent-character-creator-3-0
    note: "Look at how one workflow makes a full character sheet."
quiz:
  - q: "Your character sheet has only front views. In video, the character turns her head, and her face changes. Why?"
    options: ["The video model is broken", "The model has no information about her profile; it invents one, and each take invents a different one", "The light is wrong", "The frame rate is too low"]
    answer: 1
    explain: "A model can copy only what the references show. Add three-quarter, side, and back views."
  - q: "Why must sheet images have neutral, soft light and a plain background?"
    options: ["They look better", "Strong light and busy backgrounds get copied into every shot; neutral sheets carry identity without a fixed light or place", "They are smaller files", "Models need grey"]
    answer: 1
    explain: "References transfer everything they contain. Keep only what you want to carry: the person, the object, or the place."
  - q: "The side view shows the scar on the right eyebrow. The descriptor says left. What do you do?"
    options: ["Accept it; nobody sees it", "Fix the side view with a mask edit before the sheet is approved; a wrong reference is copied into every later shot", "Change the descriptor to right", "Remove the scar"]
    answer: 1
    explain: "Errors in references multiply. Check every view against the descriptor before you approve the sheet."
  - q: "For a real product ad, which source for the product sheet is best?"
    options: ["A generated product that looks similar", "Real photos of the real product (or the client's CAD renders), with the logo file and exact color values", "A drawing", "Text description only"]
    answer: 1
    explain: "A model must never invent or 'improve' a real product. Use real images and check every output against them."
  - q: "What is the panorama anchor for?"
    options: ["VR delivery", "One consistent source of the whole space, so walls, windows, and props stay in place across many shots", "Sound design", "Color grading"]
    answer: 1
    explain: "A panorama shows the room in all directions. Each shot can take the part it needs from one source."
  - q: "Why does each reference set have an ID like CHAR-MARA and a sheet.json file?"
    options: ["For decoration", "Prompts, pipelines, and logs can point to exact files by ID, and the rights status of each file is recorded", "It makes generation faster", "Platforms require it"]
    answer: 1
    explain: "IDs connect the script tags (C03·M02), prompts, the prompt log, and the rights log (C16)."
  - q: "In the consistency test, the face scores 4/5 but the brass buttons change shape in every shot. What is the next step?"
    options: ["Ignore buttons", "Add a close-up reference of the buttons to the sheet and name it in the prompt; if it still drifts, the character needs a LoRA (C14)", "Change the coat", "Lower the resolution"]
    answer: 1
    explain: "Small details drift first. A detail reference often fixes it. A LoRA is the stronger fix."
deeper:
  - title: "Runflow — ComfyUI consistent characters with FLUX (2026 guide)"
    url: https://www.runflow.io/blog/comfyui-consistent-characters-flux
  - title: "Tencent Cloud — AI comic-drama industrial pipeline (character libraries, Chinese)"
    url: https://cloud.tencent.com/developer/article/2647810
---
## Learn

### Why sheets
A model keeps a character, a product, or a place the same only when it gets the same information every time. Words are not exact enough. "Short black hair" gives a different haircut in every shot. A reference sheet is the exact information, made once, approved once, and used in every shot.

Think of a sheet as a fixed dependency. Every key frame depends on it. If a sheet has an error, every shot gets the error.

### Character sheet
Contents:
- **Turnaround:** front, three-quarter, side, and back, full body and head. Same light, same plain background, same scale.
- **Expressions:** neutral, happy, sad, angry, surprised, and thinking. Close-ups, front view.
- **Wardrobe variants:** A, B, C. Each as a full-body front view.
- **Details:** hands, a unique mark (scar, tattoo), jewelry, buttons, glasses. Close-ups.
- **Descriptor sentence:** one fixed sentence that every prompt uses, word for word. Example: "Mara, early 30s, short black bob, small scar through the left eyebrow, olive raincoat with brass buttons."
- **Voice ID** for audio (C06·M01), and height and age for consistency of scale.

Use neutral, soft light and a plain mid-grey background. A sheet with dramatic light teaches every shot that light. A sheet in a kitchen puts kitchen details in every shot.

### How to make a character sheet
1. Generate one strong front portrait. Approve it carefully. It is the root of all other views.
2. Generate each other view with the front portrait as the reference: "The same woman as image 1. Full body, side view, facing left. Same clothes, same light, plain grey background."
3. Check each view against the descriptor and the front: the mark on the correct side, the same hairline, the same buttons. Fix errors with a mask edit (M02).
4. Generate the expressions from the front portrait.
5. Generate the wardrobe variants. Then generate one view of each variant in the other views if the story needs it.

Short-drama studios keep a large expression library per character, because emotion close-ups are a large part of their shots. Make the expressions that your story needs.

### Product sheet
A real product must never be invented or "improved". Use real photos of the product, or the client's CAD renders. If you generate a product (a fictional one), generate it once, approve it, and freeze it.

Contents:
- 6 views: front, back, left, right, top, and three-quarter;
- a logo close-up and the logo vector file;
- material swatches: matte, gloss, metal, glass;
- exact color values (hex, or the brand's spot colors);
- do-not rules from the brand guide: no tilted logo, no other colors.

### Environment sheet
- **Angles:** a wide establishing view, a reverse view, and 3–4 detail views (door, window, the main prop).
- **Light states:** the same place at 3 times or moods, for example day, night, and night with emergency light. This is your light plan (C02·M03).
- **Panorama:** a 360° image of the space. Make it with a model that supports panoramas, or stitch it from several views. It anchors the layout. Each shot uses the part of the panorama that it needs, so walls, windows, and props stay in place.
- **Top-view plan:** a simple drawing with walls, doors, the main props, the action line, and the camera positions (C02·M04).

### The reference library
Store references so that code can read them:

```
refs/
  CHAR-MARA/   sheet.json  01_front.png  02_34.png  03_side.png  04_back.png  10_happy.png ...
  PROD-CAMERA/ sheet.json  front.png  back.png ... logo.png
  LOC-LOCKER/  sheet.json  wide.png  reverse.png  pano.png  plan.png  night.png
```

`sheet.json` holds the ID, the kind, the descriptor, the source (generated, photo, licensed), the rights status, a consent file for any real person, and the file of each view. `starter/tools/refs_check.py` checks the library: required views, files that exist, files that are not listed, rights values, and consent for photos of real people.

### Test consistency
A sheet is good when new shots made only from the sheet keep the identity. Test it:
1. Write 3–5 new short prompts in new places and with new actions.
2. Generate them with the references only, no long descriptions.
3. Score each detail: face, hair, mark, clothes, buttons, scale.
4. The details that drift tell you what to add: a detail close-up, a missing view, or a LoRA (C14).

## Tool walkthrough

### Turnaround prompts (any model with multi-reference input)
Front portrait:

```text
Studio character reference, front view, head and shoulders, neutral expression.
Mara, early 30s, short black bob, small scar through the left eyebrow, olive raincoat with brass buttons.
Soft even light, plain mid-grey background, no shadows on the background. 3:4.
```

Side view, with the approved front as image 1:

```text
Image 1 is the character. The same woman as image 1, full body, side view facing left,
same raincoat and buttons, same hair. The scar is on her LEFT eyebrow (the side facing away).
Soft even light, plain mid-grey background, same scale as a 170 cm person in frame. 3:4.
```

Write the side of a mark in capitals when the view could confuse it. Models often mirror features in side views.

### The open path
`02_ref_edit_flux2_klein_4b.json` (C11 starter kit) takes two references. For a turnaround, use the front portrait as reference 1 and a grey background image as reference 2. Change only the view in the prompt.

### Check the library

```bash
python starter/tools/refs_check.py refs/
```

## Worked example

**Character Mara.**
1. Front portrait: 8 tries, 1 approved. Approval checklist: scar on her left eyebrow, short bob above the jaw, 4 brass buttons visible.
2. Turnaround with the front as reference: three-quarter ✓ on try 1, back ✓ on try 2, side ✗ — the scar moved to the right eyebrow. Mask edit on the eyebrow area with the instruction "small scar through the eyebrow". Outside change 0.1 %. ✓
3. Expressions: 6 close-ups. "Angry" changed her hairline; regenerated with the instruction "same hairline as image 1". ✓
4. Wardrobe B: hospital scrubs, full-body front. ✓
5. `sheet.json` written. `refs_check.py` reported one problem: `CHAR-MARA: file 05_side_v1.png is not listed in sheet.json` (an old rejected file). Moved it to `rejects/`. ✓

**Consistency test:** 4 new scenes (street, car, kitchen, hospital corridor) from references only:

| Detail | Street | Car | Kitchen | Corridor |
|---|---|---|---|---|
| Face | 5 | 4 | 4 | 5 |
| Scar side | ✓ | ✓ | ✗ | ✓ |
| Hair | 5 | 5 | 4 | 5 |
| Buttons (4, brass) | 3 | 2 | 3 | 3 |

Finding: buttons drift most. Fix: a close-up of the coat front added as `11_buttons.png`, and the prompt names it. The re-test gives buttons 4, 4, 4, 5.

## Lab

**Deliverable:** `refs/` with 1 character, 1 product, and 1 environment set, plus `C04/M03/consistency.md`.

1. Character sheet: 4 views, 6 expressions, 2 wardrobe variants, detail close-ups, and the descriptor sentence.
2. Product sheet: 6 views and a logo close-up. Use a real object that you own (photograph it on a plain background), or a generated object that you freeze.
3. Environment sheet: 4 views, 3 light states, a panorama, and a top-view plan with the action line.
4. Write `sheet.json` for each set. Run `refs_check.py refs/` until it passes.
5. Consistency test: 4 new scenes from references only. Score each detail. Add one fix for the detail that drifts most, and test again.
6. Log every kept reference image with `promptlog.py`. Add a rights line for every photo that you did not take.

**Result checklist**
- [ ] Three complete sets; `refs_check.py` passes.
- [ ] Every view checked against the descriptor (write the checks).
- [ ] Consistency table before and after one fix.
- [ ] Prompt-log and rights-log lines for all files.

## Model answer

A strong submission is boring on purpose. All sheet images have the same grey background, the same soft light, and the same scale. That is why they work as references.

`consistency.md` has a detail table before and after one fix, like the worked example, and three conclusions with evidence:
1. "Face and hair hold with 2 views (mean 4.6 / 5). Small parts drift: buttons 2.75 → 4.25 after I added a close-up."
2. "The scar flipped sides in 1 of 4 scenes. Side and three-quarter views must state the side in capitals in every prompt."
3. "The panorama kept the locker room layout in all 4 test shots: the window is always on the left of the door. Without the panorama, it moved in 2 of 4."

The product set uses real photos of a real object (an old film camera), with the logo photographed flat. The sheet has `"source": "photo", "rights": "own"`.

The environment plan is a simple top view with the action line and three camera positions. It is the input for continuity in C02·M04 and for camera planning in C07·M03.

`refs_check.py refs/` prints `3 reference sets, 0 problems`.
