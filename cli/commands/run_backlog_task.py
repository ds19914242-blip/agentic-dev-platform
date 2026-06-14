import argparse

from orchestrator.services.task_execution_service import (
    run_interactive_task,
    run_task_path,
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("task_path", nargs="?")
    parser.add_argument("--product", default="rss-agent-lab_2")
    parser.add_argument("--repo-path", default=None)
    args = parser.parse_args()

    if args.task_path:
        run_task_path(
            args.task_path,
            product_name=args.product,
            repo_path=args.repo_path,
        )
        return

    run_interactive_task()


if __name__ == "__main__":
    main()
