import json
import os
import time
from pathlib import Path


def metrics_path(run_dir):
    return Path(run_dir) / "metrics.json"


def default_metrics():
    return {
        "model_calls": 0,
        "started_at": None,
        "completed_at": None,
        "duration_seconds": 0,
    }


def read_metrics(run_dir):
    path = metrics_path(run_dir)

    if not path.exists():
        return default_metrics()

    try:
        return json.loads(path.read_text())
    except Exception:
        return default_metrics()


def write_metrics(run_dir, metrics):
    path = metrics_path(run_dir)
    path.write_text(json.dumps(metrics, indent=2, ensure_ascii=False))
    return path


def start_metrics(run_dir):
    metrics = read_metrics(run_dir)

    if not metrics.get("started_at"):
        metrics["started_at"] = time.time()

    write_metrics(run_dir, metrics)
    return metrics


def finish_metrics(run_dir):
    metrics = read_metrics(run_dir)

    if not metrics.get("started_at"):
        metrics["started_at"] = time.time()

    metrics["completed_at"] = time.time()
    metrics["duration_seconds"] = int(metrics["completed_at"] - metrics["started_at"])

    write_metrics(run_dir, metrics)
    return metrics


def increment_model_calls(run_dir=None):
    run_dir = run_dir or os.environ.get("AGENTIC_RUN_DIR")

    if not run_dir:
        return None

    metrics = read_metrics(run_dir)
    metrics["model_calls"] = int(metrics.get("model_calls", 0)) + 1

    if not metrics.get("started_at"):
        metrics["started_at"] = time.time()

    write_metrics(run_dir, metrics)
    return metrics
