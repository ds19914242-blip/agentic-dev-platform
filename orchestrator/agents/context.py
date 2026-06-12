from dataclasses import dataclass, field


@dataclass
class AgentRunContext:
    agent: str
    run_dir: str = ""
    product_name: str = ""
    repo_path: str = ""
    feature: str = ""
    task_path: str = ""
    inputs: dict = field(default_factory=dict)
