from pathlib import Path
import argparse
import re

from orchestrator.claude_executor import run_claude
from orchestrator.acceptance_scenarios import (
    write_acceptance_scenarios,
    create_e2e_verification_task,
)


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


def normalize_depends_on(task_text):
    task_text = re.sub(r"\n#### Depends On\n\n.*?(?=\n---|\n## |\Z)", "", task_text, flags=re.DOTALL)
    task_text = re.sub(r"\n---\n\n## Depends On\n\n.*$", "", task_text, flags=re.DOTALL)

    if "## Depends On" not in task_text:
        task_text += "\n\n## Depends On\n\n_None_"

    return task_text


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

    scenarios_path, scenarios_text = write_acceptance_scenarios(epic_dir)

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

## Acceptance Scenarios

{scenarios_text}

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
- Do not create a final manual QA task yourself; the platform will add it automatically.

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
        task_text = normalize_depends_on(task.strip())

        if not any(line.lower().startswith("status:") for line in task_text.splitlines()):
            task_text = "Status: todo\n\n" + task_text

        (epic_dir / f"task-{i:03d}.md").write_text(task_text + "\n")

    e2e_task = create_e2e_verification_task(epic_dir, len(tasks), scenarios_text)
    total_tasks = len(tasks) + 1

    (epic_dir / "tasks.md").write_text(
        "# Tasks\n\n" + "\n\n".join(
            f"- [task-{i:03d}.md](task-{i:03d}.md)"
            for i in range(1, total_tasks + 1)
        ) + "\n"
    )

    (epic_dir / "spec-status.txt").write_text("spec_approved\n")

    print(f"Feature spec approved: {epic_dir}")
    print(f"Acceptance scenarios: {scenarios_path}")
    print(f"E2E/manual verification task: {e2e_task}")
    print(f"Tasks created: {total_tasks}")


if __name__ == "__main__":
    main()
