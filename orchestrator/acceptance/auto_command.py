from pathlib import Path


def infer_acceptance_command(epic_dir):
    epic_dir = Path(epic_dir)
    generated = epic_dir / "generated-playwright" / "acceptance.spec.ts"
    if generated.exists():
        return f"npx playwright test {generated}"
    return None
