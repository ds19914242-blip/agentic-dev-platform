from orchestrator.agents.result import failed, passed
from orchestrator.run_artifacts import register_artifacts
from orchestrator.run_context import update_run_context
from orchestrator.validation_runner import run_validators, write_validation_report


def execute_validator(context):
    product = context.inputs.get("product", {})
    validators = product.get("validators", [])

    if not context.repo_path:
        return failed(
            "validator",
            "Validator cannot run because repo_path is missing.",
            next_actions=["Provide repo_path in AgentRunContext."],
        )

    if not context.run_dir:
        return failed(
            "validator",
            "Validator cannot run because run_dir is missing.",
            next_actions=["Provide run_dir in AgentRunContext."],
        )

    validation_results = run_validators(context.repo_path, validators)
    _, validation_ok = write_validation_report(context.run_dir, validation_results)
    register_artifacts(context.run_dir, ["validation.md", "validation.json"], stage="validation")
    update_run_context(context.run_dir, validation_passed=validation_ok)

    if validation_ok:
        return passed(
            "validator",
            "Validation passed.",
            artifacts=["validation.md", "validation.json"],
            metadata={"validation_passed": True},
        )

    return failed(
        "validator",
        "Validation failed.",
        artifacts=["validation.md", "validation.json"],
        next_actions=["Run replanner or create recovery bug task."],
        metadata={"validation_passed": False},
    )
