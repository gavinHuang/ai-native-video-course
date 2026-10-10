---
title: Agents in the NLE through MCP
hours: 15
outcomes:
  - Connect an AI assistant to an NLE through MCP, a built-in assistant, a bridge, or your own scripting wrapper.
  - Delegate organization, conform checks, markers, versions, and renders, with clear permissions per task.
  - Review every agent session with a timeline diff and a check of the agent's own log.
  - Write and test repeatable agent recipes for your team.
keywords: [MCP, agent recipe, conform, plan-approve-act-review]
summary: >
  Current NLEs can be operated by AI agents: some have a native MCP server or a built-in assistant, others work
  through bridges or scripting APIs. Agents are good at mechanical work: organizing bins, renaming, conform checks,
  markers, cut-downs by rules, and render queues. You keep story, rhythm, performance, music, and approval. Run
  every session as plan, approve, act, review. Work on a duplicate, ask the agent to log every change, and compare
  its log with a diff of the timeline before and after. Save tested instructions as recipes.
diagram:
  type: cycle
  title: An agent session
  nodes: ["Plan: agent proposes steps", "Approve: you accept or change", "Act: on a duplicate timeline", "Log: every change as JSON", "Review: diff + log check"]
  center: "Editor decides"
watch:
  - title: "DaVinci Resolve 21.1 MCP — Y.M.Cinema"
    url: https://ymcinema.com/2026/09/17/davinci-resolve-21-1-mcp-ai-assistants-control-edit/
    note: "Read the list of actions."
  - title: "Broadcast Now — Adobe rolls out AI agent on Premiere"
    url: https://www.broadcastnow.co.uk/production-and-post/adobe-rolls-out-ai-agent-on-premiere/5217912.article
    note: "Note which project-panel and timeline tasks it can do."
quiz:
  - q: "Which task do you give to an agent, and which do you keep?"
    options: ["Give it the music choice", "Give it the conform check (frame rate, resolution, color space) with markers; keep the choice of performance and the rhythm of the cut", "Give it final approval", "Give it everything"]
    answer: 1
    explain: "Agents are fast and exact at mechanical checks. Story and feeling are the editor's decisions."
  - q: "Why does the agent work on a duplicate timeline?"
    options: ["It is faster", "If it makes a mistake, the original is untouched; you compare the two and accept only the right changes", "MCP requires it", "To save storage"]
    answer: 1
    explain: "A duplicate is the cheapest safety net, safer than undo across many steps."
  - q: "The agent says: 'I renamed 18 clips.' The diff shows 18 renames and 2 trims. What do you do?"
    options: ["Accept it", "Treat the 2 trims as unreported changes: find out why, revert them on the original, and fix the recipe so the agent cannot trim", "Delete the timeline", "Ignore the diff"]
    answer: 1
    explain: "Unreported changes are the dangerous ones. A review that compares the log and the diff finds them."
  - q: "What makes a good agent recipe?"
    options: ["A short wish ('fix the timeline')", "A precise task, the allowed actions, explicit 'do not change' rules, the output format of the report, and how you check it", "A long story", "Only the timeline name"]
    answer: 1
    explain: "A recipe is like a function: inputs, allowed side effects, output, and a test."
  - q: "You test a recipe on a second timeline, and the result is different from the first run. What does this tell you?"
    options: ["The agent is random, accept it", "The recipe is ambiguous or depends on something not stated (metadata, track layout); make it more precise and test again", "The NLE is broken", "Use a different agent"]
    answer: 1
    explain: "A recipe is ready when it gives the same kind of result on different material."
  - q: "Your NLE has no native MCP server. What are your options?"
    options: ["None", "A built-in assistant, a bridge tool, or your own MCP server that wraps the NLE's scripting API with a few safe tools (C12·M03)", "Use another computer", "Edit by hand only"]
    answer: 1
    explain: "A scripting API plus a small MCP server gives an agent exactly the tools that you choose."
  - q: "Why add markers where the agent changed something?"
    options: ["For color", "The editor can jump to every change and review it in context, in the NLE", "Markers are required by MCP", "For the render"]
    answer: 1
    explain: "Markers make the agent's work visible inside the editor's normal workflow."
deeper:
  - title: "Jumper — agentic editing (Premiere, Resolve, Final Cut, Avid)"
    url: https://getjumper.io/ai-agents
  - title: "EditAssist — MCP integrations"
    url: https://editassist.dev/integrations
  - title: "Model Context Protocol — specification (tools, permissions)"
    url: https://modelcontextprotocol.io/specification
---
## Learn

### How an agent reaches the NLE
An agent is an LLM that can call tools (C03·M04). To edit, it needs tools that read and change the NLE project. There are four ways to give it these tools:
1. **A native MCP server** in the NLE: the NLE offers tools (list clips, add markers, rename, render) to any MCP client (C03·M05).
2. **A built-in assistant** inside the NLE: the vendor's own agent, with its own set of actions.
3. **A bridge:** a separate application that connects MCP clients to one or more NLEs.
4. **Your own MCP server** around the NLE's scripting API: you choose a few safe tools and their limits (C12·M03).

### Good tasks for agents
Agents are fast and exact at mechanical, rule-based work:
- **Organize:** bins by scene, rename clips from metadata, add metadata from the shot list.
- **Markers:** shots shorter than N frames, flash frames, gaps, offline media, frame-rate mismatches.
- **Conform checks:** frame rate, resolution, and color space of every clip (read-only).
- **Versions by rules:** a 15 s cut-down from marked shots of the 30 s; 9:16 timelines (M04).
- **Renders:** queue several formats; check delivery specs (C09·M04, C10·M02).

### Keep for the editor
Story, rhythm, the choice of performance, the music, and the final approval. These need judgment about feeling and meaning. An agent can propose; you decide.

### Plan, approve, act, review
Run every session in this cycle:
1. **Plan:** the agent lists the steps it will take. Read them.
2. **Approve:** accept, change, or remove steps.
3. **Act:** the agent works on a duplicate timeline, never on the original.
4. **Log:** the agent writes every change as a structured record (type, clip, old value, new value) and adds a marker at each change.
5. **Review:** export the timeline before and after, diff them with code (M01), and compare the diff with the agent's log.

The log check finds two kinds of problems:
- **Unreported changes:** the diff shows a change that the log does not mention. These are the dangerous ones.
- **Not done:** the log claims a change that the diff does not show.
`starter/tools/agent_review.py` does this comparison.

### Permissions
Give each task the least power that it needs, like any API design:
- A conform check needs read access and markers. It must not move clips.
- A rename task needs rename only.
- A render task must not change the timeline.
Write the permissions into the recipe. If your MCP server or bridge supports it, give the agent only the tools of that task.

### Recipes
A recipe is a tested instruction that your team can reuse. It has:
- the task, with placeholders (timeline name, frame rate);
- the allowed actions, and explicit "do not change" rules;
- the format of the agent's report (JSON);
- how to check it (the diff and the log check).
Test each recipe on two different timelines. If the results differ in kind, the recipe is ambiguous: make it more precise. The starter kit has three recipe templates in `templates/recipes/`.

## Tool walkthrough

### Connection options (as of 2026-10)
- **DaVinci Resolve Studio 21.1:** native MCP server. Assistants can organize timelines, rename, grade, apply LUTs, add markers, render, and check delivery specs. Works with MCP clients such as Claude Desktop and Claude Code.
- **Adobe Premiere 26.x:** Firefly AI Assistant inside the app (bins, renames, markers, first cut, storyboard to video). An MCP server is reported.
- **Bridges:** Jumper (local MCP for Premiere, Resolve, Final Cut, Avid), EditAssist.
- **Scripting APIs:** Resolve has a Python and Lua API (also in the free version, with limits); Premiere has UXP scripting.

### A read-only conform check with the Resolve Python API
This sketch uses the Resolve scripting API (see the README in Resolve's Developer folder). We did not run it for this release, because it needs a Resolve installation. Wrap it as an MCP tool in C12·M03.

```python
import DaVinciResolveScript as dvr
resolve = dvr.scriptapp("Resolve")
project = resolve.GetProjectManager().GetCurrentProject()
tl = project.GetCurrentTimeline()
target_fps = float(project.GetSetting("timelineFrameRate"))
report = []
for item in tl.GetItemListInTrack("video", 1):
    mp = item.GetMediaPoolItem()
    fps = float(mp.GetClipProperty("FPS") or 0)
    if abs(fps - target_fps) > 0.01:
        frame = item.GetStart() - tl.GetStartFrame()
        tl.AddMarker(frame, "Red", f"FPS {fps:g}", item.GetName(), 1)  # frame is relative to the timeline start
        report.append({"type": "markers", "clip": item.GetName(), "problem": f"FPS {fps:g}"})
print(report)
```

### Review a session

```bash
python starter/tools/otio_diff.py before.otio after.otio --json diff.json
python starter/tools/agent_review.py --log agent_log.json --diff diff.json
```

## Worked example

**Review test** (2026-10-04). A timeline with 3 clips. A simulated agent session renamed S04, trimmed S02, and added a marker on S01. Two agent logs were checked against the measured diff:

| Agent log | `agent_review.py` result |
|---|---|
| Lists all 3 changes | MATCH |
| Lists the rename and the marker, and a relink of S03 that it did not do; forgets the trim | UNREPORTED change: trimmed S02_t01; NOT DONE: relinked S03_t01 |

The second case is the typical failure: the agent did something extra and claimed something it did not do. Only a check against the real timeline finds it.

**Session on a 30 s ad** (Resolve Studio 21.1 via MCP, with an MCP client):
1. "Duplicate timeline 'Ad v5' as 'Ad v5 agent'." ✓
2. Recipe `conform-check` with fps 24 → 3 clips at 30 fps marked red. Diff: 3 markers only ✓.
3. Recipe `rename-from-metadata` → 18 clips renamed; 2 clips without metadata marked "NO METADATA" ✓.
4. Recipe `multi-format-render` with "YT_16x9" and "Reels_9x16" → both rendered; the 9:16 file at −12.8 LUFS flagged (target −14 ± 1).
5. The editor reviews the markers, conforms the 30 fps clips (C09·M04), fixes the mix (C10·M02), and runs the render recipe again.

## Lab

**Deliverable:** `C08/M03/` with a session log, before and after timelines, a diff report, an `agent_review.py` result, and 3 tested recipes.

1. Connect an agent to your NLE: a native MCP server, a built-in assistant, a bridge, or your own scripting wrapper.
2. Run a 6-step session on a duplicate of your C05 sequence, with plan and approval for each step.
3. Ask the agent to log every change as JSON and to add a marker at each change.
4. Export the timeline before and after. Run `otio_diff.py` and `agent_review.py`. Explain every unreported change.
5. Adapt the 3 recipe templates (conform check, rename, multi-format render) to your NLE. Test each one on two different timelines.

**Result checklist**
- [ ] Session log with plan, approvals, and actions.
- [ ] Diff report and an `agent_review.py` result (MATCH, or each problem explained).
- [ ] 3 recipes, each tested twice, with the results.

## Model answer

**Review (shape of a strong answer):** "Step 5 (rename) also trimmed 2 clips by 1 frame. The agent did not report it. Cause: it used 'replace clip' instead of 'rename' for 2 clips with a long name. Fix: the recipe now says 'Use the rename action only. Never replace a clip.' On the second run: MATCH."

**Recipe test table:**

| Recipe | Timeline A | Timeline B | Same kind of result? | Change to the recipe |
|---|---|---|---|---|
| Conform check | 3 markers, 0 other changes | 0 markers (all 24 fps), 0 changes | Yes | — |
| Rename from metadata | 18 renamed, 2 "NO METADATA" | 9 renamed | Yes | — |
| Multi-format render | 2 files, 1 loudness fail | 2 files, both pass | Yes | Added "report, do not fix" after the agent tried to change the mix in run 1 |

"Agents saved about 25 minutes per version on mechanical work. The review step takes 3 minutes and found one real problem in 6 sessions."
