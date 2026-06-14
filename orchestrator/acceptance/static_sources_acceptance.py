from pathlib import Path


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
    repo_path = Path(repo_path)
    epic_dir = Path(epic_dir)

    acceptance_dir = repo_path / ".agentic" / "acceptance"
    acceptance_dir.mkdir(parents=True, exist_ok=True)

    spec = r'''import { test, expect } from '@playwright/test';

const baseURL = process.env.ACCEPTANCE_BASE_URL || 'http://127.0.0.1:3000';

test('new source types are selectable and change source form', async ({ page }) => {
  await page.goto(baseURL + '/sources');

  await expect(page.getByText('CISA KEV')).toBeVisible();
  await expect(page.getByText('GitHub')).toBeVisible();
  await expect(page.getByText('Hacker News')).toBeVisible();

  await page.getByText('CISA KEV').click();
  await expect(page.getByText(/CISA|KEV/i)).toBeVisible();

  await page.getByText('GitHub').click();
  await expect(page.getByText(/GitHub|Advisories/i)).toBeVisible();

  await page.getByText('Hacker News').click();
  await expect(page.getByText(/Hacker News|keywords|ключ/i)).toBeVisible();

  await expect(page.getByText('RSS URL')).not.toBeVisible();
});
'''

    spec_path = acceptance_dir / "generated-acceptance.spec.ts"
    spec_path.write_text(spec)
    (epic_dir / "generated-acceptance.spec.ts").write_text(spec)

    command = (
        "bash -lc 'set -e; "
        "npm run dev -- --hostname 127.0.0.1 > .agentic/acceptance/dev.log 2>&1 & "
        "SERVER_PID=$!; "
        "trap \"kill $SERVER_PID 2>/dev/null || true\" EXIT; "
        "for i in $(seq 1 60); do curl -fsS http://127.0.0.1:3000 >/dev/null 2>&1 && break; sleep 1; done; "
        "ACCEPTANCE_BASE_URL=http://127.0.0.1:3000 "
        "npx playwright test .agentic/acceptance/generated-acceptance.spec.ts --reporter=list'"
    )

    (epic_dir / "acceptance-command.txt").write_text(command + "\n")
    return command
