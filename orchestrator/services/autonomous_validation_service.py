from orchestrator.failure_memory import ingest_validation_failure
from orchestrator.replanner_agent import run_replanner
from orchestrator.run_artifacts import register_artifacts
from orchestrator.run_context import update_run_context
from orchestrator.validation_runner import run_validators, write_validation_report


def run_validation_with_replan(
    product_name,
    product,
    repo_path,
    run_dir,
    run,
    graph,
    graph_v2,
    feature,
):
    validation_results = run_validators(repo_path, product.get("validators", []))
    _, validation_ok = write_validation_report(run_dir, validation_results)
    register_artifacts(run_dir, ["validation.md", "validation.json"], stage="validation")
    update_run_context(run_dir, validation_passed=validation_ok)

    if validation_ok:
        graph.mark_completed("validation")
        run.status("validated")
        run.event("Validation passed")
        graph_v2.complete("validation", artifacts=["validation.md", "validation.json"])
        graph_v2.skip("replanning")
        graph_v2.write()
        return True

    run.status("validation_failed")
    run.event("Validation failed")
    graph_v2.fail("validation", error="Validation failed", artifacts=["validation.md", "validation.json"])
    graph_v2.write()

    max_replans = 1

    for replan_attempt in range(max_replans):
        run.status("replanning")
        run.event(f"Replanner started, attempt {replan_attempt + 1}")
        graph_v2.start("replanning")
        graph_v2.write()

        run_replanner(
            run_dir=run_dir,
            repo_path=repo_path,
            feature=feature,
        )

        graph_v2.complete("replanning", artifacts=["replan-prompt.md", "replan-response.md"])
        graph_v2.write()

        validation_results = run_validators(repo_path, product.get("validators", []))
        _, validation_ok = write_validation_report(run_dir, validation_results)
        register_artifacts(run_dir, ["validation.md", "validation.json"], stage="validation")
        update_run_context(
            run_dir,
            validation_passed=validation_ok,
            replan_attempts=replan_attempt + 1,
        )

        if validation_ok:
            graph.mark_completed("validation")
            run.status("validated_after_replan")
            run.event("Validation passed after replanning")
            graph_v2.complete("validation", artifacts=["validation.md", "validation.json"])
            graph_v2.write()
            return True

    run.status("validation_failed")
    run.event("Validation still failed after replanning")
    graph_v2.fail(
        "validation",
        error="Validation failed after replanning",
        artifacts=["validation.md", "validation.json"],
    )
    graph_v2.write()

    failure = ingest_validation_failure(product_name, run_dir)
    if failure:
        run.event(f"Failure memory recorded: {failure.get('failure_type')}")

    return False
