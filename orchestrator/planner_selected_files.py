from pathlib import Path


def extract_files_from_plan(plan_text, repo_files):
    selected = []
    repo_file_set = set(repo_files)

    for file in repo_files:
        if file in plan_text:
            selected.append(file)

    return sorted(set(selected))


def write_planner_selected_files(run_dir, files):
    path = Path(run_dir) / "planner-selected-files.md"

    path.write_text(
        "# Planner Selected Files\n\n"
        + ("\n".join(f"- {f}" for f in files) if files else "_None_")
        + "\n"
    )

    return path
