#!/usr/bin/env python3
"""Estimate the energy and emissions of a production's own GPU work (C16·M04).

  python footprint.py --gpu-hours 40 --gpu-w 450 --overhead 1.4 --grid 0.35 [--finished-min 3]
  python footprint.py --takes-gpu-s 60 --takes 1200 --gpu-w 700 --grid 0.35

energy (kWh) = GPU hours x GPU power (kW) x overhead (rest of the machine + cooling; data centres report a
PUE of about 1.1-1.6) ; emissions (kg CO2e) = energy x grid factor (kg CO2e per kWh; varies from below 0.05
to above 0.7 by country and hour - use your grid operator's or cloud region's number).
Hosted APIs rarely publish energy per output: report them as "not disclosed" with the number of output seconds,
instead of inventing a value. The lever that matters most is the number of takes (explore cheap, finish selectively).
"""
import argparse


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--gpu-hours", type=float)
    ap.add_argument("--takes", type=float)
    ap.add_argument("--takes-gpu-s", type=float, help="GPU seconds per take")
    ap.add_argument("--gpu-w", type=float, required=True, help="average GPU power draw in watts (measure with nvidia-smi)")
    ap.add_argument("--overhead", type=float, default=1.4)
    ap.add_argument("--grid", type=float, required=True, help="kg CO2e per kWh")
    ap.add_argument("--finished-min", type=float)
    ap.add_argument("--api-output-s", type=float, default=0)
    a = ap.parse_args()
    h = a.gpu_hours if a.gpu_hours is not None else a.takes * a.takes_gpu_s / 3600
    kwh = h * a.gpu_w / 1000 * a.overhead
    co2 = kwh * a.grid
    print(f"own GPU work: {h:.1f} GPU hours x {a.gpu_w:.0f} W x {a.overhead} overhead = {kwh:.1f} kWh -> {co2:.1f} kg CO2e (grid {a.grid})")
    if a.finished_min:
        print(f"per finished minute: {kwh / a.finished_min:.2f} kWh, {co2 / a.finished_min:.2f} kg CO2e")
    if a.api_output_s:
        print(f"hosted API output: {a.api_output_s:.0f} s generated - energy not disclosed by the vendor (report the seconds)")


if __name__ == "__main__":
    main()
