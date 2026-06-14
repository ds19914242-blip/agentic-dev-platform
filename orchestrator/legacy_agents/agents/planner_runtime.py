from orchestrator.agents.result import passed
from orchestrator.llm_planner_agent import create_llm_plan
from orchestrator.run_context import update_run_context
from orchestrator.services.autonomous_run_service import apply_planner_selected_files


def execute_planner(context):
    run_dir = context.run_dir
    repo_path = context.repo_path
    feature = context.feature
    files = context.inputs.get("files", [])
    affected = context.inputs.get("affected", [])
    repo_map_text = context.inputs.get("repo_map_text", "")
    run = context.inputs.get("run")

    plan = create_llm_plan(repo_path, feature, affected, repo_map_text)
    update_run_context(run_dir, plan=plan, affected_files=affected)

    if run:
        affected, planner_selected_files = apply_planner_selected_files(
            run_dir,
            plan,
            files,
            affected,
            run,
        )
    else:
        planner_selected_files = []

    return passed(
        "planner",
        "Planner created implementation plan.",
        artifacts=["plan.md", "planner-selected-files.md"],
        metadata={
            "plan": plan,
            "affected": affected,
            "planner_selected_files": planner_selected_files,
        },
    )
