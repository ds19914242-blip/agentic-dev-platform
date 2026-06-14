from pathlib import Path

from orchestrator.claude_executor import run_claude


def _read(path):
    path = Path(path)
    return path.read_text(errors="ignore") if path.exists() else ""


def generate_acceptance_command(epic_dir, product_name, repo_path):
    epic_dir = Path(epic_dir)

    scenarios = _read(epic_dir / "acceptance-scenarios.md")
    feature_spec = _read(epic_dir / "feature-spec.md")

    prompt = f"""# Acceptance Verification Agent

You verify product behavior from the user's perspective.

Generate ONE executable shell command that verifies the accepted scenarios.

Product: {product_name}
Repository: {repo_path}

## Feature Spec

{feature_spec}

## Acceptance Scenarios

{scenarios}

## Requirements

Return ONLY a shell command.

The command should:
- run from the product repository root
- prefer existing test tooling if present
- if no test exists, create and run a temporary Playwright smoke test using npx
- verify real UI behavior, not just typecheck/build
- fail with non-zero exit code when a scenario fails
- be safe and not modify production data unless the scenario explicitly requires creating test data
- write useful stdout/stderr for debugging

For UI features, the command should start or reuse the local Next.js app and exercise the relevant page with Playwright.
"""

    command = run_claude(
        repo_path=repo_path,
        prompt=prompt,
        allow_writes=False,
        max_turns=10,
        retries=1,
    ).strip()

    command = command.strip()

    if not command or command.lower().startswith("error:"):
        raise RuntimeError(f"Acceptance command generation failed: {command}")

    import re
    block = re.search(r"```(?:bash|sh)?\\n(.*?)```", command, flags=re.DOTALL)
    if block:
        command = block.group(1).strip()
    else:
        if "\n" in command:
            raise RuntimeError("Claude returned multiline text without a shell code block")
        lines = [line.strip() for line in command.splitlines() if line.strip()]
        allowed = ("bash ", "bash -lc", "sh ", "npm ", "npx ", "pnpm ", "yarn ", "python", "node ")
        command = next((line for line in lines if line.startswith(allowed)), "")

    if not command:
        raise RuntimeError("Claude did not return an executable acceptance command")

    return command
