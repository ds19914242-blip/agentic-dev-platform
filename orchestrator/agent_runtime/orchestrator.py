from pathlib import Path

from orchestrator.agent_runtime.context import AgentContext
from orchestrator.agent_runtime.dynamic_graph_factory import create_dynamic_agent_graph
from orchestrator.agent_runtime.executor import AgentGraphExecutor
from orchestrator.agent_runtime.result_store import write_agent_report, write_agent_results
from orchestrator.agent_runtime.analysis_context import build_runtime_analysis_context


def run_runtime_orchestrator(
    task,
    product="",
    repo_path="",
    output_dir="runs/runtime-orchestrator",
    dry_run=True,
    max_workers=3,
    inputs=None,
):
    graph, plan = create_dynamic_agent_graph(task)

    payload = dict(inputs or {})
    payload["dry_run"] = dry_run
    payload["graph_plan"] = plan
    payload["analysis_context"] = build_runtime_analysis_context(task, repo_path=repo_path)

    context = AgentContext(
        task=task,
        product=product,
        repo_path=repo_path,
        run_dir=output_dir,
        inputs=payload,
    )

    results = AgentGraphExecutor(max_workers=max_workers).run(graph, context)

    output = Path(output_dir)
    results_path = write_agent_results(output, results)
    report_path = write_agent_report(output, results)

    return {
        "plan": plan,
        "results": results,
        "results_path": str(results_path),
        "report_path": str(report_path),
        "output_dir": str(output),
    }
