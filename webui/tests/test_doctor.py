#!/usr/bin/env python3
"""Unit tests for console.doctor — pure state↔git consistency heuristics.

Hermetic: no real repo. We feed parsed facts + predicate callables. Run:

    python3 webui/tests/test_doctor.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WEBUI = os.path.dirname(HERE)
sys.path.insert(0, WEBUI)

from console import doctor  # noqa: E402

PASS, FAIL = [], []


def check(name, cond, extra=""):
    if cond:
        PASS.append(name)
        print(f"  \033[32mPASS\033[0m {name}")
    else:
        FAIL.append(name)
        print(f"  \033[31mFAIL\033[0m {name}" + (f" — {extra}" if extra else ""))


def test_classify_worktrees():
    tracked = ["/wt/a", "/wt/b"]
    existing = ["/wt/b", "/wt/c"]
    c = doctor.classify_worktrees(tracked, existing)
    check("orphan = on disk, untracked", c["orphan"] == ["/wt/c"])
    check("stale = tracked, dir gone", c["stale"] == ["/wt/a"])
    check("shared one is neither", "/wt/b" not in c["orphan"] and "/wt/b" not in c["stale"])
    empty = doctor.classify_worktrees([], [])
    check("empty -> empty", empty == {"orphan": [], "stale": []})
    check("none-safe", doctor.classify_worktrees(None, None) == {"orphan": [], "stale": []})


def test_worktree_findings():
    f = doctor.worktree_findings(["/wt/a"], ["/wt/c"])
    kinds = {x["kind"] for x in f}
    check("orphan + stale both reported", kinds == {"orphan_worktree", "stale_worktree"})
    check("worktree findings are warn", all(x["level"] == "warn" for x in f))
    check("clean repo -> no findings", doctor.worktree_findings(["/wt/a"], ["/wt/a"]) == [])


def test_ghost_epic_branch():
    es = {"assembled": True}
    gone = doctor.epic_branch_findings(es, "agentic/epic-x", lambda r: False)
    check("assembled+missing -> bad ghost", gone and gone[0]["kind"] == "ghost_epic_branch"
          and gone[0]["level"] == "bad")
    present = doctor.epic_branch_findings(es, "agentic/epic-x", lambda r: True)
    check("assembled+present -> no finding", present == [])
    not_asm = doctor.epic_branch_findings({"assembled": False}, "agentic/epic-x", lambda r: False)
    check("not assembled -> no ghost even if branch absent", not_asm == [])


def test_ghost_assembled_branch():
    es = {"assembled": True, "assembled_branch": "agentic/epic-old"}
    # epic branch present, but the recorded assembled_branch is gone
    f = doctor.epic_branch_findings(es, "agentic/epic-x",
                                    lambda r: r == "agentic/epic-x")
    kinds = {x["kind"] for x in f}
    check("recorded assembled_branch missing -> warn", "ghost_assembled_branch" in kinds)


def test_task_commit_findings():
    rs = {
        "__epic__": {"assembled": True},
        "task-001.md": {"state": "accepted", "head": "deadbeefcafe"},
        "task-002.md": {"state": "accepted", "head": "feedface0000"},
        "task-003.md": {"state": "todo"},  # no commit expected
        "task-004.md": {"state": "running"},
    }
    present = {"deadbeefcafe"}
    f = doctor.task_commit_findings(rs, lambda sha: sha in present)
    msgs = [x["msg"] for x in f]
    check("missing commit flagged", any("task-002.md" in m for m in msgs))
    check("present commit not flagged", not any("task-001.md" in m for m in msgs))
    check("todo/running tasks skipped", not any("task-003" in m or "task-004" in m for m in msgs))
    check("__epic__ key skipped", not any("__epic__" in m for m in msgs))
    check("missing-commit level is warn", all(x["level"] == "warn" for x in f))


def test_summarize():
    findings = [
        {"level": "bad", "kind": "k1", "msg": "m"},
        {"level": "warn", "kind": "k2", "msg": "m"},
        {"level": "warn", "kind": "k3", "msg": "m"},
    ]
    s = doctor.summarize(findings)
    check("counts correct", s["counts"] == {"ok": 0, "warn": 2, "bad": 1})
    check("worst = bad when any bad", s["worst"] == "bad")
    check("total", s["total"] == 3)
    check("not clean", s["clean"] is False)
    s2 = doctor.summarize([])
    check("empty -> clean ok", s2["clean"] and s2["worst"] == "ok" and s2["total"] == 0)
    s3 = doctor.summarize([{"level": "warn", "kind": "k", "msg": "m"}])
    check("warn-only -> worst warn", s3["worst"] == "warn")


def main():
    for t in (test_classify_worktrees, test_worktree_findings, test_ghost_epic_branch,
              test_ghost_assembled_branch, test_task_commit_findings, test_summarize):
        print(t.__name__ + ":")
        try:
            t()
        except Exception as exc:
            FAIL.append(t.__name__)
            print("  \033[31mERROR\033[0m", t.__name__, "—", exc)
    print()
    print(f"doctor: {len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        for n in FAIL:
            print("  -", n)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
