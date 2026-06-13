import re
from datetime import datetime
from pathlib import Path

from orchestrator.backlog_store import load_task, save_task
from orchestrator.product_outcome import maybe_write_product_outcome_for_task
from orchestrator.outcome_store import ACCEPTED, FAILED, set_outcome_status


RESULT_BLOCK_RE = re.compile(
    r"\n## Manual Verification Result\n\n.*?(?=\n## |\Z)",
    flags=re.DOTALL,
)


def remove_previous_result_blocks(text):
    while RESULT_BLOCK_RE.search(text):
        text = RESULT_BLOCK_RE.sub("", text)
    return text.rstrip() + "\n"


def task_title(text, fallback):
    for line in text.splitlines():
        if line.startswith("### Task "):
            return line.replace("### ", "").strip()
    return fallback


def existing_manual_bug_task(text):
    match = re.search(r"Manual Bug Task:\s*(.+)", text)
    return match.group(1).strip() if match else None


def next_task_path(epic_dir):
    max_id = 0
    for task in epic_dir.glob("task-*.md"):
        match = re.match(r"task-(\d+)\.md", task.name)
        if match:
            max_id = max(max_id, int(match.group(1)))
    return epic_dir / f"task-{max_id + 1:03d}.md"


def create_manual_bug_task(source_task_path, source_text, note):
    epic_dir = source_task_path.parent
    existing = existing_manual_bug_task(source_text)
    if existing:
        return Path(existing)

    bug_path = next_task_path(epic_dir)
    source_id = source_task_path.stem
    source_title = task_title(source_text, source_task_path.name)

    bug_text = f"""Status: todo
Type: bug_fix
Pipeline: standard_bugfix
Risk: medium
Source: manual_verification_failed

### Bug Fix — Recover manual verification failure for {source_id}

**Problem:** Manual verification failed for `{source_task_path}`.

**Source task:** {source_title}

**Evidence:**
- Manual verification note: {note}

**Goal:** Fix the issue with the smallest safe change.

**Acceptance criteria:**
- The failed manual verification scenario now passes.
- Existing related behavior still works.
- Validation passes.
- No unrelated files are changed.

**Risk:** medium

## Depends On

{source_id}
"""

    bug_path.write_text(bug_text)
    return bug_path


def mark_manual_verification(task_path, failed=False, note=""):
    path = Path(task_path)

    if not path.exists():
        raise FileNotFoundError(f"Task not found: {path}")

    status = "manual_verification_failed" if failed else "manual_verification_passed"
    note = note or (
        "Manual verification failed."
        if failed
        else "Manual verification passed."
    )
    timestamp = datetime.now().isoformat(timespec="seconds")

    task = load_task(path)
    original_text = task.text
    bug_task = None

    if failed:
        bug_task = create_manual_bug_task(path, original_text, note)

    task.set_status(status)
    text = remove_previous_result_blocks(task.text)

    text += f"""
## Manual Verification Result

Status: {status}
Verified At: {timestamp}
Note: {note}
"""

    if bug_task:
        text += f"Manual Bug Task: {bug_task}\n"

    outcome_artifacts = maybe_write_product_outcome_for_task(
        task_path=path,
        task_text=text,
        manual_status=status,
        note=note,
    )

    if outcome_artifacts:
        set_outcome_status(
            path.parent,
            FAILED if failed else ACCEPTED,
            note,
        )

    task.text = text
    save_task(task)

    return {
        "task_path": path,
        "status": status,
        "bug_task": bug_task,
        "product_outcome": outcome_artifacts,
    }
