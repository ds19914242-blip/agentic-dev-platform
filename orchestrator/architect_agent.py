def create_architecture_review(feature, affected_files, repo_map_text):
    lines = []

    lines.append("# Architecture Review")
    lines.append("")
    lines.append("## Feature Request")
    lines.append("")
    lines.append(feature)
    lines.append("")
    lines.append("## Review Focus")
    lines.append("")
    lines.append("- Does the feature fit existing architecture?")
    lines.append("- Which modules are affected?")
    lines.append("- Are there unnecessary risky changes?")
    lines.append("- Are auth, billing, secrets, DB schema or deployment config affected?")
    lines.append("")
    lines.append("## Affected Areas")
    lines.append("")

    for file in affected_files:
        if file.startswith("app/api/"):
            lines.append(f"- API route: {file}")
        elif file.startswith("components/"):
            lines.append(f"- UI component: {file}")
        elif file.startswith("lib/"):
            lines.append(f"- Library/module: {file}")
        elif file.startswith("src/agents/"):
            lines.append(f"- Agent/LLM layer: {file}")
        elif file.startswith("src/llm/"):
            lines.append(f"- LLM client layer: {file}")
        else:
            lines.append(f"- Other: {file}")

    lines.append("")
    lines.append("## Initial Risk Assessment")
    lines.append("")
    lines.append("- Risk level: medium")
    lines.append("- Reason: code changes may affect user-facing behavior.")
    lines.append("")
    lines.append("## Architecture Rule")
    lines.append("")
    lines.append("Prefer the smallest change that reuses existing modules.")
    lines.append("Do not introduce new infrastructure unless required.")
    lines.append("")

    return "\n".join(lines)
