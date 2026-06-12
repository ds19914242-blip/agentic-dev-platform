from pathlib import Path


def write_scenario_report(epic_dir, scenarios):
    epic_dir = Path(epic_dir)
    report_path = epic_dir / "acceptance-scenarios-report.md"

    lines = ["# Acceptance Scenarios Report", "", f"Scenarios: {len(scenarios)}", ""]

    for index, scenario in enumerate(scenarios, start=1):
        lines.append(f"## {index}. {scenario.title}")
        lines.append("")
        lines.append(f"Steps: {len(scenario.steps)}")
        for step in scenario.steps:
            lines.append(f"- {step}")
        lines.append("")
        lines.append(f"Expected: {len(scenario.expected)}")
        for expected in scenario.expected:
            lines.append(f"- {expected}")
        lines.append("")

    report_path.write_text("\n".join(lines).rstrip() + "\n")
    return report_path
