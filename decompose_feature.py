from pathlib import Path
from datetime import datetime
import re

from orchestrator.product_registry import load_product_config
from orchestrator.repository_scanner import scan_repo
from orchestrator.repository_intelligence import build_repository_map, format_repository_map
from orchestrator.claude_executor import run_claude


def slugify(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9а-яё]+", "-", text)
    return text.strip("-")[:60] or "epic"


def make_epic_dir(title):
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = Path("backlog") / f"{stamp}-{slugify(title)}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def main():
    product_name = input("Product name: ").strip()
    request = input("Big request / epic: ").strip()

    product = load_product_config(product_name)
    repo_path = product["repo_path"]

    print(f"Analyzing product: {product_name}")
    print(f"Repo: {repo_path}")

    files = scan_repo(repo_path)
    repo_map = format_repository_map(build_repository_map(files))

    prompt = f"""# Analyst / Decomposer Agent

You are an analyst agent for an autonomous development platform.

Your job is to decompose a large request into small, safe, independently shippable backlog tasks.

Do not modify files.

## Product

{product_name}

## Repository

{repo_path}

## Big Request

{request}

## Repository Map

{repo_map}

## Output Requirements

Return markdown with:

# Epic

## Summary

## Assumptions

## Task List

Each task must be:
- small enough for one autonomous coding run
- scoped to a few files where possible
- independently reviewable as a PR
- safe to validate with typecheck/tests
- dependency-aware

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
- Put foundational/shared architecture tasks before dependent UI tasks.

Then continue Task 002, Task 003, etc.

Do not include implementation code.
"""

    response = run_claude(
        repo_path=repo_path,
        prompt=prompt,
        allow_writes=False,
        max_turns=8,
    )

    epic_dir = make_epic_dir(request)

    (epic_dir / "epic.md").write_text(f"""# Epic Request

## Product

{product_name}

## Repository

{repo_path}

## Request

{request}
""")

    (epic_dir / "decomposition.md").write_text(response)

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

    print(f"Epic created: {epic_dir}")
    print(f"Tasks created: {len(tasks)}")


if __name__ == "__main__":
    main()
