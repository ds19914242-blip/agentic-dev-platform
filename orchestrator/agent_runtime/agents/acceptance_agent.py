from orchestrator.agent_runtime.agent import Agent
from orchestrator.agent_runtime.context import AgentContext
from orchestrator.agent_runtime.result import AgentResult
from orchestrator.acceptance.runner import run_acceptance


class AcceptanceAgent(Agent):
    name = "acceptance"

    def run(self, context: AgentContext) -> AgentResult:
        if context.inputs.get("dry_run"):
            return AgentResult(
                status="skipped",
                confidence=0.0,
                findings=["AcceptanceAgent skipped by dry_run"],
                handoff={"dry_run": True},
            )

        epic_dir = context.inputs.get("epic_dir")

        if not epic_dir:
            return AgentResult(
                status="skipped",
                confidence=0.0,
                findings=["AcceptanceAgent skipped: no epic_dir provided"],
            )

        result = run_acceptance(
            epic_dir=epic_dir,
            product_name=context.product,
        )

        return AgentResult(
            status="passed" if result.passed else "failed",
            confidence=1.0 if result.passed else 0.2,
            artifacts=["acceptance-result.md", "acceptance-result.json"],
            findings=[
                "Acceptance passed" if result.passed else "Acceptance failed",
                f"Command: {result.command}",
            ],
            handoff={
                "passed": result.passed,
                "returncode": result.returncode,
                "command": result.command,
            },
        )
