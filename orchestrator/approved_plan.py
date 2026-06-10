from pathlib import Path


def save_approved_plan(run_dir, text):
    path = Path(run_dir) / "approved-plan.md"
    path.write_text(f"""# Approved Plan

{text}
""")
    return path


def load_approved_plan(run_dir):
    path = Path(run_dir) / "approved-plan.md"

    if not path.exists():
        raise FileNotFoundError(f"Approved plan not found: {path}")

    return path.read_text()
