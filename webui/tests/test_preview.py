#!/usr/bin/env python3
"""Tests for preview env seeding (ws-50).

The epic preview runs from a fresh git worktree, where gitignored env files (.env.local with
SESSION_SECRET + real creds) don't exist — so login used to 500 / use wrong creds. _seed_preview_env
copies the product repo's real env into the worktree, falling back to a synthetic .env.local only
if the product ships none. Hermetic: temp 'repo' + temp 'worktree'. Run:

    python3 webui/tests/test_preview.py
"""
import os
import sys
import tempfile
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
WEBUI = os.path.dirname(HERE)
ROOT = os.path.dirname(WEBUI)
sys.path.insert(0, ROOT)
sys.path.insert(0, WEBUI)

import server  # noqa: E402  (main() is __main__-guarded)

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("  \033[32mPASS\033[0m " if cond else "  \033[31mFAIL\033[0m ") + name +
          (("" if cond else (" — " + detail)) if detail else ""))


def test_copies_real_env():
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp) / "repo"
        wt = Path(tmp) / "wt"
        repo.mkdir()
        wt.mkdir()
        (repo / ".env.local").write_text("SESSION_SECRET=real_secret_123\nAPP_PASSWORD=password123\n")
        (repo / ".env").write_text("DATABASE_URL=postgres://x\n")
        copied = server._seed_preview_env(str(repo), str(wt))
        check("reports copied env files", set(copied) == {".env", ".env.local"})
        check("worktree .env.local has the REAL secret",
              "real_secret_123" in (wt / ".env.local").read_text())
        check("worktree .env copied too", (wt / ".env").exists())


def test_does_not_overwrite_existing():
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp) / "repo"
        wt = Path(tmp) / "wt"
        repo.mkdir()
        wt.mkdir()
        (repo / ".env.local").write_text("SESSION_SECRET=from_repo\n")
        (wt / ".env.local").write_text("SESSION_SECRET=already_here\n")
        copied = server._seed_preview_env(str(repo), str(wt))
        check("does not clobber an existing worktree env", ".env.local" not in copied)
        check("existing worktree env preserved",
              "already_here" in (wt / ".env.local").read_text())


def test_synthetic_fallback_when_no_repo_env():
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp) / "repo"
        wt = Path(tmp) / "wt"
        repo.mkdir()
        wt.mkdir()
        copied = server._seed_preview_env(str(repo), str(wt))
        check("nothing copied when repo has no env", copied == [])
        check("synthetic .env.local written as fallback", (wt / ".env.local").exists())
        body = (wt / ".env.local").read_text()
        check("synthetic fallback has a SESSION_SECRET", "SESSION_SECRET=" in body)


def main():
    for t in (test_copies_real_env, test_does_not_overwrite_existing,
              test_synthetic_fallback_when_no_repo_env):
        print(t.__name__ + ":")
        try:
            t()
        except Exception as exc:
            FAIL.append(t.__name__)
            print("  \033[31mERROR\033[0m", t.__name__, "—", exc)
    print()
    print(f"preview: {len(PASS)} passed, {len(FAIL)} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
