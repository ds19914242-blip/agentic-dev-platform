#!/usr/bin/env python3
"""Unit tests for console.state — run-state / epic-state persistence (Phase 5a).

Hermetic: a temp dir stands in for the backlog. Run:

    python3 webui/tests/test_state.py
"""
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
WEBUI = os.path.dirname(HERE)
sys.path.insert(0, WEBUI)

from console import state  # noqa: E402

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("  \033[32mPASS\033[0m " if cond else "  \033[31mFAIL\033[0m ") + name +
          (("" if cond else (" — " + detail)) if detail else ""))


def _epic(d, eid="epicA"):
    (Path(d) / eid).mkdir(parents=True, exist_ok=True)
    return eid


def test_path_and_empty():
    with tempfile.TemporaryDirectory() as d:
        p = state.runstate_path(d, "epicA")
        check("runstate_path ends with .console_runs.json", p.name == ".console_runs.json")
        check("runstate_path under epic dir", p.parent.name == "epicA")
        check("load on missing file -> {}", state.load_runstate(d, "epicA") == {})


def test_set_and_roundtrip():
    with tempfile.TemporaryDirectory() as d:
        eid = _epic(d)
        out = state.set_runstate(d, eid, "task-001.md", state="running", branch="b1")
        check("set returns the entry", out.get("state") == "running" and out.get("branch") == "b1")
        check("set stamps ts", "ts" in out)
        reread = state.load_runstate(d, eid)
        check("round-trips to disk", reread["task-001.md"]["state"] == "running")
        check("file is valid json on disk",
              isinstance(json.loads(state.runstate_path(d, eid).read_text()), dict))


def test_merge_update():
    with tempfile.TemporaryDirectory() as d:
        eid = _epic(d)
        state.set_runstate(d, eid, "task-001.md", state="implemented", head="abc", changed=["a.ts"])
        state.set_runstate(d, eid, "task-001.md", state="accepted")  # partial update
        e = state.load_runstate(d, eid)["task-001.md"]
        check("update merges (keeps head)", e.get("head") == "abc")
        check("update overrides changed field", e.get("state") == "accepted")
        check("update keeps changed list", e.get("changed") == ["a.ts"])


def test_epic_state_separation():
    with tempfile.TemporaryDirectory() as d:
        eid = _epic(d)
        state.set_runstate(d, eid, "task-001.md", state="running")
        state.set_epic_state(d, eid, assembled=True, validation="passed")
        es = state.load_epic_state(d, eid)
        check("epic state stored under __epic__", es.get("assembled") is True)
        check("epic state carries fields", es.get("validation") == "passed")
        full = state.load_runstate(d, eid)
        check("__epic__ key used", state.EPIC_KEY in full)
        check("task entry untouched by epic state", full["task-001.md"]["state"] == "running")
        check("epic state is not a task entry", state.EPIC_KEY == "__epic__")


def test_corrupt_file():
    with tempfile.TemporaryDirectory() as d:
        eid = _epic(d)
        state.runstate_path(d, eid).write_text("{ not json")
        check("corrupt file loads as {}", state.load_runstate(d, eid) == {})
        # a subsequent set overwrites the corrupt file cleanly
        state.set_runstate(d, eid, "task-001.md", state="todo")
        check("set recovers after corrupt", state.load_runstate(d, eid)["task-001.md"]["state"] == "todo")


def main():
    for t in (test_path_and_empty, test_set_and_roundtrip, test_merge_update,
              test_epic_state_separation, test_corrupt_file):
        print(t.__name__ + ":")
        try:
            t()
        except Exception as exc:
            FAIL.append(t.__name__)
            print("  \033[31mERROR\033[0m", t.__name__, "—", exc)
    print()
    print(f"state: {len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        for n in FAIL:
            print("  -", n)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
