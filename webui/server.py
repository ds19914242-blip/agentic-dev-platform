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

STATIC_DIR = Path(__file__).resolve().parent / "static"
BACKLOG_DIR = ROOT / "backlog"
RUNS_DIR = ROOT / "runs"
PRODUCTS_DIR = ROOT / "products"
MEMORY_DIR = ROOT / "memory"

# Bumped whenever the API surface changes, so the frontend can detect a
# stale server (we hit "new frontend / old backend" desyncs before).
API_VERSION = "workspace-11"

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
    import re
    m = re.search(rf"##\s*{re.escape(heading)}\s*\n+(.*?)(?=\n##\s|\Z)", text, re.DOTALL)
    return m.group(1).strip() if m else ""


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
    epic_id = (epic_id or "").strip()
    if not epic_id or "/" in epic_id or "\\" in epic_id or ".." in epic_id:
        return None
    return epic_id


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
    text = path.read_text(errors="ignore")
    fields, deps, title, in_deps = {}, [], path.name, False
    for line in text.splitlines():
        ls = line.strip()
        if ls.startswith("### ") and title == path.name:
            title = ls.lstrip("# ").strip()
        if ":" in line and not line.startswith("#") and not line.startswith("**"):
            k, _, v = line.partition(":")
            k = k.strip().lower()
            if k in {"status", "type", "pipeline", "risk", "pr", "run"}:
                fields.setdefault(k, v.strip())
        if ls.lower().startswith("## depends"):
            in_deps = True
            continue
        if in_deps:
            if ls.startswith("## "):
                in_deps = False
            elif ls and ls != "_None_" and not ls.startswith("_"):
                deps.append(ls.lstrip("- ").strip())
    return {"file": path.name, "title": title, "status": fields.get("status", ""),
            "pr": fields.get("pr", ""), "run": fields.get("run", ""), "depends_on": deps}


def _task_num(name):
    m = re.search(r"task-(\d+)", name or "")
    return int(m.group(1)) if m else None


def _runstate_path(epic_id):
    return BACKLOG_DIR / epic_id / ".console_runs.json"


def load_runstate(epic_id):
    p = _runstate_path(epic_id)
    if p.exists():
        try:
            return json.loads(p.read_text())
        except Exception:
            return {}
    return {}


def set_runstate(epic_id, task_file, **fields):
    d = load_runstate(epic_id)
    cur = d.get(task_file, {})
    cur.update(fields)
    cur["ts"] = datetime.now().strftime("%H:%M:%S")
    d[task_file] = cur
    try:
        _runstate_path(epic_id).write_text(json.dumps(d, ensure_ascii=False, indent=2))
    except Exception:
        pass
    return cur


def _dep_num(s):
    m = re.search(r"task-(\d+)", s or "")
    if m:
        return int(m.group(1))
    m = re.search(r"(\d+)", s or "")
    return int(m.group(1)) if m else None


def epic_dep_nums(epic_id, files):
    """Return {task_num: set(dep_task_nums)} from dag.json (preferred) or the
    platform's Depends-On parser. Always excludes a task from its own blockers."""
    ed = BACKLOG_DIR / epic_id
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
        tn = _dep_num(tid)
        if tn is None:
            continue
        s = set()
        for d in dlist:
            dn = _dep_num(d)
            if dn is not None and dn != tn:
                s.add(dn)
        deps[tn] = s
    return deps


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


# --- task execution: implement one task in an isolated git worktree -----------
# Safety: each task gets its own worktree + agentic/ branch from the base; the
# agent writes only there; changes are committed on that branch; NO push / PR /
# merge, and the product's main working tree is never touched. Worktrees isolate
# concurrent runs, so several Ready tasks can run in parallel without colliding.
def _git_run(repo, args, timeout=1200):
    import subprocess
    try:
        return subprocess.run(["git", "-C", str(repo)] + args, capture_output=True, text=True, timeout=timeout)
    except Exception as exc:
        class R:
            returncode = 1
            stdout = ""
            stderr = str(exc)
        return R()


def run_task_implementation(epic_id, task_file):
    def target(job):
        eid = _safe_epic_id(epic_id)
        if not eid or "/" in (task_file or "") or ".." in (task_file or ""):
            return {"ok": False, "error": "invalid task reference"}
        task_path = BACKLOG_DIR / eid / task_file
        if not task_path.is_file():
            return {"ok": False, "error": "task not found"}
        product = _epic_product(BACKLOG_DIR / eid) or ""
        try:
            from orchestrator.product_registry import load_product_config
            cfg = load_product_config(product)
        except Exception as exc:
            return {"ok": False, "error": f"product config: {exc}"}
        repo = cfg.get("repo_path", "")
        if not repo or not Path(repo).exists():
            set_runstate(eid, task_file, state="failed", error="repo path not found on this machine")
            return {"ok": False, "error": "repo path not found on this machine"}

        set_runstate(eid, task_file, state="running", branch=None, changed=[], error=None)
        base = (_git_run(repo, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout or "").strip() or "HEAD"
        stem = task_path.stem
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        branch = f"agentic/{stem}-{ts}"
        wt_root = Path(repo).parent / ".agentic-worktrees"
        wt = wt_root / f"{stem}-{ts}"
        job.emit(f"Creating isolated worktree on {branch} from {base} (main stays clean)")
        r = _git_run(repo, ["worktree", "add", "-b", branch, str(wt), base])
        if r.returncode != 0:
            set_runstate(eid, task_file, state="failed", error=(r.stderr or "").strip())
            return {"ok": False, "error": "git worktree failed: " + (r.stderr or "").strip()}

        try:
            job.emit("Running implementation agent (Architect → lanes → Implementation → Validation → Review)…")
            try:
                from orchestrator.agent_runtime.orchestrator import run_runtime_orchestrator
                task = task_path.read_text(errors="ignore")
                out_dir = f"runs/webui-task-{stem}-{datetime.now().strftime('%H%M%S')}"
                run_runtime_orchestrator(
                    task=task, product=product, repo_path=str(wt), output_dir=out_dir,
                    dry_run=False,
                    inputs={"task_path": str(task_path), "epic_dir": str(task_path.parent),
                            "execute_writes": True})
                job.emit("Implementation agent finished", "ok")
            except FileNotFoundError:
                set_runstate(eid, task_file, state="failed", error="claude CLI not found")
                return {"ok": False, "error": "claude CLI not found — no code written", "branch": branch}
            except Exception as exc:
                set_runstate(eid, task_file, state="failed", error=str(exc), branch=branch)
                return {"ok": False, "error": str(exc), "branch": branch}

            # commit whatever the agent wrote, so the branch durably holds the diff
            _git_run(wt, ["add", "-A"])
            commit = _git_run(wt, ["commit", "-m", f"agentic: {stem}"])
            ns = _git_run(repo, ["diff", "--name-only", f"{base}..{branch}"])
            changed = [l for l in ns.stdout.splitlines() if l.strip()]
            if changed:
                set_runstate(eid, task_file, state="implemented", branch=branch, base=base, changed=changed)
                job.emit(f"{len(changed)} file(s) committed on {branch}.", "ok")
                job.emit("No push / PR / merge — open the task to review the diff.", "ok")
                return {"ok": True, "branch": branch, "base": base, "changed": changed, "state": "implemented"}
            else:
                set_runstate(eid, task_file, state="no_changes", branch=branch, base=base, changed=[])
                job.emit("Agent produced NO file changes for this task.", "skip")
                return {"ok": True, "branch": branch, "base": base, "changed": [], "state": "no_changes"}
        finally:
            _git_run(repo, ["worktree", "remove", "--force", str(wt)])
    return target


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
    branch, base = run.get("branch"), run.get("base")
    if not branch or not base:
        return {"error": "no run diff available"}
    product = _epic_product(BACKLOG_DIR / eid) or ""
    try:
        from orchestrator.product_registry import load_product_config
        repo = load_product_config(product).get("repo_path", "")
    except Exception as exc:
        return {"error": str(exc)}
    if not repo or not Path(repo).exists():
        return {"error": "repo path not found on this machine"}
    args = ["diff", f"{base}..{branch}"]
    if path:
        args += ["--", path]
    r = _git_run(repo, args)
    return {"diff": r.stdout, "branch": branch, "base": base}


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
    return {
        "epics_total": len(epics), "epics_by_status": estatus,
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
            tasks.append({"file": name, "title": title, **fields})

    def _txt(name):
        p = epic_dir / name
        return p.read_text(errors="ignore").strip() if p.exists() else ""

    have = set(files)
    has_task = any(f.startswith("task-") and f.endswith(".md") for f in have)
    if "product-spec.md" not in have:
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
    import subprocess
    try:
        r = subprocess.run(["git", "-C", str(repo)] + args,
                            capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except Exception as exc:
        return 1, "", str(exc)


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
JOBS = {}
INFLIGHT = {}
JOBS_LOCK = threading.Lock()


class Job:
    def __init__(self, kind, key):
        self.id = uuid.uuid4().hex[:12]
        self.kind = kind
        self.key = key
        self.log = []
        self.done = False
        self.result = None
        self._lock = threading.Lock()

    def emit(self, msg, level=""):
        with self._lock:
            self.log.append({"ts": datetime.now().strftime("%H:%M:%S"), "msg": msg, "level": level})

    def snapshot(self, frm):
        with self._lock:
            return self.log[frm:], self.done, self.result


def start_job(kind, key, target):
    """Start target(job) in a thread. Returns (job, started_new)."""
    with JOBS_LOCK:
        existing = INFLIGHT.get(key)
        if existing and existing in JOBS and not JOBS[existing].done:
            return JOBS[existing], False
        job = Job(kind, key)
        JOBS[job.id] = job
        INFLIGHT[key] = job.id

    def run():
        stop = threading.Event()

        def heartbeat():
            t0 = time.time()
            while not stop.wait(3):
                job.emit(f"…still working ({int(time.time() - t0)}s)")

        hb = threading.Thread(target=heartbeat, daemon=True)
        job.emit(f"{kind}: dispatched")
        hb.start()
        try:
            job.result = target(job) or {"ok": True}
        except Exception as exc:
            job.emit(f"error: {exc}", "err")
            job.result = {"ok": False, "error": str(exc)}
        finally:
            stop.set()
            with JOBS_LOCK:
                if INFLIGHT.get(key) == job.id:
                    del INFLIGHT[key]
            job.emit("done", "ok")
            job.done = True

    threading.Thread(target=run, daemon=True).start()
    return job, True


def _forward(fn, *args):
    """Wrap a synchronous webui action so its returned log streams to the job."""
    def target(job):
        r = fn(*args) or {}
        for l in r.get("log", []):
            job.emit(l.get("msg", ""), l.get("level", ""))
        return {k: v for k, v in r.items() if k != "log"}
    return target


# --- HTTP layer ---------------------------------------------------------------
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
            if path in ("/", "/index.html"):
                return self._static("index.html")
            if path.startswith("/static/"):
                return self._static(path[len("/static/"):])

            if path == "/api/state":
                return self._send(200, {
                    "version": platform_version(),
                    "api_version": API_VERSION,
                    "products": list_products(),
                    "agents": AGENTS,
                    "pipeline": PIPELINE,
                })
            if path == "/api/epics":
                return self._send(200, {"epics": list_epics(q.get("product", [""])[0])})
            if path == "/api/epics/archived":
                return self._send(200, {"epics": list_archived_epics(q.get("product", [""])[0])})
            if path == "/api/overview":
                return self._send(200, product_overview(q.get("product", [""])[0]))
            if path == "/api/backlog":
                return self._send(200, product_backlog(q.get("product", [""])[0]))
            if path == "/api/task":
                return self._send(200, task_detail(q.get("epic_id", [""])[0], q.get("task_file", [""])[0]))
            if path == "/api/task/diff":
                return self._send(200, task_diff(q.get("epic_id", [""])[0], q.get("task_file", [""])[0], q.get("path", [""])[0]))
            if path == "/api/jobs/active":
                with JOBS_LOCK:
                    active = [{"job_id": j.id, "kind": j.kind, "key": list(j.key)}
                              for j in JOBS.values() if not j.done and j.kind == "task_run"]
                return self._send(200, {"active": active})
            if path == "/api/epic":
                d = epic_detail(q.get("id", [""])[0])
                return self._send(200, d) if d else self._send(404, {"error": "epic not found"})
            if path == "/api/runs":
                return self._send(200, {"runs": list_runs()})
            if path == "/api/version":
                return self._send(200, {"api_version": API_VERSION})
            if path == "/api/job":
                job = JOBS.get(q.get("id", [""])[0])
                if not job:
                    return self._send(404, {"error": "job not found"})
                lines, done, result = job.snapshot(0)
                return self._send(200, {"id": job.id, "log": lines, "done": done, "result": result})
            if path == "/api/job/stream":
                return self._stream_job(q.get("id", [""])[0])
            if path == "/api/repo/tree":
                return self._send(200, repo_tree(q.get("product", [""])[0], q.get("path", [""])[0]))
            if path == "/api/repo/file":
                return self._send(200, repo_file(q.get("product", [""])[0], q.get("path", [""])[0]))
            if path == "/api/repo/structure":
                return self._send(200, repo_structure(q.get("product", [""])[0]))
            if path == "/api/repo/operational":
                return self._send(200, product_operational(q.get("product", [""])[0]))
            if path == "/api/repo/history":
                return self._send(200, repo_history(q.get("product", [""])[0]))
            if path == "/api/repo/baseline":
                return self._send(200, read_baseline(q.get("product", [""])[0]))
            if path == "/api/repo/changes":
                return self._send(200, repo_changes(q.get("product", [""])[0]))
            if path == "/api/repo/diff":
                return self._send(200, repo_diff(q.get("product", [""])[0], q.get("path", [""])[0]))
            if path == "/api/git":
                return self._send(200, git_status())
            if path == "/api/analysis":
                return self._send(200, get_analysis(q.get("product", [""])[0]))
            if path == "/api/file":
                rel = q.get("path", [""])[0]
                target = resolve_artifact(rel)
                if not target:
                    return self._send(404, {"error": "file not found or not allowed"})
                return self._send(200, {"path": rel, "content": target.read_text(errors="ignore")})

            return self._send(404, {"error": "unknown endpoint"})
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
            if u.path == "/api/decompose":
                product = (payload.get("product") or "").strip()
                request = (payload.get("request") or "").strip()
                if not product or not request:
                    return self._send(400, {"error": "product and request are required"})
                job, started = start_job("decompose", ("decompose", product, request),
                                         _forward(run_decompose, product, request))
                return self._send(200, {"job_id": job.id, "started": started})
            if u.path == "/api/connect-repo":
                return self._send(200, connect_repo(
                    payload.get("path", ""), payload.get("name", ""),
                    payload.get("framework", "other"), bool(payload.get("force"))))
            if u.path == "/api/analyze":
                product = (payload.get("product") or "").strip()
                if not product:
                    return self._send(400, {"error": "product is required"})
                return self._send(200, analyze_product(product))
            if u.path == "/api/baseline":
                product = (payload.get("product") or "").strip()
                if not product:
                    return self._send(400, {"error": "product is required"})
                return self._send(200, run_baseline(product))
            if u.path == "/api/approve-product":
                eid = (payload.get("epic_id") or "").strip()
                job, started = start_job("approve_product", ("approve_product", eid),
                                         _forward(approve_product_spec, eid))
                return self._send(200, {"job_id": job.id, "started": started})
            if u.path == "/api/approve-spec":
                eid = (payload.get("epic_id") or "").strip()
                job, started = start_job("approve_spec", ("approve_spec", eid),
                                         _forward(approve_feature_spec, eid))
                return self._send(200, {"job_id": job.id, "started": started})
            if u.path == "/api/task/accept":
                eid = _safe_epic_id((payload.get("epic_id") or "").strip())
                tf = (payload.get("task_file") or "").strip()
                if not eid or not tf:
                    return self._send(400, {"error": "epic_id and task_file required"})
                set_runstate(eid, tf, state="accepted")
                return self._send(200, {"ok": True, "epic_id": eid, "task_file": tf, "state": "accepted"})
            if u.path == "/api/task/run":
                eid = (payload.get("epic_id") or "").strip()
                tf = (payload.get("task_file") or "").strip()
                if not eid or not tf:
                    return self._send(400, {"error": "epic_id and task_file required"})
                job, started = start_job("task_run", ("task_run", eid, tf),
                                         run_task_implementation(eid, tf))
                return self._send(200, {"job_id": job.id, "started": started})
            if u.path == "/api/epic/archive":
                return self._send(200, archive_epic((payload.get("epic_id") or "").strip()))
            if u.path == "/api/epic/restore":
                return self._send(200, restore_epic((payload.get("epic_id") or "").strip()))
            if u.path == "/api/epic/delete":
                return self._send(200, delete_epic((payload.get("epic_id") or "").strip()))
            if u.path == "/api/commit-epic":
                return self._send(200, commit_epic((payload.get("epic_id") or "").strip(),
                                                   payload.get("message")))
            return self._send(404, {"error": "unknown endpoint"})
        except Exception as exc:
            traceback.print_exc()
            return self._send(500, {"error": str(exc)})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--host", default="127.0.0.1")
    args = ap.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
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
