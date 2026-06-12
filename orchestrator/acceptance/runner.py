import subprocess
from pathlib import Path
from orchestrator.acceptance.result import AcceptanceResult, write_acceptance_result
from orchestrator.acceptance.bug_recovery import create_acceptance_bug_task

def load_acceptance_command(epic_dir):
    epic_dir = Path(epic_dir)
    command_file = epic_dir / "acceptance-command.txt"
    if command_file.exists():
        command = command_file.read_text(errors="ignore").strip()
        if command:
            return command
    scenarios = epic_dir / "acceptance-scenarios.md"
    if scenarios.exists():
        return "echo No acceptance-command.txt found && exit 1"
    return "echo No acceptance-scenarios.md or acceptance-command.txt found && exit 1"

def run_acceptance(epic_dir, command=None, cwd=None):
    epic_dir = Path(epic_dir)
    command = command or load_acceptance_command(epic_dir)
    cwd = cwd or "."
    result = subprocess.run(command, shell=True, cwd=cwd, text=True, capture_output=True)
    acceptance_result = AcceptanceResult(str(epic_dir), command, result.returncode == 0, result.returncode, result.stdout, result.stderr)
    write_acceptance_result(epic_dir, acceptance_result)

    if not acceptance_result.passed:
        bug_task = create_acceptance_bug_task(epic_dir, acceptance_result)
        print(f"Acceptance bug task: {bug_task}")

    return acceptance_result
