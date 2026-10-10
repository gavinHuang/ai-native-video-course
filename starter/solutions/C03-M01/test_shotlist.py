import json, subprocess, sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).parent))
import shotlist as s

GOOD = json.loads((Path(__file__).parent / "examples.json").read_text())


def fake(*replies):
    seq = list(replies)
    return lambda system, messages: seq[min(sum(m["role"] == "assistant" for m in messages), len(seq) - 1)]


def test_valid_first_try():
    sl, n = s.run("t", 7, fake(json.dumps(GOOD)))
    assert n == 0 and len(sl.shots) == 2


def test_repairs_schema_error():
    bad = json.loads(json.dumps(GOOD)); bad["shots"][0]["size"] = "close"
    sl, n = s.run("t", 7, fake(json.dumps(bad), json.dumps(GOOD)))
    assert n == 1


def test_repairs_duration():
    long = json.loads(json.dumps(GOOD)); long["shots"][1]["duration_s"] = 12
    assert any("route limit" in p for p in s.checks(s.ShotList.model_validate(long), 15))
    assert any("total duration" in p for p in s.checks(s.ShotList.model_validate(GOOD), 30))


def test_prose_around_json():
    sl, n = s.run("t", 7, fake("Here is the list:\n" + json.dumps(GOOD) + "\nDone."))
    assert n == 0


def test_gives_up():
    with pytest.raises(SystemExit):
        s.run("t", 60, fake(json.dumps(GOOD)), max_repairs=1)
