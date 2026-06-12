from pathlib import Path
import re


def extract_section(text, heading):
    pattern = rf"## {re.escape(heading)}\n\n(.*?)(?=\n## |\Z)"
    match = re.search(pattern, text, flags=re.DOTALL)
    return match.group(1).strip() if match else ""


def extract_scenarios(spec_text):
    scenarios = []

    for heading in [
        "Acceptance Scenarios",
        "Manual Verification Scenarios",
        "Acceptance Criteria",
    ]:
        section = extract_section(spec_text, heading)
        if section:
            scenarios.append((heading, section))

    return scenarios


def write_acceptance_scenarios(epic_dir):
    epic_dir = Path(epic_dir)
    spec_path = epic_dir / "feature-spec.md"

    if not spec_path.exists():
        return None, ""

    spec_text = spec_path.read_text(errors="ignore")
    scenarios = extract_scenarios(spec_text)

    body = ["# Acceptance Scenarios", ""]

    if not scenarios:
        body.append("No acceptance scenarios found in feature-spec.md.")
    else:
        for heading, section in scenarios:
            body.append(f"## {heading}")
            body.append("")
            body.append(section)
            body.append("")

    path = epic_dir / "acceptance-scenarios.md"
    text = "\n".join(body).rstrip() + "\n"
    path.write_text(text)

    return path, text


def create_e2e_verification_task(epic_dir, task_count, scenarios_text):
    epic_dir = Path(epic_dir)
    task_id = task_count + 1
    task_name = f"task-{task_id:03d}.md"

    deps = ", ".join(f"task-{i:03d}" for i in range(1, task_count + 1)) or "_None_"

    task_text = f"""Status: todo
Type: verification_task
Pipeline: manual_verification
Risk: medium

### Task {task_id:03d} — End-to-end acceptance verification

**Goal:** Verify the approved feature works end-to-end from the user's perspective.

**Scope:** Product behavior verification. Do not implement new features unless a defect is found and a follow-up bug task is created.

**Acceptance scenarios source:** `acceptance-scenarios.md`

**Required checks:**
{scenarios_text.strip() if scenarios_text.strip() else "- Manually verify the feature against feature-spec.md."}

**Acceptance criteria:**
- All acceptance scenarios pass on the target environment.
- If any scenario fails, mark this task with `agentic.py verify --failed`.
- Failed manual verification automatically creates a bug task.
- If all scenarios pass, mark this task with `agentic.py verify`.

**Risk:** medium

## Depends On

{deps}
"""

    path = epic_dir / task_name
    path.write_text(task_text)
    return path
