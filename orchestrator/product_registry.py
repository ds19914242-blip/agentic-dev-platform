from pathlib import Path
import re


def parse_validators(text):
    validators = []
    lines = text.splitlines()
    current = None

    for line in lines:
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
    capabilities = {}
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
                capabilities[key.strip()] = value.strip().lower() == "true"

    return capabilities


def read_scalar(text, key, default=""):
    match = re.search(rf"^{key}:\s*(.+)$", text, re.MULTILINE)
    return match.group(1).strip() if match else default


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
    }
