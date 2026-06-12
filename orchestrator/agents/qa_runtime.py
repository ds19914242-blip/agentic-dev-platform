from orchestrator.agents.result import passed
from orchestrator.qa_agent import create_qa_plan


def execute_qa(context):
    feature = context.feature
    affected = context.inputs.get("affected", [])
    plan = context.inputs.get("plan", "")
    architecture_review = context.inputs.get("architecture_review", "")

    qa_plan = create_qa_plan(
        feature,
        affected,
        plan,
        architecture_review,
    )

    return passed(
        "qa",
        "QA agent created verification plan.",
        artifacts=["qa-plan.md"],
        metadata={"qa_plan": qa_plan},
    )
