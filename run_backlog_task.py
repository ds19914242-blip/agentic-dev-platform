from pathlib import Path
import subprocess


def list_epics():
    backlog = Path("backlog")

    epics = sorted(
        p for p in backlog.iterdir()
        if p.is_dir()
    )

    if not epics:
        raise RuntimeError("No backlog epics found.")

    return epics


def list_tasks(epic_path):
    return sorted(epic_path.glob("task-*.md"))


def task_done(task_path):
    text = task_path.read_text(errors="ignore").lower()
    return "status: done" in text


def mark_done(task_path):
    text = task_path.read_text(errors="ignore")

    if "Status:" in text:
        lines = []
        for line in text.splitlines():
            if line.startswith("Status:"):
                lines.append("Status: done")
            else:
                lines.append(line)
        task_path.write_text("\n".join(lines) + "\n")
    else:
        task_path.write_text("Status: done\n\n" + text)


def run_autonomous(product_name, task_text):
    input_text = f"{product_name}\n{task_text}\n"

    result = subprocess.run(
        ["python3", "run_autonomous_feature.py"],
        input=input_text,
        text=True,
        capture_output=True,
    )

    print(result.stdout)

    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError("Backlog task run failed")


def main():
    product_name = input("Product name: ").strip()

    epics = list_epics()

    print("\nAvailable backlog epics:\n")

    for i, epic in enumerate(epics, start=1):
        print(f"[{i}] {epic.name}")

    epic_index = int(input("\nSelect epic: ").strip())
    epic_path = epics[epic_index - 1]

    tasks = list_tasks(epic_path)

    print("\nTasks:\n")

    for i, task in enumerate(tasks, start=1):
        status = "done" if task_done(task) else "pending"
        title = task.read_text(errors="ignore").splitlines()[0]
        print(f"[{i}] [{status}] {task.name} — {title}")

    choice = input("\nTask number or 'next': ").strip()

    if choice == "next":
        pending = [task for task in tasks if not task_done(task)]

        if not pending:
            raise RuntimeError("No pending tasks in this epic.")

        task_path = pending[0]
    else:
        task_path = tasks[int(choice) - 1]

    task_text = task_path.read_text(errors="ignore")

    print(f"\nRunning task: {task_path}\n")

    run_autonomous(product_name, task_text)

    mark_done(task_path)

    print(f"\nTask marked done: {task_path}")


if __name__ == "__main__":
    main()
