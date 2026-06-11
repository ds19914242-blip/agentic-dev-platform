import json
from pathlib import Path
from datetime import datetime


MEMORY_DIR = Path("memory")


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


def ensure_memory_dir():
    MEMORY_DIR.mkdir(exist_ok=True)


def read_json(path, default):
    path = Path(path)
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text())
    except Exception:
        return default


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    return path


def product_memory_path(product_name):
    return MEMORY_DIR / f"{product_name}-product-memory.json"


def run_memory_path(product_name):
    return MEMORY_DIR / f"{product_name}-run-memory.json"


def architecture_memory_path(product_name):
    return MEMORY_DIR / f"{product_name}-architecture-memory.json"


def load_product_memory(product_name):
    ensure_memory_dir()
    return read_json(product_memory_path(product_name), {})


def save_product_memory(product_name, data):
    ensure_memory_dir()
    data["updated_at"] = now_iso()
    return write_json(product_memory_path(product_name), data)


def update_product_memory(product_name, updates):
    data = load_product_memory(product_name)
    data.update(updates)
    return save_product_memory(product_name, data)


def load_run_memory(product_name):
    ensure_memory_dir()
    return read_json(run_memory_path(product_name), [])


def append_run_memory(product_name, entry, limit=100):
    entries = load_run_memory(product_name)
    entry["recorded_at"] = now_iso()
    entries.append(entry)
    entries = entries[-limit:]
    return write_json(run_memory_path(product_name), entries)


def load_architecture_memory(product_name):
    ensure_memory_dir()
    return read_json(architecture_memory_path(product_name), [])


def append_architecture_memory(product_name, decision):
    entries = load_architecture_memory(product_name)
    decision["recorded_at"] = now_iso()
    entries.append(decision)
    return write_json(architecture_memory_path(product_name), entries)


def summarize_run(run_dir):
    run_dir = Path(run_dir)
    run_json = read_json(run_dir / "run.json", {})

    validation = read_json(run_dir / "validation.json", {})
    confidence = read_json(run_dir / "confidence.json", {})
    review = read_json(run_dir / "review.json", {})

    return {
        "run_id": run_json.get("run_id", run_dir.name),
        "run_type": run_json.get("run_type"),
        "product": run_json.get("product"),
        "request": run_json.get("request"),
        "status": run_json.get("status"),
        "current_stage": run_json.get("current_stage"),
        "validation_result": validation.get("overall_result"),
        "confidence_status": confidence.get("status"),
        "requirements_covered": review.get("requirements_covered"),
        "scope_creep": review.get("scope_creep"),
        "architecture_risk": review.get("architecture_risk"),
        "artifacts": sorted((run_json.get("artifacts") or {}).keys()),
        "events_count": len(run_json.get("events") or []),
    }


def ingest_run(product_name, run_dir):
    entry = summarize_run(run_dir)
    return append_run_memory(product_name, entry)
