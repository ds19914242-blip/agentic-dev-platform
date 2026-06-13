import json
import re
from datetime import datetime
from pathlib import Path

from orchestrator.criteria_evidence import build_criteria_evidence, write_criteria_evidence


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


def _read(path):
    path = Path(path)
    return path.read_text(errors="ignore") if path.exists() else ""


def _extract_section(text, heading):
    pattern = rf"## {re.escape(heading)}\n\n(.*?)(?=\n## |\Z)"
    match = re.search(pattern, text, flags=re.DOTALL)
    return match.group(1).strip() if match else ""


def _criteria_items(text):
    items = re.findall(r"^\s*-\s*\[[ xX]\]\s+(.+)", text, flags=re.MULTILINE)
    if items:
        return [item.strip() for item in items]

    return [
        item.strip()
        for item in re.findall(r"^\s*-\s+(.+)", text, flags=re.MULTILINE)
        if item.strip()
    ]


def build_criteria_verification(epic_dir, note, route_result=None):
    epic_dir = Path(epic_dir)

    product_spec = _read(epic_dir / "product-spec.md")
    feature_spec = _read(epic_dir / "feature-spec.md")
    evidence = _read(epic_dir / "verification-evidence.md")
    criteria_evidence = _read(epic_dir / "criteria-evidence.md")

    success_criteria = _criteria_items(
        _extract_section(product_spec, "Success Criteria")
    )
    acceptance_criteria = _criteria_items(
        _extract_section(feature_spec, "Acceptance Criteria")
    )

    checks = {
        "has_success_criteria": len(success_criteria) > 0,
        "has_acceptance_criteria": len(acceptance_criteria) > 0,
        "has_verification_note": bool(note.strip()),
        "has_verification_evidence": bool(evidence.strip()),
        "has_criteria_evidence": bool(criteria_evidence.strip()),
        "route_verification_passed": (
            True if route_result is None else route_result.get("result") == "passed"
        ),
    }

    passed = all(checks.values())

    return {
        "schema": "product_criteria_verification_v1",
        "result": "passed" if passed else "failed",
        "verified_at": now_iso(),
        "checks": checks,
        "success_criteria_count": len(success_criteria),
        "acceptance_criteria_count": len(acceptance_criteria),
        "success_criteria": success_criteria,
        "acceptance_criteria": acceptance_criteria,
        "note": note,
    }


def write_criteria_verification(epic_dir, result):
    epic_dir = Path(epic_dir)

    json_path = epic_dir / "product-criteria-verification.json"
    md_path = epic_dir / "product-criteria-verification.md"

    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))

    lines = [
        "# Product Criteria Verification",
        "",
        "## Result",
        "",
        result["result"],
        "",
        "## Checks",
        "",
    ]

    for name, passed in result["checks"].items():
        lines.append(f"- {'PASS' if passed else 'FAIL'}: {name}")

    lines.extend([
        "",
        "## Success Criteria",
        "",
    ])

    if result["success_criteria"]:
        for item in result["success_criteria"]:
            lines.append(f"- {item}")
    else:
        lines.append("_No success criteria found._")

    lines.extend([
        "",
        "## Acceptance Criteria",
        "",
    ])

    if result["acceptance_criteria"]:
        for item in result["acceptance_criteria"]:
            lines.append(f"- {item}")
    else:
        lines.append("_No acceptance criteria found._")

    lines.extend([
        "",
        "## Note",
        "",
        result.get("note") or "_No note._",
        "",
        "## Verified At",
        "",
        result["verified_at"],
        "",
    ])

    md_path.write_text("\n".join(lines))
    return md_path, json_path
