import argparse

from orchestrator.agent_runtime.orchestrator import run_runtime_orchestrator


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("task")
    parser.add_argument("--product", default="")
    parser.add_argument("--repo-path", default="")
    parser.add_argument("--output-dir", default="runs/runtime-orchestrator")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--max-workers", type=int, default=3)
    parser.add_argument("--epic-dir", default="")
    parser.add_argument("--task-path", default="")
    args = parser.parse_args()

    inputs = {}

    if args.epic_dir:
        inputs["epic_dir"] = args.epic_dir

    if args.task_path:
        inputs["task_path"] = args.task_path

    result = run_runtime_orchestrator(
        task=args.task,
        product=args.product,
        repo_path=args.repo_path,
        output_dir=args.output_dir,
        dry_run=not args.execute,
        max_workers=args.max_workers,
        inputs=inputs,
    )

    print("Runtime orchestrator completed")
    print(f"Output: {result['output_dir']}")
    print(f"Results: {result['results_path']}")
    print(f"Report: {result['report_path']}")
    print(f"Lanes: {', '.join(result['plan'].lanes)}")
    print(f"Requires acceptance: {result['plan'].requires_acceptance}")
    print(f"Requires release: {result['plan'].requires_release}")


if __name__ == "__main__":
    main()
