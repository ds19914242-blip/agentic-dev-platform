from pathlib import Path
import subprocess


def execute_generated_playwright(epic_dir, cwd=None):
    epic_dir = Path(epic_dir)
    test_file = epic_dir / "generated-playwright" / "acceptance.spec.ts"

    if not test_file.exists():
        raise FileNotFoundError(test_file)

    cmd = ["npx", "playwright", "test", str(test_file)]

    return subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        capture_output=True,
    )
