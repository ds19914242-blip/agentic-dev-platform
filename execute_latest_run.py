# DEPRECATED ENTRYPOINT
#
# This file belongs to an older workflow path.
# It is kept temporarily for compatibility while the v0.4 architecture stabilizes.
# Do not extend this file. Prefer agentic.py + orchestrator/workflows + orchestrator/services.
#

from pathlib import Path

from orchestrator.product_registry import load_product_config
from orchestrator.claude_executor import run_claude_from_file
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
    allow_writes_input = input("Allow Claude to modify files? [y/N]: ").strip().lower()
    allow_writes = allow_writes_input == "y"

    product = load_product_config(product_name)
    repo_path = product["repo_path"]

    run_dir = latest_run()
    prompt_path = run_dir / "claude-prompt.md"

    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt not found: {prompt_path}")

    print(f"Executing run: {run_dir}")
    print(f"Using repo: {repo_path}")

    write_status(run_dir, "executing")
    append_event(run_dir, "Claude execution started")

    response = run_claude_from_file(repo_path, prompt_path, allow_writes=allow_writes)

    save_claude_response(run_dir, response)
    append_event(run_dir, "Claude response recorded")

    record_execution_result(
        run_dir=run_dir,
        repo_path=repo_path,
        summary="Claude Code execution completed automatically.",
    )

    write_status(run_dir, "implemented")
    append_event(run_dir, "Implementation result recorded")

    print(f"Execution complete: {run_dir}")
    print(f"Claude response: {run_dir / 'claude-response.md'}")
    print(f"Implementation result: {run_dir / 'implementation.md'}")


if __name__ == "__main__":
    main()
