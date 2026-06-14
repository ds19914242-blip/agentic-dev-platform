from dataclasses import dataclass
from typing import Callable, Dict, List

from orchestrator.agent_runtime.agent import Agent


@dataclass
class AgentDefinition:
    name: str
    description: str
    factory: Callable[[], Agent]


class AgentRegistry:
    def __init__(self):
        self._agents: Dict[str, AgentDefinition] = {}

    def register(self, name: str, description: str, factory: Callable[[], Agent]):
        self._agents[name] = AgentDefinition(
            name=name,
            description=description,
            factory=factory,
        )

    def get(self, name: str) -> AgentDefinition:
        if name not in self._agents:
            raise KeyError(f"Agent not registered: {name}")
        return self._agents[name]

    def list(self) -> List[AgentDefinition]:
        return [self._agents[name] for name in sorted(self._agents)]
