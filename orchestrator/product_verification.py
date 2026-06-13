from pathlib import Path

from orchestrator.criteria_evidence import build_criteria_evidence, write_criteria_evidence

from orchestrator.outcome_criteria import (
    build_criteria_verification,
    write_criteria_verification,
)
from orchestrator.outcome_store import ACCEPTED, FAILED, set_outcome_status
from orchestrator.product_outcome import (
    _extract_section,
    _read,
    maybe_write_product_outcome_for_task,
)
from orchestrator.product_registry import load_product_config
from orchestrator.route_verification import verify_routes, write_route_verification
from orchestrator.verification_evidence import (
    build_verification_evidence,
    write_verification_evidence,
)


def run_product_verification(task_path, task_text, status, failed, note):
    task_path = Path(task_path)

    outcome_artifacts = maybe_write_product_outcome_for_task(
        task_path=task_path,
        task_text=task_text,
        manual_status=status,
        note=note,
    )

    if not outcome_artifacts:
        return {
            "failed": failed,
            "note": note,
            "product_outcome": None,
            "verification_evidence": None,
            "route_verification": None,
            "criteria_verification": None,
        }

    route_artifacts = None
    route_result = None
    route_failed = False

    try:
        epic_text = _read(task_path.parent / "epic.md")
        product_name = _extract_section(epic_text, "Product")
        product = load_product_config(product_name)
        route_result = verify_routes(task_path.parent, product["repo_path"])
        route_artifacts = write_route_verification(task_path.parent, route_result)
        route_failed = route_result.get("result") == "failed"
    except Exception as exc:
        route_failed = True
        note = f"{note}\nRoute verification error: {exc}"

    evidence = build_verification_evidence(
        task_path=task_path,
        task_text=task_text,
        status="manual_verification_failed" if route_failed else status,
        note=note,
    )
    evidence_artifacts = write_verification_evidence(task_path.parent, evidence)

    criteria_evidence_result = build_criteria_evidence(
        epic_dir=task_path.parent,
        note=note,
        route_result=route_result,
    )
    criteria_evidence_artifacts = write_criteria_evidence(
        task_path.parent,
        criteria_evidence_result,
    )
    criteria_evidence_failed = criteria_evidence_result.get("result") == "failed"

    criteria_result = build_criteria_verification(
        epic_dir=task_path.parent,
        note=note,
        route_result=route_result,
    )
    criteria_artifacts = write_criteria_verification(task_path.parent, criteria_result)
    criteria_failed = criteria_result.get("result") == "failed"

    final_failed = failed or route_failed or criteria_failed or criteria_evidence_failed

    set_outcome_status(
        task_path.parent,
        FAILED if final_failed else ACCEPTED,
        note,
    )

    return {
        "failed": final_failed,
        "note": note,
        "product_outcome": outcome_artifacts,
        "verification_evidence": evidence_artifacts,
        "route_verification": route_artifacts,
        "criteria_verification": criteria_artifacts,
        "criteria_evidence": criteria_evidence_artifacts,
    }
