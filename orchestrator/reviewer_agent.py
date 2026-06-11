import json
from pathlib import Path

from orchestrator.claude_executor import run_claude
from orchestrator.run_artifacts import register_artifacts
from orchestrator.run_status import append_event


def read_file(path):
    path = Path(path)
    return path.read_text() if path.exists() else ""


def build_review_prompt(feature, plan, implementation_response, validation_report):
    return f"""# Review Implementation

Review whether the implementation satisfies the feature request.

Return ONLY valid JSON with this shape:

{{
  "requirements_covered": true,
  "scope_creep": false,
  "architecture_risk": "low",
  "blocking_issues": [],
  "summary": ""
}}

Rules:
- Be strict but practical.
- Do not invent issues.
- Mark requirements_covered=false only if the feature clearly was not implemented.
- Mark scope_creep=true if implementation changed unrelated areas.
- architecture_risk must be one of: low, medium, high.

# Feature Request

{feature}

# Approved Plan

{plan}

# Implementation Response

{implementation_response}

# Validation Report

{validation_report}
"""


def parse_review(text):
    try:
        return json.loads(text)
    except Exception:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start:end + 1])

    return {
        "requirements_covered": False,
        "scope_creep": False,
        "architecture_risk": "medium",
        "blocking_issues": ["Reviewer did not return valid JSON"],
        "summary": text[:1000],
    }


def run_reviewer(run_dir, repo_path, feature):
    run_dir = Path(run_dir)

    plan = read_file(run_dir / "approved-plan.md")
    implementation_response = read_file(run_dir / "claude-implementation-response.md")
    validation_report = read_file(run_dir / "validation.md")

    prompt = build_review_prompt(
        feature=feature,
        plan=plan,
        implementation_response=implementation_response,
        validation_report=validation_report,
    )

    (run_dir / "review-prompt.md").write_text(prompt)

    response = run_claude(
        repo_path=repo_path,
        prompt=prompt,
        allow_writes=False,
        max_turns=5,
    )

    (run_dir / "review-response.md").write_text(
        "# Reviewer Response\n\n" + response
    )

    review = parse_review(response)

    (run_dir / "review.json").write_text(
        json.dumps(review, indent=2, ensure_ascii=False)
    )

    lines = [
        "# Reviewer Result",
        "",
        f"Requirements Covered: {review.get('requirements_covered')}",
        "",
        f"Scope Creep: {review.get('scope_creep')}",
        "",
        f"Architecture Risk: {review.get('architecture_risk')}",
        "",
        "## Blocking Issues",
        "",
    ]

    issues = review.get("blocking_issues") or []
    if issues:
        lines.extend(f"- {issue}" for issue in issues)
    else:
        lines.append("_None_")

    lines.extend([
        "",
        "## Summary",
        "",
        review.get("summary", ""),
        "",
    ])

    (run_dir / "review.md").write_text("\n".join(lines))

    register_artifacts(
        run_dir,
        ["review-prompt.md", "review-response.md", "review.json", "review.md"],
        stage="review",
    )

    append_event(run_dir, f"Reviewer completed: requirements_covered={review.get('requirements_covered')}")

    return review
