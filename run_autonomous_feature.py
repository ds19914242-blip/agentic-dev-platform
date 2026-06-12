from pathlib import Path

from orchestrator.repository_state import ensure_clean_repo
from orchestrator.graph_runtime import GraphRuntime
from orchestrator.run_context import update_run_context
from orchestrator.llm_metrics import finish_metrics
from orchestrator.run_artifacts import register_artifacts, register_artifact
from orchestrator.pr_creator import create_pr, has_changes
from orchestrator.run_decision import decide_after_confidence, write_decision
from orchestrator.failure_memory import ingest_validation_failure
from orchestrator.memory_store import ingest_run
from orchestrator.work_item_analyst import analyze_work_item
from orchestrator.services.autonomous_preflight_service import prepare_autonomous_run
from orchestrator.services.autonomous_artifacts_service import (
    initialize_legacy_execution_graph,
    write_planning_artifacts,
    write_security_and_agent_artifacts,
)
from orchestrator.services.autonomous_claude_planning_service import run_claude_planning_and_approve
from orchestrator.services.autonomous_implementation_service import run_autonomous_implementation_and_tests
from orchestrator.services.autonomous_review_service import run_autonomous_review_and_confidence
from orchestrator.services.autonomous_validation_service import run_validation_with_replan
from orchestrator.services.autonomous_planning_service import run_autonomous_planning
from orchestrator.services.autonomous_run_service import (
    create_autonomous_run,
    initialize_autonomous_graph,
    prepare_repository_context,
)

import subprocess
import os


def git_status(repo_path):
    result = subprocess.run(
        ["git", "status", "--short"],
        cwd=repo_path,
        text=True,
        capture_output=True,
    )
    return result.stdout.strip()




def main():
    product_name = input("Product name: ").strip()
    feature = input("Feature request: ").strip()

    preflight = prepare_autonomous_run(product_name, feature)
    product = preflight["product"]
    repo_path = preflight["repo_path"]
    work_item = preflight["work_item"]
    classification = preflight["classification"]
    classification_text = preflight["classification_text"]

    if classification["route"] == "DECOMPOSE_FIRST":
        print("Request should be decomposed first.")
        print("Run:")
        print("python3 decompose_feature.py")
        print()
        print(classification_text)
        return

    if classification["route"] == "NEEDS_HUMAN_REVIEW":
        print("Request needs human review before execution.")
        print()
        print(classification_text)
        return

    ensure_clean_repo(repo_path)

    run_state = create_autonomous_run(
        product_name=product_name,
        product=product,
        repo_path=repo_path,
        feature=feature,
        work_item=work_item,
    )
    run_dir = run_state["run_dir"]
    run = run_state["run"]
    graph_v2 = run_state["graph_v2"]
    memory_context = run_state["memory_context"]
    initialize_autonomous_graph(graph_v2)

    print(f"Run: {run_dir}")
    print(f"Repo: {repo_path}")

    repo_context = prepare_repository_context(repo_path, feature, memory_context)
    files = repo_context["files"]
    repo_map_text = repo_context["repo_map_text"]
    import_map_text = repo_context["import_map_text"]
    affected = repo_context["affected"]
    context = repo_context["context"]

    graph_v2.complete("repo_scan")
    graph_v2.complete("repo_intelligence")
    graph_v2.complete("affected_files")
    graph_v2.write()

    planning_state = run_autonomous_planning(
        run_dir=run_dir,
        run=run,
        graph_v2=graph_v2,
        repo_path=repo_path,
        feature=feature,
        files=files,
        affected=affected,
        repo_map_text=repo_map_text,
    )
    agent_context = planning_state["agent_context"]
    plan = planning_state["plan"]
    architecture_review = planning_state["architecture_review"]
    qa_plan = planning_state["qa_plan"]
    affected = planning_state["affected"]
    planner_selected_files = planning_state["planner_selected_files"]

    graph = initialize_legacy_execution_graph()

    status_before = git_status(repo_path)

    write_planning_artifacts(
        run_dir=run_dir,
        run=run,
        graph=graph,
        feature=feature,
        repo_path=repo_path,
        files=files,
        affected=affected,
        context=context,
        status_before=status_before,
        repo_map_text=repo_map_text,
        import_map_text=import_map_text,
        plan=plan,
    )

    security = write_security_and_agent_artifacts(
        run_dir=run_dir,
        run=run,
        graph_v2=graph_v2,
        affected=affected,
        architecture_review=architecture_review,
        qa_plan=qa_plan,
        agent_context=agent_context,
    )

    # MVP mode: Security Gate is advisory only.
    # It writes security-gate.md / security-gate.json, but never blocks execution.
    run.event(f"Security advisory: {security['status']}")

    claude_planning_state = run_claude_planning_and_approve(
        repo_path=repo_path,
        run_dir=run_dir,
        run=run,
        graph=graph,
        graph_v2=graph_v2,
    )

    if claude_planning_state["stopped"]:
        return

    manual_verification_required = run_autonomous_implementation_and_tests(
        product=product,
        repo_path=repo_path,
        run_dir=run_dir,
        run=run,
        graph=graph,
        graph_v2=graph_v2,
        feature=feature,
        qa_plan=qa_plan,
    )

    validation_ok = run_validation_with_replan(
        product_name=product_name,
        product=product,
        repo_path=repo_path,
        run_dir=run_dir,
        run=run,
        graph=graph,
        graph_v2=graph_v2,
        feature=feature,
    )

    review_state = run_autonomous_review_and_confidence(
        run_dir=run_dir,
        repo_path=repo_path,
        run=run,
        graph=graph,
        graph_v2=graph_v2,
        feature=feature,
    )
    confidence_path = review_state["confidence_path"]
    confidence = review_state["confidence"]

    confidence_decision = decide_after_confidence(run_dir)
    write_decision(run_dir, "confidence", confidence_decision)

    # MVP mode: Confidence Gate is advisory only.
    # It writes confidence.md / confidence.json / decision-confidence.*, but does not block PR creation.
    run.event(f"Confidence advisory: {confidence_decision['status']}")

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


if __name__ == "__main__":
    main()
