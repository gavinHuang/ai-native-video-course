#!/usr/bin/env python3
"""Run an API-format ComfyUI workflow with named inputs. Reference solution for C11·M04.

Try the lab yourself first. Then compare your client with this one.

Usage:
  python comfy_run.py --workflow 03_i2v_wan22_5b.json --map 03_i2v_wan22_5b.map.json \
      --set prompt="She looks up, surprised." --set seed=1234 --upload start_image=KF-S07-v3.png \
      --out renders/ --log runs.jsonl

  --set name=value      set a named input (from the map file). Numbers and true/false are converted.
  --upload name=file    upload a local image/audio/video file, then set the named input to it.
  --server URL          default http://127.0.0.1:8188 (or the COMFY_SERVER environment variable)
  --timeout S           total time limit for one job (default 1800 s)

Exit codes: 0 = done, 2 = bad input, 3 = server rejected the workflow, 4 = execution error, 5 = timeout.
"""
import argparse
import copy
import hashlib
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

try:
    import websocket  # pip install websocket-client
except ImportError:  # the client still works: it polls /history instead
    websocket = None


class ComfyError(Exception):
    def __init__(self, msg, code):
        super().__init__(msg)
        self.code = code


def http_json(url, data=None, timeout=60):
    body = None if data is None else json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        raise ComfyError(f"HTTP {e.code} from {url}: {detail[:2000]}", 3) from None


def upload(server, path, kind):
    """Upload a file with multipart/form-data. Returns the name to put in the workflow."""
    p = Path(path)
    if not p.is_file():
        raise ComfyError(f"file not found: {path}", 2)
    boundary = uuid.uuid4().hex
    ctype = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
    parts = [
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n".encode(),
        (f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{p.name}\"\r\n"
         f"Content-Type: {ctype}\r\n\r\n").encode() + p.read_bytes() + b"\r\n",
        f"--{boundary}--\r\n".encode(),
    ]
    req = urllib.request.Request(f"{server}/upload/image", data=b"".join(parts),
                                 headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    with urllib.request.urlopen(req, timeout=300) as r:
        info = json.load(r)
    return f"{info['subfolder']}/{info['name']}" if info.get("subfolder") else info["name"]


def parse_value(raw):
    if raw.lower() in ("true", "false"):
        return raw.lower() == "true"
    for cast in (int, float):
        try:
            return cast(raw)
        except ValueError:
            pass
    return raw


def set_input(wf, mapping, name, value):
    if name not in mapping:
        raise ComfyError(f"unknown input '{name}'. Known: {', '.join(sorted(mapping))}", 2)
    nid, key = mapping[name].split(".", 1)
    if nid not in wf:
        raise ComfyError(f"map points to node {nid}, which is not in the workflow", 2)
    old = wf[nid]["inputs"].get(key)
    if isinstance(old, list):
        raise ComfyError(f"input '{name}' ({mapping[name]}) is a link in this workflow; it cannot be set", 2)
    wf[nid]["inputs"][key] = value


def wait_ws(server, client_id, prompt_id, deadline):
    url = server.replace("http", "ws", 1) + f"/ws?clientId={client_id}"
    ws = websocket.create_connection(url, timeout=30)
    try:
        while time.time() < deadline:
            try:
                raw = ws.recv()
            except websocket.WebSocketTimeoutException:
                continue
            if not isinstance(raw, str):
                continue  # binary preview image
            msg = json.loads(raw)
            data = msg.get("data", {})
            if data.get("prompt_id") not in (None, prompt_id):
                continue
            t = msg.get("type")
            if t == "progress":
                print(f"\r  step {data.get('value')}/{data.get('max')}", end="", file=sys.stderr)
            elif t == "execution_error":
                raise ComfyError(f"execution error in node {data.get('node_id')} ({data.get('node_type')}): "
                                 f"{data.get('exception_message', '').strip()}", 4)
            elif t == "execution_interrupted":
                raise ComfyError("the job was interrupted", 4)
            elif t == "executing" and data.get("node") is None and data.get("prompt_id") == prompt_id:
                print(file=sys.stderr)
                return
        raise ComfyError("timeout", 5)
    finally:
        ws.close()


def wait_poll(server, prompt_id, deadline):
    while time.time() < deadline:
        h = http_json(f"{server}/history/{prompt_id}")
        if prompt_id in h:
            st = h[prompt_id].get("status", {})
            if st.get("status_str") == "error":
                msgs = [m for m in st.get("messages", []) if m[0] == "execution_error"]
                detail = msgs[0][1].get("exception_message", "") if msgs else ""
                raise ComfyError(f"execution error: {detail.strip()}", 4)
            if st.get("completed", True):
                return
        time.sleep(2)
    raise ComfyError("timeout", 5)


def download_outputs(server, history, out_dir):
    files = []
    out_dir.mkdir(parents=True, exist_ok=True)
    for node_id, out in history.get("outputs", {}).items():
        for key in ("images", "videos", "gifs", "audio"):
            for item in out.get(key, []):
                if item.get("type") == "temp":
                    continue  # previews
                q = urllib.parse.urlencode({k: item.get(k, "") for k in ("filename", "subfolder", "type")})
                dest = out_dir / item["filename"]
                with urllib.request.urlopen(f"{server}/view?{q}", timeout=300) as r:
                    dest.write_bytes(r.read())
                files.append(str(dest))
    return files


def run(args):
    server = args.server.rstrip("/")
    template = json.loads(Path(args.workflow).read_text())
    mapping = json.loads(Path(args.map).read_text()) if args.map else {}
    wf = copy.deepcopy(template)  # never change the template file
    values = {}
    for item in args.set:
        name, _, raw = item.partition("=")
        values[name] = parse_value(raw)
        set_input(wf, mapping, name, values[name])
    for item in args.upload:
        name, _, path = item.partition("=")
        remote = upload(server, path, "image")
        values[name] = remote
        set_input(wf, mapping, name, remote)

    client_id = str(uuid.uuid4())
    t0 = time.time()
    resp = http_json(f"{server}/prompt", {"prompt": wf, "client_id": client_id})
    if resp.get("node_errors"):
        raise ComfyError(f"node errors: {json.dumps(resp['node_errors'])[:2000]}", 3)
    prompt_id = resp["prompt_id"]
    print(f"queued {prompt_id}", file=sys.stderr)
    deadline = t0 + args.timeout
    if websocket is not None:
        wait_ws(server, client_id, prompt_id, deadline)
    else:
        wait_poll(server, prompt_id, deadline)
    history = http_json(f"{server}/history/{prompt_id}")[prompt_id]
    files = download_outputs(server, history, Path(args.out))
    stats = http_json(f"{server}/system_stats")
    record = {
        "time": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "prompt_id": prompt_id,
        "workflow": args.workflow,
        "workflow_sha256": hashlib.sha256(Path(args.workflow).read_bytes()).hexdigest(),
        "inputs": values,
        "seconds": round(time.time() - t0, 1),
        "outputs": files,
        "comfyui_version": stats.get("system", {}).get("comfyui_version"),
        "pytorch_version": stats.get("system", {}).get("pytorch_version"),
        "devices": [d.get("name") for d in stats.get("devices", [])],
    }
    if args.log:
        with open(args.log, "a") as f:
            f.write(json.dumps(record) + "\n")
    print(json.dumps(record, indent=2))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--workflow", required=True)
    ap.add_argument("--map")
    ap.add_argument("--set", action="append", default=[])
    ap.add_argument("--upload", action="append", default=[])
    ap.add_argument("--server", default=os.environ.get("COMFY_SERVER", "http://127.0.0.1:8188"))
    ap.add_argument("--out", default="renders")
    ap.add_argument("--log", default="runs.jsonl")
    ap.add_argument("--timeout", type=float, default=1800)
    args = ap.parse_args()
    try:
        run(args)
    except ComfyError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(e.code)
    except urllib.error.URLError as e:
        print(f"ERROR: cannot reach the server {args.server}: {e.reason}", file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()
