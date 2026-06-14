from orchestrator.agent_runtime.agent import Agent
from orchestrator.agent_runtime.context import AgentContext
from orchestrator.agent_runtime.registry import AgentRegistry
from orchestrator.agent_runtime.result import AgentResult
from orchestrator.agent_runtime.agents.acceptance_agent import AcceptanceAgent
from orchestrator.agent_runtime.agents.architect_agent import ArchitectAgent
from orchestrator.agent_runtime.agents.implementation_agent import ImplementationPlanningAgent
from orchestrator.agent_runtime.agents.product_owner_agent import ProductOwnerAgent
from orchestrator.agent_runtime.agents.release_agent import ReleaseAgent
from orchestrator.agent_runtime.agents.review_agent import ReviewAgent
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

    registry.register("planner", "Creates implementation plan", lambda: PlaceholderAgent("planner"))
    registry.register("qa", "Creates QA plan", lambda: PlaceholderAgent("qa"))

    registry.register(
        name="product_owner",
        description="Defines product scope and acceptance criteria",
        factory=ProductOwnerAgent,
    )

    registry.register(
        name="architect",
        description="Creates architecture plan and lane handoffs",
        factory=ArchitectAgent,
    )

    registry.register(
        name="implementation",
        description="Prepares runtime implementation handoff",
        factory=ImplementationPlanningAgent,
    )

    registry.register(
        name="validation",
        description="Runs product validators and reports evidence",
        factory=ValidationAgent,
    )

    registry.register(
        name="review",
        description="Reviews runtime outputs and risks",
        factory=ReviewAgent,
    )

    registry.register(
        name="reviewer",
        description="Compatibility reviewer alias",
        factory=ReviewAgent,
    )

    registry.register(
        name="acceptance",
        description="Runs acceptance scenarios",
        factory=AcceptanceAgent,
    )

    registry.register(
        name="release",
        description="Verifies production deployment",
        factory=ReleaseAgent,
    )

    return registry
