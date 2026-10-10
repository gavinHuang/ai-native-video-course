---
code: C03
title: LLMs as Creative and Production Engine
level: 1
hours: 50
prereq: C02 recommended
outcomes:
  - Engineer context for an LLM so that its output fits a project.
  - Turn a brief into a treatment, script, shot list, and prompts as validated structured data.
  - Build critique loops where an LLM reviews and improves work against criteria.
  - Explain agents, tool calls, and the Model Context Protocol (MCP).
  - Connect an LLM client to MCP servers and use them for media tasks.
  - Use agentic coding tools to build and run small media tools.
---
## About this course

In an AI-native production, the LLM is the planner, writer, critic, and operator. It turns a brief into structured data that every other tool can read. It also operates tools through MCP. This course teaches you to use LLMs as an engineer: with schemas, validation, tests, and clear responsibility for the human.

**Starter tools for this course** (in the [starter kit](starter.zip); tested on 2026-10-04):

| Tool | Use |
|---|---|
| `solutions/C03-M01/shotlist.py` | Treatment → validated JSON shot list with a validate-and-repair loop; 5 offline tests (M01) |
| `tools/judge_agreement.py` | Raw agreement and Cohen's kappa between an LLM judge and human scores (M03) |
| `examples/judge_scores.csv` | Example scores for the M03 worked example |
| `solutions/C03-M05/media_mcp.py` | A minimal read-only MCP server, tested with a real MCP client over stdio (M05) |
| `pipeline/mediakit.py`, `tools/transcribe.py` | Tested media functions to wrap as agent tools (M04) |
