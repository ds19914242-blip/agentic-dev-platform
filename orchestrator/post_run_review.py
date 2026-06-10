from pathlib import Path
import subprocess


def get_changed_files(repo_path):
    result = subprocess.run(
        ["git", "status", "--short"],
        cwd=repo_path,
        text=True,
        capture_output=True,
    )

    files = []

    for line in result.stdout.splitlines():
        if not line.strip():
            continue

        parts = line.strip().split(maxsplit=1)

        if len(parts) == 2:
            files.append(parts[1])

    return sorted(files)


def read_expected_files(run_dir):
    path = Path(run_dir) / "affected-files.md"

    if not path.exists():
        return []

    files = []

    for line in path.read_text().splitlines():
        line = line.strip()

        if line.startswith("- "):
            files.append(line[2:])

    return sorted(files)


def create_post_run_review(run_dir, repo_path):
    expected = set(read_expected_files(run_dir))
    actual = set(get_changed_files(repo_path))

    unexpected = sorted(actual - expected)
    missing = sorted(expected - actual)
    matched = sorted(expected & actual)

    text = ["# Post Run Review", ""]

    text.append("## Expected Changed Files")
    text.append("")
    for f in sorted(expected):
        text.append(f"- {f}")
    if not expected:
        text.append("_None_")

    text.append("")
    text.append("## Actually Changed Files")
    text.append("")
    for f in sorted(actual):
        text.append(f"- {f}")
    if not actual:
        text.append("_None_")

    text.append("")
    text.append("## Matched Files")
    text.append("")
    for f in matched:
        text.append(f"- {f}")
    if not matched:
        text.append("_None_")

    text.append("")
    text.append("## Unexpected Changes")
    text.append("")
    for f in unexpected:
        text.append(f"- {f}")
    if not unexpected:
        text.append("_None_")

    text.append("")
    text.append("## Expected But Not Changed")
    text.append("")
    for f in missing:
        text.append(f"- {f}")
    if not missing:
        text.append("_None_")

    path = Path(run_dir) / "post-run-review.md"
    path.write_text("\n".join(text))

    return path
