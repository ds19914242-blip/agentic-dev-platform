#!/usr/bin/env python3
"""Unit tests for console.jobs — the background job machinery.

Hermetic: no server, no network. Runs targets in real daemon threads and waits
briefly for completion. Run:

    python3 webui/tests/test_jobs.py
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
WEBUI = os.path.dirname(HERE)
sys.path.insert(0, WEBUI)

from console import jobs  # noqa: E402

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("  \033[32mPASS\033[0m " if cond else "  \033[31mFAIL\033[0m ") + name +
          (("" if cond else (" — " + detail)) if detail else ""))


def wait_done(job, timeout=3.0):
    t0 = time.time()
    while not job.done and time.time() - t0 < timeout:
        time.sleep(0.02)
    return job.done


def test_emit_snapshot():
    j = jobs.Job("test", ("k",))
    j.emit("one")
    j.emit("two", "err")
    lines, done, result = j.snapshot(0)
    check("emit accumulates", len(lines) == 2 and lines[0]["msg"] == "one")
    check("emit carries level", lines[1]["level"] == "err")
    check("snapshot offset works", j.snapshot(1)[0][0]["msg"] == "two")
    check("fresh job not done", done is False and result is None)


def test_start_and_result():
    def target(job):
        job.emit("working")
        return {"ok": True, "value": 42}
    job, started = jobs.start_job("unit", ("start", "a"), target)
    check("start_job returns started=True", started is True)
    check("completes", wait_done(job), "job did not finish")
    check("result captured", job.result == {"ok": True, "value": 42}, str(job.result))
    msgs = [l["msg"] for l in job.snapshot(0)[0]]
    check("dispatched + done emitted", "unit: dispatched" in msgs and "done" in msgs)
    check("target emit present", "working" in msgs)


def test_exception_becomes_error_result():
    def boom(job):
        raise ValueError("nope")
    job, _ = jobs.start_job("unit", ("start", "boom"), boom)
    check("error job completes", wait_done(job))
    check("error captured in result", job.result.get("ok") is False and "nope" in (job.result.get("error") or ""))


def test_inflight_dedup():
    gate = {"go": False}
    def slow(job):
        while not gate["go"]:
            time.sleep(0.01)
        return {"ok": True}
    key = ("dedup", "same")
    j1, s1 = jobs.start_job("unit", key, slow)
    j2, s2 = jobs.start_job("unit", key, slow)  # same key, j1 still running
    check("second call dedups (started=False)", s2 is False)
    check("dedup returns the same job", j1.id == j2.id)
    gate["go"] = True
    check("slow job finishes", wait_done(j1))
    # after completion, a new call with same key starts fresh
    j3, s3 = jobs.start_job("unit", key, lambda job: {"ok": True})
    check("new job after completion (started=True)", s3 is True and j3.id != j1.id)
    wait_done(j3)


def test_forward():
    def action(x):
        return {"ok": True, "x": x, "log": [{"msg": "line1", "level": ""},
                                            {"msg": "line2", "level": "ok"}]}
    target = jobs._forward(action, 7)
    j = jobs.Job("unit", ("fwd",))
    out = target(j)
    check("_forward strips log from result", "log" not in out and out["x"] == 7)
    msgs = [l["msg"] for l in j.snapshot(0)[0]]
    check("_forward streams log lines to job", msgs == ["line1", "line2"])


def main():
    for t in (test_emit_snapshot, test_start_and_result, test_exception_becomes_error_result,
              test_inflight_dedup, test_forward):
        print(t.__name__ + ":")
        try:
            t()
        except Exception as exc:
            FAIL.append(t.__name__)
            print("  \033[31mERROR\033[0m", t.__name__, "—", exc)
    print()
    print(f"jobs: {len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        for n in FAIL:
            print("  -", n)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
