from pathlib import Path
import sys

from orchestrator.backlog_store import get_pr, get_status, list_epics, task_title
from orchestrator.task_status import COMPLETED_STATUSES, ORDERED_STATUSES
from orchestrator.outcome_store import infer_epic_state, load_outcome


def epic_progress(epic_path: Path):
    tasks = sorted(epic_path.glob("task-*.md"))
    grouped = {status: [] for status in ORDERED_STATUSES}

    for task in tasks:
        status = get_status(task)
        if status not in grouped:
            status = "todo"

        grouped[status].append(
            {
                "name": task.name,
                "title": task_title(task),
                "pr": get_pr(task),
            }
        )

    return {
        "total": len(tasks),
        "grouped": grouped,
    }


def print_epic_summary(epic_path: Path):
    progress = epic_progress(epic_path)
    grouped = progress["grouped"]
    total = progress["total"]

    completed = sum(len(grouped[status]) for status in COMPLETED_STATUSES)
    percent = round((completed / total) * 100) if total else 0

    outcome = load_outcome(epic_path)
    epic_state = infer_epic_state(epic_path, total, completed)

    print(f"Epic: {epic_path.name}")
    print(f"Progress: {completed}/{total} completed ({percent}%)")
    print(f"Outcome: {outcome.get('status', 'planned')}")
    print(f"Epic State: {epic_state}")
    print(f"Outcome Goal: {outcome.get('goal', '')[:140]}")

    for status in ORDERED_STATUSES:
        print(f"{status}: {len(grouped[status])}")

    print()


def print_group(title, icon, items):
    print(title)
    print("-" * len(title))

    if not items:
        print("None")
        print()
        return

    for task in items:
        suffix = f" — {task['pr']}" if task["pr"] else ""
        print(f"{icon} {task['title']}{suffix}")

    print()


def print_epic_detail(epic_path: Path):
    progress = epic_progress(epic_path)
    grouped = progress["grouped"]

    print_epic_summary(epic_path)

    icons = {
        "merged": "✓",
        "pr_created": "◉",
        "done": "✓",
        "done_no_pr": "•",
        "already_satisfied": "=",
        "no_changes_needed": "•",
        "manual_verification_required": "?",
        "manual_verification_passed": "✓",
        "manual_verification_failed": "✗",
        "in_progress": "…",
        "blocked": "⚠",
        "blocked_human_review": "!",
        "todo": "□",
    }

    for status in ORDERED_STATUSES:
        print_group(status.upper().replace("_", " "), icons.get(status, "-"), grouped[status])


def main():
    epics = list_epics()

    if not epics:
        print("No backlog epics found.")
        return

    args = sys.argv[1:]

    if "--all" in args:
        for epic in epics:
            print_epic_summary(epic)
        return

    if "--detail" in args:
        index = 0
        for arg in args:
            if arg.isdigit():
                index = int(arg) - 1

        print_epic_detail(epics[index])
        return

    for epic in epics:
        print_epic_summary(epic)


if __name__ == "__main__":
    main()
