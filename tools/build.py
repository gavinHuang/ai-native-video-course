#!/usr/bin/env python3
"""Build the self-paced course site from content/.

Usage:
  .venv/bin/python tools/build.py            # build site/index.html
  .venv/bin/python tools/build.py --audio    # also make narration audio (macOS `say` + ffmpeg)
  .venv/bin/python tools/build.py --check    # run structure + STE checks only
"""
import hashlib
import html
import json
import math
import re
import subprocess
import sys
import zipfile
from pathlib import Path

import markdown
import yaml

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
SITE = ROOT / "site"
AUDIO_DIR = SITE / "audio"
FIG_DIR = ROOT / "assets" / "figures"
VOICE = "Samantha"

REQUIRED_SECTIONS = ["Learn", "Worked example", "Lab", "Model answer"]
OPTIONAL_SECTIONS = ["Tool walkthrough"]  # product names are allowed here, not in Learn

# Quality gates for self-paced study (see docs/writing-rules.md).
MIN_TEACHING_WORDS = 600   # Learn + Tool walkthrough
MIN_MODEL_ANSWER_WORDS = 120
MIN_QUIZ = 6


def product_regex():
    names = [l.strip() for l in (ROOT / "tools" / "product_names.txt").read_text().splitlines()
             if l.strip() and not l.startswith("#")]
    alt = "|".join(re.escape(n) for n in sorted(names, key=len, reverse=True))
    return re.compile(rf"(?<![\w.-])({alt})(?![\w])")  # case-sensitive: product names are proper nouns


# ---------------------------------------------------------------- loading
def split_front(text):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        raise ValueError("missing front matter")
    return yaml.safe_load(m.group(1)), m.group(2)


def load():
    courses = []
    for cdir in sorted(p for p in CONTENT.iterdir() if p.is_dir() and re.match(r"C\d\d", p.name)):
        meta, body = split_front((cdir / "_course.md").read_text())
        meta["body"] = body
        meta["dir"] = cdir
        meta["modules"] = []
        for mf in sorted(cdir.glob("M*.md")):
            mmeta, mbody = split_front(mf.read_text())
            mmeta["body"] = mbody
            mmeta["file"] = mf
            mmeta["id"] = f"{meta['code'].lower()}-{mf.stem.split('-')[0].lower()}"
            mmeta["code"] = f"{meta['code']}·{mf.stem.split('-')[0]}"
            meta["modules"].append(mmeta)
        courses.append(meta)
    glossary = yaml.safe_load((CONTENT / "glossary.yml").read_text()) or []
    return courses, glossary


# ---------------------------------------------------------------- diagrams
def _wrap(text, width):
    words, lines, cur = str(text).split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width and cur:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    return lines


def _box(x, y, w, h, text, cls="d-node", chars=None):
    chars = chars or max(8, int(w / 7.2))
    lines = _wrap(text, chars)
    out = [f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="6"/>']
    lh = 16
    y0 = y + h / 2 - (len(lines) - 1) * lh / 2 + 5
    for i, ln in enumerate(lines):
        out.append(f'<text class="d-label" x="{x + w / 2}" y="{y0 + i * lh}" text-anchor="middle">{html.escape(ln)}</text>')
    return "".join(out)


def _arrow(x1, y1, x2, y2):
    return f'<line class="d-edge" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" marker-end="url(#ah)"/>'


DEFS = ('<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
        'orient="auto-start-reverse"><path class="d-head" d="M0,0 L10,5 L0,10 z"/></marker></defs>')


def diagram_svg(spec):
    t = spec.get("type", "flow")
    title = spec.get("title", "")
    W = 760
    parts = []
    if t == "flow":
        nodes = spec["nodes"]
        per = min(4, len(nodes))
        bw, bh, gx, gy = 150, 70, 40, 50
        rows = math.ceil(len(nodes) / per)
        total_w = per * bw + (per - 1) * gx
        x0 = (W - total_w) / 2
        H = 40 + rows * bh + (rows - 1) * gy + 20
        for i, n in enumerate(nodes):
            r, c = divmod(i, per)
            if r % 2 == 1:
                c = per - 1 - c  # snake layout keeps arrows short
            x, y = x0 + c * (bw + gx), 40 + r * (bh + gy)
            parts.append(_box(x, y, bw, bh, n, "d-node d-accent" if i in spec.get("highlight", []) else "d-node"))
            if i + 1 < len(nodes):
                r2, c2 = divmod(i + 1, per)
                if r2 % 2 == 1:
                    c2 = per - 1 - c2
                x2, y2 = x0 + c2 * (bw + gx), 40 + r2 * (bh + gy)
                if r2 == r:
                    if c2 > c:
                        parts.append(_arrow(x + bw, y + bh / 2, x2 - 2, y2 + bh / 2))
                    else:
                        parts.append(_arrow(x, y + bh / 2, x2 + bw + 2, y2 + bh / 2))
                else:
                    parts.append(_arrow(x + bw / 2, y + bh, x2 + bw / 2, y2 - 2))
        if spec.get("loop"):
            parts.append(f'<text class="d-note" x="{W/2}" y="{H-4}" text-anchor="middle">↺ {html.escape(spec["loop"])}</text>')
            H += 10
    elif t == "cycle":
        nodes = spec["nodes"]
        n = len(nodes)
        cx, cy, R = W / 2, 200, 150
        bw, bh = 150, 56
        H = 410
        pts = [(cx + R * 1.5 * math.sin(2 * math.pi * i / n), cy - R * math.cos(2 * math.pi * i / n)) for i in range(n)]
        for i in range(n):
            (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % n]
            dx, dy = x2 - x1, y2 - y1
            d = math.hypot(dx, dy) or 1
            sx, sy = x1 + dx / d * 70, y1 + dy / d * 34
            ex, ey = x2 - dx / d * 78, y2 - dy / d * 36
            parts.append(_arrow(sx, sy, ex, ey))
        for i, (x, y) in enumerate(pts):
            parts.append(_box(x - bw / 2, y - bh / 2, bw, bh, nodes[i]))
        if spec.get("center"):
            parts.append(f'<text class="d-center" x="{cx}" y="{cy + 5}" text-anchor="middle">{html.escape(spec["center"])}</text>')
    elif t == "stack":
        layers = spec["nodes"]
        bh, gap = 46, 10
        H = 40 + len(layers) * (bh + gap) + 10
        for i, n in enumerate(layers):
            label, _, detail = str(n).partition(":")
            y = 40 + i * (bh + gap)
            cls = "d-node d-accent" if i in spec.get("highlight", []) else "d-node"
            parts.append(f'<rect class="{cls}" x="60" y="{y}" width="{W-120}" height="{bh}" rx="6"/>')
            parts.append(f'<text class="d-label d-strong" x="80" y="{y + 28}">{html.escape(label.strip())}</text>')
            if detail:
                parts.append(f'<text class="d-label" x="300" y="{y + 28}">{html.escape(detail.strip()[:70])}</text>')
    elif t == "compare":
        cols = [spec["left"], spec["right"]]
        rows = max(len(c["items"]) for c in cols)
        H = 40 + 44 + rows * 40 + 20
        cw = 320
        for k, col in enumerate(cols):
            x = 40 + k * (cw + 40)
            parts.append(f'<rect class="d-node d-accent" x="{x}" y="40" width="{cw}" height="36" rx="6"/>')
            parts.append(f'<text class="d-label d-strong" x="{x + cw/2}" y="63" text-anchor="middle">{html.escape(col["title"])}</text>')
            for i, it in enumerate(col["items"]):
                y = 86 + i * 40
                parts.append(_box(x, y, cw, 32, it, chars=44))
    elif t == "layers2d":  # grid of labelled cells: rows x cols
        rows_ = spec["rows"]
        cols_ = spec["cols"]
        cells = spec["cells"]
        lw = 130
        cw = (W - 60 - lw) / len(cols_)
        H = 40 + 34 + len(rows_) * 52 + 10
        for j, c in enumerate(cols_):
            parts.append(f'<text class="d-label d-strong" x="{40 + lw + j*cw + cw/2}" y="62" text-anchor="middle">{html.escape(c)}</text>')
        for i, r in enumerate(rows_):
            y = 74 + i * 52
            parts.append(f'<text class="d-label d-strong" x="40" y="{y + 28}">{html.escape(r)}</text>')
            for j in range(len(cols_)):
                parts.append(_box(40 + lw + j * cw + 4, y, cw - 8, 44, cells[i][j], chars=int((cw - 8) / 7)))
    else:
        raise ValueError(f"unknown diagram type {t}")
    head = f'<text class="d-title" x="20" y="24">{html.escape(title)}</text>' if title else ""
    return (f'<svg class="diagram" viewBox="0 0 {W} {int(H)}" role="img" aria-label="{html.escape(title)}">'
            f'{head}{"".join(parts)}</svg>')


# ---------------------------------------------------------------- markdown
MD = markdown.Markdown(extensions=["tables", "fenced_code", "attr_list", "sane_lists"])


def inline_figures(md_text):
    """Replace ![alt](fig:name.svg) with the inline SVG file from assets/figures."""
    def rep(m):
        alt, name = m.group(1), m.group(2)
        p = FIG_DIR / name
        if not p.exists():
            raise FileNotFoundError(p)
        svg = p.read_text()
        return f'\n<figure class="fig">{svg}<figcaption>{html.escape(alt)}</figcaption></figure>\n'
    return re.sub(r"!\[([^\]]*)\]\(fig:([^)]+)\)", rep, md_text)


def fix_lists(text):
    """Python-Markdown needs a blank line before a list. Insert it where authors omitted it."""
    out, prev = [], ""
    in_code = False
    for line in (text or "").splitlines():
        if line.startswith("```"):
            in_code = not in_code
        is_item = bool(re.match(r"^\s*(?:[-*]|\d+\.)\s+", line))
        prev_item = bool(re.match(r"^\s*(?:[-*]|\d+\.)\s+", prev))
        if not in_code and is_item and prev.strip() and not prev_item and not line.startswith(" "):
            out.append("")
        out.append(line)
        prev = line
    return "\n".join(out)


def md(text):
    MD.reset()
    out = MD.convert(inline_figures(fix_lists(text or "")))
    out = re.sub(r'<a href="(https?://[^"]+)"', r'<a href="\1" target="_blank" rel="noopener"', out)
    return out


def split_sections(body):
    """Split module body on '## ' headings → ordered dict name → markdown."""
    secs, cur, buf = {}, None, []
    for line in body.splitlines():
        m = re.match(r"^## (.+)$", line)
        if m:
            if cur:
                secs[cur] = "\n".join(buf).strip()
            cur, buf = m.group(1).strip(), []
        else:
            buf.append(line)
    if cur:
        secs[cur] = "\n".join(buf).strip()
    return secs


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


# ---------------------------------------------------------------- audio
def narration_text(course, mod):
    outs = " ".join(f"{i+1}. {o}" for i, o in enumerate(mod.get("outcomes", [])))
    return (f"{course['code']}, module {mod['code'].split('·')[1][1:]}. {mod['title']}. "
            f"After this module, you can: {outs} {mod.get('summary', '')}")


def make_audio(courses):
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    for c in courses:
        for m in c["modules"]:
            text = narration_text(c, m)
            h = hashlib.sha1(text.encode()).hexdigest()[:10]
            out = AUDIO_DIR / f"{m['id']}.mp3"
            stamp = AUDIO_DIR / f"{m['id']}.hash"
            if out.exists() and stamp.exists() and stamp.read_text() == h:
                continue
            aiff = AUDIO_DIR / f"{m['id']}.aiff"
            subprocess.run(["say", "-v", VOICE, "-r", "175", "-o", str(aiff), text], check=True)
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(aiff), "-ac", "1", "-c:a", "libmp3lame", "-b:a", "48k", str(out)], check=True)
            aiff.unlink()
            stamp.write_text(h)
            print("audio", out.name)


# ---------------------------------------------------------------- checks
STE_LONG = 25


def ste_report(text):
    plain = re.sub(r"```.*?```", "", text, flags=re.S)
    plain = re.sub(r"\|.*\|", "", plain)
    plain = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", plain)
    # Headings, list items, and paragraphs are separate units; split on line breaks first.
    sentences = [x for line in plain.splitlines() for x in re.split(r"(?<=[.!?])\s+", line.strip()) if x]
    long_ = [s for s in sentences if len(s.split()) > STE_LONG]
    passive = [s for s in sentences if re.search(r"\b(is|are|was|were|be|been|being)\s+\w+ed\b", s)]
    return long_, passive


def words(text):
    return len(re.sub(r"```.*?```", "", text or "", flags=re.S).split())


def check(courses, glossary):
    problems = []
    prx = product_regex()
    gterms = {g["term"].lower() for g in glossary}
    total_long = total_sent = 0
    for c in courses:
        if not c["modules"]:
            problems.append(f"{c['code']}: no modules")
        for m in c["modules"]:
            secs = split_sections(m["body"])
            for s in REQUIRED_SECTIONS:
                if s not in secs:
                    problems.append(f"{m['id']}: missing section '{s}'")
            for key in ("outcomes", "summary", "diagram", "watch", "quiz", "deeper", "keywords"):
                if not m.get(key):
                    problems.append(f"{m['id']}: missing '{key}'")
            for k in m.get("keywords", []):
                if k.lower() not in gterms:
                    problems.append(f"{m['id']}: keyword '{k}' not in glossary")
            for q in m.get("quiz", []):
                if not (0 <= q["answer"] < len(q["options"])):
                    problems.append(f"{m['id']}: quiz answer index out of range")
            teach = words(secs.get("Learn")) + words(secs.get("Tool walkthrough"))
            if teach < MIN_TEACHING_WORDS:
                problems.append(f"{m['id']}: teaching text {teach} words (min {MIN_TEACHING_WORDS})")
            if words(secs.get("Model answer")) < MIN_MODEL_ANSWER_WORDS:
                problems.append(f"{m['id']}: model answer {words(secs.get('Model answer'))} words (min {MIN_MODEL_ANSWER_WORDS})")
            if len(m.get("quiz", [])) < MIN_QUIZ:
                problems.append(f"{m['id']}: {len(m.get('quiz', []))} quiz questions (min {MIN_QUIZ})")
            allowed = set(c.get("learn_allows", []))
            learn_plain = re.sub(r"```.*?```|`[^`]*`", "", secs.get("Learn", ""), flags=re.S)
            names = sorted({h for h in prx.findall(learn_plain) if h not in allowed})
            if names:
                problems.append(f"{m['id']}: product names in Learn (move to Tool walkthrough): {', '.join(names)}")
            long_, _ = ste_report(secs.get("Learn", ""))
            total_long += len(long_)
            total_sent += len(re.split(r"(?<=[.!?])\s+", secs.get("Learn", "")))
            try:
                diagram_svg(m["diagram"])
            except Exception as e:  # noqa
                problems.append(f"{m['id']}: diagram error {e}")
    print(f"Courses: {len(courses)}  Modules: {sum(len(c['modules']) for c in courses)}  Glossary: {len(glossary)}")
    print(f"STE: {total_long} long sentences (> {STE_LONG} words) in Learn sections, of about {total_sent}")
    for p in problems:
        print("PROBLEM", p)
    return problems


# ---------------------------------------------------------------- render
def render_module(c, m, prev_id, next_id):
    secs = split_sections(m["body"])
    out = [f'<article class="page module" id="{m["id"]}" data-course="{c["code"].lower()}" hidden>']
    out.append(f'<p class="eyebrow"><a href="#{c["code"].lower()}">{c["code"]} · {html.escape(c["title"])}</a></p>')
    out.append(f'<h1><span class="tc">{m["code"]}</span> {html.escape(m["title"])}</h1>')
    out.append(f'<p class="meta">Study time: {m.get("hours", "?")} h · Level {c["level"]}</p>')

    out.append('<section class="block outcomes"><h2>Outcomes</h2><p>After this module, you can:</p><ol>')
    out += [f"<li>{html.escape(o)}</li>" for o in m["outcomes"]]
    out.append("</ol></section>")

    kws = " ".join(f'<a class="chip" href="#g-{slug(k)}">{html.escape(k)}</a>' for k in m.get("keywords", []))
    out.append(f'<section class="block"><h2>Key words</h2><p class="chips">{kws}</p></section>')

    audio = f"audio/{m['id']}.mp3"
    out.append('<section class="block listen"><h2>Listen</h2>'
               f'<audio controls preload="none" src="{audio}"></audio>'
               '<details><summary>Transcript (synthetic voice)</summary>'
               f'<p>{html.escape(narration_text(c, m))}</p></details></section>')

    out.append(f'<section class="block learn"><h2>Learn</h2>{md(secs.get("Learn", ""))}</section>')
    out.append(f'<figure class="block diagram-wrap">{diagram_svg(m["diagram"])}'
               f'<figcaption>Diagram: {html.escape(m["diagram"].get("title", ""))}</figcaption></figure>')

    for extra in secs:
        if extra not in REQUIRED_SECTIONS + ["Learn"]:
            out.append(f'<section class="block"><h2>{html.escape(extra)}</h2>{md(secs[extra])}</section>')

    out.append('<section class="block watch"><h2>Watch</h2><ul class="links">')
    for w in m["watch"]:
        out.append(f'<li><a href="{html.escape(w["url"])}" target="_blank" rel="noopener">{html.escape(w["title"])}</a>'
                   f'<span>{html.escape(w.get("note", ""))}</span></li>')
    out.append("</ul></section>")

    out.append(f'<section class="block worked"><h2>Worked example</h2>{md(secs.get("Worked example", ""))}</section>')
    out.append(f'<section class="block lab"><h2>Lab</h2>{md(secs.get("Lab", ""))}</section>')

    qid = m["id"]
    out.append(f'<section class="block quiz" data-quiz="{qid}"><h2>Self-check quiz</h2>')
    for i, q in enumerate(m["quiz"]):
        out.append(f'<fieldset class="q" data-answer="{q["answer"]}"><legend>{i+1}. {html.escape(q["q"])}</legend>')
        for j, o in enumerate(q["options"]):
            out.append(f'<label><input type="radio" id="{qid}-q{i}-o{j}" name="{qid}-q{i}" value="{j}"> {html.escape(o)}</label>')
        out.append(f'<p class="explain" hidden>{html.escape(q["explain"])}</p></fieldset>')
    out.append('<p class="score" aria-live="polite"></p></section>')

    out.append(f'<details class="block answer"><summary>Model answer (open after you do the lab)</summary>{md(secs.get("Model answer", ""))}</details>')

    out.append('<section class="block deeper"><h2>Go deeper</h2><ul class="links">')
    for d in m["deeper"]:
        out.append(f'<li><a href="{html.escape(d["url"])}" target="_blank" rel="noopener">{html.escape(d["title"])}</a></li>')
    out.append("</ul></section>")

    out.append(f'<p class="done"><label><input type="checkbox" class="done-box" id="done-{m["id"]}" data-id="{m["id"]}"> I completed this module</label></p>')
    nav = []
    if prev_id:
        nav.append(f'<a href="#{prev_id}">← Previous</a>')
    nav.append(f'<a href="#{c["code"].lower()}">Course overview</a>')
    if next_id:
        nav.append(f'<a href="#{next_id}">Next →</a>')
    out.append(f'<nav class="pager">{"".join(nav)}</nav></article>')
    return "\n".join(out)


def timeline(c):
    total = sum(float(m.get("hours", 1)) for m in c["modules"]) or 1
    segs = "".join(
        f'<a class="clip" href="#{m["id"]}" data-id="{m["id"]}" style="flex:{float(m.get("hours",1))}" title="{html.escape(m["title"])}">'
        f'<span>{m["code"].split("·")[1]}</span></a>' for m in c["modules"])
    return f'<div class="timeline" aria-label="Modules">{segs}</div>'


def render_course(c):
    out = [f'<article class="page course" id="{c["code"].lower()}" hidden>']
    out.append(f'<p class="eyebrow"><a href="#home">Program</a> · Level {c["level"]}</p>')
    out.append(f'<h1><span class="tc">{c["code"]}</span> {html.escape(c["title"])}</h1>')
    out.append(f'<p class="meta">{c["hours"]} h · Prerequisites: {html.escape(c.get("prereq", "none"))}</p>')
    out.append(timeline(c))
    out.append(f'<section class="block">{md(c["body"])}</section>')
    out.append('<section class="block"><h2>Course outcomes</h2><ol>' + "".join(f"<li>{html.escape(o)}</li>" for o in c["outcomes"]) + "</ol></section>")
    out.append('<section class="block"><h2>Modules</h2><ol class="modlist">')
    for m in c["modules"]:
        out.append(f'<li><a href="#{m["id"]}"><span class="tc">{m["code"]}</span> {html.escape(m["title"])}</a> <span class="meta">{m.get("hours","?")} h</span></li>')
    out.append("</ol></section></article>")
    return "\n".join(out)


def render_home(courses, home_md):
    out = ['<article class="page home" id="home">']
    out.append(md(home_md))
    levels = {}
    for c in courses:
        levels.setdefault(c["level"], []).append(c)
    names = {1: "Core models and screen language", 2: "Generation", 3: "AI-native post-production",
             4: "Pipelines and infrastructure", 5: "Trust, frontier, capstone"}
    out.append('<section class="levels">')
    for lv in sorted(levels):
        out.append(f'<div class="level"><h2><span class="tc">L{lv}</span> {names.get(lv, "")}</h2><ul class="cards">')
        for c in levels[lv]:
            out.append(f'<li><a class="card" href="#{c["code"].lower()}"><span class="tc">{c["code"]}</span>'
                       f'<strong>{html.escape(c["title"])}</strong><span class="meta">{c["hours"]} h · {len(c["modules"])} modules</span>'
                       f'<span class="prog" data-course="{c["code"].lower()}"></span></a></li>')
        out.append("</ul></div>")
    out.append("</section></article>")
    return "\n".join(out)


def render_glossary(glossary):
    out = ['<article class="page" id="glossary" hidden><h1>Glossary</h1><dl class="gloss">']
    for g in sorted(glossary, key=lambda x: x["term"].lower()):
        out.append(f'<dt id="g-{slug(g["term"])}">{html.escape(g["term"])}</dt><dd>{html.escape(g["def"])}</dd>')
    out.append("</dl></article>")
    return "\n".join(out)


def fill_totals(text, courses):
    """Replace {{HOURS}}, {{WEEKS_15}}, {{WEEKS_40}}, {{MODULES}} with values from the module files."""
    hours = sum(float(m.get("hours", 0)) for c in courses for m in c["modules"])
    vals = {"HOURS": f"{round(hours / 10) * 10:,.0f}", "MODULES": str(sum(len(c["modules"]) for c in courses)),
            "MONTHS_15": str(round(hours / 15 / 4.33)), "MONTHS_40": str(round(hours / 40 / 4.33))}
    return re.sub(r"\{\{(HOURS|MODULES|MONTHS_15|MONTHS_40)\}\}", lambda m: vals[m.group(1)], text)


def render_page(pid, title, md_text):
    return f'<article class="page" id="{pid}" hidden>{md(md_text)}</article>'


def build():
    courses, glossary = load()
    problems = check(courses, glossary)
    pages = [render_home(courses, fill_totals((CONTENT / "home.md").read_text(), courses))]
    flat = [m["id"] for c in courses for m in c["modules"]]
    for c in courses:
        pages.append(render_course(c))
        for m in c["modules"]:
            i = flat.index(m["id"])
            pages.append(render_module(c, m, flat[i - 1] if i else None, flat[i + 1] if i + 1 < len(flat) else None))
    pages.append(render_glossary(glossary))
    for extra in ("how-to-study", "requirements", "landscape", "paths"):
        p = CONTENT / f"{extra}.md"
        if p.exists():
            pages.append(render_page(extra, extra, fill_totals(p.read_text(), courses)))
    nav = "".join(f'<a href="#{c["code"].lower()}" class="navc"><span class="tc">{c["code"]}</span> {html.escape(c["title"])}</a>' for c in courses)
    shell = (ROOT / "tools" / "shell.html").read_text()
    index = {m["id"]: {"c": c["code"].lower(), "t": m["title"]} for c in courses for m in c["modules"]}
    page = (shell.replace("{{NAV}}", nav)
                 .replace("{{PAGES}}", "\n".join(pages))
                 .replace("{{INDEX}}", json.dumps(index)))
    SITE.mkdir(exist_ok=True)
    (SITE / "artifact.html").write_text(page)  # fragment: the artifact host adds the document skeleton
    full = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"></head><body>'
            + page + '</body></html>')
    (SITE / "index.html").write_text(full)  # offline copy: open site/index.html in any browser
    print(f"Wrote {SITE/'index.html'} ({len(full)//1024} KB)")
    make_starter_zip()
    return problems


def make_starter_zip():
    """Pack starter/ into site/starter.zip. Course pages link to it as 'starter.zip'."""
    src = ROOT / "starter"
    out = SITE / "starter.zip"
    skip = {"__pycache__", ".pytest_cache", ".DS_Store"}
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(src.rglob("*")):
            if p.is_file() and not (set(p.parts) & skip):
                z.write(p, Path("starter") / p.relative_to(src))
    print(f"Wrote {out} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    if "--check" in sys.argv:
        c, g = load()
        sys.exit(1 if check(c, g) else 0)
    if "--audio" in sys.argv:
        c, _ = load()
        make_audio(c)
    build()
