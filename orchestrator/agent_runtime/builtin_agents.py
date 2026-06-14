from orchestrator.agent_runtime.agent import Agent
from orchestrator.agent_runtime.context import AgentContext
from orchestrator.agent_runtime.registry import AgentRegistry
from orchestrator.agent_runtime.result import AgentResult
from orchestrator.agent_runtime.agents.release_agent import ReleaseAgent
from orchestrator.agent_runtime.agents.architect_agent import ArchitectAgent
from orchestrator.agent_runtime.agents.validation_agent import ValidationAgent


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
        ("implementation", "Implements product changes"),
        ("review", "Reviews implementation and risks"),
        ("acceptance", "Runs acceptance scenarios"),
    ]:
        registry.register(
            name=name,
            description=description,
            factory=lambda agent_name=name: PlaceholderAgent(agent_name),
        )

    registry.register(
        name="architect",
        description="Creates architecture plan and lane handoffs",
        factory=ArchitectAgent,
    )

    registry.register(
        name="validation",
        description="Runs product validators and reports evidence",
        factory=ValidationAgent,
    )

    registry.register(
        name="release",
        description="Verifies production deployment",
        factory=ReleaseAgent,
    )

    return registry
