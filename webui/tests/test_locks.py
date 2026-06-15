#!/usr/bin/env python3
"""Unit tests for console.git_ops.repo_lock — per-repo serialization (Phase 3).

Hermetic: pure threading, no git, no server. Run:

    python3 webui/tests/test_locks.py
"""
import os
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
WEBUI = os.path.dirname(HERE)
sys.path.insert(0, WEBUI)

from console import git_ops  # noqa: E402

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("  \033[32mPASS\033[0m " if cond else "  \033[31mFAIL\033[0m ") + name +
          (("" if cond else (" — " + detail)) if detail else ""))


def test_identity():
    a1 = git_ops.repo_lock("/repo/a")
    a2 = git_ops.repo_lock("/repo/a")
    b = git_ops.repo_lock("/repo/b")
    check("same repo -> same lock object", a1 is a2)
    check("different repo -> different lock", a1 is not b)
    # Path-like inputs normalize to the same key as their str()
    from pathlib import Path
    check("Path and str agree on lock", git_ops.repo_lock(Path("/repo/a")) is a1)


def test_mutual_exclusion():
    lk = git_ops.repo_lock("/repo/excl")
    lk.acquire()
    got = lk.acquire(blocking=False)
    check("held lock blocks a second acquire", got is False)
    lk.release()
    got2 = lk.acquire(blocking=False)
    check("released lock can be re-acquired", got2 is True)
    lk.release()


def test_serializes_same_repo():
    """Two threads doing a non-atomic read-modify-write under the same repo lock
    must not interleave: with a sleep inside the critical section, an unlocked
    version would corrupt the counter."""
    state = {"val": 0, "max_concurrent": 0, "concurrent": 0}
    guard = threading.Lock()

    def worker():
        with git_ops.repo_lock("/repo/serial"):
            with guard:
                state["concurrent"] += 1
                state["max_concurrent"] = max(state["max_concurrent"], state["concurrent"])
            v = state["val"]
            time.sleep(0.02)          # widen the race window
            state["val"] = v + 1      # non-atomic on purpose
            with guard:
                state["concurrent"] -= 1

    threads = [threading.Thread(target=worker) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    check("same-repo critical sections never overlap", state["max_concurrent"] == 1,
          f"max_concurrent={state['max_concurrent']}")
    check("no lost updates under lock", state["val"] == 8, f"val={state['val']}")


def test_parallel_across_repos():
    """Different repos use different locks, so work on repo A and repo B overlaps."""
    overlap = {"seen": False}
    inA = threading.Event()

    def a():
        with git_ops.repo_lock("/repo/parA"):
            inA.set()
            time.sleep(0.05)

    def b():
        with git_ops.repo_lock("/repo/parB"):
            # if locks were shared, this would block until A releases
            if inA.wait(0.2):
                overlap["seen"] = True

    ta, tb = threading.Thread(target=a), threading.Thread(target=b)
    ta.start(); tb.start()
    ta.join(); tb.join()
    check("different repos run in parallel", overlap["seen"] is True)


def main():
    for t in (test_identity, test_mutual_exclusion, test_serializes_same_repo,
              test_parallel_across_repos):
        print(t.__name__ + ":")
        try:
            t()
        except Exception as exc:
            FAIL.append(t.__name__)
            print("  \033[31mERROR\033[0m", t.__name__, "—", exc)
    print()
    print(f"locks: {len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        for n in FAIL:
            print("  -", n)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
