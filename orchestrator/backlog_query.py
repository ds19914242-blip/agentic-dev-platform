from pathlib import Path

from orchestrator.backlog_store import list_epics


def latest_epic_dir(backlog_dir="backlog"):
    epics = sorted(
        list_epics(backlog_dir),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    if not epics:
        raise SystemExit("No backlog epic directories found")

    return epics[0]
