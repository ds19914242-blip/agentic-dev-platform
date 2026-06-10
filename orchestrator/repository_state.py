import subprocess


def git_status(repo_path):
    result = subprocess.run(
        ["git", "status", "--short"],
        cwd=repo_path,
        text=True,
        capture_output=True,
    )

    return result.stdout.strip()


def ensure_clean_repo(repo_path):
    status = git_status(repo_path)

    if status:
        raise RuntimeError(
            "Target repository has uncommitted changes:\n\n"
            + status
            + "\n\nCommit or restore changes before starting a new run."
        )
