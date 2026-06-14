from orchestrator.agent_runtime.builtin_agents import create_builtin_registry
from orchestrator.agent_runtime.graph import AgentGraph
from orchestrator.agent_runtime.graph_plan import plan_graph_for_task
from orchestrator.agent_runtime.agents.lane_agents import (
    BackendImplementationAgent,
    FrontendImplementationAgent,
    QAPlanAgent,
)


def create_dynamic_agent_graph(task: str):
    registry = create_builtin_registry()
    plan = plan_graph_for_task(task)
    graph = AgentGraph()

    graph.add("architect", registry.get("architect").factory())

    lane_nodes = []

    if "backend" in plan.lanes:
        graph.add("implementation_backend", BackendImplementationAgent(), depends_on=["architect"])
        lane_nodes.append("implementation_backend")

    if "frontend" in plan.lanes:
        graph.add("implementation_frontend", FrontendImplementationAgent(), depends_on=["architect"])
        lane_nodes.append("implementation_frontend")

    if "qa" in plan.lanes:
        graph.add("qa_plan", QAPlanAgent(), depends_on=["architect"])
        lane_nodes.append("qa_plan")

    graph.add("validation", registry.get("validation").factory(), depends_on=lane_nodes or ["architect"])
    graph.add("review", registry.get("review").factory(), depends_on=["validation"])

    previous = "review"

    if plan.requires_acceptance:
        graph.add("acceptance", registry.get("acceptance").factory(), depends_on=[previous])
        previous = "acceptance"

    if plan.requires_release:
        graph.add("release", registry.get("release").factory(), depends_on=[previous])

    return graph, plan
