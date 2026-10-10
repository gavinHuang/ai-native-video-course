#!/usr/bin/env python3
"""Build a white-box scene from a JSON layout and render control videos (C07·M03). Needs Blender's Python module.

  pip install bpy            # Blender as a Python module (Python 3.11); or run inside Blender:
                             # blender -b --python whitebox.py -- layout.json --out wb/
  python whitebox.py layout.json --out wb/ [--res 640x352] [--passes depth,edges,clay]

Output: wb/depth.mp4 (near = white), wb/edges.mp4 (white lines on black), wb/clay.mp4 (grey shading),
and wb/first_frame_clay.png. Use depth or edges as the control video of starter workflow 05, and the clay
render as a V2V source or a layout reference.

layout.json (meters, degrees; z is up; the floor is z = 0):
{
  "fps": 24, "seconds": 5,
  "room":  {"w": 6, "d": 4, "h": 2.7, "door": {"wall": "back", "x": 1.0, "w": 0.9, "h": 2.0},
            "window": {"wall": "left", "y": 0.5, "w": 1.2, "h": 1.0, "sill": 0.9}},
  "boxes": [{"name": "lockers", "pos": [-1.5, 1.7, 0], "size": [2.4, 0.5, 1.9]},
            {"name": "bench", "pos": [0, 0.4, 0], "size": [1.8, 0.4, 0.45]}],
  "people": [{"name": "MARA", "pos": [0.3, 0.9, 0], "height": 1.68, "facing": 200}],
  "camera": {"lens_mm": 35, "sensor_mm": 36,
             "from": {"pos": [0.2, -1.6, 1.5], "look": [0.3, 0.9, 1.45]},
             "to":   {"pos": [0.25, -0.6, 1.5], "look": [0.3, 0.9, 1.5]}}
}
The camera moves in a straight line from "from" to "to" with ease in and out. Real lens values matter:
a 35 mm lens on a 36 mm sensor is a normal wide; 85 mm is a close-up lens (C02·M02).
"""
import argparse
import json
import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def args_after_dashdash():
    return sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]


def build(L):
    import bpy
    from mathutils import Vector

    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.fps = L.get("fps", 24)
    sc.frame_start, sc.frame_end = 1, int(round(L.get("fps", 24) * L.get("seconds", 5)))

    def box(name, center, size):
        bpy.ops.mesh.primitive_cube_add(size=1, location=center)
        o = bpy.context.active_object
        o.name = name
        o.scale = size
        bpy.ops.object.transform_apply(scale=True)
        return o

    r = L["room"]
    w, d, h, t = r["w"], r["d"], r["h"], 0.1
    box("floor", (0, d / 2, -t / 2), (w, d, t))
    box("ceiling", (0, d / 2, h + t / 2), (w, d, t))
    walls = {"back": ((0, d + t / 2, h / 2), (w, t, h)), "left": ((-w / 2 - t / 2, d / 2, h / 2), (t, d, h)),
             "right": ((w / 2 + t / 2, d / 2, h / 2), (t, d, h))}
    for name, (c, s) in walls.items():
        box(f"wall_{name}", c, s)
    # Openings: a dark recessed box shows a door or a window as a depth step (enough for layout control).
    for key in ("door", "window"):
        op = r.get(key)
        if not op:
            continue
        sill = op.get("sill", 0.0)
        if op["wall"] == "back":
            c = (op.get("x", 0), d + 0.05, sill + op["h"] / 2)
            s = (op["w"], 0.3, op["h"])
        else:
            sign = -1 if op["wall"] == "left" else 1
            c = (sign * (w / 2 + 0.05), op.get("y", d / 2), sill + op["h"] / 2)
            s = (0.3, op["w"], op["h"])
        hole = box(f"{key}_cut", c, s)
        wall = bpy.data.objects[f"wall_{op['wall']}"]
        mod = wall.modifiers.new("cut", "BOOLEAN")
        mod.object, mod.operation = hole, "DIFFERENCE"
        bpy.context.view_layer.objects.active = wall
        bpy.ops.object.modifier_apply(modifier="cut")
        bpy.data.objects.remove(hole)
        box(f"{key}_recess", (c[0] + (0 if op["wall"] == "back" else (-0.35 if op["wall"] == "left" else 0.35)),
                              c[1] + (0.35 if op["wall"] == "back" else 0), c[2]), s)
    for b in L.get("boxes", []):
        x, y, z = b["pos"]
        sx, sy, sz = b["size"]
        box(b["name"], (x, y, z + sz / 2), (sx, sy, sz))
    for p in L.get("people", []):
        # A simple mannequin: body capsule + head sphere, at real height.
        x, y, z = p["pos"]
        H = p.get("height", 1.7)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=H * 0.82, location=(x, y, z + H * 0.41))
        bpy.context.active_object.name = f"{p['name']}_body"
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.11, location=(x, y, z + H - 0.11))
        bpy.context.active_object.name = f"{p['name']}_head"
        f = math.radians(p.get("facing", 0))
        bpy.ops.mesh.primitive_cube_add(size=0.08, location=(x + 0.12 * math.sin(f), y + 0.12 * math.cos(f), z + H - 0.11))
        bpy.context.active_object.name = f"{p['name']}_nose"  # shows which way the person faces

    # A soft ceiling light for the clay pass (the depth pass uses emission and ignores lights).
    light = bpy.data.lights.new("ceiling_light", "AREA")
    light.energy = 6 * w * d  # watts; about 140 W for a 6 x 4 m room
    light.size = min(w, d) * 0.6
    lo = bpy.data.objects.new("ceiling_light", light)
    lo.location = (0, d / 2, h - 0.05)
    sc.collection.objects.link(lo)

    cam_d = bpy.data.cameras.new("cam")
    cam_d.lens = L["camera"].get("lens_mm", 35)
    cam_d.sensor_width = L["camera"].get("sensor_mm", 36)
    cam = bpy.data.objects.new("cam", cam_d)
    sc.collection.objects.link(cam)
    sc.camera = cam
    target = bpy.data.objects.new("look", None)
    sc.collection.objects.link(target)
    con = cam.constraints.new("TRACK_TO")
    con.target, con.track_axis, con.up_axis = target, "TRACK_NEGATIVE_Z", "UP_Y"
    for frame, key in ((sc.frame_start, "from"), (sc.frame_end, "to")):
        k = L["camera"][key]
        cam.location = Vector(k["pos"])
        target.location = Vector(k["look"])
        cam.keyframe_insert("location", frame=frame)
        target.keyframe_insert("location", frame=frame)
    return sc


def depth_material(near, far):
    import bpy
    m = bpy.data.materials.new("depth")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    cam = nt.nodes.new("ShaderNodeCameraData")
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = near, far
    mr.inputs["To Min"].default_value, mr.inputs["To Max"].default_value = 1.0, 0.0  # near = white
    em = nt.nodes.new("ShaderNodeEmission")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(cam.outputs["View Z Depth"], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], em.inputs["Color"])
    nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    return m


def clay_material():
    import bpy
    m = bpy.data.materials.new("clay")
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.6, 0.6, 0.6, 1)
    bsdf.inputs["Roughness"].default_value = 0.8
    return m


def render(sc, mat, folder, samples, res, world_strength, view="Standard"):
    import bpy
    for o in sc.objects:
        if o.type == "MESH":
            o.data.materials.clear()
            o.data.materials.append(mat)
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = False
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "PNG"
    sc.view_settings.view_transform = view  # "Standard" keeps depth values linear; "AgX" tone-maps the clay pass
    world = bpy.data.worlds.new("w")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = world_strength
    sc.world = world
    sc.render.filepath = str(folder / "f_")
    bpy.ops.render.render(animation=True)


def to_mp4(folder, out, fps):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(fps), "-start_number", "1", "-i", str(folder / "f_%04d.png"),
                    "-pix_fmt", "yuv420p", "-c:v", "libx264", "-crf", "16", str(out)], check=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("layout")
    ap.add_argument("--out", default="wb")
    ap.add_argument("--res", default="640x352")
    ap.add_argument("--passes", default="depth,edges,clay")
    a = ap.parse_args(args_after_dashdash())
    L = json.loads(Path(a.layout).read_text())
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    res = tuple(map(int, a.res.split("x")))
    passes = a.passes.split(",")
    tmp = Path(tempfile.mkdtemp(prefix="wb_"))
    sc = build(L)
    fps = sc.render.fps
    # Depth range from the room size: from 0.3 m to the far corner.
    r = L["room"]
    far = math.dist(L["camera"]["from"]["pos"], (r["w"] / 2, r["d"], 0)) + 0.5
    if "depth" in passes or "edges" in passes:
        (tmp / "depth").mkdir()
        render(sc, depth_material(0.3, far), tmp / "depth", 1, res, 0.0)
        to_mp4(tmp / "depth", out / "depth.mp4", fps)
    if "edges" in passes:
        try:
            import cv2
            import numpy as np
        except ImportError:
            sys.exit("the edges pass needs opencv-python and numpy")
        (tmp / "edges").mkdir()
        for f in sorted((tmp / "depth").glob("f_*.png")):
            dimg = cv2.imread(str(f), cv2.IMREAD_GRAYSCALE)
            e = cv2.Canny(cv2.GaussianBlur(dimg, (3, 3), 0), 4, 12)  # depth steps = object outlines
            cv2.imwrite(str(tmp / "edges" / f.name), cv2.dilate(e, np.ones((2, 2), np.uint8)))
        to_mp4(tmp / "edges", out / "edges.mp4", fps)
    if "clay" in passes:
        (tmp / "clay").mkdir()
        render(sc, clay_material(), tmp / "clay", 16, res, 0.3, view="AgX")
        to_mp4(tmp / "clay", out / "clay.mp4", fps)
        shutil.copy(tmp / "clay" / "f_0001.png", out / "first_frame_clay.png")
    shutil.rmtree(tmp)
    print(json.dumps({"out": str(out), "frames": sc.frame_end, "fps": fps, "lens_mm": L["camera"].get("lens_mm"),
                      "passes": passes, "depth_far_m": round(far, 2)}))


if __name__ == "__main__":
    main()
