from orchestrator.agent_runtime.agent import Agent
from orchestrator.agent_runtime.context import AgentContext
from orchestrator.agent_runtime.result import AgentResult
from orchestrator.product_registry import load_product_config
from orchestrator.validation_runner import run_validators, write_validation_report


class ValidationAgent(Agent):
    name = "validation"

    def run(self, context: AgentContext) -> AgentResult:
        if context.inputs.get("dry_run"):
            return AgentResult(
                status="skipped",
                confidence=0.0,
                findings=["ValidationAgent skipped by dry_run"],
                handoff={"dry_run": True},
            )

        if not context.product:
            return AgentResult(
                status="failed",
                confidence=0.0,
                findings=["ValidationAgent requires context.product"],
            )

        product = load_product_config(context.product)
        repo_path = context.repo_path or product.get("repo_path")
        validators = product.get("validators", [])

        if not repo_path:
            return AgentResult(
                status="failed",
                confidence=0.0,
                findings=["No repo_path configured"],
            )

        results = run_validators(repo_path, validators)

        artifacts = []
        if context.run_dir:
            _, ok = write_validation_report(context.run_dir, results)
            artifacts = ["validation.md", "validation.json"]
        else:
            ok = all(
                (not item.get("required", True)) or item.get("passed", item.get("ok", False))
                for item in results
            )

        findings = [
            f"{item.get('name')}: {'passed' if item.get('passed', item.get('ok', False)) else 'failed'}"
            for item in results
        ]

        return AgentResult(
            status="passed" if ok else "failed",
            confidence=1.0 if ok else 0.2,
            artifacts=artifacts,
            findings=findings,
            handoff={
                "repo_path": repo_path,
                "validators": len(validators),
            },
        )
