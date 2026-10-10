# Recipe: multi-format render with spec checks

**Use:** delivery of one master in several formats (C08·M04, C09·M04, C10·M02).
**Permissions:** add render jobs; read rendered files. Do not change the timeline.

Instruction for the agent:

> For the timeline "{timeline}", add render jobs with these presets: {presets, for example "YT_16x9", "Reels_9x16"}.
> Name each file "{project}_{version}_{preset}_{date}".
> After rendering, check each file: resolution, frame rate, duration (± 1 frame of the timeline), integrated
> loudness {target} LUFS ± 1, true peak ≤ −1 dBTP. Use ffprobe and ffmpeg ebur128 if you have a shell tool.
> Report a table: file, each check, pass or fail. Do not change the timeline or the mix to fix a failure; report it.

**Check:** the timeline diff must be empty. The editor fixes failures and runs the recipe again.
