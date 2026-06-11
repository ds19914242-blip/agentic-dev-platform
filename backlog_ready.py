import sys
from pathlib import Path

from orchestrator.backlog_dag import (
    load_epic_tasks,
    ready_tasks,
    ensure_epic_depends_on_sections,
    write_dag_json,
)


def latest_epic_dir():
    dirs = sorted(Path("backlog").glob("*"), key=lambda p: p.stat().st_mtime, reverse=True)
    dirs = [p for p in dirs if p.is_dir()]
    if not dirs:
        raise SystemExit("No backlog epic directories found")
    return dirs[0]


def main():
    epic_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else latest_epic_dir()

    ensure_epic_depends_on_sections(epic_dir)
    write_dag_json(epic_dir)

    ready = ready_tasks(load_epic_tasks(epic_dir))

    if not ready:
        print("No ready tasks")
        return

    for task in ready:
        print(task["path"])


if __name__ == "__main__":
    main()
