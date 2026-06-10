from pathlib import Path
from datetime import datetime


def make_run_dir(prefix="feature"):
    Path("runs").mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = Path("runs") / f"{prefix}-{stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def write_run_files(run_dir, feature, repo_path, files, affected, status, prompt):
    (run_dir / "work-item.md").write_text(f"""# Work Item

## Type

feature

## Request

{feature}

## Repository

{repo_path}

## Status

created
""")

    (run_dir / "affected-files.md").write_text(
        "# Affected Files\n\n" + "\n".join(f"- {f}" for f in affected) + "\n"
    )

    (run_dir / "claude-prompt.md").write_text(prompt)

    (run_dir / "summary.md").write_text(f"""# Run Summary

## Feature Request

{feature}

## Repository

{repo_path}

## Files scanned

{len(files)}

## Affected files

{len(affected)}

## Git status before execution

```text
{status or "clean"}
Status

prompt_created
""")
