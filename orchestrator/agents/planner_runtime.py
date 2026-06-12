from orchestrator.agents.result import passed


def execute_planner(context):
    return passed(
        "planner",
        "Planner runtime adapter executed.",
        artifacts=[
            "plan.md",
            "architecture-review.md",
            "qa-plan.md",
            "planner-selected-files.md",
        ],
        metadata={
            "feature": context.feature,
            "repo_path": context.repo_path,
            "inputs": context.inputs,
        },
    )
