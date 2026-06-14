from pathlib import Path


def _load_yaml_file(path):
    try:
        import yaml  # type: ignore
    except Exception as exc:
        raise RuntimeError(
            "PyYAML is required to load product config files"
        ) from exc

    data = yaml.safe_load(path.read_text()) or {}

    if not isinstance(data, dict):
        raise ValueError(f"Product config must be a YAML object: {path}")

    return data


def _dict(value):
    return value if isinstance(value, dict) else {}


def _list(value):
    return value if isinstance(value, list) else []


def _scalar(data, key, default=""):
    value = data.get(key, default)

    if value is None:
        return default

    if isinstance(value, (dict, list)):
        return default

    return str(value)


def load_product_config(product_name):
    config_path = Path("products") / product_name / "config.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"Product config not found: {config_path}")

    data = _load_yaml_file(config_path)

    repo_path = _scalar(data, "repo_path")

    if not repo_path:
        raise ValueError("repo_path not found in product config")

    validation = _dict(data.get("validation"))
    validators = _list(data.get("validators")) or _list(validation.get("validators"))

    return {
        "name": _scalar(data, "name", product_name),
        "repo_path": repo_path,
        "type": _scalar(data, "type"),
        "status": _scalar(data, "status"),
        "framework": _scalar(data, "framework"),
        "capabilities": _dict(data.get("capabilities")),
        "validators": validators,
        "acceptance": _dict(data.get("acceptance")),
        "deployment": _dict(data.get("deployment")),
        "validation": validation,
    }
