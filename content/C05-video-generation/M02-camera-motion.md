---
title: Camera, motion, and first/last-frame control
hours: 16
outcomes:
  - Write motion prompts that state subject motion, camera motion, timing, and what stays still.
  - Use first and last frames to make transitions, reveals, loops, and product turns.
  - Use camera-control settings, motion references, and 3D layouts when words are not exact enough.
  - Measure joins and loops with a jump ratio and a color shift, and fix the common motion defects.
keywords: [first/last frame, motion control, camera control, morphing, temporal consistency]
summary: >
  A video prompt must describe three motions: what the subject does, what the camera does, and when. Keep one main
  action and one camera move per clip, and say what does not move. First and last frames give exact start and end
  states, so you can make transitions, reveals, and loops. Camera-control settings, motion references, and 3D layouts
  are more exact than words. The common defects are morphing, sliding feet, extra limbs, flicker, and drift. Measure
  joins instead of guessing, and fix defects with shorter clips, simpler motion, stronger references, or another mode.
diagram:
  type: flow
  title: Motion prompt structure
  nodes: ["Start state (or first frame)", "Subject action + speed", "Camera move + speed", "Timing beats (0–2 s, 2–4 s…)", "What stays still", "End state (or last frame)"]
  highlight: [1, 2]
watch:
  - title: "Kling 3.0 — Zhihu overview: multi-shot, motion control, native audio (Chinese)"
    url: https://zhuanlan.zhihu.com/p/2002832521004590013
    note: "Note the per-shot settings: duration, shot size, camera move."
  - title: "ComfyUI docs — Wan 2.2 workflows, including first/last frame"
    url: https://docs.comfy.org/tutorials/video/wan/wan2_2
    note: "Read the first/last-frame section. You can run it with starter workflow 04."
quiz:
  - q: "Your prompt is 'She turns around, walks to the window, opens it, and the camera orbits her.' The result morphs. What is the first fix?"
    options: ["More steps", "One main action and one camera move per clip: split it into 2–3 shots, or keep 'she turns to the window, slow push-in'", "Higher guidance", "Longer clip"]
    answer: 1
    explain: "Several actions plus a complex camera move in one short clip is the most common cause of morphing. Simplify, then cut."
  - q: "You want a match cut from the photo in her hand to the real roof. How do you use first and last frames?"
    options: ["Generate both shots from text", "Make the last frame of shot A an ECU of the photo, and the first frame of shot B the same composition as the real place; generate each with I2V", "Use the same seed", "Use a cross-fade"]
    answer: 1
    explain: "The two frames share a composition, so the cut matches. Each shot only has to reach or leave that frame."
  - q: "A first/last-frame clip of 3 s morphs between the two frames. What is the likely cause?"
    options: ["The frame rate", "The two frames are too different to connect with natural motion in 3 s; bring them closer or make the clip longer", "The prompt is too short", "The codec"]
    answer: 1
    explain: "The model must find a physical motion between the frames. A large change in a short time forces a morph."
  - q: "The join check of a loop gives jump ratio 1.3 and color shift (+6, 0, −7). What do you see when it plays, and what do you do?"
    options: ["Nothing", "The motion is continuous, but the color jumps at the loop point; match the last frame's color to the first frame, or generate with first = last frame", "A frame drop", "A sound pop"]
    answer: 1
    explain: "The ratio measures motion continuity. The shift measures color. Both must pass."
  - q: "The model ignores 'slow dolly left' and makes a zoom. What do you try first?"
    options: ["Write the instruction three times", "Use the model's camera-control setting or a motion reference; if neither exists, describe the parallax: 'the foreground lamp passes the frame from left to right'", "Use T2V", "Raise the frame rate"]
    answer: 1
    explain: "Settings and references are more exact than words. If you only have words, describe what a dolly does in the image: parallax."
  - q: "Feet slide on the floor in a walking shot. Which change is most likely to help?"
    options: ["Add 'realistic' to the prompt", "A follow camera at the same speed, a framing without feet, or a motion reference of a real walk", "More saturation", "A longer clip"]
    answer: 1
    explain: "Foot contact is a known weakness. Hide it with framing, give real motion as a reference, or let the camera move with the subject."
  - q: "Why write 'locked-off camera, background people are still' in a dialogue shot?"
    options: ["It is optional decoration", "Models add motion where you do not say anything; saying what stays still removes random camera drift and background movement", "It makes the clip longer", "It is required"]
    answer: 1
    explain: "A model fills gaps with its own defaults. State the non-motion too."
deeper:
  - title: "He et al. — CameraCtrl: Enabling Camera Control for Text-to-Video Generation"
    url: https://arxiv.org/abs/2404.02101
  - title: "Wang et al. — MotionCtrl: A Unified and Flexible Motion Controller for Video Generation"
    url: https://arxiv.org/abs/2312.03641
  - title: "StudioBinder — camera movement guide"
    url: https://www.studiobinder.com/blog/different-types-of-camera-movements-in-film/
---
## Learn

### Three motions in every prompt
A video prompt must describe motion. There are three kinds:
1. **Subject motion:** what moves, how, and how fast. "She slowly lifts the photo to eye level."
2. **Camera motion:** one move, its direction, and its speed (C02·M02). "Very slow push-in."
3. **Timing:** when things happen. For clips of 8 s or more, write beats: "0–3 s she reads; 3–5 s she looks up; 5–8 s she turns to the locker."

Also say what does **not** move: "locked-off camera", "the people in the background are still", "her hands stay on the photo". A model fills every gap with its own default motion. Saying what stays still removes random drift.

### One action, one move
Each generated clip should have one main action and one camera move. Several actions and a complex move in 5 s are the most common cause of morphing and broken anatomy. If the story needs several actions, plan several shots and cut between them (C02·M04). Editing is cheaper than fighting the model.

### Speed words
Models tend toward a slow, dreamy speed. If you need real-time motion, say it: "real-time speed", "quick", "she snaps the locker shut". Give timing beats for longer clips. If the result is still slow, plan to speed up the clip in the edit by up to about 20 %; more than that makes motion look wrong.

### First and last frames
With first/last-frame control you give the start and the end. The model makes the motion between them. Uses:
- **Transitions and match cuts:** the last frame of shot A and the first frame of shot B share a composition, so the cut matches.
- **Reveals:** the first frame is dark, the last frame is lit.
- **Loops:** the first frame is the last frame.
- **Product turns:** a front view to a side view.

The two frames must be reachable with natural motion in the clip time. A large change in 3 s forces a morph. Bring the frames closer (same lens, smaller move), or make the clip longer.

### When words are not enough
Words are a weak control for camera paths. Use, in this order:
1. **Camera-control settings** of the model (pan, tilt, zoom, orbit, speed), when it has them.
2. **A motion reference:** a video that has the motion you want (a real dolly move, a dance, a walk). R2V and V2V modes accept it.
3. **A 3D layout:** block the scene in 3D, render the camera path as a depth or edge video, and use it as control (C07·M03, C11 starter workflow `05`).
If you have only words, describe what the move does in the image. A dolly makes parallax: "the foreground lamp passes the frame from left to right; the window behind her moves less".

### Common defects and fixes
| Defect | Cause | Fix |
|---|---|---|
| Morphing (a face or an object changes) | Too much motion; weak identity | Shorter clip; one action; references; I2V from a key frame |
| Sliding feet, floating | Weak physics of contact | Follow camera; framing without feet; motion reference |
| Extra fingers or limbs | Fast hand action | Slower action; hide the hands; an insert shot |
| Flicker | Unstable fine detail | Fewer fine textures; deflicker in post (C09) |
| Camera ignores the instruction | Conflicting words | One move only; camera settings; motion reference |
| Slow-motion feel | Model default | "real-time speed"; timing beats; speed up in the edit |
| Drift (color or identity changes over the clip) | Long clip; weak anchor | Shorter clip; first/last frame; re-anchor (M03) |

### Measure joins
A join that must not be seen (a loop, a chained clip, a first/last-frame transition) can fail in two ways:
1. **Motion jump:** the image changes more across the join than between normal neighbor frames.
2. **Color shift:** the motion continues, but the color or brightness jumps.

`starter/tools/join_check.py` measures both. It reads small grey frames near the join. It compares the change across the join (step_join) with the median change between neighbor frames inside the clips (step_inside). The **jump ratio** is step_join / step_inside. About 1 is seamless. Above 3 is a visible jump. It also reports the mean RGB change across the join. Use it on every loop and every chained join. Your eyes miss small jumps on a laptop screen. Viewers on a large screen do not.

## Tool walkthrough

### Camera settings in current products (as of 2026-10)
- **Kling 3.0:** per-shot camera moves in multi-shot mode; start and end frames; motion control.
- **Veo 3.1 / Flow:** first and last frames ("Frames to Video"); camera words work well; Extend for continuation.
- **Seedance 2.5:** 3D white-model references for camera and layout.
- **Open (ComfyUI):** starter workflow `04_flf2v_wan22_14b` (first and last frame), `05_v2v_control_wan22_5b` (control video for exact camera paths), `08_flf2v_ltx25`.

### A first/last-frame run with the starter kit

```bash
python starter/solutions/C11-M04/comfy_run.py \
  --workflow starter/comfyui/workflows/04_flf2v_wan22_14b.json \
  --map starter/comfyui/workflows/04_flf2v_wan22_14b.map.json \
  --upload first_frame=KF-S07-v3.png --upload last_frame=KF-S07-photo-ecu.png \
  --set prompt="Very slow push-in into the photo in her hands. Locked focus on the photo. Real-time speed." \
  --set seed=7
```

### Check a join or a loop

```bash
python starter/tools/join_check.py --loop loop_bg.mp4
python starter/tools/join_check.py S07_t04.mp4 S08_t02.mp4
```

## Worked example

**Calibrate the join check.** We made a 4 s clip with a slow push-in on a portrait photo and cut it at frame 48 (2026-10-04):

| Join | Jump ratio | Color shift (R, G, B) | Result |
|---|---|---|---|
| Frame 47 → 48 of the same push (continuous) | 1.32 | (0.1, 0.1, 0.0) | SEAMLESS |
| The same, but the second half warmed (red +6 %, blue −6 %) | 1.51 | (+6.2, 0.1, −7.4) | COLOR SHIFT |
| 8 frames removed at the join | 6.31 | (2.6, 2.3, 2.1) | VISIBLE JUMP |
| A cut to a different shot | 20.90 | (21.1, 20.4, 22.6) | VISIBLE JUMP |

Two lessons. First, a jump of only 8 frames gives a ratio above 6, so the check is sensitive. Second, the warm join passes the motion test and fails only on color. This is the typical failure of chained generations.

**Transition through the photo** (locker room S07 → hospital roof at dawn S08):
1. Last frame of S07: ECU of the printed photo, filling the frame (an image edit of the key frame).
2. First frame of S08: the same composition, but now it is the real roof (image edit: "turn the photo into a real wide view of the roof, same composition").
3. S07 with first/last frame: start = MCU key frame, end = photo ECU; "very slow push-in into the photo".
4. S08 with I2V: start = roof frame; "camera slowly pulls back; dawn wind in her coat".
5. Cut at the matching frame. `join_check.py S07.mp4 S08.mp4` gives a high ratio, because the content changes on purpose. For a match cut, check by eye that the composition holds across the cut. Use the tool for joins that must be invisible.

## Lab

**Deliverable:** `C05/M02/` with 5 clips, join reports, and a defect log.

1. Make one first/last-frame transition between two of your shots.
2. Make one seamless loop (a background or a product turn). Check it with `join_check.py --loop` until it passes.
3. Make one shot with camera-control settings, a motion reference, or a control video.
4. Make one 8–10 s shot with timing beats.
5. Make one V2V shot with your own recorded motion as the reference.
6. Chain two clips (last frame → first frame). Check the join. If it fails on color, fix the anchor frame and check again.
7. Log every defect: take, defect, cause, fix, result.

**Result checklist**
- [ ] A loop that passes `join_check.py` (report saved).
- [ ] A chained join with its report before and after the fix.
- [ ] Defect log with at least 6 entries; each fix is a specific change.
- [ ] All takes in the take log.

## Model answer

**Defect log (shape of a strong answer):**

| Take | Defect | Cause | Fix | Result |
|---|---|---|---|---|
| S04_t02 | Face morphs at 5 s | 8 s clip, 3 actions | Split into S04a (look) and S04b (walk); 4 s each | ✓ |
| S04b_t01 | Feet slide | Wide shot, floor visible | MS framing, follow camera | ✓ |
| S09_t03 | Camera zooms instead of dolly | Word conflict "push in, dolly left" | Removed "push in"; added parallax description | ✓ on try 2 |
| S11_t01 | Slow-motion feel | Model default | "real-time speed" + beats; sped up 12 % in edit | ✓ |
| LOOP_t02 | Jump at loop | First ≠ last frame | Generated with first = last frame | ratio 1.4, ✓ |
| S07→S08 chain | COLOR SHIFT (+5, 0, −6) | Warm drift in S07 | Color-matched the anchor frame to KF-S07 | ratio 1.2, shift < 2, ✓ |

The summary names the main rule that the log shows: "Most defects came from too much in one clip. After I split actions into separate shots, the reject rate fell from 60 % to 30 %."

The loop report and the chain reports (before and after) are saved as JSON next to the clips. The V2V shot shows the phone reference and the result side by side.
