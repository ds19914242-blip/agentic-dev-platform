import json
from collections import Counter
from pathlib import Path


def load_json(path):
    try:
        return json.loads(Path(path).read_text())
    except Exception:
        return {}


def main():
    runs = sorted(Path("runs").glob("*/run.json"))

    by_type = Counter()
    by_status = Counter()
    by_pipeline = Counter()

    for run_json in runs:
        data = load_json(run_json)
        run_type = data.get("run_type") or "unknown"
        status = data.get("status") or "unknown"

        by_type[run_type] += 1
        by_status[status] += 1

        context = load_json(run_json.parent / "run-context.json")
        pipeline = context.get("pipeline") or run_type or "unknown"
        by_pipeline[pipeline] += 1

    print("Agentic Metrics")
    print()

    print("Runs by type:")
    for key, value in by_type.most_common():
        print(f"- {key}: {value}")

    print()
    print("Runs by pipeline:")
    for key, value in by_pipeline.most_common():
        print(f"- {key}: {value}")

    print()
    print("Runs by status:")
    for key, value in by_status.most_common():
        print(f"- {key}: {value}")


if __name__ == "__main__":
    main()
