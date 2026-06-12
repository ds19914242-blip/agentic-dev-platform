from pathlib import Path


def write_playwright_setup_guide(epic_dir):
    epic_dir = Path(epic_dir)
    path = epic_dir / "playwright-setup.md"
    path.write_text("""# Playwright Setup

If Playwright is not installed in the product repo, run:

```bash
npm install -D @playwright/test
npx playwright install
```

Then run generated acceptance verification:

```bash
python3 agentic.py acceptance <epic-dir>
```
""")
    return path
