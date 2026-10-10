---
title: NLE concepts for engineers
hours: 15
outcomes:
  - Explain media, clips, bins, timelines, tracks, and edits, and the difference between source and record time.
  - Use timecode and frame rates correctly, and find frame-rate problems before the edit.
  - Exchange timelines with OpenTimelineIO, EDL, FCPXML, and AAF, and know what each format loses.
  - Build a timeline from code (selects to timeline), and check a round trip with a diff.
  - Do a first edit in an NLE - import, cut, trim, J and L cuts, export.
keywords: [NLE, timeline, timecode, EDL, OpenTimelineIO, proxy]
summary: >
  An NLE (non-linear editor) never changes your media files. A timeline is a list of references: each edit points
  to a part of a media file (source in and out) and places it at a time on a track (record in and out). Timecode
  addresses frames, so the frame rate must be known and consistent. Timelines move between tools as exchange files:
  OpenTimelineIO is an open model with a Python API, and adapters write EDL, FCPXML, and other formats. Each format
  keeps some information and loses some, so check every round trip with a diff.
diagram:
  type: flow
  title: From selects to an editable timeline
  nodes: ["Selects (take, file, in, out)", "Script: build OTIO timeline", "Export: OTIO / FCPXML / EDL", "Import into the NLE; edit", "Export back; diff with code", "Fix what the format lost"]
  highlight: [4]
watch:
  - title: "OpenTimelineIO — documentation"
    url: https://opentimelineio.readthedocs.io/
    note: "Read 'Quickstart' and 'Architecture'."
  - title: "Blackmagic — DaVinci Resolve training (free official books and videos)"
    url: https://www.blackmagicdesign.com/products/davinciresolve/training
    note: "Download the beginner's guide; do the editing chapters (about 3 hours)."
quiz:
  - q: "You delete a clip from the timeline. What happens to the media file on disk?"
    options: ["It is deleted", "Nothing: the timeline only references the media; the file stays", "It is moved to the trash", "It is re-encoded"]
    answer: 1
    explain: "An NLE is non-destructive. Edits are references with in and out points."
  - q: "An edit has source in 00:00:01:12 and record in 00:00:10:00 at 24 fps. What do the two times mean?"
    options: ["Two copies of the clip", "Source in: the frame of the media where the edit starts (1.5 s into the file); record in: where the edit sits on the timeline (10 s)", "Two frame rates", "Audio and video"]
    answer: 1
    explain: "Source time is inside the media. Record time is on the timeline. Every exchange format stores both."
  - q: "Your selects come from three models at 16, 24, and 25 fps. The timeline is 24 fps. What do you do before you edit?"
    options: ["Nothing; the NLE handles it", "Find the clips that are not 24 fps and conform them (frame interpolation or speed change, C09·M04); otherwise motion stutters or durations change", "Change the timeline to 25 fps", "Export at 16 fps"]
    answer: 1
    explain: "Mixed frame rates cause stutter, repeated frames, or wrong durations. The starter timeline script warns about each mismatch."
  - q: "You export a timeline as an EDL and import it again. The audio track is gone and the marker notes are now in capital letters. Is the exporter broken?"
    options: ["Yes", "No: CMX 3600 EDLs carry one video track and short upper-case comments; use FCPXML, AAF, or OTIO when you need more", "The import failed", "The audio is in a second file"]
    answer: 1
    explain: "EDL is old and universal, and it is limited. Know what each format keeps."
  - q: "Why name clips on the timeline by take ID (S07_t04) instead of the file name?"
    options: ["Shorter names", "The editor, the logs, and agents can connect each edit to its take, its prompt, and its rights record", "NLEs require it", "Faster import"]
    answer: 1
    explain: "IDs connect the edit to the prompt log and the take log (C05·M06, C16)."
  - q: "What is an L-cut?"
    options: ["A cut in the shape of an L on screen", "The audio of shot A continues over the start of shot B, so the picture cuts before the sound", "A cut on a long shot", "A cut that loops"]
    answer: 1
    explain: "In a J-cut, the sound of B starts before its picture. In an L-cut, the sound of A continues under B. Both make cuts feel natural (C02·M04)."
  - q: "Why edit with proxies?"
    options: ["They look better", "Small files decode fast, so the edit is smooth on a laptop; you relink to the full-quality masters for finishing", "They have more color", "They are required for export"]
    answer: 1
    explain: "A proxy is a low-resolution copy with the same timecode and name. Finish from the masters."
deeper:
  - title: "OpenTimelineIO — GitHub (Academy Software Foundation)"
    url: https://github.com/AcademySoftwareFoundation/OpenTimelineIO
  - title: "Blackmagic — developer page (Resolve scripting API overview)"
    url: https://www.blackmagicdesign.com/developer/
  - title: "Wikipedia — Edit decision list (CMX 3600 format)"
    url: https://en.wikipedia.org/wiki/Edit_decision_list
---
## Learn

### Non-linear editing
An NLE never changes your media files. It keeps a project: a database of references and decisions. This is why you can try ten versions of a cut in one afternoon, and why a timeline file is small.

### The core objects
- **Media:** files on disk (video, audio, images). Never changed by the edit.
- **Clip:** a reference to a media file, with metadata: scene, shot, take, tags, notes.
- **Bin:** a folder of clips in the project.
- **Timeline** (also: sequence): tracks in time. Video tracks stack: V1 is at the bottom, and a higher track covers the tracks below. Audio tracks mix together.
- **Edit:** a clip placed on a track. It has two time ranges:
  - **source in and out:** which part of the media file it uses;
  - **record in and out:** where it sits on the timeline.

Every exchange format stores these two ranges for each edit. If you understand them, you can build, read, and change timelines in code.

### Timecode and frame rate
Timecode `HH:MM:SS:FF` addresses a frame: hours, minutes, seconds, frames. It means nothing without the frame rate. Common rates: 23.976, 24, 25, 29.97, 30, 50, 60. The timeline has one rate.

Generated clips come at many rates: 16, 24, 25, or 30 fps, depending on the model. Find mismatches before you edit, and conform those clips (C09·M04): interpolate frames, or change the speed if the motion allows it. A 25 fps clip on a 24 fps timeline either drops a frame every second (stutter) or plays 4 % slower.

29.97 and 23.976 rates use drop-frame or non-drop-frame timecode. Do not mix them in one project.

### Basic edits
- **Cut:** one shot ends and the next starts.
- **Trim:** move the in or the out point of an edit.
- **Ripple trim:** a trim that moves everything after the edit, so no gap appears.
- **Roll:** move a cut point between two edits; one gets longer, the other shorter.
- **J-cut and L-cut:** the audio and the picture of a cut change at different times. In a J-cut, the sound of the next shot starts first. In an L-cut, the sound of the last shot continues under the next picture. They make dialogue cuts feel natural (C02·M04).

### Exchange formats
| Format | Keeps | Loses (typical) |
|---|---|---|
| EDL (CMX 3600) | One video track: cuts, source and record times, reel names, short comments | Other tracks, effects, long names; comments become upper case |
| FCPXML | Tracks, clips, ranges, markers, many effects | Some effects between applications |
| AAF | Video and audio tracks between editing and audio systems | Depends on the tools |
| OTIO | An open model of tracks, clips, gaps, markers, and metadata, with a Python API | Effects are application-specific |

OpenTimelineIO (OTIO) is the key tool for engineers. It reads and writes many formats through adapters. You can build a timeline in Python, write it as FCPXML for the editors that read it, or as an EDL for any system.

### Round trips and diffs
When a timeline goes to another tool and back, some information can be lost. Check every round trip with a diff: compare the clips, their ranges, their order, and their markers, track by track. The same diff is how you review an agent's changes (M03).

### Proxies
Generated masters can be large: 4K, 10-bit, high bitrate. Make proxies: small copies with the same name and timecode (for example 1080p H.264 or ProRes Proxy). Edit with the proxies. Relink to the masters for color and delivery (C09).

## Tool walkthrough

### Your first edit in DaVinci Resolve (free version)
1. **Project:** open the Project Manager → New Project. In Project Settings, set the timeline frame rate (24) and resolution before you import anything. You cannot change the frame rate of a timeline later.
2. **Import:** on the Media page, drag your takes into the Media Pool. Make a bin per scene.
3. **Timeline:** on the Edit page, right-click in the Media Pool → Timelines → Create New Timeline.
4. **Cut:** open a take in the source viewer, set in (I) and out (O), and press F9 (insert) or F10 (overwrite) to put it on the timeline.
5. **Trim:** press T for the trim tool; drag the edit points. Press A to return to selection.
6. **J and L cuts:** unlink audio from video (the link button, or Ctrl/Cmd+Shift+L), then drag the audio edit point before or after the picture cut.
7. **Export a timeline:** File → Export → Timeline (FCPXML, EDL, OTIO, AAF).
8. **Render:** on the Deliver page, choose a preset (for example H.264 1080p), add to the queue, render.
Other NLEs use the same ideas with other keys. The landscape page lists the current tools.

### Build a timeline from selects

```bash
pip install opentimelineio otio-cmx3600-adapter otio-fcpx-xml-adapter
python starter/tools/takes.py selects > selects.csv            # from C05·M06
python starter/tools/selects_to_otio.py selects.csv --order shots.json --rate 24 \
  --out S01_rough.otio --edl --fcpxml
```

`shots.json` gives the shot order and the planned durations. Shots without a select become labeled gaps (`GAP S03`), so holes are visible. The script warns about frame-rate mismatches. Import the FCPXML (or OTIO) into your NLE.

### Diff two versions

```bash
python starter/tools/otio_diff.py S01_rough.otio S01_rough_from_nle.fcpxml
```

## Worked example

**Selects to timeline, and three round trips** (2026-10-04, OTIO 0.18.1). Three selects and a 4-shot order (S03 has no select):

```
{"timeline": "S01_rough", "shots": 4, "seconds": 10.0, "gaps": ["S03"],
 "files": ["rough.otio", "rough.edl", "rough.fcpxml"]}
```

The EDL (extract):

```
001  S01t01mp V     C        00:00:00:00 00:00:03:00 00:00:00:00 00:00:03:00
* FROM CLIP NAME:  S01_t01
* LOC: 00:00:00:00 RED     BEST EYELINE
002  S02t01mp V     C        00:00:00:10 00:00:02:22 00:00:03:00 00:00:05:12
003  S04t01mp V     C        00:00:00:12 00:00:03:12 00:00:07:00 00:00:10:00
```

Read event 002: source in 00:00:00:10 (the select starts 0.4 s into the file, rounded to frame 10), record in 00:00:03:00. Event 003 starts at 00:00:07:00, after the 1.5 s gap of S03.

`otio_diff.py` on the round trips:
- **OTIO → EDL:** the audio track is gone ("an EDL has one video track only"), and the marker notes changed to upper case ("best eyeline" → "BEST EYELINE"). Cuts and ranges are the same.
- **OTIO → FCPXML:** 0 changes.
- **A simulated agent edit** (trim S02 by 0.5 s, rename S04, add a marker): the diff lists exactly these 3 changes.

In a second test, the script warned: `P01 is 25.000 fps, timeline is 24.0 fps: conform it`. The clip came from a source at 25 fps. Without the warning, it would have stuttered in the edit.

## Lab

**Deliverable:** `C08/M01/` with your timeline script (or the starter script), the exported timelines, an NLE screenshot, and a round-trip report.

1. Do the first-edit steps in your NLE with 6 takes: cut, trim, one J-cut, one L-cut, render.
2. Export your selects from `takes.py`. Build a timeline with V1 and A1 in shot order, with planned durations.
3. Export OTIO, FCPXML, and EDL. Import one into your NLE. Take a screenshot.
4. Change 2 edits in the NLE (a trim and a reorder). Export the timeline. Diff it against the original with `otio_diff.py`.
5. Do the EDL round trip. Write what the format lost.
6. Check the frame rate of every take. Conform any mismatch (or list it for C09).

**Result checklist**
- [ ] A rendered first edit with a J-cut and an L-cut.
- [ ] Timeline built by code; imported in the NLE.
- [ ] Diff report that shows exactly your 2 changes.
- [ ] List of what the EDL lost; frame-rate check done.

## Model answer

**Round-trip report (shape of a strong answer):**

| Round trip | Changes found | Expected? |
|---|---|---|
| OTIO → Resolve (FCPXML) → back | trim S04 −8 frames; S06 and S07 swapped | Yes: my 2 edits |
| OTIO → EDL → back | audio track missing; notes upper case; long clip names cut to 8 characters in the reel field | Known EDL limits |
| OTIO → FCPXML → back (no edit) | none | — |

"Rule for this project: FCPXML between the script and Resolve; EDL only for a system that needs it, and never as the master."

**Frame-rate check:** "14 takes at 24 fps, 3 at 16 fps (the open model), 1 at 30 fps. The 16 fps takes go to frame interpolation (C09·M04) before the fine cut. The 30 fps take is a 1 s insert: I slowed it to 24 fps (80 % speed); the motion still looks natural."

The script uses take IDs as clip names, puts the take note into a marker, and makes a labeled gap for every shot without a select.
