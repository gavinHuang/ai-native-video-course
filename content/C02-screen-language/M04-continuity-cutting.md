---
title: Continuity and cutting
hours: 8
outcomes:
  - Apply the 180-degree rule, screen direction, and eyeline match.
  - Plan match cuts, cut on action, J-cuts, and L-cuts.
  - Control rhythm and pace with shot length.
  - Plan generated shots so that they cut together.
keywords: [180-degree rule, screen direction, match cut, J-cut, L-cut, pacing]
summary: >
  Continuity makes separate shots feel like one space and one time. Keep the camera on one side of the action line,
  the 180-degree rule, so that people keep their left and right positions. Keep screen direction: a character who
  exits right enters the next shot from the left. Match eyelines between speakers. Cut on action to hide the cut.
  J-cuts and L-cuts let sound lead or follow the picture. Rhythm comes from shot length. For AI shots, plan
  continuity before generation: same light direction, same costume, same direction of travel.
diagram:
  type: flow
  title: Plan continuity before generating
  nodes: ["Draw the action line (180°)", "Fix screen direction for each character", "Fix light direction + time of day", "Fix wardrobe, props, hair state", "Plan cut points on action", "Generate shots with these constraints"]
  highlight: [5]
watch:
  - title: "StudioBinder — The 180 Degree Rule in Film"
    url: https://www.studiobinder.com/blog/what-is-the-180-degree-rule/
    note: "Read with the diagrams; note the 'crossing the line' examples."
  - title: "Every Frame a Painting — How Does an Editor Think and Feel? (YouTube search)"
    url: https://www.youtube.com/results?search_query=every+frame+a+painting+how+does+an+editor+think+and+feel
    note: "Open the first result from the Every Frame a Painting channel. Watch all (10 min)."
quiz:
  - q: "In shot A, person 1 is left and person 2 is right. In shot B (reverse), the camera crossed the line. Effect?"
    options: ["Nothing", "They seem to swap sides; the viewer is confused", "Better rhythm", "The light changes"]
    answer: 1
    explain: "Crossing the 180° line flips screen positions."
  - q: "What is an L-cut?"
    options: ["Audio of shot A continues over the start of shot B", "Audio of shot B starts before its picture", "A cut on a dissolve", "A jump cut"]
    answer: 0
    explain: "The audio track looks like an 'L' on the timeline. A J-cut is the reverse: the next sound arrives first."
  - q: "A rider exits frame right in shot 1. In shot 2 (continuing travel), they should enter from:"
    options: ["Right", "Left", "Top", "Any side"]
    answer: 1
    explain: "Consistent screen direction shows continued travel."
  - q: "Why do generated shots often fail to cut together?"
    options: ["Models cannot make 24 fps", "Each generation chooses its own light direction, wardrobe details, and direction of motion", "Codecs differ", "They are too short"]
    answer: 1
    explain: "Without constraints and references, every clip invents its own continuity."
  - q: "Two takes of a medium shot differ only by a small reframing. You cut from one to the other. What happens?"
    options: ["A smooth cut", "An unwanted jump cut: change the angle by at least 30° or the size by at least one step", "A match cut", "An L-cut"]
    answer: 1
    explain: "Small changes between similar shots look like errors."
  - q: "At a cut between two generated shots, the room sound changes from a quiet hum to silence. What do you do?"
    options: ["Nothing", "Lay one continuous room tone under the whole scene (C08), so the background sound does not jump at the cut", "Cut faster", "Add music only"]
    answer: 1
    explain: "Sound continuity is as noticeable as picture continuity, and easier to fix."
deeper:
  - title: "Murch — In the Blink of an Eye (book, the 'rule of six')"
    url: https://en.wikipedia.org/wiki/In_the_Blink_of_an_Eye_(Murch_book)
  - title: "Wikipedia — Continuity editing (overview and terms)"
    url: https://en.wikipedia.org/wiki/Continuity_editing
---
## Learn

### The 180-degree rule
Draw an imaginary line through two people who talk (or along a direction of travel). Keep all cameras on one side. Then person 1 stays on the left and person 2 on the right in every shot. If you need to cross, show the move on screen, or cut to a neutral shot on the line.

![The 180-degree rule: cameras 1–3 stay on one side of the action line](fig:rule-180.svg)

### Screen direction and eyeline
- A character who moves left to right keeps that direction until a visible turn.
- In dialogue, person 1 looks frame right; person 2 looks frame left. Their **eyelines** meet.

![Keep screen direction across the cut; in dialogue the eyelines meet](fig:eyeline.svg)

### The 30-degree rule and size steps
Between two shots of the same subject, change the camera angle by at least 30°, or the shot size by at least one step (for example MS to CU). A smaller change looks like a mistake: a jump cut that you did not want. The same applies to generated shots. Two takes of the same prompt with a slightly different framing do not cut together. Choose one, or make the second one clearly closer or from a different angle.

![Change the angle by at least 30°, or the size by at least one step](fig:rule-30.svg)

### Cut types
- **Cut on action:** cut during a movement (a door opens, a hand reaches). The movement hides the cut.
- **Match cut:** two shots linked by shape, motion, or idea (a spinning wheel → a spinning coin).
- **J-cut:** the sound of the next shot starts before its picture. It pulls the viewer forward.
- **L-cut:** the sound of the current shot continues over the next picture. It lets a moment breathe.
- **Jump cut:** a cut inside the same shot with a time jump. Energy; common in creator videos.
- **Cutaway / insert:** a detail shot. It also hides a continuity problem.

![J-cut and L-cut: the sound cut and the picture cut happen at different times](fig:j-l-cuts.svg)

### Murch's rule of six
Walter Murch ranks what makes a good cut: emotion (51%), story (23%), rhythm (10%), eye trace (7%), 2D plane (5%), 3D space (4%). Emotion first. A small continuity error is fine if the emotion is right.

![Murch's rule of six: what matters most at a cut](fig:murch-six.svg)

### Rhythm and pace
Shot length makes rhythm. Short shots = energy. Long shots = calm or tension. Cut when the shot has given its information or its emotion, not when the clip ends. Social video in 2026 often cuts every 1–3 s at the start (the hook) and then slows. Vary length; a constant length feels mechanical.

![Varied shot length, with a fast hook, against a mechanical constant length](fig:rhythm.svg)

### What to watch at a cut
At every cut, check the position of the subject in the frame (eye trace: the eye should find the subject quickly after the cut). Check the direction of movement, the eyeline, the light side, and wardrobe, props, and hair. Check the sound too: a room tone that changes at the cut is very noticeable (C08). Review cuts at full speed first, as a viewer, then frame by frame. Many small errors are invisible at full speed. Fix only what a viewer would notice, and spend the saved time on the errors that break the emotion (Murch's rule).

### Continuity for AI
Every generation is independent. The model does not know the previous shot unless you give it a reference or a frame from it. You must carry continuity yourself:
- Same light direction and time of day in every prompt of a scene.
- Same wardrobe and prop words, the same references, every time.
- Direction words: "walks from left to right".
- Plan the cut point. Generate 1 s more before and after it ("handles").
- Use first/last frames to join shots exactly (C05·M03).

![Handles: generate about 1 s more before and after the planned cut](fig:handles.svg)

## Tool walkthrough

### Check joins and continuity
```bash
python starter/tools/join_check.py shot02.mp4 shot03.mp4        # color, brightness, and motion jump at the join (C05·M03)
python starter/tools/frame_diff.py shotA_last.png shotB_first.png  # how different two frames are
```
Use the numbers to find the worst cuts quickly; decide with your eyes.

## Worked example

**Dialogue scene with generated shots.** Two people at a café table. Window light from frame left (for camera side A).

1. Wide two-shot: A on left, B on right, window left, "late afternoon warm light from the left".
2. OTS on B (over A's right shoulder): B looks frame left. Light on B comes from... the window is now behind camera-left. Write: "warm window light from frame left, B looks slightly left of the lens".
3. Reverse OTS on A: A looks frame right. Light from frame left-behind: "warm rim light from the right edge of frame" (the window is now behind A).
4. Insert: B's hand turns the cup — cut on the action from shot 2.
5. Edit: an L-cut. A's line continues over B's reaction in shot 2.

The plan writes the light direction for each camera position. Without it, the model puts the light where it likes, and the scene breaks.

## Lab

**Deliverable:** `C02/M04/` with a top-view diagram, 5 shots, and a 30 s edit.

1. Draw a top-view plan of a two-person scene: the action line, camera positions, and the window.
2. Write 5 shot prompts with continuity constraints (light direction, eyeline, wardrobe words).
3. Generate the shots (image-to-video from consistent frames is easiest).
4. Edit them into a 30 s scene in any editor. Use at least one L-cut or J-cut (use any generated or recorded dialogue).
5. List every continuity error you see, and the cause.

**Result checklist**
- [ ] Top-view plan with line and cameras.
- [ ] 5 shots that respect the line.
- [ ] 30 s edit with a J- or L-cut.
- [ ] Error list with causes.

## Model answer

Typical errors and causes: light flips side in the reverse shot (prompt did not state direction for that camera); coffee cup changes color (no prop reference); B's jacket changes buttons (no character reference or LoRA); B looks into the lens (prompt said "looks at camera" by mistake). Fixes: one reference board per scene; light direction per camera position; eyeline words "looks slightly off-camera left"; an insert shot to hide unsolved mismatches.

**Error list (shape):** "Cut 2→3 (00:08): light side flips; cause: no light direction for camera 3; fix: re-generated with 'warm rim light from frame right'. Cut 4→5 (00:19): cup changes from white to grey; cause: no prop reference; hidden with an insert of the hand. Cut 1→2: room tone jumps; fixed with one continuous room tone." Each line has a timecode, a cause, and a fix.
