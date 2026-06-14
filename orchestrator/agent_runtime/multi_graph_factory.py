from orchestrator.agent_runtime.builtin_agents import create_builtin_registry
from orchestrator.agent_runtime.graph import AgentGraph
from orchestrator.agent_runtime.agents.lane_agents import (
    BackendImplementationAgent,
    FrontendImplementationAgent,
    QAPlanAgent,
)


def create_multi_agent_graph():
    registry = create_builtin_registry()
    graph = AgentGraph()

    graph.add(
        "architect",
        registry.get("architect").factory(),
    )

    graph.add(
        "implementation_backend",
        BackendImplementationAgent(),
        depends_on=["architect"],
    )

    graph.add(
        "implementation_frontend",
        FrontendImplementationAgent(),
        depends_on=["architect"],
    )

    graph.add(
        "qa_plan",
        QAPlanAgent(),
        depends_on=["architect"],
    )

    graph.add(
        "validation",
        registry.get("validation").factory(),
        depends_on=[
            "implementation_backend",
            "implementation_frontend",
            "qa_plan",
        ],
    )

    graph.add(
        "review",
        registry.get("review").factory(),
        depends_on=["validation"],
    )

    graph.add(
        "acceptance",
        registry.get("acceptance").factory(),
        depends_on=["review"],
    )

    graph.add(
        "release",
        registry.get("release").factory(),
        depends_on=["acceptance"],
    )

    return graph
