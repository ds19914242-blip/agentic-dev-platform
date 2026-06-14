from orchestrator.confidence_gate import write_confidence_report
from orchestrator.post_run_review import create_post_run_review
from orchestrator.run_artifacts import register_artifacts
from orchestrator.run_context import update_run_context
from orchestrator.agent_runtime.compatibility.legacy_runtime import LegacyAgentRunContext
from orchestrator.agent_runtime.compatibility.legacy_runtime import run_runtime_agent


def run_autonomous_review_and_confidence(run_dir, repo_path, run, graph, graph_v2, feature):
    run.status("reviewing")
    run.event("Reviewer started")
    graph_v2.start("review")
    graph_v2.write()

    reviewer_result = run_runtime_agent(
        "reviewer",
        LegacyAgentRunContext(
            agent="reviewer",
            run_dir=str(run_dir),
            repo_path=repo_path,
            feature=feature,
        ),
    )
    review = reviewer_result.metadata.get("review", {})

    graph_v2.complete("review", artifacts=["review.md", "review.json", "review-response.md"])
    graph_v2.write()

    create_post_run_review(run_dir, repo_path)
    run.artifact("post-run-review.md", stage="post_review")
    graph.mark_completed("post_run_review")
    run.event("Post run review created")
    graph_v2.complete("post_review", artifacts=["post-run-review.md"])
    graph_v2.write()

    confidence_path, confidence = write_confidence_report(run_dir)
    register_artifacts(run_dir, ["confidence.md", "confidence.json"], stage="confidence")
    update_run_context(run_dir, confidence=confidence)
    run.event(f"Confidence gate: {confidence['status']}")
    graph_v2.complete("confidence", artifacts=["confidence.md", "confidence.json"])
    graph_v2.write()

    return {
        "review": review,
        "confidence_path": confidence_path,
        "confidence": confidence,
    }
