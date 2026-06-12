from orchestrator.approved_plan import load_approved_plan
from orchestrator.claude_executor import run_claude
from orchestrator.execution_result import record_execution_result
from orchestrator.manual_verification import write_manual_verification
from orchestrator.test_generator import generate_tests


def run_autonomous_implementation_and_tests(
    product,
    repo_path,
    run_dir,
    run,
    graph,
    graph_v2,
    feature,
    qa_plan,
):
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

    return manual_verification_required
