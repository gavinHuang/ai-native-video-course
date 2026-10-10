---
title: Cloud GPU - rental, serverless, and per-output APIs
hours: 12
outcomes:
  - Compare GPU rental (24/7 and on demand), serverless GPU, per-output model APIs, and hosted apps.
  - Calculate the monthly cost of a workload on each path, per usable second, with measured inputs.
  - Find the break-even volume between owning a GPU and paying per use.
  - Use spot capacity safely, and keep data and models close to the GPU.
keywords: [GPU rental, serverless GPU, per-output API, break-even, spot instance]
summary: >
  There are four ways to pay for generation compute: rent a GPU by the hour (always on, or on demand), run on
  serverless GPUs billed per second, pay a model API per output second, or own the hardware. Each fits a different
  workload. The comparison needs measured inputs - GPU seconds per clip and the usable share - and the result per
  usable second. Always-on rental is expensive unless the GPU is busy; owning wins only at high, steady volume.
  Spot capacity is cheap for jobs that can restart. Keep models and data in the same region as the GPU.
diagram:
  type: layers2d
  title: Four ways to pay for compute
  rows: ["Rental (24/7 or on demand)", "Serverless GPU", "Per-output API", "Own hardware"]
  cols: ["You pay for", "Best for"]
  cells:
    - ["Every hour the GPU is on", "Steady, high use; full control"]
    - ["GPU seconds + cold starts", "Spiky batches; scale to zero"]
    - ["Output seconds; no operations", "Low volume; closed models; no ops team"]
    - ["Purchase + power + your time", "High, steady volume over years"]
watch:
  - title: "Fal.ai vs RunPod — pricing and features compared (2026)"
    url: https://getdeploying.com/fal-ai-vs-runpod
    note: "Note per-hour against per-output pricing."
  - title: "Scale-to-zero serverless GPUs: Modal vs RunPod vs Replicate"
    url: https://www.buildmvpfast.com/blog/scale-to-zero-serverless-gpu-modal-runpod-ai-hosting-2026
    note: "Read the cold-start and pricing trade-offs."
quiz:
  - q: "A workload needs 20 busy GPU hours per month. Why is a 24/7 rental the most expensive choice?"
    options: ["It is not", "You pay for 730 hours to use 20; the GPU is idle 97 % of the time", "Rentals are slow", "Rentals have no GPUs"]
    answer: 1
    explain: "In the module example: about US$2,110 per month for 24/7 against US$75 on demand for the same work."
  - q: "Why compare paths per USABLE second?"
    options: ["It is the same as per generated second", "You pay for every take; if 40 % of generated seconds are usable, every price per generated second is 2.5 times higher per usable second", "APIs require it", "For taxes"]
    answer: 1
    explain: "The usable share comes from your take log (C05·M01). It changes the ranking less than it changes the budget."
  - q: "When does a per-output API win over serverless GPUs for an open model?"
    options: ["Never", "At low volume, or when you have no time for operations (images, containers, scaling, monitoring); it also gives closed models that you cannot self-host", "Always", "Only for audio"]
    answer: 1
    explain: "Your time is a cost. At 1,200 clips per month the API cost US$300 against about US$81 serverless, a difference that may or may not pay for the operations work."
  - q: "The cost model says owning beats pay-as-you-go above about 2,230 clips per month. What is missing from that number?"
    options: ["Nothing", "Your time, space, noise, failures and repairs, the risk that a faster GPU makes it obsolete, and the capacity limit of one GPU", "The GPU price", "The power cost"]
    answer: 1
    explain: "Break-even is a starting point for a decision, not the decision."
  - q: "What is a spot (preemptible) instance good for?"
    options: ["Live client sessions", "Jobs that can restart: LoRA training with frequent checkpoints and batch generation through a queue with retries", "Storing the archive", "Webhooks"]
    answer: 1
    explain: "Spot capacity is cheaper and can stop at any time. Design the job to resume (C12·M01, C14·M02)."
  - q: "Your models are in one region and your rented GPUs in another. What happens?"
    options: ["Nothing", "Every cold start downloads tens of GB across regions: slow starts and egress fees; keep models on a volume or in an image in the GPU's region", "The GPU is faster", "The models change"]
    answer: 1
    explain: "Data locality matters for large weights (C13·M01 load times)."
  - q: "Which input to the cost model must you measure yourself?"
    options: ["None", "GPU seconds per clip for your workflow and size, and your usable share; list prices are only a start", "The number of GPUs in the cloud", "The model's parameter count"]
    answer: 1
    explain: "Measure on the GPU type you will rent (C11·M02 perf.csv)."
deeper:
  - title: "GPU cloud pricing comparison (mid-2026)"
    url: https://www.buildmvpfast.com/api-costs/gpu
  - title: "Modal — docs (GPU functions)"
    url: https://modal.com/docs
  - title: "RunPod — documentation"
    url: https://docs.runpod.io/
---
## Learn

### Four ways to pay
1. **GPU rental:** a virtual machine or container with a GPU, billed per hour.
   - *Always on (24/7):* the GPU waits for work. You pay 730 hours a month.
   - *On demand:* you start it for a session and stop it after. You pay the hours it is on, plus start, stop, and idle time.
2. **Serverless GPU:** your container runs only when a job arrives; you pay per GPU second, plus cold starts (loading the container and the weights). It scales to zero when idle.
3. **Per-output APIs:** the provider runs the model; you pay per output second or per image. No operations work. This is also the only way to use closed models.
4. **Own hardware:** you buy it. You pay the purchase (spread over its life), the power, the space, and your time.
Hosted apps (subscriptions with credits) are a fifth option for people without a pipeline. They are hard to automate.

### The cost model
For one month:
- rental 24/7 = 730 h × price per hour
- rental on demand = busy hours × overhead × price per hour
- serverless = (busy hours + cold-start hours) × price per hour
- per-output API = output seconds × price per output second
- own = purchase / months of life + busy hours / relative speed × power × electricity price

Busy hours = clips × GPU seconds per clip / 3,600. Measure the GPU seconds per clip for your workflow and size on the GPU type you plan to use (C11·M02). Divide each result by the **usable seconds** (generated seconds × usable share from your take log, C05·M01). That is the cost of what the edit can use.

### What the numbers usually show
- **Always-on rental** is expensive unless the GPU is busy most of the time.
- **On-demand rental** and **serverless** are close for batches. Serverless is simpler to scale; rental gives full control and no cold starts during a session.
- **Per-output APIs** cost more per second at volume, and nothing in operations work. At low volume, they are often the right choice.
- **Owning** wins at high, steady volume over years, if one machine has enough capacity.

### Break-even of owning
Owning has a fixed monthly cost (the purchase spread over its life) and a small variable cost (power). Pay-as-you-go has only a variable cost. Owning wins above the volume where the saving per clip pays the fixed cost. The number leaves out your time, space, repairs, the capacity limit of one GPU, and the risk that next year's models need more VRAM. Treat it as a starting point.

### Spot capacity
Spot (preemptible) instances are cheaper and can stop at any moment. Use them for jobs that can resume: LoRA training with checkpoints every few hundred steps (C14·M02), and batch generation through a queue with retries (C12·M01). Do not use them for live sessions with a client.

### Data locality
Keep models and data in the same region as the GPU. Every cold start reads tens of GB of weights (C13·M01): across regions this is slow, and it costs egress fees. Bake weights into the container image, or use a network volume in the same region (M04).

## Tool walkthrough

### The cost model

```bash
python starter/tools/cost_model.py --clips 1200 --gpu-s 60 --out-s 5 --usable 0.4 \
  --rent-h 2.89 --serverless-h 3.95 --api-s 0.05 --own-price 4500 --own-power-w 650 --kwh 0.30 --own-speed 0.5
```

The defaults are example list prices from mid-2026. Replace every price with the current price of the provider that you would use, with its date.

### Providers (as of 2026-10; list prices mid-2026, check current)
- **GPU rental:** RunPod (H100 about US$2.89/h; A100 community from about US$0.69/h), Lambda, and the hyperscalers (AWS, GCP, Azure; more expensive, with more enterprise features).
- **Serverless GPU:** Modal (H100 about US$3.95/h base, billed per second; region and non-preemptible multipliers), RunPod Serverless, Replicate deployments.
- **Per-output APIs:** fal.ai (some video models about US$0.05 per output second; images about US$0.03), Replicate (per-second GPU billing; H100 effective about US$5.49/h), and vendor APIs (about US$0.10 per output second for some closed video models).

![Three compute paths behind one backend interface](fig:local-cloud.svg)

## Worked example

**Workload:** 1,200 open-model clips per month (5 s each), 60 GPU seconds per clip on an H100-class GPU, usable share 40 %. Output of `cost_model.py` with the default example prices (2026-10-04):

| Path | US$ per month | US$ per usable second |
|---|---|---|
| Rental on demand (×1.3 overhead) | 75.14 | 0.031 |
| Serverless (+ 60 cold starts of 30 s) | 80.98 | 0.034 |
| Own GPU (US$4,500 over 3 years, half the speed, 650 W) | 132.80 | 0.055 |
| Per-output API (US$0.05/s) | 300.00 | 0.125 |
| Rental 24/7 | 2,109.70 | 0.879 |

"Owning beats the cheapest pay-as-you-go path above about 2,228 clips per month." At 6,000 clips per month the order changes: own GPU US$164, on-demand rental US$376, serverless US$397, API US$1,500. The owned GPU then runs about 200 hours a month (27 % of the time), so one machine still has the capacity.

**Decision for 1,200 clips per month:** serverless for the open model (the team can maintain a container), the vendor API for 300 premium closed-model clips (300 × 5 s × US$0.10 = US$150), and no purchase until the volume is steady above about 2,500 clips per month.

## Lab

**Deliverable:** `C13/M03/` with measured inputs, a cost comparison for your workload, a break-even analysis, and a decision.

1. Measure the GPU seconds per clip of one workflow at your production size, on a rented GPU of the type that you would use.
2. Take your usable share from your take log (C05).
3. Collect current prices for each path from real providers, with the date.
4. Run the cost model for your monthly workload, and for 3 times that workload.
5. Write the decision per shot type (open models, closed models, training), with the numbers and what the model leaves out.

**Result checklist**
- [ ] Measured GPU seconds per clip, with the GPU type and settings.
- [ ] Current prices with dates and sources.
- [ ] The cost table for 1× and 3× the workload.
- [ ] A decision with the limits of the model.

## Model answer

**Inputs (shape of a strong answer):** "Wan 2.2 5B I2V, 1280 × 704, 121 frames, 20 steps: 410 s per clip on a rented RTX 5090-class GPU, 214 s on an H100 (measured, 3 runs each). Usable share 0.44 (take log, 230 takes)."

| Path | 900 clips/month | 2,700 clips/month |
|---|---|---|
| Serverless H100 (US$3.95/h, 60 cold starts of 30 s) | US$213 | US$636 |
| On-demand rental H100 (US$2.89/h × 1.3) | US$201 | US$603 |
| Own RTX 5090 workstation (US$4,500 over 3 years, 650 W at US$0.30/kWh) | US$145 (103 h of 730) | US$185 (308 h) |
| Vendor API at US$0.10 per output second | US$450 | US$1,350 |

"At 900 clips the owned workstation is already cheapest, because our GPU seconds per clip are high. But we would need it free 103 hours a month next to the editing work. Decision: buy one generation workstation; keep serverless for peaks and for LTX-2.5 batches that need 80 GB. Left out: our setup and maintenance time (estimated 4 h per month)."
