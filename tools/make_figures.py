#!/usr/bin/env python3
"""Generate concept illustrations (theme-aware SVG) into assets/figures/."""
import math
import random
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "figures"
OUT.mkdir(parents=True, exist_ok=True)


def person(cx, top, h):
    """Simple figure: head + body, height h from top."""
    r = h * 0.11
    hy = top + r
    body = f'<path class="f-line" stroke-width="{max(1.5, h/60):.1f}" d="M{cx},{hy+r} L{cx},{top+h*0.62} M{cx},{top+h*0.62} L{cx-h*0.13},{top+h} M{cx},{top+h*0.62} L{cx+h*0.13},{top+h} M{cx-h*0.2},{top+h*0.36} L{cx+h*0.2},{top+h*0.36}"/>'
    return f'<circle class="f-soft" cx="{cx}" cy="{hy}" r="{r}"/>' + body


def shot_sizes():
    sizes = [("EWS", 0.12), ("WS", 0.75), ("MS", 1.6), ("MCU", 2.3), ("CU", 4.0), ("ECU", 8.5)]
    w, h, gap = 112, 63, 12
    parts = []
    for i, (name, scale) in enumerate(sizes):
        x = 10 + i * (w + gap)
        y = 20
        clip = f"c{i}"
        parts.append(f'<clipPath id="{clip}"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath>')
        parts.append(f'<rect class="f-fill" x="{x}" y="{y}" width="{w}" height="{h}" stroke-width="1" style="stroke:var(--line)"/>')
        ph = h * scale
        top = y + h * 0.18 if scale < 1 else y + h * 0.12 - (ph * 0.11) * (scale > 3)
        if scale >= 4:
            top = y + h * 0.5 - ph * 0.11  # center on the face
        parts.append(f'<g clip-path="url(#{clip})">{person(x + w/2, top, ph)}'
                     + (f'<line class="f-line" x1="{x}" y1="{y+h*0.82}" x2="{x+w}" y2="{y+h*0.82}" stroke-width="1"/>' if scale < 1 else "")
                     + '</g>')
        parts.append(f'<text class="f-text" x="{x + w/2}" y="{y + h + 18}" text-anchor="middle" font-weight="600">{name}</text>')
    W = 10 + 6 * (w + gap)
    return f'<svg viewBox="0 0 {W} 112" role="img" aria-label="Six shot sizes">{"".join(parts)}</svg>'


def three_point():
    p = ['<svg viewBox="0 0 520 300" role="img" aria-label="Three-point lighting, top view">',
         '<text class="f-mute" x="16" y="22">TOP VIEW</text>']
    sx, sy = 260, 120
    p.append(f'<circle class="f-soft" cx="{sx}" cy="{sy}" r="22"/><text class="f-text" x="{sx}" y="{sy+4}" text-anchor="middle">subject</text>')
    p.append(f'<rect class="f-fill" x="{sx-28}" y="250" width="56" height="30" style="stroke:var(--ink)"/><text class="f-text" x="{sx}" y="270" text-anchor="middle">camera</text>')
    p.append(f'<line class="f-line" x1="{sx}" y1="248" x2="{sx}" y2="{sy+26}" stroke-dasharray="4 4"/>')
    lights = [("KEY", 120, 220, "f-mark", "strong, 45° side"), ("FILL", 410, 225, "f-acc", "soft, sets ratio"), ("BACK", 340, 38, "f-acc", "rim, separation")]
    for name, x, y, cls, note in lights:
        p.append(f'<line class="f-line" x1="{x}" y1="{y}" x2="{sx + (x-sx)*0.2}" y2="{sy + (y-sy)*0.2}" stroke-width="1.5"/>')
        p.append(f'<circle class="{cls}" cx="{x}" cy="{y}" r="14"/>')
        p.append(f'<text class="f-text" x="{x}" y="{y-22}" text-anchor="middle" font-weight="600">{name}</text>')
        p.append(f'<text class="f-mute" x="{x}" y="{y+30}" text-anchor="middle">{note}</text>')
    p.append("</svg>")
    return "".join(p)


def rule_180():
    p = ['<svg viewBox="0 0 520 300" role="img" aria-label="180-degree rule, top view">',
         '<text class="f-mute" x="16" y="22">TOP VIEW · ACTION LINE</text>']
    ax, bx, y = 170, 350, 130
    p.append(f'<line x1="60" y1="{y}" x2="460" y2="{y}" style="stroke:var(--mark)" stroke-width="2" stroke-dasharray="8 5"/>')
    p.append(f'<circle class="f-soft" cx="{ax}" cy="{y}" r="20"/><text class="f-text" x="{ax}" y="{y+4}" text-anchor="middle">A</text>')
    p.append(f'<circle class="f-soft" cx="{bx}" cy="{y}" r="20"/><text class="f-text" x="{bx}" y="{y+4}" text-anchor="middle">B</text>')
    p.append('<rect x="60" y="140" width="400" height="140" style="fill:var(--accent-soft);opacity:.55"/>')
    p.append('<text class="f-mute" x="72" y="272">ALLOWED SIDE: A stays left, B stays right</text>')
    for i, (cx, cy) in enumerate([(260, 240), (150, 210), (380, 210)]):
        p.append(f'<rect class="f-fill" x="{cx-16}" y="{cy-10}" width="32" height="20" style="stroke:var(--ink)"/><text class="f-mute" x="{cx}" y="{cy+4}" text-anchor="middle">{i+1}</text>')
    p.append('<rect class="f-fill" x="244" y="52" width="32" height="20" style="stroke:var(--bad)"/><text class="f-mute" x="260" y="66" text-anchor="middle">✕</text>')
    p.append('<text class="f-mute" x="290" y="66">crossing the line: A and B swap sides on screen</text>')
    p.append("</svg>")
    return "".join(p)


def denoise():
    random.seed(7)
    p = ['<svg viewBox="0 0 640 170" role="img" aria-label="Denoising from noise to image in steps">']
    labels = ["step 0: noise", "step 2", "step 4", "step 8", "final"]
    for k in range(5):
        x0, y0, s = 10 + k * 126, 20, 110
        p.append(f'<rect class="f-fill" x="{x0}" y="{y0}" width="{s}" height="{s}" style="stroke:var(--line)"/>')
        t = k / 4  # 0 = noise, 1 = clean
        # target shape: a sun (circle) over a horizon
        for _ in range(int(260 * (1 - t) + 30)):
            px, py = x0 + random.random() * s, y0 + random.random() * s
            p.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="1.6" style="fill:var(--muted);opacity:{0.85*(1-t)+0.05:.2f}"/>')
        op = t
        p.append(f'<circle class="f-mark" cx="{x0+s*0.5}" cy="{y0+s*0.42}" r="{s*0.16}" style="opacity:{op:.2f}"/>')
        p.append(f'<rect class="f-acc" x="{x0}" y="{y0+s*0.68}" width="{s}" height="{s*0.32}" style="opacity:{op*0.8:.2f}"/>')
        p.append(f'<text class="f-mute" x="{x0+s/2}" y="{y0+s+20}" text-anchor="middle">{labels[k]}</text>')
        if k < 4:
            p.append(f'<text class="f-text" x="{x0+s+8}" y="{y0+s/2+4}">→</text>')
    p.append("</svg>")
    return "".join(p)


def local_cloud():
    p = ['<svg viewBox="0 0 640 230" role="img" aria-label="Local and cloud generation paths">']
    cols = [("LOCAL", ["Workstation GPU (24–96 GB)", "NVMe: models + cache", "ComfyUI / scripts"], 20),
            ("SERVERLESS / RENTED", ["Container with model", "Autoscale on queue", "Pay per GPU-second/hour"], 230),
            ("MODEL APIs", ["Vendor or aggregator", "Pay per output second", "No ops, less control"], 440)]
    for title, items, x in cols:
        p.append(f'<text class="f-mute" x="{x}" y="22">{title}</text>')
        for i, it in enumerate(items):
            p.append(f'<rect class="f-fill" x="{x}" y="{34+i*44}" width="180" height="34" rx="5" style="stroke:var(--line)"/>')
            p.append(f'<text class="f-text" x="{x+10}" y="{56+i*44}">{it}</text>')
    p.append('<rect class="f-soft" x="20" y="176" width="600" height="38" rx="6"/>')
    p.append('<text class="f-text" x="320" y="200" text-anchor="middle" font-weight="600">Your pipeline: one backend interface routes each shot to the best path</text>')
    p.append("</svg>")
    return "".join(p)


FIGS = {"shot-sizes.svg": shot_sizes, "three-point.svg": three_point, "rule-180.svg": rule_180,
        "denoise.svg": denoise, "local-cloud.svg": local_cloud}

if __name__ == "__main__":
    for name, fn in FIGS.items():
        (OUT / name).write_text(fn())
        print("wrote", name)
