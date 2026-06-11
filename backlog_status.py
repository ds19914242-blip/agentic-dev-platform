from pathlib import Path
import sys


STATUSES = [
    "merged",
    "pr_created",
    "done",
    "done_no_pr",
    "in_progress",
    "blocked",
    "blocked_human_review",
    "todo",
]


def get_status(task_path):
    text = task_path.read_text(errors="ignore").lower()

    for line in text.splitlines():
        if line.startswith("status:"):
            return line.split(":", 1)[1].strip()

    return "todo"


def get_pr(task_path):
    text = task_path.read_text(errors="ignore")

    for line in text.splitlines():
        if line.lower().startswith("pr:"):
            return line.split(":", 1)[1].strip()

    return ""


def task_title(task_path):
    text = task_path.read_text(errors="ignore")

    for line in text.splitlines():
        line = line.strip()

        if line.startswith("### Task "):
            return line.replace("### ", "")

    return task_path.name


def epic_progress(epic_path):
    tasks = sorted(epic_path.glob("task-*.md"))
    grouped = {status: [] for status in STATUSES}

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


def print_epic_summary(epic_path):
    progress = epic_progress(epic_path)
    grouped = progress["grouped"]

    total = progress["total"]

    merged = len(grouped["merged"])
    pr_created = len(grouped["pr_created"])
    done = len(grouped["done"])
    done_no_pr = len(grouped["done_no_pr"])
    in_progress = len(grouped["in_progress"])
    blocked = len(grouped["blocked"])
    blocked_human_review = len(grouped["blocked_human_review"])
    todo = len(grouped["todo"])

    completed = merged + pr_created + done + done_no_pr

    percent = round((completed / total) * 100) if total else 0

    print(f"Epic: {epic_path.name}")
    print(f"Progress: {completed}/{total} completed ({percent}%)")
    print(f"Merged: {merged}")
    print(f"PR created: {pr_created}")
    print(f"Done: {done}")
    print(f"Done no PR: {done_no_pr}")
    print(f"In progress: {in_progress}")
    print(f"Blocked: {blocked}")
    print(f"Human review: {blocked_human_review}")
    print(f"Todo: {todo}")
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


def print_epic_detail(epic_path):
    progress = epic_progress(epic_path)
    grouped = progress["grouped"]

    print_epic_summary(epic_path)

    print_group("MERGED", "✓", grouped["merged"])
    print_group("PR CREATED", "◉", grouped["pr_created"])
    print_group("DONE", "✓", grouped["done"])
    print_group("DONE NO PR", "•", grouped["done_no_pr"])
    print_group("IN PROGRESS", "…", grouped["in_progress"])
    print_group("BLOCKED", "⚠", grouped["blocked"])
    print_group("HUMAN REVIEW", "!", grouped["blocked_human_review"])
    print_group("TODO", "□", grouped["todo"])


def list_epics():
    backlog = Path("backlog")

    if not backlog.exists():
        return []

    return sorted(p for p in backlog.iterdir() if p.is_dir())


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
