from pathlib import Path

from orchestrator.agent_runtime.agent import Agent
from orchestrator.agent_runtime.context import AgentContext
from orchestrator.agent_runtime.platform_systems import write_runtime_json, write_runtime_markdown
from orchestrator.agent_runtime.result import AgentResult
from orchestrator.claude_executor import run_claude
from orchestrator.prompt_builder import build_feature_prompt


class ImplementationPlanningAgent(Agent):
    name = "implementation"

    def run(self, context: AgentContext) -> AgentResult:
        execute_writes = bool(context.inputs.get("execute_writes"))
        analysis = context.inputs.get("analysis_context", {})
        affected = analysis.get("affected_files", [])
        repo_context = analysis.get("repository_map_text", "")

        prompt = build_feature_prompt(
            feature=context.task,
            repo_path=context.repo_path,
            affected=affected,
            context=repo_context,
            mode="implement" if execute_writes else "plan_only",
        )

        handoff = {
            "task": context.task,
            "repo_path": context.repo_path,
            "affected_files": affected,
            "prompt": prompt,
            "execute_writes": execute_writes,
        }

        artifacts = []

        if context.run_dir:
            prompt_path = write_runtime_markdown(
                context.run_dir,
                "runtime-implementation-prompt.md",
                "# Runtime Implementation Prompt\n\n" + prompt,
                stage="implementation",
            )
            handoff_path = write_runtime_json(
                context.run_dir,
                "runtime-implementation-handoff.json",
                handoff,
                stage="implementation",
            )
            artifacts = [str(prompt_path), str(handoff_path)]

        if not execute_writes:
            return AgentResult(
                status="completed",
                confidence=0.7,
                artifacts=artifacts,
                findings=[
                    "Implementation prompt prepared with existing prompt_builder",
                    f"Affected files: {len(affected)}",
                    "Code writes disabled",
                ],
                handoff=handoff,
            )

        if not context.repo_path:
            return AgentResult(
                status="failed",
                confidence=0.1,
                artifacts=artifacts,
                findings=["Implementation failed: repo_path is required for code writes"],
                handoff=handoff,
            )

        try:
            response = run_claude(
                repo_path=context.repo_path,
                prompt=prompt,
                allow_writes=True,
                max_turns=int(context.inputs.get("max_turns", 5)),
                retries=1,
            )

            if context.run_dir:
                response_path = write_runtime_markdown(
                    context.run_dir,
                    "runtime-implementation-response.md",
                    "# Runtime Implementation Response\n\n" + response,
                    stage="implementation",
                )
                artifacts.append(str(response_path))

            return AgentResult(
                status="completed",
                confidence=0.85,
                artifacts=artifacts,
                findings=["Claude implementation completed through existing claude_executor"],
                handoff={**handoff, "response": response},
            )

        except Exception as exc:
            return AgentResult(
                status="failed",
                confidence=0.1,
                artifacts=artifacts,
                findings=[f"Implementation failed: {exc}"],
                handoff=handoff,
            )
