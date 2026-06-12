import argparse
import json

from orchestrator.agents.context import AgentRunContext
from orchestrator.agents.runtime import run_agent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("agent")
    parser.add_argument("--run-dir", default="")
    parser.add_argument("--product", default="")
    parser.add_argument("--repo-path", default="")
    parser.add_argument("--feature", default="")
    parser.add_argument("--task-path", default="")
    parser.add_argument("--input-json", default="{}")
    args = parser.parse_args()

    context = AgentRunContext(
        agent=args.agent,
        run_dir=args.run_dir,
        product_name=args.product,
        repo_path=args.repo_path,
        feature=args.feature,
        task_path=args.task_path,
        inputs=json.loads(args.input_json),
    )

    result = run_agent(args.agent, context)

    print(f"Agent: {result.agent}")
    print(f"Status: {result.status}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
