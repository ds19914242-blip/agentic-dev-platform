import json
import shutil
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from orchestrator.backlog_dag import (
    ensure_epic_depends_on_sections,
    load_epic_tasks,
    ready_tasks,
    write_dag_json,
)
from orchestrator.product_registry import load_product_config


PRODUCT_NAME = "rss-agent-lab_2"
WORKTREE_LOCK = threading.Lock()


def run(cmd, cwd=None, check=True):
    result = subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        capture_output=True,
    )

    if check and result.returncode != 0:
        raise RuntimeError(
            f"Command failed: {' '.join(cmd)}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )

    return result


def latest_epic_dir():
    dirs = sorted(Path("backlog").glob("*"), key=lambda p: p.stat().st_mtime, reverse=True)
    dirs = [p for p in dirs if p.is_dir()]
    if not dirs:
        raise SystemExit("No backlog epic directories found")
    return dirs[0]


def safe_branch_name(task_id):
    return f"agentic/worktree-{task_id}"


def prepare_worktree(base_repo, worktrees_root, task_id):
    branch = safe_branch_name(task_id)
    worktree_path = worktrees_root / task_id

    if worktree_path.exists():
        shutil.rmtree(worktree_path)

    # Delete local branch if left over from previous failed run.
    run(["git", "branch", "-D", branch], cwd=base_repo, check=False)

    run(["git", "fetch", "origin"], cwd=base_repo, check=False)

    run(
        ["git", "worktree", "add", "-B", branch, str(worktree_path), "origin/main"],
        cwd=base_repo,
    )

    base_node_modules = base_repo / "node_modules"
    worktree_node_modules = worktree_path / "node_modules"

    if base_node_modules.exists() and not worktree_node_modules.exists():
        worktree_node_modules.symlink_to(base_node_modules, target_is_directory=True)

    return worktree_path, branch


def cleanup_worktree(base_repo, worktree_path):
    run(["git", "worktree", "remove", "--force", str(worktree_path)], cwd=base_repo, check=False)
    run(["git", "worktree", "prune"], cwd=base_repo, check=False)


def run_task(task, base_repo, worktrees_root):
    task_id = task["id"]

    # git worktree add mutates the main repo .git/config,
    # so worktree creation must be serialized even when task execution is parallel.
    with WORKTREE_LOCK:
        worktree_path, branch = prepare_worktree(base_repo, worktrees_root, task_id)

    try:
        result = subprocess.run(
            [
                "python3",
                "run_backlog_task.py",
                task["path"],
                "--repo-path",
                str(worktree_path),
                "--product",
                PRODUCT_NAME,
            ],
            text=True,
            capture_output=True,
        )

        return {
            "task": task_id,
            "path": task["path"],
            "branch": branch,
            "worktree": str(worktree_path),
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

    finally:
        cleanup_worktree(base_repo, worktree_path)


def main():
    epic_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else latest_epic_dir()
    max_workers = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    product = load_product_config(PRODUCT_NAME)
    base_repo = Path(product["repo_path"]).resolve()

    worktrees_root = base_repo.parent / f"{base_repo.name}-worktrees"
    worktrees_root.mkdir(parents=True, exist_ok=True)

    ensure_epic_depends_on_sections(epic_dir)
    write_dag_json(epic_dir)

    ready = ready_tasks(load_epic_tasks(epic_dir))

    if not ready:
        print("No ready backlog tasks")
        return

    print(f"Ready tasks: {', '.join(task['id'] for task in ready)}")
    print(f"Parallel workers: {max_workers}")
    print(f"Worktrees root: {worktrees_root}")

    failed = False
    selected = ready[:max_workers]

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(run_task, task, base_repo, worktrees_root) for task in selected]

        for future in as_completed(futures):
            result = future.result()

            print()
            print(f"=== {result['task']} ===")
            print(f"Return code: {result['returncode']}")
            print(f"Branch: {result['branch']}")
            print(f"Worktree: {result['worktree']}")

            if result["stdout"]:
                print("--- STDOUT ---")
                print(result["stdout"])

            if result["stderr"]:
                print("--- STDERR ---")
                print(result["stderr"])

            if result["returncode"] != 0:
                failed = True

    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
