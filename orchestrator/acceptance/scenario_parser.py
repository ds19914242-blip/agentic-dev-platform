import json
import re
from pathlib import Path

from orchestrator.acceptance.scenario_model import AcceptanceScenario


SCENARIO_HEADING_RE = re.compile(r"^#{2,3}\\s*(?:Scenario:?\\s*)?(.+)$", re.MULTILINE | re.IGNORECASE)


def extract_bullets(section_text):
    items = []
    for line in section_text.splitlines():
        line = line.strip()
        if line.startswith("-"):
            items.append(line.lstrip("-").strip())
    return items


def split_sections(body):
    sections = {"steps": [], "expected": []}
    current = None
    buffer = []

    for line in body.splitlines():
        clean = line.strip().lower()
        if clean in {"steps:", "## steps", "### steps"}:
            if current and buffer:
                sections[current].extend(extract_bullets("\\n".join(buffer)))
            current = "steps"
            buffer = []
            continue
        if clean in {"expected:", "expect:", "assertions:", "## expected", "### expected"}:
            if current and buffer:
                sections[current].extend(extract_bullets("\\n".join(buffer)))
            current = "expected"
            buffer = []
            continue
        if current:
            buffer.append(line)

    if current and buffer:
        sections[current].extend(extract_bullets("\\n".join(buffer)))

    return sections


def parse_acceptance_scenarios(markdown_text):
    matches = list(SCENARIO_HEADING_RE.finditer(markdown_text))
    scenarios = []

    for index, match in enumerate(matches):
        title = match.group(1).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown_text)
        body = markdown_text[start:end].strip()
        sections = split_sections(body)
        scenarios.append(AcceptanceScenario(title=title, body=body, steps=sections["steps"], expected=sections["expected"]))

    return scenarios


def parse_acceptance_file(path):
    path = Path(path)
    return parse_acceptance_scenarios(path.read_text(errors="ignore"))


def write_scenarios_json(epic_dir):
    epic_dir = Path(epic_dir)
    scenarios_path = epic_dir / "acceptance-scenarios.md"
    output_path = epic_dir / "acceptance-scenarios.json"

    if not scenarios_path.exists():
        raise FileNotFoundError(f"Missing acceptance scenarios: {scenarios_path}")

    scenarios = parse_acceptance_file(scenarios_path)
    output_path.write_text(json.dumps([s.to_dict() for s in scenarios], indent=2, ensure_ascii=False))
    return output_path, scenarios
