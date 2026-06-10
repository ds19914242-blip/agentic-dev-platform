from pathlib import Path
import subprocess


def run(command, cwd="."):
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True)

    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)

    return result.stdout.strip()


def get_status(task_path):
    text = task_path.read_text(errors="ignore").lower()

    for line in text.splitlines():
        if line.startswith("status:"):
            return line.split(":", 1)[1].strip()

    return "todo"


def set_status(task_path, status):
    text = task_path.read_text(errors="ignore")
    lines = text.splitlines()
    updated = []
    found = False

    for line in lines:
        if line.lower().startswith("status:"):
            updated.append(f"Status: {status}")
            found = True
        else:
            updated.append(line)

    if not found:
        updated = [f"Status: {status}", ""] + updated

    task_path.write_text("\n".join(updated) + "\n")


def get_pr(task_path):
    text = task_path.read_text(errors="ignore")

    for line in text.splitlines():
        if line.lower().startswith("pr:"):
            return line.split(":", 1)[1].strip()

    return ""


def main():
    tasks = sorted(Path("backlog").glob("*/task-*.md"))

    updated = 0

    for task in tasks:
        pr = get_pr(task)

        if not pr:
            continue

        status = get_status(task)

        if status not in {"pr_created", "in_progress"}:
            continue

        state = run([
            "gh",
            "pr",
            "view",
            pr,
            "--json",
            "state,mergedAt",
            "--jq",
            "if .mergedAt then \"merged\" else .state end",
        ])

        if state.lower() == "merged":
            set_status(task, "merged")
            updated += 1
        elif state.lower() == "closed":
            set_status(task, "blocked")
            updated += 1
        else:
            set_status(task, "pr_created")

    print(f"Backlog PR sync complete. Updated: {updated}")


if __name__ == "__main__":
    main()
