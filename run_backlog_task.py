import sys
import argparse
import os
from pathlib import Path

from orchestrator.product_registry import load_product_config
from orchestrator.task_classifier import classify_task
from orchestrator.execution_router import route_task
import subprocess
import re


ACTIVE_STATUSES = {"todo", "blocked"}
SKIP_STATUSES = {"in_progress", "pr_created", "merged"}


def list_epics():
    backlog = Path("backlog")
    epics = sorted(p for p in backlog.iterdir() if p.is_dir())

    if not epics:
        raise RuntimeError("No backlog epics found.")

    return epics


def list_tasks(epic_path):
    return sorted(epic_path.glob("task-*.md"))


def get_status(task_path):
    text = task_path.read_text(errors="ignore").lower()

    for line in text.splitlines():
        if line.startswith("status:"):
            return line.split(":", 1)[1].strip()

    return "todo"


def set_status(task_path, status):
    text = task_path.read_text(errors="ignore")
    lines = text.splitlines()

    updated = []
    found = False

    for line in lines:
        if line.lower().startswith("status:"):
            updated.append(f"Status: {status}")
            found = True
        else:
            updated.append(line)

    if not found:
        updated = [f"Status: {status}", ""] + updated

    task_path.write_text("\n".join(updated) + "\n")


def set_pr_url(task_path, pr_url):
    text = task_path.read_text(errors="ignore")
    lines = text.splitlines()

    updated = []
    found = False

    for line in lines:
        if line.lower().startswith("pr:"):
            updated.append(f"PR: {pr_url}")
            found = True
        else:
            updated.append(line)

    if not found:
        updated = [f"PR: {pr_url}"] + updated

    task_path.write_text("\n".join(updated) + "\n")


def set_run_id(task_path, run_id):
    text = task_path.read_text(errors="ignore")
    lines = text.splitlines()

    updated = []
    found = False

    for line in lines:
        if line.lower().startswith("run:"):
            updated.append(f"Run: {run_id}")
            found = True
        else:
            updated.append(line)

    if not found:
        updated = [f"Run: {run_id}"] + updated

    task_path.write_text("\n".join(updated) + "\n")


def set_task_profile(task_path, profile):
    text = task_path.read_text(errors="ignore")

    header = [
        f"Type: {profile.get('task_type')}",
        f"Pipeline: {profile.get('pipeline')}",
        f"Risk: {profile.get('risk')}",
    ]

    lines = text.splitlines()
    cleaned = [
        line for line in lines
        if not line.lower().startswith(("type:", "pipeline:", "risk:"))
    ]

    task_path.write_text("\n".join(header + cleaned) + "\n")


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
    match = re.search(r"Run:\s+(runs/feature-[0-9\-]+)", stdout)
    if not match:
        match = re.search(r"Autonomous run complete:\s+(runs/feature-[0-9\-]+)", stdout)

    return Path(match.group(1)) if match else None


def run_autonomous(product_name, task_text, repo_path_override=None):
    feature_request = build_feature_request(task_text)
    input_text = product_name + "\n" + feature_request + "\n"

    env = os.environ.copy()
    if repo_path_override:
        env["AGENTIC_REPO_PATH_OVERRIDE"] = str(repo_path_override)

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
        task_path = Path(args.task_path)

        if not task_path.exists():
            raise RuntimeError(f"Task not found: {task_path}")

        status = get_status(task_path)

        if status in SKIP_STATUSES:
            raise RuntimeError(f"Task is not runnable because status is: {status}")

        task_text = task_path.read_text(errors="ignore")

        product = load_product_config(product_name)
        classifier_repo_path = args.repo_path or product["repo_path"]
        task_profile = classify_task(classifier_repo_path, task_text)
        pipeline = route_task(task_profile)
        set_task_profile(task_path, task_profile)

        print(f"Running task from argv: {task_path}")
        print(f"Task type: {task_profile.get('task_type')}")
        print(f"Pipeline: {pipeline}")
        print(f"Risk: {task_profile.get('risk')}")

        if pipeline == "audit":
            set_status(task_path, "done_no_pr")
            print(f"Task marked done_no_pr: audit task should create follow-up work, not direct PR")
            return

        set_status(task_path, "in_progress")

        try:
            if pipeline == "fast":
                cmd = ["python3", "run_fast_task.py", product_name, str(task_path)]
                if args.repo_path:
                    cmd.append(str(args.repo_path))

                result = subprocess.run(
                    cmd,
                    text=True,
                    capture_output=True,
                )

                print(result.stdout)

                if result.returncode != 0:
                    print(result.stderr)
                    raise RuntimeError("Fast backlog task run failed")

                stdout = result.stdout

            elif pipeline in {"standard", "standard_bugfix"}:
                cmd = ["python3", "run_standard_task.py", product_name, str(task_path), pipeline]
                if args.repo_path:
                    cmd.append(str(args.repo_path))

                result = subprocess.run(
                    cmd,
                    text=True,
                    capture_output=True,
                )

                print(result.stdout)

                if result.returncode != 0:
                    print(result.stderr)
                    raise RuntimeError(f"{pipeline} backlog task run failed")

                stdout = result.stdout

            else:
                stdout = run_autonomous(product_name, task_text, repo_path_override=args.repo_path)
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
            print(f"Task marked pr_created: {task_path}")
            print(f"Run: {run_dir}")
            print(f"PR: {pr_url}")
        else:
            set_status(task_path, "done_no_pr")
            print(f"Task marked done_no_pr: no PR found for {task_path}")
            print(f"Run: {run_dir}")

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
        set_status(task_path, "blocked")
        print(f"\nTask marked blocked: no PR found for {task_path}")


if __name__ == "__main__":
    main()


# Compatibility note:
# Dependency-aware scheduler calls:
#   python3 run_backlog_task.py backlog/<epic>/task-001.md
# If this script does not yet consume sys.argv[1], keep old behavior.
