from pathlib import Path
import subprocess


def get_changed_files(repo_path):
    result = subprocess.run(
        ["git", "status", "--short"],
        cwd=repo_path,
        text=True,
        capture_output=True,
    )

    return result.stdout.strip()


def get_diff_stat(repo_path):
    result = subprocess.run(
        ["git", "diff", "--stat"],
        cwd=repo_path,
        text=True,
        capture_output=True,
    )

    return result.stdout.strip()


def record_execution_result(run_dir, repo_path, summary=""):
    changed_files = get_changed_files(repo_path)
    diff_stat = get_diff_stat(repo_path)

    Path(run_dir / "implementation.md").write_text(f"""# Implementation Result

## Summary

{summary or "Implementation result recorded."}

## Changed Files

```text
{changed_files or "No changes detected"}
Diff Stat
{diff_stat or "No diff detected"}

""")
