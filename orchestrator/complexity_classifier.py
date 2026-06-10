from orchestrator.claude_executor import run_claude


def classify_request_with_llm(repo_path, feature, repo_map_text):
    prompt = f"""# Complexity Classifier

You are an intake analyst for an autonomous development platform.

Classify the request before execution.

## Feature Request

{feature}

## Repository Map

{repo_map_text}

## Return exactly this format

# Complexity Assessment

Complexity: SMALL | MEDIUM | EPIC

Estimated Files: <number>

Risk: LOW | MEDIUM | HIGH

Recommended Route: RUN_AUTONOMOUS | DECOMPOSE_FIRST | NEEDS_HUMAN_REVIEW

Reason:
<short reason>

Rules:
- SMALL means likely 1-3 files.
- MEDIUM means likely 4-8 files or moderate uncertainty.
- EPIC means many files, multiple pages, multiple subsystems, or broad product change.
- If the task affects auth, billing, database schema, secrets, deployment or permissions, recommend NEEDS_HUMAN_REVIEW.
- If the task is broad or unclear, recommend DECOMPOSE_FIRST.
"""

    return run_claude(
        repo_path=repo_path,
        prompt=prompt,
        allow_writes=False,
        max_turns=3,
    )


def parse_complexity(text):
    low = text.lower()

    if "recommended route: decompose_first" in low:
        route = "DECOMPOSE_FIRST"
    elif "recommended route: needs_human_review" in low:
        route = "NEEDS_HUMAN_REVIEW"
    else:
        route = "RUN_AUTONOMOUS"

    if "complexity: epic" in low:
        complexity = "EPIC"
    elif "complexity: medium" in low:
        complexity = "MEDIUM"
    else:
        complexity = "SMALL"

    return {
        "complexity": complexity,
        "route": route,
        "raw": text,
    }
