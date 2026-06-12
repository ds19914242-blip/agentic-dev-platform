from pathlib import Path


SECTIONS = {
    "CLI entrypoints": [
        "agentic.py",
        "run_backlog_task.py",
        "run_fast_task.py",
        "run_standard_task.py",
        "run_autonomous_feature.py",
        "mark_manual_verified.py",
    ],
    "Workflow layer": [
        "orchestrator/workflows/autonomous_workflow.py",
    ],
    "Backlog state layer": [
        "orchestrator/task_status.py",
        "orchestrator/task_model.py",
        "orchestrator/backlog_store.py",
        "orchestrator/backlog_query.py",
        "orchestrator/backlog_dag.py",
    ],
    "Service layer": [
        "orchestrator/services/task_execution_service.py",
        "orchestrator/services/pipeline_runner.py",
        "orchestrator/services/verification_service.py",
        "orchestrator/services/autonomous_preflight_service.py",
        "orchestrator/services/autonomous_run_service.py",
        "orchestrator/services/autonomous_planning_service.py",
        "orchestrator/services/autonomous_claude_planning_service.py",
        "orchestrator/services/autonomous_implementation_service.py",
        "orchestrator/services/autonomous_validation_service.py",
        "orchestrator/services/autonomous_review_service.py",
        "orchestrator/services/autonomous_finalize_service.py",
        "orchestrator/services/autonomous_artifacts_service.py",
    ],
}


def count_lines(path):
    p = Path(path)
    if not p.exists():
        return 0
    return len(p.read_text(errors="ignore").splitlines())


def main():
    print("# Architecture Report")
    print()

    total = 0

    for section, files in SECTIONS.items():
        print(f"## {section}")
        print()
        for file_name in files:
            lines = count_lines(file_name)
            total += lines
            status = "present" if Path(file_name).exists() else "missing"
            print(f"- {file_name}: {status}, {lines} lines")
        print()

    print(f"Total tracked architecture lines: {total}")


if __name__ == "__main__":
    main()
