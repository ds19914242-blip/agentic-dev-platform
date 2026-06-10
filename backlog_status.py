from pathlib import Path


STATUSES = ["merged", "pr_created", "in_progress", "blocked", "todo"]


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

        grouped[status].append({
            "name": task.name,
            "title": task_title(task),
            "pr": get_pr(task),
        })

    return {
        "total": len(tasks),
        "grouped": grouped,
    }


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


def print_epic(epic_path):
    progress = epic_progress(epic_path)

    grouped = progress["grouped"]
    done = len(grouped["merged"])
    total = progress["total"]
    active = len(grouped["pr_created"]) + len(grouped["in_progress"])
    percent = round((done / total) * 100) if total else 0

    print()
    print(f"Epic: {epic_path.name}")
    print(f"Progress: {done}/{total} merged ({percent}%)")
    print(f"Active PR / In progress: {active}")
    print()

    print_group("MERGED", "✓", grouped["merged"])
    print_group("PR CREATED", "◉", grouped["pr_created"])
    print_group("IN PROGRESS", "…", grouped["in_progress"])
    print_group("BLOCKED", "⚠", grouped["blocked"])
    print_group("TODO", "□", grouped["todo"])


def main():
    backlog = Path("backlog")
    epics = sorted(p for p in backlog.iterdir() if p.is_dir())

    if not epics:
        print("No backlog epics found.")
        return

    print("Available Epics")
    print("----------------")

    for i, epic in enumerate(epics, start=1):
        print(f"[{i}] {epic.name}")

    default = "1" if len(epics) == 1 else ""
    choice = input(f"\nSelect epic [{default}]: ").strip() or default

    epic = epics[int(choice) - 1]
    print_epic(epic)


if __name__ == "__main__":
    main()
