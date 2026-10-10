"""Tests for mediakit.py with generated media (ffmpeg lavfi): no files needed. Run: pytest -q test_mediakit.py"""
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mediakit as mk  # noqa: E402


def make_clip(path, seconds=2, size="640x360", fps=24, audio=True, tone=440):
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"testsrc2=s={size}:r={fps}:d={seconds}"]
    if audio:
        cmd += ["-f", "lavfi", "-i", f"sine=f={tone}:d={seconds}", "-shortest"]
    cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", str(path)]
    subprocess.run(cmd, check=True)
    return path


def test_probe(tmp_path):
    p = mk.probe(make_clip(tmp_path / "a.mp4"))
    assert (p["width"], p["height"], p["fps"]) == (640, 360, 24.0)
    assert abs(p["duration"] - 2) < 0.1 and p["acodec"] == "aac"


def test_trim_is_frame_accurate(tmp_path):
    src = make_clip(tmp_path / "a.mp4", seconds=4)
    out = mk.trim(src, 1.0, 2.5, tmp_path / "t.mov")
    assert out["frames"] == 36  # 1.5 s at 24 fps
    assert out["pix_fmt"] == "yuv422p10le"


def test_no_overwrite(tmp_path):
    src = make_clip(tmp_path / "a.mp4")
    mk.make_proxy(src, tmp_path / "p.mp4")
    with pytest.raises(mk.MediaError, match="exists"):
        mk.make_proxy(src, tmp_path / "p.mp4")


def test_concat_mixed_inputs(tmp_path):
    a = make_clip(tmp_path / "a.mp4", seconds=1, size="640x360", fps=24)
    b = make_clip(tmp_path / "b.mp4", seconds=1, size="1280x720", fps=30, audio=False)
    out = mk.concat([a, b], tmp_path / "c.mov", fps=24)
    assert (out["width"], out["height"], out["fps"]) == (640, 360, 24.0)
    assert abs(out["duration"] - 2) < 0.1 and out["acodec"] == "pcm_s24le"


def test_loudness_and_errors(tmp_path):
    src = make_clip(tmp_path / "a.mp4", seconds=3)
    L = mk.loudness(src)
    assert -30 < L["I"] < 0 and L["TP"] < 0.5
    silent = make_clip(tmp_path / "s.mp4", audio=False)
    with pytest.raises(mk.MediaError, match="no audio"):
        mk.loudness(silent)


def test_contact_sheet(tmp_path):
    out = mk.contact_sheet(make_clip(tmp_path / "a.mp4", seconds=3), tmp_path / "sheet.png")
    assert Path(out["path"]).stat().st_size > 1000
