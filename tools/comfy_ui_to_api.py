#!/usr/bin/env python3
"""Convert a ComfyUI UI-format workflow (with subgraphs) to API format.

Course tooling: we use it to make the starter workflows in starter/comfyui/workflows/
from the official templates (github.com/Comfy-Org/workflow_templates). Students normally use
"Export (API)" in the ComfyUI menu instead.

Usage:
  python tools/comfy_ui_to_api.py template.json out_api.json --object-info object_info.json

Rules that the converter follows (the same rules as the ComfyUI frontend):
  - Widget values map to the node's widget inputs in object_info order (required, then optional).
    A seed widget with control_after_generate and an upload widget each add one extra value.
  - Dynamic combos (COMFY_DYNAMICCOMBO_V3) use dotted keys: "format", "format.codec".
  - Subgraph nodes are expanded. Inner node IDs become "<outer id>:<inner id>".
  - Notes are removed. Muted nodes (mode 2) are removed. Bypassed nodes (mode 4) pass their inputs through.
  - Reroute and frontend PrimitiveNode nodes are resolved to their source.
"""
import argparse
import json
import sys

WIDGET_TYPES = {"INT", "FLOAT", "STRING", "BOOLEAN", "COMBO"}
DROP_TYPES = {"Note", "MarkdownNote", "PrimitiveNode", "Reroute"}
UPLOAD_KEYS = ("image_upload", "video_upload", "audio_upload", "animated_image_upload")


def norm_links(links):
    out = {}
    for l in links or []:
        if isinstance(l, dict):
            out[l["id"]] = (l["origin_id"], l["origin_slot"], l["target_id"], l["target_slot"], l.get("type"))
        else:
            out[l[0]] = (l[1], l[2], l[3], l[4], l[5] if len(l) > 5 else None)
    return out


def is_widget(spec):
    t = spec[0]
    opts = spec[1] if len(spec) > 1 and isinstance(spec[1], dict) else {}
    if opts.get("forceInput"):
        return False
    if isinstance(t, list) or t == "COMFY_DYNAMICCOMBO_V3" or opts.get("widgetType"):
        return True
    return any(part in WIDGET_TYPES for part in str(t).split(","))


class Converter:
    def __init__(self, ui, oi):
        self.ui = ui
        self.oi = oi
        self.subgraphs = {s["id"]: s for s in ui.get("definitions", {}).get("subgraphs", [])}
        self.api = {}
        self.warnings = []
        self.overrides = {}  # subgraph prefix -> {(inner node id, widget name): value} from proxyWidgets

    # ---------------------------------------------------------------- widgets
    def map_widgets(self, cls, values, where):
        """Return {input_name: value} for a backend node from its widgets_values list."""
        if isinstance(values, dict):
            return dict(values)
        values = list(values or [])
        out = {}
        info = self.oi.get(cls)
        if info is None:
            self.warnings.append(f"{where}: unknown class {cls}")
            return out
        pos = [0]

        def take():
            if pos[0] < len(values):
                v = values[pos[0]]
                pos[0] += 1
                return v, True
            return None, False

        def walk(inputs, prefix):
            for group in ("required", "optional"):
                for name, spec in (inputs.get(group) or {}).items():
                    if not is_widget(spec):
                        continue
                    key = f"{prefix}{name}"
                    v, ok = take()
                    if not ok:
                        if values:
                            self.warnings.append(f"{where} ({cls}): no widget value for '{key}'; the server default applies")
                        return
                    out[key] = v
                    opts = spec[1] if len(spec) > 1 and isinstance(spec[1], dict) else {}
                    if opts.get("control_after_generate"):
                        take()
                    if any(opts.get(k) for k in UPLOAD_KEYS):
                        take()
                    if spec[0] == "COMFY_DYNAMICCOMBO_V3":
                        for o in opts.get("options", []):
                            if o["key"] == v:
                                walk(o.get("inputs", {}), f"{key}.")

        walk(info.get("input", {}), "")
        if pos[0] < len(values):
            extra = values[pos[0]:]
            if any(x not in (None, "", "auto", "fixed", "randomize", "increment", "decrement") for x in extra):
                self.warnings.append(f"{where} ({cls}): {len(extra)} widget values not mapped: {extra!r:.120}")
        return out

    # ---------------------------------------------------------------- graph expansion
    def expand(self, nodes, links, prefix, bindings, path=""):
        """Add the nodes of one graph level to self.api.

        bindings: subgraph input slot -> ("link", (api_id, slot)) or ("value", v)
        returns: function out_ref(local_id, slot) -> ("link", (api_id, slot)) or ("value", v)
        """
        L = norm_links(links)
        by_id = {n["id"]: n for n in nodes}
        sub_outputs = {}  # instance id -> function(slot) -> ref

        def link_source(link_id):
            if link_id is None or link_id not in L:
                return None
            oid, oslot, *_ = L[link_id]
            return resolve(oid, oslot)

        def resolve(oid, oslot):
            if oid == -10:
                return bindings.get(oslot)
            n = by_id.get(oid)
            if n is None:
                return None
            t = n["type"]
            if t == "Reroute":
                return link_source(n["inputs"][0].get("link")) if n.get("inputs") else None
            if t == "PrimitiveNode":
                wv = n.get("widgets_values") or [None]
                return ("value", wv[0])
            if n.get("mode") == 4:  # bypass: pass through the first input of the same type
                out_type = n["outputs"][oslot]["type"]
                for i in n.get("inputs", []):
                    if i.get("type") == out_type and i.get("link") is not None:
                        return link_source(i["link"])
                return None
            if n.get("mode") == 2:
                return None
            if t in self.subgraphs:
                return sub_outputs[oid](oslot)
            return ("link", [f"{prefix}{oid}", oslot])

        # Expand subgraph instances first so their outputs can be resolved lazily.
        for n in nodes:
            if n["type"] in self.subgraphs and n.get("mode", 0) not in (2,):
                sub_outputs[n["id"]] = self.make_subgraph(n, prefix, link_source)

        for n in nodes:
            t = n["type"]
            if t in DROP_TYPES or t in self.subgraphs or n.get("mode", 0) in (2, 4):
                continue
            nid = f"{prefix}{n['id']}"
            where = f"{path}node {n['id']}"
            inputs = self.map_widgets(t, n.get("widgets_values"), where)
            for (wnode, wname), val in self.overrides.get(prefix, {}).items():
                if wnode == str(n["id"]):
                    inputs[wname] = val
            for i in n.get("inputs", []):
                src = link_source(i.get("link"))
                if src is None:
                    continue
                kind, v = src
                inputs[i["name"]] = v
            title = n.get("title") or t
            self.api[nid] = {"inputs": inputs, "class_type": t, "_meta": {"title": title}}
        return resolve

    def make_subgraph(self, inst, prefix, outer_link_source):
        sg = self.subgraphs[inst["type"]]
        inner_prefix = f"{prefix}{inst['id']}:"
        bindings = {}
        sg_inputs = sg.get("inputs", [])
        # Links into the instance, by input name.
        linked = {}
        for i in inst.get("inputs", []):
            src = outer_link_source(i.get("link"))
            if src is not None:
                linked[i["name"]] = src
        # Widget values on the instance map to the widget-type subgraph inputs, in order.
        wv = inst.get("widgets_values") or []
        proxy = (inst.get("properties") or {}).get("proxyWidgets")
        widget_inputs = [k for k, s in enumerate(sg_inputs) if str(s.get("type")) in WIDGET_TYPES]
        if proxy:
            ov = self.overrides.setdefault(inner_prefix, {})
            for (pnode, pname), val in zip(proxy, wv):
                if str(pnode) != "-1":
                    ov[(str(pnode), pname)] = val
            wv_for_inputs = []
        else:
            wv_for_inputs = wv
        if wv_for_inputs and len(wv_for_inputs) != len(widget_inputs):
            self.warnings.append(f"subgraph {sg.get('name')}: {len(wv_for_inputs)} values for {len(widget_inputs)} widget inputs")
        for k, v in zip(widget_inputs, wv_for_inputs):
            bindings[k] = ("value", v)
        for k, s in enumerate(sg_inputs):
            if s["name"] in linked:
                bindings[k] = linked[s["name"]]
        resolve = self.expand(sg["nodes"], sg.get("links"), inner_prefix, bindings, path=f"{sg.get('name')}/")
        L = norm_links(sg.get("links"))
        out_src = {}
        for lid, (oid, oslot, tid, tslot, _t) in L.items():
            if tid == -20:
                out_src[tslot] = (oid, oslot)

        def out_ref(slot):
            if slot not in out_src:
                return None
            return resolve(*out_src[slot])
        return out_ref

    def run(self):
        self.expand(self.ui["nodes"], self.ui.get("links"), "", {})
        return self.api


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ui")
    ap.add_argument("out")
    ap.add_argument("--object-info", required=True)
    a = ap.parse_args()
    ui = json.load(open(a.ui))
    oi = json.load(open(a.object_info))
    c = Converter(ui, oi)
    api = c.run()
    json.dump(api, open(a.out, "w"), indent=2)
    for w in c.warnings:
        print("WARN", w, file=sys.stderr)
    print(f"{a.out}: {len(api)} nodes", file=sys.stderr)


if __name__ == "__main__":
    main()
