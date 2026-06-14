from orchestrator.agent_runtime.agent import Agent
from orchestrator.agent_runtime.context import AgentContext
from orchestrator.agent_runtime.result import AgentResult
from orchestrator.agent_runtime.platform_systems import write_runtime_json, write_runtime_markdown


class ArchitectAgent(Agent):
    name = "architect"

    def run(self, context: AgentContext) -> AgentResult:
        task = context.task.strip()

        analysis_context = context.inputs.get("analysis_context", {})

        findings = [
            "Architecture plan created",
            "Split work into backend, frontend, and QA planning lanes",
        ]

        if analysis_context.get("summary"):
            findings.extend(analysis_context.get("summary", []))

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
            "analysis_context": analysis_context,
            "risks": [
                "implementation may touch product-specific assumptions",
                "acceptance evidence must verify visible user outcome",
                "release verification should be skipped unless task_path is explicit",
            ],
        }

        artifacts = []

        if context.run_dir:
            from pathlib import Path

            run_dir = Path(context.run_dir)
            run_dir.mkdir(parents=True, exist_ok=True)

            plan_md = (
                "# Architect Plan\n\n"
                f"Task: {task}\n\n"
                "## Analysis Summary\n\n"
                + "\n".join(f"- {item}" for item in analysis_context.get("summary", []))
                + "\n\n"
                "## Lanes\n\n"
                "- backend\n"
                "- frontend\n"
                "- qa\n\n"
                "## Risks\n\n"
                + "\n".join(f"- {risk}" for risk in handoff["risks"])
                + "\n\n"
                "## Repository Map\n\n"
                + analysis_context.get("repository_map_text", "_No repository map._")
                + "\n"
            )

            plan_path = write_runtime_markdown(run_dir, "architect-plan.md", plan_md, stage="architect")
            json_path = write_runtime_json(run_dir, "architect-handoff.json", handoff, stage="architect")

            artifacts = [str(plan_path), str(json_path)]

        return AgentResult(
            status="completed",
            confidence=0.7,
            artifacts=artifacts,
            findings=findings,
            handoff=handoff,
        )
