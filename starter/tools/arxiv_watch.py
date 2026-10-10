#!/usr/bin/env python3
"""Weekly research skim: new arXiv papers for your keywords (C17·M01, M03).

    python arxiv_watch.py --query 'video generation' --query 'video diffusion' --days 7 --max 30 > week.md

Uses the public arXiv API (export.arxiv.org); be polite: one run per day is enough.
Writes a Markdown list with a pass-1 checkbox for each paper.
"""
import argparse, datetime as dt, sys, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

NS = {"a": "http://www.w3.org/2005/Atom"}
API = "https://export.arxiv.org/api/query?"


def fetch(query, max_results, cats):
    terms = " AND ".join(f'all:"{w}"' if " " in w else f"all:{w}" for w in [query])
    if cats:
        terms = f"({terms}) AND ({' OR '.join('cat:' + c for c in cats)})"
    url = API + urllib.parse.urlencode({"search_query": terms, "sortBy": "submittedDate",
                                        "sortOrder": "descending", "max_results": max_results})
    req = urllib.request.Request(url, headers={"User-Agent": "course-arxiv-watch/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        root = ET.fromstring(r.read())
    for e in root.findall("a:entry", NS):
        yield {
            "id": e.findtext("a:id", namespaces=NS).rsplit("/", 1)[-1].split("v")[0],
            "title": " ".join(e.findtext("a:title", namespaces=NS).split()),
            "date": e.findtext("a:published", namespaces=NS)[:10],
            "authors": [x.findtext("a:name", namespaces=NS) for x in e.findall("a:author", NS)],
            "summary": " ".join(e.findtext("a:summary", namespaces=NS).split()),
        }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--query", action="append", required=True)
    ap.add_argument("--cat", action="append", default=["cs.CV", "cs.LG", "cs.MM", "cs.SD", "eess.AS"])
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--max", type=int, default=30)
    a = ap.parse_args(argv)
    since = (dt.date.today() - dt.timedelta(days=a.days)).isoformat()
    seen = {}
    for i, q in enumerate(a.query):
        if i:
            time.sleep(3)  # arXiv asks for a 3 s gap between calls
        for p in fetch(q, a.max, a.cat):
            if p["date"] >= since:
                seen.setdefault(p["id"], p)
    papers = sorted(seen.values(), key=lambda p: p["date"], reverse=True)
    print(f"# arXiv watch {dt.date.today()} ({len(papers)} papers since {since})\n")
    for p in papers:
        auth = ", ".join(p["authors"][:3]) + (" et al." if len(p["authors"]) > 3 else "")
        first = p["summary"].split(". ")[0][:240]
        print(f"- [ ] **{p['title']}** ({p['date']}, {auth}) https://arxiv.org/abs/{p['id']}\n  {first}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
