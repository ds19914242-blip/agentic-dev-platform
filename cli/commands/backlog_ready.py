import sys
from pathlib import Path

from orchestrator.backlog_dag import (
    ensure_epic_depends_on_sections,
    load_epic_tasks,
    ready_tasks,
    write_dag_json,
)
from orchestrator.backlog_query import latest_epic_dir


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
