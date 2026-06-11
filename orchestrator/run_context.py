import json
from pathlib import Path

from orchestrator.run_state import attach_artifact


def write_run_context(run_dir, data):
    path = Path(run_dir) / "run-context.json"
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    run_json = Path(run_dir) / "run.json"
    if run_json.exists():
        attach_artifact(run_dir, "run-context.json", path, kind="json")

    return path


def update_run_context(run_dir, **updates):
    path = Path(run_dir) / "run-context.json"

    if path.exists():
        data = json.loads(path.read_text())
    else:
        data = {}

    data.update(updates)
    write_run_context(run_dir, data)

    return data
