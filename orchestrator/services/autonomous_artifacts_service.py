from orchestrator.execution_graph import ExecutionGraph
from orchestrator.prompt_builder import build_feature_prompt
from orchestrator.run_artifacts import register_artifacts
from orchestrator.run_context import update_run_context
from orchestrator.run_manager import write_run_files
from orchestrator.security_gate import evaluate_security_gate, write_security_report


def initialize_legacy_execution_graph():
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

    return graph


def write_planning_artifacts(
    run_dir,
    run,
    graph,
    feature,
    repo_path,
    files,
    affected,
    context,
    status_before,
    repo_map_text,
    import_map_text,
    plan,
):
    plan_prompt = build_feature_prompt(
        feature,
        repo_path,
        affected,
        context,
        mode="plan_only",
    )

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

    graph.mark_completed("prompt")
    (run_dir / "execution-graph.md").write_text(graph.to_markdown())
    run.artifact("execution-graph.md", stage="planning")


def write_security_and_agent_artifacts(
    run_dir,
    run,
    graph_v2,
    affected,
    architecture_review,
    qa_plan,
    agent_context,
):
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

    run.event(f"Security advisory: {security['status']}")

    return security
