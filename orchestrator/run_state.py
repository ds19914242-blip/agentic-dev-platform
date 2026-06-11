import json
from datetime import datetime
from pathlib import Path


STAGE_PENDING = "pending"
STAGE_RUNNING = "running"
STAGE_COMPLETED = "completed"
STAGE_FAILED = "failed"
STAGE_SKIPPED = "skipped"


DEFAULT_STAGES = [
    "classification",
    "planning",
    "architecture_review",
    "qa_plan",
    "implementation",
    "test_generation",
    "validation",
    "security_gate",
    "confidence_gate",
    "review",
    "pr",
]


def now_iso():
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def create_run_id(prefix="run"):
    return f"{prefix}-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"


def default_stage_state():
    return {
        "status": STAGE_PENDING,
        "started_at": None,
        "completed_at": None,
        "attempt": 0,
        "artifacts": [],
        "error": None,
    }


def create_run_state(
    run_id,
    product,
    request,
    run_type="feature",
    backlog_task=None,
):
    return {
        "schema_version": "0.5",
        "run_id": run_id,
        "product": product,
        "request": request,
        "run_type": run_type,
        "backlog_task": backlog_task,
        "status": STAGE_RUNNING,
        "current_stage": None,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "completed_at": None,
        "stages": {
            stage: default_stage_state()
            for stage in DEFAULT_STAGES
        },
        "artifacts": {},
        "metadata": {},
    }


def load_run_state(run_dir):
    path = Path(run_dir) / "run.json"

    if not path.exists():
        raise FileNotFoundError(f"run.json not found: {path}")

    return json.loads(path.read_text())


def save_run_state(run_dir, state):
    path = Path(run_dir)
    path.mkdir(parents=True, exist_ok=True)

    state["updated_at"] = now_iso()

    run_json = path / "run.json"
    run_json.write_text(json.dumps(state, indent=2, ensure_ascii=False))

    return run_json


def start_stage(run_dir, stage):
    state = load_run_state(run_dir)

    stage_state = state["stages"].setdefault(stage, default_stage_state())
    stage_state["status"] = STAGE_RUNNING
    stage_state["started_at"] = stage_state["started_at"] or now_iso()
    stage_state["completed_at"] = None
    stage_state["attempt"] = int(stage_state.get("attempt", 0)) + 1
    stage_state["error"] = None

    state["current_stage"] = stage
    state["status"] = STAGE_RUNNING

    save_run_state(run_dir, state)
    return state


def complete_stage(run_dir, stage, artifacts=None):
    state = load_run_state(run_dir)

    stage_state = state["stages"].setdefault(stage, default_stage_state())
    stage_state["status"] = STAGE_COMPLETED
    stage_state["completed_at"] = now_iso()
    stage_state["error"] = None

    if artifacts:
        for artifact in artifacts:
            if artifact not in stage_state["artifacts"]:
                stage_state["artifacts"].append(artifact)

    state["current_stage"] = stage

    save_run_state(run_dir, state)
    return state


def fail_stage(run_dir, stage, error=None, artifacts=None):
    state = load_run_state(run_dir)

    stage_state = state["stages"].setdefault(stage, default_stage_state())
    stage_state["status"] = STAGE_FAILED
    stage_state["completed_at"] = now_iso()
    stage_state["error"] = str(error) if error else None

    if artifacts:
        for artifact in artifacts:
            if artifact not in stage_state["artifacts"]:
                stage_state["artifacts"].append(artifact)

    state["current_stage"] = stage
    state["status"] = STAGE_FAILED

    save_run_state(run_dir, state)
    return state


def attach_artifact(run_dir, name, path, kind="file"):
    state = load_run_state(run_dir)

    state["artifacts"][name] = {
        "kind": kind,
        "path": str(path),
        "attached_at": now_iso(),
    }

    save_run_state(run_dir, state)
    return state


def complete_run(run_dir):
    state = load_run_state(run_dir)
    state["status"] = STAGE_COMPLETED
    state["completed_at"] = now_iso()
    save_run_state(run_dir, state)
    return state


def fail_run(run_dir, error=None):
    state = load_run_state(run_dir)
    state["status"] = STAGE_FAILED
    state["completed_at"] = now_iso()
    state["metadata"]["error"] = str(error) if error else None
    save_run_state(run_dir, state)
    return state
