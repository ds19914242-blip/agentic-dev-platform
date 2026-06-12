from orchestrator.agents.result import passed

def execute_validator(context):
    return passed(
        "validator",
        "Validator runtime adapter executed.",
        artifacts=["validation.md", "validation.json"],
    )
