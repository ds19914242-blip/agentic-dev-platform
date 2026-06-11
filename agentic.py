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


def print_help():
    print("Agentic Dev Platform")
    print()
    print("Usage:")
    print("  python3 agentic.py <command> [args]")
    print()
    print("Commands:")
    for name, script in COMMANDS.items():
        print(f"  {name:<12} {script}")
    print()
    print("Examples:")
    print("  python3 agentic.py feature")
    print("  python3 agentic.py decompose")
    print("  python3 agentic.py backlog")
    print("  python3 agentic.py status")
    print("  python3 agentic.py status --detail")
    print("  python3 agentic.py status --all")
    print("  python3 agentic.py sync")
    print("  python3 agentic.py validate")


def main():
    if len(sys.argv) < 2:
        print_help()
        return

    command = sys.argv[1]

    if command in {"help", "-h", "--help"}:
        print_help()
        return

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
