from dataclasses import dataclass, field
from typing import List


@dataclass
class AgentGraphPlan:
    task: str
    lanes: List[str] = field(default_factory=list)
    requires_acceptance: bool = True
    requires_release: bool = False

    def node_chain(self):
        nodes = ["architect"]

        if "backend" in self.lanes:
            nodes.append("implementation_backend")

        if "frontend" in self.lanes:
            nodes.append("implementation_frontend")

        if "qa" in self.lanes:
            nodes.append("qa_plan")

        nodes.append("validation")
        nodes.append("review")

        if self.requires_acceptance:
            nodes.append("acceptance")

        if self.requires_release:
            nodes.append("release")

        return nodes


def plan_graph_for_task(task: str) -> AgentGraphPlan:
    text = task.lower()

    lanes = []

    if any(word in text for word in ["api", "db", "database", "backend", "server", "validator", "auth"]):
        lanes.append("backend")

    if any(word in text for word in ["ui", "page", "button", "screen", "frontend", "form", "visible", "selector", "sources"]):
        lanes.append("frontend")

    if any(word in text for word in ["test", "qa", "acceptance", "playwright", "verify", "verification"]):
        lanes.append("qa")

    if not lanes:
        lanes = ["frontend", "qa"]

    requires_release = any(word in text for word in ["production", "deploy", "release", "live"])

    return AgentGraphPlan(
        task=task,
        lanes=lanes,
        requires_acceptance=True,
        requires_release=requires_release,
    )
