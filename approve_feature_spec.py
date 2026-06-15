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
- If task B consumes a contract that task A changes, B MUST depend on A. If two tasks edit
  the same shared file or module, encode the real ordering as a dependency — do not leave
  genuinely related tasks as _None_.
- Do not create a final manual QA task yourself; the platform will add it automatically.

## One file, one task (prevents assembly conflicts)

Do NOT split edits to the SAME source file across multiple tasks. If several changes from
the request touch the same file (e.g. several edits to one component, one router, one
stylesheet), combine them into a SINGLE task — list each change as a separate bullet under
**Scope** so it stays reviewable. Different files remain different tasks, exactly as before.
Reason: two independent tasks editing the same file from a common base cannot be merged
cleanly at assembly time and will collide. Keeping same-file work in one task removes that
collision by construction, while still allowing a clean DAG across files.

When a single shared file is genuinely touched by work that must be staged (e.g. a contract
change in file A consumed by file B), keep A's edits in one task and B's in another, with B
depending on A — never two sibling tasks both editing A from the same base.

## Change-integrity invariant (critical — this is what keeps the build green)

A change to any SHARED or EXPORTED contract creates obligations elsewhere. Treat all of
these as contract changes: removing, renaming, or narrowing a type, union member, enum
value, or interface field; changing a function/method signature; adding a required
parameter, prop, or field; changing the shape of an API request or response; moving or
renaming an exported module or its path.

For every contract change a task introduces, the plan MUST also guarantee that ALL
consumers of that contract are updated, so the repository still compiles and behaves
consistently:
- Changing a definition (removing, renaming, retyping) while leaving references to it
  elsewhere is an INCOMPLETE decomposition. Either fold the consumer updates into the same
  task, or add a dedicated task that reconciles every consumer, depending on the change.
- Naming "Suggested files" is not enough. For a contract change, identify where the
  contract is DEFINED and where it is CONSUMED, and make sure both are covered.
- Scope this to shared / exported / public contracts only. Purely local edits inside a
  single file do not need a separate consumer task — do not over-split or invent
  dependencies for local changes.

Any contract-changing task's **Acceptance criteria** MUST include: "tsc/build pass and no
dangling references to the changed or removed symbols remain anywhere in the repo".

## Self-check before returning

Silently re-read your own task list and verify, then fix the plan if any check fails:
1. Every contract change has coverage for ALL its consumers (same task or a dependent task).
2. No task removes or renames a definition while leaving references to it elsewhere.
3. The dependency graph reflects real relationships: consumers depend on the task that
   changes what they consume; tasks touching the same shared module are ordered.
4. Applied in dependency order, the plan leaves the repository compiling at the end.
Then output the final markdown only.

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
