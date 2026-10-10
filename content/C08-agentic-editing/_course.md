---
code: C08
title: Agentic Editing
level: 3
hours: 60
prereq: C02, C03, C05
outcomes:
  - Explain NLE concepts - media, bins, timelines, tracks, edits - and their exchange formats.
  - Assemble a rough cut automatically from a script, transcript, and selects.
  - Let an agent operate an NLE through MCP, with review and undo.
  - Make long-to-short and multi-format versions automatically.
---
## About this course

The edit is where a video becomes a story. In 2026, agents can do much of the mechanical work: organize, assemble, trim, version, and render. You stay the editor: you decide rhythm, emotion, and story. Tools: DaVinci Resolve (free; Studio 21.1 for native MCP), Adobe Premiere (Firefly AI Assistant; MCP), Final Cut Pro, Avid Media Composer, Descript, CapCut; OpenTimelineIO for exchange.

**Starter tools for this course** (in the [starter kit](starter.zip)):

| Tool | Use |
|---|---|
| `tools/selects_to_otio.py` | Selects → timeline (OTIO, FCPXML, EDL), with gaps and frame-rate warnings (M01, M02) |
| `tools/otio_diff.py` | What changed between two timelines: round trips and agent sessions (M01, M03) |
| `tools/papercut.py` | Validates an LLM paper edit against the transcript; rejects invented, merged, or changed quotes (M02) |
| `tools/agent_review.py` | Compares an agent's log with the timeline diff; finds unreported changes (M03) |
| `templates/recipes/` | Agent recipes: conform check, rename from metadata, multi-format render (M03) |
| `tools/reframe.py` | Face-tracked 9:16 reframe with a report of two-shots and fast moves (M04) |
| `tools/captions.py` | Burned-in captions inside safe zones; SRT and VTT (M04) |

Python packages: `pip install opentimelineio otio-cmx3600-adapter otio-fcpx-xml-adapter opencv-python pillow`.
