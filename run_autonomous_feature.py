from pathlib import Path

from orchestrator.product_registry import load_product_config
from orchestrator.repository_state import ensure_clean_repo
from orchestrator.repository_scanner import scan_repo
from orchestrator.repository_intelligence import build_repository_map, format_repository_map
from orchestrator.import_analyzer import analyze_imports, format_import_map
from orchestrator.affected_file_detector import detect_affected_files
from orchestrator.context_builder import read_context
from orchestrator.planner_agent import create_plan
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
from orchestrator.confidence_gate import write_confidence_report

import subprocess


def git_status(repo_path):
    result = subprocess.run(
        ["git", "status", "--short"],
        cwd=repo_path,
        text=True,
        capture_output=True,
    )
    return result.stdout.strip()


def validate_typescript(run_dir, repo_path):
    result = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        cwd=repo_path,
        text=True,
        capture_output=True,
    )

    validation_path = run_dir / "validation.md"
    status = "passed" if result.returncode == 0 else "failed"

    validation_path.write_text(f"""# Validation Result

## Command

npx tsc --noEmit

## Result

{status}

## Exit Code

{result.returncode}

## STDOUT

{result.stdout}

## STDERR

{result.stderr}
""")

    return result.returncode == 0


def main():
    product_name = input("Product name: ").strip()
    feature = input("Feature request: ").strip()

    product = load_product_config(product_name)
    repo_path = product["repo_path"]

    ensure_clean_repo(repo_path)

    run_dir = make_run_dir("feature")
    write_status(run_dir, "created")
    append_event(run_dir, "Autonomous feature run created")

    print(f"Run: {run_dir}")
    print(f"Repo: {repo_path}")

    files = scan_repo(repo_path)
    repo_map = build_repository_map(files)
    repo_map_text = format_repository_map(repo_map)

    import_map = analyze_imports(repo_path, files)
    import_map_text = format_import_map(import_map)

    affected = detect_affected_files(feature, files)
    context = read_context(repo_path, affected)

    agent_context = AgentContext()

    plan = create_plan(feature, affected)
    agent_context.set("plan", plan)

    architecture_review = create_architecture_review(
        feature,
        affected,
        repo_map_text,
        agent_context.get("plan"),
    )
    agent_context.set("architecture_review", architecture_review)

    qa_plan = create_qa_plan(
        feature,
        affected,
        agent_context.get("plan"),
        agent_context.get("architecture_review"),
    )
    agent_context.set("qa_plan", qa_plan)

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
    (run_dir / "architecture-review.md").write_text(architecture_review)
    (run_dir / "qa-plan.md").write_text(qa_plan)
    (run_dir / "agent-context.md").write_text(agent_context.to_markdown())

    graph.mark_completed("prompt")
    (run_dir / "execution-graph.md").write_text(graph.to_markdown())

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

    save_approved_plan(run_dir, claude_plan_response)
    graph.mark_completed("approved_plan")
    write_status(run_dir, "plan_approved")
    append_event(run_dir, "Plan automatically approved")

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

    record_execution_result(
        run_dir=run_dir,
        repo_path=repo_path,
        summary="Autonomous feature implementation completed.",
    )

    validation_ok = validate_typescript(run_dir, repo_path)

    if validation_ok:
        graph.mark_completed("validation")
        write_status(run_dir, "validated")
        append_event(run_dir, "Validation passed")
    else:
        write_status(run_dir, "validation_failed")
        append_event(run_dir, "Validation failed")

    create_post_run_review(run_dir, repo_path)
    graph.mark_completed("post_run_review")
    append_event(run_dir, "Post run review created")

    confidence_path, confidence = write_confidence_report(run_dir)
    append_event(run_dir, f"Confidence gate: {confidence['status']}")

    if confidence["status"] == "passed":
        write_status(run_dir, "confidence_passed")
    elif confidence["status"] == "failed":
        write_status(run_dir, "confidence_failed")
    else:
        write_status(run_dir, "needs_review")

    (run_dir / "execution-graph.md").write_text(graph.to_markdown())

    print(f"Autonomous run complete: {run_dir}")
    print(f"Validation: {'passed' if validation_ok else 'failed'}")
    print(f"Review: {run_dir / 'post-run-review.md'}")
    print(f"Confidence: {confidence_path}")
    print(f"Confidence status: {confidence['status']}")


if __name__ == "__main__":
    main()
