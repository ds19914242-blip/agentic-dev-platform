from orchestrator.agents.result import passed


def execute_planner(context):
    return passed(
        "planner",
        "Planner runtime executed.",
        artifacts=[
            "plan.md",
            "architecture-review.md",
            "qa-plan.md",
        ],
    )
