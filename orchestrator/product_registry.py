from pathlib import Path
import re


def _load_yaml_text(text):
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(text) or {}
        if isinstance(data, dict):
            return data
    except Exception:
        pass

    return {}


def parse_validators(text):
    data = _load_yaml_text(text)

    if isinstance(data.get("validators"), list):
        return data.get("validators") or []

    validation = data.get("validation") or {}
    if isinstance(validation, dict) and isinstance(validation.get("validators"), list):
        return validation.get("validators") or []

    validators = []
    lines = text.splitlines()
    current = None
    in_validators = False

    for line in lines:
        if line.strip() == "validators:":
            in_validators = True
            continue

        if in_validators and line and not line.startswith(" "):
            break

        if not in_validators:
            continue

        stripped = line.strip()

        if stripped.startswith("- name:"):
            if current:
                validators.append(current)

            current = {
                "name": stripped.split(":", 1)[1].strip(),
                "command": "",
                "required": True,
            }

        elif stripped.startswith("command:") and current is not None:
            current["command"] = stripped.split(":", 1)[1].strip()

        elif stripped.startswith("required:") and current is not None:
            value = stripped.split(":", 1)[1].strip().lower()
            current["required"] = value == "true"

    if current:
        validators.append(current)

    return validators


def parse_capabilities(text):
    data = _load_yaml_text(text)

    capabilities = data.get("capabilities")
    if isinstance(capabilities, dict):
        return capabilities

    parsed = {}
    in_capabilities = False

    for line in text.splitlines():
        if line.strip() == "capabilities:":
            in_capabilities = True
            continue

        if in_capabilities:
            if line and not line.startswith(" "):
                break

            stripped = line.strip()
            if ":" in stripped:
                key, value = stripped.split(":", 1)
                parsed[key.strip()] = value.strip().lower() == "true"

    return parsed


def read_scalar(text, key, default=""):
    data = _load_yaml_text(text)

    value = data.get(key)
    if value is not None and not isinstance(value, (dict, list)):
        return str(value)

    match = re.search(rf"^{key}:\s*(.+)$", text, re.MULTILINE)
    return match.group(1).strip() if match else default


def read_section(text, key):
    data = _load_yaml_text(text)

    value = data.get(key)
    if isinstance(value, dict):
        return value

    return {}


def load_product_config(product_name):
    config_path = Path("products") / product_name / "config.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"Product config not found: {config_path}")

    text = config_path.read_text()
    repo_path = read_scalar(text, "repo_path")

    if not repo_path:
        raise ValueError("repo_path not found in product config")

    return {
        "name": read_scalar(text, "name", product_name),
        "repo_path": repo_path,
        "type": read_scalar(text, "type"),
        "status": read_scalar(text, "status"),
        "framework": read_scalar(text, "framework"),
        "capabilities": parse_capabilities(text),
        "validators": parse_validators(text),
        "acceptance": read_section(text, "acceptance"),
        "deployment": read_section(text, "deployment"),
        "validation": read_section(text, "validation"),
    }
