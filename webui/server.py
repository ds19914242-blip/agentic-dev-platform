"""
Agentic Console - local web control plane for the Agentic Dev Platform.

Zero external dependencies (Python stdlib only) so it runs next to the
platform without `pip install`. It does NOT reimplement platform logic:
it reads the real file-based state (backlog/, runs/, products/) and calls
the platform's own modules to drive the spec pipeline.

Run from anywhere:
    python3 webui/server.py            # serves on http://127.0.0.1:8765
    python3 webui/server.py --port 9000

Stage 1 scope:
    - browse products, agents, epics, runs (real state)
    - submit a human request -> create epic + run the Product Agent (decompose)
    - inspect every artifact produced and which stage/agent owns it
"""

import argparse
import json
import os
import re
import shutil
import sys
import threading
import time
import traceback
import uuid
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# --- locate platform root (parent of webui/) and make it importable -----------
ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # webui/ — for the console package

from console import git_ops
from console import state as _state
from console import inbox as _inbox
from console import serializers as _ser

STATIC_DIR = Path(__file__).resolve().parent / "static"
BACKLOG_DIR = ROOT / "backlog"
RUNS_DIR = ROOT / "runs"
PRODUCTS_DIR = ROOT / "products"
MEMORY_DIR = ROOT / "memory"

# Bumped whenever the API surface changes, so the frontend can detect a
# stale server (we hit "new frontend / old backend" desyncs before).
API_VERSION = "workspace-49"

# Directories never shown in the repository file tree.
REPO_IGNORE_DIRS = {
    ".git", "node_modules", ".next", "dist", "build", "out",
    "coverage", ".venv", "venv", "__pycache__", ".turbo", ".cache",
}

# Roots that artifact reads are allowed to touch (prevents path traversal).
ALLOWED_ROOTS = [BACKLOG_DIR, RUNS_DIR, PRODUCTS_DIR]

# --- the real spec pipeline, encoded as ordered stations ----------------------
# Each station names the agent persona that runs it and the artifacts it emits.
PIPELINE = [
    {
        "id": "request",
        "label": "Human request",
        "agent": None,
        "command": None,
        "outputs": [],
        "kind": "input",
    },
    {
        "id": "decompose",
        "label": "Product spec",
        "agent": "Product Agent",
        "command": "agentic.py decompose",
        "outputs": ["epic.md", "product-spec.md", "outcome.json"],
        "kind": "llm",
    },
    {
        "id": "approve_product",
        "label": "Feature spec",
        "agent": "Product Analyst Agent",
        "command": "agentic.py approve-product-spec",
        "outputs": ["feature-spec.md"],
        "kind": "llm",
    },
    {
        "id": "approve_spec",
        "label": "Backlog tasks",
        "agent": "Backlog Decomposer",
        "command": "agentic.py approve-spec",
        "outputs": ["acceptance-scenarios.md", "task-NNN.md"],
        "kind": "llm",
    },
    {
        "id": "execute",
        "label": "Execute & verify",
        "agent": "Runtime agents",
        "command": "agentic.py schedule / backlog",
        "outputs": ["runs/<id>/", "PR", "release-verification.json"],
        "kind": "runtime",
    },
]

# Roster shown in the Agents view. Spec personas are prompt-driven; runtime
# agents are the orchestrator/agent_runtime classes.
AGENTS = [
    {"name": "Product Agent", "stage": "decompose", "tier": "spec",
     "role": "Clarifies WHAT to build. Writes the product spec with no repo context."},
    {"name": "Product Analyst Agent", "stage": "approve_product", "tier": "spec",
     "role": "Translates the product spec into a technical feature spec using the repo map."},
    {"name": "Backlog Decomposer", "stage": "approve_spec", "tier": "spec",
     "role": "Cuts the feature spec into small, dependency-aware backlog tasks + acceptance scenarios."},
    {"name": "architect", "stage": "execute", "tier": "runtime",
     "role": "Splits work into backend / frontend / qa lanes and writes the handoff."},
    {"name": "implementation", "stage": "execute", "tier": "runtime",
     "role": "Builds the prompt and runs Claude Code to write the actual changes."},
    {"name": "validation", "stage": "execute", "tier": "runtime",
     "role": "Runs the product validators (typecheck, build) and reports evidence."},
    {"name": "review", "stage": "execute", "tier": "runtime",
     "role": "Aggregates validation + acceptance evidence and flags risks."},
    {"name": "acceptance", "stage": "execute", "tier": "runtime",
     "role": "Runs the Playwright acceptance scenarios for the epic."},
    {"name": "release", "stage": "execute", "tier": "runtime",
     "role": "Verifies the production deployment and confirms the release."},
]


def platform_version():
    try:
        text = (ROOT / "PLATFORM_CHECKPOINT.md").read_text(errors="ignore")
        for line in text.splitlines():
            if line.lower().startswith("version:"):
                return line.split(":", 1)[1].strip()
    except Exception:
        pass
    return "unknown"


# --- product / config helpers -------------------------------------------------
def _safe_yaml(path):
    try:
        import yaml  # platform already depends on this
        return yaml.safe_load(path.read_text(errors="ignore")) or {}
    except Exception:
        return {}


def list_products():
    out = []
    if not PRODUCTS_DIR.exists():
        return out
    for cfg in sorted(PRODUCTS_DIR.glob("*/config.yaml")):
        data = _safe_yaml(cfg)
        out.append({
            "name": str(data.get("name") or cfg.parent.name),
            "framework": data.get("framework", ""),
            "type": data.get("type", ""),
            "status": data.get("status", ""),
            "repo_path": data.get("repo_path", ""),
            "validators": [v.get("name") for v in (data.get("validators") or []) if isinstance(v, dict)],
            "has_analysis": (MEMORY_DIR / f"{data.get('name') or cfg.parent.name}-analysis.md").exists(),
        })
    return out


# --- epic / artifact helpers --------------------------------------------------
def _section(text, heading):
    return _ser.section(text, heading)


def _read_json(path):
    try:
        return json.loads(path.read_text(errors="ignore"))
    except Exception:
        return None


def _kind_of(name):
    if name.endswith(".json"):
        return "json"
    if name.endswith(".md") or name.endswith(".txt"):
        return "text"
    return "other"


def _stage_status_for_epic(epic_dir, files):
    """Mark each pipeline station done/active/pending from artifacts on disk."""
    have = set(files)
    has_task = any(f.startswith("task-") and f.endswith(".md") for f in have)
    done = {
        "request": "epic.md" in have,
        "decompose": "product-spec.md" in have,
        "approve_product": "feature-spec.md" in have,
        "approve_spec": has_task,
        "execute": False,  # execution lives under runs/, surfaced separately
    }
    # outcome can tell us execution moved
    outcome = _read_json(epic_dir / "outcome.json") or {}
    if outcome.get("status") in {"implementing", "implemented", "verification_pending",
                                 "verified", "accepted", "failed"}:
        done["execute"] = outcome.get("status") in {"accepted", "verified"}
    stations = []
    active_set = False
    for st in PIPELINE:
        is_done = done.get(st["id"], False)
        status = "done" if is_done else "pending"
        if not is_done and not active_set:
            status = "active"
            active_set = True
        stations.append({**st, "status": status})
    return stations


def _epic_product(epic_dir):
    """Which product an epic belongs to (product.txt, else parsed from epic.md)."""
    marker = epic_dir / "product.txt"
    if marker.exists():
        return marker.read_text(errors="ignore").strip()
    epic_md = epic_dir / "epic.md"
    if epic_md.exists():
        import re as _re
        m = _re.search(r"##\s*Product\s*\n+\s*([^\n]+)", epic_md.read_text(errors="ignore"))
        if m:
            return m.group(1).strip()
    return ""


def epic_summary(epic_dir):
    epic_md = epic_dir / "epic.md"
    text = epic_md.read_text(errors="ignore") if epic_md.exists() else ""
    outcome = _read_json(epic_dir / "outcome.json") or {}
    files = sorted(p.name for p in epic_dir.iterdir() if p.is_file())
    tasks = sorted(f for f in files if f.startswith("task-") and f.endswith(".md"))
    return {
        "product": _epic_product(epic_dir),
        "id": epic_dir.name,
        "request": _section(text, "Request") or "",
        "status": outcome.get("status", "—"),
        "goal": outcome.get("goal", ""),
        "created_at": outcome.get("created_at", ""),
        "updated_at": outcome.get("updated_at", ""),
        "task_count": len(tasks),
        "artifact_count": len(files),
    }


def list_epics(product=""):
    if not BACKLOG_DIR.exists():
        return []
    epics = []
    for d in sorted(BACKLOG_DIR.iterdir(), reverse=True):
        if d.name.startswith("_") or d.name.startswith("."):
            continue
        if d.is_dir() and (d / "epic.md").exists():
            try:
                summary = epic_summary(d)
            except Exception:
                continue
            if product and summary.get("product") and summary["product"] != product:
                continue
            epics.append(summary)
    return epics


ARCHIVE_DIR = BACKLOG_DIR / "_archive"


def list_archived_epics(product=""):
    if not ARCHIVE_DIR.exists():
        return []
    out = []
    for d in sorted(ARCHIVE_DIR.iterdir(), reverse=True):
        if d.is_dir() and (d / "epic.md").exists():
            try:
                s = epic_summary(d)
            except Exception:
                continue
            if product and s.get("product") and s["product"] != product:
                continue
            out.append(s)
    return out


def _safe_epic_id(epic_id):
    return git_ops.safe_epic_id(epic_id)


def archive_epic(epic_id):
    eid = _safe_epic_id(epic_id)
    if not eid:
        return {"ok": False, "error": "invalid epic id"}
    src = BACKLOG_DIR / eid
    if not src.is_dir():
        return {"ok": False, "error": "epic not found"}
    ARCHIVE_DIR.mkdir(exist_ok=True)
    dst = ARCHIVE_DIR / eid
    if dst.exists():
        shutil.rmtree(dst)
    shutil.move(str(src), str(dst))
    return {"ok": True, "epic_id": eid, "archived": True}


def restore_epic(epic_id):
    eid = _safe_epic_id(epic_id)
    if not eid:
        return {"ok": False, "error": "invalid epic id"}
    src = ARCHIVE_DIR / eid
    if not src.is_dir():
        return {"ok": False, "error": "archived epic not found"}
    dst = BACKLOG_DIR / eid
    if dst.exists():
        return {"ok": False, "error": "epic already exists in backlog"}
    shutil.move(str(src), str(dst))
    return {"ok": True, "epic_id": eid, "restored": True}


def delete_epic(epic_id):
    eid = _safe_epic_id(epic_id)
    if not eid:
        return {"ok": False, "error": "invalid epic id"}
    for base in (BACKLOG_DIR, ARCHIVE_DIR):
        p = base / eid
        if p.is_dir():
            shutil.rmtree(p)
            return {"ok": True, "epic_id": eid, "deleted": True}
    return {"ok": False, "error": "epic not found"}


_DONE_STATUSES = {
    "done", "done_no_pr", "merged", "release_confirmed", "pr_created",
    "already_satisfied", "no_changes_needed", "manual_verification_passed",
}


def _parse_task_file(path):
    return _ser.parse_task(path.read_text(errors="ignore"), path.name)


def _task_num(name):
    return git_ops.task_num(name)


def _runstate_path(epic_id):
    return _state.runstate_path(BACKLOG_DIR, epic_id)


def load_runstate(epic_id):
    return _state.load_runstate(BACKLOG_DIR, epic_id)


def set_runstate(epic_id, task_file, **fields):
    return _state.set_runstate(BACKLOG_DIR, epic_id, task_file, **fields)


_EPIC_KEY = _state.EPIC_KEY


def load_epic_state(epic_id):
    return _state.load_epic_state(BACKLOG_DIR, epic_id)


def set_epic_state(epic_id, **fields):
    return _state.set_epic_state(BACKLOG_DIR, epic_id, **fields)


def _dep_num(s):
    return git_ops.dep_num(s)


def epic_dep_nums(epic_id, files):
    return git_ops.epic_dep_nums(BACKLOG_DIR, epic_id, files)


def product_backlog(product_name):
    out = []
    for e in list_epics(product_name):
        ed = BACKLOG_DIR / e["id"]
        files = sorted(ed.glob("task-*.md"))
        parsed = [(f, _parse_task_file(f)) for f in files]
        rs = load_runstate(e["id"])
        def _is_done(fname, status):
            return status in _DONE_STATUSES or rs.get(fname, {}).get("state") == "accepted"
        donemap = {_task_num(f.name): _is_done(f.name, t["status"]) for f, t in parsed}
        depnums = epic_dep_nums(e["id"], files)
        for f, t in parsed:
            st = t["status"] or ""
            tn = _task_num(f.name)
            unmet = sorted(n for n in depnums.get(tn, set()) if not donemap.get(n, False))
            run = rs.get(f.name, {})
            run_state = run.get("state")
            done = st in _DONE_STATUSES or run_state == "accepted"
            # console run-state overrides column so the board reflects live work
            if done:
                col = "done"
            elif run_state == "running":
                col = "in_progress"
            elif run_state in ("implemented", "no_changes"):
                col = "in_review"
            elif st == "pr_created" or st.startswith("manual_verification"):
                col = "in_review"
            elif st == "in_progress" or st.endswith("_running"):
                col = "in_progress"
            elif unmet:
                col = "blocked"
            else:
                col = "ready"
            t.update({"epic_id": e["id"], "epic": e.get("request", ""), "num": tn,
                      "blocked_by": unmet, "ready": col == "ready", "done": done, "column": col,
                      "run_state": run_state, "run_branch": run.get("branch"),
                      "run_changed": len(run.get("changed", [])) if run.get("changed") else 0})
            out.append(t)
    return {"tasks": out, "count": len(out)}


# --- task execution: build a single epic branch in dependency order ----------
# Model: each epic accumulates code on ONE branch `agentic/epic-<ts>`. A task
# runs in a worktree checked out on that branch (so it sees predecessors' code),
# the agent writes, the change is committed, and the branch advances linearly —
# no merges, no conflicts, main untouched, no push / PR. Per-epic lock serializes
# runs so the linear history stays clean.
def _git_run(repo, args, timeout=1800):
    return git_ops.git_run(repo, args, timeout)


def _epic_branch(epic_id):
    return git_ops.epic_branch(epic_id)


def _base_ref(repo):
    return git_ops.base_ref(repo)


def _resolve_repo(epic_id):
    product = _epic_product(BACKLOG_DIR / epic_id) or ""
    try:
        from orchestrator.product_registry import load_product_config
        repo = load_product_config(product).get("repo_path", "")
    except Exception as exc:
        return None, None, str(exc)
    if not repo or not Path(repo).exists():
        return product, None, "repo path not found on this machine"
    return product, repo, None


def _task_branch(epic_id, stem):
    return git_ops.task_branch(epic_id, stem)


def _dep_base_ref(epic_id, stem, repo, job=None):
    return git_ops.dep_base_ref(BACKLOG_DIR, epic_id, stem, repo, load_runstate, job)


def _run_task(epic_id, task_file, product, repo, job):
    """Implement ONE task in a worktree built on top of its accepted dependencies;
    commit it on its OWN reusable branch agentic/task-… so the epic build can later
    cherry-pick it cleanly. Runs the agent (LLM) — the only place the agent runs."""
    task_path = BACKLOG_DIR / epic_id / task_file
    if not task_path.is_file():
        return {"ok": False, "error": "task not found"}
    stem = task_path.stem
    base, depbase = _dep_base_ref(epic_id, stem, repo, job)
    tb = _task_branch(epic_id, stem)
    wt = Path(repo).parent / ".agentic-worktrees" / f"{stem}-{datetime.now().strftime('%H%M%S')}"
    job.emit(f"Creating worktree on {tb} from {base} (main untouched)")
    r = _git_run(repo, ["worktree", "add", "-B", tb, str(wt), base])
    if depbase:
        _git_run(repo, ["branch", "-D", depbase])
    if r.returncode != 0:
        set_runstate(epic_id, task_file, state="failed", error=(r.stderr or "").strip())
        return {"ok": False, "error": "git worktree failed: " + (r.stderr or "").strip()}
    try:
        before = (_git_run(wt, ["rev-parse", "HEAD"]).stdout or "").strip()
        job.emit("Running implementation agent (Architect → lanes → Implementation → Validation → Review)…")
        try:
            from orchestrator.agent_runtime.orchestrator import run_runtime_orchestrator
            out_dir = f"runs/webui-task-{stem}-{datetime.now().strftime('%H%M%S')}"
            run_runtime_orchestrator(
                task=task_path.read_text(errors="ignore"), product=product, repo_path=str(wt),
                output_dir=out_dir, dry_run=False,
                inputs={"task_path": str(task_path), "epic_dir": str(task_path.parent),
                        "execute_writes": True})
        except FileNotFoundError:
            set_runstate(epic_id, task_file, state="failed", error="claude CLI not found")
            return {"ok": False, "error": "claude CLI not found — no code written"}
        except Exception as exc:
            set_runstate(epic_id, task_file, state="failed", error=str(exc))
            return {"ok": False, "error": str(exc)}
        _git_run(wt, ["add", "-A"])
        _git_run(wt, ["commit", "-m", f"agentic: {stem}"])
        after = (_git_run(wt, ["rev-parse", "HEAD"]).stdout or "").strip()
        if after and after != before:
            changed = [l for l in _git_run(wt, ["diff", "--name-only", f"{before}..{after}"]).stdout.splitlines() if l.strip()]
            set_runstate(epic_id, task_file, state="implemented", branch=tb, base=before, head=after, changed=changed)
            job.emit(f"{stem}: {len(changed)} file(s) committed on {tb}", "ok")
            return {"ok": True, "branch": tb, "changed": changed, "state": "implemented"}
        set_runstate(epic_id, task_file, state="no_changes", branch=tb, base=before, head=before, changed=[])
        job.emit(f"{stem}: agent produced NO file changes", "skip")
        return {"ok": True, "branch": tb, "changed": [], "state": "no_changes"}
    finally:
        _git_run(repo, ["worktree", "remove", "--force", str(wt)])
        _git_run(repo, ["worktree", "prune"])


def run_task_implementation(epic_id, task_file):
    def target(job):
        eid = _safe_epic_id(epic_id)
        if not eid or "/" in (task_file or "") or ".." in (task_file or ""):
            return {"ok": False, "error": "invalid task reference"}
        product, repo, err = _resolve_repo(eid)
        if err:
            set_runstate(eid, task_file, state="failed", error=err)
            return {"ok": False, "error": err}
        set_runstate(eid, task_file, state="running")
        with git_ops.repo_lock(repo):
            return _run_task(eid, task_file, product, repo, job)
    return target


def _topo_order(nums, depmap):
    return git_ops.topo_order(nums, depmap)


def epic_build_status(epic_id):
    """Gate info for assembling an epic: build is allowed only when every task is
    accepted (reviewed). Returns counts + which task numbers are still pending."""
    eid = _safe_epic_id(epic_id)
    if not eid:
        return {"error": "invalid epic id"}
    files = sorted((BACKLOG_DIR / eid).glob("task-*.md"))
    rs = load_runstate(eid)
    accepted, pending = [], []
    for f in files:
        n = _task_num(f.name)
        if rs.get(f.name, {}).get("state") == "accepted":
            accepted.append(n)
        else:
            pending.append(n)
    return {"total": len(files), "accepted": sorted(accepted), "pending": sorted(pending),
            "buildable": len(files) > 0 and not pending, "branch": _epic_branch(eid)}


def build_epic(epic_id):
    """Assemble the epic branch by CHERRY-PICKING each accepted task's commit in
    DAG order. No agent / LLM is invoked here — pure git integration of work that
    was already implemented and accepted. Gated on all tasks being accepted."""
    def target(job):
        eid = _safe_epic_id(epic_id)
        if not eid:
            return {"ok": False, "error": "invalid epic id"}
        status = epic_build_status(eid)
        if not status.get("buildable"):
            msg = "Not all tasks accepted — pending: " + ", ".join("#" + str(n) for n in status.get("pending", []))
            job.emit(msg, "err")
            return {"ok": False, "error": msg, "pending": status.get("pending", [])}
        product, repo, err = _resolve_repo(eid)
        if err:
            return {"ok": False, "error": err}
        files = sorted((BACKLOG_DIR / eid).glob("task-*.md"))
        depmap = epic_dep_nums(eid, files)
        byname = {_task_num(f.name): f.name for f in files}
        order = _topo_order([_task_num(f.name) for f in files], depmap)
        rs = load_runstate(eid)
        eb = _epic_branch(eid)
        base = _base_ref(repo)
        wt = Path(repo).parent / ".agentic-worktrees" / f"{eb.split('/')[-1]}-assemble-{datetime.now().strftime('%H%M%S')}"
        job.emit(f"Assembling {eb} from {base} by cherry-pick (no agent) — order: " +
                 ", ".join("#" + str(n) for n in order))
        with git_ops.repo_lock(repo):
            r = _git_run(repo, ["worktree", "add", "-B", eb, str(wt), base])
            if r.returncode != 0:
                return {"ok": False, "error": "git worktree failed: " + (r.stderr or "").strip()}
            try:
                picked, skipped, conflict = 0, 0, False
                for n in order:
                    tf = byname.get(n)
                    if not tf:
                        continue
                    run = rs.get(tf, {})
                    head = run.get("head")
                    if not run.get("changed") or not head or head == run.get("base"):
                        job.emit(f"#{n} {tf}: no code change — skipped", "skip")
                        skipped += 1
                        continue
                    cp = _git_run(wt, ["cherry-pick", head])
                    if cp.returncode != 0:
                        confl = [l[3:] for l in _git_run(wt, ["status", "--porcelain"]).stdout.splitlines()
                                 if l.startswith(("UU", "AA", "DD"))]
                        _git_run(wt, ["cherry-pick", "--abort"])
                        conflict = True
                        job.emit(f"#{n} {tf}: CONFLICT on {', '.join(confl) or 'files'} — assembly stopped, partial branch discarded", "err")
                        job.emit("Этот таск правит те же строки, что и его зависимости, но был выполнен от main. "
                                 "Сбрось его (Вернуть в todo) и перезапусти — он соберётся поверх зависимостей без конфликта.", "err")
                        return {"ok": False, "error": "merge conflict at #" + str(n),
                                "conflict_task": tf, "conflict_files": confl,
                                "hint": "reset_and_rerun"}
                    job.emit(f"#{n} {tf}: applied", "ok")
                    picked += 1
                job.emit(f"Epic assembled on {eb}: {picked} applied, {skipped} skipped. main untouched, no PR.", "ok")
                set_epic_state(eid, assembled=True, assembled_branch=eb, validated=False, validation=None)
                return {"ok": True, "branch": eb, "applied": picked, "skipped": skipped}
            finally:
                _git_run(repo, ["worktree", "remove", "--force", str(wt)])
                _git_run(repo, ["worktree", "prune"])
                if conflict:
                    _git_run(repo, ["branch", "-D", eb])
    return target


def validate_epic(epic_id):
    """Run the product validators (tsc, build) on the assembled epic branch in a
    worktree. main untouched. Sets epic state validated true/false."""
    def target(job):
        eid = _safe_epic_id(epic_id)
        if not eid:
            return {"ok": False, "error": "invalid epic id"}
        if not load_epic_state(eid).get("assembled"):
            return {"ok": False, "error": "epic not assembled yet — build the branch first"}
        product, repo, err = _resolve_repo(eid)
        if err:
            return {"ok": False, "error": err}
        eb = _epic_branch(eid)
        if _git_run(repo, ["rev-parse", "--verify", eb]).returncode != 0:
            return {"ok": False, "error": "epic branch not found — re-assemble"}
        wt = Path(repo).parent / ".agentic-worktrees" / f"{eb.split('/')[-1]}-validate-{datetime.now().strftime('%H%M%S')}"
        with git_ops.repo_lock(repo):
            r = _git_run(repo, ["worktree", "add", str(wt), eb])
            if r.returncode != 0:
                return {"ok": False, "error": "git worktree failed: " + (r.stderr or "").strip()}
            try:
                base_nm = Path(repo) / "node_modules"
                wt_nm = wt / "node_modules"
                if base_nm.exists() and not wt_nm.exists():
                    try:
                        wt_nm.symlink_to(base_nm, target_is_directory=True)
                    except Exception:
                        pass
                try:
                    from orchestrator.product_registry import load_product_config
                    from orchestrator.validation_runner import run_validators
                    validators = load_product_config(product).get("validators", [])
                except Exception as exc:
                    return {"ok": False, "error": str(exc)}
                if not validators:
                    set_epic_state(eid, validated=True, validation="none")
                    job.emit("No validators configured — nothing to check.", "skip")
                    return {"ok": True, "overall": "none", "validators": []}
                job.emit(f"Running {len(validators)} validator(s) on {eb}…")
                results = run_validators(str(wt), validators)
                out = []
                for rr in results:
                    passed = rr.get("passed", False)
                    job.emit(f"{rr.get('name')}: {'passed' if passed else 'FAILED'}"
                             + (" (timed out)" if rr.get("timed_out") else ""),
                             "ok" if passed else "err")
                    if not passed:
                        tail = ((rr.get("stdout", "") or "") + "\n" + (rr.get("stderr", "") or "")).strip().splitlines()
                        for line in tail[-25:]:
                            job.emit("  " + line, "err")
                    out.append({"name": rr.get("name"), "passed": passed, "required": rr.get("required", True),
                                "stdout": rr.get("stdout", ""), "stderr": rr.get("stderr", "")})
                required = [r for r in out if r["required"]]
                overall = "passed" if required and all(r["passed"] for r in required) else "failed"
                _write_validation_report(eid, eb, out, overall)
                set_epic_state(eid, validated=(overall == "passed"), validation=overall)
                job.emit(f"Validation {overall}." + ("" if overall == "passed"
                         else " Errors saved to validation-report.md — use Fix build or fix manually, then re-validate."),
                         "ok" if overall == "passed" else "err")
                return {"ok": True, "overall": overall,
                        "validators": [{"name": r["name"], "passed": r["passed"]} for r in out]}
            finally:
                _git_run(repo, ["worktree", "remove", "--force", str(wt)])
                _git_run(repo, ["worktree", "prune"])
    return target


def _write_validation_report(epic_id, branch, validators, overall):
    lines = [f"# Validation report — {branch}", "",
             f"Overall: **{overall}** · {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ""]
    for v in validators:
        lines.append(f"## {v['name']}: {'passed' if v['passed'] else 'FAILED'}")
        body = ((v.get("stdout", "") or "") + "\n" + (v.get("stderr", "") or "")).strip()
        if not v["passed"] and body:
            lines.append("```")
            lines.append(body[-8000:])
            lines.append("```")
        lines.append("")
    try:
        (BACKLOG_DIR / epic_id / "validation-report.md").write_text("\n".join(lines), encoding="utf-8")
    except Exception:
        pass


def _read_spec_excerpt(epic_id):
    parts = []
    for name in ("product-spec.md", "feature-spec.md"):
        p = BACKLOG_DIR / epic_id / name
        if p.exists():
            parts.append(f"### {name}\n" + p.read_text(errors="ignore")[:1500])
    return "\n\n".join(parts)


def _parse_tsc_errors(text):
    return _ser.parse_tsc_errors(text)


def _build_fix_prompt(epic_id):
    report = BACKLOG_DIR / epic_id / "validation-report.md"
    raw = report.read_text(errors="ignore") if report.exists() else ""
    files, symbols = _parse_tsc_errors(raw)
    lines = [
        "The assembled epic branch fails `npx tsc --noEmit` / `npm run build`.",
        "Fix it strictly IN LINE WITH THE EPIC INTENT below. Definitions were removed ON PURPOSE.",
        "Do NOT restore deleted types/functions/constants. Instead, update or remove the CONSUMERS",
        "that still reference removed symbols, so the code compiles while keeping the epic's intent.",
        "",
    ]
    spec = _read_spec_excerpt(epic_id)
    if spec:
        lines += ["## Epic intent", spec, ""]
    if symbols:
        lines.append("## Removed / undefined symbols still referenced — fix the consumers:")
        for s, c in sorted(symbols.items(), key=lambda x: -x[1])[:30]:
            lines.append(f"- {s} ({c} use(s))")
        lines.append("")
    if files:
        lines.append("## Errors by file:")
        for f, errs in list(files.items())[:20]:
            lines.append(f"### {f}")
            lines += ["- " + e for e in errs[:30]]
            lines.append("")
    else:
        lines += ["## Raw validator output:", raw[:6000]]
    return "\n".join(lines)[:12000], files, symbols


def fix_epic_build(epic_id):
    """Semi-auto build fix with structured context: parses tsc errors (files +
    removed symbols), feeds the agent the epic INTENT (specs) plus an explicit
    'fix consumers, don't restore deleted defs' instruction. Commits the fix on
    the epic branch (never main), caps at 3 attempts, stores the fix diff for
    review, and requires a manual Re-validate afterwards."""
    def target(job):
        eid = _safe_epic_id(epic_id)
        if not eid:
            return {"ok": False, "error": "invalid epic id"}
        es = load_epic_state(eid)
        if not es.get("assembled"):
            return {"ok": False, "error": "epic not assembled"}
        if es.get("validation") != "failed":
            return {"ok": False, "error": "nothing to fix — validation is not failed"}
        attempts = es.get("fix_attempts", 0)
        if attempts >= 3:
            return {"ok": False, "error": "fix attempt limit (3) reached — please fix manually"}
        product, repo, err = _resolve_repo(eid)
        if err:
            return {"ok": False, "error": err}
        eb = _epic_branch(eid)
        prompt, files, symbols = _build_fix_prompt(eid)
        wt = Path(repo).parent / ".agentic-worktrees" / f"{eb.split('/')[-1]}-fix-{datetime.now().strftime('%H%M%S')}"
        with git_ops.repo_lock(repo):
            r = _git_run(repo, ["worktree", "add", str(wt), eb])
            if r.returncode != 0:
                return {"ok": False, "error": "git worktree failed: " + (r.stderr or "").strip()}
            try:
                base_nm = Path(repo) / "node_modules"
                wt_nm = wt / "node_modules"
                if base_nm.exists() and not wt_nm.exists():
                    try:
                        wt_nm.symlink_to(base_nm, target_is_directory=True)
                    except Exception:
                        pass
                before = (_git_run(wt, ["rev-parse", "HEAD"]).stdout or "").strip()
                job.emit(f"Fix attempt {attempts + 1}/3 — {len(files)} file(s), "
                         f"{len(symbols)} removed symbol(s). Feeding agent the errors + epic intent…")
                if symbols:
                    job.emit("  consumers to clean: " + ", ".join(list(symbols)[:8])
                             + (" …" if len(symbols) > 8 else ""))
                try:
                    from orchestrator.agent_runtime.orchestrator import run_runtime_orchestrator
                    run_runtime_orchestrator(
                        task=prompt, product=product, repo_path=str(wt),
                        output_dir=f"runs/webui-fix-{datetime.now().strftime('%H%M%S')}", dry_run=False,
                        inputs={"task_path": str(BACKLOG_DIR / eid / "validation-report.md"),
                                "epic_dir": str(BACKLOG_DIR / eid), "execute_writes": True})
                except FileNotFoundError:
                    return {"ok": False, "error": "claude CLI not found — no fix written"}
                except Exception as exc:
                    return {"ok": False, "error": str(exc)}
                _git_run(wt, ["add", "-A"])
                _git_run(wt, ["commit", "-m", f"agentic: fix build (attempt {attempts + 1})"])
                after = (_git_run(wt, ["rev-parse", "HEAD"]).stdout or "").strip()
                changed = bool(after and after != before)
                set_epic_state(eid, fix_attempts=attempts + 1, validated=False, validation=None,
                               fix_base=before, fix_head=after)
                if changed:
                    nfiles = len([l for l in _git_run(wt, ["diff", "--name-only", f"{before}..{after}"]).stdout.splitlines() if l.strip()])
                    job.emit(f"Fix committed on {eb} ({nfiles} file(s)). Review the fix diff, then Re-validate.", "ok")
                else:
                    job.emit("Agent made no changes. Re-validate or fix manually.", "skip")
                return {"ok": True, "branch": eb, "attempt": attempts + 1, "changed": changed}
            finally:
                _git_run(repo, ["worktree", "remove", "--force", str(wt)])
                _git_run(repo, ["worktree", "prune"])
    return target


def _epic_routes_added(wt, base):
    """High-recall view: the route files (app-router page/api) this epic added or changed
    vs its base, derived from the branch diff. Robust where the spec-mention heuristic is
    blind (dynamic [id] routes, unquoted paths). Returns [{route, kind, file, status}]."""
    r = _git_run(wt, ["diff", "--name-status", f"{base}...HEAD"])
    if r.returncode != 0:
        r = _git_run(wt, ["diff", "--name-status", base])
    out, seen = [], set()
    for line in (r.stdout or "").splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        status, path = parts[0].strip(), parts[-1].strip()
        mapped = _ser.file_to_route(path)
        if not mapped:
            continue
        route, kind = mapped
        if (route, kind) in seen:
            continue
        seen.add((route, kind))
        out.append({"route": route, "kind": kind, "file": path, "status": status[:1]})
    out.sort(key=lambda x: (x["kind"], x["route"]))
    return out


def _nav_orphans(wt):
    """Nav links (components/NavBar.tsx) that point to a route with no page on this branch —
    i.e. a menu item that would 404 (the /saved class of defect that tsc+build misses).
    Reads NavBar + walks app/ for page routes, both from the worktree. Returns
    {checked, orphans:[href...], routes} or None if there is no NavBar to check."""
    nav = Path(wt) / "components" / "NavBar.tsx"
    if not nav.exists():
        return None
    try:
        hrefs = _ser.nav_hrefs(nav.read_text(errors="ignore"))
    except Exception:
        return None
    routes = set()
    for root in (Path(wt) / "app", Path(wt) / "src" / "app"):
        if not root.exists():
            continue
        for pf in root.rglob("page.*"):
            try:
                rel = str(pf.relative_to(wt))
            except Exception:
                continue
            mapped = _ser.file_to_route(rel)
            if mapped and mapped[1] == "page":
                routes.add(mapped[0])
    orphans = [h for h in hrefs if not _ser.route_set_has(h, routes)]
    return {"checked": len(hrefs), "orphans": orphans, "routes": len(routes)}


def _branch_route_set(wt):
    """All app-router routes (page + api) present on the branch worktree, as a sorted list.
    Used to auto-check route-bearing acceptance criteria during Verify."""
    routes = set()
    for root in (Path(wt) / "app", Path(wt) / "src" / "app"):
        if not root.exists():
            continue
        for pat in ("page.*", "route.*"):
            for f in root.rglob(pat):
                try:
                    rel = str(f.relative_to(wt))
                except Exception:
                    continue
                mapped = _ser.file_to_route(rel)
                if mapped:
                    routes.add(mapped[0])
    return sorted(routes)


def verify_epic(epic_id):
    """Deeper-than-tsc check: do the routes the spec PROMISED actually exist as files
    on the assembled epic branch? Reuses the platform's pure verify_routes (the same
    check the autonomous path runs) against a lightweight worktree of agentic/epic-<id>.
    Stores a compact summary in epic-state (route_verify) for the UI. INFORMATIONAL —
    does NOT gate preview/push. Heuristic: dynamic routes like /users/[id] can show as
    false positives, so we never block on it in this version."""
    def target(job):
        eid = _safe_epic_id(epic_id)
        if not eid:
            return {"ok": False, "error": "invalid epic id"}
        es = load_epic_state(eid)
        if not es.get("assembled"):
            return {"ok": False, "error": "epic not assembled — build the epic branch first"}
        product, repo, err = _resolve_repo(eid)
        if err:
            return {"ok": False, "error": err}
        eb = _epic_branch(eid)
        wt = Path(repo).parent / ".agentic-worktrees" / f"{eb.split('/')[-1]}-verify-{datetime.now().strftime('%H%M%S')}"
        with git_ops.repo_lock(repo):
            r = _git_run(repo, ["worktree", "add", str(wt), eb])
            if r.returncode != 0:
                return {"ok": False, "error": "git worktree failed: " + (r.stderr or "").strip()}
            try:
                from orchestrator.route_verification import verify_routes
                eb_base = _base_ref(repo)
                added = _epic_routes_added(wt, eb_base)
                if added:
                    job.emit(f"Routes this epic adds/changes ({len(added)}) — high-recall, from the branch diff:")
                    for a in added:
                        job.emit(f"  {a['status']} {a['route']}  ·  {a['kind']}  [{a['file']}]", "ok")
                else:
                    job.emit("This epic adds no app-router page/route files (nothing in the diff under app/**).", "skip")

                job.emit(f"Cross-check: routes the spec promised vs files present on {eb}…")
                res = verify_routes(BACKLOG_DIR / eid, str(wt))
                pages = res.get("routes", [])
                apis = res.get("api_routes", [])
                for c in pages + apis:
                    job.emit(("  OK   " if c["exists"] else "  MISS ") + c["route"] + " → " + c["expected_file"],
                             "ok" if c["exists"] else "err")
                missing = res.get("missing", [])
                summary = {
                    "result": res.get("result"),
                    "missing": [{"route": m["route"], "expected_file": m["expected_file"]} for m in missing],
                    "n_pages": len(pages),
                    "n_api": len(apis),
                    "verified_at": res.get("verified_at"),
                    "branch": eb,
                }
                set_epic_state(eid, route_verify=summary, routes_added=added)
                if not (pages or apis):
                    job.emit("Spec cross-check: no quoted route literals in the spec — only the diff view above "
                             "is meaningful here (the spec heuristic misses unquoted and dynamic [id] routes).", "skip")
                elif missing:
                    job.emit(f"Spec cross-check: {len(missing)} quoted route(s) have no matching file. "
                             "NOTE: low-recall heuristic — dynamic /…/[id] and unquoted paths are invisible to it.", "err")
                else:
                    job.emit(f"Spec cross-check: all {len(pages) + len(apis)} quoted route(s) have matching files.", "ok")

                nav = _nav_orphans(wt)
                if nav is None:
                    job.emit("Nav check: components/NavBar.tsx not found on this branch — skipped.", "skip")
                elif nav["orphans"]:
                    job.emit(f"Nav check: {len(nav['orphans'])} broken nav link(s) — a menu item points to a "
                             "route with no page (would 404 in prod):", "err")
                    for h in nav["orphans"]:
                        job.emit(f"  BROKEN {h} → no app{h}/page.* on this branch", "err")
                else:
                    job.emit(f"Nav check: all {nav['checked']} nav link(s) resolve to a page.", "ok")
                set_epic_state(eid, nav_orphans=(nav["orphans"] if nav else None),
                               branch_routes=_branch_route_set(wt))

                return {"ok": True, "added": len(added), "result": res.get("result"),
                        "missing": len(missing), "n_pages": len(pages), "n_api": len(apis),
                        "nav_broken": (len(nav["orphans"]) if nav else 0)}
            except Exception as exc:
                return {"ok": False, "error": str(exc)}
            finally:
                _git_run(repo, ["worktree", "remove", "--force", str(wt)])
                _git_run(repo, ["worktree", "prune"])
    return target


def epic_fix_diff(epic_id, path=""):
    eid = _safe_epic_id(epic_id)
    es = load_epic_state(eid)
    base, head = es.get("fix_base"), es.get("fix_head")
    if not base or not head or base == head:
        return {"error": "no fix diff available"}
    product, repo, err = _resolve_repo(eid)
    if err:
        return {"error": err}
    args = ["diff", f"{base}..{head}"]
    if path:
        args += ["--", path]
    return {"diff": _git_run(repo, args).stdout, "base": base, "head": head}


def _base_branch(repo):
    r = _git_run(repo, ["symbolic-ref", "--short", "refs/remotes/origin/HEAD"])
    if r.returncode == 0 and r.stdout.strip():
        return r.stdout.strip().split("/")[-1]
    for b in ("main", "master"):
        if _git_run(repo, ["rev-parse", "--verify", b]).returncode == 0:
            return b
    return "main"


def _epic_human_title(epic_id):
    p = BACKLOG_DIR / epic_id / "epic.md"
    if p.exists():
        for line in p.read_text(errors="ignore").splitlines():
            s = line.strip()
            if s.startswith("# "):
                return s[2:].strip()
    return ""


def _preview_path(repo, epic_id):
    return Path(repo).parent / ".agentic-worktrees" / f"preview-{_epic_branch(epic_id).split('-', 1)[-1]}"


PREVIEW_PROCS = {}
PREVIEW_GUARD = threading.Lock()
PREVIEW_PORT = 3100


def _preview_kill(eid):
    import os
    import signal
    with PREVIEW_GUARD:
        ent = PREVIEW_PROCS.pop(eid, None)
    if not ent:
        return
    proc = ent["proc"]
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    except Exception:
        try:
            proc.terminate()
        except Exception:
            pass
    try:
        proc.wait(timeout=5)
    except Exception:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass


def _preview_state(eid):
    with PREVIEW_GUARD:
        ent = PREVIEW_PROCS.get(eid)
    if not ent:
        return None
    alive = ent["proc"].poll() is None
    if not alive:
        with PREVIEW_GUARD:
            PREVIEW_PROCS.pop(eid, None)
    return {"running": alive, "port": ent["port"],
            "url": f"http://localhost:{ent['port']}", "log": list(ent["log"])}


def _ensure_worktree(repo, eb, wt):
    """Make sure `wt` is a valid worktree checked out on `eb` with a real working
    tree (package.json present). Cleans stale/empty leftovers and retries. Returns
    an error string or None on success."""
    _git_run(repo, ["worktree", "prune"])
    if wt.exists():
        if (wt / "package.json").exists():
            return None
        _git_run(repo, ["worktree", "remove", "--force", str(wt)])
        try:
            shutil.rmtree(wt, ignore_errors=True)
        except Exception:
            pass
    r = _git_run(repo, ["worktree", "add", str(wt), eb])
    if r.returncode != 0:
        _git_run(repo, ["worktree", "prune"])
        try:
            shutil.rmtree(wt, ignore_errors=True)
        except Exception:
            pass
        r = _git_run(repo, ["worktree", "add", str(wt), eb])
        if r.returncode != 0:
            return "git worktree failed: " + (r.stderr or "").strip()
    if not (wt / "package.json").exists():
        return "worktree created but package.json is missing — the epic branch may be empty"
    return None


def preview_start(epic_id):
    """Managed preview: ensure a worktree on the epic branch (node_modules symlinked,
    test .env.local written), then launch `npm run dev -p 3100` as a tracked background
    process whose output is streamed. Console owns the process; Stop kills it."""
    eid = _safe_epic_id(epic_id)
    if not eid:
        return {"ok": False, "error": "invalid epic id"}
    if not load_epic_state(eid).get("assembled"):
        return {"ok": False, "error": "assemble the epic branch first"}
    product, repo, err = _resolve_repo(eid)
    if err:
        return {"ok": False, "error": err}
    eb = _epic_branch(eid)
    if _git_run(repo, ["rev-parse", "--verify", eb]).returncode != 0:
        return {"ok": False, "error": "epic branch not found — re-assemble"}
    wt = _preview_path(repo, eid)
    with git_ops.repo_lock(repo):
        werr = _ensure_worktree(repo, eb, wt)
    if werr:
        return {"ok": False, "error": werr}
    base_nm = Path(repo) / "node_modules"
    wt_nm = wt / "node_modules"
    if base_nm.exists() and not wt_nm.exists():
        try:
            wt_nm.symlink_to(base_nm, target_is_directory=True)
        except Exception:
            pass
    import secrets
    envf = wt / ".env.local"
    if not envf.exists():
        try:
            envf.write_text(f"APP_USERNAME=admin\nAPP_PASSWORD=admin\nSESSION_SECRET={secrets.token_hex(32)}\n")
        except Exception:
            pass
    set_epic_state(eid, preview_path=str(wt))
    _preview_kill(eid)  # no duplicates
    import subprocess
    try:
        proc = subprocess.Popen(["npm", "run", "dev", "--", "-p", str(PREVIEW_PORT)],
                                cwd=str(wt), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, bufsize=1, start_new_session=True)
    except FileNotFoundError:
        return {"ok": False, "error": "npm not found on this machine"}
    from collections import deque
    buf = deque(maxlen=400)

    def reader():
        try:
            for line in proc.stdout:
                buf.append(line.rstrip("\n"))
        except Exception:
            pass
    threading.Thread(target=reader, daemon=True).start()
    with PREVIEW_GUARD:
        PREVIEW_PROCS[eid] = {"proc": proc, "port": PREVIEW_PORT, "path": str(wt),
                              "log": buf, "started": time.time()}
    return {"ok": True, "port": PREVIEW_PORT, "url": f"http://localhost:{PREVIEW_PORT}",
            "user": "admin", "password": "admin"}


def preview_active():
    """The single currently-running preview (one port, one worktree at a time),
    so the sidebar can offer Open/Stop from anywhere."""
    for eid in list(PREVIEW_PROCS):
        st = _preview_state(eid)
        if st and st.get("running"):
            title = _epic_human_title(eid) or eid
            return {"running": True, "epic_id": eid, "port": st["port"],
                    "url": st["url"], "title": title}
    return {"running": False}


def preview_log(epic_id):
    eid = _safe_epic_id(epic_id)
    st = _preview_state(eid)
    if not st:
        return {"running": False, "log": []}
    return st


def preview_stop(epic_id):
    eid = _safe_epic_id(epic_id)
    if not eid:
        return {"ok": False, "error": "invalid epic id"}
    _preview_kill(eid)
    product, repo, err = _resolve_repo(eid)
    if not err and repo:
        wt = _preview_path(repo, eid)
        with git_ops.repo_lock(repo):
            _git_run(repo, ["worktree", "remove", "--force", str(wt)])
            _git_run(repo, ["worktree", "prune"])
    set_epic_state(eid, preview_path=None)
    return {"ok": True}


def preview_mark(epic_id):
    eid = _safe_epic_id(epic_id)
    if not eid:
        return {"ok": False, "error": "invalid epic id"}
    if not load_epic_state(eid).get("validated"):
        return {"ok": False, "error": "validate the epic first"}
    set_epic_state(eid, previewed=True)
    return {"ok": True, "previewed": True}


import atexit


@atexit.register
def _kill_all_previews():
    for eid in list(PREVIEW_PROCS):
        try:
            _preview_kill(eid)
        except Exception:
            pass


def push_epic(epic_id):
    """Push the validated+previewed epic branch to origin and open a PR — but NEVER
    merge. Merging (and the prod deploy it triggers) stays a manual GitHub action.
    The console never merges and never deploys."""
    def target(job):
        import subprocess
        eid = _safe_epic_id(epic_id)
        if not eid:
            return {"ok": False, "error": "invalid epic id"}
        es = load_epic_state(eid)
        if not es.get("validated"):
            return {"ok": False, "error": "validate the epic first"}
        if not es.get("previewed"):
            return {"ok": False, "error": "preview the epic first"}
        product, repo, err = _resolve_repo(eid)
        if err:
            return {"ok": False, "error": err}
        eb = _epic_branch(eid)
        if _git_run(repo, ["rev-parse", "--verify", eb]).returncode != 0:
            return {"ok": False, "error": "epic branch not found — re-assemble"}
        base = _base_branch(repo)
        job.emit(f"Pushing {eb} → origin…")
        with git_ops.repo_lock(repo):
            pr = _git_run(repo, ["push", "-u", "origin", eb])
        if pr.returncode != 0:
            job.emit("push failed: " + (pr.stderr or "").strip(), "err")
            return {"ok": False, "error": "git push failed: " + (pr.stderr or "").strip()}
        title = _epic_human_title(eid) or f"Epic {eid}"
        body = ("Assembled by the agentic console via cherry-pick of accepted tasks, "
                "validated (tsc + build), previewed locally. NOT merged — review and merge manually.")
        pr_url = ""
        job.emit(f"Opening PR into {base} via gh (no merge)…")
        try:
            cp = subprocess.run(["gh", "pr", "create", "--head", eb, "--base", base,
                                 "--title", title, "--body", body],
                                cwd=repo, capture_output=True, text=True, timeout=120)
            if cp.stdout and cp.stdout.strip():
                pr_url = cp.stdout.strip().splitlines()[-1].strip()
            if not pr_url:
                vv = subprocess.run(["gh", "pr", "view", eb, "--json", "url", "-q", ".url"],
                                    cwd=repo, capture_output=True, text=True)
                pr_url = (vv.stdout or "").strip()
        except FileNotFoundError:
            job.emit("gh not found — branch pushed; open the PR manually on GitHub.", "skip")
        set_epic_state(eid, pushed=True, pr_url=pr_url)
        if pr_url:
            job.emit(f"Pushed. PR opened (NOT merged): {pr_url}", "ok")
        else:
            job.emit(f"Pushed {eb} to origin. Open a PR on GitHub and merge it yourself.", "ok")
        return {"ok": True, "branch": eb, "pr_url": pr_url, "merged": False}
    return target


def rollback_epic(epic_id):
    """Send the epic back for rework (e.g. a problem found at preview): stop preview,
    delete the local epic branch, and clear epic-level stage flags — but KEEP each
    task's implemented/accepted work so you can re-run the broken task and reassemble."""
    eid = _safe_epic_id(epic_id)
    if not eid:
        return {"ok": False, "error": "invalid epic id"}
    _preview_kill(eid)
    product, repo, err = _resolve_repo(eid)
    if not err and repo:
        wt = _preview_path(repo, eid)
        with git_ops.repo_lock(repo):
            _git_run(repo, ["worktree", "remove", "--force", str(wt)])
            _git_run(repo, ["worktree", "prune"])
            eb = _epic_branch(eid)
            _git_run(repo, ["branch", "-D", eb])
    set_epic_state(eid, assembled=False, validated=False, validation=None, previewed=False,
                   pushed=False, pr_url=None, preview_path=None, fix_attempts=0,
                   fix_base=None, fix_head=None)
    return {"ok": True, "epic_id": eid}


_EPIC_STAGES = ["implementing", "assembled", "validated", "previewed", "pushed"]


def epic_criteria(epic_id):
    """Stage 2 review surface: the spec's success/acceptance criteria (texts via the platform's
    pure build_criteria_verification) crossed with our Verify signals (branch_routes, nav_orphans
    from the last Verify) → each criterion tagged confirmed / not_met / review. Read-only:
    does NOT call write_criteria_verification / attach_evidence / set_outcome_status."""
    eid = _safe_epic_id(epic_id)
    if not eid:
        return (400, {"error": "invalid epic id"})
    try:
        from orchestrator.outcome_criteria import build_criteria_verification
        cv = build_criteria_verification(BACKLOG_DIR / eid, note="")
    except Exception as exc:
        return {"error": f"criteria extraction failed: {exc}"}
    es = load_epic_state(eid)
    branch = es.get("branch_routes")
    nav = es.get("nav_orphans") or []
    verified = branch is not None

    def mk(items):
        out = []
        for t in (items or []):
            if verified:
                state, why = _ser.criterion_state(t, branch, nav)
            else:
                state = "review"
                why = "роут — прогони Verify для авто-проверки" if _ser.criterion_routes(t) else "ручная проверка"
            out.append({"text": t, "state": state, "why": why})
        return out

    def counts(xs):
        c = {"confirmed": 0, "not_met": 0, "review": 0}
        for x in xs:
            c[x["state"]] = c.get(x["state"], 0) + 1
        return c

    succ = mk(cv.get("success_criteria"))
    acc = mk(cv.get("acceptance_criteria"))
    return {"success": succ, "acceptance": acc, "verified": verified,
            "counts": {"success": counts(succ), "acceptance": counts(acc)},
            "total": len(succ) + len(acc)}


def epic_stage(epic_id):
    eid = _safe_epic_id(epic_id)
    if not eid:
        return {"error": "invalid epic id"}
    bs = epic_build_status(eid)
    es = load_epic_state(eid)
    if es.get("pushed"):
        stage = "pushed"
    elif es.get("previewed"):
        stage = "previewed"
    elif es.get("validated"):
        stage = "validated"
    elif es.get("assembled"):
        stage = "assembled"
    else:
        stage = "implementing"  # not assembled yet (whether or not all tasks accepted)
    pv = _preview_state(eid)
    return {"stage": stage, "stages": _EPIC_STAGES, "buildable": bs.get("buildable"),
            "assembled": bool(es.get("assembled")), "validated": bool(es.get("validated")),
            "validation": es.get("validation"), "fix_attempts": es.get("fix_attempts", 0),
            "route_verify": es.get("route_verify"),
            "routes_added": es.get("routes_added"),
            "nav_orphans": es.get("nav_orphans"),
            "has_fix": bool(es.get("fix_head") and es.get("fix_head") != es.get("fix_base")),
            "previewed": bool(es.get("previewed")), "preview_path": es.get("preview_path"),
            "preview_running": bool(pv and pv.get("running")),
            "preview_port": (pv or {}).get("port", PREVIEW_PORT),
            "preview_url": (pv or {}).get("url"),
            "released": bool(es.get("pushed")), "pushed": bool(es.get("pushed")), "pr_url": es.get("pr_url"),
            "accepted": bs.get("accepted"),
            "pending": bs.get("pending"), "total": bs.get("total"), "branch": bs.get("branch")}


def reset_epic_runs(epic_id):
    eid = _safe_epic_id(epic_id)
    if not eid:
        return {"ok": False, "error": "invalid epic id"}
    p = _runstate_path(eid)
    if p.exists():
        try:
            p.unlink()
        except Exception:
            pass
    product, repo, err = _resolve_repo(eid)
    deleted = None
    if not err and repo:
        with git_ops.repo_lock(repo):
            _git_run(repo, ["worktree", "prune"])
            eb = _epic_branch(eid)
            tag = eb.split("-", 1)[-1]
            for b in (_git_run(repo, ["branch", "--list", "agentic/*"]).stdout or "").splitlines():
                name = b.strip().lstrip("* ").strip()
                if name and (name == eb or name.startswith(f"agentic/task-{tag}-") or name.startswith("agentic/task-")):
                    _git_run(repo, ["branch", "-D", name])
            deleted = eb
    return {"ok": True, "epic_id": eid, "reset_branch": deleted}


def reset_task_run(epic_id, task_file):
    """Return ONE task to todo: clear a stuck/running inflight job, drop its
    run-state entry, and delete its reusable branch so a re-run starts clean.
    Lets the user recover a task whose run crashed mid-flight without nuking
    the whole epic (unlike reset_epic_runs)."""
    eid = _safe_epic_id(epic_id)
    if not eid or "/" in (task_file or "") or ".." in (task_file or ""):
        return {"ok": False, "error": "invalid task reference"}
    # 1) clear any stuck inflight job for this task (the "running…" that never ended)
    key = ("task_run", eid, task_file)
    with JOBS_LOCK:
        jid = INFLIGHT.get(key)
        if jid is not None:
            INFLIGHT.pop(key, None)
            j = JOBS.get(jid)
            if j and not j.done:
                j.done = True
                j.result = {"ok": False, "error": "reset by user"}
    # 2) drop this task's run-state entry -> it reads as todo again
    d = load_runstate(eid)
    removed = d.pop(task_file, None)
    try:
        _runstate_path(eid).write_text(json.dumps(d, ensure_ascii=False, indent=2))
    except Exception:
        pass
    # 3) delete the task's reusable branch so the next run is clean
    deleted = None
    product, repo, err = _resolve_repo(eid)
    if not err and repo:
        stem = Path(task_file).stem
        tb = _task_branch(eid, stem)
        with git_ops.repo_lock(repo):
            _git_run(repo, ["worktree", "prune"])
            if _git_run(repo, ["branch", "-D", tb]).returncode == 0:
                deleted = tb
    return {"ok": True, "epic_id": eid, "task_file": task_file,
            "was": (removed or {}).get("state"), "deleted_branch": deleted}


def task_detail(epic_id, task_file):
    eid = _safe_epic_id(epic_id)
    if not eid or "/" in (task_file or "") or ".." in (task_file or ""):
        return {"error": "invalid task reference"}
    p = BACKLOG_DIR / eid / task_file
    if not p.is_file():
        return {"error": "task not found"}
    run = load_runstate(eid).get(task_file, {})
    return {"content": p.read_text(errors="ignore"), "run": run,
            "task": _parse_task_file(p)}


def task_diff(epic_id, task_file, path):
    eid = _safe_epic_id(epic_id)
    run = load_runstate(eid).get(task_file, {})
    base, head = run.get("base"), run.get("head")
    if not base or not head:
        return {"error": "no run diff available"}
    product, repo, err = _resolve_repo(eid)
    if err:
        return {"error": err}
    args = ["diff", f"{base}..{head}"]
    if path:
        args += ["--", path]
    r = _git_run(repo, args)
    return {"diff": r.stdout, "base": base, "head": head}


def product_overview(product_name):
    epics = list_epics(product_name)
    estatus = {}
    tstatus = {}
    total_tasks = 0
    for e in epics:
        estatus[e.get("status", "—")] = estatus.get(e.get("status", "—"), 0) + 1
        ed = BACKLOG_DIR / e["id"]
        for tf in sorted(ed.glob("task-*.md")):
            t = _parse_task_file(tf)
            total_tasks += 1
            st = t["status"] or "—"
            tstatus[st] = tstatus.get(st, 0) + 1
    bl = read_baseline(product_name)
    hist = repo_history(product_name)
    stages = {}
    for e in epics:
        try:
            s = epic_stage(e["id"]).get("stage")
        except Exception:
            s = None
        if s:
            stages[s] = stages.get(s, 0) + 1
    return {
        "epics_total": len(epics), "epics_by_status": estatus,
        "epics_by_stage": stages,
        "tasks_total": total_tasks, "tasks_by_status": tstatus,
        "baseline": bl.get("overall") if bl.get("exists") else None,
        "runs": len(hist.get("runs", [])),
        "analysis_exists": (MEMORY_DIR / f"{product_name}-analysis.md").exists(),
    }


def epic_detail(epic_id):
    epic_dir = BACKLOG_DIR / epic_id
    if not epic_dir.is_dir():
        return None
    files = sorted(p.name for p in epic_dir.iterdir() if p.is_file())
    summary = epic_summary(epic_dir)
    stations = _stage_status_for_epic(epic_dir, files)

    # which artifact belongs to which stage (best-effort mapping)
    stage_of = {}
    for st in PIPELINE:
        for out in st["outputs"]:
            stage_of[out] = st["id"]
    # extra known artifacts that aren't listed as canonical stage outputs
    stage_of.update({
        "product-status.txt": "decompose",
        "feature-spec.md": "approve_product",
        "decomposition.md": "approve_spec",
        "tasks.md": "approve_spec",
        "spec-status.txt": "approve_spec",
        "dag.json": "approve_spec",
        "validation.md": "execute",
        "validation.json": "execute",
        "release-verification.md": "execute",
        "release-verification.json": "execute",
    })
    artifacts = []
    for name in files:
        stage = stage_of.get(name)
        if stage is None and name.startswith("task-"):
            stage = "approve_spec"
        artifacts.append({
            "name": name,
            "kind": _kind_of(name),
            "size": (epic_dir / name).stat().st_size,
            "stage": stage,
        })

    tasks = []
    rs = load_runstate(epic_id)
    task_paths = [epic_dir / n for n in files if n.startswith("task-") and n.endswith(".md")]
    depmap = epic_dep_nums(epic_id, task_paths)
    for name in files:
        if name.startswith("task-") and name.endswith(".md"):
            ttext = (epic_dir / name).read_text(errors="ignore")
            fields = {}
            for line in ttext.splitlines():
                if ":" in line and not line.startswith("#") and not line.startswith("**"):
                    k, _, v = line.partition(":")
                    k = k.strip().lower()
                    if k in {"status", "type", "pipeline", "risk", "pr", "run"}:
                        fields[k] = v.strip()
            title = name
            for line in ttext.splitlines():
                if line.strip().startswith("### Task"):
                    title = line.replace("###", "").strip()
                    break
            run = rs.get(name, {})
            rstate = run.get("state")
            eff = _ser.eff_status(fields.get("status"), rstate, _DONE_STATUSES)
            tasks.append({"file": name, "title": title, "run_state": rstate,
                          "eff_status": eff, "num": _task_num(name),
                          "depends_on": sorted(depmap.get(_task_num(name), [])), **fields})

    def _txt(name):
        p = epic_dir / name
        return p.read_text(errors="ignore").strip() if p.exists() else ""

    have = set(files)
    has_task = any(f.startswith("task-") and f.endswith(".md") for f in have)
    is_quick = bool(load_epic_state(epic_id).get("quick"))
    epic_kind = load_epic_state(epic_id).get("kind") or ("task" if is_quick else "")
    if is_quick and has_task:
        next_action = {"id": "execute", "label": "Run the task", "agent": "Runtime agents"}
    elif "product-spec.md" not in have:
        next_action = {"id": "decompose", "label": "Run Product Agent", "agent": "Product Agent"}
    elif "feature-spec.md" not in have:
        next_action = {"id": "approve_product", "label": "Approve → Feature spec", "agent": "Product Analyst Agent"}
    elif not has_task:
        next_action = {"id": "approve_spec", "label": "Approve → Backlog tasks", "agent": "Backlog Decomposer"}
    else:
        next_action = {"id": "execute", "label": "Ready for execution", "agent": "Runtime agents"}

    return {
        "summary": summary,
        "stations": stations,
        "artifacts": artifacts,
        "tasks": tasks,
        "quick": is_quick,
        "kind": epic_kind,
        "outcome": _read_json(epic_dir / "outcome.json"),
        "statuses": {
            "product": _txt("product-status.txt"),
            "spec": _txt("spec-status.txt"),
        },
        "next_action": next_action,
    }


def list_runs(limit=60):
    if not RUNS_DIR.exists():
        return []
    runs = []
    dirs = [d for d in RUNS_DIR.iterdir() if d.is_dir()]
    dirs.sort(key=lambda d: d.stat().st_mtime, reverse=True)
    for d in dirs[:limit]:
        rj = _read_json(d / "run.json") or {}
        runs.append({
            "id": d.name,
            "type": rj.get("run_type", ""),
            "product": rj.get("product", ""),
            "status": rj.get("status", ""),
            "stage": rj.get("current_stage", ""),
            "updated_at": rj.get("updated_at", ""),
        })
    return runs


def resolve_artifact(rel):
    """Resolve a requested artifact path safely inside ALLOWED_ROOTS."""
    target = (ROOT / rel).resolve()
    for root in ALLOWED_ROOTS:
        try:
            target.relative_to(root.resolve())
            if target.is_file():
                return target
        except ValueError:
            continue
    return None


# --- default validators per framework (used by Connect repo) ------------------
FRAMEWORK_VALIDATORS = {
    "nextjs": [
        {"name": "typecheck", "command": "npx tsc --noEmit", "required": True},
        {"name": "build", "command": "npm run build", "required": True},
    ],
    "node": [
        {"name": "build", "command": "npm run build", "required": True},
    ],
    "python": [
        {"name": "compile", "command": "python -m compileall -q .", "required": True},
    ],
    "other": [],
}


def _run_cli(args, log, label):
    """Run a platform CLI command from ROOT, stream stdout/stderr into log."""
    import subprocess
    log.append({"ts": datetime.now().strftime("%H:%M:%S"), "msg": f"{label}: started"})
    try:
        proc = subprocess.run(
            ["python3"] + args, cwd=str(ROOT), text=True,
            capture_output=True, timeout=900,
        )
    except FileNotFoundError:
        log.append({"ts": "", "msg": f"{label}: python3 not found", "level": "err"})
        return False
    except subprocess.TimeoutExpired:
        log.append({"ts": "", "msg": f"{label}: timed out", "level": "err"})
        return False
    tail = (proc.stdout or "").strip().splitlines()[-8:]
    for line in tail:
        log.append({"ts": "", "msg": line})
    if proc.returncode != 0:
        err = (proc.stderr or "").strip().splitlines()[-4:]
        for line in err:
            log.append({"ts": "", "msg": line, "level": "err"})
        log.append({"ts": "", "msg": f"{label}: exit {proc.returncode}", "level": "err"})
        return False
    log.append({"ts": datetime.now().strftime("%H:%M:%S"), "msg": f"{label}: completed", "level": "ok"})
    return True


def git_status(repo_path=None):
    """Status of a git repo (platform root by default)."""
    import subprocess
    repo = str(repo_path or ROOT)

    def g(*a):
        try:
            return subprocess.run(["git", "-C", repo, *a], text=True,
                                  capture_output=True, timeout=15).stdout.strip()
        except Exception:
            return ""

    inside = g("rev-parse", "--is-inside-work-tree")
    if inside != "true":
        return {"git": False}
    branch = g("rev-parse", "--abbrev-ref", "HEAD")
    porcelain = g("status", "--porcelain")
    dirty = [l for l in porcelain.splitlines() if l.strip()]
    ahead = behind = 0
    counts = g("rev-list", "--left-right", "--count", "@{upstream}...HEAD")
    if counts and "\t" in counts:
        try:
            behind, ahead = (int(x) for x in counts.split("\t"))
        except Exception:
            pass
    remote = g("remote", "get-url", "origin")
    return {
        "git": True, "branch": branch, "dirty_count": len(dirty),
        "ahead": ahead, "behind": behind, "remote": remote,
    }


def connect_repo(path, name, framework, force=False):
    """Create products/<name>/config.yaml pointing at a local repo."""
    log = []

    def step(msg, level=""):
        log.append({"ts": datetime.now().strftime("%H:%M:%S"), "msg": msg, "level": level})

    repo = Path(path).expanduser()
    if not repo.exists() or not repo.is_dir():
        return {"ok": False, "error": f"Path is not a folder: {repo}", "log": log}

    is_git = (repo / ".git").exists()
    step(f"Repo path OK: {repo}" + ("" if is_git else "  (warning: no .git found)"),
         "" if is_git else "err")

    framework = framework if framework in FRAMEWORK_VALIDATORS else "other"
    name = name.strip() or repo.name
    cfg_dir = PRODUCTS_DIR / name
    cfg_path = cfg_dir / "config.yaml"
    if cfg_path.exists() and not force:
        return {"ok": False, "error": f"Product '{name}' already exists. Use a different name.",
                "log": log, "exists": True}

    validators = FRAMEWORK_VALIDATORS[framework]
    caps = {
        "typecheck": any(v["name"] == "typecheck" for v in validators),
        "build": any(v["name"] == "build" for v in validators),
        "lint": False, "unit_tests": False, "e2e_tests": False, "auto_pr": True,
    }

    lines = [
        f"name: {name}",
        f"repo_path: {repo}",
        "type: existing_product",
        "status: local",
        f"framework: {framework}",
        "",
        "capabilities:",
    ]
    for k, v in caps.items():
        lines.append(f"  {k}: {str(v).lower()}")
    lines.append("")
    lines.append("validators:")
    if validators:
        for v in validators:
            lines += [f"  - name: {v['name']}",
                      f"    command: {v['command']}",
                      f"    required: {str(v['required']).lower()}", ""]
    else:
        lines.append("  []")
        lines.append("")

    cfg_dir.mkdir(parents=True, exist_ok=True)
    cfg_path.write_text("\n".join(lines).rstrip() + "\n")
    step(f"Wrote products/{name}/config.yaml ({framework}, {len(validators)} validators)", "ok")

    gs = git_status(repo)
    if gs.get("git"):
        step(f"Git: branch {gs.get('branch')}" + (f", remote {gs.get('remote')}" if gs.get("remote") else ""))

    return {"ok": True, "name": name, "framework": framework, "git": gs, "log": log}


# --- stage 2 & 3: approve product spec / feature spec (real CLI) ---------------
def approve_product_spec(epic_id):
    epic_dir = BACKLOG_DIR / epic_id
    if not (epic_dir / "product-spec.md").exists():
        return {"ok": False, "error": "product-spec.md missing — run Product Agent first."}
    log = []
    ok = _run_cli(["agentic.py", "approve-product-spec", str(epic_dir)], log, "Product Analyst Agent")
    return {"ok": ok, "epic_id": epic_id, "produced": "feature-spec.md", "log": log}


def approve_feature_spec(epic_id):
    epic_dir = BACKLOG_DIR / epic_id
    if not (epic_dir / "feature-spec.md").exists():
        return {"ok": False, "error": "feature-spec.md missing — approve the product spec first."}
    log = []
    ok = _run_cli(["agentic.py", "approve-spec", str(epic_dir)], log, "Backlog Decomposer")
    return {"ok": ok, "epic_id": epic_id, "produced": "task-*.md + acceptance-scenarios.md", "log": log}


def commit_epic(epic_id, message=None):
    """Commit an epic's artifacts to the platform git history."""
    import subprocess
    epic_dir = BACKLOG_DIR / epic_id
    if not epic_dir.is_dir():
        return {"ok": False, "error": "epic not found"}
    rel = f"backlog/{epic_id}"
    msg = message or f"epic: {epic_id}"
    try:
        subprocess.run(["git", "-C", str(ROOT), "add", rel], check=True, capture_output=True, text=True)
        # also stage product config changes if any
        subprocess.run(["git", "-C", str(ROOT), "add", "products"], capture_output=True, text=True)
        proc = subprocess.run(["git", "-C", str(ROOT), "commit", "-m", msg],
                              capture_output=True, text=True)
        if proc.returncode != 0:
            out = (proc.stdout + proc.stderr).strip()
            if "nothing to commit" in out:
                return {"ok": True, "nothing": True, "message": "Nothing to commit."}
            return {"ok": False, "error": out[-300:]}
        return {"ok": True, "message": proc.stdout.strip().splitlines()[0] if proc.stdout else "Committed."}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


# --- step 0: Repository Analyst ------------------------------------------------
def analyze_product(product_name):
    log = []

    def step(msg, level=""):
        log.append({"ts": datetime.now().strftime("%H:%M:%S"), "msg": msg, "level": level})

    try:
        from orchestrator.repository_analyst import analyze_repository
    except Exception as exc:
        return {"ok": False, "error": f"Platform import failed: {exc}", "log": log}

    step(f"Repository Analyst: started for {product_name}")
    try:
        result = analyze_repository(product_name, write=True)
    except FileNotFoundError as exc:
        return {"ok": False, "error": f"Product not found: {exc}", "log": log}
    except Exception as exc:
        return {"ok": False, "error": str(exc), "log": log}

    step(f"Scanned {result['file_count']} files")
    if result["agent_ran"]:
        step("LLM analysis completed", "ok")
    else:
        step("LLM step skipped (no `claude` CLI) — wrote deterministic map only", "skip")
    step("Stored: memory analysis.md + architecture-memory + product-memory", "ok")

    return {
        "ok": True,
        "agent_ran": result["agent_ran"],
        "product": product_name,
        "file_count": result["file_count"],
        "summary": result["summary"],
        "log": log,
    }


def get_analysis(product_name):
    path = MEMORY_DIR / f"{product_name}-analysis.md"
    if not path.exists():
        return {"exists": False}
    return {"exists": True, "product": product_name, "content": path.read_text(errors="ignore")}


# --- the one write action in stage 1: run the Product Agent (decompose) -------
def inbox_list(product):
    return _inbox.list_items(BACKLOG_DIR, product)


def inbox_add(product, itype, text):
    return _inbox.add(BACKLOG_DIR, product, itype, text)


def inbox_delete(item_id):
    return _inbox.delete(BACKLOG_DIR, item_id)


def run_quick_task(product_name, request, kind="task"):
    """A 'quick task' is a ONE-task epic with NO planning phase: the user's plain
    request becomes a single task the agent implements directly. kind='bug' gives the
    agent a diagnostic frame (reproduce -> root cause -> minimal fix -> guard) instead of
    a plain 'implement this'. Flows through the normal execution UI afterwards."""
    try:
        from orchestrator.product_registry import load_product_config
        import decompose_feature as df
    except Exception as exc:
        return {"ok": False, "error": f"Platform import failed: {exc}"}
    try:
        product = load_product_config(product_name)
    except Exception as exc:
        return {"ok": False, "error": f"Product config error: {exc}"}
    if not (request or "").strip():
        return {"ok": False, "error": "empty request"}
    kind = "bug" if kind == "bug" else "task"
    repo_path = product.get("repo_path", "")
    prefix = "bug " if kind == "bug" else "quick "
    epic_dir = df.make_epic_dir(prefix + request)
    eid = epic_dir.name
    (epic_dir / "product.txt").write_text(product_name + "\n")
    (epic_dir / "epic.md").write_text(
        f"# Epic Request\n\n## Product\n\n{product_name}\n\n"
        f"## Repository\n\n{repo_path}\n\n## Request\n\n{request}\n")
    title = request.strip().splitlines()[0][:80]
    if kind == "bug":
        (epic_dir / "task-001.md").write_text(
            "Status: todo\nType: bug_fix\n\n"
            f"### Task 001 — Bug: {title}\n\n"
            f"**Problem:** {request.strip()}\n"
            "**Goal:** Reproduce the issue, find the ROOT CAUSE, and fix it with the smallest "
            "safe change — do not just patch the symptom. Add a lightweight guard or test only "
            "if it is cheap and directly relevant.\n"
            "**Scope:** Touch only what the fix needs. Do not refactor unrelated code.\n"
            "**Acceptance criteria:** The bug no longer reproduces; `npx tsc --noEmit` and the "
            "build pass; no dangling references; no unrelated changes.\n"
            "**Risk:** medium\n\n"
            "## Depends On\n\n_None_\n")
    else:
        (epic_dir / "task-001.md").write_text(
            "Status: todo\n\n"
            f"### Task 001 — {title}\n\n"
            f"**Goal:** {request.strip()}\n"
            "**Scope:** Implement the request directly, in the smallest reasonable change. "
            "Touch only what the request needs.\n"
            "**Acceptance criteria:** The request is satisfied; `npx tsc --noEmit` and the build "
            "pass; no dangling references remain.\n"
            "**Risk:** medium\n\n"
            "## Depends On\n\n_None_\n")
    set_epic_state(eid, quick=True, kind=kind)
    return {"ok": True, "epic_id": eid, "kind": kind}


def run_decompose(product_name, request):
    """Drive the real platform decompose stage. Always scaffolds the epic;
    attempts the Product Agent (which needs the `claude` CLI). Returns a log
    so the UI can show exactly what ran and what produced each artifact."""
    log = []
    created = []

    def step(msg):
        log.append({"ts": datetime.now().strftime("%H:%M:%S"), "msg": msg})

    try:
        from orchestrator.product_registry import load_product_config
        import decompose_feature as df
    except Exception as exc:
        return {"ok": False, "error": f"Platform import failed: {exc}",
                "log": log, "created": created}

    try:
        product = load_product_config(product_name)
    except Exception as exc:
        return {"ok": False, "error": f"Product config error: {exc}",
                "log": log, "created": created}

    repo_path = product["repo_path"]
    step(f"Loaded product '{product_name}' (repo: {repo_path})")

    epic_dir = df.make_epic_dir(request)
    step(f"Created epic folder: backlog/{epic_dir.name}")

    (epic_dir / "product.txt").write_text(product_name + "\n")
    created.append("product.txt")
    (epic_dir / "epic.md").write_text(
        f"# Epic Request\n\n## Product\n\n{product_name}\n\n"
        f"## Repository\n\n{repo_path}\n\n## Request\n\n{request}\n"
    )
    created.append("epic.md")
    step("Wrote epic.md")

    # Product Agent (LLM persona) -> product-spec.md. Needs the claude CLI.
    agent_ok = False
    try:
        from orchestrator.product_memory_context import format_product_memory
        memory = format_product_memory(product_name)
    except Exception:
        memory = ""
    step("Product Agent: started")
    try:
        spec = df.build_product_spec(
            product_name=product_name,
            repo_path=repo_path,
            request=request,
            product_memory=memory,
        )
        (epic_dir / "product-spec.md").write_text(spec)
        created.append("product-spec.md")
        agent_ok = True
        step("Product Agent: completed -> product-spec.md")
    except FileNotFoundError:
        step("Product Agent: SKIPPED - `claude` CLI not found on this machine")
    except Exception as exc:
        step(f"Product Agent: FAILED - {exc}")

    (epic_dir / "product-status.txt").write_text("product_pending_review\n")
    created.append("product-status.txt")

    try:
        from orchestrator.outcome_store import ensure_outcome
        ensure_outcome(epic_dir)
        created.append("outcome.json")
        step("Initialized outcome.json (status: planned)")
    except Exception as exc:
        step(f"outcome.json init failed: {exc}")

    return {
        "ok": True,
        "agent_ran": agent_ok,
        "epic_id": epic_dir.name,
        "created": created,
        "log": log,
        "next": "Review product-spec.md, then approve-product-spec",
    }


# --- repository workspace (read-only access to the product's repo) ------------
def _product_repo_path(product_name):
    try:
        from orchestrator.product_registry import load_product_config
        return load_product_config(product_name).get("repo_path", "")
    except Exception:
        return ""


def _safe_repo_target(repo_root, rel):
    """Resolve rel inside repo_root; None if outside or root missing."""
    root = Path(repo_root)
    if not root.exists():
        return None
    target = (root / (rel or "")).resolve()
    try:
        target.relative_to(root.resolve())
    except ValueError:
        return None
    return target


def repo_tree(product_name, rel=""):
    repo = _product_repo_path(product_name)
    if not repo:
        return {"error": "product has no repo_path"}
    target = _safe_repo_target(repo, rel)
    if target is None or not target.exists():
        return {"error": f"path not found: {rel}"}
    if not target.is_dir():
        return {"error": "not a directory"}

    entries = []
    for child in sorted(target.iterdir(), key=lambda p: (p.is_file(), p.name.lower())):
        if child.is_dir() and child.name in REPO_IGNORE_DIRS:
            continue
        rel_child = str(child.relative_to(Path(repo)))
        entries.append({
            "name": child.name,
            "path": rel_child,
            "type": "dir" if child.is_dir() else "file",
            "size": child.stat().st_size if child.is_file() else 0,
        })
    return {"repo": repo, "path": rel, "entries": entries}


def repo_file(product_name, rel, max_bytes=300_000):
    repo = _product_repo_path(product_name)
    if not repo:
        return {"error": "product has no repo_path"}
    target = _safe_repo_target(repo, rel)
    if target is None or not target.is_file():
        return {"error": f"file not found: {rel}"}
    data = target.read_bytes()
    if b"\x00" in data[:4096]:
        return {"path": rel, "binary": True, "size": len(data)}
    truncated = len(data) > max_bytes
    text = data[:max_bytes].decode("utf-8", errors="replace")
    return {"path": rel, "content": text, "truncated": truncated, "size": len(data)}


def repo_structure(product_name):
    repo = _product_repo_path(product_name)
    if not repo:
        return {"error": "product has no repo_path"}

    result = {
        "repo": repo,
        "exists": Path(repo).exists(),
        "file_count": 0,
        "is_empty": True,
        "categories": {},
        "imports": {},
        "hot_modules": [],
        "analysis_exists": (MEMORY_DIR / f"{product_name}-analysis.md").exists(),
    }
    if not result["exists"]:
        return result

    try:
        from orchestrator.repository_scanner import scan_repo
        from orchestrator.repository_intelligence import build_repository_map
        files = scan_repo(repo)
        result["file_count"] = len(files)
        result["is_empty"] = len(files) == 0
        result["categories"] = {k: v for k, v in build_repository_map(files).items() if v}
    except Exception as exc:
        result["categories_error"] = str(exc)
        files = []

    try:
        from orchestrator.import_analyzer import analyze_imports
        imports = analyze_imports(repo, files)
        result["imports"] = dict(list(imports.items())[:200])
        result["hot_modules"] = _hot_modules(imports)
    except Exception as exc:
        result["imports_error"] = str(exc)

    return result


def _hot_modules(imports):
    """Most-imported internal modules — a cheap 'where is the core' signal."""
    from collections import Counter
    counter = Counter()
    internal_prefixes = (".", "@/", "~/", "~", "src/", "lib/", "components/", "app/")
    for _file, deps in imports.items():
        for dep in deps:
            if dep.startswith(internal_prefixes):
                counter[dep] += 1
    return [{"module": m, "count": n} for m, n in counter.most_common(15)]


# Strip anything secret-looking before sending config to the browser.
_SECRET_HINTS = ("password", "secret", "token", "apikey", "api_key", "passwd")


def _strip_secrets(value):
    if isinstance(value, dict):
        return {
            k: ("•••" if any(h in str(k).lower() for h in _SECRET_HINTS) else _strip_secrets(v))
            for k, v in value.items()
        }
    if isinstance(value, list):
        return [_strip_secrets(v) for v in value]
    return value


def product_operational(product_name):
    """Operational inventory from the product config (secrets stripped)."""
    try:
        from orchestrator.product_registry import load_product_config
        cfg = load_product_config(product_name)
    except Exception as exc:
        return {"error": str(exc)}
    return {
        "framework": cfg.get("framework", ""),
        "status": cfg.get("status", ""),
        "capabilities": cfg.get("capabilities", {}),
        "validators": [
            {"name": v.get("name"), "command": v.get("command"), "required": v.get("required", True)}
            for v in cfg.get("validators", []) if isinstance(v, dict)
        ],
        "acceptance": _strip_secrets(cfg.get("acceptance", {})),
        "deployment": cfg.get("deployment", {}),
    }


def repo_history(product_name):
    """Prior runs / failures / architecture notes for this product."""
    try:
        from orchestrator.memory_store import load_run_memory, load_architecture_memory
    except Exception as exc:
        return {"error": str(exc)}
    runs = load_run_memory(product_name)[-15:]
    try:
        from orchestrator.failure_memory import load_failure_memory
        failures = load_failure_memory(product_name)[-10:]
    except Exception:
        failures = []
    try:
        arch = load_architecture_memory(product_name)
    except Exception:
        arch = []
    return {
        "runs": [
            {"run_id": r.get("run_id"), "request": r.get("request"),
             "status": r.get("status"), "validation": r.get("validation_result")}
            for r in reversed(runs)
        ],
        "failures": [
            {"run_id": f.get("run_id"), "type": f.get("failure_type"), "request": f.get("request")}
            for f in reversed(failures)
        ],
        "architecture_count": len(arch),
    }


def read_baseline(product_name):
    path = MEMORY_DIR / f"{product_name}-baseline.json"
    if not path.exists():
        return {"exists": False}
    data = _read_json(path) or {}
    return {"exists": True, **data}


def run_baseline(product_name):
    """Run the product's configured validators once to capture starting health."""
    log = []

    def step(msg, level=""):
        log.append({"ts": datetime.now().strftime("%H:%M:%S"), "msg": msg, "level": level})

    try:
        from orchestrator.product_registry import load_product_config
        from orchestrator.validation_runner import run_validators
    except Exception as exc:
        return {"ok": False, "error": str(exc), "log": log}
    try:
        cfg = load_product_config(product_name)
    except Exception as exc:
        return {"ok": False, "error": f"product config: {exc}", "log": log}

    repo = cfg["repo_path"]
    validators = cfg.get("validators", [])
    if not Path(repo).exists():
        return {"ok": False, "error": "repo path does not exist on this machine", "log": log}
    if not validators:
        step("No validators configured for this product", "skip")
        return {"ok": True, "overall": "none", "validators": [], "log": log}

    step(f"Running {len(validators)} validator(s) in {repo}")
    results = run_validators(repo, validators)
    out = []
    for r in results:
        passed = r.get("passed", False)
        step(f"{r.get('name')}: {'passed' if passed else 'failed'}"
             + (" (timed out)" if r.get("timed_out") else ""),
             "ok" if passed else "err")
        out.append({"name": r.get("name"), "passed": passed,
                    "required": r.get("required", True),
                    "exit_code": r.get("exit_code"), "timed_out": r.get("timed_out", False)})

    required = [r for r in out if r["required"]]
    overall = "passed" if required and all(r["passed"] for r in required) else "failed"
    data = {"overall": overall, "validators": out,
            "checked_at": datetime.now().isoformat(timespec="seconds")}
    try:
        MEMORY_DIR.mkdir(exist_ok=True)
        (MEMORY_DIR / f"{product_name}-baseline.json").write_text(
            json.dumps(data, indent=2, ensure_ascii=False))
    except Exception:
        pass
    step(f"Baseline: {overall}", "ok" if overall == "passed" else "err")
    return {"ok": True, **data, "log": log}


# --- Changes: git state of the product repo (read-only) -----------------------
def _git(repo, args, timeout=20):
    return git_ops.git(repo, args, timeout)


def _porcelain_status(xy):
    s = xy.strip()
    if "?" in s:
        return "untracked"
    if "R" in s:
        return "renamed"
    if "A" in s:
        return "added"
    if "D" in s:
        return "deleted"
    if "M" in s:
        return "modified"
    return "changed"


def repo_changes(product_name):
    repo = _product_repo_path(product_name)
    if not repo:
        return {"error": "product has no repo_path"}
    if not Path(repo).exists():
        return {"exists": False, "error": "repo path not found on this machine"}

    code, out, _ = _git(repo, ["rev-parse", "--is-inside-work-tree"])
    if code != 0 or out.strip() != "true":
        return {"exists": True, "is_git": False, "files": [], "count": 0}

    _, branch, _ = _git(repo, ["rev-parse", "--abbrev-ref", "HEAD"])
    _, out, _ = _git(repo, ["status", "--porcelain=v1", "-uall"])
    files = []
    for line in out.splitlines():
        if not line.strip():
            continue
        xy, path = line[:2], line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        files.append({"path": path, "xy": xy.strip(), "status": _porcelain_status(xy)})

    files.sort(key=lambda f: f["path"])
    return {"exists": True, "is_git": True, "branch": branch.strip(),
            "files": files, "count": len(files)}


def repo_diff(product_name, rel):
    repo = _product_repo_path(product_name)
    if not repo or not Path(repo).exists():
        return {"error": "repo not found"}
    if _safe_repo_target(repo, rel) is None:
        return {"error": "invalid path"}

    _, status_out, _ = _git(repo, ["status", "--porcelain=v1", "--", rel])
    if status_out.startswith("??"):
        target = Path(repo) / rel
        if target.is_file():
            data = target.read_bytes()
            if b"\x00" in data[:4096]:
                return {"path": rel, "untracked": True, "binary": True}
            text = data[:300_000].decode("utf-8", errors="replace")
            return {"path": rel, "untracked": True, "content": text,
                    "truncated": len(data) > 300_000}
        return {"path": rel, "untracked": True}

    _, out, _ = _git(repo, ["diff", "HEAD", "--", rel])
    return {"path": rel, "diff": out, "empty": not out.strip()}


# --- background jobs: stream agent progress, block double-runs ----------------
# Machinery lives in console.jobs; re-bind the SAME objects so existing call
# sites (start_job / _forward / JOBS / INFLIGHT) and the SSE handler are unchanged.
from console import jobs as _jobs
JOBS = _jobs.JOBS
INFLIGHT = _jobs.INFLIGHT
JOBS_LOCK = _jobs.JOBS_LOCK
Job = _jobs.Job
start_job = _jobs.start_job
_forward = _jobs._forward


# --- HTTP layer ---------------------------------------------------------------
# --- GET route table ---------------------------------------------------------
# do_GET dispatches through this dict instead of a long if/elif ladder, so routes
# are enumerable (test_routes guards against lost/duplicate paths) and each handler
# unpacks query params uniformly. A handler takes the parsed query dict and returns
# either a body (sent with 200) or a (status, body) tuple for non-200 responses.
# Special cases NOT in the table (handled directly in do_GET): "/", "/index.html",
# "/static/*" (static files), and "/api/job/stream" (SSE, writes the socket itself).

def _qp(q, key, default=""):
    """First value of a query param, matching the old q.get(key, [""])[0] idiom."""
    return q.get(key, [default])[0]


def _route_state(q):
    return {
        "version": platform_version(),
        "api_version": API_VERSION,
        "products": list_products(),
        "agents": AGENTS,
        "pipeline": PIPELINE,
    }


def _route_epics_overview(q):
    eps = list_epics(_qp(q, "product"))
    for e in eps:
        try:
            stg = epic_stage(e["id"])
            e["stage"] = stg.get("stage")
            e["accepted"] = len(stg.get("accepted") or [])
            e["total"] = stg.get("total")
            e["validation"] = stg.get("validation")
            e["pushed"] = stg.get("pushed")
            e["pr_url"] = stg.get("pr_url")
            e["preview_running"] = stg.get("preview_running")
            e["kind"] = load_epic_state(e["id"]).get("kind") or ("task" if load_epic_state(e["id"]).get("quick") else "epic")
        except Exception:
            e["stage"] = None
    return {"epics": eps}


def _route_jobs_active(q):
    with JOBS_LOCK:
        active = [{"job_id": j.id, "kind": j.kind, "key": list(j.key)}
                  for j in JOBS.values() if not j.done and j.kind == "task_run"]
    return {"active": active}


def _route_epic(q):
    d = epic_detail(_qp(q, "id"))
    return d if d else (404, {"error": "epic not found"})


def _route_job(q):
    job = JOBS.get(_qp(q, "id"))
    if not job:
        return (404, {"error": "job not found"})
    lines, done, result = job.snapshot(0)
    return {"id": job.id, "log": lines, "done": done, "result": result}


def _route_file(q):
    rel = _qp(q, "path")
    target = resolve_artifact(rel)
    if not target:
        return (404, {"error": "file not found or not allowed"})
    return {"path": rel, "content": target.read_text(errors="ignore")}


GET_ROUTES = {
    "/api/state": _route_state,
    "/api/inbox": lambda q: inbox_list(_qp(q, "product")),
    "/api/epics": lambda q: {"epics": list_epics(_qp(q, "product"))},
    "/api/epics/overview": _route_epics_overview,
    "/api/epics/archived": lambda q: {"epics": list_archived_epics(_qp(q, "product"))},
    "/api/overview": lambda q: product_overview(_qp(q, "product")),
    "/api/backlog": lambda q: product_backlog(_qp(q, "product")),
    "/api/task": lambda q: task_detail(_qp(q, "epic_id"), _qp(q, "task_file")),
    "/api/task/diff": lambda q: task_diff(_qp(q, "epic_id"), _qp(q, "task_file"), _qp(q, "path")),
    "/api/epic/build-status": lambda q: epic_build_status(_qp(q, "epic_id")),
    "/api/epic/stage": lambda q: epic_stage(_qp(q, "epic_id")),
    "/api/epic/criteria": lambda q: epic_criteria(_qp(q, "epic_id")),
    "/api/epic/fix-diff": lambda q: epic_fix_diff(_qp(q, "epic_id"), _qp(q, "path")),
    "/api/epic/preview-log": lambda q: preview_log(_qp(q, "epic_id")),
    "/api/preview/active": lambda q: preview_active(),
    "/api/jobs/active": _route_jobs_active,
    "/api/epic": _route_epic,
    "/api/runs": lambda q: {"runs": list_runs()},
    "/api/version": lambda q: {"api_version": API_VERSION},
    "/api/job": _route_job,
    "/api/repo/tree": lambda q: repo_tree(_qp(q, "product"), _qp(q, "path")),
    "/api/repo/file": lambda q: repo_file(_qp(q, "product"), _qp(q, "path")),
    "/api/repo/structure": lambda q: repo_structure(_qp(q, "product")),
    "/api/repo/operational": lambda q: product_operational(_qp(q, "product")),
    "/api/repo/history": lambda q: repo_history(_qp(q, "product")),
    "/api/repo/baseline": lambda q: read_baseline(_qp(q, "product")),
    "/api/repo/changes": lambda q: repo_changes(_qp(q, "product")),
    "/api/repo/diff": lambda q: repo_diff(_qp(q, "product"), _qp(q, "path")),
    "/api/git": lambda q: git_status(),
    "/api/analysis": lambda q: get_analysis(_qp(q, "product")),
    "/api/file": _route_file,
}


# --- POST route table --------------------------------------------------------
# Same convention as GET: a handler takes the parsed JSON body (payload) and returns
# either a body (sent with 200) or a (status, body) tuple. Body reading + JSON parse
# (and the 400 on invalid JSON) stay in do_POST; there are no streaming POST routes,
# so every POST endpoint lives in this table.

def _pp(payload, key):
    """Stripped string body field, matching the old (payload.get(key) or '').strip()."""
    return (payload.get(key) or "").strip()


def _post_decompose(p):
    product, request = _pp(p, "product"), _pp(p, "request")
    if not product or not request:
        return (400, {"error": "product and request are required"})
    job, started = start_job("decompose", ("decompose", product, request),
                             _forward(run_decompose, product, request))
    return {"job_id": job.id, "started": started}


def _post_quick_task(p):
    product, request = _pp(p, "product"), _pp(p, "request")
    kind = (p.get("kind") or "task").strip()
    if not product or not request:
        return (400, {"error": "product and request are required"})
    return run_quick_task(product, request, kind)


def _post_analyze(p):
    product = _pp(p, "product")
    if not product:
        return (400, {"error": "product is required"})
    return analyze_product(product)


def _post_baseline(p):
    product = _pp(p, "product")
    if not product:
        return (400, {"error": "product is required"})
    return run_baseline(product)


def _post_approve_product(p):
    eid = _pp(p, "epic_id")
    job, started = start_job("approve_product", ("approve_product", eid),
                             _forward(approve_product_spec, eid))
    return {"job_id": job.id, "started": started}


def _post_approve_spec(p):
    eid = _pp(p, "epic_id")
    job, started = start_job("approve_spec", ("approve_spec", eid),
                             _forward(approve_feature_spec, eid))
    return {"job_id": job.id, "started": started}


def _post_epic_build(p):
    eid = _safe_epic_id(_pp(p, "epic_id"))
    if not eid:
        return (400, {"error": "epic_id required"})
    job, started = start_job("epic_build", ("epic_build", eid), build_epic(eid))
    return {"job_id": job.id, "started": started}


def _post_epic_push(p):
    eid = _safe_epic_id(_pp(p, "epic_id"))
    if not eid:
        return (400, {"error": "epic_id required"})
    job, started = start_job("epic_push", ("epic_push", eid), push_epic(eid))
    return {"job_id": job.id, "started": started}


def _post_epic_fix(p):
    eid = _safe_epic_id(_pp(p, "epic_id"))
    if not eid:
        return (400, {"error": "epic_id required"})
    job, started = start_job("epic_fix", ("epic_fix", eid), fix_epic_build(eid))
    return {"job_id": job.id, "started": started}


def _post_epic_validate(p):
    eid = _safe_epic_id(_pp(p, "epic_id"))
    if not eid:
        return (400, {"error": "epic_id required"})
    job, started = start_job("epic_validate", ("epic_validate", eid), validate_epic(eid))
    return {"job_id": job.id, "started": started}


def _post_epic_verify(p):
    eid = _safe_epic_id(_pp(p, "epic_id"))
    if not eid:
        return (400, {"error": "epic_id required"})
    job, started = start_job("epic_verify", ("epic_verify", eid), verify_epic(eid))
    return {"job_id": job.id, "started": started}


def _post_task_accept(p):
    eid = _safe_epic_id(_pp(p, "epic_id"))
    tf = _pp(p, "task_file")
    if not eid or not tf:
        return (400, {"error": "epic_id and task_file required"})
    set_runstate(eid, tf, state="accepted")
    return {"ok": True, "epic_id": eid, "task_file": tf, "state": "accepted"}


def _post_task_run(p):
    eid = _pp(p, "epic_id")
    tf = _pp(p, "task_file")
    if not eid or not tf:
        return (400, {"error": "epic_id and task_file required"})
    job, started = start_job("task_run", ("task_run", eid, tf),
                             run_task_implementation(eid, tf))
    return {"job_id": job.id, "started": started}


POST_ROUTES = {
    "/api/decompose": _post_decompose,
    "/api/quick-task": _post_quick_task,
    "/api/inbox/add": lambda p: inbox_add(_pp(p, "product"), (p.get("type") or "task").strip(), _pp(p, "text")),
    "/api/inbox/delete": lambda p: inbox_delete(_pp(p, "id")),
    "/api/connect-repo": lambda p: connect_repo(p.get("path", ""), p.get("name", ""),
                                                p.get("framework", "other"), bool(p.get("force"))),
    "/api/analyze": _post_analyze,
    "/api/baseline": _post_baseline,
    "/api/approve-product": _post_approve_product,
    "/api/approve-spec": _post_approve_spec,
    "/api/epic/build": _post_epic_build,
    "/api/epic/preview-start": lambda p: preview_start(_pp(p, "epic_id")),
    "/api/epic/preview-stop": lambda p: preview_stop(_pp(p, "epic_id")),
    "/api/epic/preview-mark": lambda p: preview_mark(_pp(p, "epic_id")),
    "/api/epic/push": _post_epic_push,
    "/api/epic/rollback": lambda p: rollback_epic(_pp(p, "epic_id")),
    "/api/epic/fix-build": _post_epic_fix,
    "/api/epic/validate": _post_epic_validate,
    "/api/epic/verify": _post_epic_verify,
    "/api/epic/reset-runs": lambda p: reset_epic_runs(_pp(p, "epic_id")),
    "/api/task/reset": lambda p: reset_task_run(_pp(p, "epic_id"), _pp(p, "task_file")),
    "/api/task/accept": _post_task_accept,
    "/api/task/run": _post_task_run,
    "/api/epic/archive": lambda p: archive_epic(_pp(p, "epic_id")),
    "/api/epic/restore": lambda p: restore_epic(_pp(p, "epic_id")),
    "/api/epic/delete": lambda p: delete_epic(_pp(p, "epic_id")),
    "/api/commit-epic": lambda p: commit_epic(_pp(p, "epic_id"), p.get("message")),
}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # quiet

    def _stream_job(self, job_id):
        job = JOBS.get(job_id)
        if not job:
            return self._send(404, {"error": "job not found"})
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()
        sent = 0
        try:
            while True:
                lines, done, result = job.snapshot(sent)
                for ln in lines:
                    self.wfile.write(("data: " + json.dumps(ln, ensure_ascii=False) + "\n\n").encode("utf-8"))
                sent += len(lines)
                if lines:
                    self.wfile.flush()
                if done:
                    self.wfile.write(("event: done\ndata: " + json.dumps(result or {}, ensure_ascii=False) + "\n\n").encode("utf-8"))
                    self.wfile.flush()
                    return
                time.sleep(0.5)
        except (BrokenPipeError, ConnectionResetError, OSError):
            return

    def _send(self, code, body, ctype="application/json"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False).encode("utf-8")
        elif isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype + ("; charset=utf-8" if "json" in ctype or "text" in ctype or "html" in ctype else ""))
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _static(self, name):
        path = (STATIC_DIR / name).resolve()
        try:
            path.relative_to(STATIC_DIR.resolve())
        except ValueError:
            return self._send(403, {"error": "forbidden"})
        if not path.is_file():
            return self._send(404, {"error": "not found"})
        ctype = "text/html" if name.endswith(".html") else \
                "text/css" if name.endswith(".css") else \
                "application/javascript" if name.endswith(".js") else "text/plain"
        self._send(200, path.read_bytes(), ctype)

    def do_GET(self):
        u = urlparse(self.path)
        path, q = u.path, parse_qs(u.query)
        try:
            # special cases: static files and the SSE stream write the socket directly
            if path in ("/", "/index.html"):
                return self._static("index.html")
            if path.startswith("/static/"):
                return self._static(path[len("/static/"):])
            if path == "/api/job/stream":
                return self._stream_job(q.get("id", [""])[0])

            handler = GET_ROUTES.get(path)
            if handler is None:
                return self._send(404, {"error": "unknown endpoint"})
            result = handler(q)
            if isinstance(result, tuple):
                status, body = result
                return self._send(status, body)
            return self._send(200, result)
        except Exception as exc:
            traceback.print_exc()
            return self._send(500, {"error": str(exc)})

    def do_POST(self):
        u = urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw or b"{}")
        except Exception:
            return self._send(400, {"error": "invalid JSON body"})
        try:
            handler = POST_ROUTES.get(u.path)
            if handler is None:
                return self._send(404, {"error": "unknown endpoint"})
            result = handler(payload)
            if isinstance(result, tuple):
                status, body = result
                return self._send(status, body)
            return self._send(200, result)
        except Exception as exc:
            traceback.print_exc()
            return self._send(500, {"error": str(exc)})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--host", default="127.0.0.1")
    args = ap.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    try:
        _n = _jobs.reconcile_interrupted(BACKLOG_DIR)
        if _n:
            print(f"Recovery         ·  marked {_n} interrupted task(s) from a previous run")
    except Exception as exc:
        print(f"Recovery         ·  reconcile skipped ({exc})")
    print(f"Agentic Console  ·  http://{args.host}:{args.port}")
    print(f"Platform root    ·  {ROOT}")
    print(f"Version          ·  {platform_version()}")
    print("Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
