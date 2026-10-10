---
title: Model APIs - async jobs, queues, retries, webhooks
hours: 14
outcomes:
  - Call video, image, and audio model APIs that run as asynchronous jobs, and download results before they expire.
  - Build a job queue with idempotency keys, retries with backoff and jitter, timeouts, and a dead-letter state.
  - Enforce budgets per shot and in total before any job is sent.
  - Receive results with webhooks or polling, and verify webhook signatures.
  - Put vendors behind one interface, so a model change is a configuration change.
keywords: [async job, idempotency key, exponential backoff, webhook, dead-letter queue]
summary: >
  Generation APIs are asynchronous: you submit a job, the vendor queues and runs it, and you collect the result
  later. A reliable pipeline needs a queue with idempotency keys (a retry never pays twice), retries with
  exponential backoff and jitter that respect Retry-After, timeouts, and a dead-letter state for jobs that need a
  person. Budgets must be checked before a job is sent. Webhooks deliver results efficiently; polling is simpler.
  One backend interface for all vendors turns a removed model into a configuration change.
diagram:
  type: flow
  title: One job through the queue
  nodes: ["Submit with idempotency key", "Budget check (shot cap, total cap)", "Send to backend", "429 / 5xx → backoff + jitter → retry", "Succeeded → download + log cost", "Too many tries → dead letter → person"]
  highlight: [1, 3]
watch:
  - title: "fal.ai — documentation (queue, webhooks, model APIs)"
    url: https://docs.fal.ai/
    note: "Read the queue and webhook sections."
  - title: "Replicate — documentation (predictions, webhooks)"
    url: https://replicate.com/docs
    note: "Compare its job model with fal's."
quiz:
  - q: "A network error happens after you send a job, before you receive its ID. You retry. How do you avoid paying for two generations?"
    options: ["Never retry", "Send an idempotency key with each attempt of the same logical job, and store jobs by that key, so a repeat returns the existing job", "Wait longer", "Use a cheaper model"]
    answer: 1
    explain: "An idempotency key (for example S07.p2.g4) makes a retry safe. The starter queue returns the existing job for a known key."
  - q: "A vendor answers HTTP 429 with 'Retry-After: 2'. What does your worker do?"
    options: ["Retry at once", "Wait at least 2 s (more if your backoff says so), then retry; count the try", "Fail the job", "Switch vendors at once"]
    answer: 1
    explain: "Retry-After is a minimum. Backoff with jitter spreads retries so many workers do not hit the API together."
  - q: "Why add random jitter to exponential backoff?"
    options: ["For fun", "Without jitter, many failed jobs retry at the same moments and overload the API again (a thundering herd)", "It makes retries faster", "Vendors require it"]
    answer: 1
    explain: "Full jitter waits a random time between 0 and the backoff limit."
  - q: "Where must the budget check happen?"
    options: ["After the job succeeds", "Before the job is sent: estimate the cost, add what is already spent and queued for the shot and in total, and refuse above the cap", "At the end of the month", "In the vendor console only"]
    answer: 1
    explain: "A check after the job is a report, not a guard."
  - q: "A job fails 5 times with HTTP 500. What happens to it?"
    options: ["It retries forever", "It goes to the dead-letter state, and a person looks at it (wrong input? vendor outage? switch backend?)", "It is deleted", "It is marked succeeded"]
    answer: 1
    explain: "A limit on tries protects money and makes problems visible."
  - q: "Your webhook endpoint receives 'job succeeded' for a job ID you do not know. What is the rule?"
    options: ["Process it", "Verify the signature of every webhook; reject unsigned or unknown events; never trust the payload alone", "Reply with an error page", "Store it for later"]
    answer: 1
    explain: "A public endpoint can receive forged requests. Vendors sign webhooks; verify the signature and the job ID."
  - q: "A vendor removed the model that all your dialogue shots used. With a backend interface and a routing config, what changes?"
    options: ["The whole pipeline", "The routing entry for 'dialogue' points to another backend and model; you re-test that shot type with your eval set", "Nothing", "The database"]
    answer: 1
    explain: "This is the point of the abstraction. The Sora 2 API removal (2026-09-24) stopped pipelines that called one vendor directly."
deeper:
  - title: "OpenAI API deprecations page (Sora 2 / Videos API removal)"
    url: https://developers.openai.com/api/docs/deprecations
  - title: "AWS Architecture Blog — Exponential backoff and jitter"
    url: https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
  - title: "Stripe — idempotent requests (a clear explanation of idempotency keys)"
    url: https://docs.stripe.com/api/idempotent_requests
---
## Learn

### Why generation APIs are asynchronous
A video generation takes from seconds to many minutes. An HTTP request cannot stay open that long. So generation APIs work as jobs:
1. **Submit:** you send the model, the inputs, and often a webhook URL. You get a job ID at once.
2. **Run:** the vendor queues and runs the job. States: queued → running → succeeded or failed.
3. **Result:** you get output URLs, by webhook or by polling. Many URLs are temporary: download the files at once, and store them in your own storage.

### What can go wrong
- **Rate limits (HTTP 429):** too many requests. The response often has a Retry-After value.
- **Server errors (5xx) and network errors:** temporary. Retry later.
- **Permanent errors:** bad input, a content-policy refusal, an unknown model. Do not retry; fix the input.
- **Lost responses:** the job was accepted, but you did not receive the ID. A naive retry pays twice.
- **Hanging jobs:** no result after a long time.
- **Silent cost:** every retry and every take costs money.

### The queue
Put every generation into your own queue first. The queue is the single source of truth: which jobs exist, their state, their tries, and their cost. A worker takes due jobs, sends them, and updates them. A simple database table is enough for one studio. Larger systems use a queue service.

### Reliability patterns
- **Idempotency key:** a deterministic key for each logical job, for example `S07.p2.g4` (shot S07, prompt version 2, generation 4). Submitting the same key again returns the same job. Some vendors also accept the key, so a repeated request does not start a second paid job.
- **Retries with exponential backoff and full jitter:** after try n, wait a random time between 0 and min(cap, base × 2ⁿ). The randomness spreads retries, so many workers do not hit the API at the same moment. A Retry-After from the vendor is a minimum.
- **Timeouts:** a job that runs longer than its timeout is checked and resubmitted (with the same key).
- **Dead-letter state:** after the last try, the job stops and waits for a person. The person decides: fix the input, wait for the vendor, or switch the backend.

### Budget guards
Check the budget before the job is sent: the estimate of this job, plus what the shot and the project have already spent, plus what is already queued. Refuse above the cap. A shot that reaches its cap needs a new approach, not more takes (C05·M06).

### Webhooks and polling
- **Webhooks:** the vendor calls your endpoint when the job finishes. Efficient, but you need a public HTTPS endpoint, and you must verify the vendor's signature on every call. Reject unsigned events and unknown job IDs.
- **Polling:** your worker asks for the status every few seconds (5–15 s is enough for video). Simple, and works behind a firewall.
Many pipelines use webhooks with polling as a fallback.

### One interface for all backends
Write one interface:

```python
class Backend(Protocol):
    def estimate(self, inputs: dict) -> float: ...    # US$
    def submit(self, inputs: dict) -> str: ...        # remote job id; raises TransientError / PermanentError
    def poll(self, remote_id: str) -> tuple[str, dict]: ...   # ("running" | "succeeded" | "failed", result)
```

Each vendor is one class. Your own node-graph server is one more (C11·M04). A routing config chooses the backend per shot type (C05·M06). When a vendor removes a model, you change one line of the config and re-test that shot type.

## Tool walkthrough

### The starter queue

```bash
cd starter/pipeline
python genqueue.py submit S07.p2.g4 --backend fake --inputs '{"prompt": "...", "seconds": 6}' --cap 3.0
python genqueue.py work --once            # or: python genqueue.py work  (loop every 5 s)
python genqueue.py status S07.p2.g4       # the job and its event history
python genqueue.py dead                   # jobs that need a person
```

`genqueue.py` uses SQLite (one file, no server). It has two backends: `fake` (for tests; the `FAKE_PLAN` variable sets outcomes such as `429,500,ok`) and `comfy` (the C11 client). Add a vendor by writing a class with `estimate`, `submit`, and `poll`. Map HTTP 429 and 5xx to `TransientError` (with `retry_after` from the header) and 4xx input errors to `PermanentError`.

Run the tests: `pytest -q test_genqueue.py`.

### Vendor APIs (as of 2026-10)
- **Aggregators:** fal.ai and Replicate offer many models with one queue and webhook model.
- **Vendor APIs:** model vendors offer their own job APIs (see the landscape page).
Read each vendor's limits: concurrency, rate limits, output URL expiry, and webhook signing.

## Worked example

**Queue tests** (2026-10-04, `pytest -q test_genqueue.py`, 8 passed in 0.03 s):

| Test | What it proves |
|---|---|
| success | A job goes queued → sent → succeeded; cost logged (US$0.60 for 6 s) |
| idempotent submit | The same key twice gives one job |
| Retry-After and backoff | Plan `429,500,ok`: the first wait is ≥ 2 s (Retry-After), then a backoff, then success after 3 tries |
| dead letter | Plan `500` with 3 tries maximum: the job ends in `dead` after 3 tries |
| permanent error | Plan `bad`: `dead (permanent)` at once, no retry |
| shot cap | A second US$0.60 job on a shot with a US$1.00 cap is refused before it is sent |
| total cap | The 9th job of US$0.60 is refused under a total cap of US$5.00 |
| jitter | Backoff waits stay within the cap and are all different |

**Routing config of a project:**

```yaml
hero_product: {backend: veo,   model: veo-3.1,   mode: i2v, cap_per_shot: 3.00}
dialogue:     {backend: kling, model: kling-3.0, mode: r2v, cap_per_shot: 2.00}
broll:        {backend: comfy, workflow: 03_i2v_wan22_5b.json, cap_per_shot: 0.50}
```

A job for S07 (dialogue): budget check ✓ → submit with key `S07.p2.g4` → HTTP 429 with Retry-After 2 → wait 2.0 s → HTTP 500 → wait 3.1 s (backoff with jitter) → accepted → webhook "succeeded" (signature verified) → download → cost US$0.60 logged in the take log (C05·M06) and the prompt log.

## Lab

**Deliverable:** `pipelines/genqueue/` with your queue (or the starter queue extended), one real vendor backend, tests, and a routing config.

1. Run the starter queue and its tests. Read the code.
2. Write one real backend for a vendor or aggregator that you use: `estimate`, `submit`, `poll`. Map its errors to transient and permanent.
3. Add a webhook receiver (a small HTTP server) that verifies the vendor's signature. Keep polling as a fallback.
4. Write a routing config for your shot types and route 10 real shots through the queue.
5. Write tests with the fake backend for: a lost response (submit twice with the same key), Retry-After, the dead-letter state, and both caps.
6. Simulate a vendor outage (make your backend raise transient errors). Show the dead-letter list, then switch the routing for that shot type and finish the jobs.

**Result checklist**
- [ ] One real backend; 10 real shots through the queue with costs logged.
- [ ] Webhook signature verification (and a rejected forged request in a test).
- [ ] Tests for idempotency, Retry-After, dead letters, and caps pass.
- [ ] The outage drill: dead letters, routing change, jobs finished.

## Model answer

A strong submission has a backend of about 60 lines and tests that use the fake backend for every failure path. Its README states the vendor facts that the code depends on:

| Vendor fact | Value (from the docs, date) | Where in the code |
|---|---|---|
| Rate limit | 10 concurrent jobs | worker concurrency = 8 |
| Retry-After on 429 | yes, seconds | `TransientError(retry_after=...)` |
| Output URL expiry | 1 hour | download in the success handler |
| Webhook signature | HMAC-SHA256 of the body, header `X-Signature` | `verify_webhook()` + test with a forged body |

"Outage drill: 6 dialogue jobs went to `dead` after 5 tries each in 4 min 10 s (backoff cap 60 s). I changed `dialogue.backend` from `kling` to `comfy` with workflow `07_lipsync_ia2v_ltx23` and resubmitted with new keys (`.g5`). All 6 finished. Total extra cost: US$0, because no failed try was charged."
