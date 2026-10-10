---
title: Look bible, key frames, and storyboards
hours: 20
outcomes:
  - Write a look bible as testable rules for palette, light, texture, lens, and camera, plus a fixed look suffix.
  - Generate a storyboard of 2–4 key-frame options per shot from the shot list with a script.
  - Review every option in a sheet with the look-bible checks, and decide pick, fix, or redo.
  - Build an animatic with shot timing, slow moves, and temp audio, and change the plan from what it shows.
keywords: [look bible, key frame, storyboard, animatic]
summary: >
  A look bible defines how the whole project looks, as rules that a reviewer can check: palette with color values,
  light, contrast, texture, lens, and camera. A fixed look suffix goes into every prompt; the do-not rules go into the
  review sheet. A script turns the shot list into 2–4 key-frame options per shot. A review sheet records the
  decision for each shot. An animatic puts the chosen frames on a timeline with durations, slow moves, and temp
  sound. It tests story and timing before you pay for motion.
diagram:
  type: flow
  title: From shot list to approved storyboard
  nodes: ["Shot list (JSON)", "Look bible + reference library", "Script: 2–4 key frames per shot", "Review sheet: pick / fix / redo", "Animatic with temp audio", "Approved frames → video generation"]
  highlight: [3, 4]
watch:
  - title: "ShotDeck — reference frames searchable by color and light"
    url: https://shotdeck.com/
    note: "Collect 10–20 reference frames for your look bible. Note the color, the contrast, and the light direction of each."
  - title: "StudioBinder — What is an animatic?"
    url: https://www.studiobinder.com/blog/what-is-an-animatic-definition/
    note: "Read the definition and look at the examples. Note how simple the moves are."
quiz:
  - q: "Which look-bible rule can a reviewer check?"
    options: ["'Moody and cinematic'", "'Only one saturated color per frame: the amber of practical lamps (#D9922E); everything else below 30 % saturation'", "'Beautiful light'", "'Like a famous film'"]
    answer: 1
    explain: "A rule is useful when two people would give the same pass/fail answer. Use numbers and named colors."
  - q: "Your look bible has the do-not rule 'no lens flares'. Why is 'avoid lens flares' a bad thing to add to the prompt?"
    options: ["It is too long", "Many image models react to the words 'lens flares' and add them; check do-not rules in review, or use a negative prompt where the model supports one", "Prompts cannot have rules", "It slows the model"]
    answer: 1
    explain: "Text encoders do not reliably understand negation. Name what you want in the prompt. Check what you do not want in review."
  - q: "Why does code add one fixed look suffix to every prompt, instead of a new description per shot?"
    options: ["To save tokens", "Small wording changes give visible look changes; one fixed suffix keeps the look the same across shots", "Models need it", "For the prompt log only"]
    answer: 1
    explain: "Paraphrase is a source of drift. A fixed string is a constant in the system."
  - q: "How many key-frame options per shot are useful in review?"
    options: ["1", "2–4", "20", "As many as possible"]
    answer: 1
    explain: "One gives no choice. Many give review overload and cost. 2–4 options with different seeds usually contain a good one."
  - q: "In the animatic, shots 4–6 feel slow. What is the cheapest correct action?"
    options: ["Generate all shots as video and decide later", "Change the plan now: shorten or cut a shot and re-time the animatic; the change costs minutes, not generation money", "Add music", "Speed up the video later"]
    answer: 1
    explain: "The animatic exists to find story and timing problems before motion. A cut now saves every take of that shot."
  - q: "A key frame is 10 % too saturated against the look bible, and everything else is right. What do you do?"
    options: ["Redo the shot", "Mark it 'pick' with a grade note: small color deviations are fixed in the grade (C09); large ones are fixed in the frame", "Change the look bible", "Ignore it"]
    answer: 1
    explain: "Know what the grade can fix. Saturation and small color shifts are cheap later. Wrong light direction, identity, or composition are not."
  - q: "What must each row of the review sheet have?"
    options: ["Only the file name", "Shot, option, scores for story, continuity, identity, and look, the do-not checks, a decision (pick/fix/redo), and a note", "The cost only", "The model name only"]
    answer: 1
    explain: "The sheet is the record of decisions. The fix and redo notes become the next round of work."
deeper:
  - title: "Film Grab — film stills archive for references"
    url: https://film-grab.com/
  - title: "Coolors — palette tool (export hex values)"
    url: https://coolors.co/
  - title: "Mercado — The Filmmaker's Eye (book on composition and shot choice)"
    url: https://www.routledge.com/The-Filmmakers-Eye-Learning-and-Breaking-the-Rules-of-Cinematic-Composition/Mercado/p/book/9781138780316
---
## Learn

### Why a look bible
A project has many shots, often made with several models and on several days. Without written rules, each shot gets a slightly different look, and the cut feels like a collection, not a film. A look bible is the specification of the look. It does three jobs:
1. It gives code one fixed look suffix for every prompt.
2. It gives reviewers rules to check every frame.
3. It gives the colorist the target for the grade (C09).

### Write rules, not adjectives
A useful rule has one meaning for every reader. "Moody" has none. Write rules with numbers, named colors, and examples:
- **Palette:** 3–5 colors with hex values. Where the accent color is allowed. Example: "Teal-grey base (#3E5A5E), skin warm, one accent: practical amber (#D9922E). Nothing else above 30 % saturation."
- **Light:** key direction preferences, contrast, practicals, the night look (C02·M03). Example: "Night interiors: top light cold, one warm practical in frame, faces 1.5 stops under the practical."
- **Contrast:** deep blacks or lifted blacks; highlight roll-off.
- **Texture:** clean digital, 35 mm grain, 16 mm grain, halation, bloom.
- **Lens:** focal length per shot type, depth of field. Example: "Close-ups 85 mm look, shallow; wides 28 mm look; no ultra-wide distortion."
- **Camera:** locked, gimbal, or handheld; which moves are allowed (C02·M02).
- **References:** 10–20 frames from films or your own tests, each with one line on what to copy from it.
- **Do-not rules:** for example "no lens flares, no teal-and-orange look, no pure white backgrounds".

Keep it short: 1–3 pages. A long bible is not read.

### The look suffix
Turn the bible into one short text, for example: "muted teal and amber palette, 35 mm film grain, soft halation, deep blacks, motivated practical light". Code adds it to every prompt, word for word. Do not paraphrase it per shot. Small wording changes give visible look changes.

### Do-not rules go to review
Do not write "no lens flares" or "avoid lens flares" into the prompt. Many models react to the words "lens flares" and add them. The text encoder does not reliably understand negation. Name what you want in the prompt. Check the do-not rules in review. Some models have a separate negative prompt input. Use it only where your tests show that it works.

### The storyboard as a batch job
A storyboard is a key frame for every shot. In this program it is a batch job, not a drawing session:
1. **Input:** the shot list from C03·M02 (JSON), the reference library (M03), and the look bible.
2. **Prompt build:** for each shot, join the parts in the fixed order (M01): shot, subject descriptors from the sheets, action, place descriptor, light, and the look suffix. Add the reference roles.
3. **Options:** 2–4 seeds per shot. Name files by shot ID and option: `S07_a.png`, `S07_b.png`.
4. **Log:** every option goes into the prompt log with its seed and references.
5. **Review sheet:** one row per option, with empty score columns and one column per do-not rule.

The batch job is cheap. A 20-shot storyboard with 3 options is 60 images. On an open model on your own GPU it costs only time. On a hosted model it costs a few dollars.

### The review
Review the options of each shot together, then the shots in order. Score:
- **Story:** does the frame show the beat clearly?
- **Continuity:** does it match the shots before and after? Screen direction, light, props (C02·M04).
- **Identity:** does the character match the sheet?
- **Look:** does it follow the bible? Check each do-not rule.
- **Composition for the delivery frame:** for 9:16, is the subject large enough, and is the subject clear of the platform's text areas?

Decide for each shot: **pick** (use as is), **fix** (an edit can correct it, M02), or **redo** (generate again with a changed prompt or reference). Know what the grade can fix later: small color and saturation changes are cheap in the grade. Wrong light direction, wrong identity, and wrong composition are not.

### The animatic
An animatic is the storyboard on a timeline. Each chosen frame stays on screen for the planned duration. A slow move (push, pull, or pan) on the still shows the intended camera move. Add temporary sound: a synthetic voice for dialogue and narration, temp music, and the key sound effects.

Watch it 3 times, with one question each time:
1. Does the story work? Can a new viewer follow it?
2. Is the timing right? Where does it drag? Where is it too fast to read?
3. What is missing? A reaction shot, an insert, a sound?

Fix the plan now: cut, re-time, add a shot, or change a beat. Each change costs minutes. The same change after video generation costs every take of the changed shots. Then generate motion only for approved frames (C05).

## Tool walkthrough

### Run the storyboard script
The reference solution `starter/solutions/C04-M04/storyboard.py` uses the open path: workflow 02 from the C11 starter kit (two references) through the ComfyUI API. Plan first with `--dry-run`:

```bash
python storyboard.py shots.json --refs refs/ --look look.json --out storyboard/ --options 3 --dry-run
```

It prints the jobs and the full prompt of the first job, and writes `plan.json` and `review.csv`. Read the prompt. Check the reference roles and the order. Then run without `--dry-run` against your ComfyUI server. To use a hosted image API instead, replace the backend call with the API call from M01. Keep the prompt builder.

### Build the animatic

```bash
python starter/tools/animatic.py shots.json --frames storyboard/ --out animatic.mp4 --audio temp_mix.wav --size 1080x1920
```

Each shot needs `id` and `dur`. Optional: `move` (`push`, `pull`, `pan_left`, `pan_right`, `hold`), `frame` (a file name), and `label`. Without `frame`, the script uses `<id>_chosen.*`, then the first `<id>_*` file. A shot with no frame becomes a grey card with "[NO FRAME]", so gaps are visible. Labels show the shot ID and duration at the bottom, so reviewers can name shots in notes.

Make the temp mix in any audio tool, or with a synthetic voice: on macOS, `say -o vo.aiff "..."`, then `ffmpeg -i vo.aiff vo.wav`.

## Worked example

**Look bible for "The Camera"** (60 s, vertical, from C02·M05):

| Rule | Value |
|---|---|
| Palette | Teal-grey base #3E5A5E; skin warm; one accent: practical amber #D9922E; nothing else above 30 % saturation |
| Night interiors | Cold top light; one warm practical in frame; faces 1.5 stops under the practical |
| Morning (payoff) | Soft window light, warmer; the only shots with daylight |
| Texture | 35 mm grain, soft halation on practicals |
| Lens | CU/MCU 85 mm look, shallow; WS 28 mm look |
| Camera | Locked or slow push only; handheld only in the turn (35–48 s) |
| Do not | lens flares; pure white backgrounds; teal-and-orange look |

Look suffix: "muted teal and amber palette, 35 mm film grain, soft halation, deep blacks, motivated practical light".

**Storyboard run:** 14 shots × 3 options = 42 frames. Open model on a rented 48 GB GPU: about 3 s per image, 4 minutes in total including uploads. Review result: 9 picks, 3 fixes (a hand, the photo content, a second lamp), 2 redos (S10 was day light instead of night; S12 broke screen direction).

**Animatic:** 60 s with a synthetic voice and temp music. We built it with `animatic.py` in under 10 s. Two problems were found on the second viewing:
1. Shots S04–S06 (the setup) drag: 12 s for one idea. Cut S05; extend S06 by 1 s.
2. The turn (S11, the blank print) has no reaction. Add S11b: ECU, her eyes, 1.5 s.
The plan changes cost 20 minutes. Without the animatic, S05 would have cost about 8 video takes.

## Lab

**Deliverable:** `C04/M04/` with the look bible, `look.json`, the storyboard folder, `review.csv`, the animatic MP4, and `plan_changes.md`.

1. Write the look bible for your story (C02·M05): the rules table, 10 reference frames with one line each, and the do-not rules. Every rule must be checkable.
2. Write `look.json` with the suffix, the aspect ratio, and the do-not rules.
3. Write or adapt the storyboard script. Generate 3 options per shot from your shot list and references. Log every option.
4. Fill in `review.csv` for every option. Decide pick, fix, or redo for each shot. Do the fixes and redos.
5. Build a 30–60 s animatic with the chosen frames, durations, moves, and temp audio.
6. Watch it 3 times with the 3 questions. Write `plan_changes.md`: each change, the reason, and the shots it affects. Update the shot list and rebuild the animatic.

**Result checklist**
- [ ] Look bible with hex values, checkable rules, and do-not rules.
- [ ] Storyboard made by a script; every option in the prompt log.
- [ ] `review.csv` complete, with decisions.
- [ ] Animatic version 1 and version 2, and `plan_changes.md`.

## Model answer

A strong look bible fits on one page and can be checked: "one saturated color per frame", "faces 1.5 stops under the practical", "85 mm look for close-ups". It has no adjectives without numbers.

`review.csv` (extract):

```
shot,option,file,story,continuity,identity,look_bible,no lens flares,no pure white backgrounds,decision,note
S07,a,S07_a.png,4,4,5,4,ok,ok,pick,grade: saturation -10%
S07,b,S07_b.png,4,3,4,4,ok,ok,,
S10,a,S10_a.png,3,2,4,2,ok,ok,redo,day light in a night scene; add "night, window black" to light
S12,b,S12_b.png,4,1,5,4,ok,ok,redo,screen direction flipped (she faces left); see plan.png
S09,c,S09_c.png,5,4,4,3,FLARE,ok,fix,mask-remove flare on lamp
```

`plan_changes.md`:

| Change | Reason (from the animatic) | Shots affected | Saved |
|---|---|---|---|
| Cut S05 | Setup drags: 12 s for one idea | S05 removed; S06 +1 s | About 8 video takes |
| Add S11b (ECU eyes, 1.5 s) | The turn has no reaction | New shot | — |
| S14 from 4 s to 3 s | Payoff is clear earlier | S14 | 1 s of generation per take |

The summary states the effect on the budget: "The animatic removed 1 shot and shortened 1. That is about 20 % fewer generated seconds in C05."
