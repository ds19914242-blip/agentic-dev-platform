from pathlib import Path
import json


def next_task_path(epic_dir):
    epic_dir = Path(epic_dir)
    max_id = 0
    for path in epic_dir.glob("task-*.md"):
        try:
            max_id = max(max_id, int(path.stem.split("-", 1)[1]))
        except Exception:
            pass
    return epic_dir / f"task-{max_id + 1:03d}.md"


def existing_acceptance_bug_task(epic_dir):
    epic_dir = Path(epic_dir)
    for path in sorted(epic_dir.glob("task-*.md")):
        text = path.read_text(errors="ignore")
        if "Source: acceptance_failed" in text:
            return path
    return None


def create_acceptance_bug_task(epic_dir, result):
    epic_dir = Path(epic_dir)
    existing = existing_acceptance_bug_task(epic_dir)
    if existing:
        return existing

    task_path = next_task_path(epic_dir)
    result_md = epic_dir / "acceptance-result.md"
    result_json = epic_dir / "acceptance-result.json"

    task_path.write_text(f"""Status: todo
Type: bug_fix
Pipeline: standard_bugfix
Risk: high
Source: acceptance_failed

### Bug Fix — Recover failed acceptance verification

**Problem:** Automatic acceptance verification failed for epic `{epic_dir.name}`.

**Command:**

```bash
{result.command}
```

**Evidence:**
- {result_md}
- {result_json}

**Goal:** Fix the product so acceptance verification passes.

**Acceptance criteria:**
- Acceptance command exits with code 0.
- Existing validation still passes.
- No unrelated files are changed.

**Risk:** high

## Depends On

_None_
""")
    return task_path
