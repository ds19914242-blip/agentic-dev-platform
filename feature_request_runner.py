# DEPRECATED ENTRYPOINT
#
# This file belongs to an older workflow path.
# It is kept temporarily for compatibility while the v0.4 architecture stabilizes.
# Do not extend this file. Prefer agentic.py + orchestrator/workflows + orchestrator/services.
#

import subprocess
from pathlib import Path

IGNORE_DIRS = {
    ".git",
    "node_modules",
    "dist",
    "build",
    ".next",
    "coverage",
    ".venv",
    "__pycache__",
}

IMPORTANT_FILES = {
    "package.json",
    "README.md",
    "next.config.js",
    "vite.config.js",
    "tsconfig.json",
    "requirements.txt",
    "pyproject.toml",
}

def run_command(command, cwd=None):
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    return result.stdout

def should_ignore(path):
    return any(part in IGNORE_DIRS for part in path.parts)

def inspect_repo(repo_path):
    root = Path(repo_path)
    files = []

    for path in root.rglob("*"):
        rel = path.relative_to(root)

        if should_ignore(rel):
            continue

        if path.is_file():
            if rel.parts[0] in {"src", "app", "components", "pages", "api", "lib"}:
                files.append(str(rel))
            elif path.name in IMPORTANT_FILES:
                files.append(str(rel))

    return "\n".join(files[:300])

def main():
    repo_path = input("Repo path: ").strip()
    feature = input("Feature request: ").strip()

    print("\n[1] Inspecting repository...")
    repo_files = inspect_repo(repo_path)

    print("\n[2] Repository files:")
    print(repo_files)

    Path("runs").mkdir(exist_ok=True)
    prompt_path = "runs/latest-feature-prompt.md"

    with open(prompt_path, "w") as f:
        f.write(f"""# Feature Request

{feature}

# Repository

{repo_path}

# Relevant Files

{repo_files}

# Task

Analyze the repository and create an implementation plan.
""")

    print(f"\nPrompt saved to: {prompt_path}")

    print("\n[3] Git status:")
    try:
        print(run_command(["git", "status", "--short"], cwd=repo_path))
    except Exception as e:
        print(f"Git status failed: {e}")

if __name__ == "__main__":
    main()
