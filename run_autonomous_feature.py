from pathlib import Path

from orchestrator.repository_state import ensure_clean_repo
from orchestrator.planner_agent import create_plan
from orchestrator.llm_planner_agent import create_llm_plan
from orchestrator.architect_agent import create_architecture_review
from orchestrator.qa_agent import create_qa_plan
from orchestrator.agent_context import AgentContext
from orchestrator.execution_graph import ExecutionGraph
from orchestrator.prompt_builder import build_feature_prompt
from orchestrator.run_manager import write_run_files
from orchestrator.claude_executor import run_claude_from_file, run_claude
from orchestrator.claude_response import save_claude_response
from orchestrator.approved_plan import save_approved_plan, load_approved_plan
from orchestrator.execution_result import record_execution_result
from orchestrator.post_run_review import create_post_run_review
from orchestrator.security_gate import evaluate_security_gate, write_security_report
from orchestrator.confidence_gate import write_confidence_report
from orchestrator.graph_runtime import GraphRuntime
from orchestrator.validation_runner import run_validators, write_validation_report
from orchestrator.test_generator import generate_tests
from orchestrator.manual_verification import write_manual_verification
from orchestrator.replanner_agent import run_replanner
from orchestrator.reviewer_agent import run_reviewer
from orchestrator.run_context import update_run_context
from orchestrator.llm_metrics import finish_metrics
from orchestrator.run_artifacts import register_artifacts, register_artifact
from orchestrator.pr_creator import create_pr, has_changes
from orchestrator.run_decision import decide_after_planning, decide_after_security, decide_after_confidence, write_decision
from orchestrator.failure_memory import ingest_validation_failure
from orchestrator.memory_store import ingest_run
from orchestrator.work_item_analyst import analyze_work_item
from orchestrator.services.autonomous_preflight_service import prepare_autonomous_run
from orchestrator.services.autonomous_run_service import (
    apply_planner_selected_files,
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

    agent_context = AgentContext()

    plan = create_llm_plan(repo_path, feature, affected, repo_map_text)
    agent_context.set("plan", plan)
    update_run_context(run_dir, plan=plan, affected_files=affected)
    graph_v2.complete("planning", artifacts=["plan.md"])
    graph_v2.write()

    architecture_review = create_architecture_review(
        feature,
        affected,
        repo_map_text,
        agent_context.get("plan"),
    )
    agent_context.set("architecture_review", architecture_review)
    graph_v2.complete("architecture", artifacts=["architecture-review.md"])
    graph_v2.write()

    qa_plan = create_qa_plan(
        feature,
        affected,
        agent_context.get("plan"),
        agent_context.get("architecture_review"),
    )
    agent_context.set("qa_plan", qa_plan)
    graph_v2.complete("qa", artifacts=["qa-plan.md"])
    graph_v2.write()

    graph = ExecutionGraph()
    for node_id, name in [
        ("repository_scan", "Scan repository"),
        ("repository_intelligence", "Build repository map"),
        ("affected_files", "Detect affected files"),
        ("planning", "Create implementation plan"),
        ("architecture_review", "Create architecture review"),
        ("qa_plan", "Create QA plan"),
        ("prompt", "Create Claude prompt"),
        ("claude_plan", "Run Claude planning"),
        ("approved_plan", "Approve plan"),
        ("implementation", "Implement approved plan"),
        ("validation", "Validate implementation"),
        ("post_run_review", "Create post run review"),
    ]:
        graph.add_node(node_id, name)

    for node_id in [
        "repository_scan",
        "repository_intelligence",
        "affected_files",
        "planning",
        "architecture_review",
        "qa_plan",
    ]:
        graph.mark_completed(node_id)

    plan_prompt = build_feature_prompt(
        feature,
        repo_path,
        affected,
        context,
        mode="plan_only",
    )

    status_before = git_status(repo_path)

    write_run_files(
        run_dir,
        feature,
        repo_path,
        files,
        affected,
        status_before,
        plan_prompt,
    )

    (run_dir / "repository-map.md").write_text(repo_map_text)
    (run_dir / "import-map.md").write_text(import_map_text)
    (run_dir / "plan.md").write_text(plan)
    register_artifacts(run_dir, [
        "repository-map.md",
        "import-map.md",
        "plan.md",
    ], stage="planning")

    affected, planner_selected_files = apply_planner_selected_files(
        run_dir,
        plan,
        files,
        affected,
        run,
    )

    security = evaluate_security_gate(affected)

    (run_dir / "affected-files.md").write_text(
        "# Affected Files\n\n" + "\n".join(f"- {f}" for f in affected) + "\n"
    )

    (run_dir / "architecture-review.md").write_text(architecture_review)
    (run_dir / "qa-plan.md").write_text(qa_plan)
    write_security_report(run_dir, security)
    run.artifact("affected-files.md", stage="affected_files")
    run.artifact("architecture-review.md", stage="architecture")
    run.artifact("qa-plan.md", stage="qa")
    register_artifacts(run_dir, ["security-gate.md", "security-gate.json"], stage="security")
    update_run_context(run_dir, security=security)
    graph_v2.complete("security", artifacts=["security-gate.md", "security-gate.json"])
    graph_v2.write()
    (run_dir / "agent-context.md").write_text(agent_context.to_markdown())
    run.artifact("agent-context.md", stage="planning")

    graph.mark_completed("prompt")
    (run_dir / "execution-graph.md").write_text(graph.to_markdown())
    run.artifact("execution-graph.md", stage="planning")

    # MVP mode: Security Gate is advisory only.
    # It writes security-gate.md / security-gate.json, but never blocks execution.
    run.event(f"Security advisory: {security['status']}")

    run.status("planning_with_claude")
    run.event("Claude planning started")

    claude_plan_response = run_claude_from_file(
        repo_path,
        run_dir / "claude-prompt.md",
        allow_writes=False,
    )

    save_claude_response(run_dir, claude_plan_response)
    run.artifact("claude-response.md", stage="claude_plan")
    graph.mark_completed("claude_plan")
    run.event("Claude planning response recorded")
    graph_v2.complete("claude_plan", artifacts=["claude-response.md"])
    graph_v2.write()

    planning_decision = decide_after_planning(run_dir)
    write_decision(run_dir, "planning", planning_decision)

    if planning_decision["decision"] == "stop":
        run.status(planning_decision["status"])
        run.event(f"Stopped after planning: {planning_decision['reason']}")
        print(f"Run stopped after planning: {planning_decision['status']}")
        return

    security_decision = decide_after_security(run_dir)
    write_decision(run_dir, "security", security_decision)
    run.event(f"Security decision advisory: {security_decision['status']}")

    save_approved_plan(run_dir, claude_plan_response)
    run.artifact("approved-plan.md", stage="approved_plan")
    graph.mark_completed("approved_plan")
    run.status("plan_approved")
    run.event("Plan automatically approved")
    graph_v2.complete("approved_plan", artifacts=["approved-plan.md"])
    graph_v2.write()

    approved_plan = load_approved_plan(run_dir)

    implementation_prompt = f"""# Implement Approved Plan

You are executing an approved implementation plan.

Do not redesign the solution.
Follow the approved plan.

You are allowed to modify files.

After implementation:
- run npx tsc --noEmit if this is a TypeScript project
- summarize changed files
- summarize risks

# Approved Plan

{approved_plan}
"""

    run.status("implementing")
    run.event("Claude implementation started")

    implementation_response = run_claude(
        repo_path=repo_path,
        prompt=implementation_prompt,
        allow_writes=True,
        max_turns=15,
    )

    (run_dir / "claude-implementation-response.md").write_text(
        "# Claude Implementation Response\n\n" + implementation_response
    )
    run.artifact("claude-implementation-response.md", stage="implementation")

    graph.mark_completed("implementation")
    run.event("Claude implementation response recorded")
    graph_v2.complete("implementation", artifacts=["claude-implementation-response.md"])
    graph_v2.write()

    record_execution_result(
        run_dir=run_dir,
        repo_path=repo_path,
        summary="Autonomous feature implementation completed.",
    )

    run.status("generating_tests")
    run.event("Test generation started")

    test_generation_response = generate_tests(
        repo_path=repo_path,
        feature=feature,
        test_plan=qa_plan,
        capabilities=product.get("capabilities", {}),
    )

    (run_dir / "test-generation.md").write_text(
        "# Test Generation Result\n\n" + test_generation_response
    )
    run.artifact("test-generation.md", stage="test_generation")

    manual_verification_required = write_manual_verification(
        run_dir,
        feature,
        test_generation_response,
    )
    run.artifact("manual-verification.md", stage="test_generation")
    run.artifact("manual-verification.json", stage="test_generation")

    if manual_verification_required:
        run.event("Manual verification required")
    else:
        run.event("Test generation completed")

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
    else:
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
            update_run_context(run_dir, validation_passed=validation_ok, replan_attempts=replan_attempt + 1)

            if validation_ok:
                graph.mark_completed("validation")
                run.status("validated_after_replan")
                run.event("Validation passed after replanning")
                graph_v2.complete("validation", artifacts=["validation.md", "validation.json"])
                graph_v2.write()
                break

        if not validation_ok:
            run.status("validation_failed")
            run.event("Validation still failed after replanning")
            graph_v2.fail("validation", error="Validation failed after replanning", artifacts=["validation.md", "validation.json"])
            graph_v2.write()
            failure = ingest_validation_failure(product_name, run_dir)
            if failure:
                run.event(f"Failure memory recorded: {failure.get('failure_type')}")

    run.status("reviewing")
    run.event("Reviewer started")
    graph_v2.start("review")
    graph_v2.write()

    review = run_reviewer(
        run_dir=run_dir,
        repo_path=repo_path,
        feature=feature,
    )

    graph_v2.complete("review", artifacts=["review.md", "review.json", "review-response.md"])
    graph_v2.write()
    update_run_context(run_dir, review=review)

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
