from pathlib import Path
from datetime import datetime
import subprocess

IGNORE_DIRS = {
    ".git", "node_modules", "dist", "build", ".next",
    "coverage", ".venv", "__pycache__",
}

IMPORTANT_FILES = {
    "package.json", "README.md", "next.config.js",
    "vite.config.js", "tsconfig.json", "requirements.txt", "pyproject.toml",
}

KEYWORDS = {
    "rss": ["app/rss", "app/api/rss", "lib/rss", "src/collector", "src/config/feeds"],
    "summary": ["components", "src/reporting", "src/report", "src/agents"],
    "summaries": ["components", "src/reporting", "src/report", "src/agents"],
    "ai": ["src/llm", "src/agents", "src/analysis"],
    "feed": ["lib/rss", "src/collector", "src/config/feeds"],
}

def should_ignore(path):
    return any(part in IGNORE_DIRS for part in path.parts)

def scan_repo(repo_path):
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
    return sorted(files)

def detect_affected_files(feature, files):
    feature_l = feature.lower()
    matched = []
    for word, patterns in KEYWORDS.items():
        if word in feature_l:
            for file in files:
                if any(file.startswith(pattern) for pattern in patterns):
                    matched.append(file)
    return sorted(set(matched))[:15]

def read_context(repo_path, affected_files):
    chunks = []
    for file in affected_files:
        path = Path(repo_path) / file
        if path.exists():
            chunks.append(f"\n\n# FILE: {file}\n\n")
            chunks.append(path.read_text(errors="ignore")[:8000])
    return "".join(chunks)

def git_status(repo_path):
    result = subprocess.run(
        ["git", "status", "--short"],
        cwd=repo_path,
        text=True,
        capture_output=True,
    )
    return result.stdout.strip()

def make_run_dir():
    Path("runs").mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = Path("runs") / f"feature-{stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir

def main():
    repo_path = input("Repo path: ").strip()
    feature = input("Feature request: ").strip()

    run_dir = make_run_dir()

    print("\n[1] Scanning repository...")
    files = scan_repo(repo_path)

    print("\n[2] Detecting affected files...")
    affected = detect_affected_files(feature, files)

    print("\nAffected files:")
    for file in affected:
        print(f"- {file}")

    context = read_context(repo_path, affected)
    status = git_status(repo_path)

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

    prompt = f"""# Feature Request

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
```

## Status

prompt_created
""")

    print(f"\nRun created: {run_dir}")
    print(f"Claude prompt: {run_dir / 'claude-prompt.md'}")

if __name__ == "__main__":
    main()
