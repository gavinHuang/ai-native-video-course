---
code: C07
title: World Models, 3D, and Virtual Production
level: 2
hours: 40
prereq: C01, C05
outcomes:
  - Explain meshes, NeRFs, and Gaussian splats, and when each is useful.
  - Generate explorable 3D worlds and use them as sets and previs.
  - Use 3D layout to control camera paths for video models exactly.
  - Use a real-time engine for previs and virtual production.
---
## About this course

Video models guess space. 3D tools know space. When you combine them, you get exact camera control and stable locations. World models such as Genie 3 and Marble now generate whole 3D or interactive worlds. This course shows how to use them in production today.

**Starter tool:** `tools/whitebox.py` in the [starter kit](starter.zip) builds a white box from a JSON layout and renders depth, edge, and clay videos with a real lens (M03). It runs with Blender's Python module (`pip install bpy`, Python 3.11) without opening Blender. On 2026-10-04 it rendered 48 frames of all three passes at 640 × 352 in 25 s on a laptop CPU.
