import argparse

from orchestrator.agent_runtime.compatibility.legacy_runtime import (
    LegacyAgentRunContext,
    run_runtime_agent,
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("agent")
    parser.add_argument("task", nargs="?", default="")
    parser.add_argument("--product", default="")
    parser.add_argument("--repo-path", default="")
    parser.add_argument("--run-dir", default="runs/agent-command")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    result = run_runtime_agent(
        args.agent,
        LegacyAgentRunContext(
            agent=args.agent,
            run_dir=args.run_dir,
            product_name=args.product,
            repo_path=args.repo_path,
            feature=args.task,
            inputs={"dry_run": args.dry_run},
        ),
    )

    print(f"Agent: {result.agent}")
    print(f"Status: {result.status}")
    print(f"Summary: {result.summary}")

    if result.metadata:
        print("Metadata:")
        for key in sorted(result.metadata):
            print(f"- {key}")


if __name__ == "__main__":
    main()
