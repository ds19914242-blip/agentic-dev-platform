from orchestrator.agents.result import passed
from orchestrator.architect_agent import create_architecture_review


def execute_architect(context):
    feature = context.feature
    affected = context.inputs.get("affected", [])
    repo_map_text = context.inputs.get("repo_map_text", "")
    plan = context.inputs.get("plan", "")

    architecture_review = create_architecture_review(
        feature,
        affected,
        repo_map_text,
        plan,
    )

    return passed(
        "architect",
        "Architect reviewed architecture impact.",
        artifacts=["architecture-review.md"],
        metadata={"architecture_review": architecture_review},
    )
