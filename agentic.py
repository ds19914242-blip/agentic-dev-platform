import subprocess
import sys


COMMANDS = {
    "feature": {
        "script": "run_autonomous_feature.py",
        "description": "Run one autonomous feature",
        "legacy": False,
    },
    "decompose": {
        "script": "decompose_feature.py",
        "description": "Decompose a large request into backlog tasks",
        "legacy": False,
    },
    "backlog": {
        "script": "run_backlog_task.py",
        "description": "Run a backlog task",
        "legacy": False,
    },
    "status": {
        "script": "backlog_status.py",
        "description": "Show backlog status",
        "legacy": False,
    },
    "sync": {
        "script": "sync_backlog_prs.py",
        "description": "Sync backlog PR statuses",
        "legacy": False,
    },
    "dag": {
        "script": "backlog_dag.py",
        "description": "Show dependency-aware backlog DAG",
        "legacy": False,
    },
    "ready": {
        "script": "backlog_ready.py",
        "description": "Show ready backlog tasks",
        "legacy": False,
    },
    "schedule": {
        "script": "backlog_scheduler.py",
        "description": "Run next dependency-ready backlog task",
        "legacy": False,
    },
    "parallel": {
        "script": "backlog_parallel_worktree.py",
        "description": "Run ready backlog tasks in parallel",
        "legacy": False,
    },
    "memory": {
        "script": "memory_report.py",
        "description": "Show product memory report",
        "legacy": False,
    },
    "classify": {
        "script": "classify_task.py",
        "description": "Classify a task and show selected pipeline",
        "legacy": False,
    },
    "metrics": {
        "script": "agentic_metrics.py",
        "description": "Show runtime metrics",
        "legacy": False,
    },
    "approve-spec": {
        "script": "approve_feature_spec.py",
        "description": "Approve feature spec and generate backlog tasks",
        "legacy": False,
    },
    "verify": {
        "script": "mark_manual_verified.py",
        "description": "Mark manual verification passed/failed",
        "legacy": False,
    },

    # Legacy latest-run workflow commands.
    "validate": {
        "script": "validate_latest_run.py",
        "description": "Validate latest run",
        "legacy": True,
    },
    "confidence": {
        "script": "confidence_latest_run.py",
        "description": "Confidence report for latest run",
        "legacy": True,
    },
}


ALIASES = {
    "run": "feature",
    "epic": "decompose",
    "next": "schedule",
    "progress": "status",
}


def print_help():
    print("Agentic Dev Platform")
    print()
    print("Usage:")
    print("  python3 agentic.py <command> [args]")
    print()

    print("Commands:")
    for name, meta in sorted(COMMANDS.items()):
        if not meta["legacy"]:
            print(f"  {name:<12} {meta['description']}")

    print()
    print("Legacy Commands:")
    for name, meta in sorted(COMMANDS.items()):
        if meta["legacy"]:
            print(f"  {name:<12} {meta['description']}")

    print()
    print("Aliases:")
    for alias, target in sorted(ALIASES.items()):
        print(f"  {alias:<12} {target}")


def resolve_command(name):
    name = ALIASES.get(name, name)
    return COMMANDS.get(name)


def main():
    if len(sys.argv) < 2:
        print_help()
        return

    command_name = sys.argv[1]

    if command_name in {"help", "-h", "--help"}:
        print_help()
        return

    command = resolve_command(command_name)

    if not command:
        print(f"Unknown command: {command_name}")
        print()
        print_help()
        raise SystemExit(1)

    if command["legacy"]:
        print(f"[LEGACY] Executing {command_name}")

    result = subprocess.run(
        ["python3", command["script"]] + sys.argv[2:]
    )

    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
