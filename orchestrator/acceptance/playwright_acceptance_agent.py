import re
from pathlib import Path

from orchestrator.claude_executor import run_claude


def _read(path):
    path = Path(path)
    return path.read_text(errors="ignore") if path.exists() else ""


def _extract_code(text):
    match = re.search(r"```(?:ts|typescript|javascript|js)?\n(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()

    if "import { test, expect }" in text:
        return text.strip()

    raise RuntimeError("Claude did not return a Playwright test file")


def generate_playwright_acceptance(epic_dir, product_name, repo_path):
    epic_dir = Path(epic_dir)
    repo_path = Path(repo_path)

    scenarios = _read(epic_dir / "acceptance-scenarios.md")
    feature_spec = _read(epic_dir / "feature-spec.md")

    prompt = f"""# Playwright Acceptance Agent

Generate a Playwright test file that verifies the user's acceptance scenarios.

Product: {product_name}

## Feature Spec

{feature_spec}

## Acceptance Scenarios

{scenarios}

## Requirements

Return ONLY one TypeScript Playwright test file in a code block.

Rules:
- Use `import {{ test, expect }} from '@playwright/test';`
- Use `const baseURL = process.env.ACCEPTANCE_BASE_URL || 'http://127.0.0.1:3000';`
- Navigate with `page.goto(baseURL + '/...')`.
- Verify real user behavior, not just that the page loads.
- For source-management UI, click each source type button/tab and assert the form visibly changes.
- Do not require external credentials.
- Prefer assertions on visible text, labels, placeholders, aria-labels, buttons, and form state.
- Make failures descriptive.
"""

    response = run_claude(
        repo_path=str(repo_path),
        prompt=prompt,
        allow_writes=False,
        max_turns=6,
        retries=0,
    )

    spec = _extract_code(response)

    acceptance_dir = repo_path / ".agentic" / "acceptance"
    acceptance_dir.mkdir(parents=True, exist_ok=True)

    spec_path = acceptance_dir / "generated-acceptance.spec.ts"
    spec_path.write_text(spec)

    command = (
        "bash -lc 'set -e; "
        "mkdir -p .agentic/acceptance; "
        "npm run dev -- --hostname 127.0.0.1 > .agentic/acceptance/dev.log 2>&1 & "
        "SERVER_PID=$!; "
        "trap \"kill $SERVER_PID 2>/dev/null || true\" EXIT; "
        "for i in $(seq 1 60); do "
        "  curl -fsS http://127.0.0.1:3000 >/dev/null 2>&1 && break; "
        "  sleep 1; "
        "done; "
        "ACCEPTANCE_BASE_URL=http://127.0.0.1:3000 "
        "npx playwright test .agentic/acceptance/generated-acceptance.spec.ts --reporter=list'"
    )

    (epic_dir / "acceptance-command.txt").write_text(command + "\n")
    (epic_dir / "generated-acceptance.spec.ts").write_text(spec)

    return command
