import argparse
import subprocess
from pathlib import Path


def run(command, cwd=None):
    print("$ " + " ".join(command), flush=True)
    result = subprocess.run(command, cwd=cwd)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--platform", default="/Users/danilsmetanev/Projects/agentic-dev-platform")
    parser.add_argument("--product", default="/Users/danilsmetanev/Projects/rss-agent-lab_2")
    parser.add_argument("--run-dir", default="runs/v16-full-acceptance")
    parser.add_argument("--task", default="Full runtime acceptance and recovery verification")
    parser.add_argument("--epic-dir", default="")
    parser.add_argument("--execute-writes", action="store_true")
    parser.add_argument("--execute-release", action="store_true")
    args = parser.parse_args()

    platform = Path(args.platform)
    product = Path(args.product)
    run_dir = platform / args.run_dir

    run_dir.mkdir(parents=True, exist_ok=True)

    run([
        "python3",
        "agentic.py",
        "feature",
        args.task,
        "--product",
        "rss-agent-lab_2",
        "--repo-path",
        str(product),
        "--output-dir",
        str(run_dir / "runtime"),
        "--execute",
        "--recovery",
    ] + (["--execute-writes"] if args.execute_writes else []), cwd=platform)

    run(["python3", "agentic.py", "runtime-monitor", str(run_dir / "runtime")], cwd=platform)

    run(["npx", "tsc", "--noEmit"], cwd=product)
    run(["npm", "run", "build"], cwd=product)

    if args.epic_dir:
        run([
            "python3",
            "agentic.py",
            "runtime-orchestrator",
            "Run runtime acceptance evidence check",
            "--product",
            "rss-agent-lab_2",
            "--repo-path",
            str(product),
            "--output-dir",
            str(run_dir / "acceptance"),
            "--execute",
            "--epic-dir",
            args.epic_dir,
        ], cwd=platform)

    if args.execute_release and args.epic_dir:
        task_candidates = sorted(Path(args.epic_dir).glob("task-*.md"))
        if not task_candidates:
            raise SystemExit("No task-*.md found for release check")
        run([
            "python3",
            "agentic.py",
            "release-check",
            str(task_candidates[-1]),
            "--product",
            "rss-agent-lab_2",
        ], cwd=platform)

    report = run_dir / "FULL_ACCEPTANCE.md"
    report.write_text(
        "# Runtime Full Acceptance\n\n"
        "- runtime orchestrator executed\n"
        "- runtime monitor events captured\n"
        "- typecheck passed\n"
        "- build passed\n"
        f"- epic acceptance executed: {bool(args.epic_dir)}\n"
        f"- release executed: {bool(args.execute_release and args.epic_dir)}\n"
    )

    print(f"DONE: {report}")


if __name__ == "__main__":
    main()
