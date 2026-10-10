#!/usr/bin/env python3
"""Show what changed between two versions of a timeline (C08·M01 round trips, C08·M03 agent review).

  python otio_diff.py before.otio after.otio            # also reads .edl, .fcpxml (with the OTIO adapters)
  python otio_diff.py before.otio after.otio --json report.json

It compares the clips of each track in order and reports: added and removed clips, moved clips, changed
source ranges (trims), changed durations, renamed clips, changed media, and marker changes. Use it after
every agent session: the report must match the agent's own log, and nothing else may have changed.
"""
import argparse
import json
import sys


def clips(tl):
    import opentimelineio as otio
    out = {}
    count = {}
    for ti, tr in enumerate(tl.tracks):
        count[tr.kind] = count.get(tr.kind, 0) + 1
        pos = 0.0
        rows = []
        for it in tr:
            dur = it.duration().to_seconds()
            if isinstance(it, otio.schema.Clip):
                sr = it.source_range
                url = getattr(it.media_reference, "target_url", "")
                rows.append({"name": it.name, "start": round(pos, 3), "dur": round(dur, 3),
                             "src_in": round(sr.start_time.to_seconds(), 3) if sr else None,
                             "media": url, "markers": sorted(m.name for m in it.markers),
                             # the same clip across formats: take ID, else the media file name, else the clip name
                             "key": (it.metadata.get("course", {}) or {}).get("take")
                             or (url.rsplit("/", 1)[-1].rsplit(".", 1)[0] if url else it.name)})
            pos += dur
        out[f"{tr.kind} {count[tr.kind]}"] = rows  # match tracks by kind and number; names differ between formats
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("before")
    ap.add_argument("after")
    ap.add_argument("--json")
    a = ap.parse_args()
    try:
        import opentimelineio as otio
    except ImportError:
        sys.exit("pip install opentimelineio")
    A, B = clips(otio.adapters.read_from_file(a.before)), clips(otio.adapters.read_from_file(a.after))
    changes = []
    for t in sorted(set(A) - set(B)):
        print(f"note: track {t} is not in the second file (an EDL has one video track only)")
    for track in sorted(set(A) & set(B)):
        ca, cb = A.get(track, []), B.get(track, [])
        ka = {c["key"]: c for c in ca}
        kb = {c["key"]: c for c in cb}
        for k in ka.keys() - kb.keys():
            changes.append({"track": track, "type": "removed", "clip": ka[k]["name"], "at": ka[k]["start"]})
        for k in kb.keys() - ka.keys():
            changes.append({"track": track, "type": "added", "clip": kb[k]["name"], "at": kb[k]["start"]})
        order_a = [c["key"] for c in ca if c["key"] in kb]
        order_b = [c["key"] for c in cb if c["key"] in ka]
        if order_a != order_b:
            changes.append({"track": track, "type": "reordered", "before": [ka[k]["name"] for k in order_a],
                            "after": [kb[k]["name"] for k in order_b]})
        for k in ka.keys() & kb.keys():
            x, y = ka[k], kb[k]
            if x["name"] != y["name"]:
                changes.append({"track": track, "type": "renamed", "clip": x["name"], "to": y["name"]})
            if x["src_in"] != y["src_in"] or x["dur"] != y["dur"]:
                changes.append({"track": track, "type": "trimmed", "clip": y["name"],
                                "src_in": [x["src_in"], y["src_in"]], "dur": [x["dur"], y["dur"]]})
            if x["media"] != y["media"]:
                changes.append({"track": track, "type": "relinked", "clip": y["name"], "media": [x["media"], y["media"]]})
            if x["markers"] != y["markers"]:
                changes.append({"track": track, "type": "markers", "clip": y["name"],
                                "added": sorted(set(y["markers"]) - set(x["markers"])),
                                "removed": sorted(set(x["markers"]) - set(y["markers"]))})
    for c in changes:
        print(json.dumps(c))
    print(f"{len(changes)} change(s)")
    if a.json:
        open(a.json, "w").write(json.dumps(changes, indent=2))


if __name__ == "__main__":
    main()
