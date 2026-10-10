---
title: Multi-shot sequences and consistency
hours: 16
outcomes:
  - Plan and generate multi-shot blocks with native multi-shot features.
  - Keep character, wardrobe, product, and location consistent across 10 or more shots with the consistency stack.
  - Join blocks and extend shots without visible seams, and check each join.
  - Measure identity drift across a sequence, tell drift from single rejects, and decide when to train a LoRA.
keywords: [multi-shot, consistency, scene extension, identity drift]
summary: >
  Current top models can generate several connected shots in one generation, with a consistent cast and place. For
  longer sequences you combine methods: fixed descriptors, a reference library, native multi-shot blocks, first and
  last frames at joins, short extensions, and a panorama anchor for places. Consistency inside one generation is
  high; drift appears at the joins between generations and over long chains. Measure identity per shot and look at
  the trend of the passing shots. A falling trend is drift; a single low shot is a reject. If drift stays high across
  many shots, train a LoRA.
diagram:
  type: stack
  title: Consistency stack (use from top to bottom)
  nodes: ["Fixed descriptors in every prompt", "Reference library (character, product, location)", "Native multi-shot generation", "First/last frames to join clips", "Short scene extensions", "LoRA for the cast and products (C14)"]
  highlight: [2]
watch:
  - title: "Bilibili — Seedance real-person short-drama workflow: multi-subject consistency (Chinese)"
    url: https://www.bilibili.com/video/BV1bnMF6MEvP/
    note: "Watch the consistency part: reference sets per character and micro-expression control."
  - title: "Google — Flow help center: Scene Builder and Extend"
    url: https://support.google.com/labs/answer/16353333
    note: "Read how one product joins and extends clips. Note the limits it states."
quiz:
  - q: "Inside one multi-shot generation, faces stay the same. Between two generations, the jacket color changes. Why?"
    options: ["Random error", "One generation shares one internal state; a new generation starts again from references and text, so small details can change at the join", "The jacket is too bright", "Multi-shot is broken"]
    answer: 1
    explain: "Consistency inside a block comes from shared attention across its shots. Joins between blocks depend on your references and anchors."
  - q: "Your drift plot: 11 shots between 0.58 and 0.63, one shot at 0.21. The trend of the passing shots is flat. What is it?"
    options: ["Drift; train a LoRA", "A single reject; regenerate that shot", "A bad threshold", "Nothing"]
    answer: 1
    explain: "Drift is a trend. One low shot with a flat trend is a failed take. The fix is cheap: regenerate it."
  - q: "The median identity falls from 0.62 in shot 1 to 0.48 in shot 12 of a chained sequence. What is the best fix?"
    options: ["Accept it", "Re-anchor: give the original references (not the previous clip's last frame) to every new block; if it still falls, train a LoRA", "Lower the threshold", "Use longer clips"]
    answer: 1
    explain: "Chaining from the last frame copies errors forward. Fresh references every block stop the error from adding up."
  - q: "A scene extension continues a good 5 s clip to 12 s. The look holds, but the action wanders. What is the rule?"
    options: ["Extend as long as possible", "Keep extensions short and give each one a specific action; cut to coverage instead of very long extensions", "Never extend", "Extend only at night"]
    answer: 1
    explain: "An extension keeps the look from the last frames but has no plan for the story. Give it a clear action, and keep it short."
  - q: "When is a native multi-shot block the right tool?"
    options: ["For every shot", "For a short scene of 2–6 shots in one place with the same cast, planned exactly like a shot list", "Only for B-roll", "Never for dialogue"]
    answer: 1
    explain: "Multi-shot blocks are strongest for short connected scenes. Long sequences still need joins."
  - q: "Your piece is 60 s with 2 characters. Face scores are ≥ 4 in 11 of 12 shots after edits. The client now orders a 20-episode series. What is the decision?"
    options: ["No change", "For the 60 s piece, edits are enough; for the series, train LoRAs for both characters, because many more shots and joins will add drift", "Train LoRAs for the 60 s piece now", "Use only T2V"]
    answer: 1
    explain: "The LoRA decision depends on the scale. A LoRA costs training and evaluation once and saves edits in every later shot."
  - q: "Which check do you do at every cut between generated shots?"
    options: ["File size", "Eyeline, screen direction, light direction, and prop positions (C02·M04)", "Bitrate", "The prompt length"]
    answer: 1
    explain: "Continuity errors are what viewers notice. Generated shots do not know the shots next to them."
deeper:
  - title: "Kuaishou — Kling 3.0 release notes (multi-shot)"
    url: https://app.klingai.com/global/release-notes
  - title: "Long-context tuning for video generation (multi-shot consistency research)"
    url: https://arxiv.org/abs/2503.10589
  - title: "Seedance 2.5 announcement (one-take creation, references)"
    url: https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5
---
## Learn

### Why consistency is hard
Each generation starts from noise. The model keeps a character the same only when the inputs carry the character: references, descriptors, and the first frame. Inside one generation, the model attends across all its frames at once, so a face stays the same. Across two generations, nothing is shared except what you give. That is why drift appears at joins and grows over long chains.

### Native multi-shot blocks
Current top models can make several connected shots in one generation. You give a shot list for the block: for each shot the duration, the shot size, the camera move, and the content. The model makes the cuts. Because the shots share one generation, the cast, the place, and the light stay consistent.

Use multi-shot blocks for short scenes of 2–6 shots in one place. Plan the block exactly as in a shot list (C03·M02). The model will not invent good coverage for you.

### Longer sequences: the consistency stack
For sequences of 1–10 minutes, combine methods. Use them from the top of the stack down. Each one adds cost:
1. **Fixed descriptors** in every prompt, word for word (C04·M03).
2. **References** for every recurring element: characters, products, places (C04·M03).
3. **I2V from approved key frames** for the important shots (M01).
4. **Native multi-shot blocks** for short scenes.
5. **First and last frames** at hard joins between blocks (M02).
6. **Short extensions** for long continuous takes.
7. **A panorama anchor** for places, so walls and windows stay in place.
8. **A LoRA** for the cast and products when the scale is large (C14).

### Joins between blocks
When you chain blocks, two methods are common:
- **Last frame → first frame.** The next block starts from the last frame of the previous block. The join is smooth, but errors are copied forward: a small color drift or a slightly wrong face becomes the new start.
- **Fresh references each block.** Each block starts from the original references and an approved key frame. The join needs a cut, an insert, or a first/last frame, but errors do not add up.

For long sequences, use fresh references at least every 2–3 blocks. Check each smooth join with `join_check.py` (M02).

### Extensions
An extension continues a clip from its last frames. The look holds well. The action can wander, because the model has no plan for the story beyond your prompt. Rules: keep each extension short, give it one specific action, and prefer a cut to coverage over a long extension.

### Measure drift
Score identity for every shot of the sequence, in order. Use `identity_score.py` (the same face-embedding scorer as in C11·M03) with your character references. Then plot the median score per shot with `drift_plot.py`.

Read the plot in two ways:
- **Single rejects:** one shot is low, and the others are flat. That shot failed. Regenerate it.
- **Drift:** the passing shots fall in a trend along the sequence. The method adds error. Re-anchor with fresh references, or train a LoRA.

The tool reports the trend of the passing shots only, so that one failed shot does not look like a drift. Scores do not cover everything. Check wardrobe details, products, and the place by eye with a scorecard (C04·M03).

### Continuity at cuts
At every cut between generated shots, check:
- eyeline and screen direction (the 180° rule, C02·M04);
- light direction and color;
- prop positions and states (the photo in which hand, the locker open or closed);
- wardrobe details.
Generated shots do not know their neighbors. A cutaway (insert, reaction) hides a join when continuity fails, and it is cheap to make.

## Tool walkthrough

### Native multi-shot (as of 2026-10)
- **Kling 3.0:** up to 6 shots per generation; each shot 3–15 s with its own shot size, camera move, and content; voice lock from a reference.
- **Seedance 2.5:** up to 30 s in one take as connected shots; up to 50 references.
- **LTX-2.5 (open):** native multishot.
- **Veo 3.1 + Flow:** Scene Builder joins clips; Extend continues a clip.

A multi-shot block prompt has one line per shot, for example:

```text
Shot 1 (4 s, wide two-shot, locked): Mara and Leo at a small café table, night, rain on the window.
Shot 2 (3 s, over-the-shoulder on Leo, slow push): Leo slides the photo across the table.
Shot 3 (3 s, MCU Mara, locked): Mara looks at the photo, then up at Leo.
Same characters as the references in all shots. Same light: warm practical lamp, cold window.
```

### Score the sequence

```bash
python starter/tools/identity_score.py --ref refs/CHAR-MARA/01_front.png --ref refs/CHAR-MARA/02_34.png \
  seq/S01.mp4 seq/S02.mp4 seq/S03.mp4 ... --json drift.json
python starter/tools/drift_plot.py drift.json --out drift.png
```

## Worked example

**Test of the drift tools** (2026-10-04, public-domain portraits). We scored 5 clips against a reference photo of one person: 4 clips of the same person and 1 clip of a different person.

```
PASS   median 0.632  A.mp4
PASS   median 0.610  B.mp4
PASS   median 0.609  Bwarm.mp4
PASS   median 0.624  push.mp4
REJECT median 0.145  C.mp4
5 shots; median range 0.14–0.63
trend of passing shots: -0.025 per 10 shots (all shots: -0.960)
REJECTS: single shots fail, but there is no trend. Regenerate those shots.
```

With all shots, the slope is −0.96 per 10 shots, which looks like strong drift. Without the reject, the trend is flat. The correct action is to regenerate clip C, not to train a LoRA.

**Scene: 6 shots, 40 s, café dialogue** (Mara and Leo):
1. Block 1, native multi-shot: wide two-shot, OTS on Leo, OTS on Mara, with voice lock for both. Faces, café layout, and light are consistent.
2. Block 2: the last frame of shot 3 as the first frame of shot 4, plus the same references. Leo's jacket color shifts slightly. Fix: an instruction edit (M05).
3. Scorecard after the fix: face 5, 5, 5, 4, 4, 5; wardrobe 5, 5, 5, 4, 5, 5.
4. Decision: no LoRA for this scene. For the 20-episode series, train LoRAs for both characters.

## Lab

**Deliverable:** `C05/M03/` with a 45–60 s sequence of 8–12 shots, `drift.json`, `drift.png`, a scorecard, and notes.

1. Use your story and reference library.
2. Generate at least one native multi-shot block of 3 or more shots. If your model has no multi-shot mode, make the block from I2V shots with the same references.
3. Join blocks with first/last frames, matching cuts, or fresh references. Check each smooth join with `join_check.py`.
4. Use one short extension.
5. Score identity for every shot. Make the drift plot. Fill in the scorecard for wardrobe, product, and place.
6. Edit the sequence. List each continuity problem, and how you fixed or hid it.
7. Write the LoRA decision for this piece and for a 20-episode version, with numbers.

**Result checklist**
- [ ] 45–60 s sequence exported.
- [ ] Drift plot, with each low shot explained (reject or drift).
- [ ] Join reports for every smooth join.
- [ ] Problem/fix list and the LoRA decision.

## Model answer

A strong submission shows the data and a clear reading of it.

**Drift summary:** "12 shots. Medians 0.52–0.66, one reject (S09, profile view, 0.31; regenerated: 0.55). Trend of passing shots: −0.08 per 10 shots. The trend comes from block 3, which started from the last frame of block 2. After I re-anchored block 3 with the original references, the trend became −0.01."

**Continuity list:**

| Cut | Problem | Fix |
|---|---|---|
| S03 → S04 | Photo in the left hand, then the right hand | Instruction edit on S04 (mirror the hand pose) |
| S06 → S07 | Window light from the left, then from the right | Regenerated S07 with the location panorama as reference |
| S10 → S11 | Leo's glasses missing | Inserted reaction S10b to hide the join; S11 regenerated with the glasses close-up reference |

**LoRA decision:** "For this 60 s piece: no LoRA. After 3 edits, face ≥ 4 in all shots. For 20 episodes (about 600 shots): train LoRAs for Mara and Leo. At my reject rate, references only would need about 150 extra takes for identity; a LoRA costs about US$15 and one day of evaluation (C14)."
