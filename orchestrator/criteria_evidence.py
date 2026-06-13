import json
import re
from datetime import datetime
from pathlib import Path

from orchestrator.criteria_classifier import classify_criterion, evidence_sources_for_type
from orchestrator.evidence_evaluator import evaluate_criterion_evidence


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


def _read(path):
    path = Path(path)
    return path.read_text(errors="ignore") if path.exists() else ""


def _extract_section(text, heading):
    pattern = rf"## {re.escape(heading)}\n\n(.*?)(?=\n## |\Z)"
    match = re.search(pattern, text, flags=re.DOTALL)
    return match.group(1).strip() if match else ""


def criteria_items(text):
    items = re.findall(r"^\s*-\s*\[[ xX]\]\s+(.+)", text, flags=re.MULTILINE)
    if items:
        return [item.strip() for item in items]

    return [
        item.strip()
        for item in re.findall(r"^\s*-\s+(.+)", text, flags=re.MULTILINE)
        if item.strip()
    ]


def load_criteria(epic_dir):
    epic_dir = Path(epic_dir)
    product_spec = _read(epic_dir / "product-spec.md")
    feature_spec = _read(epic_dir / "feature-spec.md")

    success = criteria_items(_extract_section(product_spec, "Success Criteria"))
    acceptance = criteria_items(_extract_section(feature_spec, "Acceptance Criteria"))

    criteria = []

    for index, item in enumerate(success, start=1):
        criteria.append({
            "id": f"success-{index:03d}",
            "type": "success",
            "verification_type": classify_criterion(item),
            "description": item,
        })

    for index, item in enumerate(acceptance, start=1):
        criteria.append({
            "id": f"acceptance-{index:03d}",
            "type": "acceptance",
            "verification_type": classify_criterion(item),
            "description": item,
        })

    return criteria


def build_criteria_evidence(epic_dir, note, route_result=None):
    epic_dir = Path(epic_dir)

    criteria = load_criteria(epic_dir)
    verification_evidence_exists = (epic_dir / "verification-evidence.md").exists()
    route_passed = True if route_result is None else route_result.get("result") == "passed"

    items = []

    for criterion in criteria:
        verification_type = criterion.get("verification_type", "manual")
        expected_sources = evidence_sources_for_type(verification_type)
        evaluation = evaluate_criterion_evidence(
            epic_dir=epic_dir,
            verification_type=verification_type,
            note=note,
        )

        passed = evaluation["passed"]

        items.append({
            **criterion,
            "result": "passed" if passed else "failed",
            "expected_evidence": expected_sources,
            "evidence": evaluation.get("evidence", []),
            "reason": evaluation.get("reason", ""),
            "note": note,
        })

    result = "passed" if criteria and all(item["result"] == "passed" for item in items) else "failed"

    return {
        "schema": "criteria_evidence_v1",
        "result": result,
        "verified_at": now_iso(),
        "criteria_count": len(criteria),
        "criteria": items,
    }


def write_criteria_evidence(epic_dir, result):
    epic_dir = Path(epic_dir)

    json_path = epic_dir / "criteria-evidence.json"
    md_path = epic_dir / "criteria-evidence.md"

    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))

    lines = [
        "# Criteria Evidence",
        "",
        "## Result",
        "",
        result["result"],
        "",
        "## Criteria",
        "",
    ]

    if not result["criteria"]:
        lines.append("_No criteria found._")
    else:
        for item in result["criteria"]:
            lines.append(f"### {item['id']} — {item['result']}")
            lines.append("")
            lines.append(item["description"])
            lines.append("")
            lines.append("Evidence:")
            for ref in item["evidence"]:
                lines.append(f"- {ref}")
            if not item["evidence"]:
                lines.append("- _No evidence_")
            lines.append("")
            lines.append(f"Reason: {item.get('reason') or '_No reason_'}")
            lines.append("")

    lines.extend(["## Verified At", "", result["verified_at"], ""])

    md_path.write_text("\n".join(lines))
    return md_path, json_path
