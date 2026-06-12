import json
import os
from pathlib import Path

from orchestrator.bug_task_creator import create_bug_task
from orchestrator.claude_executor import run_claude
from orchestrator.llm_metrics import finish_metrics, start_metrics
from orchestrator.pr_creator import create_pr, has_changes
from orchestrator.product_registry import load_product_config
from orchestrator.repository_state import ensure_clean_repo
from orchestrator.run_artifacts import register_artifacts
from orchestrator.run_context import update_run_context
from orchestrator.run_manager import make_run_dir
from orchestrator.run_runtime import RunRuntime
from orchestrator.validation_runner import run_validators, write_validation_report


def safe_branch(prefix, title):
    branch = f"agentic/{prefix}-" + title.lower().replace(" ", "-")[:60]
    return "".join(ch for ch in branch if ch.isalnum() or ch in "-_/")


def first_title(task_text, fallback="Agentic task"):
    for line in task_text.splitlines():
        clean = line.replace("#", "").strip()
        if clean:
            return clean[:80]
    return fallback


def run_pipeline(
    product_name,
    task_path,
    pipeline,
    prompt,
    response_filename,
    prompt_filename,
    review_title,
    review,
    max_turns,
    repo_override=None,
):
    task_path = Path(task_path)
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

    start_metrics(run_dir)
    os.environ["AGENTIC_RUN_DIR"] = str(run_dir)
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

    (run_dir / prompt_filename).write_text(prompt)
    run.artifact(prompt_filename, stage="implementation")

    run.status("implementing")
    run.event(f"{pipeline} implementation started")
    graph.start("implementation")
    graph.write()

    response = run_claude(
        repo_path=repo_path,
        prompt=prompt,
        allow_writes=True,
        max_turns=max_turns,
        retries=2,
    )

    (run_dir / response_filename).write_text(f"# {review_title} Implementation Response\n\n" + response)
    run.artifact(response_filename, stage="implementation")
    graph.complete("implementation", artifacts=[prompt_filename, response_filename])
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

    (run_dir / "review.json").write_text(json.dumps(review, indent=2, ensure_ascii=False))
    (run_dir / "review.md").write_text(f"# {review_title} Review\n\nValidation passed. No blocking issues detected.\n")
    register_artifacts(run_dir, ["review.md", "review.json"], stage="review")
    graph.complete("review", artifacts=["review.md", "review.json"])
    graph.write()

    if has_changes(repo_path):
        title = first_title(task_text)
        branch = safe_branch(f"{pipeline}-{run_dir.name}", title)

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
    finish_metrics(run_dir)

    print(f"Run: {run_dir}")
    print(f"Validation: {'passed' if validation_ok else 'failed'}")
    if (run_dir / "pull-request.md").exists():
        print((run_dir / "pull-request.md").read_text())
