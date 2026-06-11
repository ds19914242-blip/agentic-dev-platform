import subprocess
import sys


COMMANDS = {
    "feature": "run_autonomous_feature.py",
    "decompose": "decompose_feature.py",
    "backlog": "run_backlog_task.py",
    "status": "backlog_status.py",
    "sync": "sync_backlog_prs.py",
    "validate": "validate_latest_run.py",
    "confidence": "confidence_latest_run.py",
}


ALIASES = {
    "run": "feature",
    "epic": "decompose",
    "next": "backlog",
    "progress": "status",
}


def print_help():
    print("Agentic Dev Platform")
    print()
    print("Usage:")
    print("  python3 agentic.py <command> [args]")
    print()
    print("Commands:")
    print("  feature      Run one autonomous feature")
    print("  decompose    Decompose a large request into backlog tasks")
    print("  backlog      Run a backlog task")
    print("  status       Show backlog status")
    print("  sync         Sync backlog PR statuses")
    print("  validate     Validate latest run")
    print("  confidence   Run confidence report for latest run")
    print()
    print("Aliases:")
    print("  run          feature")
    print("  epic         decompose")
    print("  next         backlog")
    print("  progress     status")
    print()
    print("Examples:")
    print("  python3 agentic.py feature")
    print("  python3 agentic.py epic")
    print("  python3 agentic.py next")
    print("  python3 agentic.py progress --detail")
    print("  python3 agentic.py sync")


def main():
    if len(sys.argv) < 2:
        print_help()
        return

    command = sys.argv[1]

    if command in {"help", "-h", "--help"}:
        print_help()
        return

    command = ALIASES.get(command, command)
    script = COMMANDS.get(command)

    if not script:
        print(f"Unknown command: {command}")
        print()
        print_help()
        raise SystemExit(1)

    result = subprocess.run(["python3", script] + sys.argv[2:])
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
