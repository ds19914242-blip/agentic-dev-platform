#!/usr/bin/env python3
"""Unit tests for console.jobs.reconcile_interrupted (Phase 2b recovery).

Hermetic: builds a throwaway backlog dir with .console_runs.json files. Run:

    python3 webui/tests/test_reconcile.py
"""
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
WEBUI = os.path.dirname(HERE)
sys.path.insert(0, WEBUI)

from console import jobs  # noqa: E402

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("  \033[32mPASS\033[0m " if cond else "  \033[31mFAIL\033[0m ") + name +
          (("" if cond else (" — " + detail)) if detail else ""))


def _write(backlog, epic, data):
    ed = Path(backlog) / epic
    ed.mkdir(parents=True, exist_ok=True)
    (ed / ".console_runs.json").write_text(json.dumps(data, ensure_ascii=False, indent=2))


def _read(backlog, epic):
    return json.loads((Path(backlog) / epic / ".console_runs.json").read_text())


def test_flips_running_only():
    with tempfile.TemporaryDirectory() as d:
        _write(d, "epicA", {
            "task-001.md": {"state": "running", "branch": "b"},
            "task-002.md": {"state": "accepted"},
            "task-003.md": {"state": "implemented"},
            "task-004.md": {"state": "running"},
            "__epic__": {"assembled": True, "state": "running"},  # must NOT be touched
        })
        n = jobs.reconcile_interrupted(d, now="2026-06-15 21:00:00")
        data = _read(d, "epicA")
        check("returns count of flipped tasks", n == 2, f"n={n}")
        check("running task -> interrupted", data["task-001.md"]["state"] == "interrupted")
        check("interrupted_at stamped", data["task-001.md"]["interrupted_at"] == "2026-06-15 21:00:00")
        check("second running task flipped", data["task-004.md"]["state"] == "interrupted")
        check("accepted untouched", data["task-002.md"]["state"] == "accepted")
        check("implemented untouched", data["task-003.md"]["state"] == "implemented")
        check("__epic__ NEVER touched (task-level only)", data["__epic__"]["state"] == "running")


def test_idempotent():
    with tempfile.TemporaryDirectory() as d:
        _write(d, "epicB", {"task-001.md": {"state": "running"}})
        n1 = jobs.reconcile_interrupted(d)
        n2 = jobs.reconcile_interrupted(d)  # second pass: nothing left running
        check("first pass flips one", n1 == 1)
        check("second pass flips nothing (idempotent)", n2 == 0)
        check("stays interrupted", _read(d, "epicB")["task-001.md"]["state"] == "interrupted")


def test_multiple_epics_and_robustness():
    with tempfile.TemporaryDirectory() as d:
        _write(d, "epicC", {"task-001.md": {"state": "running"}})
        _write(d, "epicD", {"task-001.md": {"state": "running"}, "task-002.md": {"state": "running"}})
        # a corrupt file must be skipped, not crash the scan
        ed = Path(d) / "epicE"
        ed.mkdir()
        (ed / ".console_runs.json").write_text("{ this is not json")
        n = jobs.reconcile_interrupted(d)
        check("counts across epics, skips corrupt", n == 3, f"n={n}")


def test_empty_backlog():
    with tempfile.TemporaryDirectory() as d:
        check("missing backlog dir returns 0", jobs.reconcile_interrupted(Path(d) / "nope") == 0)
        check("empty backlog returns 0", jobs.reconcile_interrupted(d) == 0)


def main():
    for t in (test_flips_running_only, test_idempotent,
              test_multiple_epics_and_robustness, test_empty_backlog):
        print(t.__name__ + ":")
        try:
            t()
        except Exception as exc:
            FAIL.append(t.__name__)
            print("  \033[31mERROR\033[0m", t.__name__, "—", exc)
    print()
    print(f"reconcile: {len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        for n in FAIL:
            print("  -", n)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
