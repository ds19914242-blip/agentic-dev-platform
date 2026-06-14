import os
from pathlib import Path

from orchestrator.agent_runtime.analysis_context import build_runtime_analysis_context
from orchestrator.agent_runtime.context import AgentContext
from orchestrator.agent_runtime.dynamic_graph_factory import create_dynamic_agent_graph
from orchestrator.agent_runtime.executor import AgentGraphExecutor
from orchestrator.agent_runtime.result_store import write_agent_report, write_agent_results
from orchestrator.agent_runtime.observability.report import write_runtime_timeline
from orchestrator.agent_runtime.observability.events import write_runtime_event


def _resolve_repo_path(product, repo_path):
    if repo_path:
        return repo_path

    if not product:
        return ""

    try:
        from orchestrator.product_registry import load_product_config

        config = load_product_config(product)
        return config.get("repo_path", "")
    except Exception:
        return ""


def run_runtime_orchestrator(
    task,
    product="",
    repo_path="",
    output_dir="runs/runtime-orchestrator",
    dry_run=True,
    max_workers=3,
    inputs=None,
):
    repo_path = _resolve_repo_path(product, repo_path)
    payload = dict(inputs or {})

    graph, plan = create_dynamic_agent_graph(
        task,
        repo_path=repo_path,
        product=product,
        use_llm_planner=bool(payload.get("use_llm_planner")),
    )

    payload["dry_run"] = dry_run
    payload["graph_plan"] = plan

    write_runtime_event(output_dir, {"agent": "analysis", "status": "started"})
    payload["analysis_context"] = build_runtime_analysis_context(task, repo_path=repo_path)
    write_runtime_event(
        output_dir,
        {
            "agent": "analysis",
            "status": "completed",
            "message": f"affected_files={len(payload['analysis_context'].get('affected_files', []))}",
        },
    )

    context = AgentContext(
        task=task,
        product=product,
        repo_path=repo_path,
        run_dir=output_dir,
        inputs=payload,
    )

    if output_dir:
        os.environ["AGENTIC_RUN_DIR"] = str(output_dir)

    results = AgentGraphExecutor(max_workers=max_workers).run(graph, context)

    output = Path(output_dir)
    results_path = write_agent_results(output, results)
    report_path = write_agent_report(output, results)
    timeline_path = write_runtime_timeline(output)

    return {
        "plan": plan,
        "results": results,
        "results_path": str(results_path),
        "report_path": str(report_path),
        "timeline_path": str(timeline_path),
        "output_dir": str(output),
    }
