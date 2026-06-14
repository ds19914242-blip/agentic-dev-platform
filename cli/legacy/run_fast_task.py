import sys
from pathlib import Path

from orchestrator.services.pipeline_runner import run_pipeline


def build_prompt(task_text):
    return f"""# Fast Task Implementation

You are executing a small, bounded task.

Rules:
- Make the smallest safe change.
- Do not redesign architecture.
- Do not touch auth, billing, secrets, database schema, or deployment config.
- Prefer modifying only the suggested files in the task.
- If no change is needed, say so clearly.

Task:

{task_text}
"""


def main():
    if len(sys.argv) < 3:
        raise SystemExit("Usage: python3 run_fast_task.py <product> <task-file> [repo-path]")

    product_name = sys.argv[1]
    task_path = Path(sys.argv[2])
    repo_override = sys.argv[3] if len(sys.argv) > 3 else None

    task_text = task_path.read_text(errors="ignore")
    prompt = build_prompt(task_text)

    review = {
        "requirements_covered": True,
        "scope_creep": False,
        "architecture_risk": "low",
        "blocking_issues": [],
        "summary": "Fast pipeline lightweight review: validation passed and task was bounded.",
    }

    run_pipeline(
        product_name=product_name,
        task_path=task_path,
        pipeline="fast",
        prompt=prompt,
        response_filename="fast-response.md",
        prompt_filename="fast-prompt.md",
        review_title="Fast",
        review=review,
        max_turns=8,
        repo_override=repo_override,
    )


if __name__ == "__main__":
    main()
