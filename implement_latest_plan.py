# DEPRECATED ENTRYPOINT
#
# This file belongs to an older workflow path.
# It is kept temporarily for compatibility while the v0.4 architecture stabilizes.
# Do not extend this file. Prefer agentic.py + orchestrator/workflows + orchestrator/services.
#

from pathlib import Path

from orchestrator.product_registry import load_product_config
from orchestrator.approved_plan import load_approved_plan
from orchestrator.claude_executor import run_claude
from orchestrator.claude_response import save_claude_response
from orchestrator.execution_result import record_execution_result
from orchestrator.run_status import write_status, append_event


def latest_run():
    runs = sorted(p for p in Path("runs").glob("feature-*") if p.is_dir())

    if not runs:
        raise RuntimeError("No feature runs found")

    return runs[-1]


def main():
    product_name = input("Product name: ").strip()

    product = load_product_config(product_name)
    repo_path = product["repo_path"]
    run_dir = latest_run()

    approved_plan = load_approved_plan(run_dir)

    prompt = f"""# Implement Approved Plan

You are executing an approved implementation plan.

Do not redesign the solution.
Do not re-analyze broadly.
Follow the approved plan exactly.

You are allowed to modify files.

After implementation:
- run npx tsc --noEmit if this is a TypeScript project
- summarize changed files
- summarize risks
- stop after implementation and validation

# Approved Plan

{approved_plan}
"""

    print(f"Implementing approved plan for run: {run_dir}")

    write_status(run_dir, "implementing_approved_plan")
    append_event(run_dir, "Implementation of approved plan started")

    response = run_claude(
        repo_path=repo_path,
        prompt=prompt,
        allow_writes=True,
        max_turns=8,
    )

    save_claude_response(run_dir, response)
    append_event(run_dir, "Claude implementation response recorded")

    record_execution_result(
        run_dir=run_dir,
        repo_path=repo_path,
        summary="Claude implemented approved plan.",
    )

    write_status(run_dir, "implemented_with_possible_turn_limit")
    append_event(run_dir, "Approved plan implementation recorded")

    print(f"Implementation complete: {run_dir}")
    print(f"Claude response: {run_dir / 'claude-response.md'}")
    print(f"Implementation result: {run_dir / 'implementation.md'}")


if __name__ == "__main__":
    main()
