import os
from pathlib import Path

DEFAULT_ROOT = os.environ.get(
    "AGENTIC_DATA_ROOT",
    str(Path.home() / ".agentic-dev-platform"),
)

DATA_ROOT = Path(DEFAULT_ROOT)

RUNS_DIR = DATA_ROOT / "runs"
BACKLOG_DIR = DATA_ROOT / "backlog"
MEMORY_DIR = DATA_ROOT / "memory"

for path in [RUNS_DIR, BACKLOG_DIR, MEMORY_DIR]:
    path.mkdir(parents=True, exist_ok=True)
