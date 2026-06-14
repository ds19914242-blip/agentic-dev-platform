import json
from pathlib import Path

from orchestrator.agent_runtime.agent import Agent
from orchestrator.agent_runtime.context import AgentContext
from orchestrator.agent_runtime.result import AgentResult


class ReviewAgent(Agent):
    name = "review"

    def run(self, context: AgentContext) -> AgentResult:
        agent_results = context.inputs.get("agent_results", {})
        validation_result = agent_results.get("validation")
        acceptance_result = agent_results.get("acceptance")

        risks = []

        if validation_result is None:
            risks.append("Validation evidence is missing.")
        elif not validation_result.ok:
            risks.append("Validation did not pass.")

        if acceptance_result is None:
            risks.append("Acceptance evidence is not available yet.")
        elif not acceptance_result.ok:
            risks.append("Acceptance did not pass.")

        review_status = "passed" if not risks else "needs_evidence"

        review = {
            "status": review_status,
            "summary": "Runtime review completed with evidence check.",
            "risks": risks,
            "task": context.task,
            "has_validation_evidence": validation_result is not None,
            "has_acceptance_evidence": acceptance_result is not None,
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
                f"Status: {review_status}\n\n"
                "## Evidence\n\n"
                f"- Validation evidence: {review['has_validation_evidence']}\n"
                f"- Acceptance evidence: {review['has_acceptance_evidence']}\n\n"
                "## Risks\n\n"
                + ("\n".join(f"- {risk}" for risk in risks) if risks else "- none")
                + "\n"
            )

            json_path.write_text(json.dumps(review, indent=2, ensure_ascii=False) + "\n")
            artifacts = [str(md_path), str(json_path)]

        return AgentResult(
            status="passed" if review_status == "passed" else "needs_evidence",
            confidence=0.8 if review_status == "passed" else 0.4,
            artifacts=artifacts,
            findings=["Runtime review completed with evidence check"],
            handoff={"review": review},
        )
