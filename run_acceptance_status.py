import argparse
import json
from pathlib import Path


def latest_epic_dir():
    backlog = Path("backlog")
    epics = sorted([p for p in backlog.glob("*") if p.is_dir()], key=lambda p: p.stat().st_mtime, reverse=True)
    if not epics:
        raise SystemExit("No backlog epic directories found.")
    return epics[0]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("epic_dir", nargs="?")
    args = parser.parse_args()

    epic_dir = Path(args.epic_dir) if args.epic_dir else latest_epic_dir()
    result_path = epic_dir / "acceptance-result.json"

    if not result_path.exists():
        print(f"Epic: {epic_dir}")
        print("Acceptance: not_run")
        return

    result = json.loads(result_path.read_text(errors="ignore"))
    print(f"Epic: {epic_dir}")
    print(f"Acceptance: {passed if result.get(passed) else failed}")
    print(f"Command: {result.get(command)}")
    print(f"Return code: {result.get(returncode)}")

    bug_tasks = []
    for task in sorted(epic_dir.glob("task-*.md")):
        text = task.read_text(errors="ignore")
        if "Source: acceptance_failed" in text:
            bug_tasks.append(task)

    if result.get("bug_task"):
        print(f"Bug task: {result.get(bug_task)}")

    if bug_tasks:
        print("Bug tasks:")
        for task in bug_tasks:
            print(f"- {task}")


if __name__ == "__main__":
    main()
