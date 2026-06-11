import json
from pathlib import Path


def write_run_context(run_dir, data):
    path = Path(run_dir) / "run-context.json"
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
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
