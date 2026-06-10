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
    security = read_file(run_dir, "security-gate.md").lower()

    if "needs_approval" in security:
        return {
            "decision": "stop",
            "status": "needs_security_approval",
            "reason": "Security gate requires approval.",
        }

    return {
        "decision": "continue",
        "status": "security_ok",
        "reason": "Security gate passed.",
    }


def decide_after_confidence(run_dir):
    confidence = read_file(run_dir, "confidence.md").lower()

    if "## status\n\nfailed" in confidence:
        return {
            "decision": "stop",
            "status": "confidence_failed",
            "reason": "Confidence gate failed.",
        }

    if "## status\n\nneeds_review" in confidence:
        return {
            "decision": "review",
            "status": "needs_review",
            "reason": "Confidence gate requires human review.",
        }

    if "## status\n\npassed" in confidence:
        return {
            "decision": "create_pr",
            "status": "ready_for_pr",
            "reason": "Confidence gate passed.",
        }

    return {
        "decision": "review",
        "status": "confidence_unknown",
        "reason": "Confidence gate result is missing or unknown.",
    }


def write_decision(run_dir, stage, result):
    path = Path(run_dir) / f"decision-{stage}.md"

    path.write_text(f"""# Run Decision

## Stage

{stage}

## Decision

{result["decision"]}

## Status

{result["status"]}

## Reason

{result["reason"]}
""")

    return path
