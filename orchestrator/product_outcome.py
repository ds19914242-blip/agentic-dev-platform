import json
import re
from datetime import datetime
from pathlib import Path


def _read(path):
    path = Path(path)
    return path.read_text(errors="ignore") if path.exists() else ""


def _extract_section(text, heading):
    pattern = rf"## {re.escape(heading)}\n\n(.*?)(?=\n## |\Z)"
    match = re.search(pattern, text, flags=re.DOTALL)
    return match.group(1).strip() if match else ""


def _checkbox_count(text):
    checkbox_count = len(
        re.findall(r"^\s*-\s*\[[ xX]\]\s+", text, flags=re.MULTILINE)
    )

    if checkbox_count:
        return checkbox_count

    return len(
        re.findall(r"^\s*-\s+.+", text, flags=re.MULTILINE)
    )


def _verification_task(text):
    lowered = text.lower()
    return (
        "type: verification_task" in lowered
        or "pipeline: manual_verification" in lowered
        or "end-to-end acceptance verification" in lowered
    )


def _status_from_manual_status(manual_status):
    if manual_status == "manual_verification_passed":
        return "achieved"
    if manual_status == "manual_verification_failed":
        return "not_achieved"
    return "unknown"


def build_product_outcome(epic_dir, source_task_path, manual_status, note):
    epic_dir = Path(epic_dir)

    product_spec = _read(epic_dir / "product-spec.md")
    feature_spec = _read(epic_dir / "feature-spec.md")
    acceptance = _read(epic_dir / "acceptance-scenarios.md")

    product_goal = _extract_section(product_spec, "Product Goal")
    success_criteria = _extract_section(product_spec, "Success Criteria")
    acceptance_scenarios = _extract_section(product_spec, "Acceptance Scenarios")

    outcome_status = _status_from_manual_status(manual_status)

    if outcome_status == "achieved":
        summary = "Product outcome achieved according to manual end-to-end verification."
    elif outcome_status == "not_achieved":
        summary = "Product outcome was not achieved according to manual end-to-end verification."
    else:
        summary = "Product outcome could not be determined."

    evidence = {
        "source_task": str(source_task_path),
        "manual_status": manual_status,
        "manual_note": note,
        "has_product_spec": bool(product_spec.strip()),
        "has_feature_spec": bool(feature_spec.strip()),
        "has_acceptance_scenarios": bool(acceptance.strip()),
        "product_success_criteria_count": _checkbox_count(success_criteria),
        "feature_acceptance_criteria_count": _checkbox_count(
            _extract_section(feature_spec, "Acceptance Criteria")
        ),
    }

    return {
        "schema": "product_outcome_v1",
        "status": outcome_status,
        "summary": summary,
        "verified_at": datetime.now().isoformat(timespec="seconds"),
        "product_goal": product_goal,
        "success_criteria": success_criteria,
        "acceptance_scenarios": acceptance_scenarios,
        "evidence": evidence,
    }


def write_product_outcome(epic_dir, outcome):
    epic_dir = Path(epic_dir)

    json_path = epic_dir / "product-outcome.json"
    md_path = epic_dir / "product-outcome.md"

    json_path.write_text(json.dumps(outcome, indent=2, ensure_ascii=False))

    md = f"""# Product Outcome Verification

## Status

{outcome["status"]}

## Summary

{outcome["summary"]}

## Product Goal

{outcome.get("product_goal") or "_No product goal found._"}

## Success Criteria

{outcome.get("success_criteria") or "_No success criteria found._"}

## Evidence

- Source task: {outcome["evidence"].get("source_task")}
- Manual status: {outcome["evidence"].get("manual_status")}
- Manual note: {outcome["evidence"].get("manual_note")}
- Has product spec: {outcome["evidence"].get("has_product_spec")}
- Has feature spec: {outcome["evidence"].get("has_feature_spec")}
- Has acceptance scenarios: {outcome["evidence"].get("has_acceptance_scenarios")}
- Product success criteria count: {outcome["evidence"].get("product_success_criteria_count")}
- Feature acceptance criteria count: {outcome["evidence"].get("feature_acceptance_criteria_count")}

## Verified At

{outcome["verified_at"]}
"""
    md_path.write_text(md)
    return md_path, json_path


def maybe_write_product_outcome_for_task(task_path, task_text, manual_status, note):
    task_path = Path(task_path)

    if not _verification_task(task_text):
        return None

    epic_dir = task_path.parent

    if not (epic_dir / "product-spec.md").exists():
        return None

    outcome = build_product_outcome(
        epic_dir=epic_dir,
        source_task_path=task_path,
        manual_status=manual_status,
        note=note,
    )
    return write_product_outcome(epic_dir, outcome)
