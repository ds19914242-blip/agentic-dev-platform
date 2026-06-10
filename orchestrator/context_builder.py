from pathlib import Path


def read_context(repo_path, affected_files):
    chunks = []

    for file in affected_files:
        path = Path(repo_path) / file

        if path.exists():
            chunks.append(f"\n\n# FILE: {file}\n\n")
            chunks.append(path.read_text(errors="ignore")[:8000])

    return "".join(chunks)
