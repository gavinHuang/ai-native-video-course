#!/usr/bin/env python3
"""A small, reliable generation queue (C12·M01). SQLite; no server needed.

Features that every production pipeline needs, in about 300 lines you can read:
  - idempotency keys: submitting the same key twice returns the same job, never a second paid generation
  - retries with exponential backoff and full jitter; respects a backend's Retry-After
  - a per-job timeout; a dead-letter state after the last try, for human review
  - budget guards: per-shot cap and total cap, checked BEFORE a job is sent
  - one backend interface, so a vendor change is a config change

  python genqueue.py submit S07.p2.g4 --backend fake --inputs '{"prompt": "...", "seconds": 6}' --cap 3.0
  python genqueue.py work --once                     # process due jobs (run it in a loop or a cron job)
  python genqueue.py status [JOB]                    # list jobs or show one
  python genqueue.py dead                            # jobs that need a person

Backends: "fake" (for tests: configurable failures, 429s, latency, price) and "comfy" (the C11 starter client).
Add a vendor by writing a class with estimate(), submit(), poll() — see Backend below.
"""
import argparse
import json
import os
import random
import sqlite3
import sys
import time
from pathlib import Path

DB = Path(os.environ.get("GENQUEUE_DB", "genqueue.sqlite"))
TOTAL_CAP = float(os.environ.get("GENQUEUE_TOTAL_CAP_USD", "100"))


class TransientError(Exception):
    """Retry later (rate limit, 5xx, network). retry_after: seconds the backend asked for, if any."""
    def __init__(self, msg, retry_after=None):
        super().__init__(msg)
        self.retry_after = retry_after


class PermanentError(Exception):
    """Do not retry (bad input, content policy, unknown model)."""


class Backend:
    """Interface for a generation backend. submit() returns a remote id; poll() returns (state, result)."""
    def estimate(self, inputs):  # US$
        raise NotImplementedError

    def submit(self, inputs):
        raise NotImplementedError

    def poll(self, remote_id):  # -> ("running" | "succeeded" | "failed", result dict | error str)
        raise NotImplementedError


class FakeBackend(Backend):
    """Deterministic test backend. FAKE_PLAN env: comma list of outcomes per submit call, for example
    "429,ok,500,ok" (429 = rate limit with Retry-After 2 s, 500 = transient, bad = permanent, ok = success)."""
    price_per_s = 0.10

    def __init__(self):
        self.state_file = DB.with_suffix(".fake.json")

    def _load(self):
        return json.loads(self.state_file.read_text()) if self.state_file.exists() else {"calls": 0, "jobs": {}}

    def estimate(self, inputs):
        return round(self.price_per_s * float(inputs.get("seconds", 5)), 2)

    def submit(self, inputs):
        st = self._load()
        plan = os.environ.get("FAKE_PLAN", "ok").split(",")
        outcome = plan[min(st["calls"], len(plan) - 1)]
        st["calls"] += 1
        self.state_file.write_text(json.dumps(st))
        if outcome == "429":
            raise TransientError("rate limited (HTTP 429)", retry_after=2)
        if outcome == "500":
            raise TransientError("server error (HTTP 500)")
        if outcome == "bad":
            raise PermanentError("input rejected by content policy")
        rid = f"fake-{st['calls']}"
        st["jobs"][rid] = time.time()
        self.state_file.write_text(json.dumps(st))
        return rid

    def poll(self, remote_id):
        return "succeeded", {"url": f"https://example.invalid/{remote_id}.mp4", "seconds": 6}


class ComfyBackend(Backend):
    """Runs a starter workflow through the C11 client (synchronously, inside submit)."""
    def estimate(self, inputs):
        return float(inputs.get("estimate_usd", 0.0))  # your own GPU: time, not per-call price

    def submit(self, inputs):
        import subprocess
        client = Path(__file__).resolve().parent.parent / "solutions" / "C11-M04" / "comfy_run.py"
        cmd = [sys.executable, str(client), "--workflow", inputs["workflow"], "--map", inputs["map"]]
        for k, v in inputs.get("set", {}).items():
            cmd += ["--set", f"{k}={v}"]
        for k, v in inputs.get("upload", {}).items():
            cmd += ["--upload", f"{k}={v}"]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode in (3, 5):
            raise TransientError(r.stderr.strip()[-300:])
        if r.returncode:
            raise PermanentError(r.stderr.strip()[-300:])
        self._last = json.loads(r.stdout)
        return self._last["prompt_id"]

    def poll(self, remote_id):
        return "succeeded", getattr(self, "_last", {})


BACKENDS = {"fake": FakeBackend, "comfy": ComfyBackend}


def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    con.execute("""CREATE TABLE IF NOT EXISTS jobs (
        key TEXT PRIMARY KEY, shot TEXT, backend TEXT, inputs TEXT, state TEXT, tries INTEGER DEFAULT 0,
        max_tries INTEGER, next_at REAL, created REAL, updated REAL, remote_id TEXT, result TEXT,
        error TEXT, estimate REAL, cost REAL DEFAULT 0, cap REAL, timeout_s REAL, started REAL)""")
    con.execute("CREATE TABLE IF NOT EXISTS events (t REAL, key TEXT, event TEXT, detail TEXT)")
    return con


def log(con, key, event, detail=""):
    con.execute("INSERT INTO events VALUES (?,?,?,?)", (time.time(), key, event, detail))


def submit(key, backend, inputs, cap=None, max_tries=5, timeout_s=1800):
    """Add a job. Same key again = the same job (idempotent). Budget checked here, before any money is spent."""
    con = db()
    row = con.execute("SELECT * FROM jobs WHERE key=?", (key,)).fetchone()
    if row:
        return dict(row) | {"note": "existing job (idempotent submit)"}
    be = BACKENDS[backend]()
    est = be.estimate(inputs)
    shot = key.split(".")[0]
    spent_shot = con.execute("SELECT COALESCE(SUM(cost),0)+COALESCE(SUM(CASE WHEN state IN ('queued','running') THEN estimate END),0) "
                             "FROM jobs WHERE shot=?", (shot,)).fetchone()[0]
    spent_all = con.execute("SELECT COALESCE(SUM(cost),0)+COALESCE(SUM(CASE WHEN state IN ('queued','running') THEN estimate END),0) "
                            "FROM jobs").fetchone()[0]
    if cap is not None and spent_shot + est > cap:
        raise SystemExit(f"REFUSED {key}: shot {shot} would reach US${spent_shot + est:.2f}, cap US${cap:.2f}. Change the approach (C05·M06).")
    if spent_all + est > TOTAL_CAP:
        raise SystemExit(f"REFUSED {key}: total would reach US${spent_all + est:.2f}, total cap US${TOTAL_CAP:.2f}.")
    now = time.time()
    con.execute("INSERT INTO jobs (key, shot, backend, inputs, state, max_tries, next_at, created, updated, estimate, cap, timeout_s) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (key, shot, backend, json.dumps(inputs), "queued", max_tries, now, now, now, est, cap, timeout_s))
    log(con, key, "submitted", f"estimate {est}")
    con.commit()
    return dict(con.execute("SELECT * FROM jobs WHERE key=?", (key,)).fetchone())


def backoff(tries, base=2.0, cap_s=300.0, retry_after=None, rng=random.random):
    """Exponential backoff with full jitter: a random wait between 0 and min(cap, base * 2^tries).
    A Retry-After from the server is a minimum."""
    w = rng() * min(cap_s, base * (2 ** tries))
    return max(w, retry_after or 0)


def work_once(now=None, sleep=False):
    """Process every due job once. Returns a list of (key, event)."""
    con = db()
    now = now or time.time()
    done = []
    for row in con.execute("SELECT * FROM jobs WHERE state IN ('queued','running') AND next_at<=? ORDER BY created", (now,)).fetchall():
        key, be = row["key"], BACKENDS[row["backend"]]()
        inputs = json.loads(row["inputs"])
        if row["state"] == "running" and row["started"] and now - row["started"] > row["timeout_s"]:
            con.execute("UPDATE jobs SET state='queued', remote_id=NULL, updated=? WHERE key=?", (now, key))
            log(con, key, "timeout", f"after {row['timeout_s']} s; resubmit")
            done.append((key, "timeout"))
            continue
        try:
            if row["state"] == "queued":
                rid = be.submit(inputs)
                con.execute("UPDATE jobs SET state='running', remote_id=?, tries=tries+1, started=?, updated=? WHERE key=?",
                            (rid, now, now, key))
                log(con, key, "sent", rid)
                row = con.execute("SELECT * FROM jobs WHERE key=?", (key,)).fetchone()
            state, res = be.poll(row["remote_id"])
            if state == "succeeded":
                cost = row["estimate"]
                con.execute("UPDATE jobs SET state='succeeded', result=?, cost=?, updated=? WHERE key=?", (json.dumps(res), cost, now, key))
                log(con, key, "succeeded", f"cost {cost}")
                done.append((key, "succeeded"))
            elif state == "failed":
                raise TransientError(str(res))
        except TransientError as e:
            tries = con.execute("SELECT tries FROM jobs WHERE key=?", (key,)).fetchone()[0]
            if row["state"] == "queued":
                tries += 1
            if tries >= row["max_tries"]:
                con.execute("UPDATE jobs SET state='dead', tries=?, error=?, updated=? WHERE key=?", (tries, str(e), now, key))
                log(con, key, "dead", str(e))
                done.append((key, "dead"))
            else:
                wait = backoff(tries, retry_after=e.retry_after)
                con.execute("UPDATE jobs SET state='queued', tries=?, error=?, next_at=?, updated=? WHERE key=?",
                            (tries, str(e), now + wait, now, key))
                log(con, key, "retry", f"{e}; wait {wait:.1f} s")
                done.append((key, f"retry in {wait:.1f} s"))
        except PermanentError as e:
            con.execute("UPDATE jobs SET state='dead', error=?, updated=? WHERE key=?", (str(e), now, key))
            log(con, key, "dead", f"permanent: {e}")
            done.append((key, "dead (permanent)"))
        con.commit()
    return done


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("submit")
    s.add_argument("key", help="idempotency key, for example S07.p2.g4 (shot.prompt-version.generation)")
    s.add_argument("--backend", default="fake", choices=sorted(BACKENDS))
    s.add_argument("--inputs", default="{}")
    s.add_argument("--cap", type=float, help="US$ cap for this shot (all its jobs)")
    s.add_argument("--max-tries", type=int, default=5)
    w = sub.add_parser("work")
    w.add_argument("--once", action="store_true")
    w.add_argument("--interval", type=float, default=5)
    st = sub.add_parser("status")
    st.add_argument("key", nargs="?")
    sub.add_parser("dead")
    a = ap.parse_args()
    if a.cmd == "submit":
        j = submit(a.key, a.backend, json.loads(a.inputs), a.cap, a.max_tries)
        print(json.dumps({k: j[k] for k in ("key", "state", "estimate")} | ({"note": j["note"]} if "note" in j else {})))
    elif a.cmd == "work":
        while True:
            for key, ev in work_once():
                print(f"{key}: {ev}")
            if a.once:
                break
            time.sleep(a.interval)
    elif a.cmd == "status":
        con = db()
        if a.key:
            print(json.dumps(dict(con.execute("SELECT * FROM jobs WHERE key=?", (a.key,)).fetchone() or {}), indent=2))
            for e in con.execute("SELECT * FROM events WHERE key=? ORDER BY t", (a.key,)):
                print(f"  {time.strftime('%H:%M:%S', time.localtime(e['t']))} {e['event']:10} {e['detail']}")
        else:
            for r in con.execute("SELECT key, state, tries, estimate, cost, error FROM jobs ORDER BY created"):
                print(f"{r['key']:16} {r['state']:10} tries {r['tries']}  est US${r['estimate']:.2f}  cost US${r['cost']:.2f}  {r['error'] or ''}")
    elif a.cmd == "dead":
        for r in db().execute("SELECT key, tries, error FROM jobs WHERE state='dead'"):
            print(f"{r['key']}: after {r['tries']} tries: {r['error']}")


if __name__ == "__main__":
    main()
