from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class AgentContext:
    task: str
    product: str = ""
    repo_path: str = ""
    run_dir: str = ""
    inputs: Dict[str, Any] = field(default_factory=dict)
    artifacts: List[str] = field(default_factory=list)
