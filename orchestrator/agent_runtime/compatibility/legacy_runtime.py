from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict

from orchestrator.agent_runtime.context import AgentContext
from orchestrator.agent_runtime.builtin_agents import create_builtin_registry
from orchestrator.agent_runtime.result_store import write_agent_report, write_agent_results


@dataclass
class LegacyAgentRunContext:
    agent: str
    run_dir: str = ""
    product_name: str = ""
    repo_path: str = ""
    feature: str = ""
    task_path: str = ""
    inputs: dict = field(default_factory=dict)


@dataclass
class LegacyAgentResult:
    agent: str
    status: str
    summary: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


def _legacy_status(status):
    if status in {"passed", "completed", "ok"}:
        return "passed"
    if status == "skipped":
        return "skipped"
    return "failed"


def _to_agent_context(context: LegacyAgentRunContext) -> AgentContext:
    inputs = dict(context.inputs or {})
    if context.task_path:
        inputs["task_path"] = context.task_path

    return AgentContext(
        task=context.feature or context.inputs.get("task", ""),
        product=context.product_name,
        repo_path=context.repo_path,
        run_dir=context.run_dir,
        inputs=inputs,
    )


def _to_legacy_result(agent_name, result):
    return LegacyAgentResult(
        agent=agent_name,
        status=_legacy_status(result.status),
        summary="; ".join(result.findings or []),
        metadata={
            "confidence": result.confidence,
            "artifacts": result.artifacts,
            "findings": result.findings,
            "handoff": result.handoff,
            **(result.handoff or {}),
        },
    )


def run_runtime_agent(agent_name, context: LegacyAgentRunContext):
    registry = create_builtin_registry()
    definition = registry.get(agent_name)
    result = definition.factory().run(_to_agent_context(context))

    if context.run_dir:
        output_dir = Path(context.run_dir) / "agent-runtime" / agent_name
        write_agent_results(output_dir, {agent_name: result})
        write_agent_report(output_dir, {agent_name: result})

    return _to_legacy_result(agent_name, result)
