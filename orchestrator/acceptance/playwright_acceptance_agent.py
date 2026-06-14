import shlex
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




def _stabilize_login_helper(spec):
    import re

    helper = """async function login(page) {
  await page.goto(`${baseURL}/login`);
  await page.locator('input[type="text"]').fill(username);
  await page.locator('input[type="password"]').fill(password);

  const signIn = page.getByRole('button', { name: /sign in|войти/i });
  await expect(signIn).toBeEnabled({ timeout: 5000 });
  await signIn.click();

  await page.waitForURL(/\\/dashboard|\\/sources|\\/$/, { timeout: 10000 }).catch(() => {});
}
"""

    if "async function login(" in spec:
        spec = re.sub(
            r"async function login\\([^)]*\\)\\s*\\{.*?\\n\\}",
            helper,
            spec,
            flags=re.DOTALL,
        )

    return spec

def generate_playwright_acceptance(epic_dir, product_name, repo_path, config=None):
    epic_dir = Path(epic_dir).resolve()
    repo_path = Path(repo_path).resolve()
    config = config or {}

    mode = str(config.get("mode") or "local")
    base_url = str(
        config.get("production_url")
        if mode == "production" and config.get("production_url")
        else config.get("base_url") or "http://127.0.0.1:3100"
    )
    login_url = str(config.get("login_url") or "/login")
    username = str(config.get("username") or "admin")
    password = str(config.get("password") or "password123")

    scenarios = _read(epic_dir / "acceptance-scenarios.md")
    feature_spec = _read(epic_dir / "feature-spec.md")

    prompt = f"""# Playwright Acceptance Agent

Generate ONE TypeScript Playwright test file for this feature.

Product: {product_name}
Base URL: {base_url}
Login URL: {login_url}

## Feature Spec

{feature_spec}

## Acceptance Scenarios

{scenarios}

## Required Test Structure

Return ONLY a TypeScript code block.

The test must:
- import {{ test, expect }} from '@playwright/test'
- define baseURL from process.env.ACCEPTANCE_BASE_URL
- login first if the scenario targets a protected page
- use username/password from process.env.ACCEPTANCE_USERNAME / ACCEPTANCE_PASSWORD
- verify real user-visible behavior from the acceptance scenarios
- use precise locators: role, label, placeholder, exact visible text
- avoid broad regex locators that match multiple elements
- fail when the feature is not actually usable
- avoid external credentials and destructive actions
"""

    response = run_claude(
        repo_path=str(repo_path),
        prompt=prompt,
        allow_writes=False,
        max_turns=8,
        retries=0,
    )

    spec = _stabilize_login_helper(_extract_code(response))

    acceptance_dir = repo_path / ".agentic" / "acceptance"
    artifacts_dir = epic_dir / "acceptance-artifacts"
    acceptance_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    spec_path = acceptance_dir / "generated-acceptance.spec.ts"
    spec_path.write_text(spec)
    (epic_dir / "generated-acceptance.spec.ts").write_text(spec)

    q_repo = shlex.quote(str(repo_path))
    q_spec = shlex.quote(str(spec_path))
    q_artifacts = shlex.quote(str(artifacts_dir))

    if mode == "production":
        command = (
            "bash -lc 'set -euo pipefail; "
            f"cd {q_repo}; "
            "TMP_DIR=$(mktemp -d); "
            "trap \"rm -rf $TMP_DIR\" EXIT; "
            "cp " + q_spec + " \"$TMP_DIR/generated-acceptance.spec.ts\"; "
            "cd \"$TMP_DIR\"; "
            "npm init -y >/dev/null 2>&1; "
            "npm install -D @playwright/test >/dev/null 2>&1; "
            "npx playwright install chromium >/dev/null 2>&1; "
            f"curl -fsS {shlex.quote(base_url)} >/dev/null; "
            f"ACCEPTANCE_BASE_URL={shlex.quote(base_url)} "
            f"ACCEPTANCE_USERNAME={shlex.quote(username)} ACCEPTANCE_PASSWORD={shlex.quote(password)} "
            "npx playwright test generated-acceptance.spec.ts --reporter=list "
            "--output=" + q_artifacts + "'"
        )
    else:
        command = (
            "bash -lc 'set -euo pipefail; "
            f"cd {q_repo}; "
            "if [ ! -x node_modules/.bin/next ]; then npm install; fi; "
            "TMP_DIR=$(mktemp -d); "
            "trap \"kill ${SERVER_PID:-} 2>/dev/null || true; rm -rf $TMP_DIR\" EXIT; "
            "cp " + q_spec + " \"$TMP_DIR/generated-acceptance.spec.ts\"; "
            "cd \"$TMP_DIR\"; "
            "npm init -y >/dev/null 2>&1; "
            "npm install -D @playwright/test >/dev/null 2>&1; "
            "npx playwright install chromium >/dev/null 2>&1; "
            f"cd {q_repo}; "
            "rm -rf .next; npm run build; "
            f"APP_USERNAME={shlex.quote(username)} APP_PASSWORD={shlex.quote(password)} SESSION_SECRET=dev-secret PORT=3100 "
            "npm run start > " + q_artifacts + "/dev.log 2>&1 & "
            "SERVER_PID=$!; "
            "for i in $(seq 1 60); do curl -fsS http://127.0.0.1:3100 >/dev/null 2>&1 && break; sleep 1; done; "
            "curl -fsS http://127.0.0.1:3100 >/dev/null; "
            "cd \"$TMP_DIR\"; "
            "ACCEPTANCE_BASE_URL=http://127.0.0.1:3100 "
            f"ACCEPTANCE_USERNAME={shlex.quote(username)} ACCEPTANCE_PASSWORD={shlex.quote(password)} "
            "npx playwright test generated-acceptance.spec.ts --reporter=list "
            "--output=" + q_artifacts + "'"
        )

    (epic_dir / "acceptance-command.txt").write_text(command + "\n")
    return command
