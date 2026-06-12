from orchestrator.agents.result import passed

def execute_reviewer(context):
    return passed(
        "reviewer",
        "Reviewer runtime adapter executed.",
        artifacts=["review.md", "review.json"],
    )
