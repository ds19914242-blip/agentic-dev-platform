from pathlib import Path


def parse_simple_yaml(text):
    data = {}
    current_key = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line.strip() or line.strip().startswith("#"):
            continue

        if line.startswith("  - ") and current_key:
            data.setdefault(current_key, []).append(line.strip()[2:].strip())
            continue

        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            current_key = key

            if value:
                if value.lower() == "true":
                    data[key] = True
                elif value.lower() == "false":
                    data[key] = False
                else:
                    data[key] = value
            else:
                data[key] = []

    return data


def load_agent_definition(agent_name, definitions_dir="orchestrator/agents/definitions"):
    path = Path(definitions_dir) / f"{agent_name}.yaml"
    if not path.exists():
        return None

    data = parse_simple_yaml(path.read_text(errors="ignore"))
    data["definition_path"] = str(path)
    return data
