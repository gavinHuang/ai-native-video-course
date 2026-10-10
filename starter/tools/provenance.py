#!/usr/bin/env python3
"""Sign deliverables with C2PA content credentials, verify them, and gate delivery on them (C16·M03).

Needs c2patool (github.com/contentauth/c2pa-rs releases) on PATH, or set C2PATOOL=/path/to/c2patool.

  python provenance.py sign film.mp4 --out film_signed.mp4 --title "The Camera ep1" --author "Example Studio" \
      --ai generated --cert certs/studio.pem --key certs/studio.key
  python provenance.py verify film_signed.mp4
  python provenance.py gate film_signed.mp4 --record assets/film.json     # delivery gate: exit 0 = PASS

--ai: generated  = the content is made by a generative model (IPTC digital source type trainedAlgorithmicMedia)
      composite  = generated elements mixed with captured material (compositeWithTrainedAlgorithmicMedia)
      edited     = captured material edited with AI tools (an edit action; source type left to the ingredients)

Facts from the course tests (c2patool 0.27.22, 2026-10-04):
  - any later ffmpeg step, even a stream-copy remux or trim, removed the manifest: SIGN LAST, after all encodes
  - changing one byte made the file "Invalid" (assertion.bmffHash.mismatch): the credentials prove integrity
  - the sample test certificate gives "signingCredential.untrusted": use a certificate from a trusted CA for clients
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SOURCE_TYPES = {
    "generated": "http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia",
    "composite": "http://cv.iptc.org/newscodes/digitalsourcetype/compositeWithTrainedAlgorithmicMedia",
}


def tool():
    t = os.environ.get("C2PATOOL") or shutil.which("c2patool")
    if not t:
        sys.exit("c2patool not found: install it from github.com/contentauth/c2pa-rs (releases), or set C2PATOOL")
    return t


def read(path):
    r = subprocess.run([tool(), str(path)], capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return None


def sign(a):
    actions = []
    if a.ai in SOURCE_TYPES:
        actions.append({"action": "c2pa.created", "digitalSourceType": SOURCE_TYPES[a.ai],
                        "softwareAgent": {"name": a.tools or "generative models (see the prompt log)"}})
    else:
        actions.append({"action": "c2pa.edited", "softwareAgent": {"name": a.tools or "AI editing tools"}})
    m = {"claim_generator_info": [{"name": "ai-video-lab pipeline", "version": "1.0"}], "title": a.title,
         "alg": a.alg, "private_key": str(Path(a.key).resolve()), "sign_cert": str(Path(a.cert).resolve()),
         "assertions": [{"label": "c2pa.actions.v2", "data": {"actions": actions}},
                        {"label": "stds.schema-org.CreativeWork",
                         "data": {"@context": "https://schema.org", "@type": "CreativeWork",
                                  "author": [{"@type": "Organization", "name": a.author}]}}]}
    if a.tsa:
        m["ta_url"] = a.tsa
    tmp = Path(tempfile.mkdtemp()) / "manifest.json"
    tmp.write_text(json.dumps(m, indent=2))
    r = subprocess.run([tool(), a.file, "-m", str(tmp), "-o", a.out, "-f"], capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"signing failed: {r.stderr[-600:]}")
    v = verify_state(a.out)
    print(json.dumps({"signed": a.out, **v}, indent=2))


def verify_state(path):
    d = read(path)
    if not d:
        return {"state": "NO MANIFEST", "problems": ["no content credentials in the file"]}
    m = d["manifests"][d["active_manifest"]]
    codes = [s.get("code") for s in d.get("validation_status", [])]
    actions = [x for a in m["assertions"] if a["label"].startswith("c2pa.actions") for x in a["data"].get("actions", [])]
    return {"state": d.get("validation_state", "?"), "codes": codes, "title": m.get("title"),
            "issuer": m.get("signature_info", {}).get("issuer"),
            "ai_source": [x.get("digitalSourceType", "").rsplit("/", 1)[-1] for x in actions if x.get("digitalSourceType")]}


def gate(a):
    v = verify_state(a.file)
    rec = json.loads(Path(a.record).read_text()) if a.record else {}
    problems = []
    if v["state"] not in ("Valid", "Trusted"):
        problems.append(f"content credentials: {v['state']} {v.get('codes', '')}")
    if "signingCredential.untrusted" in v.get("codes", []) and not a.allow_test_cert:
        problems.append("signed with an untrusted (test) certificate; use the studio certificate for deliveries")
    disc = rec.get("disclosure", {})
    if rec.get("realistic_people_or_events") and not disc.get("visible_label"):
        problems.append("realistic synthetic people or events: a visible AI label is required (EU AI Act Art. 50 deployer duty)")
    if rec.get("platforms") and not disc.get("platform_setting"):
        problems.append("the platform's synthetic-content setting is not recorded as set")
    for log in ("prompt_log", "rights_log"):
        if rec and not rec.get(log):
            problems.append(f"{log} missing from the asset record")
    print(json.dumps({"file": a.file, "credentials": v, "problems": problems, "result": "PASS" if not problems else "FAIL"}, indent=2))
    sys.exit(0 if not problems else 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sign")
    s.add_argument("file")
    s.add_argument("--out", required=True)
    s.add_argument("--title", required=True)
    s.add_argument("--author", required=True)
    s.add_argument("--ai", choices=["generated", "composite", "edited"], required=True)
    s.add_argument("--tools", help="names of the AI tools, for the softwareAgent field")
    s.add_argument("--cert", required=True)
    s.add_argument("--key", required=True)
    s.add_argument("--alg", default="es256")
    s.add_argument("--tsa", help="a time-stamp authority URL (recommended for deliveries)")
    v = sub.add_parser("verify")
    v.add_argument("file")
    g = sub.add_parser("gate")
    g.add_argument("file")
    g.add_argument("--record")
    g.add_argument("--allow-test-cert", action="store_true")
    a = ap.parse_args()
    if a.cmd == "sign":
        sign(a)
    elif a.cmd == "verify":
        print(json.dumps(verify_state(a.file), indent=2))
    else:
        gate(a)


if __name__ == "__main__":
    main()
