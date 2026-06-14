from orchestrator.agents.result import failed, passed
from orchestrator.reviewer_agent import run_reviewer
from orchestrator.run_context import update_run_context


def execute_reviewer(context):
    if not context.run_dir:
        return failed(
            "reviewer",
            "Reviewer cannot run because run_dir is missing.",
            next_actions=["Provide run_dir in AgentRunContext."],
        )

    if not context.repo_path:
        return failed(
            "reviewer",
            "Reviewer cannot run because repo_path is missing.",
            next_actions=["Provide repo_path in AgentRunContext."],
        )

    review = run_reviewer(
        run_dir=context.run_dir,
        repo_path=context.repo_path,
        feature=context.feature,
    )

    update_run_context(context.run_dir, review=review)

    status = "failed" if review.get("blocking_issues") else "passed"
    result_factory = failed if status == "failed" else passed

    return result_factory(
        "reviewer",
        review.get("summary", "Reviewer completed."),
        artifacts=["review.md", "review.json", "review-response.md"],
        next_actions=review.get("blocking_issues", []),
        metadata={"review": review},
    )
