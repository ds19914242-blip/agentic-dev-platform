import sys
import argparse
from pathlib import Path

from orchestrator.backlog_store import get_status, list_epics, list_tasks, set_pr_url, set_run_id, set_status
from orchestrator.task_status import SKIP_STATUSES

from orchestrator.services.task_execution_service import run_task_path


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
