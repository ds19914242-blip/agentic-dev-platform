import json
from pathlib import Path
from datetime import datetime


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


def _load_run_json(run_dir):
    path = Path(run_dir) / "run.json"
    if not path.exists():
        return None, path

    return json.loads(path.read_text()), path


def _write_run_json(path, data):
    data["updated_at"] = now_iso()
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def write_status(run_dir, status):
    run_dir = Path(run_dir)
    path = run_dir / "status.md"
    timestamp = now_iso()

    path.write_text(f"""# Run Status

## Status

{status}

## Updated At

{timestamp}
""")

    data, run_json_path = _load_run_json(run_dir)
    if data is not None:
        data["status"] = status
        data.setdefault("metadata", {})
        data["metadata"]["last_status"] = status
        data["metadata"]["status_updated_at"] = timestamp

        data.setdefault("artifacts", {})
        data["artifacts"]["status.md"] = {
            "kind": "markdown",
            "path": str(path),
            "updated_at": timestamp,
        }

        _write_run_json(run_json_path, data)

    return path


def append_event(run_dir, event):
    run_dir = Path(run_dir)
    path = run_dir / "events.md"
    timestamp = now_iso()

    with path.open("a") as f:
        f.write(f"- {timestamp} — {event}\n")

    data, run_json_path = _load_run_json(run_dir)
    if data is not None:
        data.setdefault("events", [])
        data["events"].append({
            "timestamp": timestamp,
            "event": event,
        })

        data.setdefault("artifacts", {})
        data["artifacts"]["events.md"] = {
            "kind": "markdown",
            "path": str(path),
            "updated_at": timestamp,
        }

        _write_run_json(run_json_path, data)

    return path
