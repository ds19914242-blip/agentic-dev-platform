from orchestrator.agent_context import AgentContext
from orchestrator.architect_agent import create_architecture_review
from orchestrator.llm_planner_agent import create_llm_plan
from orchestrator.qa_agent import create_qa_plan
from orchestrator.run_context import update_run_context
from orchestrator.services.autonomous_run_service import apply_planner_selected_files


def run_autonomous_planning(
    run_dir,
    run,
    graph_v2,
    repo_path,
    feature,
    files,
    affected,
    repo_map_text,
):
    agent_context = AgentContext()

    plan = create_llm_plan(repo_path, feature, affected, repo_map_text)
    agent_context.set("plan", plan)
    update_run_context(run_dir, plan=plan, affected_files=affected)
    graph_v2.complete("planning", artifacts=["plan.md"])
    graph_v2.write()

    architecture_review = create_architecture_review(
        feature,
        affected,
        repo_map_text,
        agent_context.get("plan"),
    )
    agent_context.set("architecture_review", architecture_review)
    graph_v2.complete("architecture", artifacts=["architecture-review.md"])
    graph_v2.write()

    qa_plan = create_qa_plan(
        feature,
        affected,
        agent_context.get("plan"),
        agent_context.get("architecture_review"),
    )
    agent_context.set("qa_plan", qa_plan)
    graph_v2.complete("qa", artifacts=["qa-plan.md"])
    graph_v2.write()

    affected, planner_selected_files = apply_planner_selected_files(
        run_dir,
        plan,
        files,
        affected,
        run,
    )

    return {
        "agent_context": agent_context,
        "plan": plan,
        "architecture_review": architecture_review,
        "qa_plan": qa_plan,
        "affected": affected,
        "planner_selected_files": planner_selected_files,
    }
