import json
from pathlib import Path

from orchestrator.agent_runtime.agent import Agent
from orchestrator.agent_runtime.context import AgentContext
from orchestrator.agent_runtime.result import AgentResult


class LaneAgent(Agent):
    lane = "lane"
    name = "lane"

    def _lane_handoff(self, context: AgentContext):
        agent_results = context.inputs.get("agent_results", {})
        architect = agent_results.get("architect")

        if architect and getattr(architect, "handoff", None):
            return architect.handoff.get("lanes", {}).get(self.lane, {})

        return {}

    def run(self, context: AgentContext) -> AgentResult:
        handoff = self._lane_handoff(context)

        goal = handoff.get("goal", f"Prepare {self.lane} work plan")
        scope = handoff.get("scope", "")

        result_handoff = {
            "lane": self.lane,
            "task": context.task,
            "goal": goal,
            "scope": scope,
            "status": "planned",
        }

        artifacts = []

        if context.run_dir:
            run_dir = Path(context.run_dir)
            run_dir.mkdir(parents=True, exist_ok=True)

            md_path = run_dir / f"{self.lane}-lane-plan.md"
            json_path = run_dir / f"{self.lane}-lane-handoff.json"

            md_path.write_text(
                f"# {self.lane.title()} Lane Plan\n\n"
                f"Task: {context.task}\n\n"
                f"Goal: {goal}\n\n"
                f"Scope: {scope}\n"
            )

            json_path.write_text(json.dumps(result_handoff, indent=2, ensure_ascii=False) + "\n")

            artifacts = [str(md_path), str(json_path)]

        return AgentResult(
            status="completed",
            confidence=0.6,
            artifacts=artifacts,
            findings=[f"{self.lane} lane plan created"],
            handoff=result_handoff,
        )


class BackendImplementationAgent(LaneAgent):
    lane = "backend"
    name = "implementation_backend"


class FrontendImplementationAgent(LaneAgent):
    lane = "frontend"
    name = "implementation_frontend"


class QAPlanAgent(LaneAgent):
    lane = "qa"
    name = "qa_plan"
