"""console.doctor — state↔git consistency checks (#1: scattered state).

All functions here are PURE: they take already-gathered facts (git output parsed
into Python, run-state dicts, predicate callables) and return findings. The server
layer does the actual git/disk I/O and feeds the facts in. This keeps the heuristics
hermetically testable without a real repo.

A "finding" is a dict: {"level": "ok"|"warn"|"bad", "kind": str, "msg": str}.
"""


def classify_worktrees(tracked_paths, existing_paths):
    """Split worktrees into orphan / stale.

    tracked_paths  : paths git knows about (`git worktree list`).
    existing_paths : directories that actually exist under .agentic-worktrees/.

    orphan : on disk but NOT tracked by git  -> leftover from a crashed run,
             safe to delete manually (git won't prune it, it doesn't know it).
    stale  : tracked by git but the directory is gone -> `git worktree prune`
             candidate (git still lists a worktree whose dir vanished).
    """
    tracked = set(tracked_paths or [])
    existing = set(existing_paths or [])
    orphan = sorted(existing - tracked)
    stale = sorted(tracked - existing)
    return {"orphan": orphan, "stale": stale}


def worktree_findings(tracked_paths, existing_paths):
    """Findings derived from worktree classification (pure)."""
    c = classify_worktrees(tracked_paths, existing_paths)
    out = []
    for p in c["orphan"]:
        out.append({"level": "warn", "kind": "orphan_worktree",
                    "msg": f"осиротевший worktree (git его не знает): {p}"})
    for p in c["stale"]:
        out.append({"level": "warn", "kind": "stale_worktree",
                    "msg": f"git числит worktree, а папки нет (нужен prune): {p}"})
    return out


def epic_branch_findings(epic_state, epic_branch, branch_exists):
    """Ghost-branch detection (pure). branch_exists(ref) -> bool.

    If the epic is marked assembled but its branch is gone, every downstream signal
    (validated/previewed/pushed, verify/smoke badges) is built on sand.
    """
    out = []
    es = epic_state or {}
    if es.get("assembled") and not branch_exists(epic_branch):
        out.append({"level": "bad", "kind": "ghost_epic_branch",
                    "msg": f"эпик помечен собранным, но ветки {epic_branch} нет в git — "
                           f"статусы и бейджи врут; пересобери ветку"})
    ab = es.get("assembled_branch")
    if ab and ab != epic_branch and not branch_exists(ab):
        out.append({"level": "warn", "kind": "ghost_assembled_branch",
                    "msg": f"в состоянии записана ветка сборки {ab}, которой нет в git"})
    return out


def task_commit_findings(runstate, commit_exists):
    """Accepted/implemented tasks whose recorded commit is gone (pure).

    commit_exists(sha) -> bool. A missing commit means the task's work is no longer
    reachable (history rewrite / branch deleted) — assembly would silently drop it.
    """
    out = []
    for name, entry in sorted((runstate or {}).items()):
        if not isinstance(entry, dict) or name.startswith("__"):
            continue
        if entry.get("state") not in ("accepted", "implemented"):
            continue
        head = entry.get("head")
        if head and not commit_exists(head):
            out.append({"level": "warn", "kind": "missing_task_commit",
                        "msg": f"{name}: записан коммит {head[:9]}, которого нет в git "
                               f"(работа потеряна — перевыполни задачу)"})
    return out


def summarize(findings):
    """Roll findings up into counts + worst level (pure)."""
    findings = findings or []
    counts = {"ok": 0, "warn": 0, "bad": 0}
    for f in findings:
        lvl = f.get("level", "ok")
        counts[lvl] = counts.get(lvl, 0) + 1
    worst = "bad" if counts["bad"] else "warn" if counts["warn"] else "ok"
    return {"counts": counts, "worst": worst, "total": len(findings), "clean": not findings}
