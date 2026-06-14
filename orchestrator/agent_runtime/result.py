from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class AgentResult:
    status: str
    confidence: float = 0.0
    artifacts: List[str] = field(default_factory=list)
    findings: List[str] = field(default_factory=list)
    handoff: Dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self):
        return self.status in {"passed", "completed", "ok"}
