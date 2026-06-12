import os
from pathib import Path

from orchestrator.acceptance.runner import run_acceptance


def epic_dir_from_source_task():
    source_task = os.environ.get("AGENTIC_SOURCE_TASK_PATH")
    if not source_task:
        return None

    path = Path(source_task)
    if not path.exists():
        return None

    return path.parent


def should_run_acceptance(epic_dir):
    if not epic_dir:
        return False

    epic_dir = Path(epic_dir)
    return (
        (epic_dir / "acceptance-scenarios.md").exists()
        or (epic_dir / "acceptance-command.txt").exists()
        or (epic_dir / "generated-playwright" / "acceptance.spec.ts").exists()
    )


def run_acceptance_gate(product_name, run, graph_v2):
    epic_dir = epic_dir_from_source_task()

    if not should_run_acceptance(epic_dir):
        run.event("Acceptance gate skipped: no source epic or acceptance artifacts")
        return True

    run.status("acceptance_running")
    run.event(f"Acceptance gate started: {epic_dir}")
    graph_v2.start("acceptance")
    graph_v2.write()

    try:
        result = run_acceptance(
            epic_dir=epic_dir,
            product_name=product_name,
        )
    except Exception as err:
        run.status("acceptance_failed")
        run.event(f"Acceptance gate failed with exception: {err}")
        graph_v2.fail("acceptance", error=str(err))
        graph_v2.write()
        return False

    if result.passed:
        run.status("acceptance_passed")
        run.event("Acceptance gate passed")
        graph_v2.complete("acceptance", artifacts=["acceptance-result.md", "acceptance-result.json"])
        graph_v2.write()
        return True

    run.status("acceptance_failed")
    run.event("Acceptance gate failed; recovery bug task should be available in epic")
    graph_v2.fail("acceptance", error="Acceptance failed", artifacts=["acceptance-result.md", "acceptance-result.json"])
    graph_v2.write()
    return False
