---
title: Cloud media services, cost control, and secure operations
hours: 12
outcomes:
  - Use cloud services for review, shared storage, asset management, and delivery.
  - Define a project's infrastructure as code, and destroy it after delivery.
  - Control cost with budgets, alerts, tags, lifecycle rules, and generation caps.
  - Report cost per finished minute by component.
  - Protect client data, secrets, and model access with a written data rule per project.
keywords: [infrastructure as code, lifecycle rule, budget alert, least privilege, data classification]
summary: >
  Cloud services carry the rest of the production: review with frame-accurate comments, shared storage for remote
  editors, object storage with signed links for clients, and a database of assets. Define each project's
  infrastructure as code, so that it can be built in minutes and destroyed after delivery. Control cost with budgets
  and alerts, tags on every resource, lifecycle rules for temporary data, and caps in the generation queue. Write a
  data rule for every project: which data may go to which vendor. Give every service only the rights it needs.
diagram:
  type: flow
  title: A project's cloud life cycle
  nodes: ["IaC: create bucket, queue, worker, budget", "Production: tagged resources, alerts", "Review: signed links, frame comments", "Lifecycle: temp data deleted after 30 days", "Delivery + archive to cold tier", "IaC: destroy compute"]
  highlight: [0, 5]
watch:
  - title: "Frame.io — review and approval (help center)"
    url: https://help.frame.io/
    note: "Look at frame-accurate comments and version stacks."
  - title: "Terraform — getting started"
    url: https://developer.hashicorp.com/terraform/tutorials
    note: "Only if you have not used infrastructure as code before."
quiz:
  - q: "Why define a project's infrastructure as code?"
    options: ["It is required by clouds", "You can build the same environment in minutes, review changes, and destroy everything after delivery, so nothing keeps costing money", "It is faster to click", "For the client"]
    answer: 1
    explain: "Forgotten GPU workers and buckets are a common, silent cost."
  - q: "What does a lifecycle rule do?"
    options: ["Rotates keys", "Moves or deletes objects automatically by age: for example delete temporary generations after 30 days, move archives to a cold tier after 90", "Backs up the NAS", "Renders files"]
    answer: 1
    explain: "Storage is cheap per GB and expensive when nobody cleans it up."
  - q: "Where must the generation budget be enforced?"
    options: ["In the cloud billing console only", "In the queue before jobs are sent (C12·M01), with cloud budget alerts as a second line", "In the agent's prompt", "Nowhere"]
    answer: 1
    explain: "Cloud alerts arrive after the money is spent. The queue refuses before."
  - q: "A client's unreleased product photos must not go to any external model API. What is the practical rule?"
    options: ["Do not use AI", "A written data rule for the project: those files stay in your own storage and are used only with open models on your GPUs; external APIs may get only generated or public material", "Ask each time", "Use a VPN"]
    answer: 1
    explain: "Classify data per project. Check each vendor's terms on training with your data (C16)."
  - q: "How do you share a draft with a client securely?"
    options: ["A public bucket link", "A review service or a signed URL that expires, with view-only access to that version", "Email the file", "A shared password"]
    answer: 1
    explain: "Expiring, scoped links limit the damage if a link leaks."
  - q: "Which tags belong on every cloud resource?"
    options: ["None", "Project, client, environment, and owner, so budgets, reports, and clean-up work per project", "Only the region", "The GPU type"]
    answer: 1
    explain: "Without tags, you cannot report cost per project or find what to delete."
  - q: "What is least privilege for a generation worker?"
    options: ["Admin rights", "Read its job queue, read the models, write only to its output prefix, read only its own secrets", "Full bucket access", "No rights"]
    answer: 1
    explain: "If the worker is compromised, the damage stays small."
deeper:
  - title: "Blackmagic Cloud — collaboration"
    url: https://www.blackmagicdesign.com/products/davinciresolve/collaboration
  - title: "AWS — media services"
    url: https://aws.amazon.com/media-services/
  - title: "AWS S3 — lifecycle configuration (the same idea exists on other clouds)"
    url: https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html
---
## Learn

### Cloud media services
- **Review and approval:** reviewers comment on exact frames, compare versions, and approve. The comments go back into the editor's timeline in some tools.
- **Shared storage for remote editors:** cloud file systems stream media on demand, so editors do not download whole projects; or a cloud NAS.
- **Object storage and delivery:** buckets for masters and deliveries; signed URLs that expire for clients; a CDN for public delivery.
- **Asset management:** a database of assets with their metadata. The sidecar JSON of C12·M02 is the start of it: prompt-log ID, rights, tech data, approvals.

### Infrastructure as code
Define each project's resources in code: buckets with lifecycle rules, the queue, the workers or serverless functions, roles and policies, budgets and alerts, dashboards. Benefits:
- the same environment in minutes for the next project;
- changes are reviewed like code;
- after delivery you destroy the compute, and nothing keeps costing money.

### Cost control
- **Generation caps** in the queue, per shot and per project (C12·M01). This is the first line: it refuses before money is spent.
- **Budgets and alerts** per project (for example at 50 %, 80 %, and 100 %). This is the second line: it warns after money is spent.
- **Tags** on every resource: project, client, environment, owner.
- **Lifecycle rules:** delete temporary generations after 30 days; move archives to a cold tier after 90 days.
- **A monthly report:** cost per finished minute by component (generation, compute, storage, licenses, review tools).

### The review loop
Review is where most project time goes after generation. Make it fast and exact:
- **One link per version**, with the version number in the file name and on screen (a small burned-in label on drafts).
- **Frame-accurate comments:** a reviewer clicks a frame and writes the note there. Comments with timecodes can go back into the timeline as markers, where an agent or an editor works through them (C08·M03).
- **Clear states:** draft, in review, changes requested, approved. Only approved versions go to delivery.
- **Expiring access:** a signed link or a review project that closes after delivery.

### Agents and vendors in the cloud
Agents (C12) and external vendors also need access, and each needs a boundary:
- an agent's tools get the same least-privilege roles as a worker, and every call is logged;
- a vendor gets only the files that the data rule allows, through a prefix or a signed URL, never the whole bucket;
- revoke access when the project ends, in the same code that destroys the compute.

### Data and security
- **A data rule per project:** which files may go to which vendor. Client material (unreleased products, real people, contracts) often stays in your own storage and goes only to open models on your GPUs. Check each vendor's terms about training on your data (C16).
- **Least privilege:** every service gets only the rights it needs. A worker reads its queue and the models and writes only to its output prefix.
- **Encryption** at rest and in transit (usually default; check it).
- **Secrets** in a secret manager; rotate keys; never in images or code.
- **Audit logs** for people and agents (C12·M03).

## Tool walkthrough

### A lifecycle rule and a budget (Terraform, AWS example)

```hcl
resource "aws_s3_bucket_lifecycle_configuration" "project" {
  bucket = aws_s3_bucket.project.id
  rule {
    id     = "temp-generations"
    status = "Enabled"
    filter { prefix = "gen/tmp/" }
    expiration { days = 30 }
  }
  rule {
    id     = "archive"
    status = "Enabled"
    filter { prefix = "archive/" }
    transition {
      days          = 90
      storage_class = "DEEP_ARCHIVE"
    }
  }
}
```

The same ideas exist on every cloud. Write the budget alert in the same code, with the project tag as its filter.

### Cost per finished minute from your logs

```bash
python starter/tools/takes.py report                     # generation cost per model and shot (C05)
python starter/tools/promptlog.py cost --since 2026-10-01   # image and other generation costs (C04)
python starter/pipeline/genqueue.py status               # queued and spent jobs (C12)
```

Add the cloud bill per project tag, and divide by the finished minutes.

### Services (as of 2026-10)
Review: Frame.io (Adobe), Blackmagic Cloud (Resolve). Shared storage: cloud file systems for media. Storage and delivery: S3-compatible object storage on any major cloud.

## Worked example

**Project "Camera Ad Q4"** (30 s ad, 6 versions):
- **Infrastructure as code** creates: a bucket with two lifecycle rules (temporary generations deleted after 30 days; archive to a cold tier after 90), the queue and a serverless worker, a budget of US$400 with alerts at 50/80/100 %, and a review project.
- **Data rule:** the client's product CAD files and photos stay in our bucket and are used only with open models on our serverless GPUs. Only generated backgrounds and public material go to external APIs.
- **Cost report:**

| Component | US$ |
|---|---|
| Generation (API takes, from `takes.py report`) | 61.40 |
| Serverless GPU (open-model takes and LoRA) | 38.20 |
| Storage and egress | 4.10 |
| Music license | 49.00 |
| Review tool (share of the month) | 15.00 |
| Total for 0.5 finished minutes (30 s master; versions are cut-downs) | 167.70 → US$335 per finished minute |

- **After delivery:** the archive moved to a cold tier; the worker and the queue destroyed with `terraform destroy`; the bucket kept for the archive only.

## Lab

**Deliverable:** `infra/project/` with infrastructure as code, a data rule, a budget with alerts, a cost report, and a clean-up check.

1. Write the infrastructure of one project as code: a bucket with lifecycle rules, the queue and a worker, roles with least privilege, a budget with alerts, and tags.
2. Write the project's data rule: data classes, and which vendor may receive which class.
3. Run a small production through it (your C12 mini-project).
4. Make the cost report per component, and the cost per finished minute.
5. After delivery, destroy the compute. Check (in the console or with the CLI) that no tagged compute resource remains.

**Result checklist**
- [ ] Infrastructure as code with lifecycle rules, budget, and tags.
- [ ] Data rule.
- [ ] Cost report per component and per finished minute.
- [ ] Clean-up check after delivery.

## Model answer

A strong submission's data rule is a table that a teammate can follow without asking:

| Data class | Examples | May go to |
|---|---|---|
| Client confidential | product CAD, unreleased photos, contracts | own bucket; open models on own or serverless GPUs only |
| Personal data | faces and voices of real people, consent records | own bucket; vendors only with consent and a data agreement |
| Generated, internal | takes, drafts | own bucket; external APIs allowed |
| Public | press photos with license, public-domain material | anywhere, with a rights-log line |

"Clean-up check: `terraform destroy` removed 7 resources; the console showed no compute with the tag `project=camera-q4`; the bucket remained with 214 GB in the cold tier. The budget alert at 50 % arrived on day 3, which made us move the B-roll shots to the open model."
