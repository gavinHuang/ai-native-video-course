---
title: 3D representations - mesh, NeRF, Gaussian splats
hours: 10
outcomes:
  - Explain meshes, NeRFs, and Gaussian splats - what each stores, how it renders, and what it is good for.
  - Estimate the size of a splat scene from its number of Gaussians.
  - Capture a real place as a Gaussian splat with a phone, and clean it.
  - Render exact camera moves through a splat, and use them to control a video model.
keywords: [mesh, NeRF, Gaussian splatting, photogrammetry]
summary: >
  A mesh is a surface of triangles with textures; it is the standard of games and VFX. A NeRF is a neural network
  that stores how a scene looks from every direction. A Gaussian splat stores a scene as millions of small, colored,
  semi-transparent ellipsoids; it renders in real time and looks photographic. You can capture a real place with a
  phone and get a splat in an hour. In AI-native video, a splat gives the real layout and the exact camera move, and
  the video model adds light, people, and life.
diagram:
  type: layers2d
  title: Three ways to store a 3D scene
  rows: ["Mesh", "NeRF", "Gaussian splat"]
  cols: ["Stores", "Strong at"]
  cells:
    - ["Triangles + textures + materials", "Editing, animation, games, VFX"]
    - ["A network: color + density per point and direction", "View synthesis quality (slow to render)"]
    - ["Millions of 3D Gaussians: position, size, rotation, opacity, view-dependent color", "Photoreal, real time, easy capture"]
watch:
  - title: "3D Gaussian Splatting — project page (INRIA)"
    url: https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/
    note: "Watch the video on the page. Note the real-time rendering and the soft areas."
  - title: "Radiance Fields — news site for splats and NeRFs"
    url: https://radiancefields.com/
    note: "Read 3 recent articles about splats in film and video production."
quiz:
  - q: "Which representation do you choose for a set that a 3D artist must edit and animate (doors that open, a car that drives)?"
    options: ["A NeRF", "A mesh", "A Gaussian splat", "A depth map"]
    answer: 1
    explain: "Meshes are made of editable surfaces with materials, so every engine can animate and light them. Splats and NeRFs are hard to edit."
  - q: "Why does a splat look photographic with no lighting setup?"
    options: ["It uses ray tracing", "The color of each Gaussian comes from the real photos and changes with the view angle, so the captured light is stored in the scene", "It is a video", "It has textures"]
    answer: 1
    explain: "A splat stores the appearance that the camera saw, including light and reflections. That is also why you cannot easily relight it."
  - q: "A splat has 1.8 million Gaussians with full view-dependent color (about 59 numbers each, 32-bit). About how large is the file?"
    options: ["About 4 MB", "About 425 MB", "About 42 GB", "About 1 KB"]
    answer: 1
    explain: "1.8 M × 59 numbers × 4 bytes ≈ 425 MB. Compressed formats make it several times smaller."
  - q: "Your capture has 'floaters' (fog-like blobs) near the windows. What causes them, and what do you do?"
    options: ["Bad GPU", "Reflections and areas seen from few angles give the optimizer wrong evidence; delete them in a splat editor and capture more views next time", "Too many photos", "Wrong file format"]
    answer: 1
    explain: "Glass, mirrors, and thin coverage confuse the reconstruction. Clean the scene, and plan the capture path."
  - q: "What is the most important rule while you film a capture?"
    options: ["Move fast", "Lock exposure and focus, move slowly, and cover the space from many positions and heights; keep people and moving objects out", "Use a zoom lens", "Film at night"]
    answer: 1
    explain: "Reconstruction needs sharp, consistent views of a static scene from many positions."
  - q: "Why render a camera move through a splat and use it in a video model, instead of only describing the move in a prompt?"
    options: ["It is faster to generate", "The render fixes the real layout and the exact camera path; the model only has to add light, people, and detail", "Prompts cannot describe moves", "Splats are required by video models"]
    answer: 1
    explain: "Words are a weak control for space and camera paths (C05·M02). A render is exact."
  - q: "You want a splat of your kitchen for a shot. A NeRF method gives a slightly better still image but renders at 1 frame per second. Which do you use for an interactive camera planning session?"
    options: ["The NeRF", "The splat: it renders in real time, so you can try camera moves interactively", "Neither", "A mesh from photos"]
    answer: 1
    explain: "Interactive planning needs real time. Quality differences are small after the video model pass."
deeper:
  - title: "Kerbl et al. (2023) — 3D Gaussian Splatting for Real-Time Radiance Field Rendering"
    url: https://arxiv.org/abs/2308.04079
  - title: "Mildenhall et al. (2020) — NeRF: Representing Scenes as Neural Radiance Fields"
    url: https://arxiv.org/abs/2003.08934
  - title: "Nerfstudio — open framework (splatfacto)"
    url: https://docs.nerf.studio/
---
## Learn

### Why 3D in an AI-native course
A video model guesses space from 2D training data. It does not know that the window is 1.2 m to the left of the door, or that the camera moved 0.8 m. A 3D representation knows. When you combine them, the 3D scene fixes the layout and the camera path, and the video model adds light, people, and life. This course shows three ways to store a 3D scene, and in M02 and M03 how to make them and use them.

### Mesh
A mesh is a surface made of triangles. Each triangle has texture coordinates (UVs) into images that give color and other material values. Every game engine, 3D application, and VFX tool uses meshes.
- **Strong:** editing, animation, physics, relighting, exact geometry.
- **Weak:** photoreal results need much work: modeling, textures, materials, and lights.

### NeRF
A NeRF (neural radiance field) is a small neural network. You give it a 3D point and a view direction. It returns a color and a density. To render a pixel, you sample many points along the camera ray and combine them. NeRFs gave very good new views of captured scenes.
- **Strong:** view synthesis quality.
- **Weak:** slow rendering (many network calls per pixel), hard editing.
NeRFs were the step before splats. You will see them in papers and some tools.

### Gaussian splat
A Gaussian splat scene is a set of millions of small 3D Gaussians: soft, semi-transparent ellipsoids. Each Gaussian stores:
- a **position** (3 numbers);
- a **size** in three directions (3 numbers) and a **rotation** (4 numbers, a quaternion);
- an **opacity** (1 number);
- a **color that changes with the view angle**, stored as spherical-harmonic coefficients (up to 16 coefficients × 3 colors = 48 numbers).
That is about 59 numbers per Gaussian. To render, the GPU sorts the Gaussians by depth and blends them onto the screen. This runs in real time, even in a web browser.

A capture tool makes the splat by optimization: it starts from points that it found in the photos, then adjusts all Gaussians until renders from the photo positions match the photos. Because the colors come from the photos, a splat looks photographic. It also stores the captured light, so you cannot easily relight it.

**Size estimate:** 1.8 million Gaussians × 59 numbers × 4 bytes ≈ 425 MB as an uncompressed `.ply` file. Compressed formats (for example `.spz` or `.sog`) are several times smaller. Use the estimate to plan storage and web delivery.

### Capture a real place
1. **Choose** a static scene. Avoid moving people, strong reflections, glass, and plain white walls (they have no detail to match).
2. **Lock** exposure, focus, and white balance on the phone. Changing exposure gives inconsistent colors.
3. **Move slowly** around and through the space. Cover it from many positions and at 2–3 heights. Overlap each view with the last one. 60–200 photos, or a 1–2 minute video.
4. **Process** with a capture app or an open tool.
5. **Clean:** delete "floaters" (stray blobs, often near windows and at the edges) and crop the scene.

### Use splats in production
- **Virtual location scout:** walk through the place on a screen before you generate or shoot.
- **Camera planning:** try moves interactively, because the splat renders in real time.
- **Exact plates:** render a camera move along a path, at a real focal length.
- **Video conditioning:** use the render as the first frame (I2V), as the source of V2V, or as a location reference (C05·M01).

The video model hides many splat faults (soft areas, small floaters) when it redraws the frames at medium strength.

## Tool walkthrough

### Capture and edit (as of 2026-10)
- **Phone capture apps** process on the phone or in the cloud and export `.ply` or `.spz`. Check the export format and the license of the output before you choose one.
- **Open pipeline:** Nerfstudio (`splatfacto`) on a rented GPU. Steps: `ns-process-data video --data capture.mp4 --output-dir data/`, then `ns-train splatfacto --data data/`, then export the splat.
- **Editing:** a splat editor in the browser (for example SuperSplat) to delete floaters, crop, and set the orientation.

### Render a camera move
Most splat viewers and editors can record a camera path. For exact moves, set two key positions and a focal length, and render at 24 fps at your working size (for example 1280 × 704). Name the file by shot: `S08_splat_dolly.mp4`.

### Into the video model
- **I2V:** the first frame of the render, plus a prompt for light and people.
- **V2V with control:** depth or edges of the render as the control video (C11 starter workflow `05`), plus a reference image for the look.

## Worked example

**Café capture** (a shape that you can follow):
1. Phone video, 2 minutes, exposure and focus locked, two passes at 1.0 m and 1.6 m height.
2. Processing gives a splat with 1.8 million Gaussians (about 425 MB as `.ply`, about 60 MB compressed).
3. Cleaning: about 30 floaters near the window deleted; the street outside cropped.
4. Camera path: a slow dolly along the counter, 6 s, 35 mm lens look, 1.4 m height.
5. V2V with the render as the source and the prompt "same camera move, morning light, a barista works at the espresso machine".

Result: the counter, the window, and the camera path match the real café exactly. The model added the barista and the morning light. A text-to-video shot with the same description invented a different café with a different layout in each take.

## Lab

**Deliverable:** `C07/M01/` with a splat, 2 rendered moves, a video-model shot, and a comparison.

1. Capture one real space (a room, a corridor, a shop with permission) as a splat. Write your capture settings and path.
2. Count the Gaussians. Estimate the file size with the formula. Compare with the real file size.
3. Clean the splat. Write what you deleted and why.
4. Render 2 camera moves at real focal lengths (one dolly, one pan or crane).
5. Use one render as the first frame (I2V) or as the source (V2V) for a video model.
6. Generate a text-to-video shot from a written description of the same space. Compare layout, camera, and look.

**Result checklist**
- [ ] Splat file and a viewer screenshot.
- [ ] Size estimate versus real size.
- [ ] 2 rendered moves with their lens and speed written down.
- [ ] Video-model result and the T2V comparison.

## Model answer

**Capture notes (shape of a strong answer):** "Kitchen, 3.5 × 4 m. iPhone video, 1 min 40 s, exposure and focus locked. Two loops: one at chest height, one at 1.8 m looking down. Result: 1.2 M Gaussians; formula 1.2 M × 59 × 4 B = 283 MB; real `.ply` 290 MB (header and extra fields). Cleaning: deleted floaters in front of the oven glass and the window; cropped the garden."

**Comparison:**

| | Splat render → I2V | Text-to-video |
|---|---|---|
| Layout | Real kitchen, window left of the fridge | Different kitchen in each take |
| Camera | Exact 0.8 m dolly, 35 mm look | A random slow push-in |
| Look | Real light + the prompted evening light | Generic |
| Faults | Soft area under the table (thin capture) | — |

"The splat fixed what words could not: the layout and the camera move. The soft area under the table disappeared at medium V2V strength. For the next capture, I will add a low pass at 0.5 m."
