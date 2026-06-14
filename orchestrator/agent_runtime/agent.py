from abc import ABC, abstractmethod

from orchestrator.agent_runtime.context import AgentContext
from orchestrator.agent_runtime.result import AgentResult


class Agent(ABC):
    name = "agent"

    @abstractmethod
    def run(self, context: AgentContext) -> AgentResult:
        raise NotImplementedError
