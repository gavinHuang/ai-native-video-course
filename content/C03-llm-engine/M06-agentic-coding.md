---
title: Agentic coding tools for media work
hours: 9
outcomes:
  - Use an agentic coding tool to build, run, and fix small media tools.
  - Give the tool a project memory file with rules and commands.
  - Review and test code that an agent writes.
  - Drive headless creative tools (ffmpeg, ComfyUI API) from an agent.
keywords: [agentic coding, project memory, headless, ffmpeg]
summary: >
  Agentic coding tools, such as Claude Code and Codex, run in your terminal. They read your files, write code, run
  commands, and fix errors in a loop. For a media creator with IT skills, they are a fast way to build small tools:
  batch renders, contact sheets, prompt builders, uploaders, and ComfyUI drivers. Give the agent a project memory
  file with rules and commands. Review every change with Git, and require tests. The agent can also drive headless
  tools directly, for example ComfyUI through its JSON API.
diagram:
  type: flow
  title: Build a media tool with an agent
  nodes: ["You: goal + constraints", "Agent reads repo + memory file", "Agent writes code + tests", "Agent runs, reads errors, fixes", "You review diff (git)", "Commit + reuse in pipeline"]
  highlight: [4]
watch:
  - title: "Claude Code — official docs (overview and best practices)"
    url: https://docs.anthropic.com/en/docs/claude-code/overview
    note: "Read the overview and 'memory' (CLAUDE.md) pages."
  - title: "Purz on X — Claude Code operating ComfyUI headless"
    url: https://x.com/PurzBeats/status/2030461786982392113
    note: "Short demo: the agent sends workflow JSON to the ComfyUI API."
quiz:
  - q: "What belongs in a project memory file (for example CLAUDE.md)?"
    options: ["API keys", "Project rules, folder layout, build/test commands, do-not-touch paths", "The full footage list", "Client invoices"]
    answer: 1
    explain: "Stable rules and commands. Never secrets."
  - q: "Best protection against a bad agent change?"
    options: ["Trust the agent", "Work in Git; review the diff; run tests before commit", "Use a bigger model", "Disable logging"]
    answer: 1
    explain: "Version control + review + tests."
  - q: "'Headless' ComfyUI means:"
    options: ["ComfyUI without a GPU", "ComfyUI controlled through its API, without the web UI", "ComfyUI with no models", "A paid version"]
    answer: 1
    explain: "You send workflow JSON to the server and receive outputs."
  - q: "An agent proposes `rm -rf footage/` to 'clean up'. What should have prevented this?"
    options: ["Nothing", "Permission settings that block destructive commands + human confirmation", "A faster SSD", "A longer prompt"]
    answer: 1
    explain: "Use the tool's permission system; deny destructive commands by default."
  - q: "A test fails, and the agent 'fixes' it by changing the expected value in the test. What do you do?"
    options: ["Accept it", "Reject the change: ask why the code gives a different value, and fix the code or explain why the test was wrong", "Delete the test", "Use a bigger model"]
    answer: 1
    explain: "Weakening tests is a typical agent mistake. Review test changes with extra care."
  - q: "Your tool passes all tests on generated test clips, then fails on a client file. What do you add?"
    options: ["Nothing", "A test for that edge case (for example no audio track, variable frame rate, or spaces in the name), made with ffmpeg sources, then the fix", "A longer prompt", "Manual checks only"]
    answer: 1
    explain: "Each real failure becomes a test, so it never comes back."
deeper:
  - title: "ComfyUI — Server routes / API docs"
    url: https://docs.comfy.org/development/comfyui-server/comms_routes
  - title: "FFmpeg documentation"
    url: https://ffmpeg.org/documentation.html
---
## Learn

### What these tools do
An **agentic coding** tool is an agent (C03·M04) with tools for files and the shell. It reads your repository, writes code, runs it, reads the errors, and fixes them. Terminal agents, IDE agents, and cloud agents all work this way (dated names in the Tool walkthrough). For you, with IT skills, this is the fastest way to build the small tools that an AI-native production needs.

### Good tasks for an agent
- Batch jobs: transcode, proxies, contact sheets, loudness normalize.
- Glue code: shot list → prompts → API calls → downloads → naming.
- Drivers for **headless** tools: node-graph server APIs, NLE scripting APIs, MCP servers.
- Checks: ffprobe spec checks, file naming lints, cost reports.

### Project memory
Write a memory file in the repo root (each tool has its own file name; see the Tool walkthrough). Include:
- the goal of the repo,
- folder layout and naming rules,
- commands to build, test, and run,
- forbidden actions (never delete `footage/`, never overwrite masters),
- style rules (Python version, type hints, tests required).

### Review and test
- Work on a branch. Review each diff before you merge it.
- Ask the agent to write tests first for anything that touches media files.
- Use permission settings to block destructive commands, by default.
- Keep secrets in environment variables, never in the repo or the memory file.

### Write the task like a ticket
A good task for a coding agent has five parts. Give the goal in one sentence, and the inputs and outputs (file types, a CLI shape). Give the constraints (only ffmpeg, Python 3.12, no network), the test that proves it works, and what it must not touch. Small tasks with a test finish well. "Build the whole pipeline" does not: split it into tools that each do one job, and let the agent build and test them one by one.

### What agents get wrong
Agents are fast and confident, and they make typical mistakes. They assume a tool or a font exists. They write a command that works on their example but not on your files (spaces in names, variable frame rate, no audio track). They "fix" a failing test by weakening the test. They add a dependency that you did not want. Review the diff with these in mind, and run the tests yourself. Test on a real file from your project, not only on generated test media.

### Media in tests
Make test media in the test itself with ffmpeg's built-in sources (`testsrc2`, `sine`, `anullsrc`): a few seconds at small size, generated in milliseconds. Then tests do not depend on files that nobody can share, and they run in CI. Add one test for each edge case that broke the tool in real use: no audio, odd sizes, 23.976 fps, a long file name with spaces.

### Driving headless tools
A node-graph generation tool can run as a server. You export a workflow in "API format" (JSON). A script changes inputs (prompt, seed, image) and sends it to the server, then reads the results. An agent can write this script, call it as a tool, or use an MCP server that wraps it (C11·M04).

## Tool walkthrough

### Tools (as of 2026-10)
- Terminal agents: Claude Code (memory file `CLAUDE.md`, permission settings, MCP servers), OpenAI Codex CLI (`AGENTS.md`).
- IDE agents in VS Code and JetBrains; cloud agents that open pull requests.

### Reference solutions in the starter kit
Compare your agent's result with the tested versions: `starter/tools/spec_check.py` (delivery checks, C10·M03) and `starter/solutions/C11-M04/comfy_run.py` with `test_comfy_run.py` (a headless ComfyUI client, tested against a fake server).

## Worked example

Prompt to the agent (in the repo `ai-video-lab`):
> Build `tools/contact_sheet.py`. Input: a folder of MP4 files. Output: one PNG per file with 12 frames in a 4×3 grid, timecode burned in, file name in the header. Use ffmpeg only. Add a pytest test with a 3-second test clip made by ffmpeg `testsrc`. Do not touch `footage/`.

The agent:
1. Reads `CLAUDE.md` (rules, Python 3.12, pytest).
2. Writes the script with `ffmpeg -vf "select=..., drawtext=timecode..., tile=4x3"` (it assumes the `drawtext` filter exists).
3. Writes a test that makes a clip with `ffmpeg -f lavfi -i testsrc=duration=3:size=640x360:rate=24`.
4. Runs pytest; it fails: the installed ffmpeg (9.0.2 in the course tests) has no `drawtext` filter. The agent switches to Pillow: it renders the timecode labels as PNG images and overlays them with ffmpeg. The test passes.
5. You review the diff and commit.

## Lab

**Deliverable:** 3 tools in `ai-video-lab/tools/`, each made with an agentic coding tool, each with tests.

1. Write `CLAUDE.md` (or the equivalent) for your repo.
2. Build `contact_sheet.py` (as above).
3. Build `spec_check.py`: reads a delivery spec YAML (resolution, fps, codec, loudness range) and checks files with ffprobe and ffmpeg `ebur128`. Exit code ≠ 0 on failure.
4. Build `comfy_run.py`: loads a ComfyUI API-format workflow, sets prompt and seed, submits it, waits, downloads outputs. (No GPU? Use a cloud ComfyUI or mock the server in tests.)
5. Record what you asked, what the agent did wrong, and how you corrected it.

**Result checklist**
- [ ] 3 tools, each with passing tests.
- [ ] Memory file with forbidden actions.
- [ ] A short log of agent mistakes and fixes.

## Model answer

Good results have small, single-purpose scripts with a CLI, tests that make their own test media with ffmpeg `lavfi`, and a spec checker that prints clear failures ("fps 30 ≠ 24"; "integrated loudness −11.2 LUFS above −14 ±1"). Typical agent mistakes: wrong ffmpeg filter escaping, assuming a font file exists, polling ComfyUI without a timeout. Each was found by tests or by review.

**Mistake log (shape):** "Task: contact sheets. Agent used `drawtext`; our ffmpeg has no such filter → test failed → I told it to render labels with Pillow. Task: spec check. Agent read loudness from the wrong ffmpeg output line → my test with a −23 LUFS tone caught it. Task: ComfyUI client. Agent polled forever → I asked for a timeout and a test with a server that never answers." Each entry names the task, the mistake, how it was found, and the correction.
