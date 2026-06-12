from pathlib import Path
import json
import re

from orchestrator.backlog_store import list_tasks, load_task
from orchestrator.task_status import COMPLETED_STATUSES


TERMINAL_STATUSES = set(COMPLETED_STATUSES) | {"completed"}


def task_id_from_path(path):
    return Path(path).stem


def extract_depends_on(text):
    depends_on = []

    section_match = re.search(
        r"^##\s*Depends On\s*$([\s\S]*?)(?=^##\s+|\Z)",
        text,
        re.MULTILINE | re.IGNORECASE,
    )

    if not section_match:
        return depends_on

    body = section_match.group(1).strip()

    for line in body.splitlines():
        item = line.strip().lstrip("-").strip()

        if not item or item.lower() in {"none", "_none_", "n/a"}:
            continue

        parts = [
            part.strip()
            for part in item.replace(" and ", ",").split(",")
            if part.strip()
        ]
        depends_on.extend(parts)

    return depends_on


def read_task(path):
    task = load_task(path)

    return {
        "id": task_id_from_path(path),
        "path": str(path),
        "status": task.status,
        "depends_on": extract_depends_on(task.text),
    }


def load_epic_tasks(epic_dir):
    return [read_task(path) for path in list_tasks(epic_dir)]


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

    for path in list_tasks(epic_dir):
        if ensure_depends_on_section(path):
            changed.append(str(path))

    return changed
