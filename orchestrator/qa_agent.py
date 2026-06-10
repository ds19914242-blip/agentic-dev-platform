def create_qa_plan(feature, affected_files):
    lines = []

    lines.append("# QA Plan")
    lines.append("")
    lines.append("## Feature Request")
    lines.append("")
    lines.append(feature)
    lines.append("")
    lines.append("## Validation Goals")
    lines.append("")
    lines.append("- Confirm the feature works as requested.")
    lines.append("- Confirm existing flows still work.")
    lines.append("- Confirm no unsafe areas were modified.")
    lines.append("")
    lines.append("## Suggested Checks")
    lines.append("")
    lines.append("- Run typecheck.")
    lines.append("- Review git diff.")
    lines.append("- Manually verify the changed UI/API flow.")
    lines.append("- Check error state if API/LLM call fails.")
    lines.append("")
    lines.append("## Affected Files To Review")
    lines.append("")

    for file in affected_files:
        lines.append(f"- {file}")

    lines.append("")
    lines.append("## Required Command")
    lines.append("")
    lines.append("```bash")
    lines.append("npx tsc --noEmit")
    lines.append("```")

    return "\n".join(lines)
