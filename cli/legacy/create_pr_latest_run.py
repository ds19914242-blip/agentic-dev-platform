# DEPRECATED ENTRYPOINT
#
# This file belongs to an older workflow path.
# It is kept temporarily for compatibility while the v0.4 architecture stabilizes.
# Do not extend this file. Prefer agentic.py + orchestrator/workflows + orchestrator/services.
#

from pathlib import Path
import subprocess

from orchestrator.product_registry import load_product_config
from orchestrator.run_status import write_status, append_event


def latest_run():
    runs = sorted(p for p in Path("runs").glob("feature-*") if p.is_dir())
    if not runs:
        raise RuntimeError("No feature runs found")
    return runs[-1]


def run(command, cwd, retries=2):
    last_error = ""

    for _ in range(retries + 1):
        result = subprocess.run(command, cwd=cwd, text=True, capture_output=True)

        if result.returncode == 0:
            return result.stdout.strip()

        last_error = result.stderr or result.stdout

    raise RuntimeError(last_error)


def main():
    product_name = input("Product name: ").strip()
    branch_name = input("Branch name: ").strip()
    commit_message = input("Commit message: ").strip()

    product = load_product_config(product_name)
    repo_path = product["repo_path"]
    run_dir = latest_run()

    status = run(["git", "status", "--short"], repo_path)
    if not status:
        raise RuntimeError("No changes to commit.")

    run(["git", "checkout", "-b", branch_name], repo_path)
    run(["git", "add", "."], repo_path)
    run(["git", "commit", "-m", commit_message], repo_path)
    run(["git", "push", "-u", "origin", branch_name], repo_path)

    pr_url = run([
        "gh", "pr", "create",
        "--title", commit_message,
        "--body", f"Created by Agentic Dev Platform run: {run_dir}",
    ], repo_path)

    (run_dir / "pull-request.md").write_text(f"""# Pull Request

{pr_url}
""")

    write_status(run_dir, "pr_created")
    append_event(run_dir, f"Pull request created: {pr_url}")

    print(f"PR created: {pr_url}")


if __name__ == "__main__":
    main()
