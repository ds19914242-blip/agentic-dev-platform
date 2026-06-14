import json
from pathlib import Path


def write_agent_results(output_dir, results):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    payload = {}

    for node_id, result in results.items():
        payload[node_id] = {
            "status": result.status,
            "confidence": result.confidence,
            "artifacts": result.artifacts,
            "findings": result.findings,
            "handoff": result.handoff,
            "ok": result.ok,
        }

    path = output_dir / "agent-results.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    return path


def write_agent_report(output_dir, results):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    lines = ["# Agent Graph Report", ""]

    for node_id, result in results.items():
        lines.append(f"## {node_id}")
        lines.append("")
        lines.append(f"- Status: {result.status}")
        lines.append(f"- Confidence: {result.confidence}")
        lines.append(f"- OK: {result.ok}")
        lines.append("")
        if result.findings:
            lines.append("Findings:")
            for finding in result.findings:
                lines.append(f"- {finding}")
            lines.append("")

    path = output_dir / "agent-report.md"
    path.write_text("\n".join(lines))
    return path
