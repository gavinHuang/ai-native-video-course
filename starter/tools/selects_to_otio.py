#!/usr/bin/env python3
"""Build an editable timeline from selects (C08·M01, C08·M02). Needs OpenTimelineIO.

  pip install opentimelineio otio-cmx3600-adapter otio-fcpx-xml-adapter
  python selects_to_otio.py selects.csv --order shots.json --rate 24 --out S01_rough.otio [--edl] [--fcpxml]

selects.csv: the output of `takes.py selects` (shot, take, file, in, out, usable_s, note).
shots.json:  optional; the shot order and planned durations ([{"id": "S01", "dur": 3.0}, ...]). Without it,
             the order of the CSV is used. With it, each select is trimmed to the planned duration (from its
             in point), and shots without a select become a labeled gap, so holes are visible in the edit.

The timeline has V1 (picture) and A1 (the clip's own audio, same ranges). Clip names are take IDs, and the
take note goes into a marker, so the editor sees why a take was chosen. Use one select per shot: the first
in the CSV, or the one with "chosen" in its note.
"""
import argparse
import csv
import json
import sys
from pathlib import Path


def probe(path):
    """Return (duration_s, fps) of a media file, or (None, None)."""
    import subprocess
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                              "stream=r_frame_rate:format=duration", "-of", "json", str(path)],
                             capture_output=True, text=True, check=True).stdout
        d = json.loads(out)
        num, den = map(int, d["streams"][0]["r_frame_rate"].split("/"))
        return float(d["format"]["duration"]), num / den
    except Exception:  # noqa: BLE001 - missing file or no video stream
        return None, None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("selects")
    ap.add_argument("--order")
    ap.add_argument("--rate", type=float, default=24)
    ap.add_argument("--name", default="rough")
    ap.add_argument("--out", required=True)
    ap.add_argument("--edl", action="store_true", help="also write a CMX3600 EDL (one video track)")
    ap.add_argument("--fcpxml", action="store_true", help="also write FCPXML (Final Cut Pro, Resolve)")
    a = ap.parse_args()
    try:
        import opentimelineio as otio
    except ImportError:
        sys.exit("pip install opentimelineio")
    RT, TR = otio.opentime.RationalTime, otio.opentime.TimeRange
    rows = list(csv.DictReader(open(a.selects)))
    by_shot = {}
    for r in rows:
        if r["shot"] not in by_shot or "chosen" in (r.get("note") or "").lower():
            by_shot[r["shot"]] = r
    order = json.loads(Path(a.order).read_text()) if a.order else [{"id": s} for s in dict.fromkeys(r["shot"] for r in rows)]
    tl = otio.schema.Timeline(name=a.name, global_start_time=RT(0, a.rate))
    v1 = otio.schema.Track(name="V1", kind=otio.schema.TrackKind.Video)
    a1 = otio.schema.Track(name="A1", kind=otio.schema.TrackKind.Audio)
    tl.tracks.extend([v1, a1])
    total, gaps = 0.0, []
    for sh in order:
        sel = by_shot.get(sh["id"])
        planned = float(sh["dur"]) if sh.get("dur") is not None else None
        if sel is None:
            dur = planned or 2.0
            for tr in (v1, a1):
                g = otio.schema.Gap(source_range=TR(RT(0, a.rate), RT(round(dur * a.rate), a.rate)))
                g.name = f"GAP {sh['id']}"
                tr.append(g)
            gaps.append(sh["id"])
            total += dur
            continue
        t_in, t_out = float(sel["in"]), float(sel["out"])
        dur = min(planned, t_out - t_in) if planned else t_out - t_in
        if planned and t_out - t_in < planned - 1 / a.rate:
            print(f"warning: {sh['id']}: select is {t_out - t_in:.2f} s, planned {planned:.2f} s", file=sys.stderr)
        rng = TR(RT(round(t_in * a.rate), a.rate), RT(round(dur * a.rate), a.rate))
        media_dur, media_fps = probe(sel["file"]) if sel["file"] else (None, None)
        if media_fps and abs(media_fps - a.rate) > 0.01:
            print(f"warning: {sel['take']} is {media_fps:.3f} fps, timeline is {a.rate} fps: conform it (C09·M04)",
                  file=sys.stderr)
        for tr in (v1, a1):
            ref = otio.schema.ExternalReference(target_url=str(Path(sel["file"]).resolve()) if sel["file"] else "")
            if media_dur:
                ref.available_range = TR(RT(0, a.rate), RT(round(media_dur * a.rate), a.rate))
            c = otio.schema.Clip(name=sel["take"], media_reference=ref, source_range=rng)
            c.metadata["course"] = {"shot": sh["id"], "take": sel["take"], "note": sel.get("note", "")}
            if tr is v1 and sel.get("note"):
                c.markers.append(otio.schema.Marker(name=sel["note"][:60], marked_range=TR(RT(0, a.rate), RT(1, a.rate))))
            tr.append(c)
        total += dur
    otio.adapters.write_to_file(tl, a.out)
    outs = [a.out]
    stem = Path(a.out).with_suffix("")
    if a.edl:
        v_only = otio.schema.Timeline(name=a.name, global_start_time=RT(0, a.rate))
        v_only.tracks.append(v1.deepcopy())
        otio.adapters.write_to_file(v_only, f"{stem}.edl", adapter_name="cmx_3600")
        outs.append(f"{stem}.edl")
    if a.fcpxml:
        otio.adapters.write_to_file(tl, f"{stem}.fcpxml", adapter_name="fcpx_xml")
        outs.append(f"{stem}.fcpxml")
    print(json.dumps({"timeline": a.name, "shots": len(order), "seconds": round(total, 2), "gaps": gaps, "files": outs}))


if __name__ == "__main__":
    main()
