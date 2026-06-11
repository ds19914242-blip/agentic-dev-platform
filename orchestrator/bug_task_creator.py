from pathlib import Path
from datetime import datetime


def now_stamp():
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def create_bug_task(run_dir, source_task_path=None, reason="validation_failed"):
    run_dir = Path(run_dir)
    epic_dir = None

    if source_task_path:
        source_task_path = Path(source_task_path)
        epic_dir = source_task_path.parent

    if epic_dir is None:
        epic_dir = Path("backlog") / f"auto-bugs-{now_stamp()}"
        epic_dir.mkdir(parents=True, exist_ok=True)

    existing = sorted(epic_dir.glob("task-*.md"))
    next_id = len(existing) + 1
    task_id = f"task-{next_id:03d}"
    task_path = epic_dir / f"{task_id}.md"

    validation_md = run_dir / "validation.md"
    run_json = run_dir / "run.json"

    source_task_name = source_task_path.name if source_task_path else "unknown"

    task_path.write_text(f"""Status: todo
Type: bug_fix
Pipeline: standard_bugfix
Risk: medium
Source: {reason}
Run: {run_dir.name}

### Bug Fix — Recover failed run {run_dir.name}

**Problem:** A previous Agentic Dev Platform run failed or did not complete successfully.

**Source task:** {source_task_name}

**Evidence:**
- {validation_md}
- {run_json}

**Goal:** Fix the issue with the smallest safe change.

**Acceptance criteria:**
- Validation passes.
- The original task can be completed or safely marked resolved.
- No unrelated files are changed.

**Risk:** medium

## Depends On

_None_
""")

    return task_path
