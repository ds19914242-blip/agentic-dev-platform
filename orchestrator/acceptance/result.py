from dataclasses import dataclass, asdict
from pathlib import Path
import json

@dataclass
class AcceptanceResult:
    epic_dir: str
    command: str
    passed: bool
    returncode: int
    stdout: str
    stderr: str

    def to_dict(self):
        return asdict(self)

def write_acceptance_result(epic_dir, result):
    epic_dir = Path(epic_dir)
    json_path = epic_dir / "acceptance-result.json"
    md_path = epic_dir / "acceptance-result.md"
    json_path.write_text(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    status = "passed" if result.passed else "failed"
    md_path.write_text(f"# Acceptance Result\n\nStatus: {status}\n\nCommand:\n\n```bash\n{result.command}\n```\n\nReturn code: {result.returncode}\n\n## stdout\n\n```text\n{result.stdout}\n```\n\n## stderr\n\n```text\n{result.stderr}\n```\n")
    return json_path, md_path
