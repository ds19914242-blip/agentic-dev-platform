from pathlib import Path
from orchestrator.agent_runtime.agent import Agent
from orchestrator.agent_runtime.context import AgentContext
from orchestrator.agent_runtime.result import AgentResult
from orchestrator.acceptance.runner import run_acceptance
from orchestrator.agent_runtime.platform_systems import register_runtime_existing


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

        artifacts = [
            str(epic_dir) + "/acceptance-result.md",
            str(epic_dir) + "/acceptance-result.json",
        ]

        if context.run_dir:
            for artifact in artifacts:
                register_runtime_existing(
                    context.run_dir,
                    Path(artifact).name,
                    artifact,
                    kind="markdown" if artifact.endswith(".md") else "json",
                    stage="acceptance",
                )

        return AgentResult(
            status="passed" if result.passed else "failed",
            confidence=1.0 if result.passed else 0.2,
            artifacts=artifacts,
            findings=[
                "Acceptance passed" if result.passed else "Acceptance failed",
                f"Command: {result.command}",
                f"Return code: {result.returncode}",
            ],
            handoff={
                "passed": result.passed,
                "returncode": result.returncode,
                "command": result.command,
                "epic_dir": str(epic_dir),
                "artifacts": artifacts,
                "stdout_tail": (result.stdout or "")[-1000:],
                "stderr_tail": (result.stderr or "")[-1000:],
            },
        )
