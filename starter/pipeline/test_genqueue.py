"""Tests for genqueue.py. Run: pytest -q test_genqueue.py  (no network, no GPU)."""
import importlib
import json
import random
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))


@pytest.fixture
def q(tmp_path, monkeypatch):
    monkeypatch.setenv("GENQUEUE_DB", str(tmp_path / "q.sqlite"))
    monkeypatch.setenv("GENQUEUE_TOTAL_CAP_USD", "5")
    import genqueue
    importlib.reload(genqueue)
    return genqueue


def run_until_done(q, max_rounds=20):
    """Advance a fake clock: process due jobs, then jump to the next due time."""
    con = q.db()
    now = time.time()
    events = []
    for _ in range(max_rounds):
        events += q.work_once(now=now)
        row = con.execute("SELECT MIN(next_at) FROM jobs WHERE state IN ('queued','running')").fetchone()[0]
        if row is None:
            break
        now = max(now, row) + 0.001
    return events


def test_success(q, monkeypatch):
    monkeypatch.setenv("FAKE_PLAN", "ok")
    j = q.submit("S07.p1.g1", "fake", {"seconds": 6})
    assert j["estimate"] == 0.6
    assert run_until_done(q)[-1] == ("S07.p1.g1", "succeeded")


def test_idempotent_submit(q, monkeypatch):
    monkeypatch.setenv("FAKE_PLAN", "ok")
    q.submit("S07.p1.g1", "fake", {"seconds": 6})
    again = q.submit("S07.p1.g1", "fake", {"seconds": 6})
    assert "existing job" in again["note"]
    assert q.db().execute("SELECT COUNT(*) FROM jobs").fetchone()[0] == 1


def test_retry_after_and_backoff(q, monkeypatch):
    monkeypatch.setenv("FAKE_PLAN", "429,500,ok")
    q.submit("S08.p1.g1", "fake", {"seconds": 4})
    ev = run_until_done(q)
    assert ev[0][1].startswith("retry in") and float(ev[0][1].split()[2]) >= 2.0  # Retry-After 2 s respected
    assert ev[-1] == ("S08.p1.g1", "succeeded")
    assert q.db().execute("SELECT tries FROM jobs").fetchone()[0] == 3


def test_dead_letter_after_max_tries(q, monkeypatch):
    monkeypatch.setenv("FAKE_PLAN", "500")
    q.submit("S09.p1.g1", "fake", {"seconds": 4}, max_tries=3)
    ev = run_until_done(q)
    assert ev[-1] == ("S09.p1.g1", "dead")
    assert q.db().execute("SELECT tries FROM jobs").fetchone()[0] == 3


def test_permanent_error_no_retry(q, monkeypatch):
    monkeypatch.setenv("FAKE_PLAN", "bad")
    q.submit("S10.p1.g1", "fake", {"seconds": 4})
    assert run_until_done(q) == [("S10.p1.g1", "dead (permanent)")]


def test_shot_cap_refuses_before_spending(q, monkeypatch):
    monkeypatch.setenv("FAKE_PLAN", "ok")
    q.submit("S11.p1.g1", "fake", {"seconds": 6}, cap=1.0)
    run_until_done(q)
    with pytest.raises(SystemExit, match="cap US\\$1.00"):
        q.submit("S11.p1.g2", "fake", {"seconds": 6}, cap=1.0)


def test_total_cap(q, monkeypatch):
    monkeypatch.setenv("FAKE_PLAN", "ok")
    for i in range(8):
        q.submit(f"S{20 + i}.p1.g1", "fake", {"seconds": 6})   # 8 x 0.60 = 4.80 <= 5.00
    with pytest.raises(SystemExit, match="total cap"):
        q.submit("S99.p1.g1", "fake", {"seconds": 6})


def test_backoff_has_jitter_and_cap(q):
    rng = random.Random(1).random
    waits = [q.backoff(t, base=2, cap_s=30, rng=rng) for t in range(1, 10)]
    assert all(0 <= w <= 30 for w in waits)
    assert len(set(round(w, 3) for w in waits)) == len(waits)   # random spread, no thundering herd
