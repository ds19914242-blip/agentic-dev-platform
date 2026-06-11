from pathlib import Path
import re
import json


TERMINAL_STATUSES = {"merged", "done", "completed", "pr_created", "done_no_pr"}


def task_id_from_path(path):
    return Path(path).stem


def read_task(path):
    path = Path(path)
    text = path.read_text()

    status = "todo"
    depends_on = []

    status_match = re.search(r"^status:\s*(.+)$", text, re.MULTILINE | re.IGNORECASE)
    if status_match:
        status = status_match.group(1).strip().lower()

    section_match = re.search(
        r"^##\s*Depends On\s*$([\s\S]*?)(?=^##\s+|\Z)",
        text,
        re.MULTILINE | re.IGNORECASE,
    )

    if section_match:
        body = section_match.group(1).strip()
        for line in body.splitlines():
            item = line.strip().lstrip("-").strip()
            if item and item.lower() not in {"none", "_none_", "n/a"}:
                depends_on.append(item)

    return {
        "id": task_id_from_path(path),
        "path": str(path),
        "status": status,
        "depends_on": depends_on,
    }


def load_epic_tasks(epic_dir):
    epic_dir = Path(epic_dir)
    tasks = []

    for path in sorted(epic_dir.glob("task-*.md")):
        tasks.append(read_task(path))

    return tasks


def task_map(tasks):
    return {task["id"]: task for task in tasks}


def dependency_errors(tasks):
    tasks_by_id = task_map(tasks)
    errors = []

    for task in tasks:
        for dep in task["depends_on"]:
            if dep not in tasks_by_id:
                errors.append({
                    "task": task["id"],
                    "missing_dependency": dep,
                })

    return errors


def is_ready(task, tasks_by_id):
    if task["status"] != "todo":
        return False

    for dep in task["depends_on"]:
        dep_task = tasks_by_id.get(dep)
        if not dep_task:
            return False
        if dep_task["status"] not in TERMINAL_STATUSES:
            return False

    return True


def ready_tasks(tasks):
    tasks_by_id = task_map(tasks)
    return [task for task in tasks if is_ready(task, tasks_by_id)]


def blocked_tasks(tasks):
    tasks_by_id = task_map(tasks)
    blocked = []

    for task in tasks:
        if task["status"] != "todo":
            continue

        unmet = []
        for dep in task["depends_on"]:
            dep_task = tasks_by_id.get(dep)
            if not dep_task or dep_task["status"] not in TERMINAL_STATUSES:
                unmet.append(dep)

        if unmet:
            item = dict(task)
            item["blocked_by"] = unmet
            blocked.append(item)

    return blocked


def write_dag_json(epic_dir):
    epic_dir = Path(epic_dir)
    tasks = load_epic_tasks(epic_dir)

    data = {
        "epic": epic_dir.name,
        "tasks": tasks,
        "ready": [task["id"] for task in ready_tasks(tasks)],
        "blocked": [
            {
                "id": task["id"],
                "blocked_by": task["blocked_by"],
            }
            for task in blocked_tasks(tasks)
        ],
        "errors": dependency_errors(tasks),
    }

    path = epic_dir / "dag.json"
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    return path, data


def ensure_depends_on_section(task_path):
    task_path = Path(task_path)
    text = task_path.read_text()

    if re.search(r"^##\s*Depends On\s*$", text, re.MULTILINE | re.IGNORECASE):
        return False

    text = text.rstrip() + "\n\n## Depends On\n\n_None_\n"
    task_path.write_text(text)
    return True


def ensure_epic_depends_on_sections(epic_dir):
    changed = []
    for path in sorted(Path(epic_dir).glob("task-*.md")):
        if ensure_depends_on_section(path):
            changed.append(str(path))
    return changed
