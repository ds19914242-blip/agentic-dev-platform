from orchestrator.claude_executor import run_claude


def generate_tests(repo_path, feature, test_plan, capabilities=None):
    capabilities = capabilities or {}

    prompt = f"""# Test Generator Agent

You are a Test Generator Agent.

Create or update automated tests for this task only if the product capabilities say tests are available.

## Feature Request

{feature}

## Test Plan

{test_plan}

## Product Capabilities

{capabilities}

## Rules

- If unit_tests is false, do not create unit tests.
- If e2e_tests is false, do not create Playwright/E2E tests.
- If no compatible test framework exists, do not install dependencies.
- Do not install packages.
- Do not change production logic unless required for testability.
- For UI text-only tasks without test capability, write a short explanation and skip test generation.
"""

    return run_claude(
        repo_path=repo_path,
        prompt=prompt,
        allow_writes=True,
        max_turns=8,
    )
