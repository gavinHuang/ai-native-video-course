---
title: Serving open models - containers, cold starts, autoscaling
hours: 14
outcomes:
  - Package an open video model or a ComfyUI workflow as a container service with pinned versions and a health check.
  - Break a cold start into its parts, and reduce each one (image, weights, warm-up).
  - Autoscale on queue depth and the age of the oldest job, with a budget limit, and scale to zero.
  - Monitor queue time, load time, run time, VRAM, errors, and cost per output second.
  - Secure the service - authentication, no open UI ports, secrets, isolated custom code.
keywords: [container, cold start, autoscaling, scale to zero, observability]
summary: >
  A model service is a container with pinned versions, the model weights, and a small API in front. A cold start is
  the sum of starting the container, starting the runtime, loading the weights, and the first slow run; measure each
  part. Reduce them with weights in the image or on a volume in the same region, smaller weight formats, and a warm
  pool when people wait. Scale on queue depth and the oldest job's age, with a maximum set by the budget, and scale
  to zero when idle. Monitor each job's timings and cost, and secure the service like any API.
diagram:
  type: flow
  title: Parts of a cold start
  nodes: ["Schedule a GPU + pull the image", "Start the runtime (Python, server)", "Load the weights (bytes / read speed)", "First run: warm-up, kernel compilation", "Warm: next jobs skip all of this", "Idle N min → scale to zero"]
  highlight: [2]
watch:
  - title: "Modal — examples (ComfyUI and diffusion as a service)"
    url: https://modal.com/docs/examples
    note: "Find a ComfyUI or video-model example; note how the weights are cached."
  - title: "RunPod — Serverless documentation"
    url: https://docs.runpod.io/serverless/overview
    note: "Read about workers, cold starts, and network volumes."
quiz:
  - q: "A cold start takes 150 s. The container starts in 10 s, the server in 5 s, and the first run is 20 s slower than later runs. Where are the other 115 s, and what is the fix?"
    options: ["In the GPU", "Most likely in loading the weights from a slow volume (45 GB at about 0.3 GB/s); bake them into the image, use a faster volume in the same region, or use smaller weights", "In the network to the client", "In the prompt"]
    answer: 1
    explain: "Load time = bytes / read speed (C13·M01). Measure each part before you optimize."
  - q: "When do you keep a warm pool of at least 1 worker?"
    options: ["Always", "When people wait for results (studio hours, live sessions); for overnight batches, scale to zero", "Never", "Only for training"]
    answer: 1
    explain: "A warm worker costs money every hour; a cold start costs a person's time. Choose per time of day."
  - q: "On which signal do you autoscale a generation service?"
    options: ["CPU usage", "Queue depth and the age of the oldest job, with a maximum number of workers from the budget and the quota", "Disk space", "Time of day only"]
    answer: 1
    explain: "GPU jobs are long. Queue depth and waiting time tell you if users wait too long."
  - q: "Why batch similar jobs on one worker?"
    options: ["It is required", "The model stays loaded, so only the first job pays the load time; switching models on a worker reloads tens of GB", "It is cheaper per GPU hour", "To avoid logs"]
    answer: 1
    explain: "Route jobs of the same workflow to the same workers."
  - q: "Your ComfyUI server is reachable on a public IP, port 8188, without authentication. What is the risk?"
    options: ["None", "Anybody can run workflows on your GPU, read your output folder, and load custom nodes that run code; put the service behind an authenticated API and a private network", "Only slower jobs", "Only extra logs"]
    answer: 1
    explain: "A generation server is a powerful remote-execution service. Treat it like one."
  - q: "Which per-job fields does the dashboard need?"
    options: ["Only success", "Queue time, load time, run time, peak VRAM, output seconds, result (success or error type), and cost", "Only the prompt", "Only the GPU name"]
    answer: 1
    explain: "With these you can find the slow part, the expensive part, and the failing part."
  - q: "Why pin the versions of the server, the custom nodes, and the weights in the image?"
    options: ["For speed", "So that every worker gives the same results, and a scaled-out worker does not pull a newer version that breaks the workflow", "It is free", "Platforms require it"]
    answer: 1
    explain: "Autoscaling starts new workers at any time. They must be identical (C11·M04)."
deeper:
  - title: "NVIDIA Triton Inference Server — docs"
    url: https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/
  - title: "Hugging Face Diffusers — memory and speed optimization"
    url: https://huggingface.co/docs/diffusers/optimization/memory
  - title: "OWASP — API Security Top 10"
    url: https://owasp.org/API-Security/
---
## Learn

### Two shapes of a model service
1. **A node-graph server as a service:** the graph server, your API-format workflows (C11), and a thin API in front that accepts named inputs, runs the workflow, and returns a file URL.
2. **A direct model server:** the model's reference code or a library pipeline behind a small HTTP API or a serverless handler.
Both need: pinned versions (server, custom code, weights, drivers), a health check, structured logs, and outputs written to object storage, not to the container's disk.

### The parts of a cold start
A cold start is everything that happens before the first useful run on a new worker:
1. **Schedule a GPU and pull the image.** Large images take longer, unless the platform caches them.
2. **Start the runtime:** Python imports and the server. In our test, the graph server of the starter kit started in 5.2 s on CPU without models.
3. **Load the weights:** bytes / read speed (C13·M01). 45 GB from a typical network volume takes about 150 s; from a local NVMe drive about 7 s.
4. **First run:** kernel compilation and warm-up make the first run slower than the next ones.
Measure each part (log a timestamp at each stage). Then reduce the largest part.

### Reduce cold starts
- **Weights in the image:** a large image, but no download at start, if the platform caches images near the GPU.
- **Weights on a volume** in the same region (a network volume or a model cache).
- **Smaller weights:** FP8 or 4-bit formats halve or quarter the bytes to load (C01·M06).
- **A warm pool:** keep 1 or more workers warm in studio hours; scale to zero at night.
- **Batching:** route jobs of the same workflow to the same workers, so the model stays loaded.

### Autoscaling
Scale on the signals that users feel:
- **queue depth** (jobs waiting) and **the age of the oldest job** (how long somebody waits);
- a **maximum** number of workers from the budget and the provider's quota;
- **scale to zero** after N minutes without jobs.
A simple rule: workers = min(max_workers, ceil(queued jobs × run time per job / target wait time)).

### Throughput
Faster attention kernels, compiled models, step-distilled variants (4–8 steps), resolution tiers (preview first, final for chosen takes), and, for very large models, splitting work across several GPUs.

### Observability
Log for every job: queue time, load time (0 on a warm worker), run time, peak VRAM, output seconds, the result (success, or the error type), and the cost. Dashboards: p50 and p95 wait time, error rate by type, GPU utilization, and cost per output second.

### Security
- Authentication on the API; rate limits per client.
- No public UI ports of the graph server; keep it on a private network behind your API.
- Secrets in a secret manager, not in the image.
- Custom nodes and model code run with full rights: review, pin, and isolate them (C11·M01).
- Scan images for known vulnerabilities; update base images on a schedule.

## Tool walkthrough

### A container for the graph server
`starter/solutions/C11-M01/Dockerfile` pins the ComfyUI commit and installs PyTorch for CUDA 12.8 (or CPU for tests). Models are mounted, not built in. To bake weights into an image for a serverless platform, add a stage that runs `download_models.py` for one workflow, and check the image size against the platform's limit.

### Log the parts of a start

```python
import time, json
t0 = time.time()
# ... start the server, wait for /system_stats ...
t_server = time.time()
# ... queue a tiny warm-up job of the workflow, wait for it ...
t_warm = time.time()
print(json.dumps({"server_s": round(t_server - t0, 1), "load_and_warmup_s": round(t_warm - t_server, 1)}))
```

### Plan the load time

```bash
python starter/tools/gpu_plan.py 06_i2v_ltx25      # load time of all weights per storage type
```

### Platforms (as of 2026-10)
Serverless GPU platforms (Modal, RunPod Serverless, Replicate deployments) offer image caching, network volumes, warm pools ("min workers"), and scale to zero. Check each platform's image-size limit, volume speed, and cold-start features.

## Worked example

**Cold start plan for workflow 06 (LTX-2.5 I2V, 44.9 GB of weights) on a serverless 80 GB GPU** (a calculation; replace the numbers with your measurements):

| Part | Network volume (about 0.3 GB/s) | Weights in a cached image / local NVMe (about 6 GB/s) |
|---|---|---|
| Schedule + image | 15 s | 25 s (bigger image) |
| Server start | 5 s (measured on CPU: 5.2 s) | 5 s |
| Load weights | 150 s | 7 s |
| First-run warm-up | 20 s | 20 s |
| Total cold start | about 190 s | about 57 s |

A run of this workflow is about 60–120 s. With the volume, a cold start costs more than a run: for interactive work, keep 1 worker warm; for batches, put weights in the image.

**Service "ltx25-i2v":**
- Image: CUDA base + PyTorch + the pinned graph server + workflow 06 + weights (one workflow per image).
- Handler: input {image_url, prompt, seed, duration_s}; output: an MP4 in object storage and a signed URL.
- Scaling: min workers 1 from 09:00 to 19:00, 0 at night; max 6; scale up when the oldest job waits more than 60 s.
- Dashboard: wait time p95, load time (should be 0 on warm workers), run time, errors by type, cost per output second.

## Lab

**Deliverable:** `infra/model-service/` with a container, a deployed service, a cold-start report, a load test, and a dashboard.

1. Package one workflow (or one model) as a container with pinned versions and a health check.
2. Deploy it on a serverless GPU platform (or on a rented GPU with your own small API).
3. Measure a cold start in its parts. Make one change that reduces the largest part, and measure again.
4. Run a load test: 20 jobs in a burst. Record the scaling, the wait times, and the cost.
5. Build a dashboard (or a report from the logs) with the per-job fields.
6. Check the security: no open UI port, authentication on the API, secrets out of the image.

**Result checklist**
- [ ] Container with pinned versions; a deployed endpoint.
- [ ] Cold start in parts, before and after one change.
- [ ] Load-test results (scaling, p95 wait, cost).
- [ ] Dashboard or report; security checklist done.

## Model answer

**Cold start report (shape of a strong answer):**

| Part | Before (volume) | After (weights in image) |
|---|---|---|
| Schedule + image pull | 12 s | 41 s (cached after the first pull: 9 s) |
| Server start | 6 s | 6 s |
| Load weights (18 GB, workflow 03) | 64 s | 4 s |
| First-run warm-up | 18 s | 18 s |
| Total | 100 s | 37 s (warm image cache) |

"Load test: 20 jobs at once, max 4 workers. p95 wait 6 min 20 s, because each worker ran 5 jobs one after another. With max 8 workers: p95 wait 3 min 10 s, the same total cost (the jobs are the same; only the parallel time changes). The cost per output second was US$0.011 at 74 % GPU utilization."

"Security: the graph server listens only on the container's private network; the API needs a token; the outputs are private in object storage with 1-hour signed URLs."
