import os
import subprocess
from pathlib import Path

from orchestrator.acceptance.auto_command import infer_acceptance_command
from orchestrator.acceptance.bug_recovery import create_acceptance_bug_task
from orchestrator.acceptance.playwright_acceptance_agent import generate_playwright_acceptance
from orchestrator.acceptance.result import AcceptanceResult, write_acceptance_result
from orchestrator.product_registry import load_product_config


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


def product_acceptance_config(product_name):
    if not product_name:
        return {}

    product = load_product_config(product_name)

    return (
        product.get("acceptance", {})
        or product.get("verification", {}).get("acceptance", {})
        or {}
    )


def _acceptance_env(config):
    env = os.environ.copy()

    base_url = os.environ.get("ACCEPTANCE_BASE_URL") or config.get("base_url")

    if base_url:
        env["ACCEPTANCE_BASE_URL"] = str(base_url)

    return env


def run_acceptance(epic_dir, command=None, cwd=None, product_name=None):
    epic_dir = Path(epic_dir)
    config = product_acceptance_config(product_name)

    cwd = cwd or config.get("cwd") or "."
    command = command or config.get("command") or infer_acceptance_command(epic_dir)

    if not command:
        repo_path = cwd

        if product_name:
            try:
                product = load_product_config(product_name)
                repo_path = product.get("repo_path") or cwd
                cwd = config.get("cwd") or repo_path
            except Exception:
                repo_path = cwd

        try:
            command = generate_playwright_acceptance(
                epic_dir=epic_dir,
                product_name=product_name or "",
                repo_path=repo_path,
                config=config,
            )
        except Exception as exc:
            command = f"echo Acceptance command generation failed: {str(exc)!r} && exit 1"
            (epic_dir / "acceptance-command.txt").write_text(command + "\n")

    if not command:
        command = load_acceptance_command(epic_dir)

    env = _acceptance_env(config)

    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            text=True,
            capture_output=True,
            timeout=int(config.get("timeout_seconds", 300) or 300),
            env=env,
        )
    except subprocess.TimeoutExpired as exc:
        result = subprocess.CompletedProcess(
            args=command,
            returncode=124,
            stdout=exc.stdout or "",
            stderr=(exc.stderr or "") + "\nAcceptance verification timed out.",
        )

    acceptance_result = AcceptanceResult(
        str(epic_dir),
        command,
        result.returncode == 0,
        result.returncode,
        result.stdout,
        result.stderr,
    )

    write_acceptance_result(epic_dir, acceptance_result)

    if not acceptance_result.passed:
        bug_task = create_acceptance_bug_task(epic_dir, acceptance_result)
        acceptance_result.bug_task = str(bug_task)
        write_acceptance_result(epic_dir, acceptance_result)
        print(f"Acceptance bug task: {bug_task}")

    return acceptance_result
