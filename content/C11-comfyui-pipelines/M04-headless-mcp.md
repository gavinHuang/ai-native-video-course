---
title: Headless ComfyUI - API, MCP, and versioning
hours: 16
outcomes:
  - Run API-format workflows through the HTTP and WebSocket API, with uploads, progress, errors, and downloads.
  - Set workflow inputs by name through a map file, and validate a workflow before you queue it.
  - Write automated tests for a ComfyUI client that run on a CPU-only server.
  - Connect an agent to ComfyUI through an MCP server, with limits on what the agent can run.
  - Pin and log the versions that make a run reproducible, and reproduce an earlier output from the log.
keywords: [headless, API format, WebSocket, Comfy MCP, reproducibility]
summary: >
  ComfyUI runs as an HTTP server. You send an API-format workflow to POST /prompt and get a prompt_id. The
  WebSocket sends progress, errors, and a final message. GET /history gives the output file names, and GET /view
  downloads them. Keep a map file from input names to node inputs, so code never depends on node IDs. Validate the
  workflow first. Test the client on a CPU server with a workflow that needs no models. Agents use ComfyUI through
  MCP servers; give them packaged workflows with strict inputs. Log the workflow hash, model hashes, node versions,
  ComfyUI version, seed, and GPU for each run.
diagram:
  type: flow
  title: One headless job
  nodes: ["Load API workflow + map file", "Upload inputs: POST /upload/image", "Set inputs by name; validate", "POST /prompt → prompt_id", "WebSocket: progress · error · done", "GET /history → /view → download + log"]
  highlight: [4]
watch:
  - title: "ComfyUI docs — server routes and WebSocket messages"
    url: https://docs.comfy.org/development/comfyui-server/comms_routes
    note: "Read /prompt, /history, /view, /upload/image, and the message types."
  - title: "ComfyUI — example API scripts (script_examples)"
    url: https://github.com/comfyanonymous/ComfyUI/tree/master/script_examples
    note: "Compare websockets_api_example.py with the starter client."
  - title: "GIGAZINE on X — Comfy MCP lets agents like Claude Code automate ComfyUI (Japanese)"
    url: https://x.com/gigazine/status/2071792169153605764
    note: "Short news. Note that Comfy MCP uses Comfy Cloud."
quiz:
  - q: "POST /prompt returns HTTP 400 with 'value_not_in_list' for a LoadImage node. What happened, and what is the fix?"
    options: ["The GPU is full; wait", "The image name is not in the server input folder; upload the file with /upload/image first and use the returned name", "The prompt is too long", "The workflow is in UI format"]
    answer: 1
    explain: "The server validates file names against its folders before it queues the job. Upload first. The response gives the name (and subfolder) to use."
  - q: "Your client waits for the 'executing' message with node null. Which extra condition prevents a wrong 'done'?"
    options: ["None is needed", "Check that the message's prompt_id is your prompt_id, because other jobs on the same server send the same message type", "Check the GPU temperature", "Wait 5 more seconds"]
    answer: 1
    explain: "A server can run jobs from several clients. Filter every message by prompt_id. Also handle execution_error and execution_interrupted, and set a total timeout."
  - q: "A 2-minute control video upload fails with HTTP 413. What do you change?"
    options: ["Split the video into images", "Raise the server limit with --max-upload-size (default 100 MB), or put large inputs on shared storage that the server can read", "Use the UI instead", "Compress it to 1 MB"]
    answer: 1
    explain: "The upload endpoint has a size limit. For large media, a shared volume is often better than HTTP uploads."
  - q: "Why does the starter client refuse to set an input that is a link in the workflow?"
    options: ["Links are read-only on the server", "Writing a value over a link breaks the graph silently: the node no longer gets the upstream output", "It is a bug", "Links cannot be saved in JSON"]
    answer: 1
    explain: "A map entry must point to a widget value. If it points to a link, the map is wrong for this workflow version. Fail loudly."
  - q: "How can CI test your ComfyUI client without a GPU and without model files?"
    options: ["It cannot", "Start ComfyUI with --cpu and run a small workflow of core nodes that needs no models, for example LoadImage → ImageInvert → SaveImage", "Mock the whole server", "Run the real video workflow on CPU"]
    answer: 1
    explain: "The server, the validation, the WebSocket, the history, and the downloads are the same on CPU. Only the model nodes need a GPU. Test those in a separate, scheduled GPU job."
  - q: "You give an agent an MCP tool that accepts any API-format workflow JSON. What is the risk, and what is better?"
    options: ["No risk", "The agent can run any node with any input, for example huge sizes or file paths; expose packaged workflows as tools with typed, limited inputs instead", "The agent will be slow", "MCP does not support JSON"]
    answer: 1
    explain: "An agent tool is an API. Design it with the least power that does the job: a named workflow, a few inputs with ranges, a budget, and a log."
  - q: "You rerun a logged job with the same workflow, seed, and models, and the output differs slightly. What is the most likely cause, and what do you do?"
    options: ["The log is wrong", "Non-deterministic GPU kernels or a different GPU or driver; compare versions in the log, and use --deterministic if you need exact repeats", "The seed is random", "The cache"]
    answer: 1
    explain: "Same versions and same seed give near-identical output. Exact repeats can need deterministic kernels, which are slower. Record the GPU, driver, and PyTorch version for this reason."
deeper:
  - title: "ComfyUI — command-line options (cli_args.py)"
    url: https://github.com/comfyanonymous/ComfyUI/blob/master/comfy/cli_args.py
  - title: "Model Context Protocol — specification"
    url: https://modelcontextprotocol.io/specification
  - title: "Machine Delusions on X — local MCP server for ComfyUI"
    url: https://x.com/Machinedelusion/status/2072148272710660326
---
## Learn

### ComfyUI as a service
The editor in the browser is one client of the ComfyUI server. Your code can be another client. Then ComfyUI becomes a generation service: your pipeline sends jobs, follows them, and collects files. This is the base for agents (C12), serving (C13), and scale (C15).

### The routes that a client needs
| Route | Use |
|---|---|
| `POST /upload/image` | Upload an input file (images, and also audio and video files). Returns `name` and `subfolder`. |
| `POST /prompt` | Queue a job: `{"prompt": <api workflow>, "client_id": <uuid>}`. Returns `prompt_id`, or HTTP 400 with `node_errors`. |
| `GET /ws?clientId=<uuid>` | WebSocket with progress and status messages for your client ID. |
| `GET /history/<prompt_id>` | Status and output file names of a finished job. |
| `GET /view?filename=..&subfolder=..&type=output` | Download one output file. |
| `GET /system_stats` | ComfyUI version, PyTorch version, devices, VRAM. Put these in the run log. |
| `GET /object_info` | All node classes and their inputs. The validator uses it. |
| `POST /interrupt`, `POST /queue` | Stop the running job; clear the queue. |

### The WebSocket messages
Filter every message by your `prompt_id`. Other clients can use the same server.
- `execution_start`: the job started.
- `execution_cached`: these nodes come from the cache.
- `executing` with a node ID: this node runs now.
- `progress`: step `value` of `max` for the running sampler.
- `executing` with `node: null`: the job is done.
- `execution_error`: a node failed. The message has the node ID, the class, and the exception text.
- `execution_interrupted`: someone stopped the job.
Binary messages are preview images. Skip them unless you show previews.

### Set inputs by name
Do not edit workflow JSON with string replace. Load it as JSON, copy it, and set values. Keep a **map file** for each workflow:

```json
{"prompt": "6.text", "start_image": "56.image", "seed": "3.seed", "frames": "55.length"}
```

Your code and your agents use the names on the left. When the workflow changes and node IDs move, you change only the map. Every starter workflow has a map file. Three rules:
1. Never change the template file. Change a copy.
2. If a map entry points to a link, not a value, stop with an error. The map does not fit this workflow version.
3. Validate before you queue. `validate_workflow.py` checks classes, required inputs, link types, and file names against the server.

### Errors that you must handle
| Where | Example | Client action |
|---|---|---|
| Before the job | Unknown input name, missing local file | Exit with a clear message (exit code 2) |
| `POST /prompt` | HTTP 400: value not in list, missing input, wrong type | Show `node_errors`; exit 3 |
| During the job | `execution_error`: out of memory, missing model, bad file | Show node and message; exit 4 |
| No end | A node hangs, the server crashes | Total timeout; exit 5 |
| Upload | HTTP 413: file too large (default limit 100 MB) | Raise `--max-upload-size` or use shared storage |

Clear exit codes let a pipeline decide what to do: fix the input, retry, or call a person.

### Test the client without a GPU
Most client code does not need a GPU. The server, validation, WebSocket, history, and downloads behave the same on CPU. So:
- Start ComfyUI with `--cpu` in CI.
- Use a workflow of core nodes that needs no models. The starter kit has `test/00_smoke_cpu.json`: LoadImage → ImageInvert → SaveImage.
- Test the success path, the log fields, that the template file does not change, and each error path.
- Test the real model workflows in a separate GPU job, for example once a night.

### Agents and MCP
An agent can drive ComfyUI through an MCP server (C03·M05). Options as of 2026-10:
- **Comfy MCP** (official, public beta): agents search and run workflows on Comfy Cloud.
- **Community MCP servers** for a local ComfyUI: inspect graphs, queue jobs, manage models.
- **Your own MCP server** (C12·M03): wrap your packaged workflows as tools.

Design agent tools with the least power that does the job. A tool `generate_shot(shot_id, prompt, seed, duration_s)` with ranges and a budget is safe to give an agent. A tool `run_any_workflow(json)` gives the agent every node, every size, and every file path on the server. Log every tool call with its inputs and cost.

### Reproducibility
To reproduce an output you need the same inputs and the same versions:
- workflow file hash (SHA-256 of the API JSON that you sent);
- model file hashes (`models.lock.json`);
- custom node commits (if any);
- ComfyUI version and commit;
- seed and all input values;
- GPU, driver, and PyTorch version.

With all of these the same, output is the same or nearly the same. Small differences can come from GPU kernels that are not deterministic. If you need exact repeats, start ComfyUI with `--deterministic`. It is slower, and the ComfyUI help says that it does not guarantee exact repeats in all cases.

## Worked example

**A real run log line.** We ran the smoke workflow with the starter client against a ComfyUI 0.38.0 server on CPU (2026-10-04):

```bash
python comfy_run.py --server http://127.0.0.1:8199 \
  --workflow workflows/test/00_smoke_cpu.json --map workflows/test/00_smoke_cpu.map.json \
  --upload image=smoke_in.png --out renders --log runs.jsonl
```

```json
{"prompt_id": "2fa08d93-108b-4355-95f2-74607e199c06",
 "workflow_sha256": "e4a9ee2aa5b380095f5abf8f31be4a904a8b7507b7783fbf499a70d5e1ff5138",
 "inputs": {"image": "smoke_in.png"}, "seconds": 0.1,
 "outputs": ["renders/smoke_00001_.png"],
 "comfyui_version": "0.38.0", "pytorch_version": "2.14.1", "devices": ["cpu"]}
```

**The error paths, on the same server:**

| Test | Client output | Exit code |
|---|---|---|
| `--set promt=x` (typo) | `unknown input 'promt'. Known: filename_prefix, image` | 2 |
| `--set image=does_not_exist.png` | HTTP 400 from /prompt with `node_errors` | 3 |
| Wan 5B workflow with an empty model file | `execution error in node 39 (VAELoader): Error while deserializing header` | 4 |

The test file `test_comfy_run.py` checks these cases. Result on the CPU server: 5 passed in 0.31 s.

## Lab

**Deliverable:** `pipelines/comfy_client/` with a CLI client, tests, an agent demo, and a reproduction report.

1. **Client.** Write `comfy_run.py --workflow X --map X.map.json --set name=value --upload name=file`. It must upload files, follow the WebSocket, handle the 5 error cases in the table, download outputs, and append a log line.
2. **Validation.** Call the validator (or your own checks) before you queue.
3. **Tests.** Start ComfyUI with `--cpu`. Write tests with the smoke workflow: success, log fields, template unchanged, and each error path. Run them in CI (for example a GitHub Actions job).
4. **Real runs.** Run 2 starter workflows on your GPU server through the client. Use the same log format.
5. **Agent.** Connect an agent to ComfyUI through an MCP server. Expose one packaged workflow (for example `generate_shot`) with limited inputs. Ask the agent in natural language to make one shot. Save the transcript and the tool-call log.
6. **Reproduce.** Pick one earlier GPU run from the log. Rerun it from the log only. Compare the two outputs (pixel difference or identity score). Write the result.

Try the lab yourself first. Then compare with `starter/solutions/C11-M04/`.

**Result checklist**
- [ ] The client handles all 5 error cases with clear exit codes.
- [ ] Tests pass on a CPU server in CI.
- [ ] 2 GPU workflows ran through the client, with complete log lines.
- [ ] Agent demo: transcript and tool-call log, with limited inputs.
- [ ] Reproduction report with the measured difference.

## Model answer

A strong submission has this shape:

```
pipelines/comfy_client/
  comfy_run.py            # about 250 lines; no dependency except websocket-client (optional)
  test_comfy_run.py       # 5+ tests on a CPU server
  .github/workflows/ci.yml   # starts ComfyUI --cpu, runs pytest
  mcp/generate_shot.py    # MCP tool: shot_id, prompt (≤ 600 chars), seed, duration_s (2–8)
  agent_demo.md           # transcript + tool-call log
  REPRODUCE.md
```

`REPRODUCE.md` (example):

"Run `9c1e…` (03_i2v_wan22_5b, seed 1001, 640 × 352) was rerun from its log on the same RTX 5090, same driver, ComfyUI 0.38.0. Mean absolute pixel difference: 0.4 / 255. Identity score of both: 0.612 and 0.611. Visually identical. Without `--deterministic`, small differences come from GPU attention kernels. With `--deterministic`, the difference was 0 and the run took 18 % longer. We keep the default and record the GPU in each log."

What makes this submission strong:
1. **Clear exit codes.** A pipeline that calls the client can tell "fix your input" (2) from "the server rejected the graph" (3), "a node failed" (4), and "no answer" (5). Each needs a different action.
2. **The tests run without a GPU.** CI starts ComfyUI with `--cpu` in about 20 s and runs the smoke workflow. GPU tests run once a night.
3. **The agent tool is narrow.** The MCP tool accepts a shot ID, a prompt with a length limit, a seed, and a duration from 2 to 8 s. It rejects other values before it calls ComfyUI. Every call is logged with its cost.
4. **The reproduction is measured.** The report gives a number (pixel difference and identity score), not "it looks the same", and it explains the cause of the difference.

The reference client and tests are in `starter/solutions/C11-M04/`. Compare your error handling with it, line by line.
