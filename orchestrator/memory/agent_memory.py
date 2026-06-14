import json
from pathlib import Path

MEMORY_ROOT = Path("memory")

def load_memory(product):
    path = MEMORY_ROOT / f"{product}.json"

    if not path.exists():
        return {
            "validation_failures": [],
            "successful_patterns": [],
            "touched_files": [],
        }

    return json.loads(path.read_text())


def save_memory(product, data):
    MEMORY_ROOT.mkdir(exist_ok=True)
    path = MEMORY_ROOT / f"{product}.json"
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def record_validation_failure(product, details):
    memory = load_memory(product)
    memory["validation_failures"].append(details)
    save_memory(product, memory)


def record_success(product, details):
    memory = load_memory(product)
    memory["successful_patterns"].append(details)
    save_memory(product, memory)
