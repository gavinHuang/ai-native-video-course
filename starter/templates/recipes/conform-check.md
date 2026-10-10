# Recipe: conform check (read-only)

**Use:** before the fine cut and before delivery (C08·M03, C09·M04).
**Permissions:** read the timeline; add markers. Do not change, move, or delete any clip.

Instruction for the agent:

> For the timeline "{timeline}":
> 1. List every clip on all video tracks whose frame rate is not {fps}, whose resolution is not {width}x{height},
>    or whose color space is not {color_space}.
> 2. For each one, add a red marker at the start of the clip. Marker name: the problem ("FPS 30", "RES 1280x720").
>    Marker note: the clip name and the value found.
> 3. Do not change any clip, setting, or track.
> 4. Report as JSON: [{"type": "markers", "clip": "<name>", "problem": "<text>"}].

**Check after the session:** export the timeline (OTIO or FCPXML) and run
`otio_diff.py before after --json diff.json` and `agent_review.py --log report.json --diff diff.json`.
The only changes allowed are markers.
