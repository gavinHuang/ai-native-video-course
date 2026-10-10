"""Tests for comfy_run.py. They need a running ComfyUI server; a CPU-only server is enough.

  python main.py --cpu --port 8188          # in the ComfyUI folder
  COMFY_SERVER=http://127.0.0.1:8188 pytest -q test_comfy_run.py

The smoke workflow (LoadImage -> ImageInvert -> SaveImage) needs no model files, so these tests
can run in CI on a machine without a GPU.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
CLIENT = HERE / "comfy_run.py"
WF = HERE.parent.parent / "comfyui" / "workflows" / "test" / "00_smoke_cpu.json"
MAP = WF.with_suffix(".map.json")
SERVER = os.environ.get("COMFY_SERVER", "http://127.0.0.1:8188")


def run(*args, tmp):
    cmd = [sys.executable, str(CLIENT), "--server", SERVER, "--out", str(tmp / "out"), "--log", str(tmp / "runs.jsonl"), *args]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=120)


@pytest.fixture
def png(tmp_path):
    # A 2 x 2 PNG made without extra libraries.
    import struct
    import zlib

    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    raw = b"".join(b"\x00" + bytes([200, 30, 30] * 2) for _ in range(2))
    data = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 2, 2, 8, 2, 0, 0, 0)) + \
        chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")
    p = tmp_path / "in.png"
    p.write_bytes(data)
    return p


def test_run_and_log(tmp_path, png):
    r = run("--workflow", str(WF), "--map", str(MAP), "--upload", f"image={png}",
            "--set", "filename_prefix=test/smoke", tmp=tmp_path)
    assert r.returncode == 0, r.stderr
    rec = json.loads(r.stdout)
    assert len(rec["outputs"]) == 1 and Path(rec["outputs"][0]).stat().st_size > 0
    log = [json.loads(line) for line in (tmp_path / "runs.jsonl").read_text().splitlines()]
    for field in ("workflow_sha256", "inputs", "comfyui_version", "devices", "seconds"):
        assert field in log[-1]


def test_template_not_changed(tmp_path, png):
    before = WF.read_bytes()
    run("--workflow", str(WF), "--map", str(MAP), "--upload", f"image={png}", tmp=tmp_path)
    assert WF.read_bytes() == before


def test_unknown_input_name(tmp_path):
    r = run("--workflow", str(WF), "--map", str(MAP), "--set", "promt=x", tmp=tmp_path)
    assert r.returncode == 2 and "unknown input 'promt'" in r.stderr


def test_server_rejects_bad_value(tmp_path):
    r = run("--workflow", str(WF), "--map", str(MAP), "--set", "image=does_not_exist.png", tmp=tmp_path)
    assert r.returncode == 3, r.stderr


def test_missing_upload_file(tmp_path):
    r = run("--workflow", str(WF), "--map", str(MAP), "--upload", "image=nope.png", tmp=tmp_path)
    assert r.returncode == 2
