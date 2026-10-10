---
title: Lens language and camera movement
hours: 8
outcomes:
  - Explain how focal length changes perspective, space, and feeling.
  - Use depth of field to guide attention.
  - Name the main camera moves and the meaning of each.
  - Write camera instructions that video models follow.
keywords: [focal length, depth of field, camera movement, dolly, motivated movement]
summary: >
  Focal length changes how space looks. A wide lens makes space deep and close faces distorted. A long lens
  compresses space and isolates the subject. Depth of field decides what is sharp. Shallow focus guides the eye.
  Camera movement must have a reason. A push-in raises attention or emotion. A pull-out reveals or isolates. A
  tracking shot follows action. A handheld camera adds urgency. In prompts, name the lens, the focus, and one clear
  camera move per shot.
diagram:
  type: layers2d
  title: Camera moves and their meaning
  rows: ["Push-in (dolly in)", "Pull-out (dolly out)", "Pan / tilt", "Tracking / truck", "Orbit (arc)", "Crane / jib up", "Handheld"]
  cols: ["Camera action", "Typical meaning"]
  cells:
    - ["Moves toward subject", "Growing attention, realization"]
    - ["Moves away", "Reveal context, isolation, ending"]
    - ["Rotates on the spot", "Follow, show relation, reveal"]
    - ["Moves beside or behind subject", "Journey, energy, follow action"]
    - ["Circles around subject", "Importance, hero moment, product"]
    - ["Rises above the scene", "Scale, ending, freedom"]
    - ["Small natural shake", "Urgency, documentary, chaos"]
watch:
  - title: "StudioBinder — Ultimate Guide to Camera Movement"
    url: https://www.youtube.com/watch?v=IiyBo-qLDeM
    note: "Watch all. Note the reason for each move."
  - title: "Every Frame a Painting — Edgar Wright: How to Do Visual Comedy"
    url: https://www.youtube.com/watch?v=3FOzD4Sfgag
    note: "Watch for camera moves and cuts that are timed to action."
quiz:
  - q: "You want a crowded street to look dense and compressed. Lens?"
    options: ["14 mm ultra wide", "35 mm", "135 mm telephoto", "Fisheye"]
    answer: 2
    explain: "Long lenses compress distance between layers. The crowd looks packed."
  - q: "What does a slow push-in on a face usually mean?"
    options: ["Comedy", "Growing tension or a realization", "End of the film", "Nothing"]
    answer: 1
    explain: "The frame closes in as the character's inner state intensifies."
  - q: "Best practice for camera moves in one AI video generation?"
    options: ["Ask for 4 moves in 5 seconds", "One clear move per shot, with direction and speed", "Never mention the camera", "Always use handheld"]
    answer: 1
    explain: "Models follow one clear instruction well. Many moves in one clip give chaotic motion."
  - q: "f/1.4 vs f/11 at the same focal length. Which has shallower depth of field?"
    options: ["f/11", "f/1.4", "Same", "Depends on frame rate"]
    answer: 1
    explain: "A wider aperture (small f-number) gives shallower focus."
  - q: "You want a calm interior to feel deep in a 5 s generated shot. Which move helps most?"
    options: ["A fast whip pan", "A slow lateral track with an object in the foreground, so parallax shows the depth", "A zoom in", "Handheld shake"]
    answer: 1
    explain: "Parallax is the strongest depth cue. Slow moves also give cleaner model output."
  - q: "A fight scene should feel harsh and urgent, with sharp, stuttering motion. Which shutter look do you ask for?"
    options: ["A 180° shutter, natural blur", "A short (fast) shutter: crisp frames with little motion blur", "A long shutter, smeared motion", "60 fps slow motion"]
    answer: 1
    explain: "Short shutters remove blur and make motion staccato. 180° is the natural default."
deeper:
  - title: "Brown — Cinematography: Theory and Practice (book)"
    url: https://www.routledge.com/Cinematography-Theory-and-Practice-For-Cinematographers-and-Directors/Brown/p/book/9780367373467
  - title: "Google Cloud — Veo prompt guide (camera and lens terms)"
    url: https://cloud.google.com/vertex-ai/generative-ai/docs/video/video-gen-prompt-guide
---
## Learn

### Focal length
Focal length (in mm, for a full-frame camera) changes perspective.
- **Wide (14–24 mm):** deep space, strong perspective lines; faces close to the lens look distorted. Use for spaces, action, and unease.
- **Normal (35–50 mm):** close to human vision. Neutral and honest.
- **Portrait (85 mm):** flattering faces, background soft.
- **Telephoto (135 mm+):** compressed space, isolated subject, a "watching from far" feeling.

Video models understand these numbers. "24 mm" and "135 mm" give visibly different perspective.

![Same face size, four lenses: a longer lens shows less background, larger and softer](fig:focal-length.svg)

### Depth of field
**Depth of field** (DOF) is the zone that is sharp. Shallow DOF (wide aperture, long lens, close subject) isolates the subject and guides the eye. Deep DOF (small aperture, wide lens) shows the whole scene. A **rack focus** moves focus from one subject to another during the shot. It moves attention. Models can do rack focus when you name the start and end subject.

![Shallow and deep depth of field, and a rack focus from the face to the background](fig:depth-of-field.svg)

### Camera movement
See the diagram. The rule: every move needs a **motivation**. Good motivations:
- The subject moves (follow it).
- The story reveals something (pull out, pan to it).
- The emotion changes (push in).

A move without motivation feels like a demo reel. Also decide speed (slow, steady, fast) and direction (left, right, toward, away).

![The main camera moves; the orange arrow is the path of the camera](fig:camera-moves.svg)

### Stabilized vs handheld
- Gimbal or dolly: smooth, controlled, "cinematic".
- Handheld: shake, breath, urgency. Real documentary feeling.
- Locked-off (tripod): stillness. Lets the action speak. Often the best choice for AI shots, because fewer things move.

![The path of the frame centre over a few seconds](fig:stabilization.svg)

### Frame rate, shutter, and motion blur
Film and most drama use **24 fps**; TV and online video also use 25 or 30 fps; sport and games use 50–60 fps. Each frame is exposed for a time set by the **shutter**. The common rule is a 180° shutter: exposure = half the frame time (1/48 s at 24 fps). It gives natural motion blur. A short shutter (1/500 s) gives sharp, stuttering frames: tense, "war footage". A long shutter gives smeared, dreamy motion. Generated video imitates this blur from its training data; ask for "natural motion blur" or "crisp, fast shutter" when it matters. Slow motion is filmed at a high frame rate and played at 24 fps.

![One frame of a moving ball at 24 fps: the shutter time sets the blur](fig:shutter.svg)

### Parallax and speed
A camera that moves sideways makes near objects pass faster than far ones. This is **parallax**, and it is the strongest cue of depth. A slow lateral move with a foreground object (a pillar, a plant) makes a flat scene deep. Fast moves through complex scenes are hard for models: the background can warp. Keep moves slow and the scene simple when quality matters, and add speed in the edit (C02·M04).

![Parallax: in a sideways move, near objects cross the frame faster than far ones](fig:parallax.svg)

### Moves that are hard for models
- **Long orbits** around a complex subject: the back of the subject and the background must be invented, and they warp.
- **Moves through doors and windows:** the model must invent a new space, and it often changes the first one.
- **Combined moves** (crane up while panning and pushing in): choose one.
- **Fast whip pans:** the blur hides the cut; generate two shots and join them with a whip-pan transition in the edit instead.
For these, use first and last frames or a 3D layout (C05·M05).

![Moves that make the model invent space it has not seen](fig:hard-moves.svg)

### Camera language in prompts
Write the camera like a camera operator:
`[move] [direction] [speed], [lens], [focus]`
Example: "Slow dolly in toward her face, 85 mm, shallow depth of field, focus on the eyes."

Model behavior (as of 2026-10, from practitioners): some models need short camera words; some need detail. Many tools also offer separate camera-control parameters or camera paths (see C05·M05). Use them when they exist, because they are more exact than words.

## Worked example

**Same moment, three lenses:** a runner on a bridge at sunrise.

1. "Wide shot, 16 mm, low angle, the runner passes very close to the lens, strong perspective lines of the bridge rails, fast tracking shot following from the side." → energy, speed.
2. "Medium shot, 50 mm, eye level, steady tracking shot, runner centered, natural perspective." → neutral, documentary.
3. "Wide shot, 200 mm telephoto from far away, the runner small, the bridge and the sun compressed behind, locked-off camera." → loneliness, scale.

Each prompt has one move (or none), a lens, and a reason.

## Lab

**Deliverable:** `C02/M02/` with 6 clips and a review table.

1. Choose one action (for example "a person opens an old letter").
2. Generate 3 clips with the same prompt except the lens: 16 mm, 50 mm, 135 mm.
3. Generate 3 clips with the same lens but different moves: push-in, orbit, locked-off.
4. For each clip: did the model follow the lens? the move? Was the motion clean?
5. Write which version gives which feeling, in one sentence each.

**Result checklist**
- [ ] 6 clips with prompts in the log.
- [ ] Review table: lens followed / move followed / defects.
- [ ] 6 sentences about the feeling of each version.

## Model answer

Usual results: lens differences are clear in background blur and compression. The 16 mm version shows wide-angle distortion on the hands. Push-in is followed well; orbit is followed well when the subject is simple, and gives background warping when the scene is complex. Locked-off gives the cleanest motion, with fewest defects. Feelings: push-in = discovery; orbit = importance; locked-off = quiet observation; 135 mm = distance, privacy.

**Review table (shape):**

| Clip | Lens followed | Move followed | Defects |
|---|---|---|---|
| 16 mm | yes (strong perspective) | n/a | hands stretched near the lens |
| 135 mm | yes (flat, soft background) | n/a | none |
| Orbit | n/a | partly (stopped at 3 s) | background lamp bent during the move |

The strong answer names the defect, the time, and a fix for the next try (for example "a simpler background for the orbit").
