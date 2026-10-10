---
title: Workstation, storage, and network design
hours: 10
outcomes:
  - Specify a workstation for AI video by workload - generation, editing and grading, local LLMs, training.
  - Calculate storage needs from data rates, durations, takes, models, and caches.
  - Design storage tiers - NVMe for work, a NAS for shared media, object storage for archive - with tested backups.
  - Size the network for shared editing and for moving models.
keywords: [NVMe, NAS, RAID, object storage, 3-2-1 backup]
summary: >
  A studio for AI video has two kinds of load: GPU work (generation and training) and media work (editing,
  grading, delivery). They need different machines or at least different priorities. Storage size is data rate
  times duration, for every copy: takes, intermediates, proxies, renders, and models. Plan three tiers: fast NVMe for
  active work, a NAS for shared media with snapshots, and object storage for the archive and the offsite copy.
  Follow 3-2-1 and test restores. The network must carry the media of every editor at once.
diagram:
  type: stack
  title: Storage tiers
  nodes: ["NVMe: active project, caches, models in use (fastest)", "NAS: shared media for the team; RAID 6 / ZFS + snapshots", "Object storage: archive + offsite copy; lifecycle rules", "Offline copy: a disk in another place (the third copy)"]
  highlight: [1]
watch:
  - title: "Puget Systems — hardware recommendations for video editing and AI"
    url: https://www.pugetsystems.com/solutions/video-editing-workstations/
    note: "Read their test-based recommendations."
  - title: "Backblaze — the 3-2-1 backup strategy"
    url: https://www.backblaze.com/blog/the-3-2-1-backup-strategy/
    note: "Read the rule and the examples."
quiz:
  - q: "How much storage does one hour of UHD (3840 × 2160) ProRes 422 HQ at 24 fps need?"
    options: ["About 10 GB", "About 318 GB (707 Mbit/s × 3,600 s / 8)", "About 3 TB", "About 1 GB"]
    answer: 1
    explain: "Size = data rate × duration. Apple's table gives 707 Mbit/s for UHD 24p ProRes 422 HQ, which is 318 GB per hour."
  - q: "A NAS has 6 disks of 16 TB in RAID 6. What is the usable capacity, roughly?"
    options: ["96 TB", "About 64 TB (two disks hold parity), less after formatting", "16 TB", "32 TB"]
    answer: 1
    explain: "RAID 6 survives two disk failures because two disks' worth of space holds parity: (6 − 2) × 16 = 64 TB."
  - q: "Is RAID a backup?"
    options: ["Yes", "No: RAID survives a disk failure, but a deletion, a ransomware attack, or a fire affects all disks; backups are separate copies, one of them offsite", "Only RAID 6", "Only with snapshots"]
    answer: 1
    explain: "RAID is availability. Backup is recovery. You need both."
  - q: "What does 3-2-1 mean?"
    options: ["3 disks, 2 servers, 1 cloud", "3 copies of the data, on 2 different types of media, with 1 copy offsite", "3 backups per day", "3 TB per project"]
    answer: 1
    explain: "And test the restore. An untested backup is a hope."
  - q: "Three editors work on the same project from a NAS with UHD ProRes 422 HQ (about 88 MB/s each). Is 1 GbE enough?"
    options: ["Yes", "No: 1 GbE carries about 110 MB/s in total; 3 streams need about 265 MB/s. Use 10 GbE (about 1.1 GB/s), or edit with proxies", "Only with Wi-Fi", "It depends on the GPU"]
    answer: 1
    explain: "Add up the streams of all users at the same time, plus headroom for scrubbing and copies."
  - q: "Why plan 2–4 TB of fast storage only for models and caches?"
    options: ["Models are small", "A generation workstation keeps several workflows; each needs 15–45 GB of weights, plus caches and versions; slow storage makes every cold start slow", "For the operating system", "For audio"]
    answer: 1
    explain: "The starter workflows alone are 18–45 GB each (C13·M01)."
  - q: "Generated takes are small (a 5 s H.264 clip is a few MB). Why does an AI project still need a lot of storage?"
    options: ["It does not", "Takes are many (all takes, not only selects), and finishing uses large intermediates: a 5 s UHD ProRes 422 HQ clip is about 440 MB", "Because of the prompts", "Because of the LUTs"]
    answer: 1
    explain: "Plan for every stage: takes, intermediates, proxies, renders, deliveries, stems, and the archive."
deeper:
  - title: "Apple — ProRes white paper (data rates)"
    url: https://www.apple.com/final-cut-pro/docs/Apple_ProRes.pdf
  - title: "Blackmagic — DaVinci Resolve (configuration guide on the product page)"
    url: https://www.blackmagicdesign.com/products/davinciresolve
  - title: "OpenZFS — documentation (snapshots, RAIDZ)"
    url: https://openzfs.github.io/openzfs-docs/
---
## Learn

### Two kinds of load
An AI video studio does two kinds of work:
- **GPU work:** generation and training. It needs VRAM, low-precision compute, and fast storage for weights (M01).
- **Media work:** editing, grading, sound, delivery. It needs a responsive editing machine, a color-accurate monitor, fast storage for intermediates, and hardware video decoding.
One machine can do both for a solo creator. A team usually separates them: a generation box (or rented GPUs) and editing machines.

### Workstation by workload
| Workload | Priority |
|---|---|
| Local video generation | GPU VRAM 32 GB or more (96 GB on professional cards); 128 GB RAM for offloading; 4 TB+ NVMe |
| Editing and grading 4K | A modern GPU or media engine; fast NVMe; a calibrated monitor |
| Local LLMs | Large memory (VRAM or unified) and high bandwidth |
| LoRA training | VRAM 24–96 GB; RAM 64–128 GB; fast NVMe for datasets |

### Storage math
Size = data rate × duration, for every copy you keep. Data rates (Apple's ProRes white paper, 23.976 fps):

| Format | 1920 × 1080 | 3840 × 2160 |
|---|---|---|
| ProRes 422 Proxy | 36 Mbit/s | 145 Mbit/s (65 GB/h) |
| ProRes 422 HQ | 176 Mbit/s (79 GB/h) | 707 Mbit/s (318 GB/h) |

Convert with: GB per hour = Mbit/s × 3,600 / 8 / 1,000. H.264 web deliveries are 5–20 Mbit/s. Generated takes from APIs are small H.264 or H.265 files (a few MB each), but there are many of them.

Plan for every stage of a project:
- **takes:** all generations, not only the selects (C05·M06);
- **intermediates** of the selects for finishing (C09·M01);
- **proxies** for editing;
- **renders and deliveries** in each version and format;
- **audio:** stems and the M&E as WAV (C10·M02);
- **models and caches:** 15–45 GB per workflow (C13·M01), plus versions.

### Storage tiers
1. **NVMe (local):** the active project, caches, and the models in use. Fastest.
2. **NAS (shared):** media for the team. RAID 6 or ZFS RAIDZ2 survives two failed disks: usable capacity ≈ (disks − 2) × disk size. Snapshots protect against deletions.
3. **Object storage (S3-compatible):** the archive and the offsite copy. Cheap per TB; lifecycle rules move old data to colder tiers (M05).

### Backups
RAID is not a backup: a deletion, ransomware, or a fire affects all disks of the array. Follow **3-2-1**: 3 copies, on 2 different types of media, 1 offsite. Example: the NAS, an object-storage copy (offsite), and an offline disk. Test a restore every quarter. Measure how long it takes, and write the time into the plan.

### Network
| Link | About | Enough for |
|---|---|---|
| 1 GbE | 110 MB/s | proxies, one HD intermediate stream |
| 10 GbE | 1.1 GB/s | a few editors on UHD ProRes HQ (about 88 MB/s each) |
| 25 GbE and more | 2.8 GB/s and more | bigger teams, fast model copies |
Add up the streams of all users at the same time, plus headroom for scrubbing and copies. Remote editors use proxies or a cloud file system (M05).

## Tool walkthrough

### A storage plan in a few lines

```python
rates_mbps = {"ProRes HQ UHD": 707, "ProRes HQ HD": 176, "Proxy HD": 36, "H.264 web HD": 12}
def gb(mbps, seconds): return mbps * seconds / 8 / 1000
takes  = 2400 * 0.003                      # 2,400 takes x about 3 MB (API H.264)
inter  = gb(rates_mbps["ProRes HQ UHD"], 20 * 60 * 1.3)   # 20 finished min + 30 % handles, UHD
proxy  = gb(rates_mbps["Proxy HD"], 20 * 60 * 1.3)
deliv  = gb(rates_mbps["H.264 web HD"], 20 * 60 * 6)      # 6 versions
models = 4 * 40                            # 4 workflows x 40 GB
print(round(takes + inter + proxy + deliv + models))      # GB per month
```

### Example builds (as of 2026-10)
- **Generation box:** RTX 5090 (32 GB), 128 GB RAM, 2 × 4 TB PCIe 4.0 NVMe, a 1,200 W power supply, Linux.
- **Editing and LLM machine:** Mac Studio M5 Max with 128 GB unified memory and external Thunderbolt NVMe.
- **NAS:** 6 × 16 TB in RAID 6 (about 64 TB usable), 10 GbE, snapshots.

## Worked example

**Two-person studio, 20 finished minutes per month, UHD finishing:**

| Item | Calculation | Per month |
|---|---|---|
| Takes | 2,400 takes × about 3 MB | 7 GB |
| Intermediates | 26 min (20 + 30 % handles) × 318 GB/h | 138 GB |
| Proxies | 26 min × 65 GB/h (UHD Proxy) | 28 GB |
| Deliveries | 6 versions × 20 min at 12 Mbit/s | 11 GB |
| Stems and M&E | 20 min × 4 files × 48 kHz 24-bit stereo (about 1 GB/h each) | 1.4 GB |
| Total media | | about 185 GB |
| Models | 4 workflows × about 40 GB (one time, on NVMe) | 160 GB |

The intermediates are 75 % of the monthly media. Plan:
- Generation box: RTX 5090, 128 GB RAM, 8 TB NVMe.
- Editing: Mac Studio M5 Max.
- NAS: 6 × 16 TB RAID 6, 10 GbE: enough for more than 20 years at this rate, so the limit is the backup, not the space.
- Archive: one object-storage folder per project (about 0.2 TB), lifecycle to a cold tier after 90 days.
- Backup: NAS snapshots, a nightly sync to object storage, and a quarterly offline disk. A restore test of one project per quarter.

## Lab

**Deliverable:** `C13/M02/` with a workstation specification, a storage plan with calculations, a backup plan, and a restore test.

1. Write the workloads of your studio for the next year: finished minutes per month, finishing resolution, number of versions, team size.
2. Specify the machines (or rented capacity) for each workload, with reasons from M01.
3. Calculate the storage per month for every stage, with the data rates and your take counts. Add models and caches.
4. Design the tiers and the network. Check the network with the streams of all users at once.
5. Write the backup plan (3-2-1). Do one real restore of a project folder from your offsite copy. Measure the time.

**Result checklist**
- [ ] Machine specification with reasons.
- [ ] Storage calculation per stage.
- [ ] Tiers, network check, and backup plan.
- [ ] A measured restore test.

## Model answer

A strong plan shows the calculations, not only the result, and finds the real limit:

"Our intermediates at UHD are 318 GB per hour. 12 finished minutes per month with 30 % handles: 83 GB per month. Total media about 110 GB per month. Space is not the problem; the network is: 3 editors on UHD ProRes HQ need about 265 MB/s, so 1 GbE (110 MB/s) is not enough. Decision: 10 GbE switch and NICs, or HD proxies for the two remote editors."

"Restore test: one 180 GB project from object storage over our 500 Mbit/s line took 52 minutes (the calculation said 48). The offline disk took 9 minutes. For a deadline restore, we use the offline disk first."
