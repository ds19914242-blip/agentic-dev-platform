def create_plan(feature, affected_files):
    lines = []

    lines.append("# Implementation Plan")
    lines.append("")
    lines.append("## Feature Request")
    lines.append("")
    lines.append(feature)
    lines.append("")
    lines.append("## Affected Files")
    lines.append("")

    for file in affected_files:
        lines.append(f"- {file}")

    lines.append("")
    lines.append("## Plan")
    lines.append("")
    lines.append("1. Review affected files.")
    lines.append("2. Identify existing functionality.")
    lines.append("3. Define the smallest safe implementation.")
    lines.append("4. Modify only necessary files.")
    lines.append("5. Run typecheck or tests.")
    lines.append("6. Review git diff.")
    lines.append("7. Summarize changes and risks.")
    lines.append("")
    lines.append("## Safety Rules")
    lines.append("")
    lines.append("- Do not modify auth.")
    lines.append("- Do not modify billing.")
    lines.append("- Do not modify secrets.")
    lines.append("- Do not modify database schema unless explicitly required.")
    lines.append("- Do not modify deployment configuration.")
    lines.append("")

    return "\n".join(lines)
