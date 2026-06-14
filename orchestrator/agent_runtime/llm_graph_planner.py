from orchestrator.agent_runtime.graph_plan import plan_graph_for_task


def plan_graph(task, repo_path="", product=""):
    return plan_graph_for_task(task)
