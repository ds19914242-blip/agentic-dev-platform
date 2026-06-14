from orchestrator.agent_runtime.builtin_agents import create_builtin_registry
from orchestrator.agent_runtime.graph import AgentGraph


DEFAULT_AGENT_CHAIN = [
    ("architect", []),
    ("implementation", ["architect"]),
    ("validation", ["implementation"]),
    ("review", ["validation"]),
    ("acceptance", ["review"]),
    ("release", ["acceptance"]),
]


def create_default_agent_graph():
    registry = create_builtin_registry()
    graph = AgentGraph()

    for agent_name, depends_on in DEFAULT_AGENT_CHAIN:
        definition = registry.get(agent_name)
        graph.add(
            node_id=agent_name,
            agent=definition.factory(),
            depends_on=depends_on,
        )

    return graph
