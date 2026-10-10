---
title: The Model Context Protocol (MCP)
hours: 9
outcomes:
  - Explain the MCP architecture - hosts, clients, servers, tools, resources, prompts.
  - Connect an MCP client to local and remote MCP servers.
  - Use creative-tool MCP servers (editors, ComfyUI, generators) safely.
  - Inspect and debug an MCP server.
keywords: [MCP, MCP server, MCP client, tool call, resource]
summary: >
  The Model Context Protocol is an open standard that connects AI applications to tools and data. An MCP server
  exposes tools, resources, and prompts. An MCP client inside a host application, such as Claude Desktop or Claude
  Code, connects to servers and gives their tools to the model. In 2026 many creative tools have MCP servers:
  DaVinci Resolve Studio 21.1 has one built in, Adobe Premiere publishes one, and ComfyUI has Comfy MCP. One agent
  can now plan, generate, and edit across tools. Use permissions and review for every action.
diagram:
  type: flow
  title: MCP in a media studio
  nodes: ["Host app (Claude Desktop / Claude Code / other)", "MCP client", "MCP server: NLE (Resolve / Premiere)", "MCP server: ComfyUI / generators", "MCP server: files, storage, review", "Human reviews + approves"]
  highlight: [1]
watch:
  - title: "Model Context Protocol — Introduction (official docs)"
    url: https://modelcontextprotocol.io/introduction
    note: "Read the introduction and the architecture page."
  - title: "Y.M.Cinema — DaVinci Resolve 21.1 uses MCP to let AI assistants control the edit"
    url: https://ymcinema.com/2026/09/17/davinci-resolve-21-1-mcp-ai-assistants-control-edit/
    note: "Read the list of actions that the assistant can do."
  - title: "ComfyUI on X — Comfy MCP public beta"
    url: https://x.com/ComfyUI/status/2071625866912944151
    note: "Note: run workflows in natural language; search models, nodes, templates."
quiz:
  - q: "In MCP, who exposes the tools?"
    options: ["The host app", "The MCP server", "The LLM vendor", "The user"]
    answer: 1
    explain: "Servers expose tools, resources, and prompts. Clients connect to them."
  - q: "Your tool raises an exception for a missing file. What does the model see (Python SDK 2.3)?"
    options: ["The full error message", "Only a generic 'Error executing tool' message, so it cannot correct itself; return the error as a result with a clear message and a suggestion", "Nothing at all", "The stack trace"]
    answer: 1
    explain: "Measured in the course test. Errors are information for the agent: return them as results."
  - q: "Main risk of connecting an agent to your NLE?"
    options: ["Slow renders", "Unwanted changes to a real project", "Wrong fonts", "Higher electricity cost"]
    answer: 1
    explain: "Work on a duplicate project, and review each change."
  - q: "What is an MCP 'resource'?"
    options: ["A GPU", "Read-only data the server exposes to the client, for example a timeline description", "A payment method", "A model weight file"]
    answer: 1
    explain: "Tools act; resources provide data; prompts provide templates."
  - q: "You want to connect a remote MCP server from a vendor to an agent that edits a client's unreleased film. What do you check first?"
    options: ["The server's speed", "The project data rule: may the client's media go to this operator? Then authentication, the tools it exposes, and the vendor's data terms", "The number of tools", "Nothing; MCP is safe"]
    answer: 1
    explain: "A remote server receives the data that its tools process."
  - q: "Which design rule belongs in every MCP server that can write files?"
    options: ["Let the model choose any path", "A path sandbox enforced in the server, no delete tools by default, confirmation for costly actions, and an audit log", "Long, detailed results", "One tool that does everything"]
    answer: 1
    explain: "The server, not the prompt, enforces the limits."
deeper:
  - title: "MCP specification"
    url: https://modelcontextprotocol.io/specification
  - title: "MCP Inspector (debug tool)"
    url: https://github.com/modelcontextprotocol/inspector
  - title: "Jumper — agentic video editing with MCP (Premiere, Resolve, Final Cut, Avid)"
    url: https://getjumper.io/ai-agents
---
## Learn

### Why MCP
Before MCP, each AI app needed a custom integration for each tool. MCP is one open protocol (introduced by Anthropic in 2024, now widely adopted). Any MCP client can use any MCP server. In video this matters a lot: one agent can plan with an LLM, run generation workflows in a node-graph tool, and edit in an NLE, through one protocol.

### Architecture
- **Host:** the application you use: a desktop chat app, a coding agent, an IDE, or your own program.
- **Client:** the part of the host that connects to one server.
- **Server:** a program that exposes:
  - **tools** (actions: `render_timeline`, `run_workflow`),
  - **resources** (data: a timeline description, a bin list),
  - **prompts** (templates).
- **Transport:** local (stdio, the server runs on your machine) or remote (HTTP).

### MCP in creative tools
By 2026, MCP reached the main creative tools. Editing applications have native MCP servers (organize timelines, markers, grades, renders, delivery checks). Node-graph generation tools have official and community servers (run workflows, search models and nodes). Bridges connect one agent to several NLEs, and generation vendors offer their own servers. The dated list is in the Tool walkthrough. The pattern is the same everywhere: read tools first, then a few write tools, then renders and paid generation behind confirmation.

### Designing a server
When you write your own server (C12·M03):
- **One job per tool**, with a name and a description that say when to use it.
- **Short, structured results** with IDs that the agent can pass to the next tool.
- **Return errors as results** with a clear message and, if possible, a suggestion ("file not found; similar: C014A.mp4"). In the Python SDK used in this course (2.3), an exception in a tool reaches the model only as a generic "Error executing tool" message, so the model cannot correct itself.
- **Enforce limits in the server:** path sandbox, budgets, confirmation flags. Never rely on the model to respect them.
- **Audit log:** every call with its arguments and a result summary.

### Local and remote servers
A **local** server (stdio) runs on your machine with your permissions: fast, private, and dangerous if it is not trusted. A **remote** server (HTTP) runs elsewhere and needs authentication (usually OAuth). Remote servers send your data to their operator: apply the project data rule (C13·M05) before you connect one to client media.

### Safety rules
1. Work on a **copy** of the project.
2. Start with read-only tools. Add write tools one by one.
3. Ask for a plan before actions.
4. Review every change (markers, a change log, or a diff of the timeline export).
5. Only install servers from sources you trust. A server runs code on your machine.

### Debugging
Use the **MCP Inspector** to list a server's tools, call them by hand, and see the raw messages.

## Tool walkthrough

### Creative tools with MCP (as of 2026-10)
| Tool | MCP status |
|---|---|
| DaVinci Resolve Studio 21.1 | Native MCP server: organize timelines, rename clips, grades and LUTs, markers, multi-format renders, delivery-spec checks. |
| Adobe Premiere 26.x | Firefly AI Assistant inside; an MCP server for external clients is reported. |
| ComfyUI | Comfy MCP (public beta, uses Comfy Cloud) and community local servers: run workflows, search models and nodes. |
| Bridges | Jumper (Premiere, Resolve, Final Cut, Avid), EditAssist. |
| Generators | Higgsfield MCP (multi-model studio); many API vendors offer MCP servers. |

### A minimal server (tested)
`starter/solutions/C03-M05/media_mcp.py` is a read-only server with two tools (`list_media`, `probe`) and one resource (`media://summary`), in about 70 lines:

```python
from mcp.server.mcpserver import MCPServer
mcp = MCPServer("media-files", instructions="Read-only access to the media folder.")

@mcp.tool()
def probe(path: str) -> dict:
    """Return duration (s), resolution, frame rate, and codecs of one media file (relative path)."""
    ...

if __name__ == "__main__":
    mcp.run()        # stdio
```

```bash
pip install "mcp>=2.3" pytest
python -m pytest -q starter/solutions/C03-M05/test_media_mcp.py   # a real MCP client starts the server over stdio
claude mcp add media-files -e MEDIA_ROOT=$HOME/work -- python starter/solutions/C03-M05/media_mcp.py
npx @modelcontextprotocol/inspector python starter/solutions/C03-M05/media_mcp.py   # call tools by hand
```
The test checks the tool list, a probe, a missing file (the result suggests a similar name), and a path outside the root (refused as a result, not as an exception).

## Worked example

**Connect a local server in a JSON-config host (shape used by Claude Desktop and similar clients):**
```json
{
  "mcpServers": {
    "media-files": {
      "command": "python",
      "args": ["-m", "media_mcp_server", "--root", "/Users/me/work"]
    }
  }
}
```
In Claude Code, the same can be added with the `claude mcp add` command. After restart, the host lists the server's tools.

**A Resolve session (Studio 21.1, on a duplicate project):**
1. "List the timelines and the number of clips in each." (read only)
2. "Add a red marker on every clip shorter than 12 frames on timeline 'Edit v3'." (write, low risk)
3. "Render 'Edit v3' as 16:9 H.264 and 9:16 H.264 with the YouTube preset; check against our delivery spec." (render)
4. You review markers, renders, and the spec report. You approve or undo.

## Lab

**Deliverable:** `C03/M05/` notes, configs, and a 2-minute screen recording of a working session.

1. Install an MCP-capable host.
2. Connect 2 servers: a file-system server (official reference server) and one creative server (Resolve Studio, Premiere, Comfy MCP, or a community ComfyUI server).
3. Use the MCP Inspector to list and call one tool by hand.
4. Run a 5-step task through the agent: read → plan → one write action → render or generate → report.
5. Write a safety note: which tools you allowed, which you blocked, and why.

**Result checklist**
- [ ] Two servers connected; tool list captured.
- [ ] Inspector call recorded.
- [ ] 5-step task done on a copy, with a review of each change.
- [ ] Safety note.

## Model answer

A good submission shows the config files, a screenshot of the tool list, an Inspector call with its JSON response, and a recording where the agent first proposes a plan, then acts after approval. The safety note blocks delete and overwrite tools, limits the file server to one work folder, and requires confirmation for renders and paid generations.

It also records one failure and what it taught: for example, "the agent called `probe` with an absolute path; the server refused it, returned the reason, and the agent retried with the relative path". A strong submission shows that the limits are enforced by the servers, and it states which servers are local and which are remote, with the data that each one receives.
