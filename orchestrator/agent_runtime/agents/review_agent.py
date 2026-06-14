import json
from pathlib import Path

from orchestrator.agent_runtime.agent import Agent
from orchestrator.agent_runtime.context import AgentContext
from orchestrator.agent_runtime.result import AgentResult


class ReviewAgent(Agent):
    name = "review"

    def run(self, context: AgentContext) -> AgentResult:
        review = {
            "status": "passed",
            "summary": "Runtime review completed.",
            "risks": [
                "ReviewAgent is deterministic; LLM review is not wired yet.",
                "Use acceptance and validation evidence before release.",
            ],
            "task": context.task,
        }

        artifacts = []

        if context.run_dir:
            run_dir = Path(context.run_dir)
            run_dir.mkdir(parents=True, exist_ok=True)

            md_path = run_dir / "runtime-review.md"
            json_path = run_dir / "runtime-review.json"

            md_path.write_text(
                "# Runtime Review\n\n"
                f"Task: {context.task}\n\n"
                "Status: passed\n\n"
                "## Risks\n\n"
                + "\n".join(f"- {risk}" for risk in review["risks"])
                + "\n"
            )

            json_path.write_text(json.dumps(review, indent=2, ensure_ascii=False) + "\n")
            artifacts = [str(md_path), str(json_path)]

        return AgentResult(
            status="passed",
            confidence=0.65,
            artifacts=artifacts,
            findings=["Runtime review completed"],
            handoff={"review": review},
        )
