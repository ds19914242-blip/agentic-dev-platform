import json
import sys
from pathlib import Path


def read_json(path, default=None):
    try:
        return json.loads(Path(path).read_text())
    except Exception:
        return default if default is not None else {}


def run_dirs_for_epic(epic_dir):
    epic_dir = Path(epic_dir)
    run_names = set()

    for task in epic_dir.glob("task-*.md"):
        for line in task.read_text(errors="ignore").splitlines():
            if line.lower().startswith("run:"):
                run_names.add(line.split(":", 1)[1].strip())

    return [Path("runs") / name for name in sorted(run_names)]


def all_run_dirs():
    return sorted(p for p in Path("runs").glob("*") if p.is_dir())


def main():
    args = sys.argv[1:]

    if "--epic" in args:
        idx = args.index("--epic")
        epic_dir = args[idx + 1]
        runs = run_dirs_for_epic(epic_dir)
    else:
        runs = all_run_dirs()

    rows = []

    for run_dir in runs:
        metrics = read_json(run_dir / "metrics.json", {})
        run_json = read_json(run_dir / "run.json", {})

        rows.append({
            "run": run_dir.name,
            "status": run_json.get("status", "unknown"),
            "type": run_json.get("run_type", "unknown"),
            "model_calls": int(metrics.get("model_calls", 0) or 0),
            "duration_seconds": int(metrics.get("duration_seconds", 0) or 0),
        })

    total_runs = len(rows)
    total_calls = sum(row["model_calls"] for row in rows)
    total_duration = sum(row["duration_seconds"] for row in rows)

    avg_calls = round(total_calls / total_runs, 2) if total_runs else 0
    avg_duration = round(total_duration / total_runs, 2) if total_runs else 0

    print("Agentic Metrics")
    print()
    print(f"Total runs: {total_runs}")
    print(f"Total model calls: {total_calls}")
    print(f"Average model calls per run: {avg_calls}")
    print(f"Average duration seconds: {avg_duration}")
    print()

    print("Top 10 runs by model calls")
    print("--------------------------")

    for row in sorted(rows, key=lambda item: item["model_calls"], reverse=True)[:10]:
        print(
            f"{row['model_calls']:>4} calls | "
            f"{row['duration_seconds']:>5}s | "
            f"{row['type']} | "
            f"{row['status']} | "
            f"{row['run']}"
        )


if __name__ == "__main__":
    main()
