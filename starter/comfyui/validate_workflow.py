#!/usr/bin/env python3
"""Check an API-format ComfyUI workflow against the node definitions of a ComfyUI server.

The check finds these problems before you queue a job:
  - a node class that the server does not have (missing custom node, wrong name)
  - a required input that is not set
  - a link to a node ID that does not exist, or to an output slot that does not exist
  - a link whose type does not match the input type (for example IMAGE into LATENT)
  - a combo value (a file name or a sampler name) that is not in the server's list

Usage:
  python validate_workflow.py workflow_api.json                       # ask a running server
  python validate_workflow.py workflow_api.json --server http://host:8188
  python validate_workflow.py workflow_api.json --object-info object_info.json  # offline
  python validate_workflow.py *.json --skip-files                     # ignore model file names

Get an offline snapshot with:  curl http://127.0.0.1:8188/object_info > object_info.json
"""
import argparse
import json
import sys
import urllib.request

FILE_HINTS = (".safetensors", ".ckpt", ".pt", ".pth", ".bin", ".gguf", ".png", ".jpg", ".jpeg", ".webp", ".mp4", ".wav", ".mp3", ".flac")


def load_object_info(args):
    if args.object_info:
        with open(args.object_info) as f:
            return json.load(f)
    with urllib.request.urlopen(args.server.rstrip("/") + "/object_info", timeout=30) as r:
        return json.load(r)


def input_spec(info, name):
    """Return {input_name: (spec, required)} for one node class."""
    spec = {}
    inp = info.get("input", {})
    for group, required in (("required", True), ("optional", False)):
        for k, v in (inp.get(group) or {}).items():
            spec[k] = (v, required)
    return spec


def combo_values(spec):
    """Return the allowed values of a combo input, or None if it is not a combo.

    spec is the object_info list for one input, for example [["euler", "dpmpp_2m"], {...}].
    """
    t = spec[0]
    opts = spec[1] if len(spec) > 1 and isinstance(spec[1], dict) else {}
    if isinstance(t, list):
        return t
    if t == "COMBO":
        return opts.get("options")
    if t == "COMFY_DYNAMICCOMBO_V3":
        return [o["key"] for o in opts.get("options", [])]
    return None


def is_link(v):
    return isinstance(v, list) and len(v) == 2 and isinstance(v[0], str) and isinstance(v[1], int)


# Types that accept or give any type. The server checks them when it runs the node.
WILDCARD_TYPES = {"*", "COMFY_MATCHTYPE_V3", "COMFY_ANYTYPE_V3"}
# Inputs that grow (values.a, values.b ...) or change with a combo (format.codec).
GROUP_TYPES = {"COMFY_AUTOGROW_V3", "COMFY_DYNAMICCOMBO_V3", "COMFY_DYNAMICSLOT_V3"}


def types_match(out_type, in_type):
    if out_type in WILDCARD_TYPES or in_type in WILDCARD_TYPES:
        return True
    outs = set(str(out_type).split(","))
    ins = set(str(in_type).split(","))
    return bool(outs & ins)


def validate(wf, oi, skip_files=False):
    problems = []
    if not isinstance(wf, dict) or "nodes" in wf:
        return ["This is a UI-format workflow. Export it with 'Export (API)' and check that file."]
    if not all(isinstance(n, dict) and "class_type" in n for k, n in wf.items() if not k.startswith("_")):
        return ["This is not an API-format workflow (for example a .map.json file)."]
    for nid, node in wf.items():
        if nid.startswith("_"):
            continue  # comment keys such as "_meta_workflow"
        cls = node.get("class_type")
        title = node.get("_meta", {}).get("title", cls)
        where = f"node {nid} ({title})"
        if cls not in oi:
            problems.append(f"{where}: class '{cls}' is not on the server (install the custom node or fix the name)")
            continue
        spec = input_spec(oi[cls], cls)
        inputs = node.get("inputs", {})
        for k, (s, required) in spec.items():
            if isinstance(s[0], str) and s[0] in GROUP_TYPES and any(i == k or i.startswith(k + ".") for i in inputs):
                continue
            if required and k not in inputs:
                problems.append(f"{where}: required input '{k}' is not set")
        for k, v in inputs.items():
            if k not in spec:
                # Dynamic inputs (for example image_1, image_2 ...) are allowed on some nodes.
                continue
            in_type = spec[k][0][0]
            if is_link(v):
                src_id, slot = v
                if src_id not in wf:
                    problems.append(f"{where}: input '{k}' links to node {src_id}, which does not exist")
                    continue
                src_cls = wf[src_id].get("class_type")
                if src_cls not in oi:
                    continue
                outs = oi[src_cls].get("output", [])
                if slot >= len(outs):
                    problems.append(f"{where}: input '{k}' uses output {slot} of node {src_id}, which has {len(outs)} outputs")
                    continue
                out_type = outs[slot]
                want = "COMBO" if isinstance(in_type, list) else in_type
                if not isinstance(in_type, list) and not types_match(out_type, want):
                    problems.append(f"{where}: input '{k}' expects {want}, but node {src_id} output {slot} is {out_type}")
            else:
                allowed = combo_values(spec[k][0])
                if allowed is not None and v not in allowed:
                    if skip_files and isinstance(v, str) and v.lower().endswith(FILE_HINTS):
                        continue
                    sample = ", ".join(map(str, allowed[:6])) + (" ..." if len(allowed) > 6 else "")
                    problems.append(f"{where}: input '{k}' = {v!r} is not in the server list [{sample}]")
    return problems


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("workflows", nargs="+")
    ap.add_argument("--server", default="http://127.0.0.1:8188")
    ap.add_argument("--object-info", help="offline object_info.json snapshot")
    ap.add_argument("--skip-files", action="store_true", help="do not check model, image, and audio file names")
    args = ap.parse_args()
    oi = load_object_info(args)
    failed = 0
    for path in args.workflows:
        with open(path) as f:
            wf = json.load(f)
        problems = validate(wf, oi, args.skip_files)
        if problems:
            failed += 1
            print(f"FAIL {path}")
            for p in problems:
                print(f"  - {p}")
        else:
            print(f"OK   {path}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
