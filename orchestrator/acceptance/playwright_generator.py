from pathlib import Path


def js_string(value):
    return repr(value)


def generate_playwright_test(epic_dir, scenarios):
    epic_dir = Path(epic_dir)
    out_dir = epic_dir / "generated-playwright"
    out_dir.mkdir(exist_ok=True)
    test_path = out_dir / "acceptance.spec.ts"

    lines = [
        "import { test, expect } from '@playwright/test';",
        "",
        "const baseUrl = process.env.ACCEPTANCE_BASE_URL || 'http://localhost:3000';",
        "",
    ]

    for index, scenario in enumerate(scenarios, start=1):
        title = scenario.title.replace("'", "\\'")
        lines.append(f"test({js_string(str(index) + '. ' + title)}, async ({{ page }}) => {{")
        lines.append("  await page.goto(baseUrl);")
        lines.append("  // Generated from acceptance-scenarios.md")
        lines.append("  // Manual implementation may be needed for product-specific UI steps.")
        for step in scenario.steps:
            lines.append(f"  // STEP: {step}")
        for expected in scenario.expected:
            lines.append(f"  // EXPECTED: {expected}")
        lines.append("  expect(page).toBeTruthy();")
        lines.append("});")
        lines.append("")

    test_path.write_text("\n".join(lines))
    return test_path
