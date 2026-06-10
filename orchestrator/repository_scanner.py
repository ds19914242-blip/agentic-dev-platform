from pathlib import Path

IGNORE_DIRS = {
    ".git", "node_modules", "dist", "build", ".next",
    "coverage", ".venv", "__pycache__",
}

IMPORTANT_FILES = {
    "package.json", "README.md", "next.config.js",
    "vite.config.js", "tsconfig.json", "requirements.txt", "pyproject.toml",
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
