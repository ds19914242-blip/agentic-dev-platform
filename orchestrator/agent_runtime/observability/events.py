import json
from datetime import datetime
from pathlib import Path


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


def event_path(run_dir):
    return Path(run_dir) / "runtime-events.jsonl"


def write_runtime_event(run_dir, event):
    if not run_dir:
        return None

    path = event_path(run_dir)
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "time": now_iso(),
        **event,
    }

    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")

    return path


def read_runtime_events(run_dir):
    path = event_path(run_dir)

    if not path.exists():
        return []

    events = []

    for line in path.read_text(errors="ignore").splitlines():
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except Exception:
            pass

    return events
