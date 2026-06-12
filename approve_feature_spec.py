from pathlib import Path
import argparse
import re

from orchestrator.claude_executor import run_claude


def extract_section(text, heading):
    pattern = rf"## {re.escape(heading)}\n\n(.*?)(?=\n## |\Z)"
    match = re.search(pattern, text, flags=re.DOTALL)
    return match.group(1).strip() if match else ""


def parse_epic(epic_dir):
    epic_md = Path(epic_dir) / "epic.md"
    text = epic_md.read_text(errors="ignore")

    product = extract_section(text, "Product")
    repo = extract_section(text, "Repository")
    request = extract_section(text, "Request")

    if not product or not repo or not request:
        raise RuntimeError(f"Could not parse epic.md: {epic_md}")

    return product, repo, request


def parse_tasks(response):
    tasks = []
    current = []

    for line in response.splitlines():
        if line.startswith("### Task "):
            if current:
                tasks.append("\n".join(current).strip())
            current = [line]
        elif current:
            current.append(line)

    if current:
        tasks.append("\n".join(current).strip())

    return tasks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("epic_dir")
    args = parser.parse_args()

    epic_dir = Path(args.epic_dir)
    spec_path = epic_dir / "feature-spec.md"

    if not spec_path.exists():
        raise RuntimeError(f"feature-spec.md not found: {spec_path}")

    product, repo_path, request = parse_epic(epic_dir)
    spec = spec_path.read_text(errors="ignore")

    prompt = f"""# Backlog Decomposer

You are decomposing an approved feature specification into small dependency-aware backlog tasks.

Do not modify files.

## Product

{product}

## Repository

{repo_path}

## Original Request

{request}

## Approved Feature Specification

{spec}

## Output Requirements

Return markdown with:

# Epic

## Summary

## Task List

Each task must be:
- small enough for one autonomous coding run
- independently reviewable as a PR
- safe to validate
- dependency-aware
- directly traceable to the approved acceptance criteria

Use this exact task format:

### Task 001 — <title>

**Goal:** ...
**Scope:** ...
**Suggested files:** ...
**Acceptance criteria:** ...
**Risk:** low | medium | high

## Depends On

_None_

Dependency rules:
- Every generated task MUST include a section named exactly: ## Depends On
- Use _None_ when the task has no dependencies.
- Use task ids like task-001, task-002 when a task depends on earlier tasks.
- Prefer a DAG, not a strict chain.
- Independent tasks should have _None_ so they can run in parallel.
- Do not create unnecessary dependencies.

Do not include implementation code.
"""

    response = run_claude(
        repo_path=repo_path,
        prompt=prompt,
        allow_writes=False,
        max_turns=8,
    )

    (epic_dir / "decomposition.md").write_text(response)

    tasks = parse_tasks(response)

    for old_task in epic_dir.glob("task-*.md"):
        old_task.unlink()

    for i, task in enumerate(tasks, start=1):
        task_text = task.strip()

        if "## Depends On" not in task_text:
            task_text += "\n\n## Depends On\n\n_None_"

        if not any(line.lower().startswith("status:") for line in task_text.splitlines()):
            task_text = "Status: todo\n\n" + task_text

        (epic_dir / f"task-{i:03d}.md").write_text(task_text + "\n")

    (epic_dir / "tasks.md").write_text(
        "# Tasks\n\n" + "\n\n".join(
            f"- [task-{i:03d}.md](task-{i:03d}.md)"
            for i in range(1, len(tasks) + 1)
        ) + "\n"
    )

    (epic_dir / "spec-status.txt").write_text("spec_approved\n")

    print(f"Feature spec approved: {epic_dir}")
    print(f"Tasks created: {len(tasks)}")


if __name__ == "__main__":
    main()
