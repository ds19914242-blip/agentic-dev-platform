from pathlib import Path
import re


def load_product_config(product_name):
    config_path = Path("products") / product_name / "config.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"Product config not found: {config_path}")

    text = config_path.read_text()

    match = re.search(r"repo_path:\s*(.+)", text)

    if not match:
        raise ValueError("repo_path not found in product config")

    return {
        "name": product_name,
        "repo_path": match.group(1).strip(),
    }
