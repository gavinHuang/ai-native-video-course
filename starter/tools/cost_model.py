#!/usr/bin/env python3
"""Monthly cost of a generation workload on four compute paths, and the break-even of owning a GPU (C13·M03).

  python cost_model.py --clips 1200 --gpu-s 60 --out-s 5 --usable 0.4
  python cost_model.py --clips 1200 --gpu-s 60 --out-s 5 --usable 0.4 --rent-h 2.89 --serverless-h 3.95 --api-s 0.05 \
      --own-price 4500 --own-power-w 650 --kwh 0.30 --own-years 3

Inputs (state their source and date in your plan):
  --clips      generated clips per month (all takes, not only the usable ones)
  --gpu-s      GPU seconds per clip on the reference GPU (measure it: C11·M02 perf.csv)
  --out-s      seconds of video per clip
  --usable     usable share of generated seconds (C05·M01): the cost per USABLE second is the number that matters
  prices       rental and serverless per GPU hour, API per output second, and the costs of owning
Paths:
  rental 24/7     the GPU is paid every hour of the month, used or not
  rental on demand  paid only for the hours you run (with an overhead for start/stop and idle time)
  serverless      paid per GPU second, plus cold starts
  per-output API  paid per output second, no operations
  own             purchase spread over its life + electricity at your utilization
"""
import argparse


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--clips", type=float, required=True)
    ap.add_argument("--gpu-s", type=float, required=True)
    ap.add_argument("--out-s", type=float, required=True)
    ap.add_argument("--usable", type=float, default=0.4)
    ap.add_argument("--rent-h", type=float, default=2.89, help="US$ per GPU hour, rental (example: an H100 list price mid-2026)")
    ap.add_argument("--rent-overhead", type=float, default=1.3, help="on-demand rental: paid hours / busy hours")
    ap.add_argument("--serverless-h", type=float, default=3.95, help="US$ per GPU hour, serverless (example list price mid-2026)")
    ap.add_argument("--cold-s", type=float, default=30, help="cold-start seconds per batch")
    ap.add_argument("--batches", type=float, default=60, help="cold starts per month (batches of jobs)")
    ap.add_argument("--api-s", type=float, default=0.05, help="US$ per output second, per-output API")
    ap.add_argument("--own-price", type=float, default=4500, help="US$ for a workstation with a comparable GPU")
    ap.add_argument("--own-years", type=float, default=3)
    ap.add_argument("--own-power-w", type=float, default=650)
    ap.add_argument("--kwh", type=float, default=0.30)
    ap.add_argument("--own-speed", type=float, default=0.5, help="own GPU speed relative to the reference GPU (0.5 = half as fast)")
    a = ap.parse_args()
    busy_h = a.clips * a.gpu_s / 3600
    out_s = a.clips * a.out_s
    usable_s = out_s * a.usable
    rows = {
        "rental 24/7": 730 * a.rent_h,
        "rental on demand": busy_h * a.rent_overhead * a.rent_h,
        "serverless": (busy_h + a.batches * a.cold_s / 3600) * a.serverless_h,
        "per-output API": out_s * a.api_s,
        "own GPU": a.own_price / (a.own_years * 12) + (busy_h / a.own_speed) * a.own_power_w / 1000 * a.kwh,
    }
    print(f"workload: {a.clips:.0f} clips/month, {busy_h:.1f} busy GPU hours, {out_s:.0f} s generated, {usable_s:.0f} s usable "
          f"({a.usable:.0%})")
    own_hours = busy_h / a.own_speed
    print(f"own GPU needs {own_hours:.0f} h/month at {a.own_speed:.0%} of the reference speed "
          f"({own_hours / 730:.0%} of the month){'  <- more than the month: not enough capacity' if own_hours > 730 else ''}")
    print(f"\n{'path':20} {'US$/month':>10} {'US$/usable s':>13}")
    for k, v in sorted(rows.items(), key=lambda x: x[1]):
        print(f"{k:20} {v:10.2f} {v / usable_s:13.3f}")
    # break-even of owning vs the cheapest pay-as-you-go path, as a function of volume
    paygo = min(rows["rental on demand"], rows["serverless"], rows["per-output API"])
    own_fixed = a.own_price / (a.own_years * 12)
    own_var = rows["own GPU"] - own_fixed
    per_clip_paygo = paygo / a.clips
    per_clip_own = own_var / a.clips
    if per_clip_paygo > per_clip_own:
        be = own_fixed / (per_clip_paygo - per_clip_own)
        print(f"\nowning beats the cheapest pay-as-you-go path above about {be:.0f} clips/month "
              f"(purchase spread over {a.own_years:g} years; excludes your time, space, and failures)")
    else:
        print("\nowning never beats pay-as-you-go at these prices")


if __name__ == "__main__":
    main()
