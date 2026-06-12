from orchestrator.agent_context import AgentContext
from orchestrator.agents.context import AgentRunContext
from orchestrator.agents.runtime import run_agent


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

    planner_result = run_agent(
        "planner",
        AgentRunContext(
            agent="planner",
            run_dir=str(run_dir),
            repo_path=repo_path,
            feature=feature,
            inputs={
                "files": files,
                "affected": affected,
                "repo_map_text": repo_map_text,
                "run": run,
            },
        ),
    )
    plan = planner_result.metadata.get("plan", "")
    affected = planner_result.metadata.get("affected", affected)
    planner_selected_files = planner_result.metadata.get("planner_selected_files", [])
    agent_context.set("plan", plan)
    graph_v2.complete("planning", artifacts=["plan.md", "planner-selected-files.md"])
    graph_v2.write()

    architect_result = run_agent(
        "architect",
        AgentRunContext(
            agent="architect",
            run_dir=str(run_dir),
            repo_path=repo_path,
            feature=feature,
            inputs={
                "affected": affected,
                "repo_map_text": repo_map_text,
                "plan": agent_context.get("plan"),
            },
        ),
    )
    architecture_review = architect_result.metadata.get("architecture_review", "")
    agent_context.set("architecture_review", architecture_review)
    graph_v2.complete("architecture", artifacts=["architecture-review.md"])
    graph_v2.write()

    qa_result = run_agent(
        "qa",
        AgentRunContext(
            agent="qa",
            run_dir=str(run_dir),
            repo_path=repo_path,
            feature=feature,
            inputs={
                "affected": affected,
                "plan": agent_context.get("plan"),
                "architecture_review": agent_context.get("architecture_review"),
            },
        ),
    )
    qa_plan = qa_result.metadata.get("qa_plan", "")
    agent_context.set("qa_plan", qa_plan)
    graph_v2.complete("qa", artifacts=["qa-plan.md"])
    graph_v2.write()

    return {
        "agent_context": agent_context,
        "plan": plan,
        "architecture_review": architecture_review,
        "qa_plan": qa_plan,
        "affected": affected,
        "planner_selected_files": planner_selected_files,
    }
