import json
import re
from datetime import datetime
from pathlib import Path

from orchestrator.outcome_store import attach_evidence


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


def _read(path):
    path = Path(path)
    return path.read_text(errors="ignore") if path.exists() else ""


def _extract_acceptance_checks(task_text):
    match = re.search(
        r"\*\*Required checks:\*\*\n(.*?)(?=\n\*\*Acceptance criteria:\*\*|\Z)",
        task_text,
        flags=re.DOTALL,
    )
    if match:
        return match.group(1).strip()
    return ""


def build_verification_evidence(task_path, task_text, status, note):
    task_path = Path(task_path)
    epic_dir = task_path.parent

    acceptance_scenarios = _read(epic_dir / "acceptance-scenarios.md")
    required_checks = _extract_acceptance_checks(task_text)

    result = "failed" if status == "manual_verification_failed" else "passed"

    return {
        "schema": "verification_evidence_v1",
        "result": result,
        "status": status,
        "verified_at": now_iso(),
        "source_task": str(task_path),
        "note": note,
        "has_acceptance_scenarios": bool(acceptance_scenarios.strip()),
        "acceptance_scenarios": acceptance_scenarios,
        "required_checks": required_checks,
    }


def write_verification_evidence(epic_dir, evidence):
    epic_dir = Path(epic_dir)

    json_path = epic_dir / "verification-evidence.json"
    md_path = epic_dir / "verification-evidence.md"

    json_path.write_text(json.dumps(evidence, indent=2, ensure_ascii=False))

    md = f"""# Verification Evidence

## Result

{evidence["result"]}

## Status

{evidence["status"]}

## Source Task

{evidence["source_task"]}

## Note

{evidence["note"]}

## Required Checks

{evidence.get("required_checks") or "_No required checks captured._"}

## Acceptance Scenarios

{evidence.get("acceptance_scenarios") or "_No acceptance scenarios found._"}

## Verified At

{evidence["verified_at"]}
"""
    md_path.write_text(md)

    attach_evidence(epic_dir, "verification_report", "verification-evidence.md")
    return md_path, json_path
