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


def camera_angles():
    """What the frame looks like from each camera height/angle, same panel style as shot_sizes."""
    w, h = 112, 63
    L = 'class="f-line" stroke-width="2"'

    def eye(x, y):
        return person(x + w/2, y + h*0.12, h*1.6) + f'<line {L} x1="{x}" y1="{y+h*0.3}" x2="{x+w}" y2="{y+h*0.3}" stroke-width="1" stroke-dasharray="3 3"/>'

    def low(x, y):  # looking up: big legs, small head, horizon near the bottom
        cx = x + w/2
        return (f'<line {L} x1="{x}" y1="{y+h*0.92}" x2="{x+w}" y2="{y+h*0.92}" stroke-width="1"/>'
                f'<circle class="f-soft" cx="{cx}" cy="{y+h*0.14}" r="5"/>'
                f'<path {L} d="M{cx},{y+h*0.22} L{cx},{y+h*0.55} M{cx-12},{y+h*0.34} L{cx+12},{y+h*0.34} '
                f'M{cx},{y+h*0.55} L{cx-22},{y+h} M{cx},{y+h*0.55} L{cx+22},{y+h}" stroke-width="3"/>')

    def high(x, y):  # looking down: big head, small feet, floor fills the frame
        cx = x + w/2
        grid = "".join(f'<line class="f-line" x1="{x+k*w/6}" y1="{y}" x2="{x+k*w/6}" y2="{y+h}" stroke-width=".5" style="opacity:.35"/>' for k in range(1, 6))
        return (grid + f'<path {L} d="M{cx},{y+h*0.42} L{cx},{y+h*0.72} M{cx-9},{y+h*0.5} L{cx+9},{y+h*0.5} '
                f'M{cx},{y+h*0.72} L{cx-4},{y+h*0.86} M{cx},{y+h*0.72} L{cx+4},{y+h*0.86}"/>'
                f'<circle class="f-soft" cx="{cx}" cy="{y+h*0.28}" r="10"/>')

    def overhead(x, y):  # straight down: top of head inside shoulders, tiled floor
        cx, cy = x + w/2, y + h/2
        grid = "".join(f'<line class="f-line" x1="{x}" y1="{y+k*h/4}" x2="{x+w}" y2="{y+k*h/4}" stroke-width=".5" style="opacity:.35"/>' for k in range(1, 4))
        grid += "".join(f'<line class="f-line" x1="{x+k*w/7}" y1="{y}" x2="{x+k*w/7}" y2="{y+h}" stroke-width=".5" style="opacity:.35"/>' for k in range(1, 7))
        return grid + f'<ellipse class="f-fill" cx="{cx}" cy="{cy}" rx="18" ry="8" style="stroke:var(--ink)"/><circle class="f-soft" cx="{cx}" cy="{cy}" r="7"/>'

    def dutch(x, y):  # eye level, whole frame content tilted
        return f'<g transform="rotate(-15 {x+w/2} {y+h/2})"><line {L} x1="{x-20}" y1="{y+h*0.3}" x2="{x+w+20}" y2="{y+h*0.3}" stroke-width="1" stroke-dasharray="3 3"/>{person(x + w/2, y + h*0.12, h*1.6)}</g>'

    def ots(x, y):  # back of head and shoulder in the foreground, the other person facing us
        fg = 'style="fill:var(--line);stroke:var(--ink)"'
        return (person(x + w*0.68, y + h*0.14, h*1.5)
                + f'<ellipse cx="{x+w*0.1}" cy="{y+h*1.08}" rx="42" ry="24" {fg}/>'
                + f'<circle cx="{x+w*0.18}" cy="{y+h*0.45}" r="20" {fg}/>')

    def pov(x, y):  # our own forearms reach in from the bottom edge toward what we look at
        def arm(sx, ex):
            return (f'<line x1="{sx}" y1="{y+h+4}" x2="{ex}" y2="{y+h*0.74}" style="stroke:var(--ink)" stroke-width="9" stroke-linecap="round"/>'
                    f'<line x1="{sx}" y1="{y+h+4}" x2="{ex}" y2="{y+h*0.74}" style="stroke:var(--surface)" stroke-width="6.5" stroke-linecap="round"/>')
        return (person(x + w/2, y + h*0.2, h*0.6)
                + f'<line {L} x1="{x}" y1="{y+h*0.55}" x2="{x+w}" y2="{y+h*0.55}" stroke-width="1"/>'
                + arm(x + 14, x + 38) + arm(x + w - 14, x + w - 38))

    panels = [("Eye level", eye), ("Low angle", low), ("High angle", high), ("Overhead", overhead),
              ("Dutch", dutch), ("OTS", ots), ("POV", pov)]
    return panel_strip(panels, "ca", "Camera heights and angles")


def panel_strip(panels, prefix, label, w=112, h=63, gap=12):
    """A row of framed panels with a label under each; draw(x, y) fills one panel."""
    parts = []
    for i, (name, draw) in enumerate(panels):
        x, y = 10 + i * (w + gap), 20
        clip = f"{prefix}{i}"  # ids share the page with other figures
        parts.append(f'<clipPath id="{clip}"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath>')
        parts.append(f'<rect class="f-fill" x="{x}" y="{y}" width="{w}" height="{h}" stroke-width="1" style="stroke:var(--line)"/>')
        parts.append(f'<g clip-path="url(#{clip})">{draw(x, y)}</g>')
        parts.append(f'<text class="f-text" x="{x + w/2}" y="{y + h + 18}" text-anchor="middle" font-weight="600">{name}</text>')
    W = 10 + len(panels) * (w + gap)
    return f'<svg viewBox="0 0 {W} 112" role="img" aria-label="{label}">{"".join(parts)}</svg>'


def composition():
    """The composition rules, one small frame each; orange marks show the rule."""
    w, h = 112, 63
    L = 'class="f-line" stroke-width="2"'
    M = 'style="stroke:var(--mark);fill:none" stroke-width="1.2"'

    def thirds(x, y):
        grid = "".join(f'<line x1="{x+k*w/3}" y1="{y}" x2="{x+k*w/3}" y2="{y+h}" {M} stroke-dasharray="3 3"/>'
                       f'<line x1="{x}" y1="{y+k*h/3}" x2="{x+w}" y2="{y+k*h/3}" {M} stroke-dasharray="3 3"/>' for k in (1, 2))
        return grid + person(x + w/3, y + h/3 - h*0.11*1.6*1.1, h*1.6)  # eyes on the top third line

    def lead_room(x, y):  # profile looking right, with space in front of the face
        hx, hy = x + w*0.28, y + h*0.4
        return (f'<path {L} d="M{hx},{hy+9} L{hx},{y+h} M{hx-16},{y+h*0.78} L{hx+16},{y+h*0.78}"/>'
                f'<circle class="f-soft" cx="{hx}" cy="{hy}" r="9"/>'
                f'<path class="f-soft" d="M{hx+8},{hy-3} L{hx+13},{hy+1} L{hx+8},{hy+3} Z"/>'
                f'<line x1="{hx+18}" y1="{hy}" x2="{x+w-8}" y2="{hy}" {M} stroke-dasharray="3 3" marker-end="url(#cmp-arrow)"/>')

    def headroom(x, y):  # small, marked gap between head top and frame top
        top = y + h*0.16
        return (person(x + w/2, top, h*1.6)
                + f'<path d="M{x+w/2+16},{y+1} L{x+w/2+16},{top} M{x+w/2+12},{y+1} L{x+w/2+20},{y+1} M{x+w/2+12},{top} L{x+w/2+20},{top}" {M}/>')

    def depth(x, y):  # background hills, middle-ground person, foreground glass out of focus
        return (f'<path class="f-line" stroke-width="1" style="opacity:.5" d="M{x},{y+h*0.5} L{x+w*0.3},{y+h*0.3} L{x+w*0.55},{y+h*0.48} L{x+w*0.8},{y+h*0.25} L{x+w},{y+h*0.42}"/>'
                + person(x + w*0.6, y + h*0.32, h*0.75)
                + f'<path d="M{x+4},{y+h*0.4} L{x+30},{y+h*0.4} L{x+26},{y+h+2} L{x+8},{y+h+2} Z" style="fill:var(--line);stroke:var(--ink);opacity:.8"/>')

    def leading(x, y):  # road edges converge on the subject
        vx, vy = x + w*0.62, y + h*0.42
        return (f'<line class="f-line" x1="{x}" y1="{vy}" x2="{x+w}" y2="{vy}" stroke-width="1" style="opacity:.5"/>'
                f'<path {L} stroke-width="1.5" d="M{x+4},{y+h} L{vx},{vy} M{x+w-2},{y+h} L{vx},{vy}"/>'
                f'<path {M} stroke-dasharray="3 3" d="M{x+w*0.3},{y+h} L{vx},{vy+2}"/>'
                + person(vx, vy - 14, 14))

    def symmetry(x, y):  # corridor with a centred door and a centred person
        cx = x + w/2
        return (f'<path class="f-line" stroke-width="1" d="M{x},{y} L{cx-16},{y+h*0.3} L{cx-16},{y+h*0.78} L{x},{y+h} '
                f'M{x+w},{y} L{cx+16},{y+h*0.3} L{cx+16},{y+h*0.78} L{x+w},{y+h} M{cx-16},{y+h*0.3} L{cx+16},{y+h*0.3}"/>'
                f'<line x1="{cx}" y1="{y}" x2="{cx}" y2="{y+h}" {M} stroke-dasharray="3 3"/>'
                + person(cx, y + h*0.38, h*0.4))

    def negative(x, y):  # tiny subject in a corner, the rest empty
        return (f'<line class="f-line" x1="{x}" y1="{y+h*0.88}" x2="{x+w}" y2="{y+h*0.88}" stroke-width="1"/>'
                + person(x + w*0.82, y + h*0.68, h*0.2))

    panels = [("Rule of thirds", thirds), ("Lead room", lead_room), ("Headroom", headroom), ("Depth layers", depth),
              ("Leading lines", leading), ("Symmetry", symmetry), ("Negative space", negative)]
    arrow = ('<defs><marker id="cmp-arrow" viewBox="0 0 6 6" refX="5" refY="3" markerWidth="6" markerHeight="6" orient="auto">'
             '<path d="M0,0 L6,3 L0,6 Z" style="fill:var(--mark)"/></marker></defs>')
    return panel_strip(panels, "cmp", "Composition rules").replace('">', '">' + arrow, 1)


def shots_by_content():
    """Shot names by what is in the frame, same panel style as shot_sizes."""
    w, h = 112, 63
    L = 'class="f-line" stroke-width="2"'

    def single(x, y):
        return person(x + w/2, y + h*0.12, h*1.6)

    def two(x, y):
        return person(x + w*0.32, y + h*0.14, h*1.5) + person(x + w*0.68, y + h*0.14, h*1.5)

    def group(x, y):
        return "".join(person(x + w*f, y + h*t, h*0.7) for f, t in
                       [(0.18, 0.28), (0.38, 0.22), (0.62, 0.22), (0.82, 0.28), (0.5, 0.36)])

    def insert(x, y):  # a finger on a phone screen
        return (f'<rect class="f-fill" x="{x+w*0.3}" y="{y+6}" width="{w*0.4}" height="{h+10}" rx="6" style="stroke:var(--ink)" stroke-width="2"/>'
                + "".join(f'<rect class="f-soft" x="{x+w*0.36}" y="{y+14+k*11}" width="{w*0.28}" height="7" rx="2"/>' for k in range(3))
                + f'<line x1="{x+w}" y1="{y+h+4}" x2="{x+w*0.56}" y2="{y+h*0.62}" style="stroke:var(--ink)" stroke-width="11" stroke-linecap="round"/>'
                + f'<line x1="{x+w}" y1="{y+h+4}" x2="{x+w*0.56}" y2="{y+h*0.62}" style="stroke:var(--surface)" stroke-width="8" stroke-linecap="round"/>')

    def cutaway(x, y):  # a wall clock
        cx, cy = x + w/2, y + h/2
        ticks = "".join(f'<line class="f-line" x1="{cx+20*math.cos(a):.1f}" y1="{cy+20*math.sin(a):.1f}" x2="{cx+24*math.cos(a):.1f}" y2="{cy+24*math.sin(a):.1f}" stroke-width="1.5"/>'
                        for a in [k*math.pi/6 for k in range(12)])
        return (f'<circle class="f-fill" cx="{cx}" cy="{cy}" r="26" style="stroke:var(--ink)" stroke-width="2"/>' + ticks
                + f'<path {L} d="M{cx},{cy} L{cx},{cy-17} M{cx},{cy} L{cx+12},{cy+5}"/>')

    def reaction(x, y):  # close-up of a listener, surprised
        cx, cy = x + w/2, y + h*0.5
        return (f'<circle class="f-soft" cx="{cx}" cy="{cy}" r="27"/>'
                f'<circle cx="{cx-9}" cy="{cy-5}" r="2.5" style="fill:var(--ink)"/><circle cx="{cx+9}" cy="{cy-5}" r="2.5" style="fill:var(--ink)"/>'
                f'<path class="f-line" stroke-width="1.5" d="M{cx-14},{cy-13} Q{cx-9},{cy-17} {cx-4},{cy-13} M{cx+4},{cy-13} Q{cx+9},{cy-17} {cx+14},{cy-13}"/>'
                f'<ellipse class="f-line" cx="{cx}" cy="{cy+10}" rx="4" ry="5" stroke-width="1.5"/>')

    panels = [("Single", single), ("Two-shot", two), ("Group", group), ("Insert", insert),
              ("Cutaway", cutaway), ("Reaction", reaction)]
    return panel_strip(panels, "sbc", "Shots named by content")


def viewer_looks():
    """What pulls the eye first; in each frame one element wins (marked in orange)."""
    w, h = 112, 63

    def ring(cx, cy, r):
        return f'<circle cx="{cx}" cy="{cy}" r="{r}" style="stroke:var(--mark);fill:none" stroke-width="1.5" stroke-dasharray="3 2"/>'

    def boxes(x, y, skip=None, style='style="fill:var(--muted);opacity:.35"'):
        spots = [(0.18, 0.35), (0.42, 0.62), (0.7, 0.3), (0.85, 0.68)]
        return "".join(f'<rect x="{x+w*a-8}" y="{y+h*b-8}" width="16" height="16" rx="3" {style}/>'
                       for i, (a, b) in enumerate(spots) if i != skip)

    def face(x, y):
        cx, cy = x + w*0.7, y + h*0.3
        return (boxes(x, y, skip=2) + f'<circle class="f-soft" cx="{cx}" cy="{cy}" r="10"/>'
                f'<circle cx="{cx-3.5}" cy="{cy-1}" r="1.4" style="fill:var(--ink)"/><circle cx="{cx+3.5}" cy="{cy-1}" r="1.4" style="fill:var(--ink)"/>'
                + ring(cx, cy, 15))

    def bright(x, y):  # a "photo": fixed dark tones so it reads the same in both themes
        cx, cy = x + w*0.42, y + h*0.62
        return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" style="fill:#3a3f44"/>'
                + boxes(x, y, skip=1, style='style="fill:#5a6168"') + f'<circle cx="{cx}" cy="{cy}" r="9" style="fill:#fff6d8"/>' + ring(cx, cy, 15))

    def contrast(x, y):
        cx, cy = x + w*0.18, y + h*0.35
        return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" style="fill:#c9ccd0"/>'
                + boxes(x, y, skip=0, style='style="fill:#b3b7bc"') + f'<rect x="{cx-8}" y="{cy-8}" width="16" height="16" rx="3" style="fill:#16191c"/>' + ring(cx, cy, 15))

    def focus(x, y):
        cx, cy = x + w*0.85, y + h*0.68
        soft = boxes(x, y, skip=3, style='style="fill:var(--ink);opacity:.45"')
        return (f'<g filter="url(#vl-blur)">{soft}</g>'
                f'<rect x="{cx-8}" y="{cy-8}" width="16" height="16" rx="3" style="fill:var(--ink)"/>' + ring(cx, cy, 15))

    def warm(x, y):
        cx, cy = x + w*0.42, y + h*0.62
        return (boxes(x, y, skip=1, style='style="fill:#6f8fa8;opacity:.6"')
                + f'<rect x="{cx-8}" y="{cy-8}" width="16" height="16" rx="3" style="fill:var(--mark)"/>' + ring(cx, cy, 15))

    def movement(x, y):
        cx, cy = x + w*0.7, y + h*0.3
        trail = "".join(f'<line x1="{cx-14-k*7}" y1="{cy-4+k*4}" x2="{cx-24-k*7}" y2="{cy-4+k*4}" style="stroke:var(--ink)" stroke-width="1.2"/>' for k in range(3))
        return (boxes(x, y, skip=2) + trail + f'<rect x="{cx-8}" y="{cy-8}" width="16" height="16" rx="3" style="fill:var(--muted)"/>' + ring(cx, cy, 15))

    panels = [("Face, eyes", face), ("Brightest", bright), ("Contrast", contrast), ("Sharp focus", focus),
              ("Warm color", warm), ("Movement", movement)]
    blur = '<defs><filter id="vl-blur"><feGaussianBlur stdDeviation="2.2"/></filter></defs>'
    return panel_strip(panels, "vl", "What the eye goes to first").replace('">', '">' + blur, 1)


def aspect_ratios():
    """Common delivery ratios at the same height, then what a 16:9 to 9:16 crop does."""
    h, y, gap = 72, 20, 14
    ratios = [("16:9", 16/9, "YouTube, TV"), ("9:16", 9/16, "Shorts, Reels"), ("2.39:1", 2.39, "cinema"),
              ("1:1", 1, "feeds"), ("4:5", 4/5, "feeds")]
    p, x = [], 10
    for i, (name, r, use) in enumerate(ratios):
        w = h * r
        p.append(f'<rect class="f-fill" x="{x}" y="{y}" width="{w:.1f}" height="{h}" style="stroke:var(--ink)" stroke-width="1.5"/>')
        p.append(f'<clipPath id="ar{i}"><rect x="{x}" y="{y}" width="{w:.1f}" height="{h}"/></clipPath>')
        p.append(f'<g clip-path="url(#ar{i})">{person(x + w/2, y + h*0.14, h*1.4)}</g>')  # same subject, same size
        p.append(f'<text class="f-text" x="{x + w/2:.1f}" y="{y + h + 18}" text-anchor="middle" font-weight="600">{name}</text>')
        p.append(f'<text class="f-mute" x="{x + w/2:.1f}" y="{y + h + 32}" text-anchor="middle">{use}</text>')
        x += w + gap
    # the crop: a 16:9 two-shot with the centre 9:16 window that a vertical edit keeps
    x += 16
    w = h * 16/9
    cw = h * 9/16
    p.append(f'<rect class="f-fill" x="{x}" y="{y}" width="{w:.1f}" height="{h}" style="stroke:var(--ink)" stroke-width="1.5"/>')
    p.append(f'<clipPath id="ar-c"><rect x="{x}" y="{y}" width="{w:.1f}" height="{h}"/></clipPath>')
    p.append(f'<g clip-path="url(#ar-c)">{person(x + w*0.22, y + h*0.14, h*1.4)}{person(x + w*0.78, y + h*0.14, h*1.4)}</g>')
    p.append(f'<rect x="{x}" y="{y}" width="{(w-cw)/2:.1f}" height="{h}" style="fill:var(--ink);opacity:.18"/>')
    p.append(f'<rect x="{x + (w+cw)/2:.1f}" y="{y}" width="{(w-cw)/2:.1f}" height="{h}" style="fill:var(--ink);opacity:.18"/>')
    p.append(f'<rect x="{x + (w-cw)/2:.1f}" y="{y}" width="{cw:.1f}" height="{h}" style="stroke:var(--bad);fill:none" stroke-width="2" stroke-dasharray="4 3"/>')
    p.append(f'<text class="f-text" x="{x + w/2:.1f}" y="{y + h + 18}" text-anchor="middle" font-weight="600">16:9 cropped to 9:16</text>')
    p.append(f'<text class="f-mute" x="{x + w/2:.1f}" y="{y + h + 32}" text-anchor="middle">both people cut out</text>')
    W = x + w + 30
    return f'<svg viewBox="0 0 {W:.0f} 130" role="img" aria-label="Aspect ratios">{"".join(p)}</svg>'


def safe_areas():
    """Vertical video: where the platform interface covers the picture; TV: title-safe area."""
    p = ['<svg viewBox="0 0 520 300" role="img" aria-label="Safe areas for vertical video and TV">']
    cover = 'style="fill:var(--mark);opacity:.22"'
    # 9:16 phone frame
    x, y, w, h = 40, 16, 117, 208
    p.append(f'<rect class="f-fill" x="{x}" y="{y}" width="{w}" height="{h}" rx="8" style="stroke:var(--ink)" stroke-width="2"/>')
    p.append(f'<rect x="{x}" y="{y + h*0.78}" width="{w}" height="{h*0.22}" {cover}/>')
    p.append(f'<rect x="{x + w*0.8}" y="{y + h*0.42}" width="{w*0.2}" height="{h*0.36}" {cover}/>')
    p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h*0.08}" {cover}/>')
    for k in range(4):
        p.append(f'<circle cx="{x + w*0.9}" cy="{y + h*0.47 + k*17}" r="5" style="fill:var(--mark);opacity:.7"/>')
    p.append(f'<rect class="f-soft" x="{x + 8}" y="{y + h*0.83}" width="{w*0.55}" height="6" rx="2"/><rect class="f-soft" x="{x + 8}" y="{y + h*0.88}" width="{w*0.4}" height="6" rx="2"/>')
    p.append(f'<rect x="{x + 6}" y="{y + h*0.1}" width="{w*0.72}" height="{h*0.66}" style="stroke:var(--accent);fill:none" stroke-width="1.5" stroke-dasharray="4 3"/>')
    p.append(person(x + w*0.42, y + h*0.2, h*0.5))
    p.append(f'<text class="f-text" x="{x + w/2}" y="{y + h + 20}" text-anchor="middle" font-weight="600">9:16 vertical</text>')
    # legend
    lx = 190
    p.append(f'<rect x="{lx}" y="40" width="14" height="14" {cover}/><text class="f-text" x="{lx + 22}" y="51">covered by buttons, captions, names</text>')
    p.append(f'<rect x="{lx}" y="64" width="14" height="14" style="stroke:var(--accent);fill:none" stroke-dasharray="4 3"/><text class="f-text" x="{lx + 22}" y="75">safe area: faces, text, product</text>')
    # 16:9 TV with title-safe at 90 %
    x, y, w = 190, 100, 290
    h = w * 9/16
    p.append(f'<rect class="f-fill" x="{x}" y="{y}" width="{w}" height="{h:.1f}" style="stroke:var(--ink)" stroke-width="2"/>')
    p.append(f'<rect x="{x + w*0.05}" y="{y + h*0.05:.1f}" width="{w*0.9}" height="{h*0.9:.1f}" style="stroke:var(--accent);fill:none" stroke-width="1.5" stroke-dasharray="4 3"/>')
    p.append(f'<text class="f-mute" x="{x + w*0.05 + 6}" y="{y + h*0.05 + 14:.1f}">title-safe ≈ 90 %</text>')
    p.append(f'<rect class="f-soft" x="{x + w*0.08}" y="{y + h*0.74:.1f}" width="{w*0.42}" height="12" rx="2"/>')
    p.append(person(x + w*0.68, y + h*0.2, h*0.65))
    p.append(f'<text class="f-text" x="{x + w/2}" y="{y + h + 20:.1f}" text-anchor="middle" font-weight="600">16:9 TV</text>')
    p.append("</svg>")
    return "".join(p)


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


FIGS = {"shot-sizes.svg": shot_sizes, "camera-angles.svg": camera_angles, "composition.svg": composition, "shots-content.svg": shots_by_content, "viewer-looks.svg": viewer_looks,
        "aspect-ratios.svg": aspect_ratios, "safe-areas.svg": safe_areas, "three-point.svg": three_point, "rule-180.svg": rule_180,
        "denoise.svg": denoise, "local-cloud.svg": local_cloud}

if __name__ == "__main__":
    for name, fn in FIGS.items():
        (OUT / name).write_text(fn())
        print("wrote", name)
