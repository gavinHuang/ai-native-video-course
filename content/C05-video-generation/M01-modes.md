---
title: Generation modes and when to use each
hours: 12
outcomes:
  - Explain text-to-video, image-to-video, reference-to-video, video-to-video, and instruction editing, and what each mode fixes.
  - Choose a mode for a shot from its requirements, with a decision table.
  - Run the same shots in 3 modes and compare control, quality, and cost per usable second.
  - Run a generation session with a take log, and calculate cost per usable second by mode and model.
keywords: [text-to-video, image-to-video, reference-to-video, video-to-video, cost per usable second]
summary: >
  There are five main modes. Text-to-video starts from a prompt only; it is fast to try but gives the least control.
  Image-to-video starts from a key frame; it fixes composition and identity. Reference-to-video uses several
  reference images, videos, or audio clips; it keeps identity without fixing the first frame. Video-to-video
  transforms existing footage and keeps its motion. Instruction editing changes one thing in an existing clip. In
  professional work, image-to-video and reference-to-video are the default modes. Measure every mode by cost per
  usable second, not by cost per generated second.
diagram:
  type: layers2d
  title: Five modes
  rows: ["Text-to-video (T2V)", "Image-to-video (I2V)", "Reference-to-video (R2V)", "Video-to-video (V2V)", "Instruction edit"]
  cols: ["Input", "Best for"]
  cells:
    - ["Prompt", "Ideas, B-roll, exploration"]
    - ["Key frame + prompt", "Exact composition + identity"]
    - ["Many refs (image/video/audio) + prompt", "Consistent cast across new shots"]
    - ["Source video + prompt (+ control)", "Restyle real or rough footage"]
    - ["Existing clip + instruction", "Fix or change one element"]
watch:
  - title: "Google Flow — help center (Ingredients, Frames to Video, Extend)"
    url: https://support.google.com/labs/answer/16353333
    note: "Read how one product names the modes. Map each name to the five modes of this module."
  - title: "ComfyUI blog — Wan 2.6 Reference-to-Video in ComfyUI"
    url: https://blog.comfy.org/p/wan26-reference-to-video
    note: "An example of reference-to-video with motion and style from reference clips."
quiz:
  - q: "A client approved a key frame. Which mode keeps it exactly as the first frame?"
    options: ["T2V", "I2V", "R2V", "V2V"]
    answer: 1
    explain: "I2V starts from that exact image. The model never denoises the first frame (C11·M02 shows the mechanism)."
  - q: "You need the same 3 actors in 20 new shots with different framings. Which mode is best?"
    options: ["T2V with long descriptions", "R2V with character references", "V2V", "Upscaling"]
    answer: 1
    explain: "R2V keeps identity while the model composes each new shot. With I2V you would need 20 approved key frames first."
  - q: "You filmed a rough phone video of a friend doing the action. You want a sci-fi version. Which mode?"
    options: ["T2V", "V2V with pose or depth control", "Instruction edit", "I2V"]
    answer: 1
    explain: "V2V keeps the real motion and timing; the prompt and references set the new look."
  - q: "The shot is perfect, but a car in the background is red; it must be white. Which mode?"
    options: ["Regenerate with T2V", "Instruction edit on the existing clip", "I2V", "R2V"]
    answer: 1
    explain: "An edit changes one element and keeps the rest. A new generation risks everything that was already right."
  - q: "Model X costs US$0.05 per generated second and gives 15 % usable seconds. Model Y costs US$0.12 and gives 50 %. Which is cheaper per usable second?"
    options: ["X: US$0.33 vs Y: US$0.24, so Y", "X, because it is cheaper per second", "They are the same", "You cannot calculate it"]
    answer: 0
    explain: "Cost per usable second = price per second / usable share. 0.05 / 0.15 = 0.33. 0.12 / 0.50 = 0.24. The 'cheap' model is more expensive here."
  - q: "In your test, T2V has a 10 % usable rate for planned shots and 60 % for abstract B-roll. What do you conclude?"
    options: ["T2V is bad", "Use T2V for shots where the model may choose the details (B-roll, textures, abstract), and I2V/R2V for planned shots", "Use T2V for everything", "Only use V2V"]
    answer: 1
    explain: "A mode is good or bad for a job. T2V is good when you do not need exact control."
  - q: "Why log takes with in and out points instead of 'usable: yes/no'?"
    options: ["It looks professional", "A 6 s take with 3.7 usable seconds is not the same as a fully usable take; the budget needs usable seconds", "Editors need it", "It is required by platforms"]
    answer: 1
    explain: "The edit uses parts of takes. Usable seconds per dollar is the number that plans the next session."
deeper:
  - title: "Seedance 2.5 announcement (ByteDance Seed)"
    url: https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5
  - title: "Runway — help center (Aleph and video editing)"
    url: https://help.runwayml.com/hc/en-us
  - title: "Blattmann et al. — Stable Video Diffusion (image-to-video research background)"
    url: https://arxiv.org/abs/2311.15127
---
## Learn

### What a mode is
A mode is the set of inputs that you give the video model. Each input fixes some decisions and leaves the others to the model. The more you fix, the more control you have, and usually the more work you did before the generation. Choose the mode by asking: what must be exact in this shot?

### The five modes
1. **Text-to-video (T2V).** Input: a prompt only. The model chooses everything that you do not say: the face, the room, the framing, the light. It is fast to try. It is the weakest mode for planned shots, because identity and composition change in every take.
2. **Image-to-video (I2V).** Input: a key frame and a motion prompt. The key frame becomes frame 1, so composition, identity, light, and look are fixed (C04). The prompt adds the motion. Some models also take a last frame (M02). This is the most common professional mode.
3. **Reference-to-video (R2V).** Input: several references (character, product, place, style; in some models also video and audio) and a prompt. The model makes a new composition with those elements. It keeps identity without a fixed first frame. Use it when you need the same cast in many new framings.
4. **Video-to-video (V2V).** Input: a source video, a prompt, and often a control signal (depth, pose, or edges). The source gives motion and timing. The prompt and references give the new look. Use it for a real performance, an exact action, or a rough 3D animation that you want to look real.
5. **Instruction editing.** Input: an existing clip and one instruction. The model changes one thing (remove, add, relight, restyle) and keeps the rest (M05).

### What each mode fixes
| Mode | Identity | Composition | Motion | Look |
|---|---|---|---|---|
| T2V | model | model | model | prompt |
| I2V | key frame | key frame | prompt | key frame |
| R2V | references | model | prompt | references + prompt |
| V2V | references + prompt | source | source | prompt + references |
| Edit | source | source | source | source, except the one change |

Read the table as a design tool. If identity and composition must both be exact, only I2V fixes both. If motion must be exact, only V2V fixes it.

### Choose the mode
| Requirement of the shot | Mode |
|---|---|
| Composition approved as a still | I2V |
| Same cast in many new framings | R2V |
| A real performance or an exact motion | V2V |
| One defect in a good clip | Instruction edit |
| A fast idea, a texture, or abstract B-roll | T2V |

### The professional default
1. Explore ideas with images or T2V. It is cheap.
2. Approve key frames (C04).
3. Generate motion with I2V, or with R2V for coverage of the same scene.
4. Fix defects with edits.
This order gives the most control for the least money. Each step fixes decisions before the next, more expensive step.

### Measure by cost per usable second
A video model costs money per generated second. But you pay for every take, and the edit uses only the good parts of the good takes. So the number that matters is:

```
cost per usable second = total cost of all takes / usable seconds in the selects
                       = price per generated second / usable share
```

A model at US$0.05/s with 15 % usable seconds costs US$0.33 per usable second. A model at US$0.12/s with 50 % costs US$0.24. The "cheap" model is more expensive. Usable share changes with the mode and the shot type, so measure it per mode and per shot type.

### Takes and selects
Treat each generation as a take, as on a set. Name it by shot and number: `S07_t03`. Review each take and record a decision: select, maybe, or reject. For a select, record the usable part with in and out points, and a note ("hand flicker after 4.1 s"). The editor uses the selects. The budget uses the usable seconds. `starter/tools/takes.py` keeps this log and computes the report.

## Tool walkthrough

### Mode names in current products (as of 2026-10)
Products use their own names for the same modes:
- **Google Veo 3.1 / Flow:** "Frames to Video" is I2V with first and last frame; "Ingredients" is R2V; "Extend" continues a clip.
- **Kling 3.0 / 3.0 Omni:** I2V with start and end frames; Omni accepts references; multi-shot blocks (M03).
- **Seedance 2.5:** up to 50 references (images, audio, 3D white models, style); region editing.
- **Runway Gen-4.5 + Aleph:** generation plus editing of existing clips.
- **Open (ComfyUI):** the C11 starter kit has I2V (`03`, `06`), first/last frame (`04`, `08`), and V2V with control (`05`).

Map every new product to the five modes. Then you can compare it with what you use now.

### Log a session

```bash
python starter/tools/takes.py budget S07 --target 4 --cap 3.00
python starter/tools/takes.py add S07 --model kling-3.0 --mode i2v --dur 6 --cost 0.60 --file takes/S07_t01.mp4
python starter/tools/takes.py review S07_t01 select --in 0.4 --out 4.1 --note "hand flicker after 4.1 s"
python starter/tools/takes.py report
```

The report gives the select rate, the usable share, and US$ per usable second for each model, and the coverage and cap status for each shot.

## Worked example

**Shot S07** (Mara reads the photo, 4 s needed, planned in C04):

| Take | Mode | Result | Usable |
|---|---|---|---|
| S07_t01 | T2V | Wrong face, nice light | 0 s |
| S07_t02 | T2V | Wrong face, wrong room | 0 s |
| S07_t03 | R2V (CHAR-MARA + LOC-LOCKER) | Good face; wider than planned | 2.5 s (usable as an alternative angle) |
| S07_t04 | I2V from `KF-S07-v3` | Exact composition and face; push-in works; hand flicker after 4.1 s | 3.7 s (0.4–4.1 s) |

We entered these 4 takes (6 s each, US$0.60 each) into `takes.py`. The report:

```
model                    takes select rate usable %      US$ US$/usable s
hosted-A                     4         50%      26%     2.40         0.39
shot     takes usable s target     US$     cap  status
S07          4      6.2    4.0    2.40     3.0  covered
```

The 2 T2V takes cost US$1.20 and gave nothing. For planned shots like this one, start with I2V. Keep T2V for B-roll.

## Lab

**Deliverable:** `C05/M01/` with 12 or more clips, the take log (`takes/`), and a mode report.

1. Choose 4 shots from your storyboard (C04·M04). Set a target and a cap for each with `takes.py budget`.
2. Generate each shot in T2V, I2V (from the approved key frame), and R2V (from your reference library).
3. For one shot, make a V2V version from a phone video that you record of yourself.
4. For one good clip, do one instruction edit.
5. Review every take in `takes.py`: decision, in and out points, note.
6. Run the report. Write a mode table: usable share and cost per usable second for each mode, with one sentence on when you will use each mode.

**Result checklist**
- [ ] 12+ clips, each in the take log and the prompt log.
- [ ] Every select has in and out points.
- [ ] Mode table with numbers from the report.
- [ ] One V2V clip and one edit.

## Model answer

A strong mode table from 4 planned shots looks like this:

| Mode | Takes | Usable share | US$ per usable second | Use it for |
|---|---|---|---|---|
| T2V | 8 | 9 % | 1.11 | B-roll and textures only |
| I2V | 8 | 52 % | 0.19 | Every planned shot with an approved key frame |
| R2V | 8 | 34 % | 0.29 | Coverage: new angles of the same scene |
| V2V | 2 | 70 % | 0.14 | Exact actions that I can perform myself |
| Edit | 2 | 1 of 2 succeeded | — | One-element fixes (M05) |

The text explains the numbers:
1. "T2V failed on identity in 7 of 8 takes. It is the most expensive mode per usable second for planned shots."
2. "I2V wasted the least. Most rejects had hand or eye problems after 4 s, so I plan I2V shots at 4–5 s."
3. "V2V had the highest usable share. The motion came from my phone video, so the model only had to change the look. Faces drifted at high strength; strength 0.6 was the best value."

The take log has notes that the editor can use: in and out points for every select, and the reason for every reject.
