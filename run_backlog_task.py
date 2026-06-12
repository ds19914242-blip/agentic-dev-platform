import sys
import argparse
import os
import json
from pathlib import Path

from orchestrator.backlog_store import (
    get_status,
    list_epics,
    list_tasks,
    set_pr_url,
    set_run_id,
    set_status,
    set_task_profile,
)
from orchestrator.task_status import ACTIVE_STATUSES, SKIP_STATUSES

from orchestrator.product_registry import load_product_config
from orchestrator.task_classifier import classify_task
from orchestrator.execution_router import route_task
from orchestrator.services.task_execution_service import run_task_path
import subprocess
import re


def has_human_approval(task_path):
    text = task_path.read_text(errors="ignore").lower()

    for line in text.splitlines():
        if line.startswith("human approved:"):
            return line.split(":", 1)[1].strip() in {"yes", "true", "approved", "ok"}

    return False


def task_title(task_text):
    for line in task_text.splitlines():
        line = line.strip()
        if line.startswith("### Task "):
            return line.replace("### ", "").strip()
    return task_text.splitlines()[0].strip() if task_text.splitlines() else "Untitled task"


def build_feature_request(task_text):
    title = task_title(task_text)

    return f"""Epic task: {title}

Use the following task specification as the source of truth.

{task_text}
"""


def latest_run_dir():
    runs = sorted(p for p in Path("runs").glob("feature-*") if p.is_dir())
    if not runs:
        return None
    return runs[-1]


def run_requires_manual_verification(run_dir):
    if not run_dir:
        return False

    manual_path = Path(run_dir) / "manual-verification.json"
    if manual_path.exists():
        try:
            return bool(json.loads(manual_path.read_text()).get("required"))
        except Exception:
            return False

    run_json = Path(run_dir) / "run.json"
    if run_json.exists():
        try:
            return json.loads(run_json.read_text()).get("status") == "manual_verification_required"
        except Exception:
            return False

    return False


def read_pr_url(run_dir):
    if not run_dir:
        return ""

    path = run_dir / "pull-request.md"
    if not path.exists():
        return ""

    text = path.read_text(errors="ignore")
    match = re.search(r"https://github\.com/\S+", text)
    if not match:
        match = re.search(r"https://github\.com/\S+", text.replace("\\", ""))
    return match.group(0) if match else ""


def parse_run_dir_from_stdout(stdout):
    match = re.search(r"Run:\s+(runs/[a-zA-Z0-9\-]+)", stdout)
    if not match:
        match = re.search(r"Autonomous run complete:\s+(runs/[a-zA-Z0-9\-]+)", stdout)

    return Path(match.group(1)) if match else None


def run_autonomous(product_name, task_text, repo_path_override=None, source_task_path=None):
    feature_request = build_feature_request(task_text)
    input_text = product_name + "\n" + feature_request + "\n"

    env = os.environ.copy()
    if repo_path_override:
        env["AGENTIC_REPO_PATH_OVERRIDE"] = str(repo_path_override)

    if source_task_path and has_human_approval(source_task_path):
        env["AGENTIC_HUMAN_APPROVED"] = "1"

    result = subprocess.run(
        ["python3", "run_autonomous_feature.py"],
        input=input_text,
        text=True,
        capture_output=True,
        env=env,
    )

    print(result.stdout)

    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError("Backlog task run failed")

    return result.stdout


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("task_path", nargs="?")
    parser.add_argument("--product", default="rss-agent-lab_2")
    parser.add_argument("--repo-path", default=None)
    args = parser.parse_args()

    product_name = args.product

    if args.task_path:
        run_task_path(
            args.task_path,
            product_name=product_name,
            repo_path=args.repo_path,
        )
        return

    product_name = input("Product name: ").strip()

    epics = list_epics()

    print("\nAvailable backlog epics:\n")

    for i, epic in enumerate(epics, start=1):
        print(f"[{i}] {epic.name}")

    default_epic = "1" if len(epics) == 1 else ""
    epic_raw = input(f"\nSelect epic [{default_epic}]: ").strip() or default_epic
    epic_path = epics[int(epic_raw) - 1]

    tasks = list_tasks(epic_path)

    print("\nTasks:\n")

    for i, task in enumerate(tasks, start=1):
        status = get_status(task)
        title = task_title(task.read_text(errors="ignore"))
        print(f"[{i}] [{status}] {task.name} — {title}")

    choice = input("\nTask number or 'next' [next]: ").strip() or "next"

    if choice == "next":
        pending = [task for task in tasks if get_status(task) == "todo"]

        if not pending:
            raise RuntimeError("No todo tasks in this epic.")

        task_path = pending[0]
    else:
        task_path = tasks[int(choice) - 1]

    status = get_status(task_path)

    if status in SKIP_STATUSES:
        raise RuntimeError(f"Task is not runnable because status is: {status}")

    task_text = task_path.read_text(errors="ignore")

    print(f"\nRunning task: {task_path}\n")

    set_status(task_path, "in_progress")

    try:
        stdout = run_autonomous(product_name, task_text)
    except Exception:
        set_status(task_path, "blocked")
        raise

    run_dir = parse_run_dir_from_stdout(stdout)
    if run_dir:
        set_run_id(task_path, run_dir.name)

    pr_url = read_pr_url(run_dir)

    if pr_url:
        set_pr_url(task_path, pr_url)
        set_status(task_path, "pr_created")
        print(f"\nTask marked pr_created: {task_path}")
        print(f"PR: {pr_url}")
    else:
        set_status(task_path, "no_changes_needed")
        print(f"\nTask marked no_changes_needed: no PR found for {task_path}")


if __name__ == "__main__":
    main()


# Compatibility note:
# Dependency-aware scheduler calls:
#   python3 run_backlog_task.py backlog/<epic>/task-001.md
# If this script does not yet consume sys.argv[1], keep old behavior.
