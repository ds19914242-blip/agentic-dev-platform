from pathlib import Path

from orchestrator.repository_intelligence import build_repository_map, format_repository_map


def _repo_files(repo_path, limit=500):
    repo = Path(repo_path)
    if not repo.exists():
        return []

    ignored = {".git", "node_modules", ".next", "dist", "build", "__pycache__"}

    files = []
    for path in repo.rglob("*"):
        if len(files) >= limit:
            break
        if not path.is_file():
            continue
        if any(part in ignored for part in path.parts):
            continue
        try:
            files.append(str(path.relative_to(repo)))
        except Exception:
            files.append(str(path))

    return sorted(files)


def _affected_by_keywords(files, task):
    text = task.lower()
    scored = []

    for file in files:
        score = 0
        low = file.lower()

        for token in text.replace("/", " ").replace("-", " ").replace("_", " ").split():
            if len(token) >= 4 and token in low:
                score += 1

        if "source" in text and "source" in low:
            score += 5
        if "ui" in text and (low.endswith(".tsx") or "component" in low):
            score += 3
        if "api" in text and "api" in low:
            score += 3
        if "test" in text and ("test" in low or "spec" in low):
            score += 3

        if score:
            scored.append((score, file))

    return [file for _, file in sorted(scored, reverse=True)[:30]]


def build_runtime_analysis_context(task, repo_path=""):
    files = _repo_files(repo_path) if repo_path else []
    repo_map = build_repository_map(files)
    repo_map_text = format_repository_map(repo_map)
    affected = _affected_by_keywords(files, task)

    return {
        "task": task,
        "repo_path": repo_path,
        "files_count": len(files),
        "affected_files": affected,
        "repository_map": repo_map,
        "repository_map_text": repo_map_text,
        "summary": [
            f"repository files indexed: {len(files)}",
            f"affected files detected: {len(affected)}",
            "repository intelligence attached",
        ],
    }
