import argparse
from pathlib import Path

from orchestrator.agent_runtime.orchestrator import run_runtime_orchestrator


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("task_path")
    parser.add_argument("--product", default="rss-agent-lab_2")
    parser.add_argument("--repo-path", default="")
    parser.add_argument("--output-dir", default="")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--execute-writes", action="store_true")
    parser.add_argument("--llm-planner", action="store_true")
    parser.add_argument("--recovery", action="store_true")
    args = parser.parse_args()

    task_path = Path(args.task_path)
    task = task_path.read_text(errors="ignore")
    output_dir = args.output_dir or f"runs/runtime-task-{task_path.stem}"

    result = run_runtime_orchestrator(
        task=task,
        product=args.product,
        repo_path=args.repo_path,
        output_dir=output_dir,
        dry_run=not args.execute,
        inputs={
            "task_path": str(task_path),
            "epic_dir": str(task_path.parent),
            "execute_writes": args.execute_writes,
            "use_llm_planner": args.llm_planner,
            "recovery_enabled": args.recovery,
        },
    )

    print("Runtime task completed")
    print(f"Task: {task_path}")
    print(f"Output: {result['output_dir']}")
    print(f"Report: {result['report_path']}")


if __name__ == "__main__":
    main()
