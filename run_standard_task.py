import json
import os
import sys
from pathlib import Path

from orchestrator.product_registry import load_product_config
from orchestrator.repository_state import ensure_clean_repo
from orchestrator.claude_executor import run_claude
from orchestrator.validation_runner import run_validators, write_validation_report
from orchestrator.pr_creator import create_pr, has_changes
from orchestrator.run_manager import make_run_dir
from orchestrator.run_runtime import RunRuntime
from orchestrator.run_context import update_run_context
from orchestrator.run_artifacts import register_artifacts
from orchestrator.bug_task_creator import create_bug_task


def safe_branch(prefix, title):
    branch = f"agentic/{prefix}-" + title.lower().replace(" ", "-")[:60]
    return "".join(ch for ch in branch if ch.isalnum() or ch in "-_/")


def first_title(task_text):
    for line in task_text.splitlines():
        clean = line.replace("#", "").strip()
        if clean:
            return clean[:80]
    return "Agentic task"


def build_standard_prompt(task_text, pipeline):
    if pipeline == "standard_bugfix":
        intro = """You are fixing a known bug.

Steps:
1. Identify the likely root cause.
2. Make the smallest safe fix.
3. Do not redesign unrelated code.
4. Preserve existing behavior except for the bug.
"""
    else:
        intro = """You are implementing a bounded task.

Steps:
1. Make a short light plan internally.
2. Implement the smallest safe change.
3. Prefer suggested files.
4. Do not redesign unrelated code.
"""

    return f"""# Standard Task Execution

{intro}

Safety rules:
- Do not touch auth, billing, secrets, database schema, or deployment config unless explicitly required.
- Keep changes minimal.
- If no code change is needed, say so clearly.

Task:

{task_text}
"""


def main():
    if len(sys.argv) < 4:
        raise SystemExit("Usage: python3 run_standard_task.py <product> <task-file> <pipeline> [repo-path]")

    product_name = sys.argv[1]
    task_path = Path(sys.argv[2])
    pipeline = sys.argv[3]
    repo_override = sys.argv[4] if len(sys.argv) > 4 else None

    if pipeline not in {"standard", "standard_bugfix"}:
        raise SystemExit(f"Unsupported standard pipeline: {pipeline}")

    task_text = task_path.read_text(errors="ignore")

    product = load_product_config(product_name)
    repo_path = repo_override or os.environ.get("AGENTIC_REPO_PATH_OVERRIDE") or product["repo_path"]
    product["repo_path"] = repo_path

    ensure_clean_repo(repo_path)

    run_dir = make_run_dir(pipeline.replace("_", "-"))
    run = RunRuntime(
        run_dir,
        product=product_name,
        request=task_text,
        run_type=pipeline,
    )
    graph = run.graph

    for node_id, name in [
        ("implementation", f"Run {pipeline} implementation"),
        ("validation", "Run validation"),
        ("review", "Run lightweight review"),
        ("pr", "Create pull request"),
    ]:
        graph.add(node_id, name)
    graph.write()

    run.status("created")
    run.event(f"{pipeline} run created")
    update_run_context(
        run_dir,
        product=product_name,
        repo_path=repo_path,
        task_file=str(task_path),
        pipeline=pipeline,
    )

    profile = {
        "pipeline": pipeline,
        "task_file": str(task_path),
    }
    (run_dir / "task-profile.json").write_text(json.dumps(profile, indent=2, ensure_ascii=False))
    run.artifact("task-profile.json", stage="implementation")

    prompt = build_standard_prompt(task_text, pipeline)
    (run_dir / "standard-prompt.md").write_text(prompt)
    run.artifact("standard-prompt.md", stage="implementation")

    run.status("implementing")
    run.event(f"{pipeline} implementation started")
    graph.start("implementation")
    graph.write()

    response = run_claude(
        repo_path=repo_path,
        prompt=prompt,
        allow_writes=True,
        max_turns=12,
        retries=2,
    )

    (run_dir / "standard-response.md").write_text("# Standard Implementation Response\n\n" + response)
    run.artifact("standard-response.md", stage="implementation")
    graph.complete("implementation", artifacts=["standard-prompt.md", "standard-response.md"])
    graph.write()

    run.status("validating")
    run.event("Validation started")
    graph.start("validation")
    graph.write()

    validation_results = run_validators(repo_path, product.get("validators", []))
    _, validation_ok = write_validation_report(run_dir, validation_results)
    register_artifacts(run_dir, ["validation.md", "validation.json"], stage="validation")

    if validation_ok:
        run.status("validated")
        run.event("Validation passed")
        graph.complete("validation", artifacts=["validation.md", "validation.json"])
    else:
        run.status("validation_failed")
        run.event("Validation failed")
        graph.fail("validation", error="Validation failed", artifacts=["validation.md", "validation.json"])
        graph.write()

        bug_task = create_bug_task(run_dir, source_task_path=task_path, reason="validation_failed")
        run.event(f"Bug task created: {bug_task}")

        print(f"Run: {run_dir}")
        print("Validation: failed")
        print(f"Bug task: {bug_task}")
        raise SystemExit(1)

    graph.write()

    review = {
        "requirements_covered": True,
        "scope_creep": False,
        "architecture_risk": "low" if pipeline == "standard" else "medium",
        "blocking_issues": [],
        "summary": f"{pipeline} lightweight review: validation passed.",
    }

    (run_dir / "review.json").write_text(json.dumps(review, indent=2, ensure_ascii=False))
    (run_dir / "review.md").write_text(f"# {pipeline} Review\n\nValidation passed. No blocking issues detected.\n")
    register_artifacts(run_dir, ["review.md", "review.json"], stage="review")
    graph.complete("review", artifacts=["review.md", "review.json"])
    graph.write()

    if has_changes(repo_path):
        title = first_title(task_text)
        branch = safe_branch(pipeline, title)

        pr_url = create_pr(
            repo_path=repo_path,
            branch_name=branch,
            commit_message=title,
            body=f"Created by Agentic Dev Platform {pipeline} run: {run_dir}",
        )

        if pr_url:
            (run_dir / "pull-request.md").write_text(f"# Pull Request\n\n{pr_url}\n")
            run.artifact("pull-request.md", stage="pr")
            run.status("pr_created")
            run.event(f"Pull request created: {pr_url}")
            graph.complete("pr", artifacts=["pull-request.md"])
        else:
            run.status("done_no_pr")
            run.event("No pull request created")
            graph.skip("pr")
    else:
        run.status("done_no_pr")
        run.event("No changes detected")
        graph.skip("pr")

    graph.write()

    print(f"Run: {run_dir}")
    print(f"Validation: {'passed' if validation_ok else 'failed'}")
    if (run_dir / "pull-request.md").exists():
        print((run_dir / "pull-request.md").read_text())


if __name__ == "__main__":
    main()
