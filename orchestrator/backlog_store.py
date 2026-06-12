from __future__ import annotations

from pathlib import Path

from orchestrator.task_model import TaskDocument
from orchestrator.task_status import normalize_status


def load_task(task_path):
    path = Path(task_path)
    return TaskDocument(path=path, text=path.read_text(errors="ignore"))


def save_task(task):
    task.path.write_text(task.text)


def get_status(task_path):
    return load_task(task_path).status


def set_status(task_path, status):
    task = load_task(task_path)
    task.set_status(normalize_status(status))
    save_task(task)


def get_pr(task_path):
    return load_task(task_path).pr_url


def set_pr_url(task_path, pr_url):
    task = load_task(task_path)
    task.set_field("PR", pr_url)
    save_task(task)


def set_run_id(task_path, run_id):
    task = load_task(task_path)
    task.set_field("Run", run_id)
    save_task(task)


def set_task_profile(task_path, profile):
    task = load_task(task_path)
    task.remove_fields(["Type", "Pipeline", "Risk"])
    header = (
        f"Type: {profile.get('task_type')}\n"
        f"Pipeline: {profile.get('pipeline')}\n"
        f"Risk: {profile.get('risk')}\n"
    )
    task.text = header + task.text.lstrip()
    save_task(task)


def task_title(task_path):
    return load_task(task_path).title


def list_epics(backlog_dir="backlog"):
    backlog = Path(backlog_dir)
    if not backlog.exists():
        return []
    return sorted(path for path in backlog.iterdir() if path.is_dir())


def list_tasks(epic_path):
    return sorted(Path(epic_path).glob("task-*.md"))
