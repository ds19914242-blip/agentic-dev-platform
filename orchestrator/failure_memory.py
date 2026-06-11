import json
from pathlib import Path
from datetime import datetime


MEMORY_DIR = Path("memory")


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


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


def failure_memory_path(product_name):
    return MEMORY_DIR / f"{product_name}-failure-memory.json"


def classify_failure(validation):
    validators = validation.get("validators") or []

    for result in validators:
        if result.get("passed"):
            continue

        command = result.get("command", "")
        stderr = result.get("stderr", "")
        stdout = result.get("stdout", "")
        text = f"{command}\n{stdout}\n{stderr}".lower()

        if "tsc" in text or "typescript" in text or "type error" in text:
            return "typescript"
        if "eslint" in text or "lint" in text:
            return "lint"
        if "test" in text or "jest" in text or "vitest" in text:
            return "test"
        if "build" in text or "next build" in text:
            return "build"

    return "unknown"


def extract_failure_summary(validation, max_chars=2000):
    validators = validation.get("validators") or []
    chunks = []

    for result in validators:
        if result.get("passed"):
            continue

        chunks.append(f"Validator: {result.get('name')}")
        chunks.append(f"Command: {result.get('command')}")
        chunks.append(f"Exit code: {result.get('exit_code')}")

        stderr = result.get("stderr") or ""
        stdout = result.get("stdout") or ""

        if stderr:
            chunks.append("STDERR:")
            chunks.append(stderr[-max_chars:])

        if stdout:
            chunks.append("STDOUT:")
            chunks.append(stdout[-max_chars:])

    return "\n".join(chunks)[-max_chars:]


def load_failure_memory(product_name):
    return read_json(failure_memory_path(product_name), [])


def append_failure_memory(product_name, entry, limit=200):
    entries = load_failure_memory(product_name)
    entry["recorded_at"] = now_iso()
    entries.append(entry)
    entries = entries[-limit:]
    return write_json(failure_memory_path(product_name), entries)


def ingest_validation_failure(product_name, run_dir):
    run_dir = Path(run_dir)
    validation = read_json(run_dir / "validation.json", {})

    if validation.get("overall_result") != "failed":
        return None

    run_json = read_json(run_dir / "run.json", {})

    entry = {
        "run_id": run_json.get("run_id", run_dir.name),
        "product": product_name,
        "request": run_json.get("request"),
        "failure_type": classify_failure(validation),
        "summary": extract_failure_summary(validation),
        "status": run_json.get("status"),
        "current_stage": run_json.get("current_stage"),
    }

    append_failure_memory(product_name, entry)
    return entry


def related_failures(product_name, feature, limit=5):
    failures = load_failure_memory(product_name)
    feature_terms = {
        token.lower().strip(".,:;()[]{}")
        for token in feature.split()
        if len(token.strip(".,:;()[]{}")) >= 4
    }

    scored = []
    for failure in failures:
        text = f"{failure.get('request', '')} {failure.get('summary', '')}"
        terms = {
            token.lower().strip(".,:;()[]{}")
            for token in text.split()
            if len(token.strip(".,:;()[]{}")) >= 4
        }
        overlap = len(feature_terms & terms)
        if overlap:
            scored.append((overlap, failure))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [failure for _, failure in scored[:limit]]
