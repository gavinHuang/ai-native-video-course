#!/usr/bin/env python3
"""Check all external links in content/ (watch + deeper + inline) and record each page's title.
YouTube links are checked via oEmbed (which returns the video title).

Writes docs/link-report.md with three parts:
  1. links that do not answer 200;
  2. links whose page title shares few words with the title we give the link (check by hand: wrong page?);
  3. all links with their page titles.
Many sites block scripts (403) but work in a browser; check those by hand too."""
import concurrent.futures as cf
import html
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
URL_RE = re.compile(r"https?://(?:[^\s()\"'<>\]]|\([^\s()]*\))+")  # allows one level of (...) as in Wikipedia URLs
PAIR_RE = re.compile(r'- title: "([^"]+)"\s*\n\s*url: (\S+)')
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126 Safari/537.36",
      "Accept-Language": "en"}
STOP = set("the a an of and or to in on for with by from is are how what your you – — - · | : at as it its".split())


def page_title(body, ctype):
    if "pdf" in ctype:
        return "(PDF)"
    m = re.search(rb"<title[^>]*>(.*?)</title>", body, re.S | re.I)
    if not m:
        m = re.search(rb'property="og:title" content="([^"]+)"', body)
    if not m:
        return ""
    t = m.group(1).decode("utf-8", "replace")
    return " ".join(html.unescape(t).split())[:160]


def check(url):
    target, yt = url, "youtube.com/watch" in url or "youtu.be/" in url
    if yt:
        target = "https://www.youtube.com/oembed?format=json&url=" + urllib.parse.quote(url, safe="")
    try:
        req = urllib.request.Request(target, headers=UA)
        with urllib.request.urlopen(req, timeout=25) as r:
            body = r.read(400_000)
            if yt:
                return url, r.status, json.loads(body).get("title", ""), url
            return url, r.status, page_title(body, r.headers.get("Content-Type", "")), r.geturl()
    except urllib.error.HTTPError as e:
        return url, e.code, "", url
    except Exception as e:  # noqa
        return url, type(e).__name__, "", url


def words(s):
    return {w for w in re.findall(r"[a-z0-9]+", s.lower()) if w not in STOP and len(w) > 2}


def main():
    urls, given = {}, {}
    for f in sorted((ROOT / "content").rglob("*.md")):
        text = f.read_text()
        for t, u in PAIR_RE.findall(text):
            given.setdefault(u.rstrip(".,;"), t)
        for u in URL_RE.findall(text):
            u = u.rstrip(".,;")
            urls.setdefault(u, []).append(str(f.relative_to(ROOT)))
    with cf.ThreadPoolExecutor(16) as ex:
        results = list(ex.map(check, urls))
    bad = [r for r in results if r[1] != 200]
    mismatch = []
    for u, s, title, final in results:
        if s == 200 and u in given and title and title != "(PDF)":
            g, t = words(given[u]), words(title)
            if g and len(g & t) / len(g) < 0.2:
                mismatch.append((u, given[u], title, final))
    used = lambda u: ", ".join(sorted({p.split("/")[1][:3] + "·" + p.split("/")[-1][:3] for p in urls[u]}))
    lines = [f"# Link report\n\nChecked {len(results)} unique links: {len(results) - len(bad)} answer 200, "
             f"{len(bad)} do not, {len(mismatch)} have a page title that differs from our link title.\n",
             "## 1. Not 200\n\n403 usually means the site blocks scripts; open it in a browser.\n",
             "| Status | URL | Used in |", "|---|---|---|"]
    lines += [f"| {s} | {u} | {used(u)} |" for u, s, _, _ in sorted(bad, key=lambda x: str(x[1]))]
    lines += ["\n## 2. Title check (by hand)\n", "| Our title | Page title | URL |", "|---|---|---|"]
    lines += [f"| {g} | {t.replace('|', '/')} | {u} |" for u, g, t, _ in mismatch]
    lines += ["\n## 3. All links with page titles\n", "| Status | Page title | URL |", "|---|---|---|"]
    lines += [f"| {s} | {t.replace('|', '/')} | {u} |" for u, s, t, _ in sorted(results)]
    (ROOT / "docs" / "link-report.md").write_text("\n".join(lines) + "\n")
    print(f"{len(results)} links, {len(bad)} not 200, {len(mismatch)} title mismatches")
    for u, s, _, _ in bad:
        print(s, u)
    print("--- title mismatches")
    for u, g, t, f in mismatch:
        print(f"{g!r} vs {t!r}\n   {u}" + (f" -> {f}" if f != u else ""))


if __name__ == "__main__":
    main()
