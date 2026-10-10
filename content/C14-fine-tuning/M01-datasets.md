---
title: Datasets - collect, clean, caption, consent
hours: 12
outcomes:
  - Collect 15–60 training images (or short clips) that cover angles, light, expressions, outfits, and places.
  - Clean the data - duplicates, blur, size, watermarks - and crop consistently with aspect buckets.
  - Write captions that describe what varies and leave the identity to the trigger word.
  - Document the source and the consent or license of every item, and write a dataset card.
  - Check a dataset automatically before you pay for training.
keywords: [LoRA, dataset, trigger word, caption, dataset card]
summary: >
  A LoRA learns what the dataset shows and what the captions do not explain. Collect images that vary in everything
  except the subject: angles, light, expressions, clothes, places. Remove duplicates and soft images, and keep the
  sizes high enough. Start every caption with the trigger word, describe everything that varies, and do not describe
  the identity features that the trigger should carry. Record the source and the consent or license of every item.
  A dataset check before training finds most problems in seconds; a bad dataset costs a training run.
diagram:
  type: flow
  title: From references to a training set
  nodes: ["Collect: vary everything except the subject", "Clean: duplicates, blur, size, watermarks", "Crop + aspect buckets", "Caption: trigger first; describe what varies", "Rights: source + consent per item", "Check, then train"]
  highlight: [3]
watch:
  - title: "musubi-tuner — dataset configuration docs (GitHub)"
    url: https://github.com/kohya-ss/musubi-tuner
    note: "Read the dataset config section (images and videos, buckets, captions)."
  - title: "Hugging Face — dataset cards"
    url: https://huggingface.co/docs/hub/datasets-cards
    note: "Use the structure for your own dataset card."
quiz:
  - q: "All 30 images of your character were made on the same grey background. What will the LoRA learn?"
    options: ["Only the face", "The grey background as part of the character: new scenes drift toward it; add images in varied places", "Nothing", "A better background"]
    answer: 1
    explain: "A LoRA learns what is constant in the data. Vary everything that should not belong to the subject."
  - q: "Every caption says 'a woman with a short black bob'. What is the problem?"
    options: ["None", "The model can explain the bob with the words, so it does not bind the bob to the trigger; without those words, the bob may disappear", "Captions must be long", "Captions must be in capitals"]
    answer: 1
    explain: "Caption what varies (clothes, place, light, shot). Leave the identity features to the trigger."
  - q: "Three images are near duplicates of the front view. Why remove two of them?"
    options: ["To save disk", "Duplicates over-weight one view; the LoRA becomes strong at that angle and weak at the others", "Trainers cannot read duplicates", "They are illegal"]
    answer: 1
    explain: "Balance the views. The dataset check finds near duplicates with a perceptual hash."
  - q: "Can you train a character LoRA on photos of a real person from social media?"
    options: ["Yes, if the photos are public", "Only with that person's documented consent for this use, and a check of the photos' copyright; otherwise no", "Yes, for tests", "Yes, if you blur the face"]
    answer: 1
    explain: "A likeness model of a real person needs consent (C16·M02). Public is not the same as permitted."
  - q: "Which images do you collect for a product LoRA?"
    options: ["Only the front", "All sides, close-ups of the logo and materials, and the product in several contexts and lights", "Only lifestyle photos", "Drawings"]
    answer: 1
    explain: "Shape, logo, and materials must hold from every angle. Context images teach the model to place it."
  - q: "Why use aspect-ratio buckets instead of cropping everything to a square?"
    options: ["Squares are illegal", "Square crops cut off full bodies and wide shots; buckets keep the natural framing, so the LoRA learns both portraits and wide shots", "Buckets are faster", "Only for video"]
    answer: 1
    explain: "Most trainers group images by aspect ratio into buckets. Keep the framing that your shots need."
  - q: "What must the dataset card say?"
    options: ["Only the trigger", "Purpose, counts by type, sources, licenses and consent, known biases or gaps, and allowed uses", "The GPU", "The training time"]
    answer: 1
    explain: "The card is the documentation and the rights record of the model (C14·M03, C16)."
deeper:
  - title: "Ruiz et al. (2022) — DreamBooth: Fine Tuning Text-to-Image Diffusion Models"
    url: https://arxiv.org/abs/2208.12242
  - title: "Hu et al. (2021) — LoRA: Low-Rank Adaptation of Large Language Models"
    url: https://arxiv.org/abs/2106.09685
  - title: "AI Toolkit (ostris) — GitHub"
    url: https://github.com/ostris/ai-toolkit
---
## Learn

### What a LoRA learns
A LoRA (low-rank adapter) is a small set of extra weights added to a base model (C01·M06). Training adjusts only these weights, so that the model makes your subject when the prompt has the trigger word. The LoRA learns:
- what is the same in all images (the subject, and anything else that never changes);
- what the captions do not explain.
Both rules decide how you build the dataset.

### What to collect
- **Character:** 20–40 images. Front, three-quarter, side, back; close-ups and full body; 5 or more expressions; 3 or more outfits; 3 or more light setups; plain and real backgrounds. Sources: your character sheet (C04·M03) and new scenes made from it, or photos of a real person who consents.
- **Product:** 15–30 images. All sides, close-ups of the logo and materials, and the product in several contexts.
- **Style:** 30–60 images with the style across many different subjects, so that the LoRA learns the style, not the subjects.
- **Video LoRAs:** short clips (2–5 s) for a motion or a camera style. For identity, still images often generalize well to motion (practitioner reports).

### Vary everything except the subject
If all images share a background, a light, or a lens, the LoRA learns it as part of the subject. New scenes then drift toward it. Vary the places, the light, the shot sizes, and the clothes. Keep only the subject constant.

### Clean
- **Duplicates:** near-identical images over-weight one view. Keep one.
- **Soft images:** blurred or out-of-focus images teach softness.
- **Small images:** below about 768–1024 px on the short side, detail is lost.
- **Artifacts and watermarks:** extra fingers, warped features, text, logos. The LoRA learns them.
- **Wrong details:** an image where the scar is on the wrong side teaches the wrong side.

### Crop and buckets
Crop each image to the subject with a little space. Do not force everything to a square. Most trainers sort images into aspect-ratio buckets, so portraits, full bodies, and wide shots keep their framing.

### Captions
Each image has a caption file with the same name. Rules:
1. **Trigger first:** a rare token, for example `mrx_mara`.
2. **Describe what varies:** clothes, place, light, shot size, action. "mrx_mara, wearing hospital scrubs, standing in a corridor, cold fluorescent light, medium shot."
3. **Do not describe the bound identity features** (her bob, her scar) if you want the trigger to carry them. Words that explain a feature take it away from the trigger.
Use a vision LLM to draft captions. Read and correct every one.

### How many images
More is not always better. 20–40 good, varied images of a character usually beat 200 similar ones. Each new image should add something: an angle, a light, an outfit, an expression, a place. If a new image adds nothing, it only adds weight to what you already have.

### Rights and the dataset card
Record the source and the license or consent of every item, with the date. For a real person, the consent record must cover training a likeness model (C16·M02). Write a dataset card: purpose, counts by type, sources, licenses and consent, known gaps or biases, and allowed uses. The model registry (M03) links to it.

## Tool walkthrough

### Folder layout

```
training/mara/
  01_front.png   01_front.txt     "mrx_mara, in an olive raincoat, plain grey studio, soft light, close-up"
  12_corridor.png 12_corridor.txt "mrx_mara, wearing hospital scrubs, hospital corridor at night, ..."
  rights.csv       file,source,license_or_consent,date
  CARD.md
```

### Check before training

```bash
python starter/tools/dataset_check.py training/mara/ --trigger mrx_mara --bound "black bob,scar" --min-side 1024
```

It checks caption pairs, the trigger, size, blur, near duplicates (a perceptual hash), bound features in captions, and the rights lines.

### Trainers (as of 2026-10)
musubi-tuner (kohya-ss) for Wan, HunyuanVideo, and FLUX.2; AI Toolkit (ostris); Diffusers training scripts; hosted LoRA trainers (for example fal). Each reads image + caption pairs; check its dataset config format.

## Worked example

**Dataset check test** (2026-10-04, public-domain portraits, trigger `mrx_arm`, bound feature "short brown hair"). Six planted problems in six images:

| Planted problem | Found as |
|---|---|
| a 480 × 600 copy | PROBLEM: smaller than 768 px on the short side |
| a caption that starts with "a man…" | PROBLEM: does not start with the trigger |
| an image without a caption | PROBLEM: no caption file |
| an image without a rights line | PROBLEM: no line in rights.csv |
| a blurred copy | WARN: looks soft (sharpness 3 < 60) |
| "short brown hair" in a caption | WARN: mentions the bound feature |
| a resaved copy of the front view | WARN: near duplicates (0 of 64 bits differ) |

The mirrored copy was not flagged as a duplicate. A mirror is a different image to the hash, but for a character with a scar on one side it is a wrong image. Check mirrors by eye.

**Mara dataset:** 32 images (24 from the sheet + 8 new scenes); outfits: raincoat 10, scrubs 12, casual 10; 6 places; 4 light setups. Captions by a vision LLM, then edited: the words "black bob" and "scar" removed from all captions. Trigger `mrx_mara`. Card: "Fictional character; all images generated by us (models listed in the prompt log); no real-person likeness; allowed uses: this series."

## Lab

**Deliverable:** `training/<subject>/` with images, captions, `rights.csv`, `CARD.md`, and a dataset-check report.

1. Choose one subject: your main character (from your sheet) or a product that you own.
2. Collect 20–40 images. Vary place, light, shot size, clothes, and expression.
3. Clean them: remove duplicates, soft images, artifacts, and wrong details. Crop with buckets in mind.
4. Write the captions: trigger first, describe what varies, leave the bound features out. Correct every LLM draft.
5. Write `rights.csv` and `CARD.md`.
6. Run `dataset_check.py` until there are no problems. Review every warning and write what you did about it.

**Result checklist**
- [ ] 20–40 images with captions, varied in everything except the subject.
- [ ] `rights.csv` complete; consent records for any real person.
- [ ] `CARD.md` with purpose, counts, sources, gaps, and allowed uses.
- [ ] Dataset check: 0 problems; each warning answered.

## Model answer

**Dataset summary (shape of a strong answer):**

| Dimension | Values (count) |
|---|---|
| View | front 8, three-quarter 10, side 6, back 3, over-the-shoulder 5 |
| Shot size | close-up 9, medium 14, full body 9 |
| Outfit | raincoat 10, scrubs 12, casual 10 |
| Place | grey studio 6, locker room 7, corridor 6, street 5, café 4, kitchen 4 |
| Light | soft studio, fluorescent night, daylight window, warm practical |

"The first check found 3 near duplicates of the front view (from re-generations) and 2 soft images. I removed them and made 3 new three-quarter views. The warnings for 'scar' in 4 captions: removed the word. One mirrored side view had the scar on the wrong side; I deleted it. Final: 32 images, 0 problems, 1 accepted warning (a short caption for a plain close-up, where little varies)."

The card states the gap: "No profile close-ups in daylight; expect weaker identity there." That gap is what M03's eval checks first.
