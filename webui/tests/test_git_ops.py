#!/usr/bin/env python3
"""Unit tests for console.git_ops — the extracted git mechanics.

Hermetic: pure functions need nothing; git-touching tests build a throwaway repo
in a temp dir. No real product, no network. Run:

    python3 webui/tests/test_git_ops.py
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
WEBUI = os.path.dirname(HERE)
sys.path.insert(0, WEBUI)  # so `from console import git_ops` resolves

from console import git_ops  # noqa: E402

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("  \033[32mPASS\033[0m " if cond else "  \033[31mFAIL\033[0m ") + name +
          (("" if cond else (" — " + detail)) if detail else ""))


# --- pure: identifiers ------------------------------------------------------
def test_ids():
    check("safe_epic_id passes a clean id", git_ops.safe_epic_id("20260615-170055-x") == "20260615-170055-x")
    check("safe_epic_id rejects traversal", git_ops.safe_epic_id("../etc") is None)
    check("safe_epic_id rejects slash", git_ops.safe_epic_id("a/b") is None)
    check("safe_epic_id rejects empty", git_ops.safe_epic_id("  ") is None)
    check("task_num parses", git_ops.task_num("task-003.md") == 3)
    check("task_num none on garbage", git_ops.task_num("readme.md") is None)
    check("dep_num prefers task-N", git_ops.dep_num("task-007") == 7)
    check("dep_num falls back to any int", git_ops.dep_num("depends on 5") == 5)
    check("dep_num none on text", git_ops.dep_num("none") is None)


# --- pure: branch naming ----------------------------------------------------
def test_branches():
    eid = "20260615-170055-some-title"
    check("epic_branch uses timestamp tag", git_ops.epic_branch(eid) == "agentic/epic-20260615-170055")
    check("task_branch derives from epic tag",
          git_ops.task_branch(eid, "task-002") == "agentic/task-20260615-170055-task-002")
    check("epic_branch slugifies non-timestamp id",
          git_ops.epic_branch("My Cool Epic!!").startswith("agentic/epic-"))


# --- pure: topo sort --------------------------------------------------------
def test_topo():
    # chain 1->2->3 (2 depends on 1, 3 depends on 2)
    dm = {1: set(), 2: {1}, 3: {2}}
    check("topo linear chain order", git_ops.topo_order([1, 2, 3], dm) == [1, 2, 3])
    # diamond: 1; 2->1; 3->1; 4->2,3  => 1 first, 4 last, 2&3 by number
    dm = {1: set(), 2: {1}, 3: {1}, 4: {2, 3}}
    order = git_ops.topo_order([1, 2, 3, 4], dm)
    check("topo diamond: root first", order[0] == 1)
    check("topo diamond: sink last", order[-1] == 4)
    check("topo diamond: ties stable by number", order == [1, 2, 3, 4])
    # cycle 1<->2 must not hang and must return all nodes deterministically
    dm = {1: {2}, 2: {1}, 3: set()}
    order = git_ops.topo_order([1, 2, 3], dm)
    check("topo cycle returns all nodes", sorted(order) == [1, 2, 3])
    check("topo independent node present", 3 in order)


# --- epic_dep_nums via dag.json (no orchestrator dependency) ----------------
def test_epic_dep_nums_dag():
    with tempfile.TemporaryDirectory() as d:
        backlog = Path(d)
        ed = backlog / "epicX"
        ed.mkdir()
        (ed / "dag.json").write_text(json.dumps({"tasks": [
            {"id": "task-001", "depends_on": []},
            {"id": "task-002", "depends_on": ["task-001"]},
            {"id": "task-003", "depends_on": ["task-002", "task-003"]},  # self-dep must be dropped
        ]}))
        dm = git_ops.epic_dep_nums(backlog, "epicX", [])
        check("epic_dep_nums reads dag.json", dm.get(2) == {1})
        check("epic_dep_nums drops self-dependency", 3 not in dm.get(3, set()))
        check("epic_dep_nums keeps real dep of 3", 2 in dm.get(3, set()))


# --- git primitives on a real throwaway repo --------------------------------
def _run(repo, *args):
    return subprocess.run(["git", "-C", str(repo)] + list(args),
                          capture_output=True, text=True)


def test_git_repo():
    with tempfile.TemporaryDirectory() as d:
        repo = Path(d) / "repo"
        repo.mkdir()
        _run(repo, "init", "-q")
        _run(repo, "config", "user.email", "t@t.t")
        _run(repo, "config", "user.name", "t")
        _run(repo, "checkout", "-q", "-b", "main")
        (repo / "a.txt").write_text("hello\n")
        _run(repo, "add", "-A")
        _run(repo, "commit", "-qm", "init")

        rc, out, err = git_ops.git(repo, ["rev-parse", "--abbrev-ref", "HEAD"])
        check("git() returns tuple, branch is main", rc == 0 and out.strip() == "main", f"rc={rc} out={out!r}")

        r = git_ops.git_run(repo, ["rev-parse", "HEAD"])
        check("git_run returns object with stdout", r.returncode == 0 and len(r.stdout.strip()) >= 7)

        # no origin/* here, so base_ref should resolve to local 'main'
        check("base_ref resolves to main", git_ops.base_ref(repo) == "main", git_ops.base_ref(repo))

        # bad repo path: git_run must not raise, returns nonzero
        bad = git_ops.git_run(Path(d) / "nope", ["status"])
        check("git_run on missing repo is graceful", bad.returncode != 0)


# --- dep_base_ref: no-deps fast path (no worktree, run-state not loaded) -----
def test_dep_base_no_deps():
    with tempfile.TemporaryDirectory() as d:
        backlog = Path(d) / "backlog"
        ed = backlog / "epicY"
        ed.mkdir(parents=True)
        # one task, no dag, no Depends-On -> no deps
        (ed / "task-001.md").write_text("Status: todo\n\n## Depends On\n\n_None_\n")
        repo = Path(d) / "repo"
        repo.mkdir()
        _run(repo, "init", "-q")
        _run(repo, "config", "user.email", "t@t.t")
        _run(repo, "config", "user.name", "t")
        _run(repo, "checkout", "-q", "-b", "main")
        (repo / "x").write_text("1")
        _run(repo, "add", "-A")
        _run(repo, "commit", "-qm", "init")

        called = {"n": 0}
        def loader(_eid):
            called["n"] += 1
            return {}

        base, db = git_ops.dep_base_ref(backlog, "epicY", "task-001", repo, loader)
        check("dep_base no-deps returns (base, None)", base == "main" and db is None, f"{base},{db}")
        check("dep_base no-deps does NOT load run-state", called["n"] == 0, f"loader called {called['n']}x")


def test_base_drift_count():
    with tempfile.TemporaryDirectory() as d:
        repo = Path(d) / "repo"
        repo.mkdir()
        _run(repo, "init", "-q")
        _run(repo, "config", "user.email", "t@t.t")
        _run(repo, "config", "user.name", "t")
        _run(repo, "checkout", "-q", "-b", "main")
        (repo / "a.txt").write_text("1\n"); _run(repo, "add", "-A"); _run(repo, "commit", "-qm", "c1")
        # epic branch forks off main here
        _run(repo, "checkout", "-q", "-b", "agentic/epic-x")
        (repo / "e.txt").write_text("e\n"); _run(repo, "add", "-A"); _run(repo, "commit", "-qm", "epic work")
        check("fresh fork: behind 0", git_ops.base_drift_count(repo, "agentic/epic-x", "main") == 0)
        # main moves ahead by 2 commits after the fork
        _run(repo, "checkout", "-q", "main")
        (repo / "b.txt").write_text("2\n"); _run(repo, "add", "-A"); _run(repo, "commit", "-qm", "c2")
        (repo / "c.txt").write_text("3\n"); _run(repo, "add", "-A"); _run(repo, "commit", "-qm", "c3")
        check("epic now behind main by 2", git_ops.base_drift_count(repo, "agentic/epic-x", "main") == 2)
        check("main is not behind itself", git_ops.base_drift_count(repo, "main", "main") == 0)
        check("missing epic branch -> None", git_ops.base_drift_count(repo, "agentic/nope", "main") is None)
        check("missing main ref -> None", git_ops.base_drift_count(repo, "main", "origin/nope") is None)


def main():
    for t in (test_ids, test_branches, test_topo, test_epic_dep_nums_dag,
              test_git_repo, test_dep_base_no_deps, test_base_drift_count):
        print(t.__name__ + ":")
        try:
            t()
        except Exception as exc:
            FAIL.append(t.__name__)
            print("  \033[31mERROR\033[0m", t.__name__, "—", exc)
    print()
    print(f"git_ops: {len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        for n in FAIL:
            print("  -", n)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
