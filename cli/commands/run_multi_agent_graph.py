import argparse
from pathlib import Path

from orchestrator.agent_runtime.context import AgentContext
from orchestrator.agent_runtime.executor import AgentGraphExecutor
from orchestrator.agent_runtime.multi_graph_factory import create_multi_agent_graph
from orchestrator.agent_runtime.result_store import write_agent_report, write_agent_results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("task", nargs="?", default="Multi-agent graph smoke task")
    parser.add_argument("--product", default="")
    parser.add_argument("--repo-path", default="")
    parser.add_argument("--output-dir", default="runs/multi-agent-graph-smoke")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--max-workers", type=int, default=3)
    args = parser.parse_args()

    context = AgentContext(
        task=args.task,
        product=args.product,
        repo_path=args.repo_path,
        run_dir=args.output_dir,
        inputs={"dry_run": args.dry_run},
    )

    graph = create_multi_agent_graph()
    executor = AgentGraphExecutor(max_workers=args.max_workers)
    results = executor.run(graph, context)

    output_dir = Path(args.output_dir)
    json_path = write_agent_results(output_dir, results)
    report_path = write_agent_report(output_dir, results)

    print("Multi-agent graph completed")
    print(f"Results: {json_path}")
    print(f"Report: {report_path}")

    for node_id, result in results.items():
        print(f"{node_id}: {result.status} confidence={result.confidence}")


if __name__ == "__main__":
    main()
