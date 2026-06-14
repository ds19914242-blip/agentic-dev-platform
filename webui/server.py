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
import sys
import threading
import traceback
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


def analysis_path(product_name):
    """Path to the Repository Analyst output (step 0) for a product."""
    return MEMORY_DIR / f"{product_name}-analysis.md"


def has_analysis(product_name):
    """True if step 0 has produced a non-empty analysis for this product."""
    p = analysis_path(product_name)
    try:
        return p.is_file() and p.stat().st_size > 0
    except Exception:
        return False


def list_products():
    out = []
    if not PRODUCTS_DIR.exists():
        return out
    for cfg in sorted(PRODUCTS_DIR.glob("*/config.yaml")):
        data = _safe_yaml(cfg)
        name = str(data.get("name") or cfg.parent.name)
        out.append({
            "name": name,
            "framework": data.get("framework", ""),
            "type": data.get("type", ""),
            "status": data.get("status", ""),
            "repo_path": data.get("repo_path", ""),
            "validators": [v.get("name") for v in (data.get("validators") or []) if isinstance(v, dict)],
            "has_analysis": has_analysis(name),
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


def epic_summary(epic_dir):
    epic_md = epic_dir / "epic.md"
    text = epic_md.read_text(errors="ignore") if epic_md.exists() else ""
    outcome = _read_json(epic_dir / "outcome.json") or {}
    files = sorted(p.name for p in epic_dir.iterdir() if p.is_file())
    tasks = sorted(f for f in files if f.startswith("task-") and f.endswith(".md"))
    return {
        "id": epic_dir.name,
        "product": _section(text, "Product") or "",
        "request": _section(text, "Request") or "",
        "status": outcome.get("status", "—"),
        "goal": outcome.get("goal", ""),
        "created_at": outcome.get("created_at", ""),
        "updated_at": outcome.get("updated_at", ""),
        "task_count": len(tasks),
        "artifact_count": len(files),
    }


def list_epics():
    if not BACKLOG_DIR.exists():
        return []
    epics = []
    for d in sorted(BACKLOG_DIR.iterdir(), reverse=True):
        if d.is_dir() and (d / "epic.md").exists():
            try:
                epics.append(epic_summary(d))
            except Exception:
                continue
    return epics


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

    return {
        "summary": summary,
        "stations": stations,
        "artifacts": artifacts,
        "tasks": tasks,
        "outcome": _read_json(epic_dir / "outcome.json"),
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


# --- HTTP layer ---------------------------------------------------------------
class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # quiet

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
                    "products": list_products(),
                    "agents": AGENTS,
                    "pipeline": PIPELINE,
                })
            if path == "/api/analysis":
                product = (q.get("product", [""])[0] or "").strip()
                if not product:
                    return self._send(400, {"error": "product is required"})
                # guard against path traversal in the product name
                if "/" in product or "\\" in product or ".." in product:
                    return self._send(400, {"error": "invalid product name"})
                p = analysis_path(product)
                if not p.is_file():
                    return self._send(404, {"error": "no analysis for product",
                                            "product": product, "has_analysis": False})
                return self._send(200, {
                    "product": product,
                    "has_analysis": True,
                    "path": f"memory/{product}-analysis.md",
                    "content": p.read_text(errors="ignore"),
                })
            if path == "/api/epics":
                return self._send(200, {"epics": list_epics()})
            if path == "/api/epic":
                d = epic_detail(q.get("id", [""])[0])
                return self._send(200, d) if d else self._send(404, {"error": "epic not found"})
            if path == "/api/runs":
                return self._send(200, {"runs": list_runs()})
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
                return self._send(200, run_decompose(product, request))
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
