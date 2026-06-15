"""console.state — run-state and epic-state persistence for the Agentic Console.

Extracted verbatim from server.py (Phase 5a). Each epic keeps a single
backlog/<epic>/.console_runs.json file: task entries keyed by task filename plus
one "__epic__" entry for epic-level stage flags (assembled / validated / etc.).

Functions take the backlog directory as an explicit parameter (no server globals),
so this layer is independent and unit-testable. server.py keeps thin same-named
wrappers that inject BACKLOG_DIR, so every call site is unchanged.

Behaviour is byte-for-byte identical to the originals. NOTE: writes are still plain
read-modify-write (last-writer-wins); making them atomic/transactional is a separate,
deliberate behaviour change, not part of this pure extract.
"""
import json
from datetime import datetime
from pathlib import Path

EPIC_KEY = "__epic__"


def runstate_path(backlog_dir, epic_id):
    return Path(backlog_dir) / epic_id / ".console_runs.json"


def load_runstate(backlog_dir, epic_id):
    p = runstate_path(backlog_dir, epic_id)
    if p.exists():
        try:
            return json.loads(p.read_text())
        except Exception:
            return {}
    return {}


def set_runstate(backlog_dir, epic_id, task_file, **fields):
    d = load_runstate(backlog_dir, epic_id)
    cur = d.get(task_file, {})
    cur.update(fields)
    cur["ts"] = datetime.now().strftime("%H:%M:%S")
    d[task_file] = cur
    try:
        runstate_path(backlog_dir, epic_id).write_text(json.dumps(d, ensure_ascii=False, indent=2))
    except Exception:
        pass
    return cur


def load_epic_state(backlog_dir, epic_id):
    return load_runstate(backlog_dir, epic_id).get(EPIC_KEY, {})


def set_epic_state(backlog_dir, epic_id, **fields):
    d = load_runstate(backlog_dir, epic_id)
    cur = d.get(EPIC_KEY, {})
    cur.update(fields)
    cur["ts"] = datetime.now().strftime("%H:%M:%S")
    d[EPIC_KEY] = cur
    try:
        runstate_path(backlog_dir, epic_id).write_text(json.dumps(d, ensure_ascii=False, indent=2))
    except Exception:
        pass
    return cur
