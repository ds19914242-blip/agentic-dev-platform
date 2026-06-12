import json
import os
import re
import subprocess
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
from orchestrator.execution_router import route_task
from orchestrator.product_registry import load_product_config
from orchestrator.task_classifier import classify_task
from orchestrator.task_status import SKIP_STATUSES


def has_human_approval(task_path):
    text = Path(task_path).read_text(errors="ignore").lower()

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


def run_task_path(task_path, product_name="rss-agent-lab_2", repo_path=None):
    task_path = Path(task_path)

    if not task_path.exists():
        raise RuntimeError(f"Task not found: {task_path}")

    status = get_status(task_path)

    if status in SKIP_STATUSES:
        raise RuntimeError(f"Task is not runnable because status is: {status}")

    task_text = task_path.read_text(errors="ignore")

    product = load_product_config(product_name)
    classifier_repo_path = repo_path or product["repo_path"]
    task_profile = classify_task(classifier_repo_path, task_text)
    pipeline = route_task(task_profile)
    set_task_profile(task_path, task_profile)

    print(f"Running task from argv: {task_path}")
    print(f"Task type: {task_profile.get('task_type')}")
    print(f"Pipeline: {pipeline}")
    print(f"Risk: {task_profile.get('risk')}")

    if pipeline == "audit":
        set_status(task_path, "done_no_pr")
        print("Task marked done_no_pr: audit task should create follow-up work, not direct PR")
        return

    set_status(task_path, "in_progress")

    try:
        if pipeline == "fast":
            cmd = ["python3", "run_fast_task.py", product_name, str(task_path)]
            if repo_path:
                cmd.append(str(repo_path))

            result = subprocess.run(cmd, text=True, capture_output=True)
            print(result.stdout)

            if result.returncode != 0:
                print(result.stderr)
                raise RuntimeError("Fast backlog task run failed")

            stdout = result.stdout

        elif pipeline in {"standard", "standard_bugfix"}:
            cmd = ["python3", "run_standard_task.py", product_name, str(task_path), pipeline]
            if repo_path:
                cmd.append(str(repo_path))

            result = subprocess.run(cmd, text=True, capture_output=True)
            print(result.stdout)

            if result.returncode != 0:
                print(result.stderr)
                raise RuntimeError(f"{pipeline} backlog task run failed")

            stdout = result.stdout

        else:
            stdout = run_autonomous(
                product_name,
                task_text,
                repo_path_override=repo_path,
                source_task_path=task_path,
            )
    except Exception:
        set_status(task_path, "blocked")
        raise

    run_dir = parse_run_dir_from_stdout(stdout)
    if run_dir:
        set_run_id(task_path, run_dir.name)

    pr_url = read_pr_url(run_dir)

    if pr_url and run_requires_manual_verification(run_dir):
        set_pr_url(task_path, pr_url)
        set_status(task_path, "manual_verification_required")
        print(f"Task marked manual_verification_required: {task_path}")
        print(f"Run: {run_dir}")
        print(f"PR: {pr_url}")
    elif pr_url:
        set_pr_url(task_path, pr_url)
        set_status(task_path, "pr_created")
        print(f"Task marked pr_created: {task_path}")
        print(f"Run: {run_dir}")
        print(f"PR: {pr_url}")
    elif "NEEDS_HUMAN_REVIEW" in stdout and not has_human_approval(task_path):
        set_status(task_path, "blocked_human_review")
        print(f"Task marked blocked_human_review: human review required for {task_path}")
        print(f"Run: {run_dir}")
    elif "NEEDS_HUMAN_REVIEW" in stdout and has_human_approval(task_path):
        set_status(task_path, "blocked_human_review")
        print(f"Task still requires human review despite approval: {task_path}")
        print(f"Run: {run_dir}")
    elif "already_satisfied" in stdout.lower():
        set_status(task_path, "already_satisfied")
        print(f"Task marked already_satisfied: {task_path}")
        print(f"Run: {run_dir}")
    elif run_requires_manual_verification(run_dir):
        set_status(task_path, "manual_verification_required")
        print(f"Task marked manual_verification_required: {task_path}")
        print(f"Run: {run_dir}")
    else:
        set_status(task_path, "no_changes_needed")
        print(f"Task marked no_changes_needed: no PR found for {task_path}")
        print(f"Run: {run_dir}")


def run_interactive_task():
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
