import os
import subprocess
import sys
from pathlib import Path

from orchestrator.application.command_registry import (
    ALIASES,
    active_commands,
    legacy_commands,
    resolve_command,
)


ROOT_DIR = Path(__file__).resolve().parent


def print_help():
    print("Agentic Dev Platform")
    print()
    print("Usage:")
    print("  python3 agentic.py <command> [args]")
    print()

    print("Commands:")
    for name, meta in sorted(active_commands().items()):
        print(f"  {name:<18} {meta['description']}")

    print()
    print("Legacy Commands:")
    for name, meta in sorted(legacy_commands().items()):
        print(f"  {name:<18} {meta['description']}")

    print()
    print("Aliases:")
    for alias, target in sorted(ALIASES.items()):
        print(f"  {alias:<18} {target}")


def command_script_path(command):
    script = command["script"]
    candidates = [
        ROOT_DIR / script,
        ROOT_DIR / "cli/commands" / script,
        ROOT_DIR / "cli/legacy" / script,
    ]

    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    return script


def command_env():
    env = os.environ.copy()
    current = env.get("PYTHONPATH", "")
    root = str(ROOT_DIR)

    if current:
        env["PYTHONPATH"] = root + os.pathsep + current
    else:
        env["PYTHONPATH"] = root

    return env


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
        ["python3", command_script_path(command)] + sys.argv[2:],
        cwd=str(ROOT_DIR),
        env=command_env(),
    )

    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
