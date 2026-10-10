---
title: 3D layout for exact camera, and real-time engines
hours: 20
outcomes:
  - Block out a scene in 3D (a white box) at real scale, with a camera at real focal length and speed.
  - Calculate the field of view and the frame width from focal length, sensor size, and distance.
  - Render depth, edge, and clay passes, and use them as control videos for video models.
  - Use a real-time engine for previs, and explain LED-volume virtual production and where AI fits.
keywords: [white box, previs, virtual production, depth control, Unreal Engine]
summary: >
  A white box is a simple 3D block-out of a scene: grey boxes for walls and furniture, simple mannequins for people,
  all at real scale. With it you control the exact camera path, lens, and timing. Render the white box as depth,
  edges, or clay shading, and use those renders as the control video of a video model. Then the camera move and the
  layout are exact, and the model adds the look. Real-time engines do the same job interactively and are the base of
  LED-volume virtual production.
diagram:
  type: flow
  title: White box to final shot
  nodes: ["Top-view plan (C04·M03)", "White box at real scale", "Camera: real lens, real speed", "Render depth / edges / clay", "Video model with control + references", "Shot matches the plan"]
  highlight: [3]
watch:
  - title: "Unreal Engine — virtual production hub"
    url: https://www.unrealengine.com/en-US/virtual-production
    note: "Look at the LED-volume and previs case studies."
  - title: "Blender — official getting-started tutorials"
    url: https://www.blender.org/support/tutorials/
    note: "Do the navigation and camera animation lessons (about 1 hour)."
quiz:
  - q: "On a full-frame sensor (36 mm wide), what is the horizontal field of view of a 35 mm lens?"
    options: ["About 24°", "About 54°", "About 90°", "About 10°"]
    answer: 1
    explain: "FOV = 2 × atan(36 / (2 × 35)) ≈ 54.4°. An 85 mm lens gives about 23.9°."
  - q: "The camera is 2.4 m from an actress, with a 35 mm lens on a 36 mm sensor. How wide is the frame at her distance?"
    options: ["About 0.5 m", "About 2.5 m (2.4 × 36 / 35)", "About 10 m", "About 1 m"]
    answer: 1
    explain: "Frame width = distance × sensor width / focal length. 2.4 × 36 / 35 ≈ 2.47 m. That is a medium-wide shot, not a close-up."
  - q: "Why must a white box be at real scale?"
    options: ["For the file size", "Lens, distance, and speed only look right at real scale; a door that is 3 m high makes every person look small and every move look slow", "Engines need it", "It renders faster"]
    answer: 1
    explain: "A white box is a measurement tool. Wrong scale gives wrong framing and wrong motion."
  - q: "Which render pass gives a video model the strongest control of layout and camera?"
    options: ["A color render of grey boxes", "A depth pass: every pixel says how far the surface is, so the model must keep the 3D layout", "A normal map only", "A wireframe"]
    answer: 1
    explain: "Depth fixes space. Edges fix outlines. A clay render is useful as a V2V source or reference."
  - q: "The video model ignores a thin pole in the depth video. Why, and what do you do?"
    options: ["The pole is too dark", "Thin objects are small in a depth map and easy to lose at the control resolution; make them thicker in the white box or add an edge pass", "Use a longer lens", "Remove the pole"]
    answer: 1
    explain: "Control maps are low resolution inside the model. Make important thin objects bigger, or add edges."
  - q: "In an LED volume, why does the camera need tracking?"
    options: ["For autofocus", "The engine must render the background with the correct perspective for the real camera position and lens, so the wall looks right from the camera", "For sound", "To save power"]
    answer: 1
    explain: "The LED wall is a window into a 3D world. Without tracking, the parallax is wrong."
  - q: "Where does AI fit into LED-volume virtual production today?"
    options: ["It replaces the volume", "World building: generated textures, skies, and splat sets; and previs renders made final-looking with video models", "Only in sound", "Nowhere"]
    answer: 1
    explain: "AI makes worlds and previs faster. The volume still captures real actors and real light in camera."
deeper:
  - title: "Blender manual — cameras"
    url: https://docs.blender.org/manual/en/latest/render/cameras.html
  - title: "ComfyUI docs — depth ControlNet"
    url: https://docs.comfy.org/tutorials/controlnet/depth-controlnet
  - title: "Wikipedia — Angle of view (formula and tables)"
    url: https://en.wikipedia.org/wiki/Angle_of_view
---
## Learn

### The white box
A white box (also: block-out, layout, grey box) is a simple 3D model of a scene. Walls, doors, windows, and furniture are boxes. People are simple mannequins at their real height. Nothing has texture. The white box answers the questions that words cannot: where things stand, how far the camera is, and how the camera moves.

Rules:
- **Real scale** in meters. A door is about 2.0 m high and 0.9 m wide. A person is 1.6–1.9 m. A table is 0.75 m high.
- **People face somewhere.** Add a marker (a small nose block) that shows the facing direction. This makes eyelines and the 180° rule visible (C02·M04).
- **Start from the top-view plan** of the environment sheet (C04·M03).

### Camera math
A camera in 3D uses the same optics as a real camera. Two formulas let you plan shots:

```
horizontal field of view = 2 × atan(sensor width / (2 × focal length))
frame width at distance d = d × sensor width / focal length
```

On a full-frame sensor (36 mm wide):

| Focal length | Field of view | Frame width at 2.4 m |
|---|---|---|
| 24 mm | 73.7° | 3.60 m |
| 35 mm | 54.4° | 2.47 m |
| 50 mm | 39.6° | 1.73 m |
| 85 mm | 23.9° | 1.02 m |

So a close-up of a face (about 0.4 m of frame height) at 2.4 m needs a long lens, or the camera must come closer. The white box makes these choices visible before you generate.

Move the camera at real speed. A slow push-in is about 0.1–0.3 m/s. A walking-speed dolly is about 1.2 m/s.

### Render passes as control
Render the white box along the camera path as several passes. Each pass is a control signal (C11·M02):
- **Depth:** every pixel's distance from the camera, as a grey value (near = white). It fixes the 3D layout and the camera move. It is the strongest layout control.
- **Edges:** the outlines of objects, found where depth changes. It fixes shapes and silhouettes.
- **Clay:** grey, softly lit shading. Use it as a V2V source at high strength, or as a layout reference.
- **Pose:** the skeleton of animated mannequins, for pose control.

Feed the pass as the control video of a video model, with references for the look and the characters. The camera move and the layout then follow the plan exactly. The model adds materials, light, and people.

Thin objects (poles, cables, chair legs) are small in a depth map and easy to lose inside the model, which works at a lower resolution. Make important thin objects thicker in the white box, or add the edge pass.

### Real-time engines
A real-time engine renders 3D at interactive speed. It is the standard tool for previs and virtual production. AI fits in at several points:
- generated textures, skies, and backgrounds;
- splats from captures (M01) or world generators (M02), imported as sets;
- previs renders made final-looking with video models (animatics with the final look);
- generated plates for LED walls.

### LED volumes in short
An LED volume is a large curved LED wall (and often a ceiling). The engine shows a 3D world on it. The camera is tracked, and the engine renders the world with the correct perspective for the camera position and lens, so the wall looks like a real place from the camera. The wall also lights the actors. Final pixels are captured in camera. AI speeds up building the worlds for the wall.

## Tool walkthrough

### A white box from a JSON layout (open, scripted)
`starter/tools/whitebox.py` builds a room, boxes, and mannequins from a JSON layout, animates a camera with a real lens, and renders depth, edges, and clay videos. It uses Blender's Python module, so it runs without opening Blender:

```bash
pip install bpy opencv-python-headless numpy     # bpy needs Python 3.11
python starter/tools/whitebox.py layout.json --out wb/S07/ --res 640x352
# -> wb/S07/depth.mp4, edges.mp4, clay.mp4, first_frame_clay.png
```

`layout.json` (meters; z is up):

```json
{"fps": 24, "seconds": 2,
 "room": {"w": 6, "d": 4, "h": 2.7, "door": {"wall": "back", "x": 1.0, "w": 0.9, "h": 2.0},
          "window": {"wall": "left", "y": 1.0, "w": 1.2, "h": 1.0, "sill": 0.9}},
 "boxes": [{"name": "lockers", "pos": [-1.5, 3.5, 0], "size": [2.4, 0.5, 1.9]},
           {"name": "bench", "pos": [0, 1.6, 0], "size": [1.8, 0.4, 0.45]}],
 "people": [{"name": "MARA", "pos": [0.3, 2.2, 0], "height": 1.68, "facing": 180}],
 "camera": {"lens_mm": 35, "sensor_mm": 36,
            "from": {"pos": [0.2, -0.2, 1.5], "look": [0.3, 2.2, 1.4]},
            "to":   {"pos": [0.25, 0.8, 1.5], "look": [0.3, 2.2, 1.5]}}}
```

Then use `depth.mp4` or `edges.mp4` as `control_video` in starter workflow `05_v2v_control_wan22_5b`, with a start frame from your references as `ref_image`.

### Blender and Unreal by hand
- **Blender:** add a camera (Add → Camera), set the focal length in the camera properties, set two keyframes on its location (press I over the field), and add a Track To constraint to an Empty for the look target. Render the depth pass from the View Layer passes (Z or Mist).
- **Unreal Engine:** a Cine Camera Actor with a real lens and sensor; Sequencer for the camera move; Movie Render Queue for passes.

## Worked example

**Push-in on Mara in the locker room** (2026-10-04). The layout above: a 6 × 4 × 2.7 m room, lockers, a bench, a door, a window, and a 1.68 m mannequin facing the camera. The camera pushes in from 2.4 m to 1.4 m in 2 s, with a 35 mm lens.

- Frame width at the start: 2.4 × 36 / 35 = 2.47 m (a medium-wide shot). At the end: 1.4 × 36 / 35 = 1.44 m (a medium shot).
- The speed is 0.5 m/s, a slightly fast push for a quiet moment. For the final shot we used 4 s (0.25 m/s).
- `whitebox.py` rendered 48 frames of depth, edges, and clay at 640 × 352 in 25 s on a laptop CPU.

What the passes showed before any generation:
1. Her head touches the edge of the dark door opening behind her, so the silhouette of her head merges with the door frame. We moved the camera 0.3 m to the left.
2. The bench is out of frame for the whole move: at 1.5 m camera height, the lower edge of the frame is 0.7–1.1 m above the floor at her distance (vertical field of view 31.6° at this aspect ratio), and the bench top is at 0.45 m. If the story needs the bench (she sits down), lower the camera or start further back.

The depth video then became the control video of workflow `05`, with the approved key frame `KF-S07-v3` as the reference image.

## Lab

**Deliverable:** `C07/M03/` with a layout file, render passes, 2 final shots, a 20 s previs, and a lens plan.

1. Write the layout of one location of your story at real scale (from your top-view plan). Include the people and their facing.
2. Plan 2 camera moves. For each, write the focal length, the distance, the frame width (with the formula), and the speed in m/s.
3. Render depth, edges, and clay for both moves (with `whitebox.py`, Blender, or Unreal).
4. Fix what the passes show (merges, objects out of frame, wrong scale), and render again.
5. Make 2 final shots with a video model controlled by the depth or edge pass.
6. Make a 20 s previs from the clay renders with temp sound, and use it to approve the timing.

**Result checklist**
- [ ] Layout file and lens plan with calculated frame widths.
- [ ] Render passes, before and after one fix.
- [ ] 2 controlled shots that match the planned moves (show plan and result side by side).
- [ ] 20 s previs.

## Model answer

**Lens plan (shape of a strong answer):**

| Shot | Lens | Distance | Frame width | Move | Speed |
|---|---|---|---|---|---|
| S07 push-in | 35 mm | 2.4 → 1.4 m | 2.47 → 1.44 m | dolly in | 0.25 m/s |
| S09 profile | 85 mm | 3.0 m | 1.27 m | locked | — |

"The S09 plan showed that 85 mm at 3.0 m gives 1.27 m of frame width: a medium close-up. The room is 4 m deep, so the camera fits. At 50 mm the lockers behind her would be in frame and compete with her face."

**Fix log:** "Pass v1: her head merged with the edge of the door. Moved the camera 0.3 m left (v2). Pass v1 of S09: the thin coat hooks disappeared in the depth map; made them 3 cm thick and added the edge pass."

The controlled shots match the planned moves within a few frames. The previs shows that S07 needs 4 s, not 2 s, so the shot list was updated before any paid generation.
