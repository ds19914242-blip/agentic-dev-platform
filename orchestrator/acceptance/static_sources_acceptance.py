from pathlib import Path
import shlex


def can_use_static_sources_acceptance(epic_dir):
    text = ""
    for name in ["feature-spec.md", "acceptance-scenarios.md"]:
        p = Path(epic_dir) / name
        if p.exists():
            text += p.read_text(errors="ignore").lower()

    return (
        "/sources" in text
        and "cisa" in text
        and "github" in text
        and ("hacker news" in text or "hackernews" in text)
    )


def write_static_sources_acceptance(repo_path, epic_dir):
    repo_path = Path(repo_path).resolve()
    epic_dir = Path(epic_dir).resolve()

    acceptance_dir = repo_path / ".agentic" / "acceptance"
    artifacts_dir = epic_dir / "acceptance-artifacts"
    acceptance_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    spec = """import { test, expect } from '@playwright/test';

const baseURL = process.env.ACCEPTANCE_BASE_URL || 'http://127.0.0.1:3100';

test('source management exposes new source types after login', async ({ page }) => {
  await page.goto(baseURL + '/login');

  await page.getByLabel(/логин/i).fill(process.env.ACCEPTANCE_USERNAME || 'admin');
  await page.getByLabel(/пароль/i).fill(process.env.ACCEPTANCE_PASSWORD || 'password123');

  const signIn = page.getByRole('button', { name: /sign in|войти/i });
  await expect(signIn).toBeEnabled();
  await signIn.click();

  await page.waitForURL(url => !url.pathname.includes('/login'), { timeout: 10000 }).catch(() => {});
  await page.goto(baseURL + '/sources');

  await expect(page.getByRole('heading', { name: 'Источники' })).toBeVisible();
  await expect(page.getByText('CISA KEV')).toBeVisible();
  await expect(page.getByText(/GitHub/i)).toBeVisible();
  await expect(page.getByText('Hacker News')).toBeVisible();

  await page.getByText('CISA KEV').click();
  await expect(page.getByText(/URL CISA KEV|CISA/i)).toBeVisible();

  await page.getByText(/GitHub/i).click();
  await expect(page.getByText('URL GitHub Advisories (необязательно)')).toBeVisible();

  await page.getByText('Hacker News').click();
  await expect(page.getByText('Ключевые слова (через запятую, необязательно)')).toBeVisible();
});
"""

    spec_path = acceptance_dir / "generated-acceptance.spec.ts"
    spec_path.write_text(spec)
    (epic_dir / "generated-acceptance.spec.ts").write_text(spec)

    q_repo = shlex.quote(str(repo_path))
    q_spec = shlex.quote(str(spec_path))
    q_artifacts = shlex.quote(str(artifacts_dir))

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
        "APP_USERNAME=admin APP_PASSWORD=password123 SESSION_SECRET=dev-secret "
        "npm run dev -- --hostname 127.0.0.1 --port 3100 > " + q_artifacts + "/dev.log 2>&1 & "
        "SERVER_PID=$!; "
        "for i in $(seq 1 60); do curl -fsS http://127.0.0.1:3100 >/dev/null 2>&1 && break; sleep 1; done; "
        "curl -fsS http://127.0.0.1:3100 >/dev/null; "
        "cd \"$TMP_DIR\"; "
        "ACCEPTANCE_BASE_URL=http://127.0.0.1:3100 "
        "ACCEPTANCE_USERNAME=admin ACCEPTANCE_PASSWORD=password123 "
        "npx playwright test generated-acceptance.spec.ts --reporter=list "
        "--output=" + q_artifacts + "'"
    )

    (epic_dir / "acceptance-command.txt").write_text(command + "\n")
    return command
