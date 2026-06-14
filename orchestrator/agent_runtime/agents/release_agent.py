from orchestrator.agent_runtime.agent import Agent
from orchestrator.agent_runtime.context import AgentContext
from orchestrator.agent_runtime.result import AgentResult
from orchestrator.deployment.production_verifier import verify_production_release


class ReleaseAgent(Agent):
    name = "release"

    def run(self, context: AgentContext) -> AgentResult:
        task_path = context.inputs.get("task_path")

        if not context.product:
            return AgentResult(
                status="failed",
                confidence=0.0,
                findings=["ReleaseAgent requires context.product"],
            )

        if not task_path:
            return AgentResult(
                status="skipped",
                confidence=0.0,
                findings=["ReleaseAgent skipped: no task_path in context.inputs"],
            )

        result = verify_production_release(
            task_path=task_path,
            product_name=context.product,
        )

        return AgentResult(
            status="passed" if result.get("passed") else "failed",
            confidence=1.0 if result.get("passed") else 0.2,
            artifacts=[
                result.get("release_markdown", ""),
                result.get("release_json", ""),
            ],
            findings=[
                f"Production URL: {result.get('production_url')}",
                f"Release verification: {'passed' if result.get('passed') else 'failed'}",
            ],
            handoff=result,
        )
