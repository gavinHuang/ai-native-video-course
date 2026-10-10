---
code: C12
title: Orchestration and Agents
level: 4
hours: 60
prereq: C03, C11
outcomes:
  - Call model APIs reliably with async jobs, queues, retries, and webhooks.
  - Use ffmpeg and Whisper as programmable pipeline stages.
  - Build your own MCP server for a media tool.
  - Design a multi-agent production system with human gates.
  - Add automated quality gates to every stage.
---
## About this course

This course turns your tools into a production system. You build services that call many models, a media-tool MCP server, and a multi-agent studio with clear human approvals and automatic checks.

**Starter code for this course** (in `pipeline/` of the [starter kit](starter.zip); all tested on 2026-10-04):

| File | Use | Tests |
|---|---|---|
| `genqueue.py` | Job queue: idempotency keys, backoff with jitter, Retry-After, timeouts, dead letters, budget caps (M01) | `test_genqueue.py`: 8 passed |
| `mediakit.py` | Media functions: probe, intermediate, proxy, frame-accurate trim, concat with conform, loudness, contact sheet (M02) | `test_mediakit.py`: 6 passed |
| `studio_mcp.py` | MCP server (Python SDK 2.x) with a path sandbox, dry runs, approvals, budget guard, audit log (M03) | `test_studio_mcp.py`: 6 passed over stdio |
| `qc_gate.py` | Stage gates with PASS / FIX / REJECT and reasons (M04) | checked on 4 test clips |

Python packages: `pip install "mcp>=2.3" pytest numpy opencv-python`. The MCP SDK 2.x renamed `FastMCP` to `MCPServer`; tutorials that import `mcp.server.fastmcp` are for SDK 1.x.
