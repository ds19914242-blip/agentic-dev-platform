import json
from pathlib import Path


ALREADY_SATISFIED_MARKERS = [
    "already implemented",
    "already exists",
    "no new structural work is required",
    "feature appears to be already implemented",
]

CLARIFICATION_MARKERS = [
    "need clarification",
    "needs clarification",
    "confirm with the requester",
    "several interpretations",
    "ambiguous",
]


def read_file(run_dir, name):
    path = Path(run_dir) / name
    if not path.exists():
        return ""
    return path.read_text(errors="ignore")


def read_security_json(run_dir):
    path = Path(run_dir) / "security-gate.json"

    if not path.exists():
        return {}

    return json.loads(path.read_text())


def read_confidence_json(run_dir):
    path = Path(run_dir) / "confidence.json"

    if not path.exists():
        return {}

    return json.loads(path.read_text())


def decide_after_planning(run_dir):
    plan = read_file(run_dir, "plan.md").lower()

    if any(marker in plan for marker in ALREADY_SATISFIED_MARKERS):
        return {
            "decision": "stop",
            "status": "already_satisfied",
            "reason": "Planner detected that the requested feature already exists.",
        }

    if any(marker in plan for marker in CLARIFICATION_MARKERS):
        return {
            "decision": "stop",
            "status": "needs_clarification",
            "reason": "Planner detected ambiguity or requested confirmation.",
        }

    return {
        "decision": "continue",
        "status": "planning_ok",
        "reason": "Planning completed and implementation may continue.",
    }


def decide_after_security(run_dir):
    security = read_security_json(run_dir)
    status = security.get("status", "unknown")

    if status in {"blocked", "needs_approval"}:
        return {
            "decision": "stop",
            "status": "needs_security_approval" if status == "needs_approval" else "security_blocked",
            "reason": security.get("reason", "Security gate did not pass."),
        }

    if status == "passed_with_warning":
        return {
            "decision": "continue",
            "status": "security_warning",
            "reason": security.get("reason", "Security gate passed with warning."),
        }

    if status == "passed":
        return {
            "decision": "continue",
            "status": "security_ok",
            "reason": "Security gate passed.",
        }

    return {
        "decision": "review",
        "status": "security_unknown",
        "reason": "Security gate result is missing or unknown.",
    }


def decide_after_confidence(run_dir):
    confidence = read_confidence_json(run_dir)
    status = confidence.get("status", "unknown")

    if status == "failed":
        return {
            "decision": "stop",
            "status": "confidence_failed",
            "reason": confidence.get("reason", "Confidence gate failed."),
        }

    if status == "needs_review":
        return {
            "decision": "review",
            "status": "needs_review",
            "reason": confidence.get("reason", "Confidence gate requires human review."),
        }

    if status == "passed":
        return {
            "decision": "create_pr",
            "status": "ready_for_pr",
            "reason": confidence.get("reason", "Confidence gate passed."),
        }

    return {
        "decision": "review",
        "status": "confidence_unknown",
        "reason": "Confidence gate result is missing or unknown.",
    }


def write_decision(run_dir, stage, result):
    json_path = Path(run_dir) / f"decision-{stage}.json"
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))

    md_path = Path(run_dir) / f"decision-{stage}.md"
    md_path.write_text(f"""# Run Decision

## Stage

{stage}

## Decision

{result["decision"]}

## Status

{result["status"]}

## Reason

{result["reason"]}
""")

    return md_path
