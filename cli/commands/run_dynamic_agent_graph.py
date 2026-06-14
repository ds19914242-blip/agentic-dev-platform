import argparse
from pathlib import Path

from orchestrator.agent_runtime.context import AgentContext
from orchestrator.agent_runtime.dynamic_graph_factory import create_dynamic_agent_graph
from orchestrator.agent_runtime.executor import AgentGraphExecutor
from orchestrator.agent_runtime.result_store import write_agent_report, write_agent_results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("task")
    parser.add_argument("--product", default="")
    parser.add_argument("--repo-path", default="")
    parser.add_argument("--output-dir", default="runs/dynamic-agent-graph-smoke")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--max-workers", type=int, default=3)
    args = parser.parse_args()

    graph, plan = create_dynamic_agent_graph(args.task)

    context = AgentContext(
        task=args.task,
        product=args.product,
        repo_path=args.repo_path,
        run_dir=args.output_dir,
        inputs={"dry_run": args.dry_run, "graph_plan": plan},
    )

    results = AgentGraphExecutor(max_workers=args.max_workers).run(graph, context)

    output_dir = Path(args.output_dir)
    write_agent_results(output_dir, results)
    write_agent_report(output_dir, results)

    print("Dynamic agent graph completed")
    print(f"Lanes: {', '.join(plan.lanes)}")
    print(f"Requires acceptance: {plan.requires_acceptance}")
    print(f"Requires release: {plan.requires_release}")
    print(f"Nodes: {', '.join(graph.results.keys())}")


if __name__ == "__main__":
    main()
