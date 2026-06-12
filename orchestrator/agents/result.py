from dataclasses import dataclass, asdict, field
from pathlib import Path
import json


@dataclass
class AgentResult:
    agent: str
    status: str
    summary: str
    artifacts: list = field(default_factory=list)
    next_actions: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)


def write_agent_result(run_dir, result):
    run_dir = Path(run_dir)
    agents_dir = run_dir / "agents"
    agents_dir.mkdir(exist_ok=True)

    json_path = agents_dir / f"{result.agent}.json"
    md_path = agents_dir / f"{result.agent}.md"

    json_path.write_text(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))

    lines = [
        f"# Agent Result: {result.agent}",
        "",
        f"Status: {result.status}",
        "",
        "## Summary",
        "",
        result.summary,
        "",
        "## Artifacts",
        "",
    ]

    lines.extend([f"- {item}" for item in result.artifacts] or ["- none"])
    lines.extend(["", "## Next Actions", ""])
    lines.extend([f"- {item}" for item in result.next_actions] or ["- none"])

    md_path.write_text("\n".join(lines).rstrip() + "\n")

    return json_path, md_path


def passed(agent, summary, artifacts=None, next_actions=None, metadata=None):
    return AgentResult(agent, "passed", summary, artifacts or [], next_actions or [], metadata or {})


def failed(agent, summary, artifacts=None, next_actions=None, metadata=None):
    return AgentResult(agent, "failed", summary, artifacts or [], next_actions or [], metadata or {})


def skipped(agent, summary, artifacts=None, next_actions=None, metadata=None):
    return AgentResult(agent, "skipped", summary, artifacts or [], next_actions or [], metadata or {})
