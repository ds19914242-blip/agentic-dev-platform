from dataclasses import dataclass, field
from typing import Dict, List

from orchestrator.agent_runtime.agent import Agent
from orchestrator.agent_runtime.context import AgentContext
from orchestrator.agent_runtime.result import AgentResult


@dataclass
class AgentNode:
    node_id: str
    agent: Agent
    depends_on: List[str] = field(default_factory=list)


class AgentGraph:
    def __init__(self):
        self.nodes: Dict[str, AgentNode] = {}
        self.results: Dict[str, AgentResult] = {}

    def add(self, node_id: str, agent: Agent, depends_on=None):
        self.nodes[node_id] = AgentNode(
            node_id=node_id,
            agent=agent,
            depends_on=list(depends_on or []),
        )

    def ready_nodes(self):
        ready = []
        for node_id, node in self.nodes.items():
            if node_id in self.results:
                continue
            if all(dep in self.results for dep in node.depends_on):
                ready.append(node)
        return ready

    def run(self, context: AgentContext):
        while len(self.results) < len(self.nodes):
            ready = self.ready_nodes()

            if not ready:
                raise RuntimeError("Agent graph has no ready nodes; dependency cycle or missing dependency")

            for node in ready:
                self.results[node.node_id] = node.agent.run(context)

        return self.results
