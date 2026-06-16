"""console.git_ops — low-level git mechanics for the Agentic Console.

Extracted verbatim from server.py (Phase 1 refactor). Every function takes what
it needs as explicit parameters (repo path, backlog dir, a run-state loader) and
never reaches into server globals, so the pure logic (topo sort, dependency
extraction, branch naming) can be unit-tested without the web server.

Behaviour is byte-for-byte identical to the originals. server.py keeps thin,
same-named wrappers/aliases so its many call sites are unchanged.
"""
import json
import re
import shutil
import subprocess
import threading
from datetime import datetime
from pathlib import Path


# --- per-repo serialization -------------------------------------------------
_REPO_LOCKS = {}
_REPO_LOCKS_GUARD = threading.Lock()


def repo_lock(repo):
    """Return the process-wide lock for a repository path so that all git MUTATIONS
    on one repo (worktree add/remove, cherry-pick, branch -D, push) are serialized.
    Different repos get different locks and run in parallel. Non-reentrant — never
    acquire it twice in the same call chain. Usage:

        with git_ops.repo_lock(repo):
            ...  # git worktree / cherry-pick / branch work
    """
    key = str(repo)
    with _REPO_LOCKS_GUARD:
        lk = _REPO_LOCKS.get(key)
        if lk is None:
            lk = threading.Lock()
            _REPO_LOCKS[key] = lk
        return lk


# --- raw git ----------------------------------------------------------------
def git_run(repo, args, timeout=1800):
    try:
        return subprocess.run(["git", "-C", str(repo)] + args,
                              capture_output=True, text=True, timeout=timeout)
    except Exception as exc:
        class R:
            returncode = 1
            stdout = ""
            stderr = str(exc)
        return R()


def git(repo, args, timeout=20):
    """Like git_run but returns a (returncode, stdout, stderr) tuple."""
    try:
        r = subprocess.run(["git", "-C", str(repo)] + args,
                           capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except Exception as exc:
        return 1, "", str(exc)


# --- identifiers / parsing (pure) -------------------------------------------
def safe_epic_id(epic_id):
    epic_id = (epic_id or "").strip()
    if not epic_id or "/" in epic_id or "\\" in epic_id or ".." in epic_id:
        return None
    return epic_id


def task_num(name):
    m = re.search(r"task-(\d+)", name or "")
    return int(m.group(1)) if m else None


def dep_num(s):
    m = re.search(r"task-(\d+)", s or "")
    if m:
        return int(m.group(1))
    m = re.search(r"(\d+)", s or "")
    return int(m.group(1)) if m else None


# --- branch naming (pure) ---------------------------------------------------
def epic_branch(epic_id):
    m = re.match(r"(\d{8}-\d{6})", epic_id or "")
    tag = m.group(1) if m else re.sub(r"[^a-zA-Z0-9]+", "-", epic_id or "epic")[:24].strip("-")
    return f"agentic/epic-{tag}"


def task_branch(epic_id, stem):
    return f"agentic/task-{epic_branch(epic_id).split('-', 1)[-1]}-{stem}"


def base_ref(repo):
    for ref in ("origin/main", "main", "origin/master", "master"):
        if git_run(repo, ["rev-parse", "--verify", ref]).returncode == 0:
            return ref
    return (git_run(repo, ["symbolic-ref", "--short", "HEAD"]).stdout or "HEAD").strip() or "HEAD"


def base_drift_count(repo, branch, main_ref):
    """How many commits <main_ref> has that <branch> does not contain — i.e. how far
    <branch>'s base has fallen behind the main line. Returns int, or None if either ref
    is missing or the count can't be parsed. Pure read: no fetch, no branch mutation."""
    for ref in (branch, main_ref):
        if git_run(repo, ["rev-parse", "--verify", ref]).returncode != 0:
            return None
    r = git_run(repo, ["rev-list", "--count", f"{branch}..{main_ref}"])
    s = (r.stdout or "").strip()
    return int(s) if (r.returncode == 0 and s.isdigit()) else None


# --- dependency graph (pure) ------------------------------------------------
def topo_order(nums, depmap):
    """Kahn topological sort over task numbers; stable by number on ties."""
    nums = sorted(nums)
    indeg = {n: len([d for d in depmap.get(n, set()) if d in nums]) for n in nums}
    out, ready = [], sorted([n for n in nums if indeg[n] == 0])
    seen = set()
    while ready:
        n = ready.pop(0)
        if n in seen:
            continue
        seen.add(n)
        out.append(n)
        for m in nums:
            if n in depmap.get(m, set()) and m not in seen:
                indeg[m] -= 1
                if indeg[m] <= 0 and m not in ready:
                    ready.append(m)
        ready.sort()
    for n in nums:  # append any left over (cycles) deterministically
        if n not in seen:
            out.append(n)
    return out


def epic_dep_nums(backlog_dir, epic_id, files):
    """Return {task_num: set(dep_task_nums)} from dag.json (preferred) or the
    platform's Depends-On parser. Always excludes a task from its own blockers."""
    ed = Path(backlog_dir) / epic_id
    raw = {}
    dag = ed / "dag.json"
    if dag.exists():
        try:
            for t in json.loads(dag.read_text()).get("tasks", []):
                raw[t.get("id", "")] = t.get("depends_on", []) or []
        except Exception:
            raw = {}
    if not raw:
        try:
            from orchestrator.backlog_dag import extract_depends_on
            for f in files:
                raw[f.stem] = extract_depends_on(f.read_text(errors="ignore"))
        except Exception:
            raw = {}
    deps = {}
    for tid, dlist in raw.items():
        tn = dep_num(tid)
        if tn is None:
            continue
        s = set()
        for d in dlist:
            dn = dep_num(d)
            if dn is not None and dn != tn:
                s.add(dn)
        deps[tn] = s
    return deps


# --- dependency-aware base (git + run-state via injected loader) ------------
def dep_base_ref(backlog_dir, epic_id, stem, repo, load_runstate, job=None):
    """Base for a task = main + the task's already-accepted dependencies, assembled
    in topo order, so a dependent task is implemented ON TOP of what it depends on.
    Keeps several tasks that edit the same file from conflicting at assembly time.
    Defensive: on ANY problem it falls back to plain main — but it EMITS the reason
    so a silent fallback is never a mystery. Returns (base_ref, depbase_branch|None).

    `load_runstate` is a callable load_runstate(epic_id) -> dict, injected so this
    stays independent of server state. It is called lazily (only when the task has
    dependencies), preserving the original behaviour exactly.
    """
    base = base_ref(repo)
    def say(msg, level=""):
        if job:
            job.emit(msg, level)
    try:
        num = task_num(stem + ".md")
        files = sorted((Path(backlog_dir) / epic_id).glob("task-*.md"))
        depmap = epic_dep_nums(backlog_dir, epic_id, files)
        deps, stack = set(), list(depmap.get(num, set()))
        while stack:
            d = stack.pop()
            if d in deps:
                continue
            deps.add(d)
            stack.extend(depmap.get(d, set()))
        if not deps:
            say(f"dep-base: задача #{num} без зависимостей — строю от {base}")
            return base, None
        rs = load_runstate(epic_id)
        byname = {task_num(f.name): f.name for f in files}
        order = [n for n in topo_order(list(deps), depmap) if n in deps]
        applic = []
        for n in order:
            run = rs.get(byname.get(n, ""), {})
            head = run.get("head")
            if run.get("changed") and head and head != run.get("base"):
                applic.append((n, head))
            else:
                say(f"dep-base: зависимость #{n} ещё не выполнена/без коммита (state={run.get('state')}) — её правки не лягут в базу", "skip")
        if not applic:
            say(f"dep-base: ни одна зависимость #{num} не имеет коммита — строю от {base}", "skip")
            return base, None
        git_run(repo, ["worktree", "prune"])
        db = f"agentic/depbase-{epic_branch(epic_id).split('-', 1)[-1]}-{num:03d}"
        wt = Path(repo).parent / ".agentic-worktrees" / f"depbase-{num:03d}-{datetime.now().strftime('%H%M%S')}"
        if wt.exists():
            shutil.rmtree(wt, ignore_errors=True)
        # a stale worktree may hold the depbase branch checked out → free it
        git_run(repo, ["worktree", "remove", "--force", str(wt)])
        r = git_run(repo, ["worktree", "add", "-B", db, str(wt), base])
        if r.returncode != 0:
            say(f"dep-base: не смог создать worktree ({(r.stderr or '').strip()[:160]}) — строю от {base}", "err")
            return base, None
        try:
            for n, head in applic:
                cp = git_run(wt, ["cherry-pick", head])
                if cp.returncode != 0:
                    confl = [l[3:] for l in git_run(wt, ["status", "--porcelain"]).stdout.splitlines() if l.startswith(("UU", "AA", "DD"))]
                    git_run(wt, ["cherry-pick", "--abort"])
                    say(f"dep-base: зависимости конфликтуют между собой на #{n} ({', '.join(confl) or 'files'}) — строю от {base}", "err")
                    return base, None
            depbase_head = (git_run(wt, ["rev-parse", "HEAD"]).stdout or "").strip()
        finally:
            git_run(repo, ["worktree", "remove", "--force", str(wt)])
            git_run(repo, ["worktree", "prune"])
        if depbase_head and depbase_head != (git_run(repo, ["rev-parse", base]).stdout or "").strip():
            say(f"dep-base: строю поверх зависимостей {', '.join('#'+str(n) for n,_ in applic)} → base {depbase_head[:9]} (сборка ляжет без конфликта)", "ok")
            return depbase_head, db
        say(f"dep-base: зависимости не дали изменений — строю от {base}", "skip")
        return base, None
    except Exception as exc:
        say(f"dep-base: ошибка ({exc}) — строю от {base}", "err")
        return base, None
