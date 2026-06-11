from pathlib import Path

from orchestrator.product_registry import load_product_config
from orchestrator.repository_state import ensure_clean_repo
from orchestrator.repository_scanner import scan_repo
from orchestrator.repository_intelligence import build_repository_map, format_repository_map
from orchestrator.import_analyzer import analyze_imports, format_import_map
from orchestrator.affected_file_detector import detect_affected_files
from orchestrator.repository_intelligence_v2 import rank_affected_files
from orchestrator.context_builder import read_context
from orchestrator.planner_agent import create_plan
from orchestrator.llm_planner_agent import create_llm_plan
from orchestrator.architect_agent import create_architecture_review
from orchestrator.qa_agent import create_qa_plan
from orchestrator.agent_context import AgentContext
from orchestrator.execution_graph import ExecutionGraph
from orchestrator.prompt_builder import build_feature_prompt
from orchestrator.run_manager import make_run_dir, write_run_files
from orchestrator.run_status import write_status, append_event
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
from orchestrator.pr_creator import create_pr, has_changes
from orchestrator.run_decision import decide_after_planning, decide_after_security, decide_after_confidence, write_decision
from orchestrator.planner_selected_files import extract_files_from_plan, write_planner_selected_files
from orchestrator.complexity_classifier import classify_request_with_llm, parse_complexity

import subprocess


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

    product = load_product_config(product_name)
    repo_path = product["repo_path"]

    files_for_classification = scan_repo(repo_path)
    repo_map_for_classification = format_repository_map(
        build_repository_map(files_for_classification)
    )

    classification_text = classify_request_with_llm(
        repo_path,
        feature,
        repo_map_for_classification,
    )

    classification = parse_complexity(classification_text)

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

    run_dir = make_run_dir("feature")
    write_status(run_dir, "created")
    append_event(run_dir, "Autonomous feature run created")

    graph_v2 = GraphRuntime(run_dir)
    for node_id, name in [
        ("repo_state", "Check clean repository"),
        ("repo_scan", "Scan repository"),
        ("repo_intelligence", "Build repository intelligence"),
        ("affected_files", "Detect affected files"),
        ("planning", "Create plan"),
        ("architecture", "Create architecture review"),
        ("qa", "Create QA plan"),
        ("security", "Run security gate"),
        ("claude_plan", "Run Claude planning"),
        ("approved_plan", "Approve plan"),
        ("implementation", "Run Claude implementation"),
        ("validation", "Run validation"),
        ("post_review", "Create post-run review"),
        ("confidence", "Run confidence gate"),
    ]:
        graph_v2.add(node_id, name)
    graph_v2.complete("repo_state")
    graph_v2.write()

    print(f"Run: {run_dir}")
    print(f"Repo: {repo_path}")

    files = scan_repo(repo_path)
    graph_v2.complete('repo_scan')
    graph_v2.write()
    repo_map = build_repository_map(files)
    repo_map_text = format_repository_map(repo_map)
    graph_v2.complete('repo_intelligence')
    graph_v2.write()

    import_map = analyze_imports(repo_path, files)
    import_map_text = format_import_map(import_map)

    affected = rank_affected_files(feature, files) or detect_affected_files(feature, files)
    graph_v2.complete('affected_files')
    graph_v2.write()
    context = read_context(repo_path, affected)

    agent_context = AgentContext()

    plan = create_llm_plan(repo_path, feature, affected, repo_map_text)
    agent_context.set("plan", plan)
    graph_v2.complete("planning")
    graph_v2.write()

    architecture_review = create_architecture_review(
        feature,
        affected,
        repo_map_text,
        agent_context.get("plan"),
    )
    agent_context.set("architecture_review", architecture_review)
    graph_v2.complete("architecture")
    graph_v2.write()

    qa_plan = create_qa_plan(
        feature,
        affected,
        agent_context.get("plan"),
        agent_context.get("architecture_review"),
    )
    agent_context.set("qa_plan", qa_plan)
    graph_v2.complete("qa")
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

    planner_selected_files = extract_files_from_plan(plan, files)
    if planner_selected_files:
        affected = planner_selected_files

    write_planner_selected_files(run_dir, planner_selected_files)

    security = evaluate_security_gate(affected)

    (run_dir / "affected-files.md").write_text(
        "# Affected Files\n\n" + "\n".join(f"- {f}" for f in affected) + "\n"
    )

    (run_dir / "architecture-review.md").write_text(architecture_review)
    (run_dir / "qa-plan.md").write_text(qa_plan)
    write_security_report(run_dir, security)
    graph_v2.complete("security")
    graph_v2.write()
    (run_dir / "agent-context.md").write_text(agent_context.to_markdown())

    graph.mark_completed("prompt")
    (run_dir / "execution-graph.md").write_text(graph.to_markdown())

    # MVP mode: Security Gate is advisory only.
    # It writes security-gate.md / security-gate.json, but never blocks execution.
    append_event(run_dir, f"Security advisory: {security['status']}")

    write_status(run_dir, "planning_with_claude")
    append_event(run_dir, "Claude planning started")

    claude_plan_response = run_claude_from_file(
        repo_path,
        run_dir / "claude-prompt.md",
        allow_writes=False,
    )

    save_claude_response(run_dir, claude_plan_response)
    graph.mark_completed("claude_plan")
    append_event(run_dir, "Claude planning response recorded")
    graph_v2.complete("claude_plan")
    graph_v2.write()

    planning_decision = decide_after_planning(run_dir)
    write_decision(run_dir, "planning", planning_decision)

    if planning_decision["decision"] == "stop":
        write_status(run_dir, planning_decision["status"])
        append_event(run_dir, f"Stopped after planning: {planning_decision['reason']}")
        print(f"Run stopped after planning: {planning_decision['status']}")
        return

    security_decision = decide_after_security(run_dir)
    write_decision(run_dir, "security", security_decision)
    append_event(run_dir, f"Security decision advisory: {security_decision['status']}")

    save_approved_plan(run_dir, claude_plan_response)
    graph.mark_completed("approved_plan")
    write_status(run_dir, "plan_approved")
    append_event(run_dir, "Plan automatically approved")
    graph_v2.complete("approved_plan")
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

    write_status(run_dir, "implementing")
    append_event(run_dir, "Claude implementation started")

    implementation_response = run_claude(
        repo_path=repo_path,
        prompt=implementation_prompt,
        allow_writes=True,
        max_turns=15,
    )

    (run_dir / "claude-implementation-response.md").write_text(
        "# Claude Implementation Response\n\n" + implementation_response
    )

    graph.mark_completed("implementation")
    append_event(run_dir, "Claude implementation response recorded")
    graph_v2.complete("implementation")
    graph_v2.write()

    record_execution_result(
        run_dir=run_dir,
        repo_path=repo_path,
        summary="Autonomous feature implementation completed.",
    )

    write_status(run_dir, "generating_tests")
    append_event(run_dir, "Test generation started")

    test_generation_response = generate_tests(
        repo_path=repo_path,
        feature=feature,
        test_plan=qa_plan,
    )

    (run_dir / "test-generation.md").write_text(
        "# Test Generation Result\n\n" + test_generation_response
    )

    append_event(run_dir, "Test generation completed")

    validation_results = run_validators(repo_path, product.get("validators", []))
    _, validation_ok = write_validation_report(run_dir, validation_results)

    if validation_ok:
        graph.mark_completed("validation")
        write_status(run_dir, "validated")
        append_event(run_dir, "Validation passed")
        graph_v2.complete("validation")
        graph_v2.write()
    else:
        write_status(run_dir, "validation_failed")
        append_event(run_dir, "Validation failed")
        graph_v2.fail("validation")
        graph_v2.write()

    create_post_run_review(run_dir, repo_path)
    graph.mark_completed("post_run_review")
    append_event(run_dir, "Post run review created")
    graph_v2.complete("post_review")
    graph_v2.write()

    confidence_path, confidence = write_confidence_report(run_dir)
    append_event(run_dir, f"Confidence gate: {confidence['status']}")
    graph_v2.complete("confidence")
    graph_v2.write()

    confidence_decision = decide_after_confidence(run_dir)
    write_decision(run_dir, "confidence", confidence_decision)

    # MVP mode: Confidence Gate is advisory only.
    # It writes confidence.md / confidence.json / decision-confidence.*, but does not block PR creation.
    append_event(run_dir, f"Confidence advisory: {confidence_decision['status']}")
    write_status(run_dir, "ready_for_pr")

    (run_dir / "execution-graph.md").write_text(graph.to_markdown())

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
            write_status(run_dir, "pr_created")
            append_event(run_dir, f"Pull request created: {pr_url}")

    print(f"Autonomous run complete: {run_dir}")
    print(f"Validation: {'passed' if validation_ok else 'failed'}")
    print(f"Review: {run_dir / 'post-run-review.md'}")
    print(f"Confidence: {confidence_path}")
    print(f"Confidence status: {confidence['status']}")


if __name__ == "__main__":
    main()
