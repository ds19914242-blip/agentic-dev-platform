import sys
from pathlib import Path

from orchestrator.backlog_dag import (
    blocked_tasks,
    dependency_errors,
    ensure_epic_depends_on_sections,
    load_epic_tasks,
    ready_tasks,
    write_dag_json,
)
from orchestrator.backlog_query import latest_epic_dir


def main():
    epic_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else latest_epic_dir()

    ensure_epic_depends_on_sections(epic_dir)
    dag_path, data = write_dag_json(epic_dir)

    tasks = load_epic_tasks(epic_dir)
    ready = ready_tasks(tasks)
    blocked = blocked_tasks(tasks)
    errors = dependency_errors(tasks)

    print(f"Epic: {epic_dir}")
    print(f"DAG: {dag_path}")
    print()

    print("Ready:")
    if ready:
        for task in ready:
            print(f"- {task['id']}")
    else:
        print("- none")

    print()
    print("Blocked:")
    if blocked:
        for task in blocked:
            print(f"- {task['id']} blocked by {', '.join(task['blocked_by'])}")
    else:
        print("- none")

    if errors:
        print()
        print("Dependency errors:")
        for error in errors:
            print(f"- {error['task']} references missing {error['missing_dependency']}")


if __name__ == "__main__":
    main()
