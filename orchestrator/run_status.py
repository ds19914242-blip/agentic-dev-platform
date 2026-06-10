from pathlib import Path
from datetime import datetime


def write_status(run_dir, status):
    path = Path(run_dir) / "status.md"

    path.write_text(f"""# Run Status

## Status

{status}

## Updated At

{datetime.now().isoformat()}
""")

    return path


def append_event(run_dir, event):
    path = Path(run_dir) / "events.md"
    timestamp = datetime.now().isoformat()

    with path.open("a") as f:
        f.write(f"- {timestamp} — {event}\n")

    return path
