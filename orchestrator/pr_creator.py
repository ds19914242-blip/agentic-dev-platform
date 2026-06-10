import subprocess


def run(command, cwd, retries=2):
    last_error = ""

    for _ in range(retries + 1):
        result = subprocess.run(command, cwd=cwd, text=True, capture_output=True)

        if result.returncode == 0:
            return result.stdout.strip()

        last_error = result.stderr or result.stdout

    raise RuntimeError(last_error)


def has_changes(repo_path):
    status = run(["git", "status", "--short"], repo_path)
    return bool(status.strip())


def create_pr(repo_path, branch_name, commit_message, body):
    if not has_changes(repo_path):
        return None

    current_branch = run(["git", "branch", "--show-current"], repo_path)

    if current_branch != branch_name:
        run(["git", "checkout", "-b", branch_name], repo_path)

    run(["git", "add", "."], repo_path)
    run(["git", "commit", "-m", commit_message], repo_path)
    run(["git", "push", "-u", "origin", branch_name], repo_path)

    pr_url = run([
        "gh", "pr", "create",
        "--title", commit_message,
        "--body", body,
    ], repo_path)

    return pr_url
