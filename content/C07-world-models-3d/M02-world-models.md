---
title: Generated worlds and interactive world models
hours: 10
outcomes:
  - Explain what a world model is, and how interactive world streams and 3D world generators differ from video models.
  - Generate a 3D world from text or an image, and use it as a fixed set for many shots.
  - Plan shots in a generated world (positions, lenses, moves) and turn them into video-model shots.
  - Test the current limits of a world model - resolution, coherence over time and distance, scale, editing - and plan around them.
keywords: [world model, generated world, previs, interactive video]
summary: >
  A video model makes a fixed clip. A world model makes a space that you can move through. Interactive world models
  generate a video stream in real time that reacts to your input, but only for a limited time. 3D world generators
  make a scene from text or an image that you can export, often as a Gaussian splat, and use like a captured set. In
  production, a generated world is the fixed truth for layout and camera across many shots, and the video model adds
  detail and life. Test the limits before you plan a project around them.
diagram:
  type: compare
  title: Two kinds of world models
  left:
    title: "Interactive world stream"
    items: ["Frames generated live from your input", "Reacts to movement and actions", "Limited coherence time", "Uses: pitches, exploration, games"]
  right:
    title: "3D world generator"
    items: ["Exports a 3D scene (often a splat)", "Static, stable, re-usable", "Moving characters are weak", "Uses: sets, previs, camera planning"]
watch:
  - title: "Google DeepMind — Genie 3"
    url: https://deepmind.google/discover/blog/genie-3-a-new-frontier-for-world-models/
    note: "Watch the demo clips. Note how the world reacts to input, and where it starts to change."
  - title: "World Labs — Marble"
    url: https://www.worldlabs.ai/
    note: "Look at the examples and the export options (splats)."
quiz:
  - q: "What is the main difference between a video model and an interactive world model?"
    options: ["Resolution", "A video model makes a fixed clip from a prompt; an interactive world model generates frames live from your input, so the view follows your actions", "Audio", "File format"]
    answer: 1
    explain: "The world model is conditioned on actions at every step. That makes it interactive, and also limits how long it stays coherent."
  - q: "You need the same set in 9 shots with different angles. Which tool fits best?"
    options: ["An interactive world stream", "A 3D world generator, exported once, with all 9 shots rendered from it", "Text-to-video for each shot", "A music model"]
    answer: 1
    explain: "An exported 3D scene is static and stable. Every render shows the same layout."
  - q: "In an interactive world, you walk away from a fountain and come back after 60 s. The fountain is now a statue. What is this limit called, and how do you plan around it?"
    options: ["A bug", "Limited coherence over time and distance; keep explorations short, and use exported 3D scenes for anything that must stay the same", "A rendering error", "A license issue"]
    answer: 1
    explain: "Interactive models keep a limited memory. Use them to explore and pitch, not as the source of truth for a set."
  - q: "A generated world looks right, but a chair is as tall as the door. Why does it matter for shots?"
    options: ["It does not", "Scale errors make people and props look wrong in every shot; check scale against a known object (a door is about 2 m) before you plan cameras", "It only matters for VR", "It changes the file size"]
    answer: 1
    explain: "Generated worlds can have wrong scale. A reference object fixes your estimate of every distance and lens choice."
  - q: "Why do you add characters with the video model and not in the generated 3D world?"
    options: ["Characters are not allowed", "3D world generators make static scenes; moving characters are weak there, and the video model handles motion and identity better", "It is cheaper to add them in 3D", "Worlds cannot have people"]
    answer: 1
    explain: "Use each model for its strength: the world for space and camera, the video model for people and motion."
  - q: "Which is a strong use of an interactive world stream in a project?"
    options: ["Final pixels of a feature film", "A pitch or a scouting session: the director walks the idea and chooses angles", "Delivery masters", "Sound design"]
    answer: 1
    explain: "Interaction sells an idea and helps choose shots. Final shots come from stable sources."
  - q: "The far background of a generated world is blurry. How can you hide it in shots?"
    options: ["Raise the resolution of the export", "Plan shots with a shallow depth of field or with the camera toward the detailed area, and let the video model redraw at medium strength", "Use a wider lens", "Add more light"]
    answer: 1
    explain: "Plan around the limit: lens and composition choices, plus the video model's redraw."
deeper:
  - title: "Bruce et al. (2024) — Genie: Generative Interactive Environments"
    url: https://arxiv.org/abs/2402.15391
  - title: "Genie 3 vs Marble vs NVIDIA Cosmos (2026 comparison)"
    url: https://tech-insider.org/genie-3-vs-marble-vs-nvidia-cosmos-world-models-2026/
  - title: "Ha and Schmidhuber (2018) — World Models (the research idea)"
    url: https://arxiv.org/abs/1803.10122
---
## Learn

### What "world model" means
In research, a world model is a model that predicts what happens next in an environment, given an action. In media production the term covers two kinds of tools:
1. **Interactive world streams.** The model generates the next frames from the frames before and your input (move forward, turn left, open the door). The output is a video stream that follows your actions in real time.
2. **3D world generators.** The model makes a 3D scene from text, an image, a panorama, or a video. You export the scene, often as a Gaussian splat (M01), and use it like a captured set.

A normal video model makes a fixed clip from a prompt. It has no action input, and it does not export a space.

### Interactive streams: strengths and limits
An interactive model must make each frame fast, and it can keep only a limited memory of what it showed before. So:
- **Coherence is limited** in time and distance. If you walk away and come back, things can change.
- **Resolution and detail** are lower than top video models.
- **Control** is through actions, not through exact camera parameters.
Use interactive streams for exploration and pitches: a director walks through an idea, and you record the views that work.

### 3D world generators: strengths and limits
An exported 3D world is static. Every render shows the same layout. That makes it a good set:
- **Strengths:** one consistent place for many shots; exact camera moves (render them like a splat capture, M01); fast variants of a location.
- **Limits:** soft or blurry far areas; seams; wrong scale (a chair as tall as a door); weak moving characters; limited editing.

### How to use a generated world in production
1. **Design the location:** generate 3–5 variants from your look bible (C04·M04). Choose one. Freeze it as the location reference (C04·M03).
2. **Check the scale** against a known object: a door is about 2.0 m high, a table about 0.75 m, a step about 0.18 m.
3. **Plan shots:** place the camera positions, choose real focal lengths, and record the moves (C02·M02).
4. **Render** each move at your working size and frame rate.
5. **Generate** the final shots with I2V or V2V, using the renders. Add the characters and the life with the video model and your references.
6. **Keep** the world file and the renders with the project. Every later shot in the same place starts from them.

### Plan around the limits
- Blurry backgrounds: shallow depth of field, or point the camera toward the detailed area.
- Seams: avoid camera paths that cross them; let the video model redraw at medium strength.
- Scale: fix it in the world before you plan lenses, or scale the camera height and speed to match.
- Short coherence (interactive): record short clips; do not plan a long continuous shot.

## Tool walkthrough

### Current world models (as of 2026-10)
- **Genie 3** (Google DeepMind): interactive world stream; available to Google AI Ultra users via Project Genie since January 2026; about 720p at 24 fps, with about 60 s of coherence.
- **Marble** (World Labs): 3D world generator from text, an image, a panorama, or a video; exports Gaussian splats (a full version of about 2 M splats, or a light version of about 500 k). Reports say Sony Pictures used it for virtual-production previs.
- **NVIDIA Cosmos:** world models mainly for robotics and simulation; useful for physics-aware synthetic video.

### A world-to-shot pipeline
1. Concept frame from your image model (C04), in the look of the bible.
2. World generator → export the splat.
3. Open it in a splat viewer or editor (M01). Check the scale with a door or a table.
4. Record moves at 24 fps with real focal lengths.
5. Video model: I2V from the first frame of each render, or V2V with a depth or edge control from the render (C11 starter workflow `05`).

## Worked example

**Sci-fi short: an abandoned greenhouse on Mars, 9 shots.**
1. Concept frame from the image model: "abandoned greenhouse dome on Mars, broken glass panels, dead plants, red dust, low sun".
2. The world generator made a splat world (light version) in a few minutes. Scale check: the door was 2.9 m high. We scaled the world to 69 % so the door is 2.0 m.
3. In the viewer: 6 camera positions, 3 moves (a slow push through the door, 28 mm; a pan across the dead plants, 50 mm; a crane-up to the broken roof, 24 mm).
4. Renders at 1280 × 704, 24 fps. The far end of the dome was blurry, so the pan uses a shallow depth of field and the near plants.
5. I2V and V2V with the renders: added drifting dust, the astronaut (character references), and the light change.
6. Result: all 9 shots share one set. The broken panel above the door is in the same place in every shot.

## Lab

**Deliverable:** `C07/M02/` with a generated world, a scale check, 3 renders, 3 final shots, and a limits report.

1. Generate a world for the main location of your story with any 3D world generator. If you have access to an interactive world model, also record a 30–60 s exploration.
2. Check the scale against a known object. Fix it, or write the factor.
3. Plan 3 shots in the world: position, focal length, move, duration. Record the 3 moves.
4. Make 3 final shots with a video model from the renders.
5. Test the limits: one long move (does the world hold?), one view of the far background (detail?), and in an interactive model, a return to a place after 60 s (does it stay the same?).
6. Write the limits that you hit and how you worked around them.

**Result checklist**
- [ ] World file or viewer link, and the scale check.
- [ ] 3 renders and 3 final shots, with lens and move written down.
- [ ] Limits report with a workaround for each limit.

## Model answer

**Limits report (shape of a strong answer):**

| Test | Result | Workaround |
|---|---|---|
| Scale | Door 2.6 m → scaled to 77 % | Scale before planning lenses |
| Long move (8 s through the room) | Seam visible at 5 s on the right wall | Shortened to 4 s; cut to a reverse angle |
| Far background | Soft beyond about 6 m | 50 mm with shallow depth of field; camera toward the near props |
| Interactive return after 60 s | The fountain became a different shape | Used the interactive model only for the scouting video |

"The world was the truth for layout and camera. The video model added the people and the dust. In 3 final shots, the window and the broken lamp are in the same places. A text-to-video version of shot 2 put the window on the other side of the room."
