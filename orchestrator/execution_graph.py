from dataclasses import dataclass


@dataclass
class GraphNode:
    id: str
    name: str
    status: str = "pending"


class ExecutionGraph:
    def __init__(self):
        self.nodes = []

    def add_node(self, node_id, name):
        self.nodes.append(GraphNode(id=node_id, name=name))

    def mark_completed(self, node_id):
        for node in self.nodes:
            if node.id == node_id:
                node.status = "completed"

    def to_markdown(self):
        lines = ["# Execution Graph", ""]

        for node in self.nodes:
            lines.append(f"- [{node.status}] {node.id}: {node.name}")

        return "\n".join(lines)
