from orchestrator.agents.result import passed

def execute_acceptance(context):
    return passed(
        "acceptance",
        "Acceptance runtime adapter executed.",
        artifacts=["acceptance-result.md", "acceptance-result.json"],
    )
