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
    # max-width keeps short strips at the same panel size as long ones
    return f'<svg viewBox="0 0 {W} 112" style="max-width:{W}px" role="img" aria-label="{label}">{"".join(parts)}</svg>'


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


# ---------------------------------------------------------------- C02 helpers

def arrow_defs(mid, color="var(--ink)"):
    """An arrowhead marker; mid must be unique on the page."""
    return (f'<defs><marker id="{mid}" viewBox="0 0 6 6" refX="5" refY="3" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
            f'<path d="M0,0 L6,3 L0,6 Z" style="fill:{color}"/></marker></defs>')


def with_defs(svg, defs):
    """Insert defs right after the opening <svg ...> tag."""
    i = svg.index(">") + 1
    return svg[:i] + defs + svg[i:]


def ok_mark(x, y):
    return f'<path d="M{x-5},{y} L{x-1},{y+4} L{x+6},{y-5}" style="stroke:var(--ok);fill:none" stroke-width="2.2" stroke-linecap="round"/>'


def bad_mark(x, y):
    return f'<path d="M{x-5},{y-5} L{x+5},{y+5} M{x+5},{y-5} L{x-5},{y+5}" style="stroke:var(--bad);fill:none" stroke-width="2.2" stroke-linecap="round"/>'


def camera_top(x, y, deg=-90):
    """Camera seen from above at (x, y), lens pointing in direction deg (-90 = up)."""
    return (f'<g transform="translate({x} {y}) rotate({deg + 90})">'
            f'<rect x="-7" y="-4" width="14" height="10" rx="1.5" style="fill:var(--surface);stroke:var(--ink)" stroke-width="1.5"/>'
            f'<path d="M-4,-4 L-6,-9 L6,-9 L4,-4 Z" style="fill:var(--ink)"/></g>')


def tree(cx, base, s):
    return (f'<line x1="{cx}" y1="{base}" x2="{cx}" y2="{base - s*0.55}" style="stroke:var(--muted)" stroke-width="{max(1, s/14):.1f}"/>'
            f'<circle cx="{cx}" cy="{base - s*0.72}" r="{s*0.3:.1f}" style="fill:var(--muted);opacity:.45"/>')


def head_shoulders(cx, cy, r=12, rx=None):
    """MCU subject: head and shoulders, head centre at cy."""
    rx = rx or r
    return (f'<path d="M{cx-r*2.6},{cy+r*3.2} Q{cx-r*2.4},{cy+r*1.4} {cx},{cy+r*1.3} Q{cx+r*2.4},{cy+r*1.4} {cx+r*2.6},{cy+r*3.2} Z" class="f-fill" style="stroke:var(--ink)" stroke-width="1.5"/>'
            f'<ellipse class="f-soft" cx="{cx}" cy="{cy}" rx="{rx}" ry="{r}"/>')


# ---------------------------------------------------------------- C02·M02 lens and movement

def focal_length():
    """Same face size, different lens: the background grows and narrows as the lens gets longer."""
    w, h = 112, 63

    def lens(trees, blur, face_rx, lines):
        def draw(x, y):
            bg = "".join(tree(x + w*f, y + h*base, s) for f, base, s in trees)
            if blur:
                bg = f'<g filter="url(#fl-blur)">{bg}</g>'
            pers = ""
            if lines:  # strong converging floor lines in a wide lens
                pers = f'<path class="f-line" stroke-width="1" style="opacity:.5" d="M{x},{y+h} L{x+w/2-6},{y+h*0.5} M{x+w},{y+h} L{x+w/2+6},{y+h*0.5}"/>'
            return bg + pers + head_shoulders(x + w/2, y + h*0.45, 12, face_rx)
        return draw

    panels = [("Wide 24 mm", lens([(0.12, 0.5, 12), (0.25, 0.5, 10), (0.75, 0.5, 10), (0.88, 0.5, 12)], False, 14, True)),
              ("Normal 50 mm", lens([(0.15, 0.62, 22), (0.85, 0.62, 22)], False, 12, False)),
              ("Portrait 85 mm", lens([(0.12, 0.85, 40), (0.9, 0.85, 40)], True, 12, False)),
              ("Telephoto 135 mm+", lens([(0.05, 1.3, 90), (0.98, 1.3, 90)], True, 12, False))]
    blur = '<defs><filter id="fl-blur"><feGaussianBlur stdDeviation="1.8"/></filter></defs>'
    return with_defs(panel_strip(panels, "fl", "Focal length and background"), blur)


def depth_of_field():
    w, h = 112, 63

    def scene(sharp_fg, sharp_bg):
        def draw(x, y):
            bg = tree(x + w*0.75, y + h*0.8, 34) + tree(x + w*0.92, y + h*0.8, 28)
            fg = head_shoulders(x + w*0.32, y + h*0.42, 12)
            bg = bg if sharp_bg else f'<g filter="url(#dof-blur)">{bg}</g>'
            fg = fg if sharp_fg else f'<g filter="url(#dof-blur)">{fg}</g>'
            return bg + fg
        return draw

    def rack(x, y):
        return (scene(True, False)(x, y)
                + f'<path d="M{x+w*0.45},{y+10} Q{x+w*0.62},{y+2} {x+w*0.74},{y+14}" style="stroke:var(--mark);fill:none" stroke-width="1.5" marker-end="url(#dof-arrow)"/>')

    panels = [("Shallow DOF", scene(True, False)), ("Deep DOF", scene(True, True)),
              ("Rack focus: start", rack), ("Rack focus: end", scene(False, True))]
    defs = ('<defs><filter id="dof-blur"><feGaussianBlur stdDeviation="2.4"/></filter></defs>' + arrow_defs("dof-arrow", "var(--mark)"))
    return with_defs(panel_strip(panels, "dof", "Depth of field"), defs)


def camera_moves():
    """Top view of each move: camera, subject, and the path of the camera."""
    w, h = 112, 63
    A = 'style="stroke:var(--mark);fill:none" stroke-width="1.8" marker-end="url(#cm-arrow)"'

    def subj(x, y, cx=None, cy=None):
        return f'<circle class="f-soft" cx="{cx or x + w/2}" cy="{cy or y + h*0.28}" r="7"/>'

    def push(x, y):
        return subj(x, y) + camera_top(x + w/2, y + h*0.85) + f'<line x1="{x+w/2}" y1="{y+h*0.72}" x2="{x+w/2}" y2="{y+h*0.5}" {A}/>'

    def pull(x, y):
        return subj(x, y) + camera_top(x + w/2, y + h*0.62) + f'<line x1="{x+w/2}" y1="{y+h*0.76}" x2="{x+w/2}" y2="{y+h*0.95}" {A}/>'

    def pan(x, y):
        cx, cy = x + w/2, y + h*0.8
        return (subj(x, y, x + w*0.25) + subj(x, y, x + w*0.75) + camera_top(cx, cy, -120)
                + f'<path d="M{cx-14},{cy-16} A20,20 0 0 1 {cx+14},{cy-16}" {A}/>')

    def tilt(x, y):  # side view: camera on the ground line, lens swings up
        cx, cy = x + w*0.3, y + h*0.7
        return (f'<line class="f-line" x1="{x}" y1="{y+h*0.85}" x2="{x+w}" y2="{y+h*0.85}" stroke-width="1"/>'
                f'<rect x="{cx-8}" y="{cy-5}" width="16" height="10" rx="1.5" style="fill:var(--surface);stroke:var(--ink)" stroke-width="1.5"/>'
                f'<path d="M{cx+20},{cy} A20,20 0 0 0 {cx+14},{cy-14}" {A}/>'
                f'<text class="f-mute" x="{x+w-6}" y="{y+12}" text-anchor="end">side view</text>')

    def track(x, y):
        return (subj(x, y, x + w*0.45, y + h*0.3) + f'<line x1="{x+w*0.55}" y1="{y+h*0.3}" x2="{x+w*0.8}" y2="{y+h*0.3}" style="stroke:var(--muted)" stroke-dasharray="2 2"/>'
                + camera_top(x + w*0.3, y + h*0.78) + f'<line x1="{x+w*0.42}" y1="{y+h*0.78}" x2="{x+w*0.7}" y2="{y+h*0.78}" {A}/>')

    def orbit(x, y):
        cx, cy = x + w/2, y + h*0.45
        return (subj(x, y, cx, cy) + camera_top(cx, cy + 22) + f'<path d="M{cx+12},{cy+20} A24,22 0 0 0 {cx+22},{cy-10}" {A}/>'
                f'<ellipse cx="{cx}" cy="{cy}" rx="24" ry="22" style="stroke:var(--muted);fill:none" stroke-dasharray="2 3"/>')

    def crane(x, y):  # side view: camera rises
        cx = x + w*0.3
        return (f'<line class="f-line" x1="{x}" y1="{y+h*0.85}" x2="{x+w}" y2="{y+h*0.85}" stroke-width="1"/>'
                + person(x + w*0.75, y + h*0.45, h*0.4)
                + f'<rect x="{cx-8}" y="{y+h*0.62}" width="16" height="10" rx="1.5" style="fill:var(--surface);stroke:var(--ink)" stroke-width="1.5"/>'
                f'<line x1="{cx}" y1="{y+h*0.55}" x2="{cx}" y2="{y+h*0.15}" {A}/>'
                f'<text class="f-mute" x="{x+w-6}" y="{y+12}" text-anchor="end">side view</text>')

    def handheld(x, y):
        pts = " ".join(f"{x + w*0.2 + i*6},{y + h*0.75 + (3 if i % 2 else -3) * (1 + (i % 3) / 2)}" for i in range(11))
        return subj(x, y) + f'<polyline points="{pts}" style="stroke:var(--mark);fill:none" stroke-width="1.5"/>'

    panels = [("Push-in", push), ("Pull-out", pull), ("Pan", pan), ("Tilt", tilt),
              ("Track", track), ("Orbit", orbit), ("Crane up", crane), ("Handheld", handheld)]
    return with_defs(panel_strip(panels, "cm", "Camera moves, top view"), arrow_defs("cm-arrow", "var(--mark)"))


def stabilization():
    """The path the frame centre draws over a few seconds."""
    w, h = 112, 63

    def gimbal(x, y):
        return f'<path d="M{x+10},{y+h*0.65} C{x+40},{y+h*0.35} {x+70},{y+h*0.35} {x+w-10},{y+h*0.55}" style="stroke:var(--mark);fill:none" stroke-width="2"/>'

    def hand(x, y):
        rnd = random.Random(3)
        pts = " ".join(f"{x + 10 + i*4.6:.1f},{y + h*0.55 + rnd.uniform(-7, 7):.1f}" for i in range(21))
        return f'<polyline points="{pts}" style="stroke:var(--mark);fill:none" stroke-width="1.5" stroke-linejoin="round"/>'

    def locked(x, y):
        cx, cy = x + w/2, y + h*0.42
        return (f'<circle cx="{cx}" cy="{cy}" r="4" style="fill:var(--mark)"/>'
                f'<path class="f-line" stroke-width="1.5" d="M{cx},{cy+8} L{cx-14},{y+h-6} M{cx},{cy+8} L{cx+14},{y+h-6} M{cx},{cy+8} L{cx},{y+h-6}"/>')

    panels = [("Gimbal, dolly", gimbal), ("Handheld", hand), ("Locked-off", locked)]
    return panel_strip(panels, "stb", "Camera path: stabilized, handheld, locked-off")


def shutter():
    """A ball moving right during one frame: the shutter time sets the blur."""
    w, h = 112, 63

    def ball(blur_len, ghosts=False):
        def draw(x, y):
            cy = y + h/2
            if ghosts:  # short shutter: sharp, with gaps between frames
                return "".join(f'<circle cx="{x + 18 + k*26}" cy="{cy}" r="7" style="fill:var(--accent);opacity:{0.25 + 0.25*k}"/>' for k in range(4))
            x0 = x + w/2 - blur_len/2
            return (f'<rect x="{x0}" y="{cy-7}" width="{blur_len}" height="14" rx="7" style="fill:var(--accent);opacity:.35"/>'
                    f'<circle cx="{x0 + blur_len - 7}" cy="{cy}" r="7" style="fill:var(--accent)"/>')
        return draw

    panels = [("Short 1/500 s", ball(0, True)), ("180° 1/48 s", ball(34)), ("Long 1/25 s", ball(80))]
    return panel_strip(panels, "sh", "Shutter time and motion blur at 24 fps")


def parallax():
    """Top view: the camera moves sideways; near objects cross the frame faster than far ones."""
    p = ['<svg viewBox="0 0 520 220" role="img" aria-label="Parallax, top view">', arrow_defs("px-arrow", "var(--mark)"),
         '<text class="f-mute" x="16" y="22">TOP VIEW</text>']
    p.append('<path d="M60,40 L130,20 L200,46 L280,18 L360,42 L440,22 L480,40" class="f-line" stroke-width="1.5" style="opacity:.6"/>')
    p.append('<line x1="300" y1="44" x2="330" y2="44" style="stroke:var(--mark)" stroke-width="2" marker-end="url(#px-arrow)"/>')  # short: slow in frame
    p.append('<circle class="f-soft" cx="260" cy="100" r="12"/><text class="f-mute" x="278" y="104">subject</text>')
    p.append('<rect x="190" y="140" width="22" height="22" style="fill:var(--ink)"/>')
    p.append('<line x1="220" y1="151" x2="300" y2="151" style="stroke:var(--mark)" stroke-width="2" marker-end="url(#px-arrow)"/>')
    p.append(camera_top(230, 196))
    p.append('<line x1="250" y1="196" x2="300" y2="196" style="stroke:var(--ink)" stroke-width="1.5" marker-end="url(#px-arrow)"/>')
    p.append('<text class="f-text" x="310" y="200">camera moves right</text>')
    p.append('<text class="f-mute" x="310" y="155">near pillar: crosses the frame fast</text>')
    p.append('<text class="f-mute" x="340" y="48">far hills: move a little</text>')
    p.append("</svg>")
    return "".join(p)


def hard_moves():
    """Moves that make the model invent unseen space; top views."""
    w, h = 112, 63
    A = 'style="stroke:var(--bad);fill:none" stroke-width="1.8" marker-end="url(#hm-arrow)"'

    def orbit(x, y):
        cx, cy = x + w/2, y + h*0.45
        return (f'<circle class="f-soft" cx="{cx}" cy="{cy}" r="8"/>' + camera_top(cx, cy + 22)
                + f'<path d="M{cx+10},{cy+21} A24,22 0 1 0 {cx-14},{cy+19}" {A}/>'
                f'<text class="f-text" x="{cx}" y="{cy-14}" text-anchor="middle" font-weight="600" style="fill:var(--bad)">?</text>')

    def door(x, y):
        return (f'<path class="f-line" stroke-width="3" d="M{x},{y+h*0.4} L{x+w*0.42},{y+h*0.4} M{x+w*0.58},{y+h*0.4} L{x+w},{y+h*0.4}"/>'
                + camera_top(x + w/2, y + h*0.85)
                + f'<line x1="{x+w/2}" y1="{y+h*0.72}" x2="{x+w/2}" y2="{y+h*0.12}" {A}/>'
                f'<text class="f-mute" x="{x+w-4}" y="{y+12}" text-anchor="end">new room</text>')

    def combined(x, y):
        cx, cy = x + w/2, y + h*0.7
        return (camera_top(cx, cy)
                + f'<line x1="{cx}" y1="{cy-12}" x2="{cx}" y2="{y+10}" {A}/>'
                f'<path d="M{cx+16},{cy-6} A18,18 0 0 0 {cx+26},{cy-22}" {A}/>'
                f'<line x1="{cx-14}" y1="{cy}" x2="{cx-40}" y2="{cy}" {A}/>')

    def whip(x, y):
        cx, cy = x + w/2, y + h*0.7
        blur = "".join(f'<line x1="{x+12}" y1="{y+12+k*6}" x2="{x+w-12}" y2="{y+12+k*6}" style="stroke:var(--muted);opacity:.5"/>' for k in range(4))
        return blur + camera_top(cx, cy, -150) + f'<path d="M{cx-26},{cy-10} A28,28 0 0 1 {cx+26},{cy-10}" {A}/>'

    panels = [("Long orbit", orbit), ("Through a door", door), ("Combined moves", combined), ("Whip pan", whip)]
    return with_defs(panel_strip(panels, "hm", "Camera moves that are hard for models"), arrow_defs("hm-arrow", "var(--bad)"))


# ---------------------------------------------------------------- C02·M03 light and color

def lit_face(cx, cy, r, gid):
    """A face lit through gradient gid (defined by the caller)."""
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" style="fill:url(#{gid});stroke:var(--ink)" stroke-width="1"/>'
            f'<path d="M{cx-r*1.9},{cy+r*2.4} Q{cx-r*1.8},{cy+r*1.15} {cx},{cy+r*1.1} Q{cx+r*1.8},{cy+r*1.15} {cx+r*1.9},{cy+r*2.4} Z" style="fill:url(#{gid});stroke:var(--ink)" stroke-width="1"/>')


def light_quality():
    """Hard vs soft light, then light direction; a small sun marks the source."""
    w, h = 112, 63
    # "photo" tones stay fixed so the shading reads the same in both themes
    LIT, SHADE = "#f4e9dc", "#4a4440"

    def grad(gid, x1, y1, x2, y2, stops):
        st = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
        return f'<linearGradient id="{gid}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{st}</linearGradient>'

    defs = "<defs>" + "".join([
        grad("lq-hard", 0, 0, 1, 0, [(0, LIT), (0.5, LIT), (0.5, SHADE), (1, SHADE)]),
        grad("lq-soft", 0, 0, 1, 0, [(0, LIT), (0.25, LIT), (0.9, "#8d837b"), (1, "#7a7069")]),
        grad("lq-front", 0, 0, 1, 0, [(0, LIT), (1, LIT)]),
        grad("lq-side", 0, 0, 1, 0, [(0, LIT), (0.45, LIT), (0.62, SHADE), (1, SHADE)]),
        grad("lq-back", 0, 0, 1, 0, [(0, SHADE), (1, SHADE)]),
        grad("lq-top", 0, 0, 0, 1, [(0, LIT), (0.35, LIT), (0.6, SHADE), (1, SHADE)]),
        grad("lq-under", 0, 1, 0, 0, [(0, LIT), (0.35, LIT), (0.6, SHADE), (1, SHADE)]),
    ]) + "</defs>"

    def sun(sx, sy, big=False):
        r = 7 if big else 3.5
        return f'<circle cx="{sx}" cy="{sy}" r="{r}" style="fill:var(--mark)"/>'

    def face(gid, src, big=False, rim=False):
        def draw(x, y):
            cx, cy = x + w/2, y + h*0.42
            out = lit_face(cx, cy, 12, gid)
            if rim:
                out += f'<circle cx="{cx}" cy="{cy}" r="12.5" style="stroke:#ffe9b0;fill:none" stroke-width="2"/>'
            sx, sy = src
            return out + sun(x + w*sx, y + h*sy, big)
        return draw

    panels = [("Hard", face("lq-hard", (0.1, 0.4))), ("Soft", face("lq-soft", (0.1, 0.4), big=True)),
              ("Front", face("lq-front", (0.5, 0.92))), ("Side", face("lq-side", (0.08, 0.42))),
              ("Back", face("lq-back", (0.72, 0.12), rim=True)), ("Top", face("lq-top", (0.5, 0.06))),
              ("Under", face("lq-under", (0.5, 0.97)))]
    return with_defs(panel_strip(panels, "lq", "Light quality and direction"), defs)


def color_temperature():
    """A kelvin scale from fire to shade, with the sources from the table."""
    p = ['<svg viewBox="0 0 640 150" role="img" aria-label="Color temperature scale">']
    stops = [(0, "#ff8a2a"), (0.25, "#ffb46b"), (0.45, "#ffd8a8"), (0.66, "#fff6ec"), (0.85, "#dfe9ff"), (1, "#b9cdff")]
    p.append('<defs><linearGradient id="ct-g" x1="0" x2="1">' + "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops) + '</linearGradient></defs>')
    x0, x1, y = 30, 610, 40
    p.append(f'<rect x="{x0}" y="{y}" width="{x1-x0}" height="26" rx="4" style="fill:url(#ct-g);stroke:var(--line)"/>')
    kmin, kmax = 1800, 7500

    def kx(k):
        return x0 + (k - kmin) / (kmax - kmin) * (x1 - x0)

    marks = [(1900, "candle, fire", 0), (3200, "tungsten", 1), (4000, "golden hour", 0), (5600, "daylight", 1), (7000, "shade, overcast", 0)]
    for k, name, row in marks:
        x = kx(k)
        p.append(f'<line x1="{x:.0f}" y1="{y-6}" x2="{x:.0f}" y2="{y+32}" style="stroke:var(--ink)" stroke-width="1.2"/>')
        p.append(f'<text class="f-text" x="{x:.0f}" y="{y+50+row*28}" text-anchor="middle" font-weight="600">{name}</text>')
        p.append(f'<text class="f-mute" x="{x:.0f}" y="{y+63+row*28}" text-anchor="middle">{k:,} K</text>')
    p.append(f'<text class="f-mute" x="{x0}" y="{y-12}">WARM</text><text class="f-mute" x="{x1}" y="{y-12}" text-anchor="end">COOL</text>')
    p.append("</svg>")
    return "".join(p)


def dynamic_range():
    """Scene brightness from dark to bright; the camera records only a window of it."""
    p = ['<svg viewBox="0 0 640 170" role="img" aria-label="Dynamic range: clipped highlights and crushed shadows">']
    p.append('<defs><linearGradient id="dr-g" x1="0" x2="1"><stop offset="0" stop-color="#000"/><stop offset="1" stop-color="#fff"/></linearGradient></defs>')
    x0, x1, y = 30, 610, 50
    p.append(f'<text class="f-mute" x="{x0}" y="{y-14}">SCENE BRIGHTNESS</text>')
    p.append(f'<rect x="{x0}" y="{y}" width="{x1-x0}" height="24" style="fill:url(#dr-g);stroke:var(--line)"/>')
    r0, r1 = 150, 470  # what the camera records
    p.append(f'<rect x="{x0}" y="{y}" width="{r0-x0}" height="24" style="fill:#000;opacity:.85"/>')
    p.append(f'<rect x="{r1}" y="{y}" width="{x1-r1}" height="24" style="fill:#fff;opacity:.92"/>')
    p.append(f'<rect x="{r0}" y="{y-6}" width="{r1-r0}" height="36" rx="3" style="stroke:var(--accent);fill:none" stroke-width="2"/>')
    p.append(f'<text class="f-text" x="{(r0+r1)/2}" y="{y+52}" text-anchor="middle" font-weight="600">recorded range</text>')
    p.append(f'<text class="f-text" x="{(x0+r0)/2}" y="{y+52}" text-anchor="middle">crushed to black</text>')
    p.append(f'<text class="f-text" x="{(r1+x1)/2}" y="{y+52}" text-anchor="middle">clipped to white</text>')
    for x, name in [(330, "face: expose here"), (545, "window, sky")]:
        p.append(f'<path d="M{x},{y+100} L{x},{y+30}" style="stroke:var(--mark)" stroke-width="1.5" stroke-dasharray="3 2"/>')
        p.append(f'<text class="f-mute" x="{x}" y="{y+114}" text-anchor="middle">{name}</text>')
    p.append("</svg>")
    return "".join(p)


def light_continuity():
    """The window side in the wide shot must be the lit side in the close-up."""
    w, h = 112, 63
    LIT, SHADE = "#f4e9dc", "#4a4440"
    defs = ('<defs><linearGradient id="lc-l" x1="0" x2="1"><stop offset=".45" stop-color="' + LIT + '"/><stop offset=".7" stop-color="' + SHADE + '"/></linearGradient>'
            '<linearGradient id="lc-r" x1="1" x2="0"><stop offset=".45" stop-color="' + LIT + '"/><stop offset=".7" stop-color="' + SHADE + '"/></linearGradient></defs>')

    def wide(x, y):
        return (f'<rect x="{x+8}" y="{y+10}" width="22" height="30" style="fill:#fff2c4;stroke:var(--ink)" stroke-width="1.2"/>'
                f'<line x1="{x+19}" y1="{y+10}" x2="{x+19}" y2="{y+40}" style="stroke:var(--ink)"/>'
                f'<path d="M{x+30},{y+14} L{x+70},{y+30} L{x+70},{y+55} L{x+30},{y+40} Z" style="fill:#ffe9a8;opacity:.45"/>'
                + person(x + w*0.68, y + h*0.2, h*0.7))

    def cu(gid, good):
        def draw(x, y):
            return lit_face(x + w/2, y + h*0.42, 14, gid) + (ok_mark if good else bad_mark)(x + w - 12, y + 12)
        return draw

    panels = [("Wide: window left", wide), ("CU: lit from left", cu("lc-l", True)), ("CU: lit from right", cu("lc-r", False))]
    return with_defs(panel_strip(panels, "lc", "Light continuity between shots"), defs)


def atmosphere():
    """Clear air, light haze (beams and depth), and too much haze."""
    w, h = 112, 63

    def scene(haze):
        def draw(x, y):
            out = ""
            for k, (fx, s) in enumerate([(0.2, 26), (0.85, 30)]):
                op = 1 - haze * 0.5
                out += f'<g style="opacity:{op:.2f}">{tree(x + w*fx, y + h*0.85, s)}</g>'
            out += f'<path d="M{x+w*0.3},{y} L{x+w*0.45},{y} L{x+w*0.7},{y+h} L{x+w*0.45},{y+h} Z" style="fill:#ffe9a8;opacity:{0.15 + haze*0.45:.2f}"/>' if haze else ""
            out += person(x + w*0.55, y + h*0.25, h*0.7)
            if haze:
                out += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" style="fill:#b8b8b8;opacity:{haze*0.55:.2f}"/>'
            return out
        return draw

    panels = [("Clear", scene(0)), ("Light haze", scene(0.35)), ("Too much", scene(1.1))]
    return panel_strip(panels, "at", "Atmosphere: haze makes light visible")


def palette():
    """One project's palette decisions, shown as the four choices from the text."""
    w, h = 112, 63
    COLS = ["#1f6f6b", "#d9963a", "#2f4a37", "#efe9dd"]

    def main(x, y):
        return "".join(f'<rect x="{x+8+k*25}" y="{y+16}" width="22" height="32" rx="3" style="fill:{c};stroke:var(--line)"/>' for k, c in enumerate(COLS))

    def sat(x, y):
        muted = ["#5b7c7a", "#a98d6a"]
        return ("".join(f'<rect x="{x+10+k*22}" y="{y+16}" width="18" height="32" rx="3" style="fill:{c}"/>' for k, c in enumerate(muted))
                + "".join(f'<rect x="{x+60+k*22}" y="{y+16}" width="18" height="32" rx="3" style="fill:{c}"/>' for k, c in enumerate(["#00a39a", "#ff9a1f"]))
                + f'<text class="f-mute" x="{x+30}" y="{y+59}" text-anchor="middle">muted</text><text class="f-mute" x="{x+80}" y="{y+59}" text-anchor="middle">vivid</text>')

    def blacks(x, y):
        return (f'<rect x="{x+10}" y="{y+16}" width="40" height="32" style="fill:#3c3f44"/><rect x="{x+18}" y="{y+24}" width="24" height="16" style="fill:#b9b4aa"/>'
                f'<rect x="{x+62}" y="{y+16}" width="40" height="32" style="fill:#050505"/><rect x="{x+70}" y="{y+24}" width="24" height="16" style="fill:#e8e2d6"/>'
                f'<text class="f-mute" x="{x+30}" y="{y+59}" text-anchor="middle">lifted</text><text class="f-mute" x="{x+82}" y="{y+59}" text-anchor="middle">deep</text>')

    def accent(x, y):
        greys = "".join(f'<rect x="{x+10+k*20}" y="{y+30}" width="14" height="22" rx="2" style="fill:#9aa1a6"/>' for k in range(5) if k != 2)
        return greys + f'<rect x="{x+50}" y="{y+24}" width="14" height="28" rx="2" style="fill:#d9963a;stroke:var(--ink)"/>'

    panels = [("3–5 main colors", main), ("Saturation", sat), ("Contrast", blacks), ("Accent: hero only", accent)]
    return panel_strip(panels, "pl", "Palette and contrast decisions")


def vectorscope():
    """Vectorscope: hue is the angle, saturation the distance; skin of every color falls near one line."""
    p = ['<svg viewBox="0 0 560 260" role="img" aria-label="Vectorscope with the skin-tone line">']
    cx, cy, R = 150, 130, 105
    p.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" style="fill:#16191c;stroke:var(--ink)" stroke-width="1.5"/>')
    p.append(f'<line x1="{cx-R}" y1="{cy}" x2="{cx+R}" y2="{cy}" style="stroke:#555"/><line x1="{cx}" y1="{cy-R}" x2="{cx}" y2="{cy+R}" style="stroke:#555"/>')
    # standard Rec.709 target angles (degrees counter-clockwise from 3 o'clock)
    targets = [("R", 103.5, "#ff5a5a"), ("Mg", 60.8, "#ff5aff"), ("B", 347.0, "#6a8cff"),
               ("Cy", 283.5, "#5affff"), ("G", 240.8, "#5aff6a"), ("Yl", 167.0, "#ffff5a")]
    for name, a, c in targets:
        t = math.radians(a)
        x, y = cx + R*0.75*math.cos(t), cy - R*0.75*math.sin(t)
        p.append(f'<rect x="{x-6:.1f}" y="{y-6:.1f}" width="12" height="12" style="stroke:{c};fill:none" stroke-width="1.5"/>')
        p.append(f'<text x="{cx + R*0.92*math.cos(t):.1f}" y="{cy - R*0.92*math.sin(t) + 4:.1f}" text-anchor="middle" style="fill:{c};font:11px var(--f-mono, monospace)">{name}</text>')
    t = math.radians(123)
    p.append(f'<line x1="{cx}" y1="{cy}" x2="{cx + R*math.cos(t):.1f}" y2="{cy - R*math.sin(t):.1f}" style="stroke:#f0a640" stroke-width="2"/>')
    rnd = random.Random(5)
    for _ in range(60):  # skin samples of many tones, all near the line
        d = rnd.uniform(0.12, 0.55) * R
        a = math.radians(123 + rnd.gauss(0, 3))
        p.append(f'<circle cx="{cx + d*math.cos(a):.1f}" cy="{cy - d*math.sin(a):.1f}" r="1.6" style="fill:#f6d2b0;opacity:.8"/>')
    p.append('<text class="f-text" x="285" y="80" font-weight="600">Skin-tone line</text>')
    p.append('<text class="f-mute" x="285" y="98">skin of every color falls near it:</text>')
    p.append('<text class="f-mute" x="285" y="114">the distance from the centre varies,</text>')
    p.append('<text class="f-mute" x="285" y="130">the angle stays the same</text>')
    p.append('<text class="f-mute" x="285" y="170">angle = hue, distance = saturation</text>')
    p.append("</svg>")
    return "".join(p)


# ---------------------------------------------------------------- C02·M04 continuity and cutting

def profile(cx, cy, r, right=True):
    """A head in profile with a nose pointing frame right (or left), plus shoulders."""
    s = 1 if right else -1
    return (f'<path class="f-fill" style="stroke:var(--ink)" stroke-width="1.5" d="M{cx-r*2.2},{cy+r*3} Q{cx-r*2},{cy+r*1.3} {cx},{cy+r*1.2} Q{cx+r*2},{cy+r*1.3} {cx+r*2.2},{cy+r*3} Z"/>'
            f'<circle class="f-soft" cx="{cx}" cy="{cy}" r="{r}"/>'
            f'<path class="f-soft" d="M{cx + s*r*0.85},{cy-r*0.35} L{cx + s*r*1.35},{cy+r*0.1} L{cx + s*r*0.85},{cy+r*0.4} Z"/>')


def eyeline():
    """Screen direction across a cut, and dialogue eyelines that meet."""
    w, h = 112, 63
    A = 'style="stroke:var(--mark);fill:none" stroke-width="1.8" marker-end="url(#el-arrow)"'

    def walk(good, right_next):
        def draw(x, y):
            out = person(x + w*0.4, y + h*0.2, h*0.65)
            x1, x2 = (x + w*0.55, x + w*0.85) if right_next else (x + w*0.3, x + w*0.05)
            out += f'<line x1="{x1}" y1="{y+h*0.5}" x2="{x2}" y2="{y+h*0.5}" {A}/>'
            if good is not None:
                out += (ok_mark if good else bad_mark)(x + w - 10, y + 10)
            return out
        return draw

    def look(right):
        def draw(x, y):
            cx = x + w*(0.35 if right else 0.65)
            return (profile(cx, y + h*0.4, 11, right)
                    + f'<line x1="{cx + (16 if right else -16)}" y1="{y+h*0.38}" x2="{cx + (48 if right else -48)}" y2="{y+h*0.38}" style="stroke:var(--mark)" stroke-dasharray="3 2"/>')
        return draw

    panels = [("Shot 1: walks right", walk(None, True)), ("Shot 2: still right", walk(True, True)), ("Shot 2: now left", walk(False, False)),
              ("Person 1 looks right", look(True)), ("Person 2 looks left", look(False))]
    return with_defs(panel_strip(panels, "el", "Screen direction and eyelines"), arrow_defs("el-arrow", "var(--mark)"))


def rule_30():
    """Top view: a new angle of at least 30°, or a clear size step, between two shots of one subject."""
    p = ['<svg viewBox="0 0 560 268" role="img" aria-label="The 30-degree rule, top view">',
         '<text class="f-mute" x="16" y="22">TOP VIEW</text>']
    sx, sy, R = 200, 70, 150

    def cam(a, cls_ok, label, anchor="middle", dx=0):
        t = math.radians(a)
        x, y = sx + R*math.cos(t), sy + R*math.sin(t)
        deg = math.degrees(math.atan2(sy - y, sx - x))
        out = camera_top(x, y, deg)
        out += f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{sx}" y2="{sy}" style="stroke:var(--line)" stroke-dasharray="3 3"/>'
        mark = {True: ok_mark, False: bad_mark, None: lambda a, b: ""}[cls_ok]
        out += mark(x + dx*0.6, y - 16) + f'<text class="f-mute" x="{x + dx:.1f}" y="{y + 30:.1f}" text-anchor="{anchor}">{label}</text>'
        return out

    p.append(f'<path d="M{sx + 60*math.cos(math.radians(90))},{sy + 60} A60,60 0 0 0 {sx + 60*math.cos(math.radians(50)):.1f},{sy + 60*math.sin(math.radians(50)):.1f}" style="stroke:var(--ok);fill:none" stroke-width="1.5"/>')
    p.append(f'<text class="f-text" x="{sx + 30}" y="{sy + 80}" style="fill:var(--ok)">≥ 30°</text>')
    p.append(cam(90, None, "shot A"))
    p.append(cam(102, False, "12°: jump cut", "end", -10))
    p.append(cam(50, True, "40°: clean cut", "start", 10))
    p.append(f'<circle class="f-soft" cx="{sx}" cy="{sy}" r="12"/><text class="f-mute" x="{sx}" y="{sy - 18}" text-anchor="middle">subject</text>')
    # or: same angle, one size step
    bx, by = 400, 70
    p.append(f'<text class="f-text" x="{bx}" y="{by - 20}" font-weight="600">or one size step</text>')
    p.append(f'<rect class="f-fill" x="{bx}" y="{by}" width="64" height="36" style="stroke:var(--line)"/>')
    p.append(f'<g clip-path="url(#r30a)">{person(bx + 32, by + 6, 60)}</g><clipPath id="r30a"><rect x="{bx}" y="{by}" width="64" height="36"/></clipPath>')
    p.append(f'<text class="f-text" x="{bx + 76}" y="{by + 22}">→</text>')
    p.append(f'<rect class="f-fill" x="{bx + 90}" y="{by}" width="64" height="36" style="stroke:var(--line)"/>')
    p.append(f'<g clip-path="url(#r30b)">{head_shoulders(bx + 122, by + 18, 11)}</g><clipPath id="r30b"><rect x="{bx + 90}" y="{by}" width="64" height="36"/></clipPath>')
    p.append(f'<text class="f-mute" x="{bx + 32}" y="{by + 52}" text-anchor="middle">MS</text><text class="f-mute" x="{bx + 122}" y="{by + 52}" text-anchor="middle">CU</text>')
    p.append("</svg>")
    return "".join(p)


def j_l_cuts():
    """Timelines: a J-cut leads with the next sound, an L-cut lets the current sound run on."""
    p = ['<svg viewBox="0 0 640 210" role="img" aria-label="J-cut and L-cut on a timeline">']
    A_, B_ = "var(--accent-soft)", "var(--mark-soft, #fbefd9)"

    def tl(x0, title, audio_split):
        out = [f'<text class="f-text" x="{x0}" y="22" font-weight="600">{title}</text>']
        W, cut = 270, 140
        for row, (lab, y) in enumerate([("V", 40), ("A", 80)]):
            out.append(f'<text class="f-mute" x="{x0}" y="{y + 20}">{lab}</text>')
            split = cut if row == 0 else audio_split
            out.append(f'<rect x="{x0 + 18}" y="{y}" width="{split}" height="30" style="fill:{A_};stroke:var(--accent)"/>')
            out.append(f'<rect x="{x0 + 18 + split}" y="{y}" width="{W - split}" height="30" style="fill:{B_};stroke:var(--mark)"/>')
            out.append(f'<text class="f-mute" x="{x0 + 18 + split/2}" y="{y + 19}" text-anchor="middle">shot A</text>')
            out.append(f'<text class="f-mute" x="{x0 + 18 + split + (W - split)/2}" y="{y + 19}" text-anchor="middle">shot B</text>')
        out.append(f'<line x1="{x0 + 18 + cut}" y1="32" x2="{x0 + 18 + cut}" y2="120" style="stroke:var(--ink)" stroke-width="1.5" stroke-dasharray="4 3"/>')
        out.append(f'<text class="f-mute" x="{x0 + 18 + cut}" y="134" text-anchor="middle">picture cut</text>')
        return "".join(out)

    p.append(tl(20, "J-cut: B's sound starts first", 90))
    p.append(tl(340, "L-cut: A's sound runs on", 200))
    p.append('<text class="f-mute" x="20" y="170">The audio cut and the picture cut happen at different times.</text>')
    p.append('<text class="f-mute" x="20" y="188">The letter shows the shape of the audio edge on the timeline.</text>')
    p.append("</svg>")
    return "".join(p)


def murch_six():
    """Murch's ranking of what makes a good cut, as a bar chart."""
    data = [("Emotion", 51), ("Story", 23), ("Rhythm", 10), ("Eye trace", 7), ("2D plane", 5), ("3D space", 4)]
    p = ['<svg viewBox="0 0 560 200" role="img" aria-label="Murch\'s rule of six">']
    x0, scale = 100, 8
    for i, (name, v) in enumerate(data):
        y = 16 + i * 29
        style = "fill:var(--accent)" if i == 0 else "fill:var(--accent);opacity:.45"
        p.append(f'<text class="f-text" x="{x0 - 10}" y="{y + 15}" text-anchor="end">{name}</text>')
        p.append(f'<rect x="{x0}" y="{y}" width="{v * scale}" height="20" rx="2" style="{style}"/>')
        p.append(f'<text class="f-text" x="{x0 + v * scale + 6}" y="{y + 15}" font-weight="600">{v} %</text>')
    p.append("</svg>")
    return "".join(p)


def rhythm():
    """Shot lengths on a timeline: a fast hook that slows, vs a mechanical constant length."""
    p = ['<svg viewBox="0 0 640 150" role="img" aria-label="Rhythm: varied vs constant shot length">']
    x0, sc = 120, 18  # px per second
    rows = [("Varied", [1, 1.2, 0.8, 1.5, 2, 3.5, 2.5, 4, 3, 5], True), ("Constant", [3] * 9, False)]
    for r, (name, lens, good) in enumerate(rows):
        y = 26 + r * 56
        p.append(f'<text class="f-text" x="{x0 - 12}" y="{y + 19}" text-anchor="end" font-weight="600">{name}</text>')
        x = x0
        for k, L in enumerate(lens):
            fill = "var(--mark)" if good and x < x0 + 3 * sc else "var(--accent)"
            p.append(f'<rect x="{x:.1f}" y="{y}" width="{L * sc - 2:.1f}" height="28" rx="2" style="fill:{fill};opacity:{0.85 if k % 2 else 0.6}"/>')
            x += L * sc
        p.append((ok_mark if good else bad_mark)(x + 14, y + 14))
    p.append(f'<rect x="{x0}" y="16" width="{3 * sc}" height="2" style="fill:var(--mark)"/>')
    p.append(f'<text class="f-mute" x="{x0}" y="12">hook: 1–3 s cuts</text>')
    for s in range(0, 28, 5):
        p.append(f'<text class="f-mute" x="{x0 + s * sc}" y="138" text-anchor="middle">{s} s</text>')
    p.append("</svg>")
    return "".join(p)


def handles():
    """Generate each shot a little longer than needed; the extra (handles) gives room to move the cut."""
    p = ['<svg viewBox="0 0 640 170" role="img" aria-label="Handles around a planned cut point">']
    cut = 320
    p.append(f'<rect x="80" y="30" width="{cut - 80}" height="30" style="fill:var(--accent-soft);stroke:var(--accent)"/>')
    p.append(f'<rect x="{cut}" y="30" width="60" height="30" style="fill:var(--accent-soft);stroke:var(--accent);opacity:.5" stroke-dasharray="3 2"/>')
    p.append(f'<rect x="{cut - 60}" y="80" width="60" height="30" style="fill:var(--mark-soft, #fbefd9);stroke:var(--mark);opacity:.5" stroke-dasharray="3 2"/>')
    p.append(f'<rect x="{cut}" y="80" width="240" height="30" style="fill:var(--mark-soft, #fbefd9);stroke:var(--mark)"/>')
    p.append('<text class="f-text" x="90" y="50">shot A (used)</text><text class="f-text" x="330" y="100">shot B (used)</text>')
    p.append(f'<text class="f-mute" x="{cut + 30}" y="49" text-anchor="middle">+1 s</text><text class="f-mute" x="{cut - 30}" y="99" text-anchor="middle">+1 s</text>')
    p.append(f'<line x1="{cut}" y1="18" x2="{cut}" y2="124" style="stroke:var(--ink)" stroke-width="1.5"/>')
    p.append(f'<text class="f-mute" x="{cut}" y="140" text-anchor="middle">planned cut point</text>')
    p.append('<text class="f-mute" x="80" y="160">Dashed: handles. Generate them, so you can move the cut or add a transition.</text>')
    p.append("</svg>")
    return "".join(p)


# ---------------------------------------------------------------- C02·M05 story structure

def hook_types():
    """Four kinds of hook, each as a first frame."""
    w, h = 112, 63

    def visual(x, y):  # someone at a cliff edge
        return (f'<path class="f-fill" style="stroke:var(--ink)" stroke-width="1.5" d="M{x},{y+h*0.55} L{x+w*0.55},{y+h*0.55} L{x+w*0.55},{y+h} L{x},{y+h} Z"/>'
                + person(x + w*0.5, y + h*0.12, h*0.43)
                + f'<text class="f-text" x="{x+w*0.8}" y="{y+h*0.45}" font-weight="600" style="fill:var(--mark)">?</text>')

    def spoken(x, y):
        return (person(x + w*0.25, y + h*0.18, h*0.75)
                + f'<rect x="{x+w*0.42}" y="{y+10}" width="{w*0.52}" height="24" rx="8" class="f-soft"/>'
                f'<path class="f-soft" d="M{x+w*0.46},{y+33} L{x+w*0.38},{y+40} L{x+w*0.54},{y+33} Z"/>'
                f'<text class="f-text" x="{x+w*0.68}" y="{y+26}" text-anchor="middle" font-weight="600">US$4?</text>')

    def result(x, y):
        return (f'<rect x="{x+w*0.12}" y="{y+10}" width="{w*0.4}" height="{h-20}" rx="2" style="fill:var(--mark);opacity:.6"/>'
                f'<path d="M{x+w*0.85},{y+h*0.5} L{x+w*0.6},{y+h*0.5}" style="stroke:var(--ink)" stroke-width="1.5" marker-end="url(#hk-arrow)"/>'
                f'<text class="f-mute" x="{x+w*0.88}" y="{y+h*0.3}" text-anchor="middle">how?</text>')

    def pattern(x, y):
        pts = []
        for i in range(40):
            xx = x + 6 + i * 2.5
            amp = 18 if 18 <= i <= 21 else 2
            pts.append(f"{xx:.1f},{y + h/2 + (amp if i % 2 else -amp)}")
        return f'<polyline points="{" ".join(pts)}" style="stroke:var(--accent);fill:none" stroke-width="1.5"/>'

    panels = [("Visual question", visual), ("Spoken claim", spoken), ("Result first", result), ("Pattern break", pattern)]
    return with_defs(panel_strip(panels, "hk", "Four kinds of hook"), arrow_defs("hk-arrow"))


def story_shape():
    """Tension over time: situation, change, tension, the turn at about two thirds, release."""
    p = ['<svg viewBox="0 0 640 210" role="img" aria-label="The base shape of a story">']
    x0, x1, yb = 40, 600, 170
    p.append(f'<line x1="{x0}" y1="{yb}" x2="{x1}" y2="{yb}" style="stroke:var(--ink)"/>'
             f'<line x1="{x0}" y1="{yb}" x2="{x0}" y2="20" style="stroke:var(--ink)"/>')
    p.append(f'<text class="f-mute" x="{x1}" y="{yb + 18}" text-anchor="end">time</text>'
             f'<text class="f-mute" x="{x0 + 6}" y="28">tension</text>')

    def X(f):
        return x0 + f * (x1 - x0)
    pts = [(0, 140), (0.12, 138), (0.2, 118), (0.35, 100), (0.5, 76), (0.6, 58), (0.67, 36), (0.8, 110), (1, 128)]
    d = "M" + " L".join(f"{X(f):.0f},{y}" for f, y in pts)
    p.append(f'<path d="{d}" style="stroke:var(--accent);fill:none" stroke-width="2.5" stroke-linejoin="round"/>')
    labels = [(0.05, 132, "situation"), (0.2, 110, "change"), (0.45, 70, "tension rises"), (0.67, 28, "turn (≈ 2/3)"), (0.88, 104, "release")]
    for f, y, t in labels:
        bold = ' font-weight="600"' if "turn" in t else ""
        p.append(f'<text class="f-text" x="{X(f):.0f}" y="{y - 8}" text-anchor="middle"{bold}>{t}</text>')
    p.append(f'<line x1="{X(0.67):.0f}" y1="36" x2="{X(0.67):.0f}" y2="{yb}" style="stroke:var(--mark)" stroke-dasharray="4 3"/>')
    p.append("</svg>")
    return "".join(p)


def formats():
    """Each format scaled to the same width, so the proportions of the beats can be compared."""
    p = ['<svg viewBox="0 0 640 206" role="img" aria-label="Beats by format">']
    x0, W = 70, 550
    rows = [("15 s", [("problem", 3), ("product acts", 8), ("result + brand", 4)]),
            ("60 s", [("hook", 3), ("build", 30), ("turn", 12), ("payoff", 15)]),
            ("3 min", [("setup", 30), ("conflict", 120), ("resolution", 30)]),
            ("10 min", [("promise", 30), ("ch. 1", 120), ("ch. 2", 120), ("ch. 3", 120), ("ch. 4", 120), ("payoff", 90)])]
    for r, (name, beats) in enumerate(rows):
        y = 18 + r * 44
        total = sum(b for _, b in beats)
        p.append(f'<text class="f-text" x="{x0 - 10}" y="{y + 19}" text-anchor="end" font-weight="600">{name}</text>')
        x = x0
        for k, (lab, b) in enumerate(beats):
            bw = b / total * W
            op = 0.35 + 0.5 * (k % 2)
            p.append(f'<rect x="{x:.1f}" y="{y}" width="{bw - 2:.1f}" height="28" rx="2" style="fill:var(--accent);opacity:{op}"/>')
            if bw < 50:  # too narrow: label above the bar, at its left edge
                p.append(f'<text class="f-mute" x="{x:.1f}" y="{y - 3}">{lab}</text>')
            else:
                p.append(f'<text class="f-mute" x="{x + bw/2:.1f}" y="{y + 18}" text-anchor="middle" style="fill:var(--ink)">{lab}</text>')
            x += bw
    p.append('<text class="f-mute" x="70" y="198">Each row is scaled to the same width.</text>')
    p.append("</svg>")
    return "".join(p)


def setup_payoff():
    """An element shown early returns at the end with new meaning."""
    p = ['<svg viewBox="0 0 640 160" role="img" aria-label="Setup and payoff">', arrow_defs("sp-arrow", "var(--mark)")]
    x0, x1, y = 40, 600, 110
    p.append(f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" style="stroke:var(--ink)" stroke-width="1.5"/>')
    for k in range(9):
        x = x0 + k * (x1 - x0) / 8
        p.append(f'<line x1="{x}" y1="{y - 4}" x2="{x}" y2="{y + 4}" style="stroke:var(--ink)"/>')

    def watch(cx, cy, broken):
        out = (f'<circle cx="{cx}" cy="{cy}" r="16" class="f-fill" style="stroke:var(--ink)" stroke-width="2"/>'
               f'<path d="M{cx},{cy} L{cx},{cy-10} M{cx},{cy} L{cx+7},{cy+3}" style="stroke:var(--ink)" stroke-width="1.8"/>')
        if broken:
            out += f'<path d="M{cx-12},{cy-8} L{cx-2},{cy+2} L{cx-6},{cy+6} L{cx+6},{cy+14}" style="stroke:var(--bad);fill:none" stroke-width="1.5"/>'
        return out
    p.append(watch(110, 70, True) + '<text class="f-text" x="110" y="134" text-anchor="middle">setup: broken watch</text>')
    p.append(watch(540, 70, False) + '<text class="f-text" x="540" y="134" text-anchor="middle" font-weight="600">payoff: it works</text>')
    p.append('<path d="M130,48 Q325,-10 520,48" style="stroke:var(--mark);fill:none" stroke-width="1.8" stroke-dasharray="5 4" marker-end="url(#sp-arrow)"/>')
    p.append('<text class="f-mute" x="325" y="66" text-anchor="middle">keep it consistent in every shot between</text>')
    p.append("</svg>")
    return "".join(p)


def want_obstacle_change():
    p = ['<svg viewBox="0 0 640 120" role="img" aria-label="Want, obstacle, change">', arrow_defs("woc-arrow")]
    boxes = [("WANT", "clean shoes"), ("OBSTACLE", "rain"), ("CHANGE", "the product")]
    for i, (t, ex) in enumerate(boxes):
        x = 20 + i * 215
        cls = "f-soft" if i == 2 else "f-fill"
        p.append(f'<rect class="{cls}" x="{x}" y="24" width="170" height="64" rx="6" style="stroke:var(--accent)" stroke-width="1.5"/>')
        p.append(f'<text class="f-mute" x="{x + 85}" y="48" text-anchor="middle">{t}</text>')
        p.append(f'<text class="f-text" x="{x + 85}" y="70" text-anchor="middle" font-weight="600">{ex}</text>')
        if i < 2:
            p.append(f'<line x1="{x + 174}" y1="56" x2="{x + 210}" y2="56" style="stroke:var(--ink)" stroke-width="1.5" marker-end="url(#woc-arrow)"/>')
    p.append('<text class="f-mute" x="20" y="112">Example: a 15 s shoe ad. Write this sentence before any shot.</text>')
    p.append("</svg>")
    return "".join(p)


def escalation():
    """Beats as steps: each one raises the stakes; a beat that repeats a job is cut."""
    p = ['<svg viewBox="0 0 640 200" role="img" aria-label="Escalation and the turn">']
    x0, bw, yb = 40, 72, 170
    beats = [(30, "", True), (55, "", True), (55, "same job: cut", False), (82, "", True), (110, "", True), (140, "turn", True), (70, "payoff", True)]
    x = x0
    for k, (hgt, lab, keep) in enumerate(beats):
        if keep:
            fill = "var(--mark)" if lab == "turn" else "var(--accent)"
            p.append(f'<rect x="{x}" y="{yb - hgt}" width="{bw - 8}" height="{hgt}" rx="2" style="fill:{fill};opacity:.75"/>')
        else:
            p.append(f'<rect x="{x}" y="{yb - hgt}" width="{bw - 8}" height="{hgt}" rx="2" style="fill:none;stroke:var(--bad)" stroke-dasharray="4 3"/>')
            p.append(bad_mark(x + (bw - 8)/2, yb - hgt/2))
        if lab:
            bold = ' font-weight="600"' if lab == "turn" else ""
            p.append(f'<text class="f-text" x="{x + (bw - 8)/2}" y="{yb - hgt - 8}" text-anchor="middle"{bold}>{lab}</text>')
        p.append(f'<text class="f-mute" x="{x + (bw - 8)/2}" y="{yb + 16}" text-anchor="middle">beat {k + 1}</text>')
        x += bw
    p.append(f'<line x1="{x0}" y1="{yb}" x2="{x}" y2="{yb}" style="stroke:var(--ink)"/>')
    p.append(f'<text class="f-mute" x="{x0}" y="16">bar height = stakes</text>')
    p.append("</svg>")
    return "".join(p)


# ---------------------------------------------------------------- C02·M06 shot to prompt

def fixed_descriptors():
    """The same words give the same coat; a paraphrase gives the model a different coat."""
    w, h = 150, 63

    def coat(color, quote, good):
        def draw(x, y):
            cx = x + w/2
            return (f'<path d="M{cx-14},{y+16} L{cx+14},{y+16} L{cx+20},{y+h-6} L{cx-20},{y+h-6} Z" style="fill:{color};stroke:var(--ink)" stroke-width="1.2"/>'
                    f'<line x1="{cx}" y1="{y+16}" x2="{cx}" y2="{y+h-6}" style="stroke:var(--ink)" stroke-width="1"/>'
                    f'<text class="f-mute" x="{cx}" y="{y+11}" text-anchor="middle">"{quote}"</text>'
                    + ("" if good is None else (ok_mark if good else bad_mark)(x + w - 10, y + 24)))
        return draw

    panels = [("Prompt 1", coat("#6b6b3a", "olive raincoat", None)), ("Prompt 2: same words", coat("#6b6b3a", "olive raincoat", True)),
              ("Prompt 2: paraphrase", coat("#3f7d4a", "green coat", False))]
    return panel_strip(panels, "fd", "Fixed descriptors", w=w)


def negative_instructions():
    """Naming what you do not want often adds it; describe what you want instead."""
    w, h = 150, 63

    def wall(text_on, quote, good):
        def draw(x, y):
            out = f'<rect x="{x+8}" y="{y+18}" width="{w-16}" height="{h-24}" style="fill:#b9b6b0"/>'
            if text_on:
                out += f'<text x="{x + w/2}" y="{y+46}" text-anchor="middle" style="fill:#3a3a3a;font:700 14px var(--f-display, sans-serif)">TEXT</text>'
            out += f'<text class="f-mute" x="{x + w/2}" y="{y+12}" text-anchor="middle">"{quote}"</text>'
            return out + (ok_mark if good else bad_mark)(x + w - 12, y + 28)
        return draw

    panels = [("Negative words", wall(True, "no text on the wall", False)), ("Positive description", wall(False, "plain, empty wall", True))]
    return panel_strip(panels, "ni", "Negative instructions", w=w)


def one_action():
    """Five actions in one clip get rushed or merged; split them into one shot per action."""
    p = ['<svg viewBox="0 0 640 170" role="img" aria-label="One shot, one action">']
    acts = ["opens door", "walks in", "sees letter", "picks it up", "cries"]
    # crammed
    p.append('<text class="f-text" x="20" y="22" font-weight="600">One 8 s clip, five actions</text>')
    p.append('<rect x="20" y="32" width="200" height="34" rx="3" style="fill:var(--bad);opacity:.15;stroke:var(--bad)"/>')
    for k, a in enumerate(acts):
        p.append(f'<text class="f-mute" x="{24 + k * 40}" y="{48 + (k % 2) * 12}" style="fill:var(--ink)">{a.split()[0]}</text>')
    p.append(bad_mark(234, 49))
    # split
    p.append('<text class="f-text" x="20" y="102" font-weight="600">Five shots, one action each</text>')
    for k, a in enumerate(acts):
        x = 20 + k * 122
        p.append(f'<rect x="{x}" y="112" width="114" height="34" rx="3" style="fill:var(--accent-soft);stroke:var(--accent)"/>')
        p.append(f'<text class="f-text" x="{x + 57}" y="133" text-anchor="middle">{a}</text>')
    p.append('<text class="f-mute" x="20" y="164">Each shot has a clear start state and end state.</text>')
    p.append("</svg>")
    return "".join(p)


def review_decision():
    """Review each output against the spec, then decide."""
    p = ['<svg viewBox="0 0 640 230" role="img" aria-label="Review decision for a generated shot">', arrow_defs("rv-arrow")]

    def box(x, y, w, t, sub, cls="f-fill", stroke="var(--line)"):
        return (f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="46" rx="6" style="stroke:{stroke}" stroke-width="1.5"/>'
                f'<text class="f-text" x="{x + w/2}" y="{y + 20}" text-anchor="middle" font-weight="600">{t}</text>'
                f'<text class="f-mute" x="{x + w/2}" y="{y + 36}" text-anchor="middle">{sub}</text>')

    def arrow(x1, y1, x2, y2):
        return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" style="stroke:var(--ink)" stroke-width="1.3" marker-end="url(#rv-arrow)"/>'

    p.append(box(20, 92, 150, "Output", "check against spec"))
    outs = [("Keep", "meets the spec", "var(--ok)", 12), ("Fix in post", "small defect", "var(--accent)", 66),
            ("Regenerate", "core element fails", "var(--mark)", 120), ("Change approach", "failed 3 times", "var(--bad)", 174)]
    for t, sub, col, y in outs:
        p.append(box(250, y, 170, t, sub, stroke=col))
        p.append(arrow(172, 115, 246, y + 23))
    p.append(arrow(422, 197, 450, 197))
    p.append('<text class="f-mute" x="456" y="193">reference, first frame,</text><text class="f-mute" x="456" y="207">other model, or split</text>')
    p.append(arrow(422, 143, 450, 143))
    p.append('<text class="f-mute" x="456" y="147">new take, fixed prompt</text>')
    p.append("</svg>")
    return "".join(p)


FIGS = {"shot-sizes.svg": shot_sizes, "camera-angles.svg": camera_angles, "composition.svg": composition, "shots-content.svg": shots_by_content, "viewer-looks.svg": viewer_looks,
        "aspect-ratios.svg": aspect_ratios, "safe-areas.svg": safe_areas,
        "focal-length.svg": focal_length, "depth-of-field.svg": depth_of_field, "camera-moves.svg": camera_moves,
        "stabilization.svg": stabilization, "shutter.svg": shutter, "parallax.svg": parallax, "hard-moves.svg": hard_moves,
        "light-quality.svg": light_quality, "color-temperature.svg": color_temperature, "dynamic-range.svg": dynamic_range,
        "light-continuity.svg": light_continuity, "atmosphere.svg": atmosphere, "palette.svg": palette, "vectorscope.svg": vectorscope,
        "eyeline.svg": eyeline, "rule-30.svg": rule_30, "j-l-cuts.svg": j_l_cuts, "murch-six.svg": murch_six, "rhythm.svg": rhythm,
        "handles.svg": handles,
        "hook-types.svg": hook_types, "story-shape.svg": story_shape, "formats.svg": formats, "setup-payoff.svg": setup_payoff,
        "want-obstacle-change.svg": want_obstacle_change, "escalation.svg": escalation,
        "fixed-descriptors.svg": fixed_descriptors, "negative-instructions.svg": negative_instructions, "one-action.svg": one_action,
        "review-decision.svg": review_decision,
        "three-point.svg": three_point, "rule-180.svg": rule_180,
        "denoise.svg": denoise, "local-cloud.svg": local_cloud}

if __name__ == "__main__":
    for name, fn in FIGS.items():
        (OUT / name).write_text(fn())
        print("wrote", name)
