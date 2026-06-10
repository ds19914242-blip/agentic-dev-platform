import subprocess

from orchestrator.product_registry import load_product_config
from orchestrator.repository_scanner import scan_repo
from orchestrator.affected_file_detector import detect_affected_files
from orchestrator.context_builder import read_context
from orchestrator.run_manager import make_run_dir, write_run_files


def git_status(repo_path):
    result = subprocess.run(
        ["git", "status", "--short"],
        cwd=repo_path,
        text=True,
        capture_output=True,
    )

    return result.stdout.strip()


def build_prompt(feature, repo_path, affected, context):
    return f"""# Feature Request

{feature}

# Repository

{repo_path}

# Affected Files

{chr(10).join("- " + f for f in affected)}

# Task

You are a senior autonomous coding agent.

Analyze the affected files and implement the smallest safe solution.

Rules:
- First explain what already exists.
- Then create an implementation plan.
- Do not modify auth, billing, secrets, database schema, or deployment config unless explicitly required.
- Keep changes small and reversible.
- After implementation, run typecheck/tests if available.
- Summarize changed files and risks.

# Context

{context}
"""


def main():
    product_name = input("Product name: ").strip()
    feature = input("Feature request: ").strip()

    product = load_product_config(product_name)
    repo_path = product["repo_path"]

    print(f"\nUsing repo: {repo_path}")

    print("\n[1] Scanning repository...")
    files = scan_repo(repo_path)

    print("\n[2] Detecting affected files...")
    affected = detect_affected_files(feature, files)

    print("\nAffected files:")
    for file in affected:
        print(f"- {file}")

    print("\n[3] Building context...")
    context = read_context(repo_path, affected)

    print("\n[4] Creating run artifacts...")
    status = git_status(repo_path)
    prompt = build_prompt(feature, repo_path, affected, context)

    run_dir = make_run_dir("feature")
    write_run_files(run_dir, feature, repo_path, files, affected, status, prompt)

    print(f"\nRun created: {run_dir}")
    print(f"Claude prompt: {run_dir / 'claude-prompt.md'}")


if __name__ == "__main__":
    main()
