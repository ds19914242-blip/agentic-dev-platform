from orchestrator.failure_memory import ingest_validation_failure
from orchestrator.llm_metrics import finish_metrics
from orchestrator.memory_store import ingest_run
from orchestrator.pr_creator import create_pr, has_changes


def finalize_autonomous_run(
    product_name,
    repo_path,
    run_dir,
    run,
    graph,
    feature,
    validation_ok,
    manual_verification_required,
    confidence,
    confidence_path,
):
    if manual_verification_required:
        run.status("manual_verification_required")
        run.event("Run requires manual verification before task completion")
    else:
        run.status("ready_for_pr")

    (run_dir / "execution-graph.md").write_text(graph.to_markdown())
    run.artifact("execution-graph.md", stage="planning")

    if validation_ok and has_changes(repo_path):
        safe_branch = "agentic/" + feature.lower().replace(" ", "-")[:50]
        safe_branch = "".join(ch for ch in safe_branch if ch.isalnum() or ch in "-_/")
        commit_message = feature[:80]

        pr_url = create_pr(
            repo_path=repo_path,
            branch_name=safe_branch,
            commit_message=commit_message,
            body=f"Created by Agentic Dev Platform run: {run_dir}",
        )

        if pr_url:
            (run_dir / "pull-request.md").write_text(f"# Pull Request\n\n{pr_url}\n")
            run.artifact("pull-request.md", stage="pr")
            run.status("pr_created")
            run.event(f"Pull request created: {pr_url}")

    finish_metrics(run_dir)

    print(f"Autonomous run complete: {run_dir}")
    print(f"Validation: {'passed' if validation_ok else 'failed'}")
    print(f"Review: {run_dir / 'post-run-review.md'}")
    print(f"Confidence: {confidence_path}")

    try:
        ingest_validation_failure(product_name, run_dir)
        ingest_run(product_name, run_dir)
        run.event("Run memory ingested")
    except Exception as err:
        run.event(f"Run memory ingestion failed: {err}")

    print(f"Confidence status: {confidence['status']}")
