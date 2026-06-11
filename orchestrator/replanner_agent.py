from pathlib import Path

from orchestrator.claude_executor import run_claude
from orchestrator.run_artifacts import register_artifacts
from orchestrator.run_status import append_event


def read_file(path):
    path = Path(path)
    return path.read_text() if path.exists() else ""


def build_replan_prompt(feature, validation_report, approved_plan, implementation_response):
    return f"""# Replan Failed Implementation

The implementation failed validation.

Your job:
1. Analyze the validation failure.
2. Identify the most likely root cause.
3. Produce a minimal fix plan.
4. Apply the fix directly.
5. Do not redesign the feature.
6. Do not touch auth, billing, secrets, database schema, or deployment config.

# Feature Request

{feature}

# Approved Plan

{approved_plan}

# Implementation Response

{implementation_response}

# Validation Report

{validation_report}
"""


def run_replanner(
    run_dir,
    repo_path,
    feature,
    max_turns=10,
):
    run_dir = Path(run_dir)

    validation_report = read_file(run_dir / "validation.md")
    approved_plan = read_file(run_dir / "approved-plan.md")
    implementation_response = read_file(run_dir / "claude-implementation-response.md")

    prompt = build_replan_prompt(
        feature=feature,
        validation_report=validation_report,
        approved_plan=approved_plan,
        implementation_response=implementation_response,
    )

    (run_dir / "replan-prompt.md").write_text(prompt)

    response = run_claude(
        repo_path=repo_path,
        prompt=prompt,
        allow_writes=True,
        max_turns=max_turns,
    )

    (run_dir / "replan-response.md").write_text(
        "# Replanner Response\n\n" + response
    )

    register_artifacts(
        run_dir,
        ["replan-prompt.md", "replan-response.md"],
        stage="replanning",
    )

    append_event(run_dir, "Replanner completed")

    return response
