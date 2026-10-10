#!/usr/bin/env python3
"""Make the starter ComfyUI workflows in starter/comfyui/workflows/ from the official templates.

Steps:
  1. Download the official templates (UI format) from github.com/Comfy-Org/workflow_templates.
  2. Convert each one to API format with tools/comfy_ui_to_api.py.
  3. Apply small, documented edits (remove a second branch, connect the start image, fix inputs).
  4. Write <name>.json (API format), <name>.map.json (named inputs), and models.lock.json.

Usage:
  .venv/bin/python tools/make_starter_workflows.py --object-info object_info.json --models models.json

object_info.json comes from a running ComfyUI server (GET /object_info).
models.json lists name -> {directory, url, bytes, sha256, license}; tools/make_starter_workflows.py --help.
"""
import argparse
import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from comfy_ui_to_api import Converter  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "starter" / "comfyui" / "workflows"
TEMPLATES = "https://raw.githubusercontent.com/Comfy-Org/workflow_templates/main/templates/{}.json"


def drop_prefix(wf, prefix):
    return {k: v for k, v in wf.items() if not k.startswith(prefix)}


def edit_t2i(wf):
    # The template has two branches: base model (50 steps) and distilled model (4 steps).
    # Keep the distilled branch: it is fast and needs less VRAM.
    wf = drop_prefix(wf, "75:")
    wf["9"]["inputs"]["images"] = ["77:65", 0]
    wf["9"]["inputs"]["filename_prefix"] = "C11/t2i_klein"
    return wf


def edit_ref(wf):
    # Keep the two-reference branch (92:*): image 1 = character, image 2 = place or style.
    wf = drop_prefix(wf, "75:")
    wf["9"]["inputs"]["images"] = ["92:105", 0]
    wf["9"]["inputs"]["filename_prefix"] = "C11/ref_klein"
    wf["76"]["inputs"]["image"] = "ref_character.png"
    wf["81"]["inputs"]["image"] = "ref_place.png"
    wf["92:109"]["inputs"]["text"] = (
        "Medium close-up of the woman from image 1 standing in the place from image 2. "
        "Night, cool fluorescent light from above, shallow depth of field, 85 mm lens look. "
        "Keep her face, hair, and raincoat exactly as in image 1.")
    return wf


def edit_wan_i2v(wf):
    # The template ships as text-to-video (the image loader is bypassed). Connect the start image.
    wf["56"] = {"inputs": {"image": "start_frame.png"}, "class_type": "LoadImage", "_meta": {"title": "Start frame"}}
    wf["55"]["inputs"]["start_image"] = ["56", 0]
    wf["58"]["inputs"]["filename_prefix"] = "C11/i2v_wan5b"
    return wf


def edit_prefix(prefix):
    def f(wf):
        for n in wf.values():
            if n["class_type"] in ("SaveVideo", "SaveImage"):
                n["inputs"]["filename_prefix"] = prefix
        return wf
    return f


def edit_ltx25_i2v(wf):
    wf["395"]["inputs"]["image"] = "start_frame.png"
    wf["75"]["inputs"]["filename_prefix"] = "C11/i2v_ltx25"
    return wf


def edit_ia2v(wf):
    # No LTX-2.5 image+audio template exists yet (2026-10-04), so lip sync uses LTX-2.3.
    # Turn off the LLM prompt rewrite so that the same inputs give the same output.
    wf["340:349"]["inputs"]["value"] = False
    wf["269"]["inputs"]["image"] = "start_frame.png"
    wf["276"]["inputs"]["audio"] = "line.wav"
    wf["341"]["inputs"]["filename_prefix"] = "C11/lipsync_ltx23"
    return wf


# name, template, edit, map {friendly name: "node.input"}, notes
SPECS = [
    ("01_t2i_flux2_klein_4b", "image_flux2_klein_text_to_image", edit_t2i,
     {"prompt": "76.value", "seed": "77:73.noise_seed", "width": "77:68.value", "height": "77:69.value",
      "steps": "77:62.steps", "filename_prefix": "9.filename_prefix"},
     "Text to image, distilled 4-step model. First graph in C11·M01."),
    ("02_ref_edit_flux2_klein_4b", "image_flux2_klein_image_edit_4b_distilled", edit_ref,
     {"prompt": "92:109.text", "ref_image_1": "76.image", "ref_image_2": "81.image", "seed": "92:106.noise_seed",
      "steps": "92:102.steps", "filename_prefix": "9.filename_prefix"},
     "Start frame from two reference images (character + place). Used in C11·M02 and M03."),
    ("03_i2v_wan22_5b", "video_wan2_2_5B_ti2v", edit_wan_i2v,
     {"prompt": "6.text", "negative": "7.text", "start_image": "56.image", "seed": "3.seed", "steps": "3.steps",
      "cfg": "3.cfg", "width": "55.width", "height": "55.height", "frames": "55.length", "fps": "57.fps",
      "shift": "48.shift", "filename_prefix": "58.filename_prefix"},
     "Image to video, 5B model, 1280x704, 121 frames at 24 fps (5 s). Fits a 24 GB GPU."),
    ("04_flf2v_wan22_14b", "video_wan2_2_14B_flf2v", edit_prefix("C11/flf2v_wan14b"),
     {"prompt": "90.text", "negative": "78.text", "first_frame": "80.image", "last_frame": "89.image",
      "seed": "84.noise_seed", "width": "81.width", "height": "81.height", "frames": "81.length", "fps": "86.fps",
      "filename_prefix": "83.filename_prefix"},
     "First and last frame to video, 14B MoE (high-noise + low-noise experts), 20 steps split 10/10."),
    ("05_v2v_control_wan22_5b", "video_wan2_2_5B_fun_control", edit_prefix("C11/v2v_control_wan5b"),
     {"prompt": "6.text", "negative": "7.text", "ref_image": "70.image", "control_video": "66.file",
      "seed": "3.seed", "steps": "3.steps", "width": "60.width", "height": "60.height", "frames": "60.length",
      "filename_prefix": "58.filename_prefix"},
     "Video to video with a control video (depth, pose, or edges) and a reference image."),
    ("06_i2v_ltx25", "video_ltx2_5_i2v", edit_ltx25_i2v,
     {"prompt": "398:376.value", "start_image": "395.image", "seed": "398:339.noise_seed",
      "megapixels": "403.megapixels", "aspect_ratio": "403.aspect_ratio", "duration_s": "398:362.value",
      "fps": "398:361.value", "prompt_enhance": "398:383.value", "filename_prefix": "75.filename_prefix"},
     "Image to video with native audio (LTX-2.5, distilled, INT8). Two stages: half size, then 2x latent upscale."),
    ("07_lipsync_ia2v_ltx23", "video_ltx2_3_ia2v", edit_ia2v,
     {"prompt": "340:319.value", "start_image": "269.image", "line_audio": "276.audio", "seed": "340:286.noise_seed",
      "width": "340:330.value", "height": "340:324.value", "duration_s": "340:331.value", "fps": "340:323.value",
      "prompt_enhance": "340:349.value", "filename_prefix": "341.filename_prefix"},
     "Image + audio line to video: the face speaks the line (lip sync). Stage 6 of the C11·M03 pipeline."),
    ("08_flf2v_ltx25", "video_ltx2_5_flf2v", edit_prefix("C11/flf2v_ltx25"),
     {"prompt": "251:252.value", "first_frame": "31.image", "last_frame": "39.image", "seed": "251:196.noise_seed",
      "width": "251:215.value", "height": "251:216.value", "duration_s": "251:198.value", "fps": "251:205.value",
      "filename_prefix": "68.filename_prefix"},
     "First and last frame to video with LTX-2.5 (alternative to 04)."),
]


def models_used(wf, catalog):
    names = set()
    for n in wf.values():
        for v in n["inputs"].values():
            if isinstance(v, str) and v in catalog:
                names.add(v)
    return sorted(names)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--object-info", required=True)
    ap.add_argument("--models", required=True)
    ap.add_argument("--templates", help="local folder with template JSON files (else download)")
    a = ap.parse_args()
    oi = json.load(open(a.object_info))
    catalog = json.load(open(a.models))
    OUT.mkdir(parents=True, exist_ok=True)
    index = []
    for name, tpl, edit, mp, note in SPECS:
        if a.templates:
            ui = json.load(open(Path(a.templates) / f"{tpl}.json"))
        else:
            ui = json.load(urllib.request.urlopen(TEMPLATES.format(tpl)))
        c = Converter(ui, oi)
        wf = edit(c.run())
        for k, path in mp.items():
            nid, key = path.split(".", 1)
            if nid not in wf or key not in wf[nid]["inputs"]:
                sys.exit(f"{name}: map entry {k} -> {path} does not exist")
        (OUT / f"{name}.json").write_text(json.dumps(wf, indent=2, ensure_ascii=False) + "\n")
        (OUT / f"{name}.map.json").write_text(json.dumps(mp, indent=2) + "\n")
        used = models_used(wf, catalog)
        index.append({"workflow": name, "template": tpl, "note": note, "models": used,
                      "download_gb": round(sum(catalog[m]["bytes"] for m in used) / 1e9, 1)})
        print(f"{name}: {len(wf)} nodes, {len(used)} model files")
    lock = {m: catalog[m] for m in sorted({m for i in index for m in i["models"]} |
                                          {k for k in catalog if "lightx2v" in k})}
    (OUT.parent / "models.lock.json").write_text(json.dumps(lock, indent=2) + "\n")
    (OUT / "index.json").write_text(json.dumps(index, indent=2) + "\n")


if __name__ == "__main__":
    main()
