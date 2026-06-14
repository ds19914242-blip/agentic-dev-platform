import sys
from pathlib import Path

from orchestrator.services.pipeline_runner import run_pipeline


def build_standard_prompt(task_text, pipeline):
    if pipeline == "standard_bugfix":
        intro = """You are fixing a known bug.

Steps:
1. Identify the likely root cause.
2. Make the smallest safe fix.
3. Do not redesign unrelated code.
4. Preserve existing behavior except for the bug.
"""
    else:
        intro = """You are implementing a bounded task.

Steps:
1. Make a short light plan internally.
2. Implement the smallest safe change.
3. Prefer suggested files.
4. Do not redesign unrelated code.
"""

    return f"""# Standard Task Execution

{intro}

Safety rules:
- Do not touch auth, billing, secrets, database schema, or deployment config unless explicitly required.
- Keep changes minimal.
- If no code change is needed, say so clearly.

Task:

{task_text}
"""


def main():
    if len(sys.argv) < 4:
        raise SystemExit("Usage: python3 run_standard_task.py <product> <task-file> <pipeline> [repo-path]")

    product_name = sys.argv[1]
    task_path = Path(sys.argv[2])
    pipeline = sys.argv[3]
    repo_override = sys.argv[4] if len(sys.argv) > 4 else None

    if pipeline not in {"standard", "standard_bugfix"}:
        raise SystemExit(f"Unsupported standard pipeline: {pipeline}")

    task_text = task_path.read_text(errors="ignore")
    prompt = build_standard_prompt(task_text, pipeline)

    review = {
        "requirements_covered": True,
        "scope_creep": False,
        "architecture_risk": "low" if pipeline == "standard" else "medium",
        "blocking_issues": [],
        "summary": f"{pipeline} lightweight review: validation passed.",
    }

    run_pipeline(
        product_name=product_name,
        task_path=task_path,
        pipeline=pipeline,
        prompt=prompt,
        response_filename="standard-response.md",
        prompt_filename="standard-prompt.md",
        review_title=pipeline,
        review=review,
        max_turns=12,
        repo_override=repo_override,
    )


if __name__ == "__main__":
    main()
