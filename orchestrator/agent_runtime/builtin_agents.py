from orchestrator.agent_runtime.agent import Agent
from orchestrator.agent_runtime.context import AgentContext
from orchestrator.agent_runtime.registry import AgentRegistry
from orchestrator.agent_runtime.result import AgentResult


class PlaceholderAgent(Agent):
    def __init__(self, name: str):
        self.name = name

    def run(self, context: AgentContext) -> AgentResult:
        return AgentResult(
            status="completed",
            confidence=0.0,
            findings=[f"{self.name} placeholder executed"],
            handoff={"task": context.task},
        )


def create_builtin_registry() -> AgentRegistry:
    registry = AgentRegistry()

    for name, description in [
        ("architect", "Understands request and decomposes work"),
        ("implementation", "Implements product changes"),
        ("validation", "Runs validators and reports evidence"),
        ("review", "Reviews implementation and risks"),
        ("acceptance", "Runs acceptance scenarios"),
        ("release", "Verifies production deployment"),
    ]:
        registry.register(
            name=name,
            description=description,
            factory=lambda agent_name=name: PlaceholderAgent(agent_name),
        )

    return registry
