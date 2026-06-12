import subprocess
import sys

from orchestrator.application.command_registry import (
    ALIASES,
    active_commands,
    legacy_commands,
    resolve_command,
)


def print_help():
    print("Agentic Dev Platform")
    print()
    print("Usage:")
    print("  python3 agentic.py <command> [args]")
    print()

    print("Commands:")
    for name, meta in sorted(active_commands().items()):
        print(f"  {name:<12} {meta['description']}")

    print()
    print("Legacy Commands:")
    for name, meta in sorted(legacy_commands().items()):
        print(f"  {name:<12} {meta['description']}")

    print()
    print("Aliases:")
    for alias, target in sorted(ALIASES.items()):
        print(f"  {alias:<12} {target}")


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
