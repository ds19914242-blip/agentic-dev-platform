from pathlib import Path


def task_done(task_path):
    text = task_path.read_text(errors="ignore").lower()
    return "status: done" in text


def task_title(task_path):
    text = task_path.read_text(errors="ignore")

    for line in text.splitlines():
        line = line.strip()

        if line.startswith("### Task "):
            return line.replace("### ", "")

    return task_path.name


def epic_progress(epic_path):
    tasks = sorted(epic_path.glob("task-*.md"))

    completed = []
    pending = []

    for task in tasks:
        entry = {
            "name": task.name,
            "title": task_title(task),
        }

        if task_done(task):
            completed.append(entry)
        else:
            pending.append(entry)

    return {
        "total": len(tasks),
        "completed": completed,
        "pending": pending,
    }


def print_epic(epic_path):
    progress = epic_progress(epic_path)

    done = len(progress["completed"])
    total = progress["total"]

    percent = round((done / total) * 100) if total else 0

    print()
    print(f"Epic: {epic_path.name}")
    print(f"Progress: {done}/{total} ({percent}%)")
    print()

    print("DONE")
    print("----")

    if progress["completed"]:
        for task in progress["completed"]:
            print(f"✓ {task['title']}")
    else:
        print("None")

    print()
    print("PENDING")
    print("-------")

    if progress["pending"]:
        for task in progress["pending"]:
            print(f"□ {task['title']}")
    else:
        print("None")

    print()


def main():
    backlog = Path("backlog")

    epics = sorted(
        p for p in backlog.iterdir()
        if p.is_dir()
    )

    if not epics:
        print("No backlog epics found.")
        return

    print("Available Epics")
    print("----------------")

    for i, epic in enumerate(epics, start=1):
        print(f"[{i}] {epic.name}")

    print()

    default = "1" if len(epics) == 1 else ""

    choice = input(
        f"Select epic [{default}]: "
    ).strip()

    if not choice:
        choice = default

    epic = epics[int(choice) - 1]

    print_epic(epic)


if __name__ == "__main__":
    main()
