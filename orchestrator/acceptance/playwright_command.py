from pathlib import Path


def write_playwright_command(epic_dir, product_cwd=None):
    epic_dir = Path(epic_dir)
    test_path = epic_dir / "generated-playwright" / "acceptance.spec.ts"
    command_path = epic_dir / "acceptance-command.txt"

    if product_cwd:
        command = f"npx playwright test {test_path}"
    else:
        command = f"npx playwright test {test_path}"

    command_path.write_text(command + "\n")
    return command_path, command
