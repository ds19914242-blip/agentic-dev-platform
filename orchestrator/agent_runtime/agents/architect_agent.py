from orchestrator.agent_runtime.agent import Agent
from orchestrator.agent_runtime.context import AgentContext
from orchestrator.agent_runtime.result import AgentResult


class ArchitectAgent(Agent):
    name = "architect"

    def run(self, context: AgentContext) -> AgentResult:
        task = context.task.strip()

        findings = [
            "Architecture plan created",
            "Split work into backend, frontend, and QA planning lanes",
        ]

        handoff = {
            "task": task,
            "lanes": {
                "backend": {
                    "goal": "Identify data, API, state, and persistence changes required for the task.",
                    "scope": "backend, services, API routes, data models, validation logic",
                },
                "frontend": {
                    "goal": "Identify UI, interaction, copy, and user-visible changes required for the task.",
                    "scope": "pages, components, forms, navigation, visual feedback",
                },
                "qa": {
                    "goal": "Define verification strategy and user-visible acceptance evidence.",
                    "scope": "manual checks, Playwright scenarios, regression risks",
                },
            },
            "risks": [
                "implementation may touch product-specific assumptions",
                "acceptance evidence must verify visible user outcome",
                "release verification should be skipped unless task_path is explicit",
            ],
        }

        artifacts = []

        if context.run_dir:
            from pathlib import Path
            import json

            run_dir = Path(context.run_dir)
            run_dir.mkdir(parents=True, exist_ok=True)

            plan_path = run_dir / "architect-plan.md"
            json_path = run_dir / "architect-handoff.json"

            plan_path.write_text(
                "# Architect Plan\n\n"
                f"Task: {task}\n\n"
                "## Lanes\n\n"
                "- backend\n"
                "- frontend\n"
                "- qa\n\n"
                "## Risks\n\n"
                + "\n".join(f"- {risk}" for risk in handoff["risks"])
                + "\n"
            )

            json_path.write_text(json.dumps(handoff, indent=2, ensure_ascii=False) + "\n")

            artifacts = [str(plan_path), str(json_path)]

        return AgentResult(
            status="completed",
            confidence=0.7,
            artifacts=artifacts,
            findings=findings,
            handoff=handoff,
        )
