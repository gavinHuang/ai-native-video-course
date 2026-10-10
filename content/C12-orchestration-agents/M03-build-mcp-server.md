---
title: Build your own MCP server for media
hours: 16
outcomes:
  - Design tools for agents - names, descriptions, schemas, short results, actionable errors.
  - Implement an MCP server in Python (SDK 2.x) that wraps your media functions and your queue.
  - Add a path sandbox, dry runs, confirmation for cost, budget guards, and an audit log.
  - Test the server at the protocol level with an MCP client, including adversarial tests.
  - Connect it to a real agent and check the audit log against what you asked for.
keywords: [MCP server, tool design, sandbox, audit log, dry run]
summary: >
  An MCP server gives agents tools. Design each tool like a small API: a clear verb-object name, a description that
  says when to use it and what it returns, strict typed inputs, short results with IDs, and errors that say what to
  do next. Wrap your tested media functions and your queue. Make side effects safe: paths only inside the project,
  no delete tools, dry runs by default, confirmation above a cost, budget caps in the queue, and an audit log of every
  call. Test the server through the real protocol, including requests that it must refuse.
diagram:
  type: flow
  title: A safe generation tool call
  nodes: ["Agent: estimate_generation", "Agent: queue_generation (dry run)", "Person approves (cost > limit)", "queue_generation(confirm=True)", "Queue: idempotency + budget caps", "Audit log: every call"]
  highlight: [2, 5]
watch:
  - title: "MCP — build a server (official guide)"
    url: https://modelcontextprotocol.io/quickstart/server
    note: "Follow the Python path. Check the SDK version: SDK 2.x renamed FastMCP to MCPServer."
  - title: "MCP Python SDK — GitHub"
    url: https://github.com/modelcontextprotocol/python-sdk
    note: "Read the server examples and the v2 migration notes."
quiz:
  - q: "Which tool description helps an agent most?"
    options: ["'Generates video.'", "'Queue one generation. Without confirm=True this is a dry run. Costs above the approval limit need a human approval file. The same shot_key twice never pays twice.'", "'Use this tool.'", "An empty description"]
    answer: 1
    explain: "The description is the agent's documentation: what it does, when to use it, what it returns, and its limits."
  - q: "The agent asks probe_media for '../../etc/passwd'. What must the server do?"
    options: ["Return the file", "Resolve the path and refuse anything outside the project root, with a clear error; log the attempt", "Crash", "Ask the agent why"]
    answer: 1
    explain: "A tool is an attack surface. In the starter server test, both '../../etc/passwd' and '/etc/passwd' were refused."
  - q: "Why does queue_generation default to a dry run?"
    options: ["It is faster", "The agent must see the cost first; a real run needs an explicit confirm=True, and above a limit a person's approval", "MCP requires it", "To save tokens"]
    answer: 1
    explain: "Expensive or irreversible actions need two steps. The person stays in control of money."
  - q: "Where is the budget cap enforced: in the tool, or in the queue?"
    options: ["Only in the tool", "In the queue (the single place where all jobs go), so that every path - agent, script, person - is limited; the tool adds the confirmation step", "In the agent's prompt", "Nowhere"]
    answer: 1
    explain: "Guards belong where they cannot be bypassed. A prompt instruction is not a guard."
  - q: "An MCP SDK upgrade breaks your server: 'No module named mcp.server.fastmcp'. What happened, and what do you do?"
    options: ["The SDK is broken", "SDK 2.x renamed FastMCP to MCPServer and changed other APIs; read the migration guide, update the imports, and pin the SDK version in your requirements", "Reinstall Python", "Remove MCP"]
    answer: 1
    explain: "This happened while this module was written (SDK 2.3.0, 2026-10). Pin dependencies and run protocol tests in CI."
  - q: "How do you test an MCP server so that the test proves what an agent will see?"
    options: ["Call the Python functions directly", "Start the server as a subprocess and talk to it with an MCP client over stdio: list tools, call them, read resources", "Read the code", "Ask an agent once"]
    answer: 1
    explain: "Protocol tests catch schema, serialization, and transport problems that direct function calls miss."
  - q: "What does each audit-log line need?"
    options: ["Only the time", "Time, tool, arguments, and a summary of the result (including refusals and errors)", "The agent's thoughts", "Nothing"]
    answer: 1
    explain: "The audit log is how you review what an agent did, and the evidence when something goes wrong."
deeper:
  - title: "MCP Inspector (interactive testing tool)"
    url: https://github.com/modelcontextprotocol/inspector
  - title: "Anthropic — Writing effective tools for agents"
    url: https://www.anthropic.com/engineering/writing-tools-for-agents
  - title: "MCP Python SDK v2 — migration guide"
    url: https://py.sdk.modelcontextprotocol.io/v2/migration/
---
## Learn

### What an MCP server is
The Model Context Protocol (C03·M05) connects an agent (the client side) with tools and data (the server side). An MCP server publishes:
- **tools:** functions the agent can call, each with a name, a description, and an input schema;
- **resources:** data the agent can read, each with a URI (for example `studio://budget`);
- **prompts:** reusable instructions (optional).
The agent's model reads the tool names, descriptions, and schemas, and decides which tool to call with which arguments. So tool design is interface design for a model.

### Tool design
- **Name:** a verb and an object: `probe_media`, `queue_generation`, `job_status`.
- **Description:** what it does, when to use it, what it returns, and its limits. "Without confirm=True this is a dry run."
- **Inputs:** strict types and ranges. Few parameters. Use enums for choices (a spec name, not a free path).
- **Results:** short JSON with the facts and the IDs that the agent can pass to other tools. Do not return large blobs; return a path.
- **Errors:** say what to do next. "Unknown spec 'web'; known: broadcast_ebu_r128, reels_9x16, web_1080p." An agent can recover from that error.
- **Granularity:** one tool per meaningful action. Not one tool per ffmpeg flag, and not one tool that "does everything".

### Safety
An agent tool is an attack surface and a cost risk. Design for the least power:
1. **Path sandbox:** resolve every path, and refuse anything outside the project root (`..`, absolute paths, symbolic links outside).
2. **No delete tools.** Write new files only; overwrite only in a work folder.
3. **Dry run by default** for anything that costs money or changes state. A real run needs `confirm=True`.
4. **Human approval above a limit:** above a cost, the tool needs evidence of a person's approval (an approval file, a ticket, a button in your UI). The agent cannot create it.
5. **Budget guards in the queue** (M01), not only in the tool, so that every path to the queue is limited.
6. **Input limits:** prompt length, duration range, number of shots per call.
7. **Audit log:** every call, with its arguments and a result summary, including refusals.

### Implementation (Python SDK 2.x)
The current Python SDK (2.3, as of 2026-10) uses `MCPServer`:

```python
from mcp.server.mcpserver import MCPServer
mcp = MCPServer("studio", instructions="Media studio tools. Always estimate before you queue.")

@mcp.tool()
def probe_media(path: str) -> dict:
    """Technical facts of a media file: duration, size, fps, codecs, color tags."""
    return mediakit.probe(safe(path))

@mcp.resource("studio://budget")
def budget() -> str:
    return json.dumps(budget_status())

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

The SDK builds the input schema from the type hints and the description from the docstring. Older tutorials use `from mcp.server.fastmcp import FastMCP` (SDK 1.x). In SDK 2.x this import fails. Pin the SDK version in your requirements, and read the migration guide when you upgrade.

### Testing
1. **Protocol tests in CI:** start the server as a subprocess, connect with an MCP client over stdio, list the tools, call each tool with good and bad inputs, read the resources. Assert the results.
2. **Adversarial tests:** paths outside the root, costs above the caps, prompts above the length limit, the same key twice. The server must refuse each one, and log it.
3. **Interactive:** the MCP Inspector lists tools and lets you call them by hand.
4. **Agent tests:** give a real agent 5 tasks. Compare the audit log with what you expected it to do.

When the agent chooses a wrong tool or wrong arguments, the first fix is usually the tool description, not the agent's prompt. Descriptions are read on every call, by every client.

## Tool walkthrough

### The starter studio server
`starter/pipeline/studio_mcp.py` publishes 6 tools and 1 resource: `probe_media`, `qc_check`, `contact_sheet`, `estimate_generation`, `queue_generation`, `job_status`, and `studio://budget`. It uses `mediakit.py` (M02), `genqueue.py` (M01), and `spec_check.py` (C09·M04).

```bash
pip install "mcp>=2.3" pytest
cd starter/pipeline
pytest -q test_studio_mcp.py                      # protocol tests over stdio
STUDIO_ROOT=~/ai-video-lab python studio_mcp.py   # run it for an MCP client
```

### Connect it to an MCP client
Most MCP clients take a server definition with a command and environment variables, for example:

```json
{"mcpServers": {"studio": {"command": "python", "args": ["/path/to/starter/pipeline/studio_mcp.py"],
  "env": {"STUDIO_ROOT": "/path/to/ai-video-lab", "STUDIO_BACKEND": "comfy", "CONFIRM_ABOVE_USD": "2.0", "SHOT_CAP_USD": "3.0"}}}}
```

Check your client's documentation for the file location and the format.

### A protocol test (from the starter tests)

```python
from mcp import Client, StdioServerParameters
params = StdioServerParameters(command=sys.executable, args=["studio_mcp.py"], env=env)
async with Client(params) as c:
    tools = await c.list_tools()
    r = await c.call_tool("probe_media", {"path": "../../etc/passwd"})
    print(json.loads(r.content[0].text))   # {"error": "path '../../etc/passwd' is outside the project root; refused"}
    # r.structured_content is None here: the tools return a plain dict, with no output schema.
```

## Worked example

**Protocol tests of the starter server** (2026-10-04, MCP Python SDK 2.3.0, `pytest -q test_studio_mcp.py`: 6 passed in 3.0 s):

| Test | Steps | Result |
|---|---|---|
| tools listed | list_tools | the 6 expected tool names |
| sandbox | probe `../../etc/passwd` and `/etc/passwd` | both refused: "outside the project root" |
| QC | qc_check on a 640 × 360 clip with the web spec | pass false; failure "width" with its fix |
| dry run → real → repeat → approval | 6 s at US$0.10/s, approval limit US$1.00 | dry run with estimate US$0.60; queued; same key → "existing job"; a 12 s job (US$1.20) → needs_confirmation |
| shot cap | four 9 s jobs (US$0.90 each) with approval files, cap US$3.00 | 3 queued, the 4th refused with "cap US$3.00" |
| audit log | a good and a refused call | two lines, the second with the error |

The first version of this module used the SDK 1.x API (`FastMCP`). During the build, `pip install mcp` gave version 2.3.0, and the old import failed. The protocol tests caught it at once. That is why they run in CI.

**An agent session** (an MCP client with the studio server and an NLE server, C08·M03):
Task: "Make a 15 s cut-down of the café scene from the approved selects; generate one missing insert of the cup; QC it."
Audit log: `job_status(S03-INS2.p1.g1)` → no job; `estimate_generation(S03-INS2.p1.g1, 3)` → US$0.30; `queue_generation(..., confirm=false)` → dry run; the agent asked the user, who agreed; `queue_generation(..., confirm=true)` → queued; `job_status` → succeeded; (cut-down on the NLE server); `qc_check(cutdown.mp4, reels_9x16)` → FAIL loudness −12.8 LUFS with the fix; the agent reported it and stopped, as the recipe says (C08·M03).

## Lab

**Deliverable:** `pipelines/studio_mcp/` with your server (or the starter server extended), protocol tests, adversarial tests, an agent session, and the audit log.

1. Run the starter server and its tests. Read the code.
2. Add 2 tools for your pipeline, for example `make_proxy` and `assemble_from_selects` (from M02). Write their descriptions for an agent: when to use, what it returns, limits.
3. Write protocol tests for the new tools, with good inputs and bad inputs.
4. Write 4 adversarial tests: a path outside the root, a cost above the cap, a too-long prompt, and a repeated key. Each must be refused and logged.
5. Connect the server to an agent. Give it 5 tasks. Compare its audit log with your expectations. Fix tool descriptions where the agent chose a wrong tool or wrong arguments.
6. Pin the SDK version in `requirements.txt`, and run the tests in CI.

**Result checklist**
- [ ] 2 new tools with agent-quality descriptions and protocol tests.
- [ ] 4 adversarial tests that pass (refused and logged).
- [ ] Agent session: 5 tasks and the audit log, with 1 or more description fixes explained.
- [ ] Pinned SDK and CI.

## Model answer

**Description fix (shape of a strong answer):** "In task 3 the agent called `assemble_from_selects` with a folder of all takes, not the selects. The old description said 'Assemble clips.' The new one says: 'Assemble the SELECTED takes of one scene in shot order from selects.csv (the output of takes.py selects). Do not pass a folder of takes. Returns the assembly path and its duration.' On the rerun the agent passed the CSV."

**Adversarial results:**

| Request | Server answer | Logged |
|---|---|---|
| `probe_media("~/.ssh/id_rsa")` | refused: outside the project root | yes |
| `queue_generation(S12.p1.g9, seconds=12, confirm=true)` with US$2.80 already spent, cap US$3.00 | refused: shot would reach US$4.00 | yes |
| prompt of 4,000 characters | error: prompt longer than 1500 characters | yes |
| same key twice | "existing job (idempotent submit)" | yes |

`requirements.txt` pins `mcp==2.3.0`. CI runs `pytest -q` on every push: 6 protocol tests and 4 adversarial tests.
