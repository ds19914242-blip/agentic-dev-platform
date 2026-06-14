import json
from pathlib import Path

from orchestrator.agent_runtime.agent import Agent
from orchestrator.agent_runtime.context import AgentContext
from orchestrator.agent_runtime.platform_systems import write_runtime_json, write_runtime_markdown
from orchestrator.agent_runtime.result import AgentResult
from orchestrator.verification_evidence import build_verification_evidence, write_verification_evidence


class ReviewAgent(Agent):
    name = "review"

    def run(self, context: AgentContext) -> AgentResult:
        agent_results = context.inputs.get("agent_results", {})
        validation_result = agent_results.get("validation")
        acceptance_result = agent_results.get("acceptance")
        task_path = context.inputs.get("task_path")

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
            "summary": "Runtime review completed with existing evidence layer.",
            "risks": risks,
            "task": context.task,
            "has_validation_evidence": validation_result is not None,
            "has_acceptance_evidence": acceptance_result is not None,
        }

        artifacts = []

        if context.run_dir:
            md = (
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

            md_path = write_runtime_markdown(context.run_dir, "runtime-review.md", md, stage="review")
            json_path = write_runtime_json(context.run_dir, "runtime-review.json", review, stage="review")
            artifacts.extend([str(md_path), str(json_path)])

        if task_path:
            try:
                evidence = build_verification_evidence(
                    task_path=task_path,
                    task_text=context.task,
                    status="manual_verification_passed" if review_status == "passed" else "manual_verification_failed",
                    note=review["summary"],
                )
                md_path, json_path = write_verification_evidence(Path(task_path).parent, evidence)
                artifacts.extend([str(md_path), str(json_path)])
            except Exception as exc:
                risks.append(f"Verification evidence write failed: {exc}")

        return AgentResult(
            status="passed" if review_status == "passed" else "needs_evidence",
            confidence=0.85 if review_status == "passed" else 0.45,
            artifacts=artifacts,
            findings=["Runtime review completed with existing verification evidence layer"],
            handoff={"review": review},
        )
