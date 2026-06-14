import json

from orchestrator.bug_task_creator import create_bug_task
from orchestrator.claude_executor import run_claude
from orchestrator.pr_creator import create_pr, has_changes
from orchestrator.run_artifacts import register_artifacts
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


def run_implementation_stage(
    run,
    graph,
    run_dir,
    repo_path,
    pipeline,
    prompt,
    prompt_filename,
    response_filename,
    review_title,
    max_turns,
):
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

    (run_dir / response_filename).write_text(
        f"# {review_title} Implementation Response\n\n" + response
    )
    run.artifact(response_filename, stage="implementation")
    graph.complete("implementation", artifacts=[prompt_filename, response_filename])
    graph.write()


def run_validation_stage(run, graph, run_dir, repo_path, product, task_path):
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
        graph.write()
        return True

    run.status("validation_failed")
    run.event("Validation failed")
    graph.fail(
        "validation",
        error="Validation failed",
        artifacts=["validation.md", "validation.json"],
    )
    graph.write()

    bug_task = create_bug_task(run_dir, source_task_path=task_path, reason="validation_failed")
    run.event(f"Bug task created: {bug_task}")

    print(f"Run: {run_dir}")
    print("Validation: failed")
    print(f"Bug task: {bug_task}")

    raise SystemExit(1)


def run_review_stage(run, graph, run_dir, review_title, review):
    (run_dir / "review.json").write_text(json.dumps(review, indent=2, ensure_ascii=False))
    (run_dir / "review.md").write_text(
        f"# {review_title} Review\n\nValidation passed. No blocking issues detected.\n"
    )

    register_artifacts(run_dir, ["review.md", "review.json"], stage="review")
    graph.complete("review", artifacts=["review.md", "review.json"])
    graph.write()


def run_pull_request_stage(run, graph, run_dir, repo_path, task_text, pipeline):
    if not has_changes(repo_path):
        run.status("done_no_pr")
        run.event("No changes detected")
        graph.skip("pr")
        graph.write()
        return

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

    graph.write()
