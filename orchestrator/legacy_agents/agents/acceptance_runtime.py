from orchestrator.acceptance.runner import run_acceptance
from orchestrator.agents.result import failed, passed, skipped


def execute_acceptance(context):
    epic_dir = context.inputs.get("epic_dir")

    if not epic_dir:
        return skipped(
            "acceptance",
            "Acceptance skipped because epic_dir is missing.",
            next_actions=["Provide epic_dir when acceptance artifacts exist."],
        )

    result = run_acceptance(
        epic_dir=epic_dir,
        product_name=context.product_name,
    )

    if result.passed:
        return passed(
            "acceptance",
            "Acceptance verification passed.",
            artifacts=["acceptance-result.md", "acceptance-result.json"],
            metadata=result.to_dict(),
        )

    return failed(
        "acceptance",
        "Acceptance verification failed.",
        artifacts=["acceptance-result.md", "acceptance-result.json"],
        next_actions=["Run generated acceptance bug task."],
        metadata=result.to_dict(),
    )
