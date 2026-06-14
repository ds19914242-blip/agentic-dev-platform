import json
from pathlib import Path

from orchestrator.agent_runtime.agent import Agent
from orchestrator.agent_runtime.context import AgentContext
from orchestrator.agent_runtime.result import AgentResult


class ImplementationPlanningAgent(Agent):
    name = "implementation"

    def run(self, context: AgentContext) -> AgentResult:
        plan = {
            "task": context.task,
            "status": "planned",
            "note": "This runtime implementation agent prepares execution handoff. Code-writing remains in the existing implementation pipeline until fully migrated.",
        }

        artifacts = []

        if context.run_dir:
            run_dir = Path(context.run_dir)
            run_dir.mkdir(parents=True, exist_ok=True)

            md_path = run_dir / "runtime-implementation-plan.md"
            json_path = run_dir / "runtime-implementation-plan.json"

            md_path.write_text(
                "# Runtime Implementation Plan\n\n"
                f"Task: {context.task}\n\n"
                "Status: planned\n\n"
                "Code-writing is still delegated to the existing implementation pipeline.\n"
            )

            json_path.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n")
            artifacts = [str(md_path), str(json_path)]

        return AgentResult(
            status="completed",
            confidence=0.6,
            artifacts=artifacts,
            findings=["Implementation handoff prepared"],
            handoff={"implementation_plan": plan},
        )
