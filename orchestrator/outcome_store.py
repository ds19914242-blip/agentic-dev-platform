import json
import re
from datetime import datetime
from pathlib import Path


PLANNED = "planned"
IMPLEMENTING = "implementing"
IMPLEMENTED = "implemented"
VERIFICATION_PENDING = "verification_pending"
VERIFIED = "verified"
ACCEPTED = "accepted"
FAILED = "failed"

FINAL_STATUSES = {ACCEPTED, FAILED}


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


def outcome_path(epic_dir):
    return Path(epic_dir) / "outcome.json"


def extract_section(text, heading):
    pattern = rf"## {re.escape(heading)}\n\n(.*?)(?=\n## |\Z)"
    match = re.search(pattern, text, flags=re.DOTALL)
    return match.group(1).strip() if match else ""


def infer_goal(epic_dir):
    epic_dir = Path(epic_dir)

    product_spec = epic_dir / "product-spec.md"
    if product_spec.exists():
        goal = extract_section(product_spec.read_text(errors="ignore"), "Product Goal")
        if goal:
            return goal

    epic_md = epic_dir / "epic.md"
    if epic_md.exists():
        request = extract_section(epic_md.read_text(errors="ignore"), "Request")
        if request:
            return request

    return epic_dir.name


def default_outcome(epic_dir):
    return {
        "schema": "outcome_v1",
        "goal": infer_goal(epic_dir),
        "status": PLANNED,
        "verification_required": True,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "verified_at": None,
        "accepted_at": None,
        "failed_at": None,
        "note": "",
        "evidence": {},
    }


def load_outcome(epic_dir):
    path = outcome_path(epic_dir)
    if not path.exists():
        return default_outcome(epic_dir)

    try:
        data = json.loads(path.read_text())
    except Exception:
        data = default_outcome(epic_dir)

    data.setdefault("schema", "outcome_v1")
    data.setdefault("goal", infer_goal(epic_dir))
    data.setdefault("status", PLANNED)
    data.setdefault("verification_required", True)
    data.setdefault("created_at", now_iso())
    data.setdefault("updated_at", now_iso())
    data.setdefault("verified_at", None)
    data.setdefault("accepted_at", None)
    data.setdefault("failed_at", None)
    data.setdefault("note", "")
    data.setdefault("evidence", {})
    return data


def save_outcome(epic_dir, outcome):
    outcome["updated_at"] = now_iso()
    path = outcome_path(epic_dir)
    path.write_text(json.dumps(outcome, indent=2, ensure_ascii=False))
    return path


def ensure_outcome(epic_dir):
    outcome = load_outcome(epic_dir)
    return save_outcome(epic_dir, outcome)


def set_outcome_status(epic_dir, status, note=""):
    outcome = load_outcome(epic_dir)
    outcome["status"] = status
    outcome["note"] = note or outcome.get("note", "")

    if status == VERIFIED:
        outcome["verified_at"] = now_iso()
    elif status == ACCEPTED:
        outcome["verified_at"] = outcome.get("verified_at") or now_iso()
        outcome["accepted_at"] = now_iso()
    elif status == FAILED:
        outcome["failed_at"] = now_iso()

    save_outcome(epic_dir, outcome)
    return outcome


def infer_epic_state(epic_dir, tasks_total, tasks_completed):
    outcome = load_outcome(epic_dir)
    status = outcome.get("status", PLANNED)

    if status in FINAL_STATUSES:
        return status

    if tasks_total and tasks_completed >= tasks_total:
        if status in {PLANNED, IMPLEMENTING}:
            return IMPLEMENTED
        return status

    if tasks_completed > 0 and status == PLANNED:
        return IMPLEMENTING

    return status


def attach_evidence(epic_dir, evidence_type, file_name):
    outcome = load_outcome(epic_dir)
    evidence = outcome.setdefault("evidence", {})
    evidence[evidence_type] = file_name
    save_outcome(epic_dir, outcome)
    return outcome
