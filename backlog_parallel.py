import sys
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from orchestrator.backlog_dag import (
    ensure_epic_depends_on_sections,
    write_dag_json,
    load_epic_tasks,
    ready_tasks,
)


def latest_epic_dir():
    dirs = sorted(Path("backlog").glob("*"), key=lambda p: p.stat().st_mtime, reverse=True)
    dirs = [p for p in dirs if p.is_dir()]
    if not dirs:
        raise SystemExit("No backlog epic directories found")
    return dirs[0]


def run_task(task):
    result = subprocess.run(
        ["python3", "run_backlog_task.py", task["path"]],
        text=True,
        capture_output=True,
    )

    return {
        "task": task["id"],
        "path": task["path"],
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def main():
    epic_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else latest_epic_dir()
    max_workers = int(sys.argv[2]) if len(sys.argv) > 2 else 2

    ensure_epic_depends_on_sections(epic_dir)
    write_dag_json(epic_dir)

    ready = ready_tasks(load_epic_tasks(epic_dir))

    if not ready:
        print("No ready backlog tasks")
        return

    print(f"Ready tasks: {', '.join(task['id'] for task in ready)}")
    print(f"Parallel workers: {max_workers}")

    failed = False

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(run_task, task) for task in ready[:max_workers]]

        for future in as_completed(futures):
            result = future.result()

            print()
            print(f"=== {result['task']} ===")
            print(f"Return code: {result['returncode']}")

            if result["stdout"]:
                print("--- STDOUT ---")
                print(result["stdout"])

            if result["stderr"]:
                print("--- STDERR ---")
                print(result["stderr"])

            if result["returncode"] != 0:
                failed = True

    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
